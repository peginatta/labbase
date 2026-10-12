from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from labbase.cli import cli
from labbase.vault.check import run_checks, write_report
from labbase.vault.reader import load_vault
from labbase.vault.status import Status
from tests.test_vault_fields import vault_dir, write  # noqa: F401  (fixture reuse)

TODAY = date(2026, 10, 12)


@pytest.fixture
def lab(vault_dir: Path) -> Path:  # noqa: F811
    write(
        vault_dir,
        "Locations/Freezer A.md",
        "---\ntype: location\nkind: freezer\ntemperature_C: -80\n---\n",
    )
    write(vault_dir, "Locations/THP-1 box.md", '---\ntype: box\nparent: "[[Freezer A]]"\n---\n')
    write(vault_dir, "Locations/Fridge.md", "---\ntype: location\nkind: fridge\n---\n")
    write(
        vault_dir,
        "Cell lines/THP-1.md",
        "---\ntype: cell_line\nspecies: Homo sapiens\nkind: line\n---\n",
    )
    write(vault_dir, "Items/DMEM.md", "---\ntype: item\nunit: mL\nreorder_at: 600\n---\n")
    write(
        vault_dir,
        "Stocks/THP-1 p8.md",
        """
        ---
        type: stock
        content: "[[THP-1]]"
        box: "[[THP-1 box]]"
        positions: [A1, a2]
        vials_left: 2
        ---
    """,
    )
    write(
        vault_dir,
        "Stocks/DMEM lot 1.md",
        """
        ---
        type: stock
        content: "[[DMEM]]"
        location: "[[Fridge]]"
        vials_left: 1
        volume_mL: 500
        last_checked: 2026-10-01
        expiry: 2026-10-20
        ---
    """,
    )
    return vault_dir


def messages(root: Path) -> list[str]:
    return [f"{i.field}: {i.message}" for i in run_checks(load_vault(root), TODAY).issues]


def test_clean_lab_and_statuses(lab: Path) -> None:
    result = run_checks(load_vault(lab), TODAY)
    assert result.issues == []
    by_name = {s.note.name: s for s in result.statuses}
    assert by_name["THP-1 p8"].status == Status.OK
    dmem = by_name["DMEM lot 1"]
    assert dmem.status == Status.OK and dmem.expires_soon
    (total,) = result.totals
    assert (total.total, total.unit, total.low) == (500, "mL", True)


def test_broken_and_wrong_links(lab: Path) -> None:
    write(lab, "Stocks/x.md", '---\ntype: stock\ncontent: "[[THP1]]"\nbox: "[[Freezer A]]"\n---\n')
    msgs = messages(lab)
    assert "content: [[THP1]] points to a note that doesn't exist" in msgs
    assert "box: [[Freezer A]] is a location; expected box" in msgs


def test_double_booking_grid_and_counts(lab: Path) -> None:
    write(
        lab,
        "Stocks/THP-1 p9.md",
        """
        ---
        type: stock
        content: "[[THP-1]]"
        box: "[[THP-1 box]]"
        positions: [A1, J1, B2, B2]
        vials_left: 3
        ---
    """,
    )
    msgs = messages(lab)
    assert any("A1 is also used by [[THP-1 p8]]" in m for m in msgs)
    assert any("J1 is outside [[THP-1 box]] (9×9)" in m for m in msgs)
    assert any("B2 is listed twice" in m for m in msgs)
    assert any("vials_left: says 3 but 2 positions" in m for m in msgs)


def test_finished_stock_frees_positions(lab: Path) -> None:
    write(
        lab,
        "Stocks/old.md",
        """
        ---
        type: stock
        content: "[[THP-1]]"
        box: "[[THP-1 box]]"
        positions: [A1]
        state: finished
        ---
    """,
    )
    result = run_checks(load_vault(lab), TODAY)
    assert not result.errors
    assert any("finished but still lists positions" in i.message for i in result.warnings)
    assert {s.note.name: s.status for s in result.statuses}["old"] == Status.OUT


def test_expired_stale_low(lab: Path) -> None:
    write(
        lab,
        "Stocks/DMEM lot 0.md",
        '---\ntype: stock\ncontent: "[[DMEM]]"\nlocation: "[[Fridge]]"\nexpiry: 2026-01-01\n---\n',
    )
    write(
        lab,
        "Stocks/DMEM lot 2.md",
        '---\ntype: stock\ncontent: "[[DMEM]]"\nlocation: "[[Fridge]]"\n'
        "last_checked: 2026-08-01\n---\n",
    )
    write(
        lab,
        "Stocks/THP-1 p3.md",
        '---\ntype: stock\ncontent: "[[THP-1]]"\nlocation: "[[Freezer A]]"\nstate: low\n---\n',
    )
    st = {s.note.name: (s.status, s.reason) for s in run_checks(load_vault(lab), TODAY).statuses}
    assert st["DMEM lot 0"] == (Status.EXPIRED, "expired 2026-01-01")
    assert st["DMEM lot 2"] == (Status.STALE, "last checked 2026-08-01")
    assert st["THP-1 p3"] == (Status.LOW, "marked low")


def test_report_and_cli(lab: Path) -> None:
    write(lab, "Stocks/x.md", '---\ntype: stock\ncontent: "[[Nope]]"\n---\n')
    vault = load_vault(lab)
    path = write_report(vault, run_checks(vault, TODAY), TODAY)
    text = path.read_text()
    assert "❌" in text and "[[Stocks/x|x]]" in text and "## Reorder" in text
    assert all(not n.rel.startswith("_reports") for n in load_vault(lab).notes)
    out = CliRunner().invoke(cli, ["check", str(lab), "--no-report"])
    assert out.exit_code == 1 and "doesn't exist" in out.output and "1 errors" in out.output
