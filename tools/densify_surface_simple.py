#!/usr/bin/env python3
"""
Simple surface densifier without external deps.

Usage:
  python tools/densify_surface_simple.py <in.xyz> <out.xyz> <target_count>

Reads an XYZ+normals text file with 6 columns per line and writes a
densified version with approximately target_count rows by sampling
additional points in the local tangent plane around existing points.

Notes:
  - Normals for new points are copied from their seed points.
  - Tangent jitter scale is heuristically chosen from bbox diag and N.
  - If target_count <= current_count, a random downsample is performed.
"""
import math
import os
import sys
from typing import Tuple
import numpy as np


def load_xyz_normals(path: str):
    try:
        arr = np.loadtxt(path, dtype=np.float64)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        if arr.shape[1] < 6:
            # Pad normals if needed
            pad = np.zeros((arr.shape[0], 6), dtype=np.float64)
            pad[:, :arr.shape[1]] = arr
            arr = pad
        return arr[:, :6]
    except Exception:
        # Fallback slow path
        rows = []
        with open(path, 'r') as f:
            for line in f:
                parts = line.split()
                if len(parts) < 3:
                    continue
                vals = [float(v) for v in parts[:6]]
                while len(vals) < 6:
                    vals.append(0.0)
                rows.append(vals)
        return np.array(rows, dtype=np.float64)


def save_xyz_normals(path: str, pts) -> None:
    fmt = '%.6f %.6f %.6f %.6f %.6f %.6f'
    np.savetxt(path, pts, fmt=fmt)


def bbox_diag(pts: np.ndarray) -> float:
    if pts.size == 0:
        return 0.0
    mins = pts[:, :3].min(axis=0)
    maxs = pts[:, :3].max(axis=0)
    d = maxs - mins
    return float(np.linalg.norm(d))


def orthonormal_bases(normals: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    # normals: (m, 3)
    n = normals
    # pick helper a per-row
    use_x = np.abs(n[:, 0]) < 0.9
    a = np.zeros_like(n)
    a[use_x] = np.array([1.0, 0.0, 0.0])
    a[~use_x] = np.array([0.0, 1.0, 0.0])
    # u = normalize(n x a)
    u = np.cross(n, a)
    u_norm = np.linalg.norm(u, axis=1, keepdims=True)
    u_norm[u_norm == 0] = 1.0
    u = u / u_norm
    # v = n x u
    v = np.cross(n, u)
    v_norm = np.linalg.norm(v, axis=1, keepdims=True)
    v_norm[v_norm == 0] = 1.0
    v = v / v_norm
    return u, v


def densify(pts: np.ndarray, target_count: int) -> np.ndarray:
    n = pts.shape[0]
    if n == 0:
        return pts
    if target_count <= n:
        idx = np.random.permutation(n)[:target_count]
        return pts[idx]

    diag = bbox_diag(pts)
    spacing = diag / max(1.0, math.sqrt(n))
    sigma = 0.35 * spacing

    extra = target_count - n
    idx = np.random.randint(0, n, size=extra)
    seeds = pts[idx]
    normals = seeds[:, 3:6]
    # Normalize normals (avoid zero-division)
    n_norm = np.linalg.norm(normals, axis=1, keepdims=True)
    n_norm[n_norm == 0] = 1.0
    normals = normals / n_norm
    u, v = orthonormal_bases(normals)
    du = np.random.normal(loc=0.0, scale=sigma, size=(extra, 1))
    dv = np.random.normal(loc=0.0, scale=sigma, size=(extra, 1))
    offsets = du * u + dv * v
    new_xyz = seeds[:, :3] + offsets
    new = np.concatenate([new_xyz, seeds[:, 3:6]], axis=1)
    out = np.vstack([pts, new])
    return out


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return 2
    inp = sys.argv[1]
    outp = sys.argv[2]
    try:
        target = int(sys.argv[3])
    except Exception:
        print("target_count must be an integer", file=sys.stderr)
        return 2

    pts = load_xyz_normals(inp)
    if pts.size == 0:
        print(f"Failed to load or empty: {inp}", file=sys.stderr)
        return 3
    densified = densify(pts, target)
    os.makedirs(os.path.dirname(outp) or '.', exist_ok=True)
    save_xyz_normals(outp, densified)
    print(f"Input={pts.shape[0]} Output={densified.shape[0]} Target={target}")


if __name__ == '__main__':
    sys.exit(main())
