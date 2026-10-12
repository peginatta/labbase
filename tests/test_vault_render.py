import json
from pathlib import Path

from labbase.vault.reader import load_vault
from labbase.vault.render import END, START, render_box_maps, short_label, write_obsidian_types
from tests.test_vault_fields import vault_dir, write  # noqa: F401


def test_box_map_is_generated_and_idempotent(vault_dir: Path) -> None:  # noqa: F811
    write(vault_dir, "Locations/F.md", "---\ntype: location\nkind: freezer\n---\n")
    write(
        vault_dir,
        "Locations/Small box.md",
        '---\ntype: box\nparent: "[[F]]"\nrows: 2\ncols: 3\n---\n# Small box\n\nMy notes.\n',
    )
    write(vault_dir, "Cell lines/THP-1.md", "---\ntype: cell_line\nspecies: x\nkind: line\n---\n")
    write(
        vault_dir,
        "Stocks/THP-1 p8 2026-01-15 Marc.md",
        '---\ntype: stock\ncontent: "[[THP-1]]"\nbox: "[[Small box]]"\npositions: [B3]\n---\n',
    )
    assert render_box_maps(load_vault(vault_dir)) == [vault_dir / "Locations/Small box.md"]
    text = (vault_dir / "Locations/Small box.md").read_text()
    assert text.index("# Small box") < text.index(START) < text.index("My notes.")
    assert "(1 of 6 positions used)" in text
    assert "| **B** | ·   | ·   | [[THP-1 p8 2026-01-15 Marc\\|THP-1 p8]] |" in text
    assert render_box_maps(load_vault(vault_dir)) == []  # nothing changed -> no rewrite
    (vault_dir / "Stocks/THP-1 p8 2026-01-15 Marc.md").write_text(
        '---\ntype: stock\ncontent: "[[THP-1]]"\nstate: finished\n---\n'
    )
    render_box_maps(load_vault(vault_dir))
    text = (vault_dir / "Locations/Small box.md").read_text()
    assert text.count(START) == text.count(END) == 1 and "(0 of 6" in text


def test_short_label() -> None:
    class N:
        name = "Li JPCM5 p3 2026-03-12 Lucía backup"

    assert short_label(N()) == "Li JPCM5 p3"


def test_obsidian_types(vault_dir: Path) -> None:  # noqa: F811
    path = write_obsidian_types(load_vault(vault_dir))
    types = json.loads(path.read_text())["types"]
    assert types["frozen_on"] == "date" and types["vials_left"] == "number"
    assert types["positions"] == "multitext" and types["reference"] == "checkbox"
    assert types["aliases"] == "aliases"
