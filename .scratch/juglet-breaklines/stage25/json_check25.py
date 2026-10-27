"""ticket 25: mechanical check of the dump files the pipeline wrote.

Reads every sidecar and every PLY under <rundir>/out/dump: each sidecar must parse as JSON, each
PLY must be ASCII, carry an element-vertex count that matches the number of body rows, and carry
the two label columns the ticket asks for (int cluster_id, uchar reason). One line per problem, a
two-line summary, and no claim about whether any segmentation is right.
"""
import json
import os
import sys


def check_ply(path):
    props = []
    n = None
    fmt = None
    with open(path) as f:
        if f.readline().strip() != 'ply':
            return 'does not start with a ply magic line'
        while True:
            line = f.readline()
            if not line:
                return 'header ends without end_header'
            t = line.strip()
            if t.startswith('format '):
                fmt = t
            elif t.startswith('element vertex '):
                n = int(t.split()[2])
            elif t.startswith('property '):
                props.append(t.split()[-1])
            elif t == 'end_header':
                break
        rows = sum(1 for line in f if line.strip())
    if fmt != 'format ascii 1.0':
        return 'format is %r, not ascii 1.0' % (fmt,)
    if n is None:
        return 'no element vertex line'
    if rows != n:
        return 'header says %d points, body has %d rows' % (n, rows)
    if 'cluster_id' not in props or 'reason' not in props:
        return 'label columns missing from %s' % (props,)
    return None


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    dump = os.path.join(root, 'out', 'dump')
    if not os.path.isdir(dump):
        print('[JSON25] no dump directory under %s' % dump)
        return 0
    jn = jb = pn = pb = 0
    for dirpath, _, files in os.walk(dump):
        for name in sorted(files):
            p = os.path.join(dirpath, name)
            if name.endswith('.json'):
                jn += 1
                try:
                    with open(p) as f:
                        json.load(f)
                except Exception as e:
                    jb += 1
                    print('[JSON25] bad %s: %s' % (p, e))
            elif name.endswith('.ply'):
                pn += 1
                why = check_ply(p)
                if why:
                    pb += 1
                    print('[PLY25] bad %s: %s' % (p, why))
    print('[JSON25] sidecars=%d bad=%d' % (jn, jb))
    print('[PLY25] plys=%d bad=%d' % (pn, pb))
    return 0


if __name__ == '__main__':
    sys.exit(main())
