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


def check_stocks(vault: Vault) -> list[Issue]:
    issues: list[Issue] = []
    occupied: dict[tuple[str, str], Note] = {}  # (box rel, position) -> stock
    for stock in (n for n in vault.notes if n.type == "stock"):
        p = stock.props
        finished = p.get("state") == "finished"
        box = vault.resolve(p.get("box"))
        has_location = not is_empty(p.get("location"))
        pos_list = p.get("positions") if isinstance(p.get("positions"), list) else []
        pos_list = [x for x in pos_list if not is_empty(x)]

        if box is None and not has_location and not finished:
            issues.append(Issue(WARNING, stock.rel, "box", "no box or location — where is it?"))
        if box is not None and has_location:
            issues.append(
                Issue(WARNING, stock.rel, "location", "has both box and location; use one")
            )
        if pos_list and is_empty(p.get("box")):
            issues.append(Issue(ERROR, stock.rel, "positions", "positions need a box"))

        if box is not None and box.type == "box":
            rows, cols = box_grid(box)
            seen: set[str] = set()
            for raw in pos_list:
                pos = positions.normalize(str(raw))
                if pos is None:
                    continue  # format error reported by field validation
                if not positions.in_grid(pos, rows, cols):
                    issues.append(
                        Issue(
                            ERROR,
                            stock.rel,
                            "positions",
                            f"{pos} is outside [[{box.name}]] ({rows}×{cols})",
                        )
                    )
                    continue
                if pos in seen:
                    issues.append(Issue(ERROR, stock.rel, "positions", f"{pos} is listed twice"))
                    continue
                seen.add(pos)
                if finished:
                    continue
                other = occupied.get((box.rel, pos))
                if other is not None:
                    issues.append(
                        Issue(
                            ERROR,
                            stock.rel,
                            "positions",
                            f"[[{box.name}]] {pos} is also used by [[{other.name}]]",
                        )
                    )
                else:
                    occupied[(box.rel, pos)] = stock
            left = p.get("vials_left")
            if isinstance(left, int) and pos_list and left != len(seen):
                issues.append(
                    Issue(
                        ERROR,
                        stock.rel,
                        "vials_left",
                        f"says {left} but {len(seen)} positions are listed",
                    )
                )
        if finished and pos_list:
            issues.append(
                Issue(
                    WARNING,
                    stock.rel,
                    "positions",
                    "finished but still lists positions; clear them to free the box",
                )
            )
    return issues


def occupancy(vault: Vault) -> dict[str, dict[str, Note]]:
    """box rel -> {position -> stock} for stocks that are not finished."""
    result: dict[str, dict[str, Note]] = {}
    for stock in (n for n in vault.notes if n.type == "stock"):
        if stock.props.get("state") == "finished":
            continue
        box = vault.resolve(stock.props.get("box"))
        if box is None or box.type != "box":
            continue
        raw = stock.props.get("positions") if isinstance(stock.props.get("positions"), list) else []
        for x in raw:
            pos = positions.normalize(str(x)) if not is_empty(x) else None
            if pos:
                result.setdefault(box.rel, {}).setdefault(pos, stock)
    return result
