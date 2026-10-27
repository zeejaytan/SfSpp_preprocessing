#!/usr/bin/env python3
"""ticket 25 defaults proof.

Compares the six-column point set (x y z nx ny nz) of every written surface between two
arms. NOT md5 and NOT byte equality: the exported PLY carries a curvature column that the
pipeline never initialises, so two identical surfaces can differ byte for byte.

usage: defaults_proof25.py <outdir> <armA> <armB> [<armC> ...]   (armA is the reference)
       for each other arm, every surface present in both is compared.
An arm is a directory <outdir>/out/cells/<arm>/<piece>/surfaces/<piece>_Surface_<k>.ply
"""
import sys, os, json

def read_ply(path):
    with open(path, 'rb') as f:
        raw = f.read()
    i = raw.find(b'end_header')
    if i < 0:
        raise ValueError('no end_header: ' + path)
    end = raw.find(b'\n', i)
    header = raw[:end].decode('ascii', 'replace').splitlines()
    nvert, fmt, props = 0, None, []
    for line in header:
        t = line.split()
        if not t:
            continue
        if t[0] == 'format':
            fmt = t[1]
        elif t[0] == 'element' and len(t) >= 3 and t[1] == 'vertex':
            nvert = int(t[2])
        elif t[0] == 'property' and len(t) >= 3:
            props.append(t[2])
    if fmt != 'ascii':
        raise ValueError('not ascii ply: ' + path)
    body = raw[end + 1:].decode('ascii', 'replace').splitlines()
    pts = []
    for line in body:
        v = line.split()
        if len(v) < 6:
            continue
        pts.append(tuple(v[:6]))
        if len(pts) >= nvert:
            break
    return props, nvert, pts

def nn_displacement(a, b):
    try:
        from scipy.spatial import cKDTree
    except Exception:
        return None
    import math
    ta = cKDTree([[float(x) for x in p[:3]] for p in b])
    tb = cKDTree([[float(x) for x in p[:3]] for p in a])
    da, _ = ta.query([[float(x) for x in p[:3]] for p in a])
    db, _ = tb.query([[float(x) for x in p[:3]] for p in b])
    return (float(max(da)), float(max(db)))

def multiset_diff(a, b):
    """returns (only_in_a, only_in_b) counts on the exact 6-column string tuple"""
    from collections import Counter
    ca, cb = Counter(a), Counter(b)
    only_a = sum((ca - cb).values())
    only_b = sum((cb - ca).values())
    return only_a, only_b

def surfaces(root, arm, piece):
    d = os.path.join(root, 'out', 'cells', arm, piece, 'surfaces')
    out = {}
    for k in (0, 1):
        p = os.path.join(d, '%s_Surface_%d.ply' % (piece, k))
        if os.path.isfile(p):
            out[k] = p
    return out

def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return 2
    root, ref = sys.argv[1], sys.argv[2]
    others = sys.argv[3:]
    refdir = os.path.join(root, 'out', 'cells', ref)
    pieces = sorted(os.listdir(refdir)) if os.path.isdir(refdir) else []
    rows = []
    bad = 0
    for piece in pieces:
        sref = surfaces(root, ref, piece)
        if not sref:
            continue
        for other in others:
            soth = surfaces(root, other, piece)
            for k in sorted(set(sref) & set(soth)):
                pa, na, ta = read_ply(sref[k])
                pb, nb, tb = read_ply(soth[k])
                only_a, only_b = multiset_diff(ta, tb)
                same = (only_a == 0 and only_b == 0)
                disp = None if same else nn_displacement(ta, tb)
                row = dict(piece=piece, surface=k, arm_a=ref, arm_b=other,
                           props_a=pa, props_b=pb, n_a=na, n_b=nb, n_pts_a=len(ta), n_pts_b=len(tb),
                           point_set_equal=bool(same), only_in_a=only_a, only_in_b=only_b,
                           nn_max_a_to_b=None if disp is None else disp[0],
                           nn_max_b_to_a=None if disp is None else disp[1],
                           statistic='sorted six-column (x y z nx ny nz) multiset, md5 NOT used')
                rows.append(row)
                if not same:
                    bad += 1
                print('[PROOF25] piece=%s surface=%d a=%s b=%s npts=%d/%d pointset_equal=%s only_a=%d only_b=%d nn_max=%s'
                      % (piece, k, ref, other, len(ta), len(tb), 'yes' if same else 'no',
                         only_a, only_b, 'na' if disp is None else '%.6f/%.6f' % disp))
    with open(os.path.join(root, 'out', 'defaults_proof25.json'), 'w') as f:
        json.dump(rows, f, indent=1)
    print('[PROOF25] comparisons=%d differing=%d reference=%s others=%s'
          % (len(rows), bad, ref, ','.join(others)))
    return 0

if __name__ == '__main__':
    sys.exit(main())
