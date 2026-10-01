#!/usr/bin/env python3
"""Write a heat map (residual temporal std per pixel) for one view, next to the first frame.

    python tools/quality/flicker_heatmap.py /tmp/fl_after 08_mess /tmp/heat.png [/tmp/fl_before]

Bright = pixels whose luminance changes non-linearly across the sub-pixel camera steps (shimmer).
"""
import glob
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flicker_metric import luminance  # noqa: E402


def residual(d, cam):
    files = sorted(glob.glob(os.path.join(d, f"{cam}_[0-9][0-9].png")))
    st = np.stack([luminance(f) for f in files])
    t = np.arange(len(files), dtype=np.float32)
    t -= t.mean()
    slope = (st * t[:, None, None]).sum(0) / (t * t).sum()
    return (st - st.mean(0) - slope[None] * t[:, None, None]).std(0), files[0]


def main():
    d, cam, out = sys.argv[1:4]
    dirs = [d] + sys.argv[4:5]
    tiles = []
    for dd in dirs:
        r, f0 = residual(dd, cam)
        heat = np.clip(r / 8.0, 0, 1)
        rgb = np.stack([heat, heat ** 1.5, heat ** 3], 2)
        tiles.append(np.asarray(Image.open(f0).convert("RGB"), np.float32) / 255)
        tiles.append(rgb)
    Image.fromarray((np.concatenate([np.concatenate(tiles[i:i + 2], 1) for i in range(0, len(tiles), 2)], 0) * 255).astype(np.uint8)).save(out)


if __name__ == "__main__":
    main()
