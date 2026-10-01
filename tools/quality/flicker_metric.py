#!/usr/bin/env python3
"""Shimmer metric for the frames written by godot/tests/flicker_probe.gd.

    python tools/quality/flicker_metric.py /tmp/fl            # prints a table, --json for machines

For every view <cam>_00.png .. <cam>_NN.png (same scene, camera yawed by sub-pixel steps) it computes, per pixel,
the standard deviation of luminance across frames.  Numbers are on the 0..255 scale:
  raw      mean per-pixel temporal std (includes the genuine motion of edges)
  resid    mean std after removing the per-pixel linear trend over the frame index - genuine sub-pixel motion is
           almost linear, aliasing / shimmer is not, so this is the number that tracks "flicker"
  p95res   95th percentile of the per-pixel residual
  %>2      share of pixels (percent) whose residual exceeds 2 grey levels
Needs numpy + pillow.
"""
import argparse
import glob
import json
import os
import re

import numpy as np
from PIL import Image


def luminance(path):
    a = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32)
    return a @ np.array([0.2126, 0.7152, 0.0722], np.float32)


def analyse(directory):
    groups = {}
    for p in sorted(glob.glob(os.path.join(directory, "*_[0-9][0-9].png"))):
        m = re.match(r"(.+)_(\d\d)\.png$", os.path.basename(p))
        groups.setdefault(m.group(1), []).append(p)
    out = {}
    for cam, files in groups.items():
        if len(files) < 3:
            continue
        stack = np.stack([luminance(f) for f in files])          # (n, h, w)
        n = stack.shape[0]
        raw = stack.std(axis=0)
        t = np.arange(n, dtype=np.float32)
        t -= t.mean()
        slope = (stack * t[:, None, None]).sum(axis=0) / (t * t).sum()
        resid = (stack - stack.mean(axis=0) - slope[None] * t[:, None, None]).std(axis=0)
        out[cam] = {"frames": n, "raw": float(raw.mean()), "residual": float(resid.mean()),
                    "p95_residual": float(np.percentile(resid, 95)),
                    "pct_pixels_residual_gt2": float((resid > 2.0).mean() * 100)}
    if out:
        out["MEAN"] = {k: float(np.mean([v[k] for c, v in out.items()])) for k in
                       ("raw", "residual", "p95_residual", "pct_pixels_residual_gt2")}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    res = analyse(a.dir)
    if a.json:
        print(json.dumps(res, indent=1))
        return
    print(f"{'view':<20}{'raw':>8}{'resid':>8}{'p95res':>8}{'%>2':>8}")
    for cam, v in res.items():
        print(f"{cam:<20}{v.get('raw', 0):8.3f}{v['residual']:8.3f}{v['p95_residual']:8.3f}{v['pct_pixels_residual_gt2']:8.2f}")


if __name__ == "__main__":
    main()
