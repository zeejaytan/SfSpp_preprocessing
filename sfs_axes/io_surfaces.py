"""Surface loading — replaces read_surfaces.m + load_root_dir.m (G1/G2).

Config-driven loader (no hardcoded D:/ or /data/gpfs paths): the caller passes
a surfaces directory; files are Pot_A_Piece_%02d_Surface_{0,1}.xyz, ascii N x 6
(x y z nx ny nz, mm). Returned as (6, n) MATLAB-layout arrays.

Equal-count truncation (read_surfaces.m:34-37, first-min_points of each cloud)
is available as an explicit option (truncate=True) but is NOT the default. It
discards the tail of the denser wall arbitrarily; ticket 306 measured that on Pot A
Piece 08 those 185 points are the only ones carrying the released second
symmetry axis -- the untruncated cost has a minimum 5.23 deg from the released
line, the truncated cost has none -- so the search loses that basin's catchment.
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


def read_surfaces(surfaces_dir, pot_id="A", frag_id=1, truncate=False, verbose=False):
    """Port of read_surfaces.m (parameterised root dir).

    Returns (C0, C1) as (6, n) arrays. truncate=True reproduces the MATLAB rule
    (both walls cut to the shorter wall's point count) and is kept for parity;
    the default is False, because that cut deletes points the search needs
    (ticket 306: the tail of the denser wall can be the only carrier of a
    symmetry axis).
    """
    C0 = load_surface(surface_path(surfaces_dir, pot_id, frag_id, 0))
    C1 = load_surface(surface_path(surfaces_dir, pot_id, frag_id, 1))
    if truncate:
        m = min(C0.shape[1], C1.shape[1])
        C0, C1 = C0[:, 0:m], C1[:, 0:m]
        if verbose:
            print("Resampled surfaces to %d points each" % m)
    return C0, C1
