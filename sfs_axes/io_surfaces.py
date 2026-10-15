"""Surface loading — replaces read_surfaces.m + load_root_dir.m (G1/G2).

Config-driven loader (no hardcoded D:/ or /data/gpfs paths): the caller passes
a surfaces directory; files are Pot_A_Piece_%02d_Surface_{0,1}.xyz, ascii N x 6
(x y z nx ny nz, mm). Returned as (6, n) MATLAB-layout arrays.

Equal-count truncation (read_surfaces.m:34-37, first-min_points of each cloud)
is kept as an explicit option defaulting to True for MATLAB parity, flagged
for removal: it discards tail points of the denser wall arbitrarily.
"""

import os

import numpy as np


def surface_path(surfaces_dir, pot_id, frag_id, surface):
    """File path for one wall (surface 0 or 1)."""
    return os.path.join(
        surfaces_dir, "Pot_%s_Piece_%02d_Surface_%d.xyz" % (pot_id, frag_id, surface))


def load_surface(path):
    """Load one N x 6 surface file -> (6, n) array."""
    arr = np.loadtxt(path, dtype=float)
    if arr.ndim == 1:
        arr = arr[None, :]
    return arr.T


def read_surfaces(surfaces_dir, pot_id="A", frag_id=1, truncate=True, verbose=False):
    """Port of read_surfaces.m (parameterised root dir).

    Returns (C0, C1) as (6, n) arrays. With truncate=True (default, MATLAB
    parity) both walls are cut to the shorter wall's point count.
    """
    C0 = load_surface(surface_path(surfaces_dir, pot_id, frag_id, 0))
    C1 = load_surface(surface_path(surfaces_dir, pot_id, frag_id, 1))
    if truncate:
        m = min(C0.shape[1], C1.shape[1])
        C0, C1 = C0[:, 0:m], C1[:, 0:m]
        if verbose:
            print("Resampled surfaces to %d points each" % m)
    return C0, C1
