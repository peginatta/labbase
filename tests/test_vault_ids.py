from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from labbase.cli import cli
from labbase.vault.check import run_checks
from labbase.vault.ids import fill_ids, set_id_in_text
from labbase.vault.reader import load_vault
from labbase.vault.templates import new_note, write_templates
from tests.test_vault_fields import vault_dir, write  # noqa: F401


def test_set_id_in_text_preserves_everything_else() -> None:
    text = "---\nid:\ntype: strain  # keep comment\nspecies: L. major\n---\n# Body\n"
    assert set_id_in_text(text, "STR-0003") == (
        "---\nid: STR-0003\ntype: strain  # keep comment\nspecies: L. major\n---\n# Body\n"
    )
    assert set_id_in_text("---\ntype: x\n---\n", "A-0001") == "---\nid: A-0001\ntype: x\n---\n"
    assert set_id_in_text('---\nid: ""\n---\n', "A-0001") == "---\nid: A-0001\n---\n"
    with pytest.raises(ValueError):
        set_id_in_text("---\nid: X-0001\n---\n", "A-0001")


def test_fill_ids_continues_numbering(vault_dir: Path) -> None:  # noqa: F811
    write(vault_dir, "Strains/A.md", "---\nid: STR-0007\ntype: strain\nspecies: x\n---\n")
    write(vault_dir, "Strains/B.md", "---\ntype: strain\nspecies: x\n---\n")
    write(vault_dir, "Strains/C.md", "---\nid:\ntype: strain\nspecies: x\n---\n")
    write(vault_dir, "Notebook/free.md", "no properties")
    assert [(a.rel, a.new_id) for a in fill_ids(load_vault(vault_dir), dry_run=True)] == [
        ("Strains/B.md", "STR-0008"),
        ("Strains/C.md", "STR-0009"),
    ]
    assert (vault_dir / "Strains/B.md").read_text().startswith("---\ntype")  # dry run: untouched
    fill_ids(load_vault(vault_dir))
    ids = {n.name: n.id for n in load_vault(vault_dir).notes if n.id}
    assert ids == {"A": "STR-0007", "B": "STR-0008", "C": "STR-0009"}
    assert fill_ids(load_vault(vault_dir)) == []


def test_templates_and_new_note_are_valid(vault_dir: Path) -> None:  # noqa: F811
    vault = load_vault(vault_dir)
    paths = write_templates(vault)
    assert (vault_dir / "_templates" / "stock.md") in paths
    stock_tpl = (vault_dir / "_templates" / "stock.md").read_text()
    assert "content:" in stock_tpl and 'created: "{{date}}"' in stock_tpl
    assert "rows: 9" in (vault_dir / "_templates" / "box.md").read_text()

    path = new_note(vault, "cell_line", "THP-1", today=date(2026, 10, 12))
    assert path == vault_dir / "Cell lines" / "THP-1.md"
    text = path.read_text()
    assert text.startswith("---\nid: CEL-0001\ntype: cell_line\n") and "# THP-1" in text
    # a freshly created note only lacks the required facts a person must type in
    issues = run_checks(load_vault(vault_dir)).issues
    assert {(i.field, i.message) for i in issues} == {
        ("species", "is required"),
        ("kind", "is required"),
    }
    with pytest.raises(ValueError, match="already exists"):
        new_note(load_vault(vault_dir), "cell_line", "thp-1")
    with pytest.raises(ValueError, match="Unknown type"):
        new_note(vault, "plasmid", "pX")


def test_cli_new_and_fill_ids(vault_dir: Path) -> None:  # noqa: F811
    runner = CliRunner()
    out = runner.invoke(cli, ["new", "compound", "Miltefosine", "--vault", str(vault_dir)])
    assert out.exit_code == 0, out.output
    write(vault_dir, "Compounds/AmB.md", "---\ntype: compound\n---\n")
    out = runner.invoke(cli, ["fill-ids", str(vault_dir)])
    assert "CMP-0002  Compounds/AmB.md" in out.output
