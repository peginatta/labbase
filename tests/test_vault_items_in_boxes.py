"""Single items (e.g. primers) placed in a box via `location` + `position`."""

from pathlib import Path

from labbase.vault.check import run_checks
from labbase.vault.reader import load_vault
from labbase.vault.render import render_box_maps
from tests.test_vault_fields import vault_dir, write  # noqa: F401


def _setup(root: Path) -> None:
    write(root, "Locations/Tower.md", "---\ntype: location\nkind: tower\n---\n")
    write(
        root,
        "Locations/Primers I.md",
        '---\ntype: box\nparent: "[[Tower]]"\nrows: 10\ncols: 10\n---\n# Primers I\n',
    )
    write(root, "Cell lines/THP-1.md", "---\ntype: cell_line\nspecies: x\nkind: line\n---\n")
    for code, pos in [("IST 1", "A1"), ("IST 2", "A2")]:
        write(
            root,
            f"Primers/{code}.md",
            f'---\ntype: primer\ncode: {code}\nlocation: "[[Primers I]]"\nposition: {pos}\n---\n',
        )


def messages(root: Path) -> list[str]:
    return [f"{i.rel} › {i.field}: {i.message}" for i in run_checks(load_vault(root)).issues]


def test_primers_in_box_map(vault_dir: Path) -> None:  # noqa: F811
    _setup(vault_dir)
    assert messages(vault_dir) == []
    render_box_maps(load_vault(vault_dir))
    text = (vault_dir / "Locations/Primers I.md").read_text()
    assert "(2 of 100 positions used)" in text
    assert "[[IST 1\\|IST 1]]" in text and "[[IST 2\\|IST 2]]" in text


def test_primer_and_stock_cannot_share_a_position(vault_dir: Path) -> None:  # noqa: F811
    _setup(vault_dir)
    write(
        vault_dir,
        "Stocks/s.md",
        '---\ntype: stock\ncontent: "[[THP-1]]"\nbox: "[[Primers I]]"\npositions: [A2]\n'
        "vials_left: 1\n---\n",
    )
    write(
        vault_dir,
        "Primers/IST 3.md",
        '---\ntype: primer\ncode: IST 3\nlocation: "[[Primers I]]"\nposition: K1\n---\n',
    )
    write(
        vault_dir,
        "Primers/IST 4.md",
        '---\ntype: primer\ncode: IST 4\nlocation: "[[Tower]]"\nposition: A5\n---\n',
    )
    msgs = messages(vault_dir)
    assert any("A2 is also used by [[IST 2]]" in m for m in msgs)
    assert any("IST 3.md › position: K1 is outside [[Primers I]] (10×10)" in m for m in msgs)
    assert any("IST 4.md › position: positions need a box in `location`" in m for m in msgs)


def test_not_found_primer_frees_its_position(vault_dir: Path) -> None:  # noqa: F811
    _setup(vault_dir)
    write(
        vault_dir,
        "Primers/IST 9.md",
        '---\ntype: primer\ncode: IST 9\nlocation: "[[Primers I]]"\nposition: A1\n'
        "status: not found\n---\n",
    )
    assert messages(vault_dir) == []
