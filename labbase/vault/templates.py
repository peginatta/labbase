"""Note templates generated from schemas (`_templates/<type>.md`) and `labbase new`."""

import re
from datetime import date
from pathlib import Path

from labbase.vault.ids import format_id, next_numbers
from labbase.vault.model import Schema, Vault

TEMPLATE_DIR = "_templates"
BAD_FILENAME = re.compile(r'[\\/:*?"<>|#^\[\]]')


def _yaml_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return "[" + ", ".join(str(v) for v in value) + "]"
    return str(value)


def template_text(schema: Schema, created: str = '"{{date}}"', title: str = "{{title}}") -> str:
    """Frontmatter listing every property of the type (empty unless it has a default)."""
    lines = ["---", "id:", f"type: {schema.type}", "aliases:", "tags:"]
    for name, f in schema.fields.items():
        value = _yaml_value(f.default)
        lines.append(f"{name}: {value}".rstrip())
    lines += [f"created: {created}", "---", f"# {title}", ""]
    if schema.description:
        lines += [f"<!-- {schema.type}: {' '.join(schema.description.split())} -->", ""]
    if schema.body:
        lines += [schema.body.rstrip("\n"), ""]
    return "\n".join(lines)


def write_templates(vault: Vault) -> list[Path]:
    out = []
    folder = vault.root / TEMPLATE_DIR
    folder.mkdir(exist_ok=True)
    for schema in sorted(vault.schemas.values(), key=lambda s: s.type):
        path = folder / f"{schema.type}.md"
        path.write_text(template_text(schema), encoding="utf-8")
        out.append(path)
    return out


def new_note(vault: Vault, type_: str, name: str, today: date | None = None) -> Path:
    schema = vault.schemas.get(type_)
    if schema is None:
        raise ValueError(f"Unknown type '{type_}'. Known: {', '.join(sorted(vault.schemas))}")
    name = name.strip()
    if not name or BAD_FILENAME.search(name):
        raise ValueError("Name can't be empty or contain \\ / : * ? \" < > | # ^ [ ]")
    if name.lower() in vault.by_name():
        raise ValueError(f"A note called '{name}' already exists")
    path = vault.root / (schema.folder or ".") / f"{name}.md"
    text = template_text(schema, created=(today or date.today()).isoformat(), title=name)
    if schema.id_prefix:
        new_id = format_id(schema.id_prefix, next_numbers(vault)[schema.id_prefix])
        text = text.replace("---\nid:\n", f"---\nid: {new_id}\n", 1)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
