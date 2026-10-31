import numpy as np, os, sys
sys.path.insert(0, ".scratch/pota176_repro")
from p176_lib import load_obj, load_pcd3, wall_labels, pt_tri_dist, walk_m144
from scipy.spatial import cKDTree

H204 = ".scratch/pota204_repro"
H173 = ".scratch/pota173_repro"
H176 = ".scratch/pota176_repro"
H197 = ".scratch/pota197_repro"
ART = "artifacts/pota204"
os.makedirs(ART, exist_ok=True)
log = open(os.path.join(H204, "p204_dchain.txt"), "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")

G0SRC = {
  "01": ".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd",
  "02": os.path.join(H204, "ORIG_C02_Bl0.pcd"),
  "03": os.path.join(H204, "ORIG_C03_Bl0.pcd"),
  "04": os.path.join(H204, "ORIG_C04_Bl0.pcd"),
}
NREF = {"01": 211, "02": 221, "03": 191, "04": 131}

def load_bag(pc):
    if pc == "01":
        zb = np.load(os.path.join(H173, "p173_bag.npz"))
        return zb["BAG"]
    f0 = np.load(os.path.join(H176, "p176_C%s_F0_bag.npy" % pc))
    f1 = np.load(os.path.join(H176, "p176_C%s_F1_bag.npy" % pc))
    B = np.vstack([f0, f1])
    K = np.array([B[i].astype(np.float64).tobytes() for i in range(len(B))])
    _, uniq = np.unique(K, return_index=True)
    P = B[np.sort(uniq)]
    say("C%s pool F0=%d F1=%d pooled=%d (dupes %d)" % (pc, len(f0), len(f1), len(P), len(B)-len(P)))
    return P

def thin_v3(CLOUD, tag):
    C0 = CLOUD.mean(0)
    Uu, Ss, Vt = np.linalg.svd(CLOUD - C0, full_matrices=False)
    e1, e2 = Vt[0], Vt[1]
    P2 = np.c_[(CLOUD - C0).dot(e1), (CLOUD - C0).dot(e2)]
    cc = P2.mean(0)
    Q = P2 - cc
    ang = np.arctan2(Q[:,1], Q[:,0])
    NB = 360
    edges = np.linspace(-np.pi, np.pi, NB + 1)
    bid = np.clip(np.digitize(ang, edges) - 1, 0, NB - 1)
    means = []
    for b in range(NB):
        m = bid == b
        if m.sum(): means.append(CLOUD[m].mean(0))
    M = np.array(means)
    say("%s: fine bins %d non-empty of %d" % (tag, len(M), NB))
    ma = np.arctan2((M-C0).dot(e2)-cc[1], (M-C0).dot(e1)-cc[0])
    Mo = M[np.argsort(ma)]
    S = Mo.copy()
    for _ in range(8):
        S = S + 0.5 * ((np.roll(S,-1,0) + np.roll(S,1,0)) / 2.0 - S)
    seg = np.sqrt(((np.roll(S,-1,0)-S)**2).sum(-1))
    poly = float(seg.sum())
    N1 = min(240, int(round(poly / 1.8)))
    say("%s: smoothed polygon=%.1fmm -> N1=%d" % (tag, poly, N1))
    cum = np.r_[0, np.cumsum(np.sqrt(((S[1:]-S[:-1])**2).sum(-1)))]
    tot = cum[-1]
    tgt = np.linspace(0, tot, N1, endpoint=False)
    CL = np.zeros((N1, 3))
    j = 0
    for k, d in enumerate(tgt):
        while j < len(cum)-2 and cum[j+1] < d: j += 1
        f = (d - cum[j]) / max(cum[j+1]-cum[j], 1e-12)
        CL[k] = S[j] * (1-f) + S[j+1] * f
    return CL, C0, e1, e2

def seeds(Tc):
    s0 = 0
    Dm = np.sqrt(((Tc[:,None,:]-Tc[None,:,:])**2).sum(-1)).sum(0)
    sm = int(Dm.argmin())
    picked = [s0, sm]
    for _ in range(4):
        d = np.min([np.sqrt(((Tc-Tc[p])**2).sum(-1)) for p in picked], axis=0)
        d[picked] = -1
        picked.append(int(d.argmax()))
    return picked

def walk_face(CL, tag, G0, KG0, nref):
    results = []
    for si, s in enumerate(seeds(CL)):
        Tp = np.vstack([CL[s:], CL[:s]])
        seq, cseq, BAND, HALT, ret, fwd, bst = walk_m144(Tp)
        L = Tp[seq]
        steps = np.sqrt(((L[1:]-L[:-1])**2).sum(-1))
        arc = float(steps.sum()); closure = float(np.linalg.norm(L[-1]-L[0]))
        gaps5 = int((steps > 5).sum())
        j = KG0.query(L)[1]
        dj = np.diff(np.r_[j, j[0]]) % nref
        back = int((dj > nref // 2).sum())
        D = np.sqrt(((L[:,None,:]-G0[None,:,:])**2).sum(-1)).min(1)
        DO = np.sqrt(((G0[:,None,:]-L[None,:,:])**2).sum(-1)).min(1)
        med = float(np.median(D)); cov = int((DO < 2).sum())
        say("%s seed%d rot=%d: n=%d arc=%.1f closure=%.2f gaps5=%d back=%d ret=%d fwd=%d BAND=%.1f HALT=%s rimmed=%.4f cov=%d/%d" % (tag, si, s, len(L), arc, closure, gaps5, back, ret, fwd, BAND, HALT or "-", med, cov, nref))
        results.append(dict(si=si, s=s, L=L, arc=arc, closure=closure, gaps5=gaps5, back=back, ret=ret, fwd=fwd, HALT=HALT, med=med, cov=cov))
    ok = [r for r in results if r["closure"] <= 2.0 and r["gaps5"] == 0]
    fwdp = [r for r in ok if r["back"] == 0]
    pool = fwdp if fwdp else ok
    best = min(pool if pool else results, key=lambda r: (r["arc"]))
    say("%s PICK seed%d%s: n=%d arc=%.1f closure=%.2f gaps5=%d back=%d rimmed=%.4f cov=%d/%d" % (tag, best["si"], "" if ok else " -- NONE MET GATE", len(best["L"]), best["arc"], best["closure"], best["gaps5"], best["back"], best["med"], best["cov"], nref))
    return best

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
def render(CL, C0, e1, e2, CLOUD, best, tag, cn):
    P2 = np.c_[(CLOUD-C0).dot(e1), (CLOUD-C0).dot(e2)]
    CE = np.c_[(CL-C0).dot(e1), (CL-C0).dot(e2)]
    L = best["L"]
    fig, ax = plt.subplots(figsize=(9, 9))
    ax.scatter(P2[:,0], P2[:,1], c="lightgray", s=6, label="%s cloud (%d)" % (tag, len(CLOUD)))
    ax.scatter(CE[:,0], CE[:,1], c="green", s=18, label="centreline (%d)" % len(CL))
    ax.set_aspect("equal"); ax.legend(); ax.set_title("p204 C%s %s thin" % (cn[:3], tag))
    fig.savefig(os.path.join(ART, "p204_%s_%s_thin.png" % (cn, tag)), dpi=80); plt.close(fig)
    LW = np.c_[(L-C0).dot(e1), (L-C0).dot(e2)]
    fig, ax = plt.subplots(figsize=(9, 9))
    ax.scatter(P2[:,0], P2[:,1], c="lightgray", s=4)
    ax.scatter(LW[:,0], LW[:,1], c=np.arange(len(LW)), cmap="hsv", s=22)
    for k in [0, len(LW)//3, 2*len(LW)//3]:
        ax.text(LW[k,0], LW[k,1], str(k), fontsize=9)
    ax.set_aspect("equal"); ax.set_title("p204 %s %s seed%d n=%d arc=%.0f closure=%.2f" % (cn, tag, best["si"], len(L), best["arc"], best["closure"]))
    fig.savefig(os.path.join(ART, "p204_%s_%s_trace.png" % (cn, tag)), dpi=80); plt.close(fig)

for pc in ["01", "02", "03", "04"]:
    BAG = load_bag(pc)
    V, F = load_obj("temp_download/Mesh/Pot_C/Pot_C_Piece_%s_Mesh_DS.obj" % pc)
    T = np.loadtxt(os.path.join(H176, "inputs", "Pot_C_Piece_%d_T.txt" % int(pc))); Rr, t = T[:3,:3], T[:3,3]
    Vg = V @ Rr.T + t
    cosv = wall_labels(V, F)
    ddt, jn = pt_tri_dist(BAG, Vg, F)
    tl = cosv[jn]
    TRUE = BAG[(tl < -0.5) | (np.abs(tl) <= 0.5)]
    OUTER = BAG[tl > 0.5]
    fold = int((np.abs(tl) <= 0.5).sum()); inner = int((tl < -0.5).sum()); outer = int((tl > 0.5).sum())
    say("C%s: bag=%d inner=%d fold=%d outer=%d TRUE=%d OUTER=%d foldshare=%.1f%%" % (pc, len(BAG), inner, fold, outer, len(TRUE), len(OUTER), 100.0*fold/len(BAG)))
    if pc == "01":
        assert len(BAG) == 753 and len(TRUE) == 476 and len(OUTER) == 277, (len(BAG), len(TRUE), len(OUTER))
    G0 = load_pcd3(G0SRC[pc]) @ Rr.T + t
    assert len(G0) == NREF[pc], (pc, len(G0))
    KG0 = cKDTree(G0)
    for CLOUD, tag in [(TRUE, "TRUE"), (OUTER, "OUTER")]:
        cn = "C%s" % pc
        CL, C0, e1, e2 = thin_v3(CLOUD, "C%s-%s" % (pc, tag))
        np.save(os.path.join(H204, "p204_C%s_%s_centreline.npy" % (pc, tag.lower())), CL)
        best = walk_face(CL, "C%s-%s" % (pc, tag), G0, KG0, NREF[pc])
        np.save(os.path.join(H204, "p204_C%s_%s_walk.npy" % (pc, tag.lower())), best["L"])
        render(CL, C0, e1, e2, CLOUD, best, tag, cn)

ref = np.load(os.path.join(H197, "p197_true_walk.npy"))
mine = np.load(os.path.join(H204, "p204_C01_true_walk.npy"))
say("C01-TRUE-vs-197: ref=%s mine=%s maxdiff=%.6f" % (ref.shape, mine.shape, float(np.abs(ref-mine).max()) if ref.shape==mine.shape else -1))
say("P204 DCHAIN DONE")
log.close(); print("P204 DCHAIN DONE")
