"""POTA-204 BUILD: D-chain thin TRUE loops (seated, bundle frame) for C01-C04 Bl_0
on the PRISTINE fresh Pot C base. Port of p197_build.py generalized to 4 pieces.
Vehicle: pristine asm @ 11f4827 (A/B/C all OUT); asserts live in the E2E sbatch.
Laptop-numpy D-chain; seated walks uploaded (md5-verified both ends)."""
import numpy as np, os, hashlib, shutil
P204 = '/data/gpfs/projects/punim2657/pota204_repro'
BASE = '/data/gpfs/projects/punim2657/pota197_repro/pota197_prep/pota197_bundle_C/SfS_pp'
ORIG = '/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp'
STAGE = P204 + '/stage'
os.makedirs(P204 + '/prep', exist_ok=True)
log = open(P204 + '/p204_build.txt', 'w')
def say(s):
    print(s, flush=True); log.write(s + '\n')
def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()
def cmd(c):
    import subprocess
    return subprocess.run(c, shell=True, capture_output=True, text=True)
# 0. pristine-base freshness: C01 must equal landed-fresh C01 (197's anchor)
PRISTINE_C01 = {'Pot_C_Piece_01_Breakline_0.pcd': 'dcb078dd03aefcfc5f0361ab2bc660e0',
                'Pot_C_Piece_01_Breakline_1.pcd': 'fa3805fe86ac935d4fa872473bf80ced'}
for f, h in PRISTINE_C01.items():
    got = md5(BASE + '/Breaklines/' + f)
    say('pristine-base C01 %s md5=%s expect=%s %s' % (f, got, h, 'OK' if got == h else 'MISMATCH-STOP'))
    assert got == h, 'pristine base C01 moved -- STOP'
# 1. walk transfer check (laptop md5s, npy file bytes)
WALKS = {'01': ('32b80e8b55adeb3a6579a3a77a5e2347', 204),
         '02': ('550a03d6c5504bbd9f9afa73bd50ca50', 231),
         '03': ('355ee5bf96b39f573d2e398ea5e305ea', 191),
         '04': ('e1f4299c381431e7fe7c7bff5b9551af', 126)}
HDR = set(['VERSION', 'FIELDS', 'SIZE', 'TYPE', 'COUNT', 'WIDTH', 'HEIGHT', 'VIEWPOINT', 'POINTS', 'DATA'])
def load_pcd7(p):
    rows = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#' or s.split()[0] in HDR:
            continue
        v = s.split()
        try:
            rows.append([float(x) for x in v[:7]])
        except ValueError:
            pass
    return np.array(rows)
def load_head(p):
    lines = open(p).read().splitlines()
    seg1 = lines[1]
    nseg = int(seg1.split()[1]); npts = int(seg1.split()[2]); info = int(seg1.split()[3])
    segs = [lines[2 + i] for i in range(nseg)]
    head9 = lines[2 + nseg:2 + nseg + 9]
    assert head9[0].startswith('VERSION') and head9[-1].startswith('POINTS'), head9[0] + ' / ' + head9[-1]
    assert lines[2 + nseg + 9] == 'DATA ascii', lines[2 + nseg + 9]
    return seg1, nseg, npts, info, segs, head9
L = {}
for pc, (hm, nnew) in WALKS.items():
    wf = STAGE + '/p204_C%s_thin_walk.npy' % pc
    got = md5(wf)
    say('C%s walk md5=%s expect=%s %s' % (pc, got, hm, 'OK' if got == hm else 'CORRUPT-STOP'))
    assert got == hm, 'walk transfer corrupt -- STOP'
    Li = np.load(wf)
    assert Li.shape == (nnew, 3), (pc, Li.shape)
    st = np.sqrt(((Li[1:] - Li[:-1]) ** 2).sum(-1))
    closure = float(np.linalg.norm(Li[-1] - Li[0]))
    full = np.append(st, closure)
    say('C%s WALK: %dx3 md5-ok arc-steps=%.1f arc-closed=%.1f steps max=%.2f median=%.2f n>5mm=%d closure=%.2f' % (
        pc, nnew, float(st.sum()), float(st.sum()) + closure, full.max(), np.median(full), int((full > 5).sum()), closure))
    assert closure <= 2.0 and int((full > 5).sum()) == 0, 'loop not closed/clean -- STOP'
    L[pc] = (Li, nnew)
# 2. donor channels from author ORIG Bl_0 per piece (bundle frame, direct NN)
N = {}
for pc in ['01', '02', '03', '04']:
    Li, nnew = L[pc]
    A = load_pcd7(ORIG + '/Breaklines/Pot_C_Piece_%s_Breakline_0.pcd' % pc)
    say('C%s donor ORIG Bl_0 n=%d' % (pc, len(A)))
    d = np.sqrt(((Li[:, None, :3] - A[None, :, :3]) ** 2).sum(-1))
    nn = d.argmin(1); nd = d.min(1)
    say('C%s G0-donor NN: med=%.2f max=%.2f n>5mm=%d' % (pc, np.median(nd), nd.max(), int((nd > 5).sum())))
    assert float(np.median(nd)) < 8.0, 'frame mismatch walk-vs-donor -- STOP (frame errors are ~350mm)'
    N[pc] = A[nn][:, 3:7]
# 3. copy PRISTINE base, install thin loops into Bl_0 per piece (headers rescaled per piece)
dst = P204 + '/prep/pota204_bundle_C_204/SfS_pp'
if os.path.exists(dst):
    shutil.rmtree(dst)
shutil.copytree(BASE, dst)
for pc in ['01', '02', '03', '04']:
    Li, NNEW = L[pc]
    seg1, nseg, npts, info, segs, head9 = load_head(BASE + '/Breaklines/Pot_C_Piece_%s_Breakline_0.pcd' % pc)
    say('C%s pristine base Bl_0 header: nseg=%d npts=%d info=%d' % (pc, nseg, npts, info))
    bounds = []
    for s in segs:
        a, b, f = s.split()[1:4]
        bounds.append((int(a), int(b), int(f)))
    assert bounds[0][0] == 1 and bounds[-1][1] == npts, (pc, bounds[0], bounds[-1], npts)
    newsegs = []
    for k, (a, b, f) in enumerate(bounds):
        na = int(round((a - 1) / npts * NNEW)) + 1
        nb = int(round(b / npts * NNEW))
        if k == 0:
            na = 1
        if k == len(bounds) - 1:
            nb = NNEW
        if nb < na:
            nb = na
        newsegs.append('# %d %d %s' % (na, nb, f))
    for k in range(1, len(newsegs)):
        pa, pb, pf = newsegs[k - 1].split()[1:4]
        ca, cb, cf = newsegs[k].split()[1:4]
        if int(ca) != int(pb) + 1:
            newsegs[k] = '# %d %s %s' % (int(pb) + 1, cb, cf)
    ca, cb, cf = newsegs[-1].split()[1:4]
    assert int(ca) >= 1 and int(cb) == NNEW, (pc, newsegs[-1])
    say('C%s segments rescaled %d->%d, head=%s tail=%s' % (pc, npts, NNEW, newsegs[0], newsegs[-1]))
    outp = dst + '/Breaklines/Pot_C_Piece_%s_Breakline_0.pcd' % pc
    with open(outp, 'w') as fo:
        fo.write('# .PCD v0.7 - Point Cloud Data file format\n')
        fo.write('# %d %d %d\n' % (nseg, NNEW, info))
        for s in newsegs:
            fo.write(s + '\n')
        for h in head9:
            if h.startswith('WIDTH'):
                fo.write('WIDTH %d\n' % NNEW)
            elif h.startswith('POINTS'):
                fo.write('POINTS %d\n' % NNEW)
            else:
                fo.write(h + '\n')
        fo.write('DATA ascii\n')
        for i in range(NNEW):
            fo.write('%.4f %.4f %.4f %.7g %.7g %.7g %.7g\n' % (Li[i, 0], Li[i, 1], Li[i, 2], N[pc][i, 0], N[pc][i, 1], N[pc][i, 2], N[pc][i, 3]))
    say('C%s wrote %s' % (pc, outp))
# 4. byte-proofs
r = cmd('diff <(cd ' + BASE + '/Breaklines && md5sum *) <(cd ' + dst + '/Breaklines && md5sum *)')
say('bundle-Bl diff vs pristine base (expect ONLY C01-C04 Bl_0 differ):\n' + r.stdout.strip())
r2 = cmd('diff -rq ' + BASE + ' ' + dst)
say('recursive diff (expect only 4 Bl_0):\n' + r2.stdout.strip()[:2000])
r4 = cmd('cd ' + dst + ' && find . -type f | sort | xargs md5sum')
open(P204 + '/pota204_C_204_bun_md5.txt', 'w').write(r4.stdout)
say('bun manifest lines=%d' % len(r4.stdout.strip().splitlines()))
r5 = cmd('cd ' + dst + '/Breaklines && md5sum *')
open(P204 + '/pota204_C_204_BL_md5.txt', 'w').write(r5.stdout)
say('BL manifest:\n' + r5.stdout.strip())
say('BUILD DONE')
log.close()
