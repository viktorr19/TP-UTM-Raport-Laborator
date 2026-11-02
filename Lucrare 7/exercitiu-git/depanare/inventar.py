import argparse
import json


def incarca(cale):
    with open(cale) as f:
        return json.load(f)


def port_valid(text):
    try:
        return int(text)
    except ValueError:
        return None


def pe_servicii(tinte):
    grupe = {}
    for t in tinte:
        serviciu = t.get("serviciu", "necunoscut")
        port = port_valid(t["port"])
        if port is None:
            print("sar peste", t["gazda"], ": port invalid", t["port"])
            continue
        grupe.setdefault(serviciu, [])
        grupe[serviciu].append(port)
    return grupe


def peste_prag(tinte, prag):
    rezultat = []
    for t in tinte:
        port = port_valid(t["port"])
        if port is not None and port > prag:
            rezultat.append(t["gazda"])
    return rezultat


def main():
    p = argparse.ArgumentParser()
    p.add_argument("fisier")
    p.add_argument("--prag", type=int, default=1024)
    a = p.parse_args()

    tinte = incarca(a.fisier)
    print("Tinte citite: " + str(len(tinte)))

    grupe = pe_servicii(tinte)
    for serviciu, porturi in grupe.items():
        print(f"{serviciu}: {porturi}")

    mari = peste_prag(tinte, a.prag)
    print(f"Peste {a.prag}: {mari}")

    with open("raport_inventar.json", "w") as f:
        json.dump({"servicii": grupe, "peste_prag": mari}, f, indent=2)
    print("Raport salvat in raport_inventar.json")


if __name__ == "__main__":
    main()
