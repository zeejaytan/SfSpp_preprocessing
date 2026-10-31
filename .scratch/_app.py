p = '.scratch/pota-repro/issues/272-probe-shipped-defaults.md'
v = open('.scratch/_verdict272.md', encoding='utf-8').read()
t = open(p, encoding='utf-8').read()
open(p, 'w', encoding='utf-8').write(t.rstrip() + '\n' + v)
print('appended; lines now', len(open(p, encoding='utf-8').read().splitlines()))