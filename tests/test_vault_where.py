"""The generated `where` property: full location, following parent links up to the room."""

from pathlib import Path

from labbase.vault.check import run_checks
from labbase.vault.reader import load_vault, read_note
from labbase.vault.render import WHERE_END, WHERE_START, render_where, set_property_line
from tests.test_vault_fields import vault_dir, write  # noqa: F401

TOWER = "Lab 3260 › -20 horizontal › tower Leishmania I"


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


def test_where_property(vault_dir: Path) -> None:  # noqa: F811
    _lab(vault_dir)
    render_where(load_vault(vault_dir))
    assert where(vault_dir, "Primers/IST 19.md") == f"{TOWER} › Primers I › B9"
    assert where(vault_dir, "Stocks/THP-1 p8.md") == f"{TOWER} › Primers I › A1, A2"
    assert where(vault_dir, "Locations/Primers I.md") == TOWER
    assert where(vault_dir, "Locations/Lab 3260.md") is None  # top level
    text = (vault_dir / "Primers/IST 19.md").read_text()
    assert 'position: b9\nwhere: "' in text  # placed right after the location properties
    assert text.endswith("# IST 19\n\nMy text.\n")
    assert render_where(load_vault(vault_dir)) == []  # idempotent
    assert run_checks(load_vault(vault_dir)).issues == []


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
    msgs = [i.message for i in run_checks(load_vault(vault_dir)).warnings]
    assert any("out of date" in m for m in msgs)  # stale until the next render
    render_where(load_vault(vault_dir))
    assert where(vault_dir, "Primers/IST 19.md") == "Basement › Primers I › B9"
    path = vault_dir / "Primers/IST 19.md"
    path.write_text(path.read_text().replace('location: "[[Primers I]]"\nposition: b9\n', ""))
    render_where(load_vault(vault_dir))
    assert where(vault_dir, "Primers/IST 19.md") is None


def test_migrates_old_in_text_line(vault_dir: Path) -> None:  # noqa: F811
    _lab(vault_dir)
    path = vault_dir / "Primers/IST 19.md"
    path.write_text(
        path.read_text().replace(
            "# IST 19\n", f"# IST 19\n\n{WHERE_START}\n📍 old line\n{WHERE_END}\n"
        )
    )
    render_where(load_vault(vault_dir))
    text = path.read_text()
    assert WHERE_START not in text and "📍" not in text and "My text." in text


def test_set_property_line() -> None:
    text = "---\na: 1\nwhere: old\nb: [x,\n  y]\n---\nbody\n"
    assert set_property_line(text, "where", None) == "---\na: 1\nb: [x,\n  y]\n---\nbody\n"
    assert set_property_line(text, "where", "X › Y") == (
        '---\na: 1\nwhere: "X › Y"\nb: [x,\n  y]\n---\nbody\n'
    )
    assert set_property_line("---\na: 1\n---\n", "where", "Z") == "---\na: 1\nwhere: Z\n---\n"
