"""POTA-69: label-free hybrid axis estimator (DEFAULT OFF -- do not enable on the corpus).

WHAT THIS IS
    The ticket-68 Juglet axis method, made selectable from one command: for each piece it
    computes several candidate axes from that piece's own two walls, scores each candidate by
    a fit residual that never looks at a ground truth, and writes the best one as a standard
    six-number axis file (position-first, the layout BreakLine::ReadAxis parses).

WHAT TICKET 69 MEASURED, AND WHY THIS DEFAULTS OFF
    Part A (ticket 69) ran this estimator family over all ten corpus pots against the released
    ground-truth axes, with NO per-piece selection by GT:

        released line 1   corpus median folded error  2.78 deg   (Pot A 1.68)
        nperp             47.60 deg
        nperpS1           42.71
        npar              66.47
        nparS1            67.77
        pottS1            27.00
        potsac_s0         51.96
        blind (this rule) 44.03

    and on the assembler's own 25 deg axis gate over 288 corpus edges:

        released line 1  217/286 pass      any released line  262/288
        pottS1 109/286   nperpS1 98/286   nperp 81/286   npar 59/286   potsac_s0 36/286

    The blind residual rule picked the same estimator the ground truth would have picked on
    only 32 of 141 pieces.  On the Juglet -- the nine pieces this method was built for -- the
    same rule is a large improvement over the shipped axes (ticket 68), but the Juglet is a
    different object from released Pot J and is not in the corpus tables above.

    So: this module reproduces the Juglet result and is the switch a reviewer can flip to
    re-check it.  It is NOT a corpus-wide replacement for the released axes, and the ticket-69
    Part C seating control is the reason -- on Pot A it drops the axis gate from 12/15 to a
    handful.  Never overwrite a released axis file in place; write to a fresh directory.

USAGE
    python -m sfs_axes.hybrid --surfaces DIR --out DIR --pot Juglet --pieces 1-9 [--seed 0]
    python -m sfs_axes.hybrid --surfaces DIR --out DIR --pot Pot_A --pieces 1-8 --dry-run

    --dry-run prints what it would write and writes nothing.
"""

import argparse
import os

import numpy as np

from .io_axes import axis_filename, write_axes
from .potsac import run_potsac
from .pottmann import compute_pottmann_axis

ESTIMATORS = ("nperp", "nperpS1", "npar", "nparS1", "pottS1", "potsac_s0")


def _unit(v):
    v = np.asarray(v, dtype=float).reshape(3)
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def _eig(C, largest):
    """Extremal eigenvector of the wall normals' scatter matrix (nperp / npar)."""
    n = C[3:6].T
    n = n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    w, v = np.linalg.eigh(n.T @ n)
    return v[:, -1] if largest else v[:, 0]


def pos_from_normals(C, d):
    """Point that the projected normal lines pass closest to (least squares)."""
    x, n = C[0:3].T, C[3:6].T
    P = np.eye(3) - np.outer(d, d)
    xp, nps = x @ P, n @ P
    nps = nps / np.maximum(np.linalg.norm(nps, axis=1, keepdims=True), 1e-9)
    A = np.zeros((3, 3))
    b = np.zeros(3)
    for xi, ni in zip(xp, nps):
        Q = P - np.outer(ni, ni)
        A += Q
        b += Q @ xi
    return np.linalg.lstsq(A, b, rcond=None)[0]


def residuals(C, p, d):
    """(median cylindricality deg, median meridional deg, median radius mm).

    Cylindricality is the angle between each wall normal and the axis; meridionality the angle
    between each normal and the meridian plane of the axis.  Both are zero for a perfect body
    of revolution.  They are the terms the label-free selection minimises -- they never see a
    ground truth.
    """
    x, n = C[0:3].T - p, C[3:6].T
    n = n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    cyl = np.degrees(np.arcsin(np.clip(np.abs(n @ d), 0, 1)))
    m = np.cross(d, x)
    m = m / np.maximum(np.linalg.norm(m, axis=1, keepdims=True), 1e-9)
    mer = np.degrees(np.arcsin(np.clip(np.abs(np.sum(n * m, axis=1)), 0, 1)))
    r = np.linalg.norm(x - np.outer(x @ d, d), axis=1)
    return float(np.median(cyl)), float(np.median(mer)), float(np.median(r))


def blind_score(res):
    """The label-free rule: degrees on both curvature terms, radius as a mild sanity term."""
    cyl, mer, r = res
    return cyl + mer + 0.1 * r


def candidates(C0, C1, seed=0):
    """Every candidate axis as {name: (position, direction)}; deterministic given the seed."""
    C = np.hstack([C0, C1])
    out = {}
    for name, cloud, largest in (("nperp", C, False), ("nperpS1", C1, False),
                                 ("npar", C, True), ("nparS1", C1, True)):
        d = _eig(cloud, largest)
        out[name] = (pos_from_normals(cloud, d), d)
    vt = compute_pottmann_axis(C1)
    out["pottS1"] = (np.asarray(vt[3:6], dtype=float).reshape(3),
                     _unit(np.asarray(vt[0:3], dtype=float)))
    m = min(C0.shape[1], C1.shape[1])
    vs = run_potsac(C0[:, :m], C1[:, :m], rng=np.random.default_rng(seed), step=None)
    if vs.shape[1] > 0:
        out["potsac_s0"] = (np.asarray(vs[3:6, 0], dtype=float).reshape(3),
                            _unit(np.asarray(vs[0:3, 0], dtype=float)))
    return out


def _surface_path(surfaces_dir, pot_id, frag_id, k):
    """Resolve one wall's file, tolerating the two naming conventions in use.

    The released corpus writes Pot_A_Piece_01_Surface_0.xyz (zero-padded, 'Pot_' prefix);
    the Juglet tree writes Juglet_Piece_1_Surface_0.xyz (unpadded, no 'Pot_' prefix).
    Both exist on Spartan and a caller should not have to know which it is pointing at.
    """
    for name in ("Pot_%s_Piece_%02d_Surface_%d.xyz" % (pot_id, frag_id, k),
                 "%s_Piece_%d_Surface_%d.xyz" % (pot_id, frag_id, k),
                 "%s_Piece_%02d_Surface_%d.xyz" % (pot_id, frag_id, k)):
        path = os.path.join(surfaces_dir, name)
        if os.path.isfile(path):
            return path
    raise FileNotFoundError(
        "no Surface_%d for pot=%s piece=%d under %s (tried Pot_%%s_Piece_%%02d and "
        "%%s_Piece_%%d layouts)" % (k, pot_id, frag_id, surfaces_dir))


def read_piece_surfaces(surfaces_dir, pot_id, frag_id):
    """Both walls, equal-count truncated (MATLAB parity, as read_surfaces does)."""
    C0 = np.loadtxt(_surface_path(surfaces_dir, pot_id, frag_id, 0), dtype=float)
    C1 = np.loadtxt(_surface_path(surfaces_dir, pot_id, frag_id, 1), dtype=float)
    C0 = np.atleast_2d(C0).T
    C1 = np.atleast_2d(C1).T
    m = min(C0.shape[1], C1.shape[1])
    return C0[:, 0:m], C1[:, 0:m]


def estimate_piece(surfaces_dir, pot_id, frag_id, seed=0):
    """Return (chosen name, vt (6,1), table of per-candidate residual scores)."""
    C0, C1 = read_piece_surfaces(surfaces_dir, pot_id, frag_id)
    cand = candidates(C0, C1, seed=seed)
    C = np.hstack([C0, C1])
    table = {}
    for name, (p, d) in cand.items():
        table[name] = (blind_score(residuals(C, p, d)), residuals(C, p, d), d)
    best = min(table, key=lambda k: table[k][0])
    p, d = cand[best]
    vt = np.concatenate([d, p])[:, None]
    return best, vt, table


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="POTA-69 hybrid axis estimator (default OFF; see the module docstring)")
    ap.add_argument("--surfaces", required=True, help="dir with <pot>_Piece_NN_Surface_{0,1}.xyz")
    ap.add_argument("--out", required=True, help="output dir (never a released Axes/ dir)")
    ap.add_argument("--pot", default="Juglet")
    ap.add_argument("--pieces", default="1-9")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    if "-" in a.pieces:
        lo, hi = a.pieces.split("-")
        pieces = list(range(int(lo), int(hi) + 1))
    else:
        pieces = [int(x) for x in a.pieces.split(",")]
    if not a.dry_run:
        os.makedirs(a.out, exist_ok=True)
    print("POTA-69 hybrid estimator: pot=%s pieces=%s seed=%d -> %s%s"
          % (a.pot, a.pieces, a.seed, a.out, " (DRY RUN)" if a.dry_run else ""))
    for frag in pieces:
        best, vt, table = estimate_piece(a.surfaces, a.pot, frag, seed=a.seed)
        path = os.path.join(a.out, axis_filename(a.pot, frag))
        if not a.dry_run:
            write_axes(path, vt)
        print("piece %02d: %-8s " % (frag, best)
              + " ".join("%s=%.1f" % (k, v[0]) for k, v in sorted(table.items()))
              + ("  [would write %s]" % path if a.dry_run else "  -> %s" % path))


if __name__ == "__main__":
    main()
