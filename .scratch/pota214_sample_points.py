"""POTA-214: sample ORIG Pot_D Mesh_DS OBJs into legacy-format Point PCDs.
Density rule: match the legacy Pot_A scan density (Pot_A P01: 843433 pts /
23273.6 mm2 = 36.24 pts/mm2). Uniform-by-area triangle sampling with
barycentric-interpolated vertex normals. Output fields (legacy 6-field):
x y z normal_x normal_y normal_z, ASCII. Mesh-observable only, no ORIG
constants. Usage: python3 pota214_sample_points.py <meshdir> <outdir> <DENSITY> <pieces...>
"""
import sys
import numpy as np

def load_obj(path):
    V, N, F = [], [], []
    with open(path) as f:
        for line in f:
            if line.startswith('v '):
                p = line.split()
                V.append((float(p[1]), float(p[2]), float(p[3])))
            elif line.startswith('vn '):
                p = line.split()
                N.append((float(p[1]), float(p[2]), float(p[3])))
            elif line.startswith('f '):
                idx = []
                nidx = []
                for x in line.split()[1:]:
                    s = x.split('/')
                    idx.append(int(s[0]) - 1)
                    nidx.append(int(s[2]) - 1 if len(s) > 2 and s[2] else -1)
                for k in range(1, len(idx) - 1):
                    F.append((idx[0], idx[k], idx[k + 1]))
    return np.asarray(V), np.asarray(N), np.asarray(F)

def main():
    meshdir, outdir, density = sys.argv[1], sys.argv[2], float(sys.argv[3])
    pieces = sys.argv[4:]
    rng = np.random.default_rng(214)
    for pc in pieces:
        stem = pc.replace('_Mesh_DS.obj', '')
        V, N, F = load_obj('%s/%s' % (meshdir, pc))
        T = V[F]  # (M,3,3)
        e1 = T[:, 1] - T[:, 0]
        e2 = T[:, 2] - T[:, 0]
        cr = np.cross(e1, e2)
        area = 0.5 * np.linalg.norm(cr, axis=1)
        total = area.sum()
        n = int(round(total * density))
        prob = area / total
        cnt = rng.multinomial(n, prob)
        take = cnt > 0
        km = int(take.sum())
        r1 = rng.random(n)
        r2 = rng.random(n)
        sq1 = np.sqrt(r1)
        u = 1 - sq1
        v = sq1 * (1 - r2)
        w = sq1 * r2
        tri_of_pt = np.repeat(np.nonzero(take)[0], cnt[take])
        P = (u[:, None] * T[tri_of_pt, 0] + v[:, None] * T[tri_of_pt, 1] + w[:, None] * T[tri_of_pt, 2])
        if len(N) and np.all(F.max(axis=0) < len(N)):
            TN = N[F]
            Np = (u[:, None] * TN[tri_of_pt, 0] + v[:, None] * TN[tri_of_pt, 1] + w[:, None] * TN[tri_of_pt, 2])
            L = np.linalg.norm(Np, axis=1)
            L[L == 0] = 1.0
            Np = Np / L[:, None]
        else:
            Np = np.zeros_like(P)
        out = '%s/%s_Point.pcd' % (outdir, stem)
        with open(out, 'w') as f:
            f.write('# .PCD v0.7 - Point Cloud Data file format\n')
            f.write('VERSION 0.7\nFIELDS x y z normal_x normal_y normal_z\n')
            f.write('SIZE 4 4 4 4 4 4\nTYPE F F F F F F\nCOUNT 1 1 1 1 1 1\n')
            f.write('WIDTH %d\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\nPOINTS %d\nDATA ascii\n' % (n, n))
            Q = np.hstack([P, Np])
            np.savetxt(f, Q, fmt='%.6f')
        print('%s: area=%.1f n=%d -> %s' % (stem, total, n, out), flush=True)

main()
