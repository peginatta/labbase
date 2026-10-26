"""Generated usage log in protocols (replaces the Dataview view)."""

from pathlib import Path

from labbase.vault.reader import load_vault
from labbase.vault.render import USAGE_END, USAGE_START, render_usage
from tests.test_vault_fields import vault_dir, write  # noqa: F401

PROTOCOL = (
    "---\ntype: protocol\nstatus: draft\n---\n# BMDM\n\nIntro.\n\n## Usage log\n\n"
    f"{USAGE_START}\n{USAGE_END}\n\n## Procedure\n1. Step.\n"
)


def _entry(root: Path, name: str, date: str, body: str) -> None:
    write(
        root,
        f"Notebook/{name}.md",
        f"---\ntype: note\ndate: {date}\nauthor: Paolo\n---\n# {name}\n\n{body}\n",
    )


def test_usage_log(vault_dir: Path) -> None:  # noqa: F811
    write(vault_dir, "Protocols/BMDM - extraction.md", PROTOCOL)
    _entry(vault_dir, "Day A", "2026-10-20", "- Followed [[BMDM - extraction]] for mouse 3.")
    _entry(
        vault_dir,
        "Day B",
        "2026-10-22",
        "- [[BMDM - extraction#E. Differentiation|BMDM]] change:: spin 600 g",
    )
    _entry(vault_dir, "Day C", "2026-10-21", "Unrelated [[Other protocol]].")
    _entry(
        vault_dir, "Day D", "2026-10-23", "- [[BMDM - extraction]]: usamos 25 ng/mL en lugar de 10"
    )
    assert render_usage(load_vault(vault_dir)) == [vault_dir / "Protocols/BMDM - extraction.md"]
    text = (vault_dir / "Protocols/BMDM - extraction.md").read_text()
    block = text.split(USAGE_START)[1].split(USAGE_END)[0]
    lines = [ln for ln in block.splitlines() if ln.strip()]
    assert [ln.split(" · ")[0] for ln in lines] == ["- 2026-10-23", "- 2026-10-22", "- 2026-10-20"]
    assert "[[Day B]]" in lines[1] and lines[1].endswith("⚠️")  # change:: field
    assert lines[0].endswith("⚠️")  # "en lugar de" = change word
    assert not lines[2].endswith("⚠️")
    assert text.endswith("## Procedure\n1. Step.\n")  # rest of the note untouched
    assert render_usage(load_vault(vault_dir)) == []  # idempotent


def test_unused_and_missing_markers(vault_dir: Path) -> None:  # noqa: F811
    write(vault_dir, "Protocols/P.md", PROTOCOL.replace("# BMDM", "# P"))
    write(vault_dir, "Protocols/Q.md", "---\ntype: protocol\n---\n# Q\n\nNo usage section.\n")
    render_usage(load_vault(vault_dir))
    assert "*Not used in any notebook entry yet.*" in (vault_dir / "Protocols/P.md").read_text()
    q = (vault_dir / "Protocols/Q.md").read_text()
    assert q.startswith("---\ntype: protocol\n---\n# Q\n\nNo usage section.\n\n## Usage log\n")
