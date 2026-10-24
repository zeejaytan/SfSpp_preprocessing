#!/usr/bin/env python3
"""recompute292.py -- recompute one lane by hand and check it against its own row in lanes.tsv.

The point is independence from score292.py: its own PCD parser, and every distance from a full
ours x authors matrix (no tree, no library metric). Ticket 292 asks for four lanes this way,
before the exports are deleted."""
import sys

import numpy as np


def read_xyz(path):
    with open(path, "rb") as f:
        fields, sizes, types, n, mode = None, None, None, None, None
        while True:
            raw = f.readline()
            if not raw:
                raise ValueError("truncated header: " + path)
            line = raw.decode("ascii", "replace").strip()
            parts = line.split()
            if not parts:
                continue
            key = parts[0]
            if key == "FIELDS":
                fields = parts[1:]
            elif key == "SIZE":
                sizes = [int(v) for v in parts[1:]]
            elif key == "TYPE":
                types = parts[1:]
            elif key == "WIDTH":
                n = int(parts[1])
            elif key == "DATA":
                mode = parts[1]
                break
        if mode == "ascii":
            rows = f.read().decode("ascii", "replace").split("\n")
            vals = np.array([float(v) for v in " ".join(rows).split()][: n * len(fields)], dtype=np.float64)
            table = vals.reshape(n, len(fields))
        elif mode == "binary":
            if sorted(set(sizes)) != [4]:
                raise ValueError("only float32 fields are handled: " + path)
            nf = len(fields)
            flat = np.frombuffer(f.read(n * nf * 4), dtype="<f4", count=n * nf).astype(np.float64)
            table = flat.reshape(n, nf)
        else:
            raise ValueError("unsupported DATA " + str(mode) + " in " + path)
        ix = [fields.index(k) for k in ("x", "y", "z")]
        return table[:, ix]


def main(argv):
    if len(argv) != 6:
        print("usage: recompute292.py <piece> <lane> <ours.pcd> <author.pcd> <lanes.tsv>", file=sys.stderr)
        return 2
    piece, lane, ours_path, auth_path, lanes_path = argv[1:6]
    ours = read_xyz(ours_path)
    auth = read_xyz(auth_path)

    d_oa = np.empty(len(ours))
    for s in range(0, len(ours), 200):
        d_oa[s:s + 200] = np.linalg.norm(ours[s:s + 200, None, :] - auth[None, :, :], axis=2).min(axis=1)
    d_ao = np.empty(len(auth))
    for s in range(0, len(auth), 200):
        d_ao[s:s + 200] = np.linalg.norm(auth[s:s + 200, None, :] - ours[None, :, :], axis=2).min(axis=1)

    steps = np.linalg.norm(np.diff(ours, axis=0), axis=1) if len(ours) > 1 else np.zeros(0)
    mine = dict(n_ours=len(ours), n_auth=len(auth), median=float(np.median(d_oa)),
                cov_ours=100.0 * float((d_oa < 2.0).mean()), cov_auth=100.0 * float((d_ao < 2.0).mean()),
                jumps=int((steps > 10.0).sum()), max_step=float(steps.max()) if len(steps) else 0.0)

    row = None
    with open(lanes_path) as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 13 and parts[1] == piece and parts[2] == lane:
                row = parts
    print("[RECOMPUTE] " + piece + " Bl" + lane)
    print("  file row   : n=%s/%s median=%.3f cov=%.2f/%.2f jumps=%s maxstep=%.3f" %
          (row[3], row[4], float(row[5]), float(row[6]), float(row[7]), row[8], float(row[9])))
    print("  by hand    : n=%d/%d median=%.4f cov=%.3f/%.3f jumps=%d maxstep=%.4f" %
          (mine["n_ours"], mine["n_auth"], mine["median"], mine["cov_ours"], mine["cov_auth"],
           mine["jumps"], mine["max_step"]))
    ok = True
    ok &= mine["n_ours"] == int(row[3]) and mine["n_auth"] == int(row[4])
    ok &= abs(mine["median"] - float(row[5])) <= 0.002
    ok &= abs(mine["cov_ours"] - float(row[6])) <= 0.01
    ok &= abs(mine["cov_auth"] - float(row[7])) <= 0.01
    ok &= mine["jumps"] == int(row[8])
    print("  agreement  : " + ("PASS (n exact, median %.4f mm apart, coverage %.3f pp apart)" %
                              (abs(mine["median"] - float(row[5])),
                               max(abs(mine["cov_ours"] - float(row[6])), abs(mine["cov_auth"] - float(row[7]))))))
    if not ok:
        print("  agreement  : FAIL")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))