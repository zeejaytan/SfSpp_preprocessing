#!/usr/bin/env python3
"""Ticket 65 stage 2: which step put Surface_0's far-face points into Surface_0?

finishImprovedSurface (mesh_processing_headless.cpp:1510-1531) writes a surface as
[admitted block] + [growth cluster], in that order, with de-duplication off by default.  The
admitted block size is the WINDOW-26-FINAL count of the branch that was copied over.  So the
first n_adm rows of <P>.S0 are the B-spline admission's points and the rest are the growth
cluster -- IF the export keeps that order.  This checks the order (cluster block size equals the
classify line's cluster size; admitted rows that duplicate a cluster row) and then reports, per
block, on which mesh sheet the points lie (t65_sector.sheets, nearest mesh vertex).
Usage: t65_admit.py <out_dir> arm=geom_dir=pieces_dir [...]
"""
import os, re, sys
import numpy as np
from scipy.spatial import cKDTree

WORK = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
SPEC = sys.argv[2:]
_argv = sys.argv
sys.argv = [_argv[0], OUT]
sys.path.insert(0, WORK)
import t65_sector as ts
cs = ts.cs
sys.argv = _argv

FIN = re.compile(r'\[WINDOW-26-FINAL\] piece=(\S+) surface=(\d) admitted_own=(\d+) admitted_other=(\d+) '
                 r'other_copied_over=(\w+) final_points=(\d+)')
CLS = re.compile(r'classify: face0 n=(\d+) interior_frac=([\d.]+) face1 n=(\d+) interior_frac=([\d.]+)')


def parse(log):
    fin, cls, swapped = {}, None, False
    for ln in open(log, errors='replace'):
        m = FIN.search(ln)
        if m:
            s = int(m.group(2))
            own, oth, cop, fp = int(m.group(3)), int(m.group(4)), m.group(5) == 'yes', int(m.group(6))
            fin[s] = (oth if cop else own, fp, own, oth, cop)
        m = CLS.search(ln)
        if m:
            cls = (int(m.group(1)), int(m.group(3)))
        if 'classify: swapped' in ln:
            swapped = True
    return fin, cls, swapped


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for spec in SPEC:
        arm, geom, pieces = spec.split('=', 2)
        for i in range(1, 10):
            P = 'Juglet_Piece_%d' % i
            log = os.path.join(pieces, P, 'mesh.log')
            fin, cls, swapped = parse(log)
            z = ts.load_piece(P)
            V, F, labels = z['V'], z['F'], z['labels']
            sh = ts.sheets(V, F, labels)
            sheet = sh[0]
            vs = np.zeros((len(V), 4), int)
            sidx = np.where(sheet < 0, 3, sheet)
            for k in range(3):
                np.add.at(vs, (F[:, k], sidx), 1)
            vsheet = np.argmax(vs[:, :3], 1)
            vsheet[(vs[:, 0] == 0) & (vs[:, 1] == 0)] = 2
            tv = cKDTree(V)
            pts = {}
            for s, suf in ((0, 'S0'), (1, 'S1')):
                p = cs.read_ply(os.path.join(geom, P + '.' + suf))
                pts[s] = np.stack([p[c] for c in 'xyz'], 1)
            covA = cKDTree(pts[0]).query(V)[0] <= cs.COV_TOL
            s0s = 0 if covA[vsheet == 0].mean() >= covA[vsheet == 1].mean() else 1
            for s in (0, 1):
                X = pts[s]
                n_adm, fp, own, oth, cop = fin[s]
                n_cl = len(X) - n_adm
                own_sheet = s0s if s == 0 else 1 - s0s
                d, vi = tv.query(X)
                sh_pt = vsheet[vi]
                blocks = {'adm': slice(0, n_adm), 'cl': slice(n_adm, len(X))}
                A, C = X[blocks['adm']], X[blocks['cl']]
                dup = (cKDTree(C).query(A)[0] == 0.0).mean() if len(A) and len(C) else np.nan
                r = dict(arm=arm, piece=P, surface=s, n=len(X), final_points=fp, n_adm=n_adm, n_cl=n_cl,
                         adm_own=own, adm_other=oth, copied_other=int(cop),
                         cls_sizes='%d;%d' % cls if cls else '', swapped=int(swapped),
                         adm_dup_of_cl=round(float(dup), 4))
                for b, sl in blocks.items():
                    shb = sh_pt[sl]
                    nb = max(len(shb), 1)
                    r[b + '_on_own'] = round(float((shb == own_sheet).sum() / nb), 4)
                    r[b + '_on_far'] = round(float((shb == 1 - own_sheet).sum() / nb), 4)
                    r[b + '_on_frac'] = round(float((shb == 2).sum() / nb), 4)
                    r[b + '_n_far'] = int((shb == 1 - own_sheet).sum())
                    r[b + '_dvert_med'] = round(float(np.median(d[sl])), 3) if len(shb) else ''
                far = sh_pt == 1 - own_sheet
                r['far_total'] = int(far.sum())
                r['far_from_adm'] = round(float(far[blocks['adm']].sum() / max(far.sum(), 1)), 4)
                rows.append(r)
                ts.log('%s %s S%d n=%d adm=%d cl=%d (cls %s) dup=%.3f far_total=%d far_from_adm=%.3f '
                       'adm_on_far=%.3f cl_on_far=%.3f' % (arm, P, s, len(X), n_adm, n_cl, r['cls_sizes'],
                                                           dup, r['far_total'], r['far_from_adm'],
                                                           r['adm_on_far'], r['cl_on_far']))
                if P == 'Juglet_Piece_1' and s == 0:
                    np.savez_compressed(os.path.join(OUT, 'admit_j1_%s.npz' % arm), X=X, n_adm=n_adm,
                                        sh_pt=sh_pt, own_sheet=own_sheet)
    cols = list(rows[0].keys())
    with open(os.path.join(OUT, 'admit_blocks.tsv'), 'w') as fh:
        fh.write('\t'.join(cols) + '\n')
        for r in rows:
            fh.write('\t'.join(str(r.get(c, '')) for c in cols) + '\n')
    ts.log('done')


if __name__ == '__main__':
    main()
