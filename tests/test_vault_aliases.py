from pathlib import Path

from labbase.vault.aliases import lookup, normalize
from labbase.vault.reader import load_vault

DEMO = Path(__file__).parent.parent / "vault-demo"


def test_normalize() -> None:
    assert normalize("  Anfotericina-B ") == "anfotericina b"
    assert normalize("Schneider’s  médium") == "schneider s medium"


def test_lookup_by_name_alias_or_id() -> None:
    vault = load_vault(DEMO)
    assert [n.name for n in lookup(vault, "MILTEFOSINE")] == ["Miltefosine"]
    assert [n.name for n in lookup(vault, "anfotericina b")] == ["Amphotericin B"]
    assert [n.name for n in lookup(vault, "Glucantime")] == ["Meglumine antimoniate"]
    assert [n.name for n in lookup(vault, "THP1")] == ["THP-1"]
    thp1 = lookup(vault, "THP-1")[0]
    assert lookup(vault, thp1.id) == [thp1]
    assert lookup(vault, "unknown stuff") == []
