"""The example vault is the reference for conventions: it must always pass `labbase check`."""

import shutil
from datetime import date
from pathlib import Path

from labbase.vault.check import run_checks
from labbase.vault.reader import load_vault

DEMO = Path(__file__).parent.parent / "vault-demo"


def test_demo_vault_is_clean() -> None:
    vault = load_vault(DEMO)
    result = run_checks(vault, date(2026, 10, 12))
    assert result.issues == []
    types = {n.type for n in vault.notes}
    assert {
        "location",
        "box",
        "stock",
        "compound",
        "strain",
        "cell_line",
        "media_recipe",
        "media_batch",
        "item",
        "supplier",
        "note",
    } <= types
    assert all(n.id for n in vault.notes)


def test_check_catches_deliberate_mistakes(tmp_path: Path) -> None:
    copy = tmp_path / "vault"
    shutil.copytree(DEMO, copy, ignore=shutil.ignore_patterns("_reports"))
    stock = copy / "Stocks" / "RAW p10 2026-02-03 Marc.md"
    text = stock.read_text()
    text = text.replace('content: "[[RAW 264.7]]"', 'content: "[[RAW 264]]"')
    stock.write_text(text)
    other = copy / "Stocks" / "THP-1 p8 2026-01-15 Marc.md"
    other.write_text(other.read_text().replace('box: "[[THP-1 box]]"', 'box: "[[RAW 264.7 box]]"'))
    messages = [f"{i.rel}: {i.message}" for i in run_checks(load_vault(copy)).errors]
    assert any("[[RAW 264]] points to a note that doesn't exist" in m for m in messages)
    assert any("A1 is also used by" in m for m in messages)
