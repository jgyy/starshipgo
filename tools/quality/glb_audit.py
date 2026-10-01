#!/usr/bin/env python3
"""Geometry audit of the component GLBs (stdlib only).

    python tools/quality/glb_audit.py [--models godot/models] [--json out.json] [--only REGEX]

Finds the defects that make props flicker or look wrong in the game:

  zfight      two triangles of DIFFERENT materials lie in the same plane (<= 1.5 mm apart), face the same way and overlap:
              the depth buffer cannot order them, the two surfaces flicker against each other
  degenerate  zero-area triangles (wasted, and they break normals / tangent generation)
  inverted    a closed primitive whose signed volume is negative (faces point inwards)
  nan         non-finite vertex positions
  nouv        a textured material (screen_/tex) on a primitive without UVs

Exit code 1 when any defect is found.  Parsing is a minimal glTF-binary reader (positions, indices, material per primitive).
"""
import argparse
import json
import math
import os
import re
import struct
import sys

COMP = {5120: ("b", 1), 5121: ("B", 1), 5122: ("h", 2), 5123: ("H", 2), 5125: ("I", 4), 5126: ("f", 4)}
NCOMP = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


def read_glb(path):
    with open(path, "rb") as f:
        data = f.read()
    magic, ver, ln = struct.unpack_from("<4sII", data, 0)
    assert magic == b"glTF"
    off = 12
    js = None
    binc = b""
    while off < len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        chunk = data[off + 8: off + 8 + clen]
        if ctype == 0x4E4F534A:
            js = json.loads(chunk)
        elif ctype == 0x004E4942:
            binc = chunk
        off += 8 + clen
    return js, binc


def accessor(js, binc, idx):
    acc = js["accessors"][idx]
    bv = js["bufferViews"][acc["bufferView"]]
    fmt, size = COMP[acc["componentType"]]
    n = NCOMP[acc["type"]]
    stride = bv.get("byteStride") or size * n
    base = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    out = []
    for i in range(acc["count"]):
        out.append(struct.unpack_from("<" + fmt * n, binc, base + i * stride))
    return out


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def tris_of(js, binc):
    """[(material index, mesh name, [(p0, p1, p2), ...], has_uv, closed_volume)] per primitive of every mesh."""
    out = []
    for mesh in js.get("meshes", []):
        for prim in mesh["primitives"]:
            attrs = prim["attributes"]
            pos = accessor(js, binc, attrs["POSITION"])
            ind = [i[0] for i in accessor(js, binc, prim["indices"])] if "indices" in prim else list(range(len(pos)))
            tris = [(pos[ind[i]], pos[ind[i + 1]], pos[ind[i + 2]]) for i in range(0, len(ind) - 2, 3)]
            out.append((prim.get("material", -1), mesh.get("name", ""), tris, "TEXCOORD_0" in attrs))
    return out


def plane_key(tri):
    n = cross(sub(tri[1], tri[0]), sub(tri[2], tri[0]))
    ln = math.sqrt(dot(n, n))
    if ln < 1e-12:
        return None, 0.0
    n = (n[0] / ln, n[1] / ln, n[2] / ln)
    # canonical direction: the face normal itself (back-to-back faces are NOT a z-fight problem)
    return n, ln / 2.0


def basis(n):
    a = (1.0, 0.0, 0.0) if abs(n[0]) < 0.9 else (0.0, 1.0, 0.0)
    u = cross(n, a)
    ul = math.sqrt(dot(u, u))
    u = (u[0] / ul, u[1] / ul, u[2] / ul)
    return u, cross(n, u)


def tri_overlap_2d(a, b, eps=1e-9):
    """Separating axis test for two 2D triangles; True if their interiors overlap by more than a sliver."""
    for t in (a, b):
        for i in range(3):
            p, q = t[i], t[(i + 1) % 3]
            ax, ay = -(q[1] - p[1]), q[0] - p[0]
            ln = math.hypot(ax, ay)
            if ln < 1e-12:
                continue
            ax, ay = ax / ln, ay / ln
            pa = [ax * v[0] + ay * v[1] for v in a]
            pb = [ax * v[0] + ay * v[1] for v in b]
            if max(pa) <= min(pb) + 1e-5 or max(pb) <= min(pa) + 1e-5:
                return False
    return True


def _closed(tris):
    """True if every edge of the triangle soup is shared by exactly two triangles (positions welded to 0.1 mm)."""
    q = lambda p: (round(p[0] * 1e4), round(p[1] * 1e4), round(p[2] * 1e4))
    edges = {}
    for t in tris:
        v = [q(p) for p in t]
        for i in range(3):
            e = (v[i], v[(i + 1) % 3]) if v[i] < v[(i + 1) % 3] else (v[(i + 1) % 3], v[i])
            edges[e] = edges.get(e, 0) + 1
    return all(c == 2 for c in edges.values())


def audit_model(path, plane_eps=0.0015):
    js, binc = read_glb(path)
    prims = tris_of(js, binc)
    res = {"zfight": 0, "degenerate": 0, "inverted": 0, "nan": 0, "nouv": 0, "tris": 0, "examples": []}
    buckets = {}
    names = [m.get("name", "") for m in js.get("materials", [])]
    for pi, (mat, mname, tris, has_uv) in enumerate(prims):
        mname_full = names[mat] if 0 <= mat < len(names) else ""
        if (mname_full.startswith("screen_") or mname_full.startswith("tex_")) and not has_uv:
            res["nouv"] += 1
        vol = 0.0
        for t in tris:
            res["tris"] += 1
            if any(not math.isfinite(c) for v in t for c in v):
                res["nan"] += 1
                continue
            n, area = plane_key(t)
            if n is None or area < 1e-9:
                res["degenerate"] += 1
                continue
            vol += dot(t[0], cross(t[1], t[2])) / 6.0
            d = dot(n, t[0])
            key = (round(n[0] * 200), round(n[1] * 200), round(n[2] * 200), round(d / plane_eps / 2))
            buckets.setdefault(key, []).append((pi, mat, t, n, d))
        if vol < -1e-6 and len(tris) > 12 and _closed(tris):
            # a closed shell with negative signed volume has its faces pointing inwards
            if abs(vol) > 1e-4:
                res["inverted"] += 1
                res["examples"].append("inverted primitive %d (%s) volume %.5f" % (pi, mname_full, vol))
    seen = set()
    for key, items in buckets.items():
        if len(items) < 2:
            continue
        cand = list(items)
        for k in (1, -1):                                # neighbouring distance bucket
            cand += buckets.get((key[0], key[1], key[2], key[3] + k), [])
        for i, a in enumerate(items):
            for b in cand:
                if a is b or a[1] == b[1] and a[0] == b[0]:
                    continue
                if a[1] == b[1]:
                    continue                             # same material: invisible
                if dot(a[3], b[3]) < 0.9998 or abs(a[4] - b[4]) > plane_eps:
                    continue
                pid = (min(id(a), id(b)), max(id(a), id(b)))
                if pid in seen:
                    continue
                u, v = basis(a[3])
                ta = [(dot(p, u), dot(p, v)) for p in a[2]]
                tb = [(dot(p, u), dot(p, v)) for p in b[2]]
                if tri_overlap_2d(ta, tb):
                    seen.add(pid)
                    res["zfight"] += 1
                    if len(res["examples"]) < 3:
                        c = tuple(round(sum(p[k] for p in a[2]) / 3, 3) for k in range(3))
                        res["examples"].append("z-fight at %s between materials %s and %s" % (
                            c, names[a[1]] if a[1] >= 0 else "?", names[b[1]] if b[1] >= 0 else "?"))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default=os.path.join(os.path.dirname(__file__), "..", "..", "godot", "models"))
    ap.add_argument("--only", default="")
    ap.add_argument("--json", default="")
    a = ap.parse_args()
    rx = re.compile(a.only) if a.only else None
    report = {}
    for base, _, files in sorted(os.walk(a.models)):
        for fn in sorted(files):
            if not fn.endswith(".glb"):
                continue
            mid = fn[:-4]
            if rx and not rx.search(mid):
                continue
            r = audit_model(os.path.join(base, fn))
            if r["zfight"] or r["degenerate"] or r["inverted"] or r["nan"] or r["nouv"]:
                report[mid] = r
    for mid, r in sorted(report.items()):
        print("%-48s z-fight %-3d degenerate %-3d inverted %-2d nouv %-2d  %s" % (
            mid, r["zfight"], r["degenerate"], r["inverted"], r["nouv"], "; ".join(r["examples"][:1])))
    tot = {k: sum(r[k] for r in report.values()) for k in ("zfight", "degenerate", "inverted", "nan", "nouv")}
    print("models with defects: %d   totals: %s" % (len(report), tot))
    if a.json:
        with open(a.json, "w") as f:
            json.dump(report, f, indent=1, sort_keys=True)
    sys.exit(1 if report else 0)


if __name__ == "__main__":
    main()
