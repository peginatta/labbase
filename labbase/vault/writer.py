"""Write notes with flat, Obsidian-friendly frontmatter (no YAML library quirks)."""

import json
import re
from datetime import date
from pathlib import Path
from typing import Any

_PLAIN = re.compile(r"^[A-Za-z0-9À-ɏ_.,()/%+°µ×' -]*$")
_LOOKS_SPECIAL = re.compile(
    r"^(true|false|null|~|yes|no|on|off|[-+]?[\d.]+(e[-+]?\d+)?|\d{4}-\d\d-\d\d)$", re.I
)


def scalar(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return str(int(value)) if value.is_integer() else repr(value)
    if isinstance(value, date):
        return value.isoformat()
    text = str(value)
    if (
        text
        and _PLAIN.match(text)
        and not _LOOKS_SPECIAL.match(text)
        and text == text.strip()
        and not text.startswith(("-", "'"))
    ):
        return text
    return json.dumps(text, ensure_ascii=False)


def frontmatter(props: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in props.items():
        if isinstance(value, list):
            lines.append(f"{key}: [{', '.join(scalar(v) for v in value)}]")
        else:
            lines.append(f"{key}: {scalar(value)}".rstrip())
    lines.append("---")
    return "\n".join(lines) + "\n"


def link(name: str) -> str:
    return f"[[{name}]]"


def write_note(path: Path, props: dict[str, Any], body: str = "") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    clean = {k: v for k, v in props.items() if v not in (None, "", [])}
    path.write_text(frontmatter(clean) + body, encoding="utf-8")
    return path
