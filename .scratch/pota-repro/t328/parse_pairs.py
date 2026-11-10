
"""parse_pairs.py - bar 3 table: GTPAIR rows from the 326 harness, restricted to the nine touching pairs."""
import sys

TOUCH = [(1,2),(1,4),(1,8),(1,9),(2,5),(2,9),(3,5),(6,7),(7,9)]
COLS = ['y','x','gap_min','n_1to1','n_d20','n_dot07','n_reject_kept','n_inl15_15deg','inlierCalc',
        'score_at_gt','overlap50','area','overlap100','dot_closest','linedot_closest','dot_med_d3',
        'absdot_med_d3','n_d3','n_d3_dotneg']

def parse(path):
    rows = {}
    for line in open(path, errors='replace'):
        if not line.startswith('GTPAIR\t'): continue
        t = line.rstrip('\n').split('\t')[1:]
        if len(t) < len(COLS): continue
        d = dict(zip(COLS, t))
        try: rows[(int(d['y']), int(d['x']))] = d
        except ValueError: pass
    return rows

def main():
    before, after, out = sys.argv[1], sys.argv[2], sys.argv[3]
    B, A = parse(before), parse(after)
    print('%-6s | %-42s | %-42s' % ('pair', 'BEFORE dot_med_d3 (n_d3, neg, inl15, gap)', 'AFTER'))
    ok = 0
    lines = ['pair\tbefore_dot_med_d3\tbefore_n_d3\tbefore_neg\tbefore_inl15\tbefore_gap\tafter_dot_med_d3\tafter_n_d3\tafter_neg\tafter_inl15\tafter_gap\tverdict']
    for (y, x) in TOUCH:
        b = B.get((y, x), {}); a = A.get((y, x), {})
        def f(d, k, fmt='%.3f'):
            v = d.get(k, '')
            try: return fmt % float(v)
            except Exception: return v or '-'
        bd, ad = f(b,'dot_med_d3'), f(a,'dot_med_d3')
        pass_after = (a.get('dot_med_d3') not in (None, '') and float(a['dot_med_d3']) >= 0.7
                      and int(float(a.get('n_inl15_15deg', 0))) > 0)
        ok += pass_after
        print('%d-%d   | %+7s (%s n_d3, %s neg, inl %s, gap %s) | %+7s (%s, %s, %s, %s) %s'
              % (y, x, float(b['dot_med_d3']) if b.get('dot_med_d3') not in (None,'') else float('nan'),
                 f(b,'n_d3','%d'), f(b,'n_d3_dotneg','%d'), f(b,'n_inl15_15deg','%d'), f(b,'gap_min'),
                 float(a['dot_med_d3']) if a.get('dot_med_d3') not in (None,'') else float('nan'),
                 f(a,'n_d3','%d'), f(a,'n_d3_dotneg','%d'), f(a,'n_inl15_15deg','%d'), f(a,'gap_min'),
                 'PASS' if pass_after else 'FAIL'))
        lines.append('\t'.join([('%d-%d' % (y, x)), bd, f(b,'n_d3','%d'), f(b,'n_d3_dotneg','%d'),
                                f(b,'n_inl15_15deg','%d'), f(b,'gap_min'), ad, f(a,'n_d3','%d'),
                                f(a,'n_d3_dotneg','%d'), f(a,'n_inl15_15deg','%d'), f(a,'gap_min'),
                                'PASS' if pass_after else 'FAIL']))
    open(out, 'w').write('\n'.join(lines) + '\n')
    print('after: %d/9 touching pairs at dot_med_d3 >= +0.7 with strict-gate inliers > 0' % ok)

main()
