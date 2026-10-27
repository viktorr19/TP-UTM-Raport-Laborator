"""Analiza semnaturilor, textului, metadatelor si arhivelor ascunse."""

import argparse
import io
import json
import re
import zipfile
from pathlib import Path

from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS

RADACINA = Path(__file__).resolve().parent


def tip_real(cale):
    with Path(cale).open("rb") as f:
        cap = f.read(8)
    for semnatura, tip in ((b"%PDF", "pdf"), (b"\x89PNG\r\n\x1a\n", "png"),
                           (b"\xff\xd8\xff", "jpeg"), (b"PK\x03\x04", "zip/docx")):
        if cap.startswith(semnatura):
            return tip
    return "necunoscut:" + cap.hex()


def extrage_strings(cale, minim=4):
    if minim < 1:
        raise ValueError("Lungimea minima trebuie sa fie pozitiva.")
    expresie = rb"[ -~]{" + str(minim).encode() + rb",}"
    return [{"offset": m.start(), "text": m.group().decode("ascii")}
            for m in re.finditer(expresie, Path(cale).read_bytes())]


def grade_zecimale(dms, emisfera):
    if len(dms) != 3:
        raise ValueError("Coordonata GPS trebuie sa contina grade, minute, secunde.")
    if isinstance(emisfera, bytes):
        emisfera = emisfera.decode("ascii")
    emisfera = emisfera.rstrip("\x00").upper()
    if emisfera not in ("N", "S", "E", "W"):
        raise ValueError("Emisfera GPS necunoscuta.")
    g, m, s = map(float, dms)
    if not (0 <= m < 60 and 0 <= s < 60):
        raise ValueError("Minute/secunde GPS invalide.")
    valoare = g + m / 60 + s / 3600
    return -valoare if emisfera in ("S", "W") else valoare


def valoare_json(val):
    if isinstance(val, bytes):
        return val.hex()
    if isinstance(val, dict):
        return {str(k): valoare_json(v) for k, v in val.items()}
    if isinstance(val, (tuple, list)):
        return [valoare_json(v) for v in val]
    if isinstance(val, (str, int, float)) or val is None:
        return val
    try:
        return float(val)
    except (TypeError, ValueError):
        return str(val)


def metadate(cale):
    with Image.open(cale) as img:
        exif = img.getexif()
        valori = {TAGS.get(k, str(k)): valoare_json(v)
                  for k, v in exif.items() if k != 34853}
        gps = exif.get_ifd(34853) if 34853 in exif else {}
        rezultat = {"dimensiuni": list(img.size), "exif": valori,
                    "gps_brut": {GPSTAGS.get(k, str(k)): valoare_json(v) for k, v in gps.items()},
                    "gps_zecimal": None}
        if all(k in gps for k in (1, 2, 3, 4)):
            rezultat["gps_zecimal"] = {
                "latitudine": grade_zecimale(gps[2], gps[1]),
                "longitudine": grade_zecimale(gps[4], gps[3]),
            }
        return rezultat


def extrage_zip(cale, destinatie):
    date = Path(cale).read_bytes()
    start = 0
    while True:
        i = date.find(b"PK\x03\x04", start)
        if i == -1:
            raise ValueError("Nu s-a gasit o arhiva ZIP valida.")
        candidat = date[i:]
        if zipfile.is_zipfile(io.BytesIO(candidat)):
            break
        start = i + 1
    with zipfile.ZipFile(io.BytesIO(candidat)) as z:
        if sum(info.file_size for info in z.infolist()) > 10 * 1024 * 1024:
            raise ValueError("Arhiva depaseste limita de 10 MiB a acestui laborator.")
        corupt = z.testzip()
        if corupt:
            raise ValueError(f"CRC invalid pentru {corupt}.")
        Path(destinatie).write_bytes(candidat)
        continut = {info.filename: z.read(info).decode("utf-8", errors="replace")
                    for info in z.infolist() if not info.is_dir()}
    return {"offset": i, "dimensiune": len(candidat),
            "continut": continut}


def analizeaza_probe(probe, arhiva):
    probe, arhiva = Path(probe), Path(arhiva)
    tipuri = {nume: tip_real(probe / nume)
              for nume in ("foto.jpg", "ascuns.png")}
    siruri = extrage_strings(probe / "ascuns.png")
    foto = metadate(probe / "foto.jpg")
    extras = extrage_zip(probe / "ascuns.png", arhiva)
    tipuri[arhiva.name] = tip_real(arhiva)
    return {"tipuri": tipuri, "strings": siruri, "foto": foto, "arhiva": extras}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--probe", type=Path, default=RADACINA / "probe")
    p.add_argument("--arhiva", type=Path, default=RADACINA / "gasit.zip")
    a = p.parse_args(argv)
    try:
        rezultat = analizeaza_probe(a.probe, a.arhiva)
        print(json.dumps(rezultat, indent=2, ensure_ascii=False))
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        p.exit(2, f"Eroare: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
