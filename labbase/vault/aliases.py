"""Name matching for messy inputs (Excel imports): ignore accents, case and punctuation."""

import re
import unicodedata

from labbase.vault.model import Note, Vault


def normalize(text: str) -> str:
    """'  Anfotericina-B ' -> 'anfotericina b'."""
    text = unicodedata.normalize("NFKD", str(text))
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def name_index(vault: Vault) -> dict[str, list[Note]]:
    """Normalized note name / alias / id -> notes. More than one note = ambiguous."""
    index: dict[str, list[Note]] = {}
    for note in vault.notes:
        names = [note.name, note.id]
        aliases = note.props.get("aliases")
        if isinstance(aliases, list):
            names += [str(a) for a in aliases]
        for key in {normalize(n) for n in names if n}:
            index.setdefault(key, []).append(note)
    return index


def lookup(vault: Vault, text: str, index: dict[str, list[Note]] | None = None) -> list[Note]:
    return (index if index is not None else name_index(vault)).get(normalize(text), [])
