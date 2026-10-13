"""Checks across notes: links point to the right kind of note; box positions are consistent."""

from labbase.vault import positions
from labbase.vault.model import Note, Vault, link_target
from labbase.vault.validate import ERROR, WARNING, Issue, is_empty


def _link_values(note: Note, vault: Vault) -> list[tuple[str, str, list[str]]]:
    """(field, raw value, allowed types) for every link-valued property of the note."""
    schema = vault.schemas.get(note.type)
    if schema is None:
        return []
    out = []
    for name, f in {**vault.common.fields, **schema.fields}.items():
        value = note.props.get(name)
        if is_empty(value):
            continue
        if f.kind == "link":
            out.append((name, value, f.to))
        elif f.kind == "list" and f.of == "link" and isinstance(value, list):
            out += [(name, v, f.to) for v in value if not is_empty(v)]
    return out


def check_links(vault: Vault) -> list[Issue]:
    issues: list[Issue] = []
    index = vault.by_name()
    for note in vault.notes:
        for name, value, allowed in _link_values(note, vault):
            target_name = link_target(value)
            if target_name is None:
                continue  # already reported by field validation
            matches = index.get(target_name.lower(), [])
            target = vault.resolve(value)
            if target is None:
                why = "is ambiguous" if len(matches) > 1 else "points to a note that doesn't exist"
                issues.append(Issue(ERROR, note.rel, name, f"[[{target_name}]] {why}"))
            elif allowed and target.type not in allowed:
                issues.append(
                    Issue(
                        ERROR,
                        note.rel,
                        name,
                        f"[[{target_name}]] is a {target.type or 'note without type'}; "
                        f"expected {' or '.join(allowed)}",
                    )
                )
    return issues


def box_grid(box: Note) -> tuple[int, int]:
    rows, cols = box.props.get("rows"), box.props.get("cols")
    return (rows if isinstance(rows, int) else 9, cols if isinstance(cols, int) else 9)


INACTIVE_STATUS = {"finished", "not found"}


def placements(vault: Vault):  # noqa: ANN201
    """Everything that occupies box positions: (note, box or None, raw positions, field, active).

    Stock notes list several `positions` in their `box`; single items (e.g. primers) have a
    `location` that is a box plus one `position`.
    """
    for n in vault.notes:
        p = n.props
        if n.type == "stock":
            raw = p.get("positions") if isinstance(p.get("positions"), list) else []
            raw = [x for x in raw if not is_empty(x)]
            yield n, vault.resolve(p.get("box")), raw, "positions", p.get("state") != "finished"
        elif not is_empty(p.get("position")):
            active = str(p.get("status") or "") not in INACTIVE_STATUS
            yield n, vault.resolve(p.get("location")), [p.get("position")], "position", active


def check_stocks(vault: Vault) -> list[Issue]:
    """Stock-specific consistency: where it is, counts, finished stocks still in a box."""
    issues: list[Issue] = []
    for stock in (n for n in vault.notes if n.type == "stock"):
        p = stock.props
        finished = p.get("state") == "finished"
        box = vault.resolve(p.get("box"))
        has_location = not is_empty(p.get("location"))
        raw = p.get("positions") if isinstance(p.get("positions"), list) else []
        pos_list = [x for x in raw if not is_empty(x)]
        if box is None and not has_location and not finished:
            issues.append(Issue(WARNING, stock.rel, "box", "no box or location — where is it?"))
        if box is not None and has_location:
            issues.append(
                Issue(WARNING, stock.rel, "location", "has both box and location; use one")
            )
        if box is not None and box.type == "box":
            rows, cols = box_grid(box)
            normalized = {positions.normalize(str(x)) for x in pos_list} - {None}
            valid = {x for x in normalized if positions.in_grid(x, rows, cols)}
            left = p.get("vials_left")
            if isinstance(left, int) and pos_list and left != len(valid):
                msg = f"says {left} but {len(valid)} positions are listed"
                issues.append(Issue(ERROR, stock.rel, "vials_left", msg))
        if finished and pos_list:
            msg = "finished but still lists positions; clear them to free the box"
            issues.append(Issue(WARNING, stock.rel, "positions", msg))
    return issues


def check_positions(vault: Vault) -> list[Issue]:
    """Positions must be inside the box grid and not used twice (stocks and single items)."""
    issues: list[Issue] = []
    occupied: dict[tuple[str, str], Note] = {}
    for note, box, raw, field_name, active in placements(vault):
        if not raw:
            continue
        if box is None or box.type != "box":
            where = "box" if field_name == "positions" else "location"
            msg = f"positions need a box in `{where}`"
            issues.append(Issue(ERROR, note.rel, field_name, msg))
            continue
        rows, cols = box_grid(box)
        seen: set[str] = set()
        for x in raw:
            pos = positions.normalize(str(x))
            if pos is None:
                continue  # format error reported by field validation
            if not positions.in_grid(pos, rows, cols):
                msg = f"{pos} is outside [[{box.name}]] ({rows}×{cols})"
                issues.append(Issue(ERROR, note.rel, field_name, msg))
                continue
            if pos in seen:
                issues.append(Issue(ERROR, note.rel, field_name, f"{pos} is listed twice"))
                continue
            seen.add(pos)
            if not active:
                continue
            other = occupied.get((box.rel, pos))
            if other is not None:
                msg = f"[[{box.name}]] {pos} is also used by [[{other.name}]]"
                issues.append(Issue(ERROR, note.rel, field_name, msg))
            else:
                occupied[(box.rel, pos)] = note
    return issues


def occupancy(vault: Vault) -> dict[str, dict[str, Note]]:
    """box rel -> {position -> note} for everything active that sits in a box position."""
    result: dict[str, dict[str, Note]] = {}
    for note, box, raw, _field, active in placements(vault):
        if not active or box is None or box.type != "box":
            continue
        for x in raw:
            pos = positions.normalize(str(x))
            if pos:
                result.setdefault(box.rel, {}).setdefault(pos, note)
    return result
