"""POTA-176 build: reclaimed C01 TRUE walk (439-dot, 176 slot-0) on 98 SXC base.
Port of p145_build.py (141-build port). Veto-free chain: vehicle bffefb6
(Pot-A cure only) + laptop-numpy walk; veto patch lives only in the
lead-owned relay worktree and is asserted ABSENT here (build log + sbatch)."""
import numpy as np, os, hashlib, shutil, sys
P176 = '/data/gpfs/projects/punim2657/pota176_repro'
P98 = '/data/gpfs/projects/punim2657/pota98_repro/prep/pota98_bundle_C_SXC/SfS_pp'
P39 = '/data/gpfs/projects/punim2657/pota39_repro/prep/pota39_bundle_C/SfS_pp'
SRC = '/data/gpfs/projects/punim2657/pota39_repro/asm'
STAGE = P176 + '/stage'
os.makedirs(P176 + '/prep', exist_ok=True)
log = open(P176 + '/p176_build.txt', 'w')
def say(s):
    print(s, flush=True); log.write(s + '\n')
def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()
def cmd(c):
    import subprocess
    return subprocess.run(c, shell=True, capture_output=True, text=True)
# 0. veto-absence evidence (record; sbatch asserts hard)
r0 = cmd('git -C ' + SRC + ' log -1 --format=%H %ci')
say('vehicle HEAD: ' + r0.stdout.strip())
rv = cmd('grep -ril "FACE VETO\\|face_veto" ' + SRC + '/class/ 2>/dev/null')
say('veto grep: ' + ('ABSENT-OK' if not rv.stdout.strip() else 'PRESENT-STOP ' + rv.stdout.strip()))
assert not rv.stdout.strip(), 'veto content in vehicle SRC -- STOP'
# 1. walk reproduce-or-stop (byte-verify staged transfer from laptop)
WALK_MD5 = '5f902355dd99a4fe35885bf596193733'
wf = STAGE + '/p176_C01_TRUE_walk.npy'
assert md5(wf) == WALK_MD5, 'walk transfer corrupt -- STOP'
L = np.load(wf)
assert L.shape == (439, 3), L.shape
st = np.sqrt(((L[1:] - L[:-1]) ** 2).sum(-1))
say('WALK GREEN: 439x3 md5-ok, steps max=%.2f median=%.2f n>5mm=%d n>=40mm=%d' % (st.max(), np.median(st), int((st > 5).sum()), int((st >= 40).sum())))
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
# 2. normals from nearest fresh C01 content (Bl_0 U Bl_1, same frame per frame test)
A0 = load_pcd7(P39 + '/Breaklines/Pot_C_Piece_01_Breakline_0.pcd')
A1 = load_pcd7(P39 + '/Breaklines/Pot_C_Piece_01_Breakline_1.pcd')
A = np.vstack([A0, A1])
d = np.sqrt(((L[:, None, :3] - A[None, :, :3]) ** 2).sum(-1))
nn = d.argmin(1); nd = d.min(1)
say('fresh-content NN: med=%.2f max=%.2f n>5mm=%d (donor Bl_0 n=%d + Bl_1 n=%d)' % (np.median(nd), nd.max(), int((nd > 5).sum()), len(A0), len(A1)))
assert float(np.median(nd)) < 5.0, 'frame mismatch walk-vs-donor -- STOP'
N = A[nn][:, 3:7]
# 3. template header from fresh C01 Bl_0, rescale 13 segs 402 -> 439
seg1, nseg, npts, info, segs, head9 = load_head(P39 + '/Breaklines/Pot_C_Piece_01_Breakline_0.pcd')
assert (nseg, npts, info) == (13, 402, 0), (nseg, npts, info)
bounds = []
for s in segs:
    a, b, f = s.split()[1:4]
    bounds.append((int(a), int(b), int(f)))
assert bounds[0][0] == 1 and bounds[-1][1] == 402
NNEW = 439
newsegs = []
for k, (a, b, f) in enumerate(bounds):
    na = int(round((a - 1) / 402 * NNEW)) + 1
    nb = int(round(b / 402 * NNEW))
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
assert int(ca) >= 1 and int(cb) == NNEW, newsegs[-1]
say('segments rescaled 402->439, head=%s tail=%s' % (newsegs[0], newsegs[-1]))
# 4. copy 98 SXC base, install reclaimed C01 Bl_0 (Bl_1 untouched, C02/C03/C04 = 98-SXC)
base = '/data/gpfs/projects/punim2657/pota98_repro/prep/pota98_bundle_C_SXC'
dst = P176 + '/prep/pota176_bundle_C_176'
if os.path.exists(dst):
    shutil.rmtree(dst)
shutil.copytree(base, dst)
outp = dst + '/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd'
with open(outp, 'w') as f:
    f.write('# .PCD v0.7 - Point Cloud Data file format\n')
    f.write('# %d %d %d\n' % (nseg, NNEW, info))
    for s in newsegs:
        f.write(s + '\n')
    for h in head9:
        if h.startswith('WIDTH'):
            f.write('WIDTH %d\n' % NNEW)
        elif h.startswith('POINTS'):
            f.write('POINTS %d\n' % NNEW)
        else:
            f.write(h + '\n')
    f.write('DATA ascii\n')
    for i in range(NNEW):
        f.write('%.4f %.4f %.4f %.7g %.7g %.7g %.7g\n' % (L[i, 0], L[i, 1], L[i, 2], N[i, 0], N[i, 1], N[i, 2], N[i, 3]))
say('wrote %s' % outp)
# 5. byte-proofs
r = cmd('diff <(cd ' + P98 + '/Breaklines && md5sum *) <(cd ' + dst + '/SfS_pp/Breaklines && md5sum *)')
say('bundle-Bl diff vs 98-SXC (expect ONLY C01-Bl_0 differs):\n' + r.stdout.strip())
r2 = cmd('diff -rq ' + base + '/SfS_pp ' + dst + '/SfS_pp')
say('recursive diff (expect only C01-Bl_0):\n' + r2.stdout.strip()[:2000])
r3 = cmd('cd ' + P98 + '/Breaklines && md5sum -c /data/gpfs/projects/punim2657/pota98_repro/pota98_C_SXC_BL_md5.txt')
bad = [l for l in r3.stdout.splitlines() if 'OK' not in l]
say('98-SXC intact check: %s' % ('ALL-OK' if not bad else 'CHANGED: %s' % bad))
for ff in ['Breaklines/Pot_C_Piece_01_Breakline_0.pcd', 'Breaklines/Pot_C_Piece_01_Breakline_1.pcd']:
    say('fresh C01 %s md5=%s' % (ff.split('/')[-1], md5(P39 + '/' + ff)))
r4 = cmd('cd ' + dst + '/SfS_pp && find . -type f | sort | xargs md5sum')
open(P176 + '/pota176_C_176_bun_md5.txt', 'w').write(r4.stdout)
say('bun manifest lines=%d' % len(r4.stdout.strip().splitlines()))
r5 = cmd('cd ' + dst + '/SfS_pp/Breaklines && md5sum *')
open(P176 + '/pota176_C_176_BL_md5.txt', 'w').write(r5.stdout)
say('BL manifest:\n' + r5.stdout.strip())
say('BUILD DONE')
log.close()
