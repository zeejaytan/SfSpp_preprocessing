import re, glob, os
dirs = ["pota155_repro","pota173_repro","pota174_repro","pota175_repro","pota177_repro","pota221","pota222","pota223","pota224","pota225","pota226","pota227","pota229","pota230","pota231"]
tickets = sorted(glob.glob('.scratch/pota-repro/issues/*.md'))
pat = re.compile(r'(\.scratch/(?:%s)/[A-Za-z0-9_./\-{}\*]+)' % '|'.join(dirs))
tot_missing = 0
for d in dirs:
    refs = {}
    for t in tickets:
        txt = open(t, encoding='utf-8', errors='replace').read()
        for m in pat.finditer(txt):
            p = m.group(1).rstrip('.,;:)]')
            refs.setdefault(p, set()).add(os.path.basename(t))
    if not refs:
        print(d + ': NO CITATIONS'); continue
    missing = [p for p in refs if not os.path.exists(p)]
    tot_missing += len(missing)
    print(d + ': cited %d, missing %d, tickets %s' % (len(refs), len(missing), ','.join(sorted({x for s in refs.values() for x in s}))))
print('TOTAL missing cited paths:', tot_missing)