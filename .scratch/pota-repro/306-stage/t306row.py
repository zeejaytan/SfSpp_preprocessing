import sys
row = open('/tmp/t306a2.row').read()
assert row.endswith('\n') and row.count('\t') == 5, repr(row)
p = '/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv'
old = open(p).read()
assert row not in old, 'row already present'
assert old.endswith('\n'), 'index does not end with newline'
open(p, 'a').write(row)
new = open(p).read()
assert new.endswith(row)
print('rows', len(new.splitlines()), 'last:', repr(new.splitlines()[-1]))
