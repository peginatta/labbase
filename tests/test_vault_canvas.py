"""Generated canvases: lab map + one per freezer (JSON Canvas 1.0)."""

import json
import re
import shutil
from pathlib import Path

from labbase.vault.canvas import render_canvases
from labbase.vault.reader import load_vault

DEMO = Path(__file__).parent.parent / "vault-demo"
NODE_KEYS = {"id", "type", "x", "y", "width", "height"}


def _valid(data: dict, names: set[str]) -> list[str]:
    ids = [n["id"] for n in data["nodes"]]
    assert len(ids) == len(set(ids)), "node ids must be unique"
    linked = []
    for n in data["nodes"]:
        assert set(n) >= NODE_KEYS and n["type"] in ("text", "group")
        assert all(isinstance(n[k], int) for k in ("x", "y", "width", "height"))
        for target in re.findall(r"\[\[([^\]|]+)", n.get("text", "")):
            assert target.lower() in names, f"broken link [[{target}]]"
            linked.append(target)
    groups_first = [n["type"] for n in data["nodes"]]
    assert groups_first == sorted(groups_first, key=lambda t: t != "group")  # groups drawn below
    return linked


def test_canvases_for_demo(tmp_path: Path) -> None:
    vault_dir = tmp_path / "v"
    shutil.copytree(DEMO, vault_dir, ignore=shutil.ignore_patterns("_reports", "_maps"))
    vault = load_vault(vault_dir)
    written = render_canvases(vault)
    names = {n.name.lower() for n in vault.notes}
    lab = json.loads((vault_dir / "_maps/Lab map.canvas").read_text())
    linked = _valid(lab, names)
    boxes = {n.name for n in vault.notes if n.type == "box"}
    assert boxes <= set(linked), "every box is on the lab map"
    freezers = sorted(p.name for p in (vault_dir / "_maps/Freezers").glob("*.canvas"))
    assert "Freezer A -80.canvas" in freezers and "Fridge 4C.canvas" in freezers
    a80 = json.loads((vault_dir / "_maps/Freezers/Freezer A -80.canvas").read_text())
    _valid(a80, names)
    assert {"shelf 1 › rack 1", "shelf 2 › rack 1"} <= {
        n["label"] for n in a80["nodes"] if n["type"] == "group"
    }
    assert any(
        "THP-1 p8" in n.get("text", "") or "THP-1 box" in n.get("text", "") for n in a80["nodes"]
    )
    assert len(written) == 1 + len(freezers)
    assert render_canvases(load_vault(vault_dir)) == []  # deterministic: nothing to rewrite


def test_stale_freezer_canvas_removed(tmp_path: Path) -> None:
    vault_dir = tmp_path / "v"
    shutil.copytree(DEMO, vault_dir, ignore=shutil.ignore_patterns("_reports", "_maps"))
    render_canvases(load_vault(vault_dir))
    stale = vault_dir / "_maps/Freezers/Old freezer.canvas"
    stale.write_text("{}")
    render_canvases(load_vault(vault_dir))
    assert not stale.exists()
