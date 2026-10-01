#!/usr/bin/env python3
"""Write docs/bugs/round2/zfight.json: one defect per generator family whose models had coplanar overlapping faces.

    python tools/quality/make_zfight_ledger.py

Input: docs/bugs/glb_audit_before.json (tools/quality/glb_audit.py run over the committed models before the exporter fix),
godot/data/catalog.json (family of every model) and a live audit of godot/models (the "after" numbers).
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import glb_audit  # noqa: E402


def main():
    with open(os.path.join(ROOT, "docs", "bugs", "glb_audit_before.json"), encoding="utf-8") as f:
        before = json.load(f)
    with open(os.path.join(ROOT, "godot", "data", "catalog.json"), encoding="utf-8") as f:
        cat = {m["id"]: m for m in json.load(f)["models"]}
    fam = collections.OrderedDict()
    for mid in sorted(before):
        c = cat.get(mid)
        if c is None:
            continue
        fam.setdefault(c["family"], []).append(mid)
    out = []
    for i, (f, ids) in enumerate(sorted(fam.items()), 1):
        pre = sum(before[m]["zfight"] for m in ids)
        post = 0
        for m in ids:
            path = os.path.join(ROOT, "godot", cat[m]["file"])
            post += glb_audit.audit_model(path)["zfight"]
        ex = next((before[m]["examples"][0] for m in ids if before[m]["examples"]), "")
        out.append({
            "id": "Z%03d" % i, "area": "blender-models", "severity": "medium" if pre >= 100 else "low",
            "file": "blender/starship/components (family `%s`)" % f, "lines": "family function",
            "title": "Coplanar faces of different materials flicker in %d model(s) of family `%s`" % (len(ids), f),
            "evidence": "tools/quality/glb_audit.py over the committed GLBs found %d overlapping coplanar face pairs (<= 1.5 mm apart, same "
                        "facing, different materials) in %s%s; e.g. %s." % (
                            pre, ", ".join("`%s`" % m for m in ids[:4]), " and %d more" % (len(ids) - 4) if len(ids) > 4 else "", ex),
            "impact": "The depth buffer cannot order two surfaces in the same plane, so an inlaid strip, bezel or screen quad flickers against its "
                      "panel as the camera moves (the user's 'textures flicker').",
            "fix": "kit.fix_zfight lifts the smaller face of every such pair by 3 mm at export and slides the model back so the mounting plane "
                   "is unchanged.",
            "resolution": "Rebuilt with the exporter fix: %d pairs remain after the rebuild (`python tools/quality/glb_audit.py`); "
                          "`tests/test_regress_assets.py` / `tests/test_zfight_budget.py` keep the total under budget." % post,
        })
    with open(os.path.join(ROOT, "docs", "bugs", "round2", "zfight.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print(len(out), "families")


if __name__ == "__main__":
    main()
