
"""parse_filing.py - bar 1 table: did the t328 filing put the interior wall in slot 0, and what decided it.

Input: the classify text captured from pieces/*/mesh.log, and the exported geom bundle.
The census (independent of the code under test): about the GT axis, the interior face is the one whose
median perpendicular radius is smaller. That is the definition the ticket names; the code's own
witnesses (kappa, radius about SFS_AXIS_FILE, the axis-ray vote) are read from its print.
"""
import sys, os, re, json
import numpy as np
import geomio

def parse_cls(path):
    out = {}
    t328 = re.compile(r'PAPER-234\] t328: kappa0=(\S+) kappa1=(\S+) ratio=(\S+) kpick=(\S+) radius0=(\S+) radius1=(\S+) dr=(\S+) rpick=(\S+) axisfit=(\S+) vote_pick=(\S+) vote_gap=(\S+) -> interior_face=(\S+) decider=(\S+)')
    vote = re.compile(r'PAPER-234\] classify: face0 n=(\d+) interior_frac=(\S+) satA=(\S+) satB=(\S+)')
    flips = re.compile(r'Normals flipped: (true|false)')
    piece = None
    for line in open(path, errors='replace'):
        m = re.search(r'(Juglet_Piece_(\d+)|Pot_[A-J]_Piece_(\d+))', line)
        if m: piece = m.group(0)
        mv = vote.search(line)
        if mv and piece:
            out.setdefault(piece, {})['vote'] = dict(n0=int(mv.group(1)), in0=float(mv.group(2)),
                                                     satA=float(mv.group(3)), satB=float(mv.group(4)))
        mt = t328.search(line)
        if mt and piece:
            g = mt.groups()
            out.setdefault(piece, {})['t328'] = dict(kappa0=float(g[0]), kappa1=float(g[1]), ratio=float(g[2]),
                                                    kpick=int(g[3]), radius0=float(g[4]), radius1=float(g[5]),
                                                    dr=float(g[6]), rpick=int(g[7]), axisfit=float(g[8]),
                                                    vote_pick=int(g[9]), vote_gap=float(g[10]),
                                                    interior_face=int(g[11]), decider=g[12])
        mf = flips.search(line)
        if mf and piece:
            out.setdefault(piece, {})['flipped'] = (mf.group(1) == 'true')
    return out

def main():
    cls, geom, gt, label, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
    info = parse_cls(cls)
    rows = []
    for k in range(1, 10):
        piece = 'Juglet_Piece_%d' % k
        c, d = geomio.load_axis(os.path.join(gt, '%s_Axis.xyz' % piece))
        r = {}
        for s in (0, 1):
            data, _ = geomio.load_ply(os.path.join(geom, '%s.S%d' % (piece, s)))
            r[s] = geomio.face_stats(data[:, :3], data[:, 3:6], c, d)['r_med']
        census = 0 if r[0] < r[1] else 1          # the smaller radius about the GT axis is the interior
        e = info.get(piece, {})
        t = e.get('t328', {})
        v = e.get('vote', {})
        rows.append(dict(label=label, piece=k, r_S0=r[0], r_S1=r[1], dr_census=abs(r[0] - r[1]),
                         interior_face_exported=census, slot0_is_interior=(census == 0),
                         interior_face_code=t.get('interior_face'), decider=t.get('decider'),
                         kappa0=t.get('kappa0'), kappa1=t.get('kappa1'), ratio=t.get('ratio'),
                         radius0=t.get('radius0'), radius1=t.get('radius1'), dr_code=t.get('dr'),
                         axisfit=t.get('axisfit'), vote_pick=t.get('vote_pick'), vote_gap=t.get('vote_gap'),
                         flipped=e.get('flipped'), vote_n0=v.get('n0'), in0=v.get('in0'),
                         satA=v.get('satA'), satB=v.get('satB')))
    keys = list(rows[0].keys())
    with open(out, 'w') as f:
        f.write('\t'.join(keys) + '\n')
        for row in rows:
            f.write('\t'.join('' if row[k2] is None else (('%.4f' % row[k2]) if isinstance(row[k2], float) else str(row[k2])) for k2 in keys) + '\n')
    for row in rows:
        print('%s piece %d: r S0 %.3f S1 %.3f -> slot0 interior %s | code face %s decider %s '
              'ratio %.2f radius %.2f/%.2f axisfit %.2f vote_pick %s vote_gap %+.2f flipped %s'
              % (label, row['piece'], row['r_S0'], row['r_S1'], 'YES' if row['slot0_is_interior'] else 'NO',
                 row['interior_face_code'], row['decider'], row['ratio'] or 0, row['radius0'] or 0,
                 row['radius1'] or 0, row['axisfit'] or 0, row['vote_pick'], row['vote_gap'] or 0, row['flipped']))
    print('slot0 interior on %d/9' % sum(1 for r2 in rows if r2['slot0_is_interior']))

main()
