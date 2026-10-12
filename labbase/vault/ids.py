"""Assign stable IDs (`CEL-0001`) to notes that have none, editing only the `id:` line."""

import re
from dataclasses import dataclass
from pathlib import Path

from labbase.vault.model import ID_RE, Vault
from labbase.vault.reader import split_frontmatter

ID_LINE_RE = re.compile(r"^id:[ \t]*(?:\"\"|''|null|~)?[ \t]*$")


def next_numbers(vault: Vault) -> dict[str, int]:
    """Next free number per prefix (max used + 1)."""
    used: dict[str, int] = {}
    for n in vault.notes:
        m = ID_RE.match(n.id)
        if m:
            used[m.group(1)] = max(used.get(m.group(1), 0), int(m.group(2)))
    return {
        prefix: used.get(prefix, 0) + 1
        for prefix in {s.id_prefix for s in vault.schemas.values()} | set(used)
    }


def format_id(prefix: str, number: int) -> str:
    return f"{prefix}-{number:04d}"


def set_id_in_text(text: str, new_id: str) -> str:
    """Put `id: NEW` into the frontmatter: fill an empty `id:` line or add one at the top."""
    fm, _body = split_frontmatter(text)
    if fm is None:
        raise ValueError("note has no properties")
    lines = text.splitlines(keepends=True)
    end = 1 + len(fm.splitlines())  # index of the closing '---'
    for i in range(1, end):
        if ID_LINE_RE.match(lines[i].rstrip("\r\n")):
            newline = "\r\n" if lines[i].endswith("\r\n") else "\n"
            lines[i] = f"id: {new_id}{newline}"
            return "".join(lines)
        if lines[i].startswith("id:"):
            raise ValueError("note already has an id")
    lines.insert(1, f"id: {new_id}\n")
    return "".join(lines)


@dataclass
class Assigned:
    rel: str
    new_id: str


def fill_ids(vault: Vault, dry_run: bool = False) -> list[Assigned]:
    counters = next_numbers(vault)
    assigned: list[Assigned] = []
    for note in sorted(vault.notes, key=lambda n: n.rel):
        schema = vault.schemas.get(note.type)
        if schema is None or not schema.id_prefix or note.id or note.parse_error:
            continue
        new_id = format_id(schema.id_prefix, counters[schema.id_prefix])
        counters[schema.id_prefix] += 1
        if not dry_run:
            path: Path = note.path
            path.write_text(
                set_id_in_text(path.read_text(encoding="utf-8"), new_id), encoding="utf-8"
            )
        assigned.append(Assigned(note.rel, new_id))
    return assigned
