"""Computed stock statuses (never typed by people): OK / LOW / STALE / EXPIRED / OUT."""

from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum
from typing import Any

from labbase.vault.model import Note, Vault


class Status(StrEnum):
    OK = "OK"
    LOW = "LOW"
    STALE = "STALE"
    EXPIRED = "EXPIRED"
    OUT = "OUT"


def _date(value: Any) -> date | None:
    from labbase.vault.validate import as_date

    return as_date(value)


def _int(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


@dataclass
class StockStatus:
    note: Note
    status: Status
    reason: str
    expires_soon: bool = False


def stock_status(vault: Vault, stock: Note, today: date | None = None) -> StockStatus:
    """Rules (in order): OUT → EXPIRED → LOW → STALE → OK.

    STALE only applies to stocks of bought items (bottles, buffers…): frozen cells and compound
    aliquots are not expected to be re-confirmed every month.
    """
    today = today or date.today()
    p = stock.props
    left = _int(p.get("vials_left"))
    if p.get("state") == "finished" or left == 0:
        return StockStatus(
            stock, Status.OUT, "finished" if p.get("state") == "finished" else "0 left"
        )
    expiry = _date(p.get("expiry"))
    if expiry and expiry < today:
        return StockStatus(stock, Status.EXPIRED, f"expired {expiry.isoformat()}")
    soon = bool(expiry and expiry <= today + timedelta(days=vault.settings["expiry_warning_days"]))
    if p.get("state") == "low":
        return StockStatus(stock, Status.LOW, "marked low", soon)
    content = vault.resolve(p.get("content"))
    if content is not None and content.type == "item":
        checked = _date(p.get("last_checked"))
        stale_days = vault.settings["stale_days"]
        if checked is None:
            return StockStatus(stock, Status.STALE, "never checked", soon)
        if today - checked > timedelta(days=stale_days):
            return StockStatus(stock, Status.STALE, f"last checked {checked.isoformat()}", soon)
    reason = f"expires {expiry.isoformat()}" if soon and expiry else ""
    return StockStatus(stock, Status.OK, reason, soon)


@dataclass
class ContentTotal:
    content: Note
    stocks: list[StockStatus]
    total: float | None
    unit: str
    low: bool


def item_totals(vault: Vault, statuses: list[StockStatus]) -> list[ContentTotal]:
    """For bought items with `reorder_at`: total left across usable stocks vs the threshold."""
    by_item: dict[str, list[StockStatus]] = {}
    for s in statuses:
        content = vault.resolve(s.note.props.get("content"))
        if content is not None and content.type == "item":
            by_item.setdefault(content.rel, []).append(s)
    results = []
    for item in (n for n in vault.notes if n.type == "item"):
        stocks = by_item.get(item.rel, [])
        usable = [s for s in stocks if s.status not in (Status.OUT, Status.EXPIRED)]
        unit = str(item.props.get("unit") or "")
        per_key = {"mL": "volume_mL", "uL": "volume_uL", "µL": "volume_uL"}.get(unit)
        total = 0.0
        for s in usable:
            left = _int(s.note.props.get("vials_left")) or 0
            size = s.note.props.get(per_key) if per_key else 1
            total += left * (size if isinstance(size, int | float) else 0)
        threshold = item.props.get("reorder_at")
        low = isinstance(threshold, int | float) and total <= threshold
        results.append(ContentTotal(item, stocks, total, unit or "units", low))
    return results
