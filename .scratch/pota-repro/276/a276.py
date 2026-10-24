
import sys, os, glob, math
import numpy as np

AUTH_DIR = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines"

def readpcd(path):
    if not os.path.exists(path):
        return None
    with open(path, 'r', errors='ignore') as f:
        lines = f.read().splitlines()
    data = None
    for i, ln in enumerate(lines):
        if ln.startswith('DATA'):
            data = i + 1
            break
    if data is None:
        return None
    pts = []
    for ln in lines[data:]:
        s = ln.split()
        if len(s) < 3:
            continue
        try:
            pts.append((float(s[0]), float(s[1]), float(s[2])))
        except ValueError:
            continue
    return np.array(pts, dtype=np.float64) if pts else None

def nn(A, B, chunk=8000):
    """for each row of A, nearest distance and index in B"""
    if A is None or B is None or len(A) == 0 or len(B) == 0:
        return None, None
    n = len(A)
    best = np.full(n, np.inf)
    bidx = np.full(n, -1, dtype=np.int64)
    for s in range(0, len(B), chunk):
        blk = B[s:s+chunk]
        d = np.sqrt(((A[:, None, :] - blk[None, :, :]) ** 2).sum(axis=2))
        j = d.argmin(axis=1)
        v = d[np.arange(n), j]
        m = v < best
        best[m] = v[m]
        bidx[m] = s + j[m]
    return best, bidx

def readdump(path):
    hdr = {}
    rows = []
    with open(path) as f:
        for ln in f:
            if ln.startswith('#'):
                s = ln[1:].split()
                for i in range(0, len(s) - 1, 2):
                    try:
                        hdr[s[i]] = float(s[i+1])
                    except ValueError:
                        pass
                continue
            s = ln.split()
            if len(s) < 5:
                continue
            rows.append((int(s[0]), int(s[1]), float(s[2]), float(s[3]), float(s[4])))
    a = np.array(rows, dtype=np.float64)
    return hdr, a

def lanescore(ours, author):
    if ours is None or author is None or len(ours) == 0 or len(author) == 0:
        return dict(n=0, med=float('nan'), cov=0.0, cova=0.0, jumps=0, mx=0.0)
    dd, _ = nn(ours, author)
    dd = np.sort(dd)
    med = float(dd[len(dd)//2])
    cov = 100.0 * float((dd < 2.0).sum()) / len(dd)
    da, _ = nn(author, ours)
    cova = 100.0 * float((da < 2.0).sum()) / len(da)
    steps = np.sqrt(((ours[1:] - ours[:-1]) ** 2).sum(axis=1))
    jumps = int((steps > 10.0).sum())
    mx = float(steps.max()) if len(steps) else 0.0
    return dict(n=len(ours), med=med, cov=cov, cova=cova, jumps=jumps, mx=mx)

def main(manifest, outtsv):
    pieces = []
    with open(manifest) as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            tag, pot, nn_, tree, dump = ln.split('\t')[:5]
            pieces.append((tag, pot, nn_, tree, dump))
    cl_rows = []
    ln_rows = []
    for tag, pot, nn_, tree, dump in pieces:
        if not os.path.exists(dump):
            print("MISSING dump", tag, dump)
            continue
        hdr, a = readdump(dump)
        lab = a[:, 1].astype(int)
        M = a[:, 2:5]
        sizes = {int(c): int((lab == c).sum()) for c in np.unique(lab)}
        nmesh = len(a)
        ndropped = sum(v for k, v in sizes.items() if k >= 2)
        nuncl = sizes.get(-1, 0)
        s0 = sizes.get(0, 0); s1 = sizes.get(1, 0)
        dropped_pts = M[lab >= 2] if (lab >= 2).any() else None
        surf_pts = M[(lab >= 0) & (lab <= 1)] if ((lab >= 0) & (lab <= 1)).any() else None
        auth_all = {}
        ours_all = {}
        for lane in (0, 1):
            authp = os.path.join(AUTH_DIR, "%s_Piece_%s_Breakline_%d.pcd" % (pot, nn_, lane))
            oursp = os.path.join(tree, "Dataset/Breaklines", pot, "%s_Piece_%s_Breakline_%d.pcd" % (pot, nn_, lane))
            auth_all[lane] = readpcd(authp)
            ours_all[lane] = readpcd(oursp)
        for c in sorted(sizes):
            idx = np.where(lab == c)[0]
            cp = M[idx]
            for l2 in (0, 1):
                au = auth_all[l2]
                if au is None:
                    continue
                d, _ = nn(au, cp)
                cnt = int((d <= 2.0).sum()) if d is not None else 0
                cl_rows.append((tag, pot, nn_, l2, c, sizes[c], cnt))
        for lane in (0, 1):
            au = auth_all[lane]
            ou = ours_all[lane]
            sc = lanescore(ou, au)
            dm, di = None, None
            if au is not None:
                dm, di = nn(au, M)
            row = dict(tag=tag, pot=pot, nn=nn_, lane=lane, n=sc['n'], med=sc['med'], cov=sc['cov'],
                       cova=sc['cova'], jumps=sc['jumps'], mx=sc['mx'], nmesh=nmesh,
                       nclusters=len([k for k in sizes if k >= 0]), s0=s0, s1=s1,
                       dropped=ndropped, unclustered=nuncl,
                       dropped_pct=100.0 * ndropped / nmesh if nmesh else 0.0)
            if au is None or dm is None:
                ln_rows.append((tag, lane, row, None))
                continue
            clar = lab[di]
            row['nauth'] = len(au)
            row['auth_dropped_share'] = 100.0 * float((clar >= 2).sum()) / len(au)
            row['auth_surf_share'] = 100.0 * float(((clar >= 0) & (clar <= 1)).sum()) / len(au)
            row['auth_uncl_share'] = 100.0 * float((clar < 0).sum()) / len(au)
            row['auth_nomsh_2mm'] = int((dm > 2.0).sum())
            unc = None
            if ou is not None:
                do, _ = nn(au, ou)
                unc = do > 2.0
                row['unc_n'] = int(unc.sum())
                if unc.sum() > 0:
                    ul = clar[unc]
                    row['unc_dropped'] = int((ul >= 2).sum())
                    row['unc_surf'] = int(((ul >= 0) & (ul <= 1)).sum())
                    row['unc_uncl'] = int((ul < 0).sum())
                    row['unc_nomesh'] = int((dm[unc] > 2.0).sum())
                    row['unc_medmesh'] = float(np.median(dm[unc]))
                else:
                    row['unc_dropped'] = 0; row['unc_surf'] = 0; row['unc_uncl'] = 0
                    row['unc_nomesh'] = 0; row['unc_medmesh'] = 0.0
            ln_rows.append((tag, lane, row, unc))
    with open(outtsv + '.lanes.tsv', 'w') as f:
        f.write("tag\tlane\tn\tmed\tcov_ours\tcov_auth\tjumps\tmx\tnmesh\tnclusters\ts0\ts1\tdropped\tuncl\tdropped_pct\tnauth\tauth_dropped_pct\tauth_surf_pct\tauth_uncl_pct\tauth_nomesh_2mm\tunc_n\tunc_dropped\tunc_surf\tunc_uncl\tunc_nomesh\tunc_medmesh\n")
        for tag, lane, r, _ in ln_rows:
            f.write("\t".join(str(r.get(k, '')) for k in ["tag", "lane", "n", "med", "cov", "cova", "jumps", "mx",
                    "nmesh", "nclusters", "s0", "s1", "dropped", "unclustered", "dropped_pct", "nauth",
                    "auth_dropped_share", "auth_surf_share", "auth_uncl_share", "auth_nomsh_2mm", "unc_n",
                    "unc_dropped", "unc_surf", "unc_uncl", "unc_nomesh", "unc_medmesh"]) + "\n")
    with open(outtsv + '.clusters.tsv', 'w') as f:
        f.write("tag\tpot\tnn\tlane\tcluster\tsize\tauth_within2\n")
        for r in cl_rows:
            f.write("\t".join(str(x) for x in r) + "\n")
    print("wrote", outtsv + '.lanes.tsv', outtsv + '.clusters.tsv')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])