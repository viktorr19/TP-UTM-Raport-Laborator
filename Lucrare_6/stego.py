"""Mesaj UTF-8 in LSB-urile canalelor R, G, B, terminat cu octet 0."""

import argparse
from pathlib import Path

from PIL import Image


def ascunde(gazda, mesaj, destinatie):
    if Path(destinatie).suffix.lower() != ".png":
        raise ValueError("Salveaza rezultatul in PNG pentru a pastra bitii.")
    date = mesaj.encode("utf-8") if isinstance(mesaj, str) else bytes(mesaj)
    if b"\x00" in date:
        raise ValueError("Mesajul nu poate contine octetul terminator 0.")
    payload = date + b"\x00"
    with Image.open(gazda) as sursa:
        img = sursa.convert("RGB")
    canale = bytearray(img.tobytes())
    necesar = len(payload) * 8
    if necesar > len(canale):
        raise ValueError(f"Mesaj prea mare: necesita {necesar} biti, capacitate {len(canale)}.")
    for i in range(necesar):
        bit = (payload[i // 8] >> (7 - i % 8)) & 1
        canale[i] = (canale[i] & ~1) | bit
    stego = Image.frombytes("RGB", img.size, bytes(canale))
    Path(destinatie).parent.mkdir(parents=True, exist_ok=True)
    stego.save(destinatie, format="PNG")
    return {"octeti_mesaj": len(date), "biti_scrisi": necesar,
            "capacitate_octeti": len(canale) // 8 - 1}


def dezvaluie(cale):
    with Image.open(cale) as img:
        canale = img.convert("RGB").tobytes()
    rezultat = bytearray()
    octet, numar_biti = 0, 0
    for canal in canale:
        octet = (octet << 1) | (canal & 1)
        numar_biti += 1
        if numar_biti == 8:
            if octet == 0:
                return bytes(rezultat)
            rezultat.append(octet)
            octet, numar_biti = 0, 0
    raise ValueError("Nu exista terminator zero: imaginea nu respecta protocolul LSB.")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="comanda", required=True)
    asc = sub.add_parser("ascunde", help="Scrie mesajul si terminatorul in RGB-LSB")
    asc.add_argument("gazda", type=Path)
    asc.add_argument("mesaj")
    asc.add_argument("destinatie", type=Path)
    dez = sub.add_parser("dezvaluie", help="Citeste pana la primul octet zero")
    dez.add_argument("imagine", type=Path)
    a = p.parse_args(argv)
    try:
        if a.comanda == "ascunde":
            print(ascunde(a.gazda, a.mesaj, a.destinatie))
        else:
            print(dezvaluie(a.imagine).decode("utf-8"))
    except (OSError, ValueError, UnicodeError) as exc:
        p.exit(2, f"Eroare: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
