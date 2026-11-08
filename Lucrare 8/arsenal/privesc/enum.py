import argparse
import json
from pathlib import Path


GTFO = {
    "find", "vim.basic", "vim", "nmap", "cp", "bash",
    "less", "awk", "python3", "perl",
}


def citeste_linii(cale):
    with open(cale, encoding="utf-8") as fisier:
        linii = [linie.strip() for linie in fisier]
    return [linie for linie in linii if linie and not linie.startswith("#")]


def nume(cale):
    return cale.rsplit("/", 1)[-1]


def suid_constatari(cale):
    constatari = []
    for cale_unica in sorted(set(citeste_linii(cale))):
        binar = nume(cale_unica)
        constatari.append({
            "cale": cale_unica,
            "nume": binar,
            "risc": "mare" if binar in GTFO else "normal",
        })
    return constatari


def sudo_constatari(cale):
    constatari = []
    for linie in citeste_linii(cale):
        user, drept = linie.split(" : ", 1)
        constatari.append({
            "user": user.strip(),
            "drept": drept.strip(),
            "risc": "mare" if "NOPASSWD" in drept else "normal",
        })
    return constatari


def cron_constatari(cale):
    constatari = []
    for linie in citeste_linii(cale):
        campuri = linie.split()
        constatari.append({
            "user": campuri[5],
            "comanda": " ".join(campuri[6:]),
        })
    return constatari


def enumereaza(capturi):
    capturi = Path(capturi)
    return {
        "suid": suid_constatari(capturi / "suid.txt"),
        "sudo": sudo_constatari(capturi / "sudo.txt"),
        "cron": cron_constatari(capturi / "crontab.txt"),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("capturi")
    parser.add_argument("--json", action="store_true")
    argumente = parser.parse_args()

    raport = enumereaza(argumente.capturi)
    if argumente.json:
        print(json.dumps(raport, indent=2, ensure_ascii=False))
        return

    for categorie, constatari in raport.items():
        mari = [c for c in constatari if c.get("risc") == "mare"]
        print(f"{categorie}: {len(constatari)} gasite, {len(mari)} cu risc mare")

    utilizatori = {c["user"] for c in raport["sudo"]} | {c["user"] for c in raport["cron"]}
    print("utilizatori implicati:", ", ".join(sorted(utilizatori)))

    cale_raport = Path(__file__).with_name("enum.json")
    with cale_raport.open("w", encoding="utf-8") as fisier:
        json.dump(raport, fisier, indent=2, ensure_ascii=False)
        fisier.write("\n")
    print("Raport salvat in enum.json")


if __name__ == "__main__":
    main()
