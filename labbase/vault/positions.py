"""Box grid positions: 'b07' / 'B 7' -> 'B7'; 0-based (row, col) <-> 'A1'."""

import string

from labbase.vault.model import POSITION_RE


def parse(position: str) -> tuple[int, int] | None:
    m = POSITION_RE.match(str(position).strip())
    if m is None:
        return None
    return string.ascii_uppercase.index(m.group(1).upper()), int(m.group(2)) - 1


def label(row: int, col: int) -> str:
    return f"{string.ascii_uppercase[row]}{col + 1}"


def normalize(position: str) -> str | None:
    rc = parse(position)
    return label(*rc) if rc else None


def in_grid(position: str, rows: int, cols: int) -> bool:
    rc = parse(position)
    return rc is not None and 0 <= rc[0] < rows and 0 <= rc[1] < cols
