"""The generated 📍 line: the full location of a note, following parent links up to the room."""

from pathlib import Path

from labbase.vault.reader import load_vault
from labbase.vault.render import WHERE_END, WHERE_START, render_where
from tests.test_vault_fields import vault_dir, write  # noqa: F401


def _lab(root: Path) -> None:
    write(root, "Locations/Lab 3260.md", "---\ntype: location\nkind: room\n---\n# Lab 3260\n")
    write(
        root,
        "Locations/Lab 3260 -20 horizontal.md",
        '---\ntype: location\nkind: freezer\nparent: "[[Lab 3260]]"\n---\n# F\n',
    )
    write(
        root,
        "Locations/Lab 3260 -20 horizontal, tower Leishmania I.md",
        '---\ntype: location\nkind: tower\nparent: "[[Lab 3260 -20 horizontal]]"\n---\n# T\n',
    )
    write(
        root,
        "Locations/Primers I.md",
        '---\ntype: box\nparent: "[[Lab 3260 -20 horizontal, tower Leishmania I]]"\n'
        "rows: 10\ncols: 10\n---\n# Primers I\n\nNotes about the box.\n",
    )
    write(
        root,
        "Primers/IST 19.md",
        '---\ntype: primer\ncode: IST 19\nlocation: "[[Primers I]]"\nposition: b9\n---\n'
        "# IST 19\n\nMy text.\n",
    )
    write(root, "Cell lines/THP-1.md", "---\ntype: cell_line\nspecies: x\nkind: line\n---\n")
    write(
        root,
        "Stocks/THP-1 p8.md",
        '---\ntype: stock\ncontent: "[[THP-1]]"\nbox: "[[Primers I]]"\npositions: [A1, A2]\n'
        "vials_left: 2\n---\n",
    )


LINE = (
    "📍 [[Lab 3260]] › [[Lab 3260 -20 horizontal|-20 horizontal]] › "
    "[[Lab 3260 -20 horizontal, tower Leishmania I|tower Leishmania I]] › [[Primers I]]"
)


def test_where_lines(vault_dir: Path) -> None:  # noqa: F811
    _lab(vault_dir)
    render_where(load_vault(vault_dir))
    primer = (vault_dir / "Primers/IST 19.md").read_text()
    assert f"{LINE} › **B9**" in primer
    assert primer.index("# IST 19") < primer.index(WHERE_START) < primer.index("My text.")
    stock = (vault_dir / "Stocks/THP-1 p8.md").read_text()
    assert f"{LINE} › **A1, A2**" in stock  # note without a title: line goes at the top
    box = (vault_dir / "Locations/Primers I.md").read_text()
    assert "📍 [[Lab 3260]] › [[Lab 3260 -20 horizontal|-20 horizontal]] › " in box
    assert "Notes about the box." in box
    assert WHERE_START not in (vault_dir / "Locations/Lab 3260.md").read_text()  # top level
    assert render_where(load_vault(vault_dir)) == []  # idempotent


def test_moving_a_box_updates_its_contents(vault_dir: Path) -> None:  # noqa: F811
    _lab(vault_dir)
    render_where(load_vault(vault_dir))
    write(vault_dir, "Locations/Basement.md", "---\ntype: location\nkind: room\n---\n# B\n")
    box = vault_dir / "Locations/Primers I.md"
    box.write_text(
        box.read_text().replace(
            'parent: "[[Lab 3260 -20 horizontal, tower Leishmania I]]"', 'parent: "[[Basement]]"'
        )
    )
    render_where(load_vault(vault_dir))
    primer = (vault_dir / "Primers/IST 19.md").read_text()
    assert "📍 [[Basement]] › [[Primers I]] › **B9**" in primer
    assert primer.count(WHERE_START) == primer.count(WHERE_END) == 1


def test_line_removed_when_item_has_no_place(vault_dir: Path) -> None:  # noqa: F811
    _lab(vault_dir)
    render_where(load_vault(vault_dir))
    path = vault_dir / "Primers/IST 19.md"
    path.write_text(path.read_text().replace('location: "[[Primers I]]"\nposition: b9\n', ""))
    render_where(load_vault(vault_dir))
    text = path.read_text()
    assert WHERE_START not in text and "My text." in text and text.startswith("---\n")
