from pathlib import Path
from textwrap import dedent

import pytest

from labbase.vault.reader import load_vault, split_frontmatter
from labbase.vault.validate import ERROR, WARNING, check_fields

DEMO_SCHEMAS = Path(__file__).parent.parent / "vault-demo" / "_schema"


@pytest.fixture
def vault_dir(tmp_path: Path) -> Path:
    """An empty vault using the real schemas from vault-demo."""
    (tmp_path / "_schema").mkdir()
    for f in DEMO_SCHEMAS.glob("*.yaml"):
        (tmp_path / "_schema" / f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
    return tmp_path


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(text).lstrip(), encoding="utf-8")


def issues_for(root: Path) -> list[tuple[str, str, str, str]]:
    return [(i.level, i.rel, i.field, i.message) for i in check_fields(load_vault(root))]


def test_split_frontmatter() -> None:
    assert split_frontmatter("---\na: 1\n---\nbody") == ("a: 1\n", "body")
    assert split_frontmatter("no props") == (None, "no props")
    assert split_frontmatter("---\nunterminated") == (None, "---\nunterminated")


def test_valid_notes_pass(vault_dir: Path) -> None:
    write(
        vault_dir,
        "Cell lines/THP-1.md",
        """
        ---
        id: CEL-0001
        type: cell_line
        species: Homo sapiens
        kind: line
        aliases: [THP1]
        passage_limit: 25
        ---
        # THP-1
        Free text.
    """,
    )
    write(
        vault_dir,
        "Stocks/THP-1 p8.md",
        """
        ---
        id:
        type: stock
        content: "[[THP-1]]"
        positions: [A1, B 7]
        vials_left: 2
        frozen_on: 2026-01-15
        cells_per_vial: 5e6
        ---
    """,
    )
    write(vault_dir, "README.md", "# not a record")
    write(vault_dir, "_templates/stock.md", "---\ntype: stock\n---\n")
    vault = load_vault(vault_dir)
    assert sorted(n.rel for n in vault.notes) == ["Cell lines/THP-1.md", "Stocks/THP-1 p8.md"]
    assert check_fields(vault) == []


def test_field_errors_are_specific(vault_dir: Path) -> None:
    write(
        vault_dir,
        "Stocks/bad.md",
        """
        ---
        id: CEL-0003
        type: stock
        positions: A1
        vials_left: -1
        container: jar
        frozen_on: 15/01/2026
        volume_uL: 100 µL
        frozen_by: Marc
        pasage: 3
        ---
    """,
    )
    found = {(field, msg) for _l, _r, field, msg in issues_for(vault_dir)}
    fields = {f for f, _ in found}
    assert {
        "id",
        "content",
        "positions",
        "vials_left",
        "container",
        "frozen_on",
        "volume_uL",
        "pasage",
    } <= fields
    msgs = dict(found)
    assert "start with STK-" in msgs["id"]
    assert msgs["content"] == "is required"
    assert "list" in msgs["positions"]
    assert "minimum" in msgs["vials_left"]
    assert "cryovial" in msgs["container"]
    assert "2026-01-15" in msgs["frozen_on"]
    assert "unit is in the property name" in msgs["volume_uL"]
    assert "did you mean 'passage'" in msgs["pasage"]


def test_type_problems_and_bad_yaml(vault_dir: Path) -> None:
    write(vault_dir, "Notebook/a.md", "---\ndate: 2026-01-01\n---\n")
    write(vault_dir, "Notebook/b.md", "---\ntype: experiment\n---\n")
    write(vault_dir, "Notebook/c.md", "---\ntype: [unclosed\n---\n")
    write(vault_dir, "Notebook/d.md", "just text, no properties")
    levels = {rel: (lvl, msg) for lvl, rel, _f, msg in issues_for(vault_dir)}
    assert levels["Notebook/a.md"][0] == ERROR and "missing" in levels["Notebook/a.md"][1]
    assert "unknown type 'experiment'" in levels["Notebook/b.md"][1]
    assert "can't be read" in levels["Notebook/c.md"][1]
    assert levels["Notebook/d.md"][0] == WARNING


def test_duplicate_ids_and_names(vault_dir: Path) -> None:
    note = "---\nid: SUP-0001\ntype: supplier\n---\n"
    write(vault_dir, "Suppliers/Gibco.md", note)
    write(vault_dir, "Suppliers/old/gibco.md", note)
    msgs = [msg for _l, _r, _f, msg in issues_for(vault_dir)]
    assert any("SUP-0001 is also used by" in m for m in msgs)
    assert any("ambiguous" in m for m in msgs)
