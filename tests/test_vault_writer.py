from datetime import date

from labbase.vault.reader import read_note
from labbase.vault.writer import frontmatter, scalar, write_note


def test_scalars_round_trip(tmp_path) -> None:
    props = {
        "type": "stock",
        "content": "[[THP-1]]",
        "positions": ["A1", "B7"],
        "vials_left": 2,
        "frozen_on": date(2026, 1, 15),
        "cells_per_vial": 5e6,
        "conc_mM": 10.5,
        "species": "Homo sapiens",
        "lot": "007",
        "note": "yes",
        "code": "LB-A-001",
        "who_code": "MCAN/ES/98/LLM-877",
        "comp": "[[FBS]] 10 %",
        "reference": True,
        "name": "Schneider's: complete",
        "temp": -80,
    }
    path = write_note(tmp_path / "x.md", props, "# Body\n")
    assert read_note(path, tmp_path).props == {**props, "cells_per_vial": 5000000}
    assert scalar(5e6) == "5000000" and scalar("007") == '"007"'
    assert frontmatter({"a": []}) == "---\na: []\n---\n"
