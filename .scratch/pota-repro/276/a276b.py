
import sys, os
import numpy as np
AUTH_DIR = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines"

def readpcd(path):
    if not os.path.exists(path):
        return None
    with open(path, 'r', errors='ignore') as f:
        lines = f.read().splitlines()
    d = None
    for i, ln in enumerate(lines):
        if ln.startswith('DATA'):
            d = i + 1; break
    if d is None: return None
    pts = []
    for ln in lines[d:]:
        s = ln.split()
        if len(s) < 3: continue
        try: pts.append((float(s[0]), float(s[1]), float(s[2])))
        except ValueError: continue
    return np.array(pts, dtype=np.float64) if pts else None

def nn(A, B, chunk=8000):
    if A is None or B is None or len(A) == 0 or len(B) == 0:
        return None, None
    n = len(A); best = np.full(n, np.inf); bidx = np.full(n, -1, dtype=np.int64)
    for s in range(0, len(B), chunk):
        blk = B[s:s+chunk]
        d = np.sqrt(((A[:, None, :] - blk[None, :, :]) ** 2).sum(axis=2))
        j = d.argmin(axis=1); v = d[np.arange(n), j]; m = v < best
        best[m] = v[m]; bidx[m] = s + j[m]
    return best, bidx

def readdump(path):
    rows = []
    with open(path) as f:
        for ln in f:
            if ln.startswith('#'): continue
            s = ln.split()
            if len(s) < 5: continue
            rows.append((int(s[1]), float(s[2]), float(s[3]), float(s[4])))
    a = np.array(rows, dtype=np.float64)
    return a[:, 0].astype(int), a[:, 1:4]

def bucket(sel, lab):
    if sel is None or sel.sum() == 0:
        return (0, 0, 0, 0)
    l = lab[sel]
    return (int((l == 0).sum()), int((l == 1).sum()), int((l >= 2).sum()), int((l < 0).sum()))

def main(manifest, out):
    rows = []
    with open(manifest) as f:
        items = [ln.strip().split('\t')[:5] for ln in f if ln.strip() and not ln.startswith('#')]
    for tag, pot, nn_, tree, dump in items:
        if not os.path.exists(dump):
            print("MISSING", tag); continue
        lab, M = readdump(dump)
        cmask = lab >= 0
        Mclu = M[cmask]; labclu = lab[cmask]
        for lane in (0, 1):
            au = readpcd(os.path.join(AUTH_DIR, "%s_Piece_%s_Breakline_%d.pcd" % (pot, nn_, lane)))
            ou = readpcd(os.path.join(tree, "Dataset/Breaklines", pot, "%s_Piece_%s_Breakline_%d.pcd" % (pot, nn_, lane)))
            if au is None: continue
            da, ia = nn(au, M)
            lab_any = lab[ia]
            dcl, icl = nn(au, Mclu)
            lab_clu = labclu[icl]
            if ou is not None:
                do, _ = nn(au, ou); unc = do > 2.0
            else:
                unc = np.zeros(len(au), dtype=bool)
            near_clu = dcl <= 2.0
            a_all = bucket(np.ones(len(au), dtype=bool), lab_any)
            a_clu = bucket(near_clu, lab_clu)
            u_all = bucket(unc, lab_any)
            u_clu_n = bucket(unc & near_clu, lab_clu)
            u_far = int((unc & ~near_clu).sum())
            rows.append(dict(tag=tag, pot=pot, nn=nn_, lane=lane, nauth=len(au), unc=int(unc.sum()),
                all0=a_all[0], all1=a_all[1], alldrop=a_all[2], alluncl=a_all[3],
                clunear=int(near_clu.sum()), clu0=a_clu[0], clu1=a_clu[1], cludrop=a_clu[2],
                u0=u_all[0], u1=u_all[1], udrop=u_all[2], uuncl=u_all[3],
                uc0=u_clu_n[0], uc1=u_clu_n[1], ucdrop=u_clu_n[2], ufar=u_far,
                medmesh=float(np.median(da)) if len(da) else 0.0))
    cols = ["tag","pot","nn","lane","nauth","unc","all0","all1","alldrop","alluncl","clunear","clu0","clu1","cludrop","u0","u1","udrop","uuncl","uc0","uc1","ucdrop","ufar","medmesh"]
    with open(out, 'w') as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r[c]) for c in cols) + "\n")
    print("wrote", out)

main(sys.argv[1], sys.argv[2])
