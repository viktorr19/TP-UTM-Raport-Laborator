import pytest

from arsenal.aparare.detector import suspecti
from arsenal.aparare.parse_auth import pe_ip


def test_pragul_taie():
    esecuri = [{"ip": "a"}, {"ip": "b"}, {"ip": "a"}]
    counts = pe_ip(esecuri)
    assert counts == {"a": 2, "b": 1}
    assert suspecti(counts, 2) == [("a", 2)]


def test_prag_invalid():
    with pytest.raises(ValueError):
        suspecti({}, 0)
