#!/usr/bin/env python3
"""potpng292.py -- one summary picture per pot, assembled from the per-lane thumbnails that each
array task wrote before its geometry was deleted (ticket 292, Needs-eye line)."""
import glob
import os
import sys

from PIL import Image, ImageDraw


def main(run):
    out = os.path.join(run, "out")
    tiles = sorted(glob.glob(os.path.join(out, "tiles", "*.png")))
    if not tiles:
        print("[POTPNG] no tiles")
        return 1
    by_pot = {}
    for t in tiles:
        pot = os.path.basename(t).split("_Piece_")[0]
        by_pot.setdefault(pot, []).append(t)
    cols = 8
    for pot, ts in sorted(by_pot.items()):
        n = len(ts)
        rows = (n + cols - 1) // cols
        tw, th = Image.open(ts[0]).size
        head = 36
        img = Image.new("RGB", (cols * tw, rows * th + head), "white")
        d = ImageDraw.Draw(img)
        d.text((8, 6), pot + ": " + str(n) + " lanes. Green = ours, black = the authors. One thumbnail per lane.", fill="black")
        d.text((8, 20), "Each written by its array task from the exported lane, before the geometry was deleted (ticket 292).", fill="gray")
        for i, t in enumerate(ts):
            img.paste(Image.open(t).convert("RGB"), ((i % cols) * tw, head + (i // cols) * th))
        p = os.path.join(out, "png", "pot_" + pot + ".png")
        img.save(p)
        print("[POTPNG] " + p + " " + str(img.size) + " tiles=" + str(n))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))