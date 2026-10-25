
import sys, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RUN = sys.argv[1]
REP = sys.argv[2] if len(sys.argv) > 2 else "rep1"
sys.path.insert(0, os.path.join(RUN, "scripts"))
import measure297 as M

ctx = M.load_context(RUN)
SC = ctx["SC"]
ours = np.asarray(SC.read_pcd(os.path.join(RUN, "out/geom", REP, "ours.Bl0.pcd")), dtype=float)
auth = ctx["auth"]
i, j, arc, meangap, thr = M.worst_stretch(ours, auth)[:5]
print("stretch: our %d..%d arc %.2f mm meangap %.3f threshold %.2f" % (i, j, arc, meangap, thr))

mid = 0.5 * (ours[i] + ours[j])
body = ctx["verts"].mean(0)
fp = M.face_plane(ctx["corp_s0"], mid, body)
c, n = fp["centre"], fp["normal"]
u, v = M.plane_basis(n)
print("face plane: n_pts %d rms %.3f mm normal %s" % (fp["n_pts"], fp["rms"], np.round(n, 4)))

def proj(P):
    Q = np.atleast_2d(P) - c
    return np.stack([Q @ u, Q @ v], axis=1)

# nearest point on their polyline (segment projection), closed loop
def project_on_polyline(P, Q):
    best = (1e9, -1, 0.0)
    A = Q; B = np.roll(Q, -1, axis=0)
    for k in range(len(Q)):
        a, b = A[k], B[k]
        ab = b - a
        t = np.clip(np.dot(P - a, ab) / max(np.dot(ab, ab), 1e-12), 0.0, 1.0)
        p = a + t * ab
        d = np.linalg.norm(P - p)
        if d < best[0]:
            best = (d, k, t)
    return best

steps_a = np.linalg.norm(np.diff(np.vstack([auth, auth[:1]]), axis=0), axis=1)
cum_a = np.concatenate([[0.0], np.cumsum(steps_a)])
perim_a = float(cum_a[-1])
steps_o = np.linalg.norm(np.diff(np.vstack([ours, ours[:1]]), axis=0), axis=1)
print("their perimeter %.2f mm, ours %.2f mm" % (perim_a, steps_o.sum()))

for name, idx in (("our i", i), ("our j", j)):
    d, k, t = project_on_polyline(ours[idx], auth)
    s = cum_a[k] + t * steps_a[k]
    print("  %s (dot %d) projects onto their segment %d at s=%.2f mm of %.2f, perpendicular %.3f mm"
          % (name, idx, k, s, perim_a, d))

# their arc between the two endpoints of the stretch in both directions
d1, k1, t1 = project_on_polyline(ours[i], auth)
d2, k2, t2 = project_on_polyline(ours[j], auth)
s1 = cum_a[k1] + t1 * steps_a[k1]
s2 = cum_a[k2] + t2 * steps_a[k2]
fwd = abs(s2 - s1)
print("their arc between the two projections: one way %.2f mm, the other %.2f mm" % (fwd, perim_a - fwd))
print("their nearest vertex to our i: %d (%.3f mm); to our j: %d (%.3f mm)"
      % (int(np.argmin(np.linalg.norm(auth - ours[i], axis=1))), np.linalg.norm(auth - ours[i], axis=1).min(),
         int(np.argmin(np.linalg.norm(auth - ours[j], axis=1))), np.linalg.norm(auth - ours[j], axis=1).min()))

# ---- picture ----
V2 = proj(ctx["cen"])
sel = (np.abs(V2[:, 0] - proj(mid)[0, 0]) <= 22) & (np.abs(V2[:, 1] - proj(mid)[0, 1]) <= 22)
print("mesh triangles in the 44 mm window:", int(sel.sum()))
T = ctx["verts"][ctx["faces"][sel]]
seg = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]])
P = proj(seg.reshape(-1, 3)).reshape(-1, 2, 2)

fig, ax = plt.subplots(figsize=(13, 11), dpi=110)
from matplotlib.collections import LineCollection
ax.add_collection(LineCollection(P, colors="0.72", linewidths=0.35, zorder=1))

A2 = proj(auth); O2 = proj(ours)
ax.plot(A2[:, 0], A2[:, 1], "-", color="black", lw=1.6, zorder=4, label="authors' Bl0")
ax.plot(O2[:, 0], O2[:, 1], "-", color="#137a13", lw=1.6, zorder=3, label="ours Bl0")

# their short arc between the projections of our stretch ends, by vertex order
lo, hi = sorted((k1, k2))
cand = list(range(lo, hi + 1))
alt = list(range(hi, len(auth))) + list(range(0, lo + 1))
chosen = cand if (cum_a[hi] - cum_a[lo]) <= (perim_a - (cum_a[hi] - cum_a[lo])) else alt
ax.plot(A2[chosen, 0], A2[chosen, 1], "-", color="#c00000", lw=4.0, alpha=0.85, zorder=6,
        label="their arc between our stretch ends (%.2f mm)" % (cum_a[chosen[-1]] - cum_a[chosen[0]] if chosen is cand else perim_a - (cum_a[chosen[0]] - cum_a[chosen[-1]])))
ax.plot(O2[i:j + 1, 0], O2[i:j + 1, 1], "-", color="#1f5fd0", lw=3.6, zorder=6,
        label="our detour %d..%d (%.2f mm)" % (i, j, arc))

ax.plot(A2[:, 0], A2[:, 1], "o", color="black", ms=3.2, zorder=5)
ax.plot(O2[:, 0], O2[:, 1], "o", color="#137a13", ms=3.0, zorder=5, alpha=0.8)
for k in range(len(auth)):
    if k <= 16 or k >= len(auth) - 14:
        ax.annotate(str(k), A2[k], fontsize=7, color="#444", zorder=7,
                    textcoords="offset points", xytext=(3, 3))
for k in range(i - 4, j + 5):
    ax.annotate(str(k), O2[k], fontsize=7, color="#1f5fd0", zorder=7,
                textcoords="offset points", xytext=(-9, -6))

ax.set_aspect("equal"); ax.legend(loc="upper left", fontsize=9)
ax.set_xlabel("u (mm, face plane)"); ax.set_ylabel("v (mm, face plane)")
ax.set_title("Pot_D_Piece_22 Bl0 mouth region: theirs (black) against ours (green)\n"
             "their arc between our stretch ends vs our detour, both lines are on the mesh")
ax.set_xlim(proj(mid)[0, 0] - 22, proj(mid)[0, 0] + 22)
ax.set_ylim(proj(mid)[0, 1] - 22, proj(mid)[0, 1] + 22)
out = os.path.join("/tmp/t297", "diag_mouth.png")
fig.tight_layout(); fig.savefig(out); print("WROTE", out)
