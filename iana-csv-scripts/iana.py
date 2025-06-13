import csv

map = {}


def massage_code(code):
    if "-" in code or "*" in code or not code.startswith("0x"):
        return None
    hi, lo = code.split(",")
    return int(hi, 0) << 8 | int(lo, 0)


def notable(name):
    # nation state crypto
    if "_CAMELLIA_" in name or "_ARIA_" in name or "GOSTR" in name or "_SM4" in name:
        return False

    # ancient
    if (
        "_SEED_" in name
        or "_KRB" in name
        or "DH_anon" in name
        or "_RC4" in name
        or "_DH_" in name
        or "_DSS_" in name
        or "_DES_" in name
        or "_IDEA_" in name
        or "_3DES_" in name
        or "_ECDH_" in name
    ):
        return False

    # mental shit
    if "ECCPWD" in name or "_EXPORT_" in name or "_SRP_" in name or "_NULL_" in name:
        return False

    # drafts with unclear adoption
    if "_AEGIS_" in name:
        return False

    return True


def massage_ref(ref):
    ref = ref.replace("[", "")
    for ref in ref.split("]"):
        if not ref or " " in ref:
            continue
        yield "https://www.iana.org/go/" + ref.lower()


def print_meta(meta):
    code, item, rec, ref = meta
    print("/// The `{}` cipher suite.  Recommended={}.  Defined in".format(item, rec))

    for link in massage_ref(ref):
        print("/// <{}>".format(link))


for row in csv.reader(open("tls-parameters-4.csv")):
    code, item, dtls, rec, ref = row
    mcode = massage_code(code)
    if mcode is not None and item not in ("Reserved", "Unassigned"):
        map[mcode] = (item, rec == "Y", (code, item, rec, ref))

for code, (item, rec, meta) in sorted(map.items()):
    if rec:
        print_meta(meta)
        if code & 0xFF00 == 0x1300:
            item = item.replace("TLS_", "TLS13_")
        print("%s => 0x%04x," % (item, code))
        print()

print()

for code, (item, rec, meta) in sorted(map.items()):
    if not rec and notable(item):
        print_meta(meta)
        if code & 0xFF00 == 0x1300:
            item = item.replace("TLS_", "TLS13_")
        print("%s => 0x%04x," % (item, code))
        print()
