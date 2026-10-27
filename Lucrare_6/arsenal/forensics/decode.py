"""Decodare Base64, hex, URL, XOR si cautarea parolelor prin dictionar."""

import argparse
import base64
import binascii
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote_to_bytes

RADACINA = Path(__file__).resolve().parents[2]


def incalzire():
    b = "Salut".encode()
    return {"octeti": repr(b), "primul_octet": b[0], "hex": b.hex(),
            "refacut": repr(bytes.fromhex(b.hex()))}


def ghici_strat(s):
    s = s.strip()
    if re.search(r"%[0-9a-fA-F]{2}", s):
        return "url"
    if s and len(s) % 2 == 0 and re.fullmatch(r"[0-9a-fA-F]+", s):
        return "hex"
    if s and len(s) % 4 == 0 and re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", s):
        return "base64"
    return "necunoscut"


def desfa(s):
    strat = ghici_strat(s)
    curat = s.strip()
    try:
        if strat == "base64":
            b = base64.b64decode(curat, validate=True)
            if base64.b64encode(b).decode("ascii") != curat:
                raise ValueError("Base64 necanonic: verifica padding-ul si bitii finali.")
            return strat, b
        if strat == "hex":
            return strat, bytes.fromhex(curat)
        if strat == "url":
            return strat, unquote_to_bytes(curat)
    except (binascii.Error, UnicodeError) as exc:
        raise ValueError(f"Codare {strat} invalida: {exc}") from exc
    return strat, s.encode("utf-8")


def citibil(b):
    return all(32 <= c < 127 for c in b)


def reprezinta(b):
    try:
        return b.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return b.hex(), "hex"


def decodeaza_straturi(s, max_straturi=8):
    """Pastreaza ultimul text citibil daca urmatorul strat produce date binare."""
    if max_straturi < 1:
        raise ValueError("Limita de straturi trebuie sa fie pozitiva.")
    date = s.encode("utf-8")
    pasi, vazute = [], set()
    for _ in range(max_straturi):
        try:
            val = date.decode("utf-8")
        except UnicodeDecodeError:
            break
        if val in vazute or ghici_strat(val) == "necunoscut":
            break
        vazute.add(val)
        try:
            strat, candidat = desfa(val)
        except ValueError:
            break
        if candidat == date:
            break
        if pasi and citibil(date) and not citibil(candidat):
            break
        text, format_rezultat = reprezinta(candidat)
        pasi.append({"strat": strat, "rezultat": text, "format": format_rezultat})
        date = candidat
    return date, pasi


def xor_octet(date, cheie):
    if not 0 <= cheie <= 255:
        raise ValueError("Cheia XOR trebuie sa fie intre 0 si 255.")
    return bytes(b ^ cheie for b in date)


def scor_text(text):
    litere = sum(c.isalpha() or c == " " for c in text)
    frecvente = sum(c.lower() in "aeiourstnl" for c in text)
    indicii = sum(cuv in text.lower() for cuv in ("flag{", "secret", "mesaj", "laborator"))
    return round((litere + frecvente * 0.3) / max(len(text), 1) + indicii * 5, 4)


def sparge_xor(date):
    if not date:
        return []
    candidati = []
    for k in range(256):
        clar = xor_octet(date, k)
        if citibil(clar):
            text = clar.decode("ascii")
            candidati.append({"cheie": k, "cheie_hex": f"0x{k:02x}",
                              "rezultat": text, "scor": scor_text(text)})
    return sorted(candidati, key=lambda c: (-c["scor"], c["cheie"]))


def identifica_hash(tinta):
    """Lungimea sugereaza algoritmul, fara sa-l dovedeasca in general."""
    tinta = tinta.strip()
    if not re.fullmatch(r"[0-9a-fA-F]+", tinta):
        return None
    return {32: "md5", 40: "sha1", 64: "sha256"}.get(len(tinta))


def sparge_hash(tinta, wordlist):
    tinta = tinta.strip().lower()
    algoritm = identifica_hash(tinta)
    if algoritm is None:
        raise ValueError("Hash necunoscut; se accepta MD5, SHA-1 sau SHA-256 in hex.")
    incercari = 0
    with Path(wordlist).open(encoding="latin1") as fisier:
        for linie in fisier:
            cuvant = linie.rstrip("\r\n")
            incercari += 1
            if hashlib.new(algoritm, cuvant.encode("utf-8")).hexdigest() == tinta:
                return {"hash": tinta, "algoritm": algoritm, "parola": cuvant,
                        "gasit": True, "incercari": incercari}
    return {"hash": tinta, "algoritm": algoritm, "parola": None,
            "gasit": False, "incercari": incercari}


def analizeaza(date, mod="auto", wordlist=None, max_straturi=8):
    wordlist = wordlist or RADACINA / "probe" / "wordlist.txt"
    try:
        text = date.decode("utf-8").strip()
    except UnicodeDecodeError:
        text = None
    if mod == "hash" or (mod == "auto" and text and identifica_hash(text)):
        rezultat = sparge_hash(text or "", wordlist)
        return {"strat": "hash", "rezultat": rezultat["parola"], **rezultat}
    if mod == "xor" or (mod == "auto" and (text is None or not citibil(date.strip()))):
        candidati = sparge_xor(date)
        primul = candidati[0] if candidati else {}
        return {"strat": "xor", "rezultat": primul.get("rezultat"),
                "cheie": primul.get("cheie"), "candidati": candidati,
                "nota": "Primul candidat este o euristica; verifica mesajul sau un hash."}
    if text is None:
        raise ValueError("Pentru modul straturi, fisierul trebuie sa contina text UTF-8.")
    clar, pasi = decodeaza_straturi(text, max_straturi)
    rezultat, format_rezultat = reprezinta(clar)
    return {"strat": " -> ".join(p["strat"] for p in pasi) or "necunoscut",
            "rezultat": rezultat, "format": format_rezultat, "pasi": pasi}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("intrare", help="Sir de decodat sau cale daca folosesti --fisier")
    p.add_argument("--fisier", action="store_true")
    p.add_argument("--mod", choices=("auto", "straturi", "xor", "hash"), default="auto")
    p.add_argument("--wordlist", type=Path, default=RADACINA / "probe/wordlist.txt")
    p.add_argument("--max-straturi", type=int, default=8)
    p.add_argument("--fisa", type=Path, default=Path(__file__).with_name("fisa.json"))
    a = p.parse_args(argv)
    try:
        date = Path(a.intrare).read_bytes() if a.fisier else a.intrare.encode("utf-8")
        fisa = analizeaza(date, a.mod, a.wordlist, a.max_straturi)
        a.fisa.parent.mkdir(parents=True, exist_ok=True)
        continut = json.dumps(fisa, indent=2, ensure_ascii=False)
        a.fisa.write_text(continut + "\n", encoding="utf-8")
        print(continut)
    except (OSError, ValueError) as exc:
        p.exit(2, f"Eroare: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
