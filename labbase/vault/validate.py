"""Field-level checks of every note against its record-type schema."""

import difflib
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from labbase.vault.model import ID_RE, POSITION_RE, Field, Note, Vault, link_target

ERROR, WARNING = "error", "warning"


@dataclass(frozen=True)
class Issue:
    level: str
    rel: str
    field: str
    message: str

    def __str__(self) -> str:
        where = f"{self.rel}" + (f" › {self.field}" if self.field else "")
        return f"[{self.level}] {where}: {self.message}"


def as_date(value: Any) -> date | None:
    """date objects, or ISO strings like "2026-01-15" (quoted dates from templates)."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value.strip())
        except ValueError:
            return None
    return None


def is_empty(value: Any) -> bool:
    return value is None or value == "" or value == []


def _scalar_problem(f: Field, kind: str, value: Any) -> str | None:
    """Return a human message if `value` doesn't fit `kind`, else None."""
    if kind == "text":
        return (
            None
            if isinstance(value, str | int | float) and not isinstance(value, bool)
            else "should be text"
        )
    if kind == "integer":
        return (
            None
            if isinstance(value, int) and not isinstance(value, bool)
            else "should be a whole number"
        )
    if kind == "number":
        return (
            None
            if isinstance(value, int | float) and not isinstance(value, bool)
            else "should be a number (no units — the unit is in the property name)"
        )
    if kind == "date":
        if isinstance(value, date | datetime) or as_date(value) is not None:
            return None
        return "should be a date like 2026-01-15"
    if kind == "boolean":
        return None if isinstance(value, bool) else "should be true or false"
    if kind == "choice":
        return None if str(value) in f.options else f"should be one of: {', '.join(f.options)}"
    if kind == "link":
        return None if link_target(value) else "should be a link like [[Name]]"
    if kind == "position":
        return (
            None
            if isinstance(value, str) and POSITION_RE.match(value)
            else "should be a box position like A1"
        )
    return None


def _check_value(note: Note, f: Field, value: Any, prefix: str) -> list[Issue]:
    issues: list[Issue] = []

    def err(msg: str) -> None:
        issues.append(Issue(ERROR, note.rel, f.name, msg))

    if f.kind == "id":
        if not isinstance(value, str) or not ID_RE.match(value.strip()):
            err(f"'{value}' is not an ID like {prefix or 'ABC'}-0001")
        elif prefix and not value.strip().startswith(prefix + "-"):
            err(f"IDs of this type start with {prefix}-")
        return issues
    if f.kind == "list":
        if not isinstance(value, list):
            err("should be a list (one item per line in Properties)")
            return issues
        for item in value:
            problem = None if is_empty(item) else _scalar_problem(f, f.of, item)
            if problem:
                err(f"item '{item}' {problem}")
        return issues
    problem = _scalar_problem(f, f.kind, value)
    if problem:
        err(f"'{value}' {problem}")
        return issues
    if f.kind in ("integer", "number"):
        if f.min is not None and value < f.min:
            err(f"{value} is below the minimum {f.min:g}")
        if f.max is not None and value > f.max:
            err(f"{value} is above the maximum {f.max:g}")
    return issues


def check_note(vault: Vault, note: Note) -> list[Issue]:
    if note.parse_error:
        return [Issue(ERROR, note.rel, "", note.parse_error)]
    if not note.props:
        return [
            Issue(
                WARNING,
                note.rel,
                "",
                "has no properties, so it isn't a record (fine for free notes)",
            )
        ]
    if not note.type:
        return [
            Issue(
                ERROR, note.rel, "type", "missing — add `type:` (e.g. stock, compound, cell_line)"
            )
        ]
    schema = vault.schemas.get(note.type)
    if schema is None:
        known = ", ".join(sorted(vault.schemas))
        return [Issue(ERROR, note.rel, "type", f"unknown type '{note.type}'. Known: {known}")]

    fields = {**vault.common.fields, **schema.fields}
    issues: list[Issue] = []
    for name, f in fields.items():
        value = note.props.get(name)
        if is_empty(value):
            if f.required:
                issues.append(Issue(ERROR, note.rel, name, "is required"))
            continue
        issues += _check_value(note, f, value, schema.id_prefix)
    for name in note.props:
        if name not in fields:
            close = difflib.get_close_matches(name, fields, n=1, cutoff=0.75)
            hint = f" — did you mean '{close[0]}'?" if close else " (kept, but not in the schema)"
            issues.append(Issue(WARNING, note.rel, name, f"unknown property{hint}"))
    top = note.rel.split("/")[0]
    if schema.folder and top != schema.folder:
        issues.append(
            Issue(WARNING, note.rel, "", f"{note.type} notes usually live in {schema.folder}/")
        )
    return issues


def check_uniqueness(vault: Vault) -> list[Issue]:
    issues: list[Issue] = []
    seen_ids: dict[str, Note] = {}
    for n in vault.notes:
        if n.id:
            if n.id in seen_ids:
                issues.append(
                    Issue(ERROR, n.rel, "id", f"{n.id} is also used by {seen_ids[n.id].rel}")
                )
            else:
                seen_ids[n.id] = n
    for notes in vault.by_name().values():
        if len(notes) > 1:
            others = ", ".join(x.rel for x in notes)
            msg = f"same name as {others}; links to [[{notes[0].name}]] are ambiguous"
            issues.append(Issue(ERROR, notes[0].rel, "", msg))
    return issues


def check_fields(vault: Vault) -> list[Issue]:
    issues: list[Issue] = []
    for note in vault.notes:
        issues += check_note(vault, note)
    return issues + check_uniqueness(vault)
