#!/usr/bin/env python3
"""ticket 25 ladder: one row per (arm, piece, rung) with the ticket's expectation, what the
dump actually measured, and a mechanical pass/fail. Evidence only -- it does not judge
whether a segmentation is right.

Expectations below are transcribed from the ticket's expectation table (itself from tickets
20/23/24/26) and are the only claims this script tests. A rung the ticket made no claim about
is written with pass 'n/a' and the expectation text says so, rather than being dropped.

usage: ladder25.py <rundir>
writes <rundir>/out/ladder.tsv and <rundir>/out/ladder_summary.txt
"""
import sys, os, json

ARMS = ['B', 'D', 'E']
PIECES = ['Juglet_Piece_2', 'Juglet_Piece_3', 'Juglet_Piece_5', 'Juglet_Piece_7']

# ---- the ticket's expectations ---------------------------------------------------------
# keys: r1 points_out, r2 cluster_count/sizes, r3 cluster_count/merges, r4 fitted, r5 gates
E = {}
def exp(arm, piece, **kw):
    E[(arm, piece)] = kw

exp('B', 'Juglet_Piece_2', r1_points_out=1031, r2_clusters=0,
    text_r1='1031 points into clustering at defaults',
    text_r2='ZERO regions at all retries (failure upstream of every later rung)',
    text_r3='no cluster to merge', text_r4='no fit ran', text_r5='nothing written')
exp('D', 'Juglet_Piece_2', r5_gates={'pair'},
    text_r1='not stated by the ticket; today-default density',
    text_r2='not stated by the ticket',
    text_r3='not stated by the ticket',
    text_r4='not stated by the ticket',
    text_r5='with the chain off a pair IS written (ticket 26 W*L rows)')
exp('E', 'Juglet_Piece_2',
    text_r1='not stated by the ticket; native density',
    text_r2='not stated by the ticket', text_r3='not stated by the ticket',
    text_r4='not stated by the ticket', text_r5='not stated by the ticket')

exp('B', 'Juglet_Piece_3', r2_clusters=2, r2_sizes=[169, 99], r3_clusters=1, r3_merges=1,
    r5_gates={'single', 'single-off', 'none'},
    text_r1='not stated by the ticket; today-default density',
    text_r2='two regions (169, 99) = two patches of ONE wall',
    text_r3='fused to one by one merge (5 boundary pairs, pairDistMin 0.520166)',
    text_r4='one surviving cluster, so the single-cluster path or nothing',
    text_r5='one surface or none')
exp('E', 'Juglet_Piece_3', r2_clusters=2, r3_clusters=1,
    text_r1='not stated by the ticket; native density',
    text_r2='raw regions OPPOSITE (dot -0.983, 1.90 mm = a real pair)',
    text_r3='the merge still fires (legacy merge; not tracked by rung 3)',
    text_r4='not stated by the ticket', text_r5='not stated by the ticket')

exp('B', 'Juglet_Piece_5', r2_clusters=1, r2_sizes=[679], r1_points_out=None,
    text_r1='not stated by the ticket; today-default density',
    text_r2='ONE region (679 of 3021): second wall never separated',
    text_r3='one cluster reaches the write step',
    text_r4='one surviving cluster, single-cluster path', text_r5='no pair')
exp('D', 'Juglet_Piece_5', r2_clusters=2, r5_gates={'pair'},
    text_r1='not stated by the ticket; today-default density',
    text_r2='the only genuine wall pair at this density (2.28 mm through, 0.36 mm along)',
    text_r3='not stated by the ticket (chain off: legacy merge)', text_r4='not stated by the ticket',
    text_r5='a genuine wall pair is written')

exp('B', 'Juglet_Piece_7', r2_clusters=2, r2_sizes=[1012, 829], r5_gates={'pair'},
    text_r1='not stated by the ticket; today-default density',
    text_r2='two regions (1012, 829) = two COPLANAR patches 0.230 mm apart through the normal',
    text_r3='not stated by the ticket', text_r4='not stated by the ticket',
    text_r5='a pair is written from two coplanar patches')
exp('E', 'Juglet_Piece_7', r5_gates={'pair'},
    text_r1='not stated by the ticket; native density',
    text_r2='not stated by the ticket (the one clean pair: 3.14 mm through, 0.31 mm along)',
    text_r3='not stated by the ticket', text_r4='not stated by the ticket',
    text_r5='the positive control: a pair is written')

RUNGS = [('r1', 'r1_downsampled'), ('r2', 'r2_clusters_premerge'), ('r3', 'r3_after_merge'),
         ('r4', 'r4_after_reassign'), ('r5', 'r5_write')]

def load(dumpdir, base):
    j = os.path.join(dumpdir, base + '.json')
    p = os.path.join(dumpdir, base + '.ply')
    if not os.path.isfile(j):
        return None, None
    with open(j) as f:
        try:
            d = json.load(f)
        except Exception as e:
            return {'__error__': str(e)}, None
    return d, (p if os.path.isfile(p) else None)

def fmtw(d):
    ws = d.get('windows') or []
    out = []
    for w in ws:
        out.append('s%d clamp=%s rule=%s reason=%s' % (w.get('surface'), w.get('clamped_mm'), w.get('rule'), w.get('reason')))
    return '; '.join(out) if out else 'none'

def meas_r1(d):
    return 'points_in=%s points_out=%s target=%s radius_mm=%s spacing_policy=%s S_mm=%s' % (
        d.get('points_in'), d.get('points_out'), d.get('downsample_target'),
        d.get('sampling_radius_mm'), d.get('spacing_policy'), d.get('S_mm'))

def meas_r2(d):
    return 'clusters=%s sizes=%s npts=%s floor_applied=%s floor_from=%s capped=%s min_cluster_eff=%s scale=%s spacing_mm=%s unclaimed=%s' % (
        len(d.get('clusters') or []), d.get('clusters'), d.get('npts'), d.get('floor_applied'),
        d.get('floor_from'), d.get('floor_capped'), d.get('min_cluster_eff'), d.get('count_scale'),
        d.get('spacing_mm'), d.get('points_in_no_cluster'))

def meas_r3(d):
    ms = d.get('merges') or []
    desc = []
    for m in ms:
        desc.append('p%s %s->%s %s/%s pairs=%s ndot=%s' % (m.get('pass'), m.get('from_tags'), m.get('into_tags'),
                    m.get('from_size_before'), m.get('into_size_before'), m.get('boundary_pairs'), m.get('normal_dot')))
    return 'clusters=%s sizes=%s tracking=%s passes=%s pairs_tested=%s merges=%d [%s] classify=%s unclaimed=%s' % (
        len(d.get('clusters') or []), d.get('clusters'), d.get('merge_tracking'), d.get('merge_passes'),
        d.get('merge_pairs_tested'), len(ms), ' ; '.join(desc), d.get('classify_swap'), d.get('points_in_no_cluster'))

def meas_r4(d):
    return 'fitted=%s mode=%s flipped=%s passes=%s windows=[%s] own=%s other=%s cand=%s final=%s copied=%s rc=%s' % (
        d.get('fitted'), d.get('reassign_mode'), d.get('normals_flipped'), d.get('passes'), fmtw(d),
        d.get('admitted_own'), d.get('admitted_other'), d.get('candidates'), d.get('final_points'),
        d.get('other_copied_over'), d.get('reason_counts'))

def meas_r5(d):
    return 'gate=%s vertices=%s points=%s on_s0=%s on_s1=%s on_neither=%s without_normal=%s rc=%s' % (
        d.get('write_gate'), d.get('surface_vertices'), d.get('points'), d.get('points_on_surface_0'),
        d.get('points_on_surface_1'), d.get('points_on_neither'), d.get('points_without_normal'),
        d.get('reason_counts'))

MEAS = {'r1': meas_r1, 'r2': meas_r2, 'r3': meas_r3, 'r4': meas_r4, 'r5': meas_r5}

def verdict(rung, e, d, cell_exit):
    if cell_exit not in ('0', 0):
        return 'cell-failed', 'rung not judged: the cell exited %s' % cell_exit
    if d is None:
        return 'MISSING', 'no sidecar was written for this rung'
    if '__error__' in d:
        return 'BAD-JSON', d['__error__']
    if rung == 'r1':
        if e.get('r1_points_out') is not None and d.get('points_out') != e['r1_points_out']:
            return 'fail', 'points_out %s != expected %s' % (d.get('points_out'), e['r1_points_out'])
        if e.get('r1_points_out') is None:
            return 'n/a', 'the ticket states no rung-1 count for this arm'
        return 'pass', 'points_out matches'
    if rung == 'r2':
        if 'r2_clusters' not in e:
            return 'n/a', 'the ticket states no rung-2 count for this arm'
        if len(d.get('clusters') or []) != e['r2_clusters']:
            return 'fail', 'cluster count %d != expected %d' % (len(d.get('clusters') or []), e['r2_clusters'])
        if e.get('r2_sizes') and sorted(d.get('clusters') or []) != sorted(e['r2_sizes']):
            return 'fail', 'sizes %s != expected %s' % (d.get('clusters'), e['r2_sizes'])
        return 'pass', 'region count%s matches' % (' and sizes' if e.get('r2_sizes') else '')
    if rung == 'r3':
        if 'r3_clusters' not in e:
            return 'n/a', 'the ticket states no rung-3 count for this arm'
        if len(d.get('clusters') or []) != e['r3_clusters']:
            return 'fail', 'cluster count %d != expected %d' % (len(d.get('clusters') or []), e['r3_clusters'])
        if 'r3_merges' in e:
            n = len(d.get('merges') or [])
            if d.get('merge_tracking') != 'paper-chain':
                return 'fail', 'merge not tracked (%s) so the merge count cannot be confirmed' % d.get('merge_tracking')
            if n != e['r3_merges']:
                return 'fail', '%d merges != expected %d' % (n, e['r3_merges'])
        return 'pass', 'cluster count matches'
    if rung == 'r4':
        if 'r4_fitted' in e and bool(d.get('fitted')) != bool(e['r4_fitted']):
            return 'fail', 'fitted %s != expected %s' % (d.get('fitted'), e['r4_fitted'])
        return 'n/a', 'the ticket states no rung-4 predicate for this arm'
    if rung == 'r5':
        if 'r5_gates' in e:
            if d.get('write_gate') not in e['r5_gates']:
                return 'fail', 'write_gate %s not in expected %s' % (d.get('write_gate'), sorted(e['r5_gates']))
            return 'pass', 'write_gate %s in expected %s' % (d.get('write_gate'), sorted(e['r5_gates']))
        return 'n/a', 'the ticket states no rung-5 predicate for this arm'
    return 'n/a', ''

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    exit_of = {}
    cells = os.path.join(root, 'out', 'cells', 'cells25.tsv')
    if os.path.isfile(cells):
        with open(cells) as f:
            for line in f:
                t = line.rstrip('\n').split('\t')
                if len(t) >= 7 and t[0] not in ('tag',):
                    exit_of[(t[0], t[1])] = t[6]
    rows = []
    for arm in ARMS:
        for piece in PIECES:
            e = E.get((arm, piece), {})
            dumpdir = os.path.join(root, 'out', 'dump', arm, piece)
            for rung, base in RUNGS:
                d, ply = load(dumpdir, base)
                cell_exit = exit_of.get((arm, piece), 'no-cell-row')
                v, why = verdict(rung, e, d, cell_exit)
                if d is None:
                    meas = 'no sidecar'
                elif '__error__' in d:
                    meas = 'unreadable json'
                else:
                    meas = MEAS[rung](d)
                    if ply:
                        meas += ' ply=%s' % ply
                rows.append([arm, piece, rung, cell_exit, e.get('text_' + rung, 'not stated by the ticket'),
                             meas, v, why])
    out = os.path.join(root, 'out', 'ladder.tsv')
    with open(out, 'w') as f:
        f.write('arm\tpiece\trung\tcell_exit\texpectation\tmeasurement\tpass\twhy\n')
        for r in rows:
            f.write('\t'.join(str(x) for x in r) + '\n')
    n = {}
    for r in rows:
        n[r[6]] = n.get(r[6], 0) + 1
    with open(os.path.join(root, 'out', 'ladder_summary.txt'), 'w') as f:
        f.write('ticket 25 ladder: %d rows over arms %s, pieces %s, five rungs\n' % (len(rows), ','.join(ARMS), ','.join(PIECES)))
        for k in sorted(n):
            f.write('  %s\t%d\n' % (k, n[k]))
        f.write('pass = the ticket made a claim for this rung and the dump matches it; fail = the dump contradicts it;\n')
        f.write('n/a = the ticket made no claim for this (arm, piece, rung); MISSING = the rung file was not written.\n')
        f.write('No column here says whether a segmentation is right.\n')
    print('[LADDER25] rows=%d %s' % (len(rows), ' '.join('%s=%d' % (k, n[k]) for k in sorted(n))))

if __name__ == '__main__':
    main()
