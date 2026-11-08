from arsenal.privesc.diferenta import suid_noi


def test_doar_ce_e_nou():
    acum = {"a", "b", "c"}
    baza = {"a", "b"}
    assert suid_noi(acum, baza) == {"c"}
