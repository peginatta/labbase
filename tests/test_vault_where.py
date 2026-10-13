"""Generated location: plain `where` property + clickable 📍 line, from the parent links."""

from pathlib import Path

from labbase.vault.check import run_checks
from labbase.vault.reader import load_vault, read_note
from labbase.vault.render import WHERE_END, WHERE_START, render_where, set_property_line
from tests.test_vault_fields import vault_dir, write  # noqa: F401

TOWER = "Lab 3260 › -20 horizontal › tower Leishmania I"
LINE = (
    "📍 [[Lab 3260]] › [[Lab 3260 -20 horizontal|-20 horizontal]] › "
    "[[Lab 3260 -20 horizontal, tower Leishmania I|tower Leishmania I]] › [[Primers I]]"
)


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
        "rows: 10\ncols: 10\n---\n# Primers I\n",
    )
    write(
        root,
        "Primers/IST 19.md",
        '---\ntype: primer\ncode: IST 19\nlocation: "[[Primers I]]"\nposition: b9\n'
        "status: in stock\n---\n# IST 19\n\nMy text.\n",
    )
    write(root, "Cell lines/THP-1.md", "---\ntype: cell_line\nspecies: x\nkind: line\n---\n")
    write(
        root,
        "Stocks/THP-1 p8.md",
        '---\ntype: stock\ncontent: "[[THP-1]]"\nbox: "[[Primers I]]"\npositions: [A1, A2]\n'
        "vials_left: 2\n---\n",
    )


def where(root: Path, rel: str) -> str | None:
    return read_note(root / rel, root).props.get("where")


def test_property_and_line(vault_dir: Path) -> None:  # noqa: F811
    _lab(vault_dir)
    render_where(load_vault(vault_dir))
    assert where(vault_dir, "Primers/IST 19.md") == f"{TOWER} › Primers I › B9"
    assert where(vault_dir, "Stocks/THP-1 p8.md") == f"{TOWER} › Primers I › A1, A2"
    assert where(vault_dir, "Locations/Primers I.md") == TOWER
    assert where(vault_dir, "Locations/Lab 3260.md") is None  # top level
    text = (vault_dir / "Primers/IST 19.md").read_text()
    assert 'position: b9\nwhere: "' in text  # property right after the location properties
    assert f"{WHERE_START}\n{LINE} › **B9**\n{WHERE_END}" in text
    assert text.index("# IST 19") < text.index(WHERE_START) < text.index("My text.")
    stock = (vault_dir / "Stocks/THP-1 p8.md").read_text()
    assert f"{LINE} › **A1, A2**" in stock  # no title: line goes at the top of the text
    assert WHERE_START not in (vault_dir / "Locations/Lab 3260.md").read_text()
    assert render_where(load_vault(vault_dir)) == []  # idempotent
    assert run_checks(load_vault(vault_dir)).issues == []


def test_edits_are_put_back(vault_dir: Path) -> None:  # noqa: F811
    _lab(vault_dir)
    render_where(load_vault(vault_dir))
    path = vault_dir / "Primers/IST 19.md"
    text = path.read_text()
    tampered = text.replace("› **B9**", "› **Z1**").replace(
        f'where: "{TOWER} › Primers I › B9"', 'where: "somewhere"'
    )
    path.write_text(tampered)
    msgs = [i.message for i in run_checks(load_vault(vault_dir)).warnings]
    assert any("out of date" in m for m in msgs)
    render_where(load_vault(vault_dir))
    assert path.read_text() == text


def test_moving_a_box_and_removing_a_place(vault_dir: Path) -> None:  # noqa: F811
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
    path = vault_dir / "Primers/IST 19.md"
    assert where(vault_dir, "Primers/IST 19.md") == "Basement › Primers I › B9"
    assert "📍 [[Basement]] › [[Primers I]] › **B9**" in path.read_text()
    path.write_text(path.read_text().replace('location: "[[Primers I]]"\nposition: b9\n', ""))
    render_where(load_vault(vault_dir))
    text = path.read_text()
    assert where(vault_dir, "Primers/IST 19.md") is None
    assert WHERE_START not in text and text.endswith("# IST 19\n\nMy text.\n")


def test_set_property_line() -> None:
    text = "---\na: 1\nwhere: old\nb: [x,\n  y]\n---\nbody\n"
    assert set_property_line(text, "where", None) == "---\na: 1\nb: [x,\n  y]\n---\nbody\n"
    assert set_property_line(text, "where", "X › Y") == (
        '---\na: 1\nwhere: "X › Y"\nb: [x,\n  y]\n---\nbody\n'
    )
    assert set_property_line("---\na: 1\n---\n", "where", "Z") == "---\na: 1\nwhere: Z\n---\n"


def test_box_note_order_and_empty_map(vault_dir: Path) -> None:  # noqa: F811
    from labbase.vault.render import END, START, render_box_maps

    _lab(vault_dir)
    write(
        vault_dir,
        "Locations/Empty box.md",
        '---\ntype: box\nparent: "[[Lab 3260 -20 horizontal, tower Leishmania I]]"\n---\n'
        "# Empty box\n\nGuide text.\n",
    )
    render_box_maps(load_vault(vault_dir))  # map first, location line second: wrong order
    render_where(load_vault(vault_dir))
    render_box_maps(load_vault(vault_dir))  # ...is repaired
    for rel in ("Locations/Empty box.md", "Locations/Primers I.md"):
        text = (vault_dir / rel).read_text()
        assert text.index(WHERE_END) < text.index(START) < text.index(END), rel
    empty = (vault_dir / "Locations/Empty box.md").read_text()
    assert "No positions recorded for this box yet" in empty and "| **A** |" not in empty
    assert empty.rstrip().endswith("Guide text.")
    full = (vault_dir / "Locations/Primers I.md").read_text()
    assert "(3 of 100 positions used)" in full  # IST 19 + two stock vials
    assert (
        render_box_maps(load_vault(vault_dir)) == [] and render_where(load_vault(vault_dir)) == []
    )
