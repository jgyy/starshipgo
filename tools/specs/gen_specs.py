#!/usr/bin/env python3
"""Machine datasheets for every model of godot/data/catalog.json.

    python tools/specs/gen_specs.py [--root DIR]

Writes godot/data/specs.json, docs/MACHINE_SPECS.md, docs/specs/<category>.md and docs/specs/specs.csv.  Everything is derived from
catalogue fields (id, category, label, tags, mount, size, tris, family) and the engineering profiles in specdata.py; numbers are seeded by
the model id, so the output is deterministic.  Standard library only.
"""
import argparse
import collections
import csv
import hashlib
import json
import math
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import software_data as sd  # noqa: E402
import specdata as D  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CREW_ZERO = {"light", "router", "antenna", "junction", "camera", "rack", "storage", "clock", "noticeboard", "cleaningbot", "door", "fountain", "beacon"}


def h(mid, salt):
    """Deterministic float in [0, 1) from the model id."""
    d = hashlib.sha256((mid + "|" + salt).encode()).digest()
    return int.from_bytes(d[:6], "big") / float(1 << 48)


def sig(x, n=3):
    """Round to n significant figures."""
    if x == 0:
        return 0
    digits = n - int(math.floor(math.log10(abs(x)))) - 1
    r = round(x, digits)
    return int(r) if digits <= 0 else r


def glb_screens(path):
    """Texture names of the screen materials of a GLB (materials named screen_<texture>, without screen_off), in file order."""
    try:
        with open(path, "rb") as f:
            head = f.read(20)
            if len(head) < 20 or head[:4] != b"glTF":
                return None
            n = struct.unpack("<I", head[12:16])[0]
            doc = json.loads(f.read(n).decode("utf-8"))
    except (OSError, ValueError):
        return None
    out = []
    for m in doc.get("materials", []):
        name = m.get("name", "")
        if name.startswith("screen_") and name != "screen_off" and name[7:] not in out:
            out.append(name[7:])
    return out


def find_adjust(cat, label):
    low = label.lower().replace("_", " ")
    for c, words, ch in D.ADJUST:
        if c == cat and any(w in low for w in words):
            return ch
    return {}


def profile_for(cat):
    if cat in D.PROFILES:
        return D.PROFILES[cat]
    if any(w in cat for w in D.PROVISION_WORDS):
        return D.PROVISION_PROFILE
    return D.DEFAULT_PROFILE


def supply(role, peak_w, gen_kw, cap_kwh, cls):
    if role == "none":
        return "none"
    if role == "store":
        return "48 VDC" if cap_kwh < 10 else "400 VDC"
    if role == "gen":
        return "6.6 kVAC 3ph" if gen_kw >= 1000 else "400 VAC 3ph"
    if peak_w <= 75:
        return "24 VDC"
    if peak_w <= 400 and cls in ("electronics", "bridge", "security", "science", "medical"):
        return "48 VDC"
    if peak_w <= 1900:
        return "120 VAC 1ph"
    if peak_w <= 15000:
        return "208 VAC 3ph"
    if peak_w <= 400000:
        return "400 VAC 3ph"
    return "6.6 kVAC 3ph"


def spec_for(m, root, used_pn):
    mid, cat, label = m["id"], m["category"], m["label"]
    cls_name, fill, mat, base_w, w_m3, maker = profile_for(cat)
    cls = D.CLASSES[cls_name]
    adj = find_adjust(cat, label)
    w, hh, d = m["size"]
    vol = max(w * hh * d, 1e-4)
    tris = m.get("tris", 0) or 0
    complexity = 0.9 + 0.2 * min(1.0, tris / 2500.0)
    jit = 0.92 + 0.16 * h(mid, "mass")
    mass = vol * fill * mat * complexity * jit * adj.get("massmul", 1.0)
    mass = max(mass, 0.05)
    mass = round(mass, 2) if mass < 10 else round(mass, 1) if mass < 1000 else int(round(mass))
    # role and electrical figures
    role = adj.get("role")
    default_role = {"reactor": "gen", "generator": "conv", "capacitor": "store", "turbine": "load"}.get(cat)
    if role is None:
        role = default_role
    passive = adj.get("passive", False)
    if role is None:
        role = "none" if (passive or (base_w == 0 and w_m3 == 0)) else "load"
    gen_kw = cap_kwh = rating_kva = 0.0
    idle = typ = peak = 0.0
    if role == "gen":
        gen_kw = vol * adj.get("genkw_m3", 600.0 if cat == "reactor" else 150.0) * jit
        typ = idle = peak = gen_kw * 1000 * 0.008  # parasitic load of pumps and controls
        peak = typ * 1.5
        idle = typ * 0.5
    elif role == "store":
        cap_kwh = mass * adj.get("kwh_kg", 0.2)
        gen_kw = cap_kwh * adj.get("discharge_c", 2.0)
        typ = 5 + cap_kwh * 2
        idle = typ * 0.5
        peak = typ * 2
    elif role == "conv":
        rating_kva = vol * 400.0
        typ = rating_kva * 1000 * 0.006
        idle = typ * 0.3
        peak = typ * 1.8
        if cat == "coil":
            typ = idle = peak = 0
            role = "none"
    elif role == "load":
        typ = adj.get("wset", base_w + w_m3 * vol) * adj.get("wmul", 1.0) * (0.9 + 0.2 * h(mid, "pw"))
        idle = typ * cls["idle"]
        peak = typ * (12.0 if cat == "door" else cls["peak"] * (1.3 if cat in ("reactor", "turbine") else 1.0))
    if role == "load" and typ <= 0:
        role = "none"
    if role == "none":
        idle = typ = peak = 0.0
    if typ > 0:
        idle, typ, peak = sig(idle, 2), sig(typ, 2), sig(peak, 2)
    if role == "gen":
        gen_kw = sig(gen_kw, 3)
    if role == "store":
        cap_kwh, gen_kw = sig(cap_kwh, 3), sig(gen_kw, 3)
    if role == "conv":
        rating_kva = sig(rating_kva, 3)
    # heat (W): electrical load turns into heat, producers reject their losses
    if role == "gen":
        heat = gen_kw * 1000 * (0.30 if cat == "reactor" else 0.06)
    elif role == "store":
        heat = gen_kw * 1000 * 0.002 + typ * 0.5
    elif role == "conv":
        heat = typ
    else:
        heat = typ * (0.92 if cls_name not in ("light",) else 0.8)
    heat = sig(heat, 2) if heat else 0
    # price (credits)
    price = mass * cls["price_kg"] * (0.8 + 0.4 * h(mid, "price"))
    if cls_name in ("machinery", "power", "lifesupport"):
        price += typ * 0.25
    if role == "gen":
        price += gen_kw * (1500 if cat == "reactor" else 600 if adj.get("genkw_m3") == 120.0 else 220)
    if role == "store":
        price += cap_kwh * (380 if adj.get("kwh_kg", 0.2) >= 0.1 else 1200)
    price += tris * 0.3
    price = max(5, sig(price, 3))
    if price >= 1000:
        price = int(round(price))
    lead = cls["lead"] + int(math.log10(max(price, 10)) * 6) + int(h(mid, "lead") * 10)
    mtbf = int(round(cls["mtbf"] * (0.7 + 0.6 * h(mid, "mtbf")), -2))
    if role == "gen" and cat == "reactor":
        mtbf = int(mtbf * 1.4)
    crew = cls["crew"] if role != "none" else 0
    if cat in CREW_ZERO:
        crew = 0
    if cat == "reactor":
        crew = 2
    noise = 0
    if role != "none" and cls["noise"]:
        noise = int(round(cls["noise"] + min(18.0, 5 * math.log10(1 + max(typ, gen_kw * 20) / 100.0))))
    cert = [c for c in cls["cert"] if "R3" not in c or cat == "reactor" or "fusion" in label.lower()]
    # screens / software
    screens = glb_screens(os.path.join(root, "godot", m["file"])) if m.get("file") else None
    if screens is None:
        screens = []
        fallback = [sd.CATEGORY_APP[cat]] if cat in D.SCREEN_CATEGORIES and cat in sd.CATEGORY_APP else []
        apps = fallback
    else:
        apps = []
        for t in screens:
            a = sd.resolve_app(t, cat)
            if a not in apps:
                apps.append(a)
    # model number and designation
    maker_name = D.MAKERS[maker][0]
    code = "".join(ch for ch in cat.upper() if ch.isalnum())[:3]
    n = 1000 + int(h(mid, "pn") * 9000)
    while "%s-%s-%d" % (maker, code, n) in used_pn:
        n += 1
    pn = "%s-%s-%d" % (maker, code, n)
    used_pn.add(pn)
    title = D.CATEGORY_TITLES.get(cat, cat.replace("_", " ").capitalize())
    desig = "%s - %s" % (title, label.replace("_", " ").title())
    # notes
    notes = []
    notes.append("%s-mounted%s." % (m["mount"], ", free-standing" if m.get("solid") and m["mount"] == "floor" else ""))
    if mass >= 250:
        notes.append("Install with a hoist or gantry (%s)." % fmt_mass(mass))
    elif mass >= 25:
        notes.append("Two-person lift.")
    if adj.get("note"):
        notes.append(adj["note"])
    if role == "gen":
        notes.append("Output %s at %s; connect only through its breaker panel." % (fmt_w(gen_kw * 1000), supply(role, 0, gen_kw, 0, cls_name)))
    if role == "store":
        notes.append("Stores %s kWh; discharge limited to %s." % (fmt_num(cap_kwh), fmt_w(gen_kw * 1000)))
    if role == "conv":
        notes.append("Conversion rating %s kVA; losses about 0.6 %% at typical load." % rating_kva)
    if cls_name == "provision":
        notes.append("Perishable provision; store below 30 C.")
    spec = {"cat": cat, "cls": cls_name, "r": {"load": "c", "none": "p", "gen": "g", "store": "s", "conv": "x"}[role],
            "m": maker_name, "pn": pn, "d": desig,
            "dim": [int(round(w * 1000)), int(round(hh * 1000)), int(round(d * 1000))], "kg": mass,
            "w": [idle, typ, peak], "v": supply(role if role != "load" else "x", peak, gen_kw, cap_kwh, cls_name) if role != "none" else "none",
            "gen": gen_kw, "cap": cap_kwh, "kva": rating_kva, "heat": heat, "cr": price, "lead": lead, "mtbf": mtbf if cls["mtbf"] else 0,
            "svc": cls["svc"], "life": cls["life"], "crew": crew, "ip": cls["ip"], "temp": list(cls["temp"]), "db": noise,
            "cert": cert, "if": cls["iface"] if role != "none" else "", "sw": apps, "scr": screens, "n": " ".join(notes)}
    return spec


def build(root):
    with open(os.path.join(root, "godot", "data", "catalog.json")) as f:
        cat = json.load(f)["models"]
    used = set()
    models = {}
    for m in sorted(cat, key=lambda m: m["id"]):
        models[m["id"]] = spec_for(m, root, used)
    return {"version": 1, "currency": "cr", "models": models}


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write('{"version": %d, "currency": "%s", "models": {\n' % (data["version"], data["currency"]))
        items = list(data["models"].items())
        for i, (k, v) in enumerate(items):
            f.write(" %s: %s%s\n" % (json.dumps(k), json.dumps(v, separators=(",", ":")), "," if i < len(items) - 1 else ""))
        f.write("}}\n")


def fmt_num(x):
    if isinstance(x, float):
        return ("%.2f" % x).rstrip("0").rstrip(".")
    return str(x)


def fmt_w(w):
    if w >= 1e6:
        return "%s MW" % fmt_num(round(w / 1e6, 2))
    if w >= 1e3:
        return "%s kW" % fmt_num(round(w / 1e3, 2))
    return "%s W" % fmt_num(w)


def fmt_mass(kg):
    return "%s t" % fmt_num(round(kg / 1000.0, 2)) if kg >= 1000 else "%s kg" % fmt_num(kg)


def fmt_cr(c):
    if c >= 1e6:
        return "%s M" % fmt_num(round(c / 1e6, 2))
    if c >= 1e4:
        return "%s k" % fmt_num(round(c / 1e3, 1))
    return "{:,}".format(int(round(c)))


def esc(s):
    return str(s).replace("|", "\\|")


ROLE_NAMES = {"c": "consumer", "p": "passive", "g": "producer", "s": "energy storage", "x": "converter"}


def write_csv(path, data):
    with open(path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["id", "category", "class", "role", "manufacturer", "part_number", "designation", "width_mm", "height_mm", "depth_mm", "mass_kg",
                    "power_idle_w", "power_typ_w", "power_peak_w", "supply", "output_kw", "capacity_kwh", "heat_w", "price_cr", "lead_days",
                    "mtbf_h", "service_interval_h", "life_years", "crew", "ip", "temp_min_c", "temp_max_c", "noise_dba", "interface", "software",
                    "certifications"])
        for k, s in data["models"].items():
            w.writerow([k, s["cat"], s["cls"], ROLE_NAMES[s["r"]], s["m"], s["pn"], s["d"], *s["dim"], s["kg"], *s["w"], s["v"], s["gen"], s["cap"],
                        s["heat"], s["cr"], s["lead"], s["mtbf"], s["svc"], s["life"], s["crew"], s["ip"], s["temp"][0], s["temp"][1], s["db"],
                        s["if"], " ".join(s["sw"]), "; ".join(s["cert"])])


def category_doc(cat, rows):
    out = []
    w = out.append
    title = D.CATEGORY_TITLES.get(cat, cat.capitalize())
    w("# Machine datasheets - %s (`%s`)" % (title, cat))
    w("")
    w("*Generated by `python tools/specs/gen_specs.py`; do not edit by hand. Back to the [index](../MACHINE_SPECS.md).*")
    w("")
    w("%d models. Mass is dry mass; power is electrical (consumers draw, producers and storage supply). Prices are in credits (cr)." % len(rows))
    w("")
    w("| Model | Designation | Manufacturer | Size mm (W x H x D) | Mass | Power typ. | Supply | Price cr |")
    w("|---|---|---|---|---|---|---|---|")
    for k, s in rows:
        pw = ("+" + fmt_w(s["gen"] * 1000) + " out") if s["r"] == "g" else ("%s kWh" % fmt_num(s["cap"])) if s["r"] == "s" else fmt_w(s["w"][1])
        w("| `%s` | %s | %s | %d x %d x %d | %s | %s | %s | %s |" % (k, esc(s["d"]), esc(s["m"]), s["dim"][0], s["dim"][1], s["dim"][2], fmt_mass(s["kg"]), pw, s["v"], fmt_cr(s["cr"])))
    w("")
    w("## Datasheets")
    w("")
    for k, s in rows:
        w("### `%s`" % k)
        w("")
        w("**%s**, %s, part %s (%s)" % (s["d"], s["m"], s["pn"], ROLE_NAMES[s["r"]]))
        w("")
        w("* Mass %s; size %d x %d x %d mm; heat %s." % (fmt_mass(s["kg"]), s["dim"][0], s["dim"][1], s["dim"][2], fmt_w(s["heat"])))
        if s["r"] == "g":
            w("* Output %s kW at %s; own load %s." % (fmt_num(s["gen"]), s["v"], fmt_w(s["w"][1])))
        elif s["r"] == "s":
            w("* Capacity %s kWh, discharge up to %s kW at %s." % (fmt_num(s["cap"]), fmt_num(s["gen"]), s["v"]))
        elif s["r"] == "x":
            w("* Converter rating %s kVA, %s; losses %s." % (fmt_num(s["kva"]), s["v"], fmt_w(s["w"][1])))
        elif s["r"] == "c":
            w("* Power %s idle / %s typical / %s peak at %s." % (fmt_w(s["w"][0]), fmt_w(s["w"][1]), fmt_w(s["w"][2]), s["v"]))
        else:
            w("* Passive: no electrical load.")
        w("* Price %s cr, lead time %d days, MTBF %s, service every %s, service life %d years, crew %d." % (
            fmt_cr(s["cr"]), s["lead"], ("%s h" % "{:,}".format(s["mtbf"])) if s["mtbf"] else "n/a", ("%s h" % "{:,}".format(s["svc"])) if s["svc"] else "n/a", s["life"], s["crew"]))
        w("* %s, %d to %d C%s; certifications: %s%s." % (s["ip"], s["temp"][0], s["temp"][1], ", %d dB(A)" % s["db"] if s["db"] else "", ", ".join(s["cert"]),
                                                          ("; interface: " + s["if"]) if s["if"] else ""))
        if s["sw"]:
            w("* Software: %s (screens: %s)." % (", ".join("`%s`" % a for a in s["sw"]), ", ".join(s["scr"]) or "category default"))
        w("* %s" % s["n"])
        w("")
    return "\n".join(out) + "\n"


def top_table(w, title, rows, key, cols):
    w("**%s**" % title)
    w("")
    w("| # | Model | Category | %s |" % " | ".join(c[0] for c in cols))
    w("|---|---|---|" + "---|" * len(cols))
    for i, (k, s) in enumerate(sorted(rows, key=lambda kv: (-key(kv[1]), kv[0]))[:10], 1):
        w("| %d | `%s` | %s | %s |" % (i, k, s["cat"], " | ".join(c[1](s) for c in cols)))
    w("")


def index_doc(data):
    out = []
    w = out.append
    models = data["models"]
    bycat = collections.defaultdict(list)
    for k, s in models.items():
        bycat[s["cat"]].append((k, s))
    w("# StarshipGo - Machine Datasheets")
    w("")
    w("*Generated by `python tools/specs/gen_specs.py` from `godot/data/catalog.json`; do not edit by hand. Machine-readable: "
      "[`godot/data/specs.json`](../godot/data/specs.json) and [`docs/specs/specs.csv`](specs/specs.csv).*")
    w("")
    w("Every one of the %d models of the component library has an invented but plausible engineering datasheet: manufacturer, part number, "
      "dimensions, mass, power consumption, heat, price, reliability, ingress protection, certifications, data interface and the software it runs. "
      "The ship-level totals are in [SHIP_SPEC.md](SHIP_SPEC.md) and the bill of materials ([BOM.md](BOM.md)) carries mass, power and price columns." % len(models))
    w("")
    w("## 1. How the numbers are derived")
    w("")
    bullets = [
        "**Dimensions** are the catalogue bounding box (mm).",
        "**Mass** = bounding volume x *fill factor* x *material density* of the category (for example 0.10 x 1400 kg/m3 for a bridge console, 0.25 x 5000 kg/m3 for a reactor), "
        "x a +/-8 % complexity and seed factor. It is the dry mass.",
        "**Power**: consumers get *typical W = base + W per m3 x volume* of their category (with label-based adjustments such as ovens and pumps); idle and peak "
        "are class fractions (doors peak at 12x while moving). Passive items draw 0 W. **Producers** (reactors, gensets, micro-fusion, turbines, fuel cells) have an "
        "output in kW and a small parasitic load; **energy storage** (batteries, capacitors, flywheels) has a capacity in kWh and a discharge rating; "
        "**converters** (transformers, inverters) have a kVA rating and a loss.",
        "**Supply**: 24 VDC up to 75 W, 48 VDC for small electronics, 120 VAC 1ph up to 1.9 kW, 208 VAC 3ph up to 15 kW, 400 VAC 3ph up to 400 kW and 6.6 kVAC 3ph above. "
        "Producers feed 400 VAC (below 1 MW) or 6.6 kVAC; batteries are 48 VDC (small) or 400 VDC.",
        "**Heat** = 92 % of the electrical load (80 % for lights); producers reject 30 % (reactors) or 6 % of their output.",
        "**Price** = mass x class price per kg (x 0.8-1.2) + power-dependent and output-dependent terms + 0.3 cr per triangle of detail; rounded to three significant figures.",
        "**Reliability**: MTBF, maintenance interval, service life and crew are class values (MTBF varied by +/-30 %). **Noise** grows with power.",
        "**Software**: the screen textures actually used by the model's GLB (materials `screen_<texture>`) are mapped to application ids "
        "by the rules of [SOFTWARE_SPEC.md](SOFTWARE_SPEC.md) section 3.",
        "Everything is seeded by the model id, so the files are byte-identical on every run.",
    ]
    for b in bullets:
        w("* " + b)
    w("")
    w("### Compact keys of `specs.json`")
    w("")
    w("`{\"version\": 1, \"currency\": \"cr\", \"models\": {id: {...}}}`")
    w("")
    w("| Key | Meaning |")
    w("|---|---|")
    for k, v in [("cat", "catalogue category"), ("cls", "engineering class"), ("r", "role: `c` consumer, `p` passive, `g` producer, `s` storage, `x` converter"),
                 ("m", "manufacturer"), ("pn", "part number"), ("d", "designation"), ("dim", "[width, height, depth] mm"), ("kg", "dry mass in kg"),
                 ("w", "[idle, typical, peak] electrical load in W (0 for passive)"), ("v", "supply voltage / bus"), ("gen", "output kW (producers) or discharge kW (storage)"),
                 ("cap", "storage capacity kWh"), ("kva", "converter rating kVA"), ("heat", "heat dissipation W"), ("cr", "unit price in credits"),
                 ("lead", "lead time days"), ("mtbf", "MTBF hours (0 = n/a)"), ("svc", "maintenance interval hours"), ("life", "service life years"),
                 ("crew", "crew needed to operate"), ("ip", "ingress protection"), ("temp", "[min, max] operating temperature C"), ("db", "noise dB(A)"),
                 ("cert", "certifications (invented Concord Standards Agency codes)"), ("if", "data interface"), ("sw", "application ids it runs"),
                 ("scr", "screen texture names found in its GLB"), ("n", "installation notes")]:
        w("| `%s` | %s |" % (k, v))
    w("")
    w("## 2. Category summary")
    w("")
    w("Totals are for one of every model of the category (not the ship installation).")
    w("")
    w("| Category | Models | Total mass | Typical load | Output | Storage | Total price cr | Sheet |")
    w("|---|---|---|---|---|---|---|---|")
    tm = tp = tc = tg = ts = 0
    for cat in sorted(bycat):
        rows = bycat[cat]
        mass = sum(s["kg"] for _, s in rows)
        pw = sum(s["w"][1] for _, s in rows)
        gen = sum(s["gen"] for _, s in rows if s["r"] == "g")
        cap = sum(s["cap"] for _, s in rows if s["r"] == "s")
        price = sum(s["cr"] for _, s in rows)
        tm, tp, tc, tg, ts = tm + mass, tp + pw, tc + price, tg + gen, ts + cap
        w("| `%s` %s | %d | %s | %s | %s | %s | %s | [%s](specs/%s.md) |" % (cat, D.CATEGORY_TITLES.get(cat, ""), len(rows), fmt_mass(mass), fmt_w(pw),
                                                                    (fmt_num(round(gen / 1000, 2)) + " MW") if gen else "-", ("%s kWh" % fmt_num(round(cap, 1))) if cap else "-",
                                                                    fmt_cr(price), cat, cat))
    w("| **All** | **%d** | **%s** | **%s** | **%s MW** | **%s kWh** | **%s** | |" % (len(models), fmt_mass(tm), fmt_w(tp), fmt_num(round(tg / 1000, 2)), fmt_num(round(ts, 1)), fmt_cr(tc)))
    w("")
    w("## 3. Top ten")
    w("")
    top_table(w, "Heaviest", list(models.items()), lambda s: s["kg"], [("Mass", lambda s: fmt_mass(s["kg"]))])
    top_table(w, "Highest typical electrical load", list(models.items()), lambda s: s["w"][1], [("Typical", lambda s: fmt_w(s["w"][1])), ("Supply", lambda s: s["v"])])
    top_table(w, "Most expensive", list(models.items()), lambda s: s["cr"], [("Price cr", lambda s: fmt_cr(s["cr"]))])
    top_table(w, "Largest power producers", [kv for kv in models.items() if kv[1]["r"] == "g"], lambda s: s["gen"], [("Output", lambda s: fmt_w(s["gen"] * 1000))])
    top_table(w, "Largest energy storage", [kv for kv in models.items() if kv[1]["r"] == "s"], lambda s: s["cap"], [("Capacity", lambda s: "%s kWh" % fmt_num(s["cap"])), ("Discharge", lambda s: fmt_w(s["gen"] * 1000))])
    top_table(w, "Largest bounding volume", list(models.items()), lambda s: s["dim"][0] * s["dim"][1] * s["dim"][2], [("Size mm", lambda s: "%d x %d x %d" % tuple(s["dim"]))])
    w("## 4. Manufacturers")
    w("")
    w("| Manufacturer | Range | Models |")
    w("|---|---|---|")
    cnt = collections.Counter(s["m"] for s in models.values())
    for code, (name, rng) in sorted(D.MAKERS.items(), key=lambda kv: kv[1][0]):
        w("| %s | %s | %d |" % (name, rng, cnt.get(name, 0)))
    w("")
    w("## 5. Supply voltages")
    w("")
    w("| Supply | Models |")
    w("|---|---|")
    vc = collections.Counter(s["v"] for s in models.values())
    for v, n in sorted(vc.items()):
        w("| %s | %d |" % (v, n))
    w("")
    sw = collections.Counter(a for s in models.values() for a in s["sw"])
    w("## 6. Software hosted by machines")
    w("")
    w("| Application | Models with a screen running it |")
    w("|---|---|")
    for a, n in sorted(sw.items()):
        w("| `%s` | %d |" % (a, n))
    w("")
    return "\n".join(out) + "\n"


def write_all(root, out_root=None):
    out_root = out_root or root
    data = build(root)
    write_json(os.path.join(out_root, "godot", "data", "specs.json"), data)
    docs = os.path.join(out_root, "docs")
    os.makedirs(os.path.join(docs, "specs"), exist_ok=True)
    with open(os.path.join(docs, "MACHINE_SPECS.md"), "w") as f:
        f.write(index_doc(data))
    bycat = collections.defaultdict(list)
    for k, s in data["models"].items():
        bycat[s["cat"]].append((k, s))
    for cat, rows in bycat.items():
        with open(os.path.join(docs, "specs", cat + ".md"), "w") as f:
            f.write(category_doc(cat, rows))
    write_csv(os.path.join(docs, "specs", "specs.csv"), data)
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--out", default=None, help="write into this root instead (for tests)")
    a = ap.parse_args()
    d = write_all(a.root, a.out)
    print("specs for %d models" % len(d["models"]))


if __name__ == "__main__":
    main()
