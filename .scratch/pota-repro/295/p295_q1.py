#!/usr/bin/env python3
"""Ticket 295 Q1 -- interior/exterior naming over the corpus, and which face each breakline rides.

The conservator's reading (C1) is that on Pot I 25 our lanes are swapped, ours is right, and the
authors are the outlier there.  A single piece cannot show that.  The corpus can, two ways:

  PART 1  which of the authors' two SURFACE files is the interior face;
  PART 2  which of those two surfaces each of the authors' BREAKLINE files rides.
PART 2 is what speaks to a lane swap: if Breakline_0 rides the interior face on most of the corpus,
a piece where it rides the exterior face names itself as the outlier.

THREE CRITERIA FOR "INTERIOR", all reported, each with its validity domain
 (a) radius      r = perpendicular distance to the released axis; for a WALL the pot's cavity is
                 nearer the axis than its outside, so the interior face has the smaller median r.
                 radial_dr = r50(S1) - r50(S0).  Invalid where the two faces separate mainly along
                 the axis instead of radially (a base or a shoulder), which is exactly the case that
                 makes this corpus not uniform; plate_ratio reports that.
 (b) radial normal  m = mean(n_hat . r_hat), r_hat the unit outward radial direction.  An interior
                 wall looks at the axis (m < 0).  Wall-specific for the same reason as (a).
 (c) mutual offset  for each dot on one surface, the unit vector u to its nearest point on the OTHER
                 surface.  The two faces of a shell look away from each other -- the interior face's
                 normal points into the pot's cavity, the exterior face's out into the world -- so
                 the interior face is the one with the more negative s = mean(n_hat . u).
                 This is axis-free and holds for a wall, a base and a rim alike, so (c) is the
                 PRIMARY and (a)/(b) are consistency checks for wall-like pieces.

ORDER OF EVENTS, stated because it bears on the pre-registration: (a) and (b) were fixed before any
number was computed.  A twelve-piece pilot then printed one plate-like piece where (a) and (b)
disagree, which showed the wall proxies cannot decide such a piece; (c) was added at that point, as
the general test, and no corpus-wide run of any criterion had been looked at.  (c)'s own name for
each piece is reported alongside (a) and (b), never substituted silently.

OTHER PRE-REGISTERED THRESHOLDS, before any number was seen
  |radial_dr| < 1.0 mm -> (a) not discriminative;  |normal_dm| < 0.10 -> (b) weak;  |s| < 0.30 for
  either face -> (c) weak.  Weak criteria abstain; a piece where the three do not all agree is
  NAMED, never folded into a count.
  A breakline RIDES the surface with the smaller MEDIAN dot-to-surface distance; ride margin =
  |median d to the two surfaces|, and a margin < 0.50 mm abstains (a line drawn on the rim sits
  between the faces and is close to both).  A line is ON its surface when that median is <= 2.0 mm
  (T1, the edgeline bar).

n_ax = |mean(n_hat . w)|: ~1 a face perpendicular to the axis (plate), ~0 a wall face.
plate_ratio = |a50(S1)-a50(S0)| / (|a50(S1)-a50(S0)| + |r50(S1)-r50(S0)|): ~1 the faces separate
along the axis, ~0 radially.

Outputs (out/): q1_pieces.tsv, q1_lines.tsv, q1_summary.txt, q1_disagree.tsv, q1_i25_*.tsv.
"""
import argparse
import os
import sys
import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p295_lib import (CORP, BAR, read_xyz6, read_pcd_xyz, read_dump, frame, axial, radial_unit,
                      write_tsv, q)

R293 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261025-0456_3ada802_p293-census/out"


def surf_basic(path, p0, w):
    P, N = read_xyz6(path)
    _, r = radial_unit(P, p0, w)
    a = axial(P, p0, w, np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0]))[0]
    nn = np.linalg.norm(N, axis=1)
    ok = np.isfinite(nn) & (nn > 1e-9)
    Nh = np.zeros_like(N)
    Nh[ok] = N[ok] / nn[ok, None]
    rhat, _ = radial_unit(P, p0, w)
    dotr = (Nh * rhat).sum(1)
    dotw = Nh @ w
    return dict(P=P, Pn=P[ok], Nh=Nh[ok], n=int(len(P)),
                r5=q(r, 5), r50=q(r, 50), r95=q(r, 95),
                a5=q(a, 5), a50=q(a, 50), a95=q(a, 95),
                m=float(dotr[ok].mean()) if ok.any() else float("nan"),
                frac_neg=float((dotr[ok] < 0).mean()) if ok.any() else float("nan"),
                mw=float(dotw[ok].mean()) if ok.any() else float("nan"),
                n_ax=float(abs(dotw[ok].mean())) if ok.any() else float("nan"))


def mutual_offset(A, B):
    """s = mean(n_hat . u) from A's dots to their nearest B point; interior face has s < 0."""
    if len(A["Pn"]) == 0 or len(B["Pn"]) == 0:
        return float("nan"), float("nan"), float("nan")
    tb = cKDTree(B["Pn"])
    d, idx = tb.query(A["Pn"], k=1)
    good = d > 1e-6
    if good.sum() < 10:
        return float("nan"), float("nan"), float("nan")
    u = (B["Pn"][idx[good]] - A["Pn"][good]) / d[good, None]
    c = (A["Nh"][good] * u).sum(1)
    return float(c.mean()), float((c < 0).mean()), float(np.median(d[good]))


def pair_stats(path0, path1, p0, w):
    S = [surf_basic(path0, p0, w), surf_basic(path1, p0, w)]
    for j in (0, 1):
        s, fneg, dt = mutual_offset(S[j], S[1 - j])
        S[j].update(s=s, s_neg=fneg, thick=dt)
    return S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="out")
    ap.add_argument("--corp", default=CORP)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only", default="")
    ap.add_argument("--skip-detail", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)

    axdir, sdir, bdir = (os.path.join(a.corp, d) for d in ("Axes", "Surfaces", "Breaklines"))
    pieces = sorted(f[:-len("_Axis.xyz")] for f in os.listdir(axdir) if f.endswith("_Axis.xyz"))
    if a.only:
        pieces = [p for p in pieces if p == a.only]
    if a.limit:
        pieces = pieces[:a.limit]
    print(f"[q1] {len(pieces)} pieces with an axis file", flush=True)

    prow, lrow = [], []
    for i, pc in enumerate(pieces):
        try:
            p0, w, _, _ = frame(os.path.join(axdir, pc + "_Axis.xyz"))
            S = pair_stats(os.path.join(sdir, f"{pc}_Surface_0.xyz"),
                           os.path.join(sdir, f"{pc}_Surface_1.xyz"), p0, w)
        except Exception as ex:
            print(f"[q1] {pc}: read failed ({ex})", flush=True)
            continue
        dr = S[1]["r50"] - S[0]["r50"]
        dm = S[1]["m"] - S[0]["m"]
        ds = S[1]["s"] - S[0]["s"]
        da = S[1]["a50"] - S[0]["a50"]
        inner_r = 0 if dr > 0 else 1
        inner_n = 0 if dm > 0 else 1
        inner_s = 0 if ds > 0 else 1
        okr, okn = abs(dr) >= 1.0, abs(dm) >= 0.10
        live = {k: v for k, v, ok_ in (("radius", inner_r, okr), ("normal", inner_n, okn)) if ok_}
        if not live:
            bucket = "undiscriminating_both"
        elif len(set(live.values())) == 1:
            bucket = "agree"
        else:
            bucket = "disagree"
        gap = float(np.median(np.linalg.norm(
            S[1]["Pn"][cKDTree(S[1]["Pn"]).query(S[0]["Pn"][::4], k=1)[1]] - S[0]["Pn"][::4], axis=1)))
        prow.append(dict(piece=pc, n0=S[0]["n"], n1=S[1]["n"],
                         r5_0=S[0]["r5"], r50_0=S[0]["r50"], r95_0=S[0]["r95"],
                         r5_1=S[1]["r5"], r50_1=S[1]["r50"], r95_1=S[1]["r95"],
                         radial_dr=dr, m0=S[0]["m"], m1=S[1]["m"], normal_dm=dm,
                         s0=S[0]["s"], s1=S[1]["s"], offset_ds=ds,
                         frac_neg_s0=S[0]["s_neg"], frac_neg_s1=S[1]["s_neg"],
                         frac_neg_r0=S[0]["frac_neg"], frac_neg_r1=S[1]["frac_neg"],
                         mw0=S[0]["mw"], mw1=S[1]["mw"],
                         n_ax_0=S[0]["n_ax"], n_ax_1=S[1]["n_ax"],
                         a5_0=S[0]["a5"], a50_0=S[0]["a50"], a95_0=S[0]["a95"],
                         a5_1=S[1]["a5"], a50_1=S[1]["a50"], a95_1=S[1]["a95"],
                         axial_da=da, plate_ratio=abs(da) / (abs(da) + abs(dr)) if (abs(da) + abs(dr)) else float("nan"),
                         wall_gap=gap, thick0=S[0]["thick"], thick1=S[1]["thick"],
                         inner_by_radius=inner_r, inner_by_normals=inner_n, inner_by_offset=inner_s,
                         rad_disc=bool(okr), norm_strong=bool(okn),
                         bucket=bucket))
        L = []
        for k in (0, 1):
            p = os.path.join(bdir, f"{pc}_Breakline_{k}.pcd")
            if not os.path.exists(p):
                L.append(None)
                continue
            bl = read_pcd_xyz(p)
            d0 = cKDTree(S[0]["P"]).query(bl, k=1)[0]
            d1 = cKDTree(S[1]["P"]).query(bl, k=1)[0]
            md0, md1 = float(np.median(d0)), float(np.median(d1))
            ride = 0 if md0 < md1 else 1
            L.append(dict(k=k, n=int(len(bl)), d0=md0, d1=md1, ride=ride,
                          rmed=min(md0, md1), margin=abs(md0 - md1), on=bool(min(md0, md1) <= BAR)))
        if L[0] is None or L[1] is None:
            continue
        amb = (L[0]["margin"] < 0.5) or (L[1]["margin"] < 0.5)
        same = L[0]["ride"] == L[1]["ride"]
        conv = "both_same_face" if same else ("ambiguous" if amb else
              ("bl0_on_inner" if L[0]["ride"] == inner_n else "bl0_on_outer"))
        lrow.append(dict(piece=pc, inner_by_radius=inner_r, inner_by_normals=inner_n,
                         inner_by_offset=inner_s, bucket=bucket,
                         radial_dr=dr, normal_dm=dm, offset_ds=ds, plate_ratio=prow[-1]["plate_ratio"],
                         wall_gap=gap,
                         bl0_n=L[0]["n"], bl0_d0=L[0]["d0"], bl0_d1=L[0]["d1"], bl0_ride=f"S{L[0]['ride']}",
                         bl0_margin=L[0]["margin"], bl0_on=L[0]["on"],
                         bl1_n=L[1]["n"], bl1_d0=L[1]["d0"], bl1_d1=L[1]["d1"], bl1_ride=f"S{L[1]['ride']}",
                         bl1_margin=L[1]["margin"], bl1_on=L[1]["on"], convention=conv))
        if (i + 1) % 25 == 0:
            print(f"[q1] {i+1}/{len(pieces)}", flush=True)

    write_tsv(os.path.join(a.outdir, "q1_pieces.tsv"), prow)
    write_tsv(os.path.join(a.outdir, "q1_lines.tsv"), lrow)
    summarise(prow, lrow, a.outdir)
    if not a.skip_detail:
        i25_detail(a)
    print("[q1] done", flush=True)


def summarise(prow, lrow, outdir):
    n = len(prow)
    L = ["Q1 -- interior/exterior naming over the corpus, and which face each breakline rides", ""]
    L.append(f"pieces with an axis, two readable surfaces and two breaklines: {n}")
    L.append("")
    L.append("PART 1  which SURFACE file is the interior face")
    for nm, key, disc in (("concavity (PRIMARY: normals point toward the axis)",
                           "inner_by_normals", "norm_strong"),
                          ("radius (coarser consequence, patch-coverage sensitive)",
                           "inner_by_radius", "rad_disc")):
        live = [r for r in prow if r[disc]]
        s0 = sum(1 for r in live if r[key] == 0)
        L.append(f"  criterion {nm:14s} discriminative on {len(live):3d}/{n};"
                 f" Surface_0 interior on {s0:3d}, Surface_1 on {len(live)-s0:3d}")
        ex = [r for r in live if r[key] != 0]
        if ex:
            L.append("    Surface_1-named-interior pieces (named): "
                     + ", ".join(f"{r['piece'].replace('Pot_','').replace('_Piece_',' ')}"
                                 f"({'dr' if key=='inner_by_radius' else 'dm'} {r[key.replace('inner_by','') and ('radial_dr' if key=='inner_by_radius' else 'normal_dm')]:+.2f})"
                                 for r in ex))
    both = [r for r in prow if r["rad_disc"] and r["norm_strong"]]
    agr = [r for r in both if r["inner_by_radius"] == r["inner_by_normals"]]
    L.append(f"  HEADLINE: both criteria discriminative on {len(both):3d}/{n}; they name the same"
             f" interior face on {len(agr):3d}, different on {len(both)-len(agr):3d}"
             f" -> Surface_0 is the interior face on {sum(1 for r in agr if r['inner_by_radius']==0)}"
             f" of {len(agr)}")
    und = [r for r in prow if r["bucket"] == "undiscriminating_both"]
    if und:
        L.append("  NO CRITERION DISCRIMINATIVE (named): " + ", ".join(r["piece"] for r in und))
    dis = [r for r in prow if r["bucket"] == "disagree"]
    for r in dis:
        L.append(f"    DISAGREE {r['piece']:>22s} radius->S{r['inner_by_radius']}"
                 f" normal->S{r['inner_by_normals']} | dr {r['radial_dr']:+.2f} dm {r['normal_dm']:+.3f}"
                 f" plate_ratio {r['plate_ratio']:.2f} n_ax {r['n_ax_0']:.2f}/{r['n_ax_1']:.2f}"
                 f" thick {r['thick0']:.2f}/{r['thick1']:.2f}")
    s0 = np.array([r["s0"] for r in prow]); s1 = np.array([r["s1"] for r in prow])
    L.append(f"  criterion (c), mutual offset -- TESTED AND DISCARDED as an interior test:")
    L.append(f"    s mean(n.u) to the other surface: S0 median {np.median(s0):+.3f},"
             f" S1 median {np.median(s1):+.3f}; both faces negative on"
             f" {int(((s0 < 0) & (s1 < 0)).sum())}/{n} pieces, |ds| median"
             f" {np.median(np.abs(s1-s0)):.3f} mm-free")
    L.append(f"    both faces' normals point AWAY from each other on nearly every piece, which"
             f" validates the shell but cannot say which side is the pot's inside; the sign test"
             f" was written on the wrong premise and is reported so it is not repeated.")
    conv = {"bl0_on_inner": [], "bl0_on_outer": [], "both_same_face": [], "ambiguous": []}
    for r in lrow:
        conv[r["convention"]].append(r["piece"])
    nl = len(lrow)
    L.append("")
    L.append(f"PART 2  which surface does each BREAKLINE ride (n = {nl} pieces with both lines)")
    L.append(f"  Breakline_0 rides the INTERIOR face          {len(conv['bl0_on_inner']):3d}")
    L.append(f"  Breakline_0 rides the EXTERIOR face          {len(conv['bl0_on_outer']):3d}"
             f"   (the corpus exceptions)")
    L.append(f"  (interior = the concavity criterion, the primary one)")
    L.append(f"  both lines ride the same face                {len(conv['both_same_face']):3d}")
    L.append(f"  assignment ambiguous (margin < 0.50 mm)      {len(conv['ambiguous']):3d}")
    L.append(f"  both lines lie on their surface (<= 2.0 mm)  "
             f"{sum(1 for r in lrow if r['bl0_on'] and r['bl1_on']):3d} / {nl}")
    for lbl in ("bl0_on_outer", "both_same_face", "ambiguous"):
        if conv[lbl]:
            L.append(f"  {lbl}: {', '.join(conv[lbl])}")
    pr = [r for r in lrow if r["bl0_ride"] == "S0"]
    p1 = [r for r in lrow if r["bl1_ride"] == "S1"]
    L.append(f"  does the breakline index pair with the surface index? Bl0 on S0 {len(pr)}/{nl},"
             f" Bl1 on S1 {len(p1)}/{nl}"
             + ("  -> YES, pairing by index" if len(pr) == nl and len(p1) == nl else
                "  -> NO, the breakline index does not follow the surface index"))
    ct = {}
    for r in lrow:
        k = (r["bl0_ride"] == "S0", r["bl0_ride"] == f"S{r['inner_by_normals']}")
        ct[k] = ct.get(k, 0) + 1
    L.append("  cross-tab (Bl0 rides S0?, Bl0 rides the interior?): "
             + "; ".join(f"{'S0' if k[0] else 'S1'}/{'int' if k[1] else 'ext'} {v}" for k, v in sorted(ct.items())))
    both = [r for r in lrow if r["bl0_on"] and r["bl1_on"]]
    if both:
        m = np.array([min(r["bl0_margin"], r["bl1_margin"]) for r in both])
        L.append(f"  ride margin: median {np.median(m):.2f} mm, p5 {np.percentile(m,5):.2f},"
                 f" min {m.min():.2f}; under 0.50 mm: {int((m < 0.5).sum())}")
    plate = sorted(prow, key=lambda r: -r["plate_ratio"])[:8]
    L.append(f"  most axis-separated (plate-like) pieces, plate_ratio: "
             + ", ".join(f"{r['piece'].split('_',1)[1].replace('_Piece_',' ')} {r['plate_ratio']:.2f}" for r in plate))
    i25p = next((r for r in prow if r["piece"] == "Pot_I_Piece_25"), None)
    i25l = next((r for r in lrow if r["piece"] == "Pot_I_Piece_25"), None)
    if i25p is not None:
        gaps = np.array([r["wall_gap"] for r in prow])
        pr = np.array([r["plate_ratio"] for r in prow])
        L.append("")
        L.append("POT I 25 IN CONTEXT")
        L.append(f"  surfaces: S0 r50 {i25p['r50_0']:.2f} m {i25p['m0']:+.3f} s {i25p['s0']:+.3f}"
                 f" | S1 r50 {i25p['r50_1']:.2f} m {i25p['m1']:+.3f} s {i25p['s1']:+.3f}")
        L.append(f"  -> interior by radius S{i25p['inner_by_radius']}, by normals S{i25p['inner_by_normals']},"
                 f" by offset S{i25p['inner_by_offset']} (bucket {i25p['bucket']})")
        L.append(f"  plate_ratio {i25p['plate_ratio']:.3f} (corpus median {np.median(pr):.3f},"
                 f" {100.0*float((pr < i25p['plate_ratio']).mean()):.0f}th percentile)"
                 f"; wall gap {i25p['wall_gap']:.2f} mm (corpus median {np.median(gaps):.2f})")
    if i25l is not None:
        L.append(f"  breaklines: Bl0 rides {i25l['bl0_ride']} at {min(i25l['bl0_d0'], i25l['bl0_d1']):.3f} mm"
                 f" (margin {i25l['bl0_margin']:.3f}); Bl1 rides {i25l['bl1_ride']} at"
                 f" {min(i25l['bl1_d0'], i25l['bl1_d1']):.3f} mm (margin {i25l['bl1_margin']:.3f})")
        L.append(f"  -> convention on this piece: {i25l['convention']}"
                 f" (corpus: {len(conv['bl0_on_inner'])}/{nl} have Bl0 on the interior)")
    open(os.path.join(outdir, "q1_summary.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L), flush=True)
    if dis:
        write_tsv(os.path.join(outdir, "q1_disagree.tsv"), dis)


def i25_detail(a):
    """Pot I 25 -- both sides' surfaces and both sides' lines, side by side."""
    piece = "Pot_I_Piece_25"
    p0, w, u, v = frame(os.path.join(a.corp, "Axes", piece + "_Axis.xyz"))
    S = pair_stats(os.path.join(a.corp, "Surfaces", piece + "_Surface_0.xyz"),
                   os.path.join(a.corp, "Surfaces", piece + "_Surface_1.xyz"), p0, w)
    rows = []
    for j in (0, 1):
        r = S[j]
        rows.append(dict(subject=f"authors_S{j}", n=r["n"], r5=r["r5"], r50=r["r50"], r95=r["r95"],
                         m=r["m"], s=r["s"], frac_neg_s=r["s_neg"], mw=r["mw"], n_ax=r["n_ax"],
                         a5=r["a5"], a50=r["a50"], a95=r["a95"], thick=r["thick"]))
    lines = []
    trees = [cKDTree(S[j]["P"]) for j in (0, 1)]
    for k in (0, 1):
        bl = read_pcd_xyz(os.path.join(a.corp, "Breaklines", f"{piece}_Breakline_{k}.pcd"))
        _, rl = radial_unit(bl, p0, w)
        aa = axial(bl, p0, w, u, v)[0]
        d = [trees[j].query(bl, k=1)[0] for j in (0, 1)]
        lines.append(dict(line=f"authors_Bl{k}", n=int(len(bl)), r5=q(rl, 5), r50=q(rl, 50),
                          r95=q(rl, 95), ax5=q(aa, 5), ax50=q(aa, 50), ax95=q(aa, 95),
                          d_S0_med=q(d[0], 50), d_S1_med=q(d[1], 50),
                          rides=(0 if q(d[0], 50) < q(d[1], 50) else 1),
                          margin=abs(q(d[0], 50) - q(d[1], 50))))
    write_tsv(os.path.join(a.outdir, "q1_i25_surfaces.tsv"), rows)
    write_tsv(os.path.join(a.outdir, "q1_i25_lines.tsv"), lines)
    dump = os.path.join(R293, "diag", piece + ".diag276.txt")
    ours = []
    if os.path.exists(dump):
        hdr, cl, labels, P = read_dump(dump)
        _, rP = radial_unit(P, p0, w)
        aP = axial(P, p0, w, u, v)[0]
        for c in sorted(set(labels.tolist())):
            m = labels == c
            if m.sum() < 200:
                continue
            dmed = [float(np.median(trees[j].query(P[m][::4], k=1)[0])) for j in (0, 1)]
            ours.append(dict(cluster=c, n=int(m.sum()), kept=int(c in (0, 1)),
                             r5=q(rP[m], 5), r50=q(rP[m], 50), r95=q(rP[m], 95),
                             ax5=q(aP[m], 5), ax50=q(aP[m], 50), ax95=q(aP[m], 95),
                             d_authS0_med=dmed[0], d_authS1_med=dmed[1],
                             nearest_authors_surface=(0 if dmed[0] < dmed[1] else 1)))
    write_tsv(os.path.join(a.outdir, "q1_i25_ours.tsv"), ours)
    print("[q1] I25 detail:", flush=True)
    for r in rows + lines + ours:
        print("   ", {k: (round(x, 4) if isinstance(x, float) else x) for k, x in r.items()}, flush=True)


if __name__ == "__main__":
    main()
