import argparse
import json

from arsenal.aparare.parse_auth import citeste_esecuri, pe_ip


def suspecti(counts, prag=10):
    if prag < 1:
        raise ValueError(f"prag invalid: {prag} (cel putin 1)")

    rezultate = [(ip, n) for ip, n in counts.items() if n >= prag]
    return sorted(rezultate, key=lambda rezultat: rezultat[1], reverse=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("log")
    parser.add_argument("--prag", type=int, default=10)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    esecuri = citeste_esecuri(args.log)
    counts = pe_ip(esecuri)
    try:
        sus = suspecti(counts, args.prag)
    except ValueError as eroare:
        parser.error(str(eroare))

    if args.json:
        print(json.dumps({"esecuri": len(esecuri), "pe_ip": counts, "suspecti": sus}))
        return

    print(f"Esecuri de autentificare: {len(esecuri)}")
    for ip, n in counts.most_common():
        print(f"  {ip}: {n}")
    print(f"Suspecti (prag {args.prag}):")
    for ip, n in sus:
        print(f"  {ip}  ({n} incercari)  BRUTE FORCE")


if __name__ == "__main__":
    main()
