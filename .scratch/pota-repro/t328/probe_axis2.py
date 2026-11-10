"""Bar-1 prototype v2: robust per-piece axis from the normal lines (trimmed, multi-start),
then interior = the face with the smaller median radius.  Reports a bootstrap uncertainty so
"decisive" is a measurement, not a hope."""
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
    s[ok] = -np.sum(A[ok]*nt[ok], axis=1) / nn[ok]
    return np.linalg.norm(A + np.outer(s, np.ones(3))*nt, axis=1)

def refine(P, N, d0, c0, loss='soft_l1', f_scale=1.0, max_nfev=200):
    a = np.array([1.0, 0, 0]) if abs(d0[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(d0, a); u /= np.linalg.norm(u); v = np.cross(d0, u)
    def unpack(p):
        dd = d0 + p[0]*u + p[1]*v; dd = dd / np.linalg.norm(dd)
        return c0 + p[2]*u + p[3]*v + p[4]*d0, dd
    def fun(p):
        cc, dd = unpack(p); return res_of(P, N, cc, dd)
    r = least_squares(fun, np.zeros(5), method='trf', loss=loss, f_scale=f_scale,
                      max_nfev=max_nfev, xtol=1e-10, ftol=1e-10)
    cc, dd = unpack(r.x)
    return cc, dd, float(np.median(res_of(P, N, cc, dd)))

def start_dirs(n=40, seed=3):
    rng = np.random.default_rng(seed); out = []
    for _ in range(n):
        v = rng.normal(size=3); out.append(v/np.linalg.norm(v))
    for th in np.linspace(0, np.pi, 5):
        for ph in np.linspace(0, 2*np.pi, 8, endpoint=False):
            out.append(np.array([np.sin(th)*np.cos(ph), np.sin(th)*np.sin(ph), np.cos(th)]))
    return out

def fit_axis(P, N, keep=(-1,), verbose=False, seed=3):
    m = P.mean(axis=0); Pc = P - m; Nc = unit(N)
    rng = np.random.default_rng(seed)
    sub = rng.choice(len(Pc), min(400, len(Pc)), replace=False)
    cands = []
    for d0 in start_dirs(seed=seed):
        c, d, cost = refine(Pc[sub], Nc[sub], d0, np.zeros(3), max_nfev=80)
        cands.append((cost, c, d))
    cands.sort(key=lambda t: t[0])
    best = None
    for cost, c, d in cands[:6]:
        Pk, Nk = Pc[sub], Nc[sub]
        for it in range(3):
            c, d, _ = refine(Pk, Nk, d, c, loss='linear', max_nfev=120)
            r = res_of(Pk, Nk, c, d)
            thr = max(2.5*float(np.median(r)), 1.5)
            keepm = r <= thr
            if keepm.sum() < 30: break
            Pk, Nk = Pk[keepm], Nk[keepm]
        cost = float(np.median(res_of(Pc, Nc, c, d)))
        if best is None or cost < best[0]:
            best = (cost, c, d, float(keepm.sum())/len(sub))
    cost, c, d, frac = best
    return c + m, d, cost, frac

def boot(P, N, nb=8, seed=11):
    rng = np.random.default_rng(seed); out = []
    for b in range(nb):
        idx = rng.choice(len(P), len(P)//2, replace=False)
        c, d, cost, frac = fit_axis(P[idx], N[idx], seed=seed+b)
        out.append((c, d, cost, frac))
    return out

def line_dist(c1, d1, c2, d2):
    nn = np.cross(d1, d2)
    if np.linalg.norm(nn) > 1e-8:
        return abs(float((c2 - c1) @ nn) / np.linalg.norm(nn))
    w = c2 - c1
    return float(np.linalg.norm(w - (w @ d1) * d1))

rows = []
for k in range(1, 10):
    A = {f: load_ply6(os.path.join(GEOM, 'Juglet_Piece_%d.S%d' % (k, f))) for f in (0, 1)}
    P = np.vstack([A[0][:, :3], A[1][:, :3]]); N = unit(np.vstack([A[0][:, 3:6], A[1][:, 3:6]]))
    c, d, cost, frac = fit_axis(P, N, seed=3)
    g0, gd = load_ax(os.path.join(GT, 'Juglet_Piece_%d_Axis.xyz' % k)); gd = gd/np.linalg.norm(gd)
    ang = float(np.degrees(np.arccos(min(1.0, abs(float(d @ gd))))))
    dist = line_dist(c, d, g0, gd)
    r = {f: float(np.median(np.linalg.norm((A[f][:, :3] - c) - np.outer((A[f][:, :3] - c) @ d, d), axis=1))) for f in (0, 1)}
    thick = float(np.median(cKDTree(A[1][:, :3]).query(A[0][:, :3], k=1)[0]))
    dr = r[1] - r[0]
    # bootstrap: how well is each face's radius determined?
    bs = boot(P, N, nb=6, seed=11)
    drs = []
    for (cb, db, _, _) in bs:
        rb = [float(np.median(np.linalg.norm((A[f][:, :3] - cb) - np.outer((A[f][:, :3] - cb) @ db, db), axis=1))) for f in (0, 1)]
        drs.append(rb[1] - rb[0])
    drs = np.array(drs)
    r[0] = round(r[0], 3); r[1] = round(r[1], 3)
    row = dict(piece=k, ang=round(ang, 2), distGT=round(dist, 3), resid=round(cost, 3), keep=round(frac, 3),
               r0=r[0], r1=r[1], dr=round(dr, 3), dr_boot_sd=round(float(np.std(drs)), 3),
               thick=round(thick, 3), pick=(0 if dr > 0 else 1),
               decisive=bool(abs(dr) > 0.5*thick), boot_agrees=bool(np.all(np.sign(drs) == np.sign(dr))))
    rows.append(row)
    print('piece %d | axis vs GT %5.2f deg %5.3f mm | resid %5.3f keep %4.2f | r %7.3f %7.3f dr %+6.3f (boot sd %.3f) | t %5.3f | pick %d decisive %-5s boot %s' % (
        k, ang, dist, cost, frac, r[0], r[1], dr, float(np.std(drs)), thick, row['pick'], row['decisive'], row['boot_agrees']))
json.dump(rows, open(os.path.join(OUT, 'axis_geom2.json'), 'w'), indent=1)
