"""Generator local de probe cu metadate EXIF/GPS fictive."""

import base64
import hashlib
import io
import zipfile
from pathlib import Path
from urllib.parse import quote

from PIL import Image
from PIL.TiffImagePlugin import IFDRational

PROBE = Path(__file__).resolve().parent


def arhiva_locala():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as z:
        for nume, text in {
            "indiciu.txt": "FLAG{arhiva_ascunsa_la_coada}\n",
            "citeste.txt": "Arhiva de laborator adaugata dupa IEND intr-un PNG.\n",
        }.items():
            info = zipfile.ZipInfo(nume, date_time=(2026, 1, 1, 0, 0, 0))
            z.writestr(info, text.encode("utf-8"))
    return buffer.getvalue()


def pregateste():
    PROBE.mkdir(parents=True, exist_ok=True)
    mesaj = b"FLAG{straturi_base64_hex_url}"
    url = quote(mesaj.decode(), safe="")
    codificat = base64.b64encode(url.encode().hex().encode()).decode()
    (PROBE / "mesaj.txt").write_text(codificat + "\n", encoding="ascii")
    xor_clar = b"FLAG{xor_cu_cheie_de_un_octet} Mesaj secret pentru laborator."
    (PROBE / "xor.bin").write_bytes(bytes(b ^ 0x42 for b in xor_clar))
    parole = (("md5", "password"), ("sha1", "laborator6"), ("sha256", "steganografie"))
    hashuri = [hashlib.new(alg, parola.encode()).hexdigest() for alg, parola in parole]
    (PROBE / "hashuri.txt").write_text("\n".join(hashuri) + "\n", encoding="ascii")
    (PROBE / "wordlist.txt").write_text(
        "123456\nadmin\nparola\npassword\nstudent\nlaborator6\nsteganografie\nsecret\n",
        encoding="latin1")

    img = Image.new("RGB", (160, 120))
    img.putdata([((x * 3 + y) % 256, (x + y * 2) % 256, (x * 2 + y * 3) % 256)
                 for y in range(120) for x in range(160)])
    exif = Image.Exif()
    exif[271] = "Laborator UTM"
    exif[272] = "Camera virtuala Lab6"
    exif[306] = "2026:01:01 12:00:00"
    exif[270] = "Imagine sintetica de test; EXIF si GPS fictive."
    exif[34853] = {
        0: b"\x02\x03\x00\x00", 1: "N",
        2: (IFDRational(47), IFDRational(1), IFDRational(22)),
        3: "E", 4: (IFDRational(28), IFDRational(49), IFDRational(55)),
    }
    img.save(PROBE / "foto.jpg", quality=95, exif=exif)
    png = io.BytesIO()
    img.save(png, format="PNG")
    (PROBE / "ascuns.png").write_bytes(png.getvalue() + arhiva_locala())
    return ["mesaj.txt", "xor.bin", "hashuri.txt", "wordlist.txt", "foto.jpg", "ascuns.png"]


if __name__ == "__main__":
    for nume in pregateste():
        print(f"Creat: probe/{nume}")
