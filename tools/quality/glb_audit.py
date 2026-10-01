#!/usr/bin/env python3
"""Stdlib-only GLB reader and geometry audit for the generated models.

    python tools/quality/glb_audit.py            # audit godot/models + godot/arch, print a summary
    python tools/quality/glb_audit.py --list     # every finding

`load(path)` returns {"json", "meshes": [{name, pos, nrm, uv, idx, mat}], "materials"}.
Findings are (check, model id, detail).  Exit status is 1 when anything is found.
"""
import hashlib
import json
import math
import os
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CT = {5120: ("b", 1), 5121: ("B", 1), 5122: ("h", 2), 5123: ("H", 2), 5125: ("I", 4), 5126: ("f", 4)}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def read_glb(path):
    with open(path, "rb") as fh:
        data = fh.read()
    magic, ver, length = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or ver != 2 or length != len(data):
        raise ValueError(f"{path}: bad GLB header (magic={magic!r} ver={ver} len={length}/{len(data)})")
    off, js, binc = 12, None, b""
    while off < len(data):
        n, t = struct.unpack_from("<I4s", data, off)
        body = data[off + 8: off + 8 + n]
        if t == b"JSON":
            js = json.loads(body)
        elif t == b"BIN\0":
            binc = body
        off += 8 + n
    return js, binc


def accessor(js, binc, i):
    a = js["accessors"][i]
    bv = js["bufferViews"][a["bufferView"]]
    fmt, sz = CT[a["componentType"]]
    nc = NC[a["type"]]
    stride = bv.get("byteStride") or sz * nc
    base = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    out = []
    for k in range(a["count"]):
        row = struct.unpack_from("<" + fmt * nc, binc, base + k * stride)
        out.append(row[0] if nc == 1 else row)
    return out


def _mul(a, b):
    return [sum(a[r + k * 4] * b[k + c * 4] for k in range(4)) for c in range(4) for r in range(4)]


def _node_matrix(n):
    if "matrix" in n:
        return list(n["matrix"])
    t = n.get("translation", (0, 0, 0))
    x, y, z, w = n.get("rotation", (0, 0, 0, 1))
    s = n.get("scale", (1, 1, 1))
    r = [1 - 2 * (y * y + z * z), 2 * (x * y + z * w), 2 * (x * z - y * w), 0,
         2 * (x * y - z * w), 1 - 2 * (x * x + z * z), 2 * (y * z + x * w), 0,
         2 * (x * z + y * w), 2 * (y * z - x * w), 1 - 2 * (x * x + y * y), 0, 0, 0, 0, 1]
    for c in range(3):
        for k in range(3):
            r[c * 4 + k] *= s[c]
    r[12], r[13], r[14] = t
    return r


def load(path):
    js, binc = read_glb(path)
    meshes = []
    nodes = js.get("nodes", [])

    def walk(i, parent):
        n = nodes[i]
        m = _mul(parent, _node_matrix(n))
        if "mesh" in n:
            for p in js["meshes"][n["mesh"]]["primitives"]:
                at = p["attributes"]
                pos = accessor(js, binc, at["POSITION"])
                pos = [(m[0] * x + m[4] * y + m[8] * z + m[12], m[1] * x + m[5] * y + m[9] * z + m[13],
                        m[2] * x + m[6] * y + m[10] * z + m[14]) for x, y, z in pos]
                idx = accessor(js, binc, p["indices"]) if "indices" in p else list(range(len(pos)))
                meshes.append({
                    "name": n.get("name", ""), "pos": pos,
                    "nrm": accessor(js, binc, at["NORMAL"]) if "NORMAL" in at else None,
                    "uv": accessor(js, binc, at["TEXCOORD_0"]) if "TEXCOORD_0" in at else None,
                    "idx": [tuple(idx[k:k + 3]) for k in range(0, len(idx) - len(idx) % 3, 3)],
                    "mat": p.get("material"), "mode": p.get("mode", 4), "nidx": len(idx)})
        for c in n.get("children", []):
            walk(c, m)

    ident = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    scenes = js.get("scenes") or [{"nodes": list(range(len(nodes)))}]
    for r in scenes[0]["nodes"]:
        walk(r, ident)
    return {"json": js, "meshes": meshes, "materials": js.get("materials", [])}


def bounds(g):
    pts = [p for m in g["meshes"] for p in m["pos"]]
    if not pts:
        return None
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]


def tri_count(g):
    return sum(len(m["idx"]) for m in g["meshes"])


def signed_volume(m):
    v = 0.0
    P = m["pos"]
    for a, b, c in m["idx"]:
        ax, ay, az = P[a]
        bx, by, bz = P[b]
        cx, cy, cz = P[c]
        v += (ax * (by * cz - bz * cy) - ay * (bx * cz - bz * cx) + az * (bx * cy - by * cx)) / 6.0
    return v


def geometry_hash(g):
    h = hashlib.sha1()
    for m in sorted(g["meshes"], key=lambda m: (m["name"], len(m["pos"]))):
        for p in sorted(m["pos"]):
            h.update(("%.3f,%.3f,%.3f;" % p).encode())
    return h.hexdigest()


def audit_file(path):
    """Return a list of (check, detail) for one GLB."""
    out = []
    g = load(path)
    b = bounds(g)
    if b is None:
        return [("empty", "no geometry")]
    for m in g["meshes"]:
        for p in m["pos"]:
            if any(math.isnan(c) or abs(c) > 100 for c in p):
                out.append(("bad_vertex", f"{m['name']} vertex {p}"))
                break
        if any(max(t) >= len(m["pos"]) for t in m["idx"]):
            out.append(("bad_index", m["name"]))
        if m["uv"] and any(math.isnan(u) or math.isnan(v) for u, v in m["uv"]):
            out.append(("bad_uv", m["name"]))
        if m["mat"] is None:
            out.append(("no_material", m["name"]))
    used = {m["mat"] for m in g["meshes"] if m["mat"] is not None}
    for i, mt in enumerate(g["materials"]):
        if i not in used:
            out.append(("unused_material", mt.get("name", str(i))))
        e = mt.get("extensions", {}).get("KHR_materials_emissive_strength", {}).get("emissiveStrength", 1.0)
        if e > 20:
            out.append(("emissive_strength", f"{mt.get('name')} {e}"))
    return out


def all_glbs():
    out = []
    for sub in ("godot/models", "godot/arch"):
        for dp, _, fs in os.walk(os.path.join(ROOT, sub)):
            out += [os.path.join(dp, f) for f in fs if f.endswith(".glb")]
    return sorted(out)


def main():
    findings = {}
    for p in all_glbs():
        for chk, det in audit_file(p):
            findings.setdefault(chk, []).append((os.path.basename(p)[:-4], det))
    for chk, v in sorted(findings.items()):
        print(f"{chk}: {len(v)}")
        if "--list" in sys.argv:
            for mid, det in v:
                print("   ", mid, det)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
