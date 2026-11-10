
"""parse_linenormals.py - bar 2 table: do the exported Breakline_0 normals agree with the wall the line rides?

For every piece: for every point of Bl0, the dot between the exported line normal and the normal of the
nearest point of the wall it rides (S0, the face whose boundary Bl0 walks). frac>0 and median dot.
Flip the wall's own sign is NOT applied: the question is whether the line's exported normal matches the
wall it sits on, sign included.
"""
import sys, os
import numpy as np
import geomio

def piece_row(piece, geom):
    out = {}
    walls = {}
    for s in (0, 1):
        p = os.path.join(geom, '%s.S%d' % (piece, s))
        if not os.path.exists(p): return None
        data, _ = geomio.load_ply(p)
        walls[s] = (data[:, :3], data[:, 3:6])
    for s in (0, 1):
        p = os.path.join(geom, '%s.Bl%d' % (piece, s))
        if not os.path.exists(p): continue
        data, _, _ = geomio.load_pcd(p)
        lpts, lnrm = data[:, :3], data[:, 3:6]
        row = {}
        for w in (0, 1):
            d, dot = geomio.nn_dot(lpts, lnrm, walls[w][0], walls[w][1])
            row['wall%d' % w] = dict(frac=float((dot > 0).mean()), med=float(np.median(dot)),
                                     frac_abs=float((np.abs(dot) > 0.5).mean()),
                                     d_med=float(np.median(d)))
        row['n'] = lpts.shape[0]
        out[s] = row
    return out

def main():
    geom, label, out = sys.argv[1], sys.argv[2], sys.argv[3]
    rows = []
    for k in range(1, 10):
        piece = 'Juglet_Piece_%d' % k
        r = piece_row(piece, geom)
        if r is None: continue
        for s in sorted(r):
            e = r[s]
            rows.append((label, k, s, e['n'], e['wall0']['frac'], e['wall0']['med'], e['wall0']['frac_abs'],
                         e['wall1']['frac'], e['wall1']['med']))
    with open(out, 'w') as f:
        f.write('label\tpiece\tline\tn\tagree_riding_wall\tmeddot_riding\tfrac_absdot_gt0.5_riding\tagree_other_wall\tmeddot_other\n')
        for t in rows:
            f.write('%s\t%d\tBl%d\t%d\t%.3f\t%+.3f\t%.3f\t%.3f\t%+.3f\n' % t)
    for t in rows:
        riding = t[5] if t[2] == 0 else t[8]
        print('%s piece %d Bl%d n=%d: agrees with riding wall %.3f (med %+.3f) | other wall %.3f (med %+.3f)'
              % (t[0], t[1], t[2], t[3], t[4], t[5], t[7], t[8]))

main()
