from pathlib import Path

from arsenal.privesc.enum import GTFO, citeste_linii, nume


def cai(fisier):
    return set(citeste_linii(fisier))


def suid_noi(acum, baza):
    return acum - baza


def main():
    capturi = Path(__file__).with_name("start")
    baza = cai(capturi / "baza_suid.txt")
    acum = cai(capturi / "suid.txt")
    print("baza:", len(baza), " acum:", len(acum))

    noi = suid_noi(acum, baza)
    print(len(noi), "SUID noi fata de sistemul curat")
    for cale in sorted(noi):
        print(" ", cale)

    risc = {nume(c): "mare" if nume(c) in GTFO else "normal" for c in noi}
    periculoase = [c for c in sorted(noi) if risc[nume(c)] == "mare"]
    print("periculoase NOI:", periculoase)


if __name__ == "__main__":
    main()
