
import sys, os
import numpy as np
from scipy.spatial import cKDTree
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path

RUN = sys.argv[1]
sys.path.insert(0, os.path.join(RUN, "scripts"))
import measure297 as M

ctx = M.load_context(RUN)
SC = ctx["SC"]
auth = ctx["auth"]
ours = np.asarray(SC.read_pcd(os.path.join(RUN, "out/geom/rep1/ours.Bl0.pcd")), dtype=float)
T1, T2, T3 = ctx["T1"], ctx["T2"], ctx["T3"]
cen, nrm, area = ctx["cen"], ctx["nrm"], ctx["area"]

i, j, mean_gap, arc, thr = M.worst_stretch(ours, auth)
ai = int(np.argmin(((auth - ours[i]) ** 2).sum(1)))
aj = int(np.argmin(((auth - ours[j]) ** 2).sum(1)))
n_a = len(auth); fwd = (aj - ai) % n_a
idx_chord = ([(ai + k) % n_a for k in range(fwd + 1)] if fwd <= n_a - fwd
             else [(ai - k) % n_a for k in range(n_a - fwd + 1)])
other = set(range(n_a)) - set(idx_chord)
in_chord = np.zeros(n_a, bool); in_chord[idx_chord] = True

mid = 0.5 * (ours[i] + ours[j])
pl = M.face_plane(ctx["corp_s0"], mid, ctx["corp_s0"].mean(0))
c, n = pl["centre"], pl["normal"]
u, v = M.plane_basis(n)

lines = {
    "their chord dots (%d)" % in_chord.sum(): auth[in_chord],
    "their rest (%d)" % (~in_chord).sum(): auth[~in_chord],
    "our detour (%d)" % (j - i + 1): ours[i:j + 1],
    "our rest (%d)" % (len(ours) - (j - i + 1)): np.vstack([ours[:i], ours[j + 1:]]),
}

# nearest mesh triangle to each dot, by centroid (a local probe, 1 mm scale)
tk = cKDTree(cen)
out = []
def add(s):
    out.append(s); print(s)

add("SECONDARY (not part of the pre-registered rule; reported beside it)")
add("")
add("A. the surface each line's own dots sit on: nearest mesh triangle's tilt off the face normal")
add("   %-26s %6s %8s %8s %8s %8s %8s" % ("line", "n", "p25", "median", "p75", "<=20deg", ">=45deg"))
for name, P in lines.items():
    _, ti = tk.query(P)
    t = M.tilted(nrm[ti], n)
    add("   %-26s %6d %8.1f %8.1f %8.1f %7.1f%% %7.1f%%"
        % (name, len(P), np.percentile(t, 25), np.median(t), np.percentile(t, 75),
           100.0 * (t <= 20).mean(), 100.0 * (t >= 45).mean()))

add("")
add("B. distance from each line's dots to the authors' OWN interior face (their labelled Surface_0)")
fs0 = cKDTree(ctx["corp_s0"])
add("   %-26s %8s %8s %8s %8s" % ("line", "median", "p75", "p95", "max"))
for name, P in lines.items():
    d = fs0.query(P)[0]
    add("   %-26s %8.3f %8.3f %8.3f %8.3f" % (name, np.median(d), np.percentile(d, 75),
                                               np.percentile(d, 95), d.max()))

add("")
add("C. the enclosed patch, restricted to the strip near the face plane (|offset| <= 15 mm),")
add("   because the full polygon also wraps the body's far side (offsets down to -36.7 mm)")
det = ours[i:j + 1][::-1]
poly = np.vstack([auth[idx_chord], det])
pq = np.column_stack([(poly - c) @ u, (poly - c) @ v])
path = Path(pq)
cq = np.column_stack([(cen - c) @ u, (cen - c) @ v])
inside = path.contains_points(cq)
off = (cen - c) @ n
tilt = M.tilted(nrm, n)
near = inside & (np.abs(off) <= 15.0)
for tag, m in (("full polygon", inside), ("near-plane strip", near)):
    w = area[m]; t = tilt[m]
    add("   %-18s tris %5d  area %8.2f mm2  >=45deg %6.2f%%  <=20deg %6.2f%%  within 1mm + <=20deg: %6.2f mm2"
        % (tag, int(m.sum()), w.sum(), 100.0 * w[t >= 45].sum() / w.sum(),
           100.0 * w[t <= 20].sum() / w.sum(), w[(t <= 20) & (np.abs(off[m]) <= 1.0)].sum()))

add("")
add("D. the two routes' lengths over the same stretch")
add("   their dots %d..%d: %d dots along their order, %.2f mm of their line, ends %.2f mm apart"
    % (idx_chord[0], idx_chord[-1], len(idx_chord),
       np.linalg.norm(np.diff(auth[idx_chord], axis=0), axis=1).sum(),
       np.linalg.norm(auth[idx_chord][-1] - auth[idx_chord][0])))
add("   our detour %d..%d: %d dots, %.2f mm of our line, ends %.2f mm apart"
    % (i, j, j - i + 1, np.linalg.norm(np.diff(ours[i:j + 1], axis=0), axis=1).sum(),
       np.linalg.norm(ours[j] - ours[i])))
add("   their line lies within 2 mm of ours on %d of its %d dots: the two loops coincide"
    % (int((cKDTree(ours).query(auth)[0] <= 2.0).sum()), n_a))
add("   everywhere except this corner")

txt = "\n".join(out) + "\n"
open(os.path.join(RUN, "out", "measure297.secondary.txt"), "w").write(txt)
print("WROTE", os.path.join(RUN, "out", "measure297.secondary.txt"))
