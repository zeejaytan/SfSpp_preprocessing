#!/usr/bin/env python3
# ticket 54 -- the mechanical theta table over this run's cell.tsv files, plus three checks:
#   1. D vs X (the no-op proof): same splitter theta (to 4 dp) AND the same surface point
#      counts (surf0/surf1) per piece.  The mesh stage is unseeded, so bytes are not compared;
#      the ticket's acceptance names thetas + surface point counts.
#   2. W vs the t51/t52 capped thetas: expected = min(t48_theta_formula, 0.9 * edge50 crossing)
#      from the committed thetas51.tsv; delta reported (tolerance 1.5 deg, the t50 crossing
#      tolerance -- REPORT ONLY, no verdict here).
#   3. W7 <= W on every piece where both carry a theta (strictly the dial turns the right way).
import os, re, sys, glob, argparse

ap = argparse.ArgumentParser()
ap.add_argument('--cells', required=True)
ap.add_argument('--ref', required=True, help='thetas51.tsv (committed reference)')
ap.add_argument('--out', required=True)
ap.add_argument('--check-out', required=True)
a = ap.parse_args()

def cell_fields(p):
    d = {}
    for line in open(p, encoding='utf-8', errors='replace'):
        line = line.rstrip('\n')
        if '\t' in line:
            k, v = line.split('\t', 1)
            d[k] = v
    return d

ref = {}
for line in open(a.ref, encoding='utf-8'):
    if line.startswith('#') or line.startswith('piece\t'):
        continue
    f = line.rstrip('\n').split('\t')
    if len(f) >= 3:
        ref[f[0]] = (f[1], f[2])  # (t48_theta_formula, edge50_glue60_k10)

rows = {}   # piece -> {arm: fields}
for c in sorted(glob.glob(os.path.join(a.cells, '*_arm*'))):
    m = re.match(r'^(.*)_arm(D|X|W7|W)$', os.path.basename(c))
    if not m:
        continue
    piece, arm = m.group(1), m.group(2)
    f = os.path.join(c, 'cell.tsv')
    if os.path.isfile(f):
        rows.setdefault(piece, {})[arm] = cell_fields(f)

hdr = ['piece', 'D_theta', 'X_theta', 'D_s0', 'X_s0', 'D_s1', 'X_s1',
       'W_formula', 'W_crossing', 'W_theta', 'W_capped',
       'W7_formula', 'W7_crossing', 'W7_theta', 'W7_capped',
       't51_expected', 'W_delta_t51', 'W7_le_W']
out = ['\t'.join(hdr)]
chk = []
fails = []

for piece in sorted(rows):
    r = rows[piece]
    def g(arm, key):
        return r.get(arm, {}).get(key, '')
    d_th, x_th = g('D', 'splitter_theta'), g('X', 'splitter_theta')
    d0, x0 = g('D', 'status_surf0_points'), g('X', 'status_surf0_points')
    d1, x1 = g('D', 'status_surf1_points'), g('X', 'status_surf1_points')
    wf, wx, wt, wc = g('W', 'worness54_formula_theta'), g('W', 'worness54_crossing'), g('W', 'worness54_theta'), g('W', 'worness54_capped')
    f7, x7, t7, c7 = g('W7', 'worness54_formula_theta'), g('W7', 'worness54_crossing'), g('W7', 'worness54_theta'), g('W7', 'worness54_capped')
    exp = ''
    delta = ''
    if piece in ref and wt:
        t48, e50 = ref[piece]
        try:
            cap = 0.9 * float(e50)
            e = min(float(t48), cap)
            exp = '%.4f' % e
            delta = '%.4f' % abs(float(wt) - e)
        except ValueError:
            exp = 'na'
    le = ''
    if wt and t7:
        try:
            le = 'yes' if float(t7) <= float(wt) else 'NO'
        except ValueError:
            le = 'na'
    out.append('\t'.join([piece, d_th, x_th, d0, x0, d1, x1,
                          wf, wx, wt, wc, f7, x7, t7, c7, exp, delta, le]))

    # check 1: D vs X
    if 'D' in r and 'X' in r:
        ok_th = d_th and x_th and abs(float(d_th) - float(x_th)) < 1e-4 if (d_th and x_th) else False
        ok_pts = (d0 == x0) and (d1 == x1)
        chk.append('%s\tD-vs-X\ttheta %s/%s %s\tpoints %s/%s,%s/%s %s' % (
            piece, d_th or 'na', x_th or 'na', 'OK' if ok_th else 'DIFF',
            d0 or 'na', x0 or 'na', d1 or 'na', x1 or 'na', 'OK' if ok_pts else 'DIFF'))
        if not (ok_th and ok_pts):
            fails.append('%s D-vs-X mismatch' % piece)
    # check 3: W7 <= W
    if wt and t7 and le == 'NO':
        fails.append('%s W7 theta %.4f > W theta %.4f' % (piece, float(t7), float(wt)))
    # W internals: theta == min(formula, w*crossing) when crossing present
    for arm, f_, x_, t_, wv in (('W', wf, wx, wt, '0.9'), ('W7', f7, x7, t7, '0.7')):
        if f_ and t_:
            try:
                ff, tt = float(f_), float(t_)
                if x_ and x_ != 'none':
                    capw = float(wv) * float(x_)
                    if abs(tt - min(ff, capw)) > 1e-3:
                        fails.append('%s %s theta %.5f != min(formula %.5f, cap %.5f)' % (piece, arm, tt, ff, capw))
                elif abs(tt - ff) > 1e-3:
                    fails.append('%s %s theta %.5f != formula %.5f (crossing none)' % (piece, arm, tt, ff))
            except ValueError:
                pass

open(a.out, 'w').write('\n'.join(out) + '\n')
open(a.check_out, 'w').write('\n'.join(chk) + ('\nFAILS:\n' + '\n'.join(fails) if fails else '\nCHECKS-ALL-OK\n'))
print('\n'.join(out))
print('--- checks ---')
print('\n'.join(chk))
print('FAILS: %d' % len(fails))
for f in fails:
    print('  ' + f)
sys.exit(0)
