import io
p = '/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv'
lines = io.open(p, encoding='utf-8').read().split('\n')
out = []
hit = 0
for ln in lines:
    if ln.startswith('20261110-1202_e94d8fb_t324-axes\t'):
        f = ln.split('\t')
        while len(f) < 6:
            f.append('')
        f[4] = 'pass'
        f[5] = 'identity run for ticket 324: rule on = axes323 on all 172 files, rule off = axes322 on all 181 (lead re-verified); no assembly job needed'
        ln = '\t'.join(f[:6])
        hit += 1
    out.append(ln)
io.open(p, 'w', encoding='utf-8').write('\n'.join(out))
print('rows updated', hit)
