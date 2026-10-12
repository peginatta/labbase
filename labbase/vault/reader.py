"""Load a vault: schemas from `_schema/`, notes from every other folder."""

from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from labbase.vault.model import DEFAULT_SETTINGS, Field, Note, Schema, Vault

SCHEMA_DIR = "_schema"


def _yaml() -> YAML:
    return YAML(typ="safe", pure=True)


def split_frontmatter(text: str) -> tuple[str | None, str]:
    """Return (frontmatter YAML or None, body)."""
    if not text.startswith("---"):
        return None, text
    lines = text.splitlines(keepends=True)
    if lines[0].strip() != "---":
        return None, text
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            return "".join(lines[1:i]), "".join(lines[i + 1 :])
    return None, text  # unterminated: treat as body


def read_note(path: Path, root: Path) -> Note:
    rel = path.relative_to(root).as_posix()
    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    if fm is None:
        return Note(path, rel, {}, body)
    try:
        props = _yaml().load(fm) or {}
    except YAMLError as e:
        return Note(
            path, rel, {}, body, parse_error=f"Properties can't be read: {e}".split("\n")[0]
        )
    if not isinstance(props, dict):
        return Note(path, rel, {}, body, parse_error="Properties must be 'name: value' lines.")
    return Note(path, rel, {str(k): v for k, v in props.items()}, body)


def _schema_from(data: dict[str, Any], name: str) -> Schema:
    fields = {}
    for fname, spec in (data.get("fields") or {}).items():
        spec = spec or {}
        fields[fname] = Field(
            name=fname,
            kind=spec.get("kind", "text"),
            of=spec.get("of", "text"),
            to=list(spec.get("to") or []),
            options=[str(o) for o in spec.get("options") or []],
            required=bool(spec.get("required", False)),
            min=spec.get("min"),
            max=spec.get("max"),
            default=spec.get("default"),
            help=str(spec.get("help", "")).strip(),
        )
    return Schema(
        type=data.get("type", name),
        id_prefix=data.get("id_prefix", ""),
        folder=data.get("folder", ""),
        description=str(data.get("description", "")).strip(),
        body=str(data.get("body", "")),
        fields=fields,
    )


def load_schemas(root: Path) -> tuple[dict[str, Schema], Schema]:
    schemas: dict[str, Schema] = {}
    common = Schema(type="_common")
    for path in sorted((root / SCHEMA_DIR).glob("*.yaml")):
        if path.stem == "_settings":
            continue
        data = _yaml().load(path.read_text(encoding="utf-8")) or {}
        if path.stem == "_common":
            common = _schema_from(data, "_common")
        else:
            schema = _schema_from(data, path.stem)
            schemas[schema.type] = schema
    return schemas, common


def is_record_path(rel_parts: tuple[str, ...]) -> bool:
    """Skip hidden/underscore folders (.obsidian, _schema, _templates…) and the root README."""
    if any(p.startswith((".", "_")) for p in rel_parts[:-1]):
        return False
    return rel_parts != ("README.md",)


def load_vault(root: Path | str) -> Vault:
    root = Path(root).resolve()
    schemas, common = load_schemas(root)
    notes = [
        read_note(p, root)
        for p in sorted(root.rglob("*.md"))
        if is_record_path(p.relative_to(root).parts)
    ]
    settings = dict(DEFAULT_SETTINGS)
    settings_path = root / SCHEMA_DIR / "_settings.yaml"
    if settings_path.exists():
        settings.update(_yaml().load(settings_path.read_text(encoding="utf-8")) or {})
    return Vault(root, notes, schemas, common, settings)
