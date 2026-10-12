"""Plain data structures for vault notes and record-type schemas."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

LINK_RE = re.compile(r"^\[\[([^\[\]|#]+)(?:#[^\[\]|]*)?(?:\|[^\[\]]*)?\]\]$")
POSITION_RE = re.compile(r"^([A-Za-z])\s*0*(\d{1,2})$")
ID_RE = re.compile(r"^([A-Z]{2,8})-(\d{4,})$")


def link_target(value: Any) -> str | None:
    """'[[THP-1|cells]]' -> 'THP-1'; anything else -> None."""
    if isinstance(value, str):
        m = LINK_RE.match(value.strip())
        if m:
            return m.group(1).strip()
    return None


@dataclass
class Field:
    name: str
    kind: str = "text"  # text|integer|number|date|boolean|choice|link|list|id|position
    of: str = "text"  # element kind for lists
    to: list[str] = field(default_factory=list)  # allowed record types for links
    options: list[str] = field(default_factory=list)
    required: bool = False
    min: float | None = None
    max: float | None = None
    default: Any = None
    help: str = ""


@dataclass
class Schema:
    type: str
    id_prefix: str = ""
    folder: str = ""
    description: str = ""
    body: str = ""  # Markdown added below the title in templates (e.g. a Bases table)
    fields: dict[str, Field] = field(default_factory=dict)


@dataclass
class Note:
    path: Path  # absolute
    rel: str  # path relative to the vault root, e.g. "Cell lines/THP-1.md"
    props: dict[str, Any]
    body: str
    parse_error: str = ""

    @property
    def name(self) -> str:
        """Obsidian link name: the filename without .md."""
        return self.path.stem

    @property
    def type(self) -> str:
        t = self.props.get("type")
        return t if isinstance(t, str) else ""

    @property
    def id(self) -> str:
        v = self.props.get("id")
        return v.strip() if isinstance(v, str) else ""


DEFAULT_SETTINGS: dict[str, Any] = {
    "stale_days": 30,
    "expiry_warning_days": 30,
    "autolock_days": 7,
    "review_steps": ["author", "peer"],
}


@dataclass
class Vault:
    root: Path
    notes: list[Note]
    schemas: dict[str, Schema]
    common: Schema
    settings: dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_SETTINGS))

    def by_name(self) -> dict[str, list[Note]]:
        """Notes by lower-cased link name (Obsidian resolves links case-insensitively)."""
        index: dict[str, list[Note]] = {}
        for n in self.notes:
            index.setdefault(n.name.lower(), []).append(n)
        return index

    def resolve(self, value: Any) -> Note | None:
        target = link_target(value)
        if target is None:
            return None
        found = self.by_name().get(target.lower(), [])
        if not found:  # a link may include a folder path: [[Cell lines/THP-1]]
            found = [n for n in self.notes if n.rel[:-3].lower() == target.lower()]
        return found[0] if len(found) == 1 else None
