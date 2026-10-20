"""POTA-221 face+lane diagnostic (220 pattern): pre-dots rim-rider test + lane deviation runs."""
import numpy as np, os, sys
def load_pcd(p):
    with open(p, "rb") as f: data = f.read()
    head, _, body = data.partition(b"DATA ascii\n")
    if not body: head, _, body = data.partition(b"DATA ascii\r\n")
    nf = 3
    for line in head.decode("ascii", errors="replace").splitlines():
        if line.startswith("FIELDS"): nf = len(line.split()) - 1
    return np.fromstring(body.decode("ascii", errors="replace"), sep=" ").reshape(-1, nf)[:, :3]
def load_xyz(p):
    rows = []
    with open(p) as f:
        for line in f:
            s = line.split()
            if len(s) < 3: continue
            try: rows.append([float(s[0]), float(s[1]), float(s[2])])
            except ValueError: continue
    return np.asarray(rows)
def dist_to(A, B):
    return np.sqrt((((A[:, None, :] - B[None, :, :]) ** 2).sum(-1)).min(1))
def main():
    piece, ddir, adir, badlane = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    o0 = load_pcd(os.path.join(adir, "Pot_D_Piece_%s_Breakline_0.pcd" % piece))
    o1 = load_pcd(os.path.join(adir, "Pot_D_Piece_%s_Breakline_1.pcd" % piece))
    rim = np.vstack([o0, o1])
    pre = load_pcd(os.path.join(ddir, "boundary.pcd"))
    d_rim = dist_to(pre, rim)
    print("predots n=%d rim_riders(<2mm)=%d (%.1f%%)" % (len(pre), int((d_rim < 2).sum()), 100*(d_rim < 2).mean()))
    for s in ["0", "1"]:
        S = load_xyz(os.path.join(ddir, "Pot_D_Piece_%s_Surface_%s.xyz" % (piece, s)))
        n_face = int(((dist_to(pre, S) < 2.0) & (d_rim >= 2.0)).sum())
        print("pre vs S%s(file-rows=%d): face_interior=%d" % (s, len(S), n_face))
    L = load_pcd(os.path.join(ddir, "..", "..", "lanes", "Pot_D_Piece_%s_Breakline_%s.pcd" % (piece, badlane)))
    d = dist_to(L, rim)
    bad = np.nonzero(d >= 2.0)[0]
    print("badlane Bl%s n=%d med=%.2f cov=%.1f max=%.1f nbad=%d" % (badlane, len(L), float(np.median(d)), 100*(d < 2).mean(), float(d.max()), len(bad)))
    if len(bad):
        runs, start, prev = [], bad[0], bad[0]
        for b in bad[1:]:
            if b == prev + 1: prev = b
            else: runs.append((start, prev)); start, prev = b, b
        runs.append((start, prev))
        print("deviation runs (idx-start-end-maxdev):", [(a, b, round(float(d[a:b+1].max()), 1)) for a, b in runs])
if __name__ == "__main__":
    main()
