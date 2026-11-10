"""Bar-1 prototype v3: axis of the fragment from its own normal lines.
Each start direction gets an algebraic init for the axis position (min sum ((p-c).g)^2 with
g = n x d / |n x d| -- exact for the cylinder case and linear in c), then a plain-L2
trimmed refinement.  Interior = face with the smaller mean radius about that axis."""
import json, os, sys
import numpy as np
from scipy.spatial import cKDTree
from scipy.optimize import least_squares

B = 'C:/PR/worktrees/sfs/328-juglet-wall-side-cure'
GEOM = os.path.join(B, 'artifacts/pota328/in/geom'); GT = os.path.join(B, 'artifacts/pota328/in/gt')
OUT = os.path.join(B, 'artifacts/pota328/probe'); os.makedirs(OUT, exist_ok=True)

def load_ply6(p):
    L = open(p).read().splitlines(); i = [n for n, l in enumerate(L) if l.strip() == 'end_header'][0]
    d = [l.split() for l in L[i+1:] if l.strip() and not l.startswith('camera')]
    return np.array([[float(x) for x in r[:6]] for r in d])

def load_ax(p):
    v = [float(x) for x in open(p).read().split()]; return np.array(v[-6:-3]), np.array(v[-3:])

def unit(a): return a / np.maximum(np.linalg.norm(a, axis=1, keepdims=True), 1e-12)

def res_of(P, N, c, d):
    A = P - c; A = A - np.outer(A @ d, d)
    nt = N - np.outer(N @ d, d); nn = np.sum(nt*nt, axis=1)
    r = np.linalg.norm(A, axis=1); s = np.zeros(len(P)); ok = nn > 1e-9
    s[ok] = -np.sum(A[ok]*nt[ok], axis=1)/nn[ok]
    return np.linalg.norm(A + np.outer(s, np.ones(3))*nt, axis=1)

def init_c(P, N, d, c_anchor):
    g = np.cross(N, d)
    gl = np.linalg.norm(g, axis=1)
    m = gl > 0.25
    if m.sum() < 20: return None
    gg = g[m]/gl[m, None]
    M = gg.T @ gg + 1e-9*np.eye(3)
    rhs = np.sum(gg * (P[m] @ gg.T).T, axis=0) if False else np.einsum('ij,i->j', gg, np.sum(P[m]*gg, axis=1))
    c, *_ = np.linalg.lstsq(M, rhs, rcond=None)
    # keep the position along d at the anchor's
    return c + ((c_anchor - c) @ d) * d

def refine(P, N, d0, c0, loss='linear', max_nfev=300):
    a = np.array([1.0, 0, 0]) if abs(d0[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(d0, a); u /= np.linalg.norm(u); v = np.cross(d0, u)
    def unpack(p):
        dd = d0 + p[0]*u + p[1]*v; dd = dd/np.linalg.norm(dd)
        return c0 + p[2]*u + p[3]*v + p[4]*d0, dd
    def fun(p):
        cc, dd = unpack(p); return res_of(P, N, cc, dd)
    r = least_squares(fun, np.zeros(5), method='trf', loss=loss, max_nfev=max_nfev,
                      xtol=1e-12, ftol=1e-12)
    cc, dd = unpack(r.x)
    return cc, dd

def start_dirs(seed=3, n=24):
    rng = np.random.default_rng(seed); out = [np.array([0, 0, 1.0]), np.array([1.0, 0, 0]), np.array([0, 1.0, 0])]
    for _ in range(n):
        v = rng.normal(size=3); out.append(v/np.linalg.norm(v))
    for th in np.linspace(0, np.pi, 5):
        for ph in np.linspace(0, 2*np.pi, 8, endpoint=False):
            out.append(np.array([np.sin(th)*np.cos(ph), np.sin(th)*np.sin(ph), np.cos(th)]))
    return out

def fit_axis(P, N, verbose=False, seed=3, subsample=900):
    rng = np.random.default_rng(seed)
    if len(P) > subsample:
        idx = rng.choice(len(P), subsample, replace=False); P, N = P[idx], N[idx]
    N = unit(N); m = P.mean(axis=0); Pc = P - m
    cands = []
    for d0 in start_dirs(seed=seed):
        c0 = init_c(Pc, N, d0, np.zeros(3))
        if c0 is None: continue
        c, d = refine(Pc, N, d0, c0)
        cost = float(np.median(res_of(Pc, N, c, d)))
        cands.append((cost, c, d))
    cands.sort(key=lambda t: t[0])
    best = None
    for cost, c, d in cands[:5]:
        Pk, Nk = Pc, N
        for it in range(3):
            c, d = refine(Pk, Nk, d, c)
            r = res_of(Pk, Nk, c, d)
            thr = max(2.0*float(np.median(r)), 1.2)
            keep = r <= thr
            if keep.sum() < 40: break
            Pk, Nk = Pk[keep], Nk[keep]
        cost = float(np.median(res_of(Pc, N, c, d)))
        if best is None or cost < best[0]: best = (cost, c, d)
    cost, c, d = best
    return c + m, d/np.linalg.norm(d), cost

def radii(P0, P1, c, d):
    out = []
    for P in (P0, P1):
        w = P - c
        out.append(float(np.median(np.linalg.norm(w - np.outer(w @ d, d), axis=1))))
    return out

def line_dist(c1, d1, c2, d2):
    nn = np.cross(d1, d2)
    if np.linalg.norm(nn) > 1e-8: return abs(float((c2-c1) @ nn)/np.linalg.norm(nn))
    w = c2 - c1; return float(np.linalg.norm(w - (w @ d1)*d1))

rows = []
for k in range(1, 10):
    A = {f: load_ply6(os.path.join(GEOM, 'Juglet_Piece_%d.S%d' % (k, f))) for f in (0, 1)}
    P = np.vstack([A[0][:, :3], A[1][:, :3]]); N = unit(np.vstack([A[0][:, 3:6], A[1][:, 3:6]]))
    c, d, cost = fit_axis(P, N)
    g0, gd = load_ax(os.path.join(GT, 'Juglet_Piece_%d_Axis.xyz' % k)); gd = gd/np.linalg.norm(gd)
    ang = float(np.degrees(np.arccos(min(1.0, abs(float(d @ gd))))))
    dist = line_dist(c, d, g0, gd)
    r = radii(A[0][:, :3], A[1][:, :3], c, d)
    rg = radii(A[0][:, :3], A[1][:, :3], g0, gd)
    thick = float(np.median(cKDTree(A[1][:, :3]).query(A[0][:, :3], k=1)[0]))
    dr = r[1]-r[0]
    true_int = 0 if rg[0] < rg[1] else 1
    pick = 0 if dr > 0 else 1
    # bootstrap spread of dr and of the pick
    rng = np.random.default_rng(21); drb = []; pk = []
    for b in range(8):
        idx = rng.choice(len(P), len(P)//2, replace=False)
        cb, db, _ = fit_axis(P[idx], N[idx], seed=40+b)
        rb = radii(A[0][:, :3], A[1][:, :3], cb, db); drb.append(rb[1]-rb[0]); pk.append(0 if rb[1] > rb[0] else 1)
    row = dict(piece=k, ang=round(ang, 2), distGT=round(dist, 3), resid=round(cost, 3),
               r0=round(r[0], 3), r1=round(r[1], 3), dr=round(dr, 3),
               dr_sd=round(float(np.std(drb)), 3), votes_all_agree=bool(len(set(pk)) == 1),
               thick=round(thick, 3), true_int=true_int, pick=pick, ok=pick == true_int,
               decisive=bool(abs(dr) > 0.5*thick))
    rows.append(row)
    print('piece %d | axis vs GT %6.2f deg %6.3f mm | resid %5.3f | r %7.3f %7.3f dr %+6.3f (sd %.3f agree %s) | t %5.3f | pick %d true %d %-4s decisive %s' % (
        k, ang, dist, cost, r[0], r[1], dr, row['dr_sd'], row['votes_all_agree'], thick, pick, true_int,
        'OK' if pick == true_int else 'FAIL', row['decisive']))
json.dump(rows, open(os.path.join(OUT, 'axis_geom3.json'), 'w'), indent=1)
