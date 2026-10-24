# 286 — H 02 and H 10 hold both a rim and a base: where does the line go wrong?

Status: results-in
Answers: none
Working in: none

## Why this ticket

The conservator, 2026-10-24: **"H 02 and H 10 contain both rim and base. Can you tell me what went
wrong with it? Ideally picture show: surface, our edgeline, author edgeline."**

Both pieces look like the Pot C 03 case measured in ticket 279 — a piece carrying a base face as
well as a wall — but ticket 279's complete-disc rule flagged only Pot A 01, Pot C 03 and Pot J 03
across 163 pieces, and on these two it reported:

- Pot H 02: no complete disc (largest candidate c0 17091 points, `|n . axis|` 0.983, only 13 of 36
  angular bins filled, edge_cv 0.424).
- Pot H 10: c0 4484 points fills 36 of 36 bins but edge_cv 0.459 — ragged, so not a disc by the rule.

So the rule's *verdict* excluded them while the conservator's eye says the bases are there. The rule
was only ever a screening device; its thresholds are not evidence about these pieces. What is missing
is the direct comparison: the surface we kept, the line we exported, and the authors' line, on one
picture.

## What is already measured (do not re-derive; cite and use)

Lane scores at the shipped defaults on the frozen theta-3.4 sheets (ticket 280 Phase 0, binary
62ddd28f4476e9cdf5b27cf0ee01c2f0):

| lane | n | med mm | cov ours->author | jumps | author-side cov |
|---|---|---|---|---|---|
| H02 Bl0 | 152 | 0.582 | 100.00 | 0 | - |
| H02 Bl1 | 138 | 0.864 | 73.19 | 0 | 74.45 |
| H10 Bl0 | 98 | 0.661 | 100.00 | 0 | - |
| H10 Bl1 | 92 | 0.641 | 72.83 | 0 | 77.27 |

- Frozen sheets (reuse these, do NOT re-mesh): Pot H 02 Surface_0 md5 9de492c9..., Surface_1
  638a2219...; Pot H 10 Surface_0 07ba2430..., Surface_1 ee79326e... (full md5s in the 280 run's
  run.json).
- Ticket 280 Phase 1: H02 Bl1 has 35 uncovered author dots, all at 0.037-0.485 mm from a surface and
  all nearer Surface_1; H10 Bl1 has 20 uncovered, 19 nearer Surface_1. No detector radius/angle
  setting recovers them (16 settings swept); the max angular gap at those dots is 8.9 / 9.9 deg
  median against the 108 deg boundary threshold, i.e. they sit in smooth interior.
- Ticket 281: on H02 all 35 lie interior to kept cluster 1 and no other cluster comes within rho_d
  1.0 mm of it (nearest 1.3712 mm), so the merge cannot reach it; the rim there is a real 14.13 deg
  fold crossed in 3.23 deg median steps, 52.7% of them at or below the 3.4 deg growth gate. On H10,
  15 of the 19 map to dropped cluster 5 — a 629-point ribbon (21.66 x 3.20 x 1.76 mm at 45.0 deg to
  the axis) standing 0.3191 mm from kept cluster 1.
- Ticket 283: H10's ribbon was refused by the merge's Step 2 on rho_n — `nrm=0.9315` (21.33 deg)
  against 0.9500 (18.19 deg). Curvature passed. Step 3 was never reached, so this is not the Step 3
  defect measured on Pot C 03 / C 01.

## Phase 1 — the pictures (the deliverable the conservator asked for)

One PNG per lane (H02 Bl0, H02 Bl1, H10 Bl0, H10 Bl1), each containing:

1. the two kept surfaces as point clouds, distinguishable (e.g. Surface_0 one colour, Surface_1
   another), thin and small markers;
2. our exported breakline for that lane, thick and bright;
3. the authors' reference breakline for that lane, thick and black;
4. panels: a 3D view plus X-Y, X-Z, Y-Z;
5. a zoom on the failing stretch for the two Bl1 lanes (H02 indices 32-66, H10 40-58), where the
   author's dots have no counterpart within 2 mm.

Pull the PNGs to the laptop under `artifacts/pota286/` so the conservator can open them, and list
every path. Keep each file under ~2 MB.

## Phase 2 — the measurement behind the picture

1. **Which face does the authors' line belong to?** For every author dot on each of the four lanes:
   distance to Surface_0 and to Surface_1, its normal agreement with each, and thus whether their
   line is the boundary of a face (a) we kept as a surface, (b) we kept inside the other surface's
   points but not as a separate surface, or (c) we dropped as a cluster.
2. **Which face does our line belong to**, by the same test.
3. **Base or wall?** For every cluster on each piece (not only the top two), report ticket 279's disc
   numbers as numbers: points, angular bins filled, `l3/l1`, edge_cv, axial spread, `|n . axis|`.
   Say plainly, per piece, whether a base face exists and where it ended up (kept surface / dropped
   cluster / never clustered).
4. **Classification per lane**, using the classes already on record: (K) partition mismatch — their
   line is the boundary of a face we never kept as a surface; (S) same face, different contour —
   extent; (W) same contour, the walk lost it. Give the number that decides it.

## Constraints

- Mesh stage: do not re-run. The sheets are frozen, and the mesh RNG
  (`mesh_processing_headless.cpp:1526-1527`, `std::random_device rd`) makes a re-mesh a different
  surface.
- If the edge stage has to be re-run for an export, build from main HEAD and record the binary md5;
  do not use `build.sh --target nurbs` (ticket 282: it compiles the pre-247 duplicate).
- No code change, no default change, no retuning of any threshold. This ticket produces pictures and
  a classification.
- Copy the ticket and every evidence path into a run directory on Spartan
  (`/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHmm>_<git7>_<tag>/`) with its `run.json`,
  `submit.sbatch`, `logs/`, `out/`, and add its row to `runs/index.tsv`.

## Result — the pictures, the face each line belongs to, and where the two part company

Read this with the caveat that matters for the conservator: on both pieces the reference lines sit on
faces **we did keep**, and on H 10 the base face itself is inside our Surface_0. The failures here are
not 'we threw the base away' except on H 02, where the base was dropped and no reference line uses it.

### 1. The four pictures (the deliverable the conservator asked for)

Each PNG is one lane, 5 panels (3D, X-Y, X-Z, Y-Z, and for the Bl1 lanes a zoom on the failing stretch),
Surface_0 blue, Surface_1 orange, our line thick green, the authors' line thick black:

| lane | file | size |
|---|---|---|
| H02 Bl0 | `C:/PR/SfSpp_preprocessing/artifacts/pota286/png/p286_H02_Bl0.png` | 0.45 MB |
| H02 Bl1 | `C:/PR/SfSpp_preprocessing/artifacts/pota286/png/p286_H02_Bl1.png` | 0.56 MB |
| H10 Bl0 | `C:/PR/SfSpp_preprocessing/artifacts/pota286/png/p286_H10_Bl0.png` | 0.32 MB |
| H10 Bl1 | `C:/PR/SfSpp_preprocessing/artifacts/pota286/png/p286_H10_Bl1.png` | 0.39 MB |

The same files are under `out/png/` in the run directory. What the four show, in one line each:

- **H02 Bl0** — green lies on black the whole way round. Surface_0 (blue) is the interior bowl;
  Surface_1 (orange) appears only as a thin crescent along the top rim in X-Z.
- **H02 Bl1** — identical except mid-right, where black dips into a V-shaped notch (x 20-40, y 0-12,
  z ~515-525) and green runs straight across above it. The zoom (author dots 32-66) is the failing stretch.
- **H10 Bl0** — green and black coincide all round a boot-shaped piece; Surface_1 is offset to the
  right of Surface_0 in X-Z and Y-Z (it is the outside of the same foot).
- **H10 Bl1** — coincides except the lower-left foot, where black follows a fold dipping to y ~ -2 at
  x ~ 5 and green stays at y 5-10 and cuts across (zoom, author dots 40-58).

### 2. Which face each line belongs to (Phase 2 items 1 and 2)

Two distances matter and they are different numbers. The **sheet** distance is from an author dot to the
written B-spline surface we hand to the edge stage; the **cluster** distance is to the nearest point of
the kept clusters themselves. The gap between them is the seam region growing left unassigned.

| lane | author dots | nearer surface | median to that sheet | median to nearest kept cluster point | median normal angle | dots whose nearest raw point is unassigned |
|---|---|---|---|---|---|---|
| H02 Bl0 | 156 | Surface_0, 156/156 | 0.278 mm | 0.819 mm | 21.45 deg | 87.2% |
| H02 Bl1 | 137 | Surface_1, 137/137 | 0.233 mm | 0.823 mm | 20.30 deg | 75.2% |
| H10 Bl0 | 101 | Surface_0, 101/101 | 0.272 mm | 0.820 mm | 23.11 deg | 94.1% |
| H10 Bl1 | 88 | Surface_1, 88/88 | 0.241 mm | 0.894 mm | 18.00 deg | 77.3% |

So the authors' line is the boundary of a face **we kept as a surface** (case (a) of the ticket) on all
four lanes, with no exception. In every lane 75-94% of their dots sit closer to an **unassigned** point
than to any cluster point: their line runs in the seam that region growing left between our two
surfaces, and the written sheet bridges that seam 0.23-0.28 mm from them while the nearest kept cluster
point is 0.82-0.89 mm away. Our own line sits in the same seam (median 0.81-1.04 mm from a kept
cluster point, 79-91% of its dots on a >108 deg boundary, 2% or less of its dots nearest to kept
cluster material) — that is by construction, the walk runs on the boundary of kept material.

### 3. Where the two lines part company, and the number that decides it

- **H02 Bl0, H10 Bl0 — no gap.** Every author dot has one of our dots within 2 mm (median 0.5945 and
  0.6656 mm); the largest angular gap under our dots is 130.72 and 144.83 deg, a real boundary. Nothing
  is lost on these two lanes.
- **H02 Bl1 — 35 of 137 author dots (indices 32-66) have no dot of ours within 2 mm.** Those 35 dots are
  **closer** to kept material than the covered ones (0.2169 mm against 0.8226) and their maximum angular
  gap in a 4 mm neighbourhood is **8.85 deg median** (0% of them on a boundary by the 108 deg rule):
  in our surface they sit in the smoothest interior there is. The reference there follows a **14.13 deg
  fold** (ticket 281) — the V in the picture. The fold is real but shallow, so no boundary detector can
  see it and the walk takes the chord.
- **H10 Bl1 — 20 of 88 uncovered** (indices 40-58 and 74). 13 of the 20 have a **dropped** cluster as their
  nearest clustered point: c5, the 629-point ribbon, 0.3191 mm from kept cluster c1, at 45.0 deg to the
  axis. 2 are nearest kept c1 and 5 are unclustered. The deciding number is the merge's own Step 2:
  `nrm=0.9315` (21.33 deg) against rho_n 0.9500 (18.19 deg) — ticket 283.

### 4. The disc numbers, and where each base face went (Phase 2 item 3)

`bins` is how many of the 36 azimuth bins carry at least 5 axis-normal points; `plane` is the angle
between the cluster's own best-fit plane and the piece axis, and `rms` its thickness in mm; `l3/l1` is
the paper's flatness ratio; `edge_cv` is the raggedness of the outer edge (low = circular); `r5`-`r95` are
radii from the axis; `ax` is the axial span.

| piece | cluster | points | fate | bins | abs n.axis | plane deg | plane rms mm | l3/l1 | edge_cv | r5-r95 mm | ax mm |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H02 | c0 | 17091 | **kept Surface_0** | 13 | 0.987 | 10.59 | 1.430 | 0.0041 | 0.372 | 22.8-89.4 | 483.4-497.1 |
| H02 | c1 | 13915 | **kept Surface_1** | 9 | 0.915 | 22.20 | 1.207 | 0.0035 | 0.061 | 50.5-92.0 | 487.4-507.1 |
| H02 | c2 | 3392 | dropped | 12 | 0.997 | 4.19 | **0.108** | 0.0001 | 0.227 | 16.0-39.9 | 502.1-503.9 |
| H02 | c3 | 1377 | dropped | 0 | 0.403 | 23.83 | 1.615 | 0.0114 | - | r5 41.1 | 504.0-509.6 |
| H02 | c4 | 976 | dropped | 0 | 0.124 | 86.48 | 0.417 | 0.0011 | - | r5 39.5 | 492.8-505.1 |
| H02 | c5 | 539 | dropped | 0 | 0.120 | 86.02 | 0.264 | 0.0005 | - | r5 60.0 | 486.7-499.5 |
| H02 | c6 | 449 | dropped | 0 | 0.153 | 88.48 | 0.328 | 0.0040 | - | r5 40.5 | 497.8-505.7 |
| H02 | c7 | 278 | dropped | 0 | 0.039 | 89.45 | 0.128 | 0.0004 | - | r5 11.2 | 499.2-502.7 |
| H02 | c8 | 167 | dropped | 4 | 0.995 | 0.68 | **0.037** | 0.0000 | 0.016 | 46.6-51.0 | 510.1-510.4 |
| H02 | c9 | 128 | dropped | 3 | 0.995 | 1.78 | **0.033** | 0.0000 | 0.005 | r5 44.7 | 510.9-511.4 |
| H02 | c10 | 120 | dropped | 0 | 0.038 | 88.26 | 0.053 | 0.0003 | - | r5 15.6 | 499.6-502.4 |
| H02 | c11 | 104 | dropped | 0 | 0.190 | 80.47 | 0.151 | 0.0037 | - | r5 25.2 | 497.8-501.5 |
| H02 | unassigned | 7564 | never clustered | 13 | 0.604 | 14.32 | 5.713 | 0.0404 | 0.424 | r5 16.1 | 482.6-510.5 |
| H10 | c0 | 4484 | **kept Surface_0** | **36** | **0.999** | 7.71 | 0.996 | 0.0039 | 0.440 | 4.4-37.5 | 373.5-380.6 |
| H10 | c1 | 3403 | **kept Surface_1** | 23 | 0.964 | 16.65 | 0.614 | 0.0020 | 0.231 | 4.6-39.0 | 364.1-376.5 |
| H10 | c2 | 1685 | dropped | 0 | 0.280 | 74.32 | 0.797 | 0.0044 | - | r5 10.5 | 359.8-372.0 |
| H10 | c3 | 745 | dropped | 0 | 0.125 | 88.02 | 0.364 | 0.0008 | - | r5 16.5 | 367.1-375.2 |
| H10 | c4 | 744 | dropped | 0 | 0.089 | 86.98 | 0.395 | 0.0019 | - | r5 13.7 | 365.7-372.4 |
| H10 | c5 | 629 | dropped (the ribbon) | 0 | 0.531 | 45.00 | 0.879 | 0.0066 | - | 3.3-20.6 | 358.8-363.0 |
| H10 | c6 | 186 | dropped | 0 | 0.082 | 81.33 | 0.295 | 0.0037 | - | r5 19.1 | 370.5-376.3 |
| H10 | c7 | 151 | dropped | 0 | 0.818 | 37.97 | 0.133 | 0.0018 | - | r5 10.8 | 358.5-362.4 |
| H10 | c8 | 72 | dropped | 7 | 0.996 | 5.22 | 0.024 | 0.0000 | 0.217 | r5 7.1 | 357.6-357.8 |
| H10 | unassigned | 4288 | never clustered | 28 | 0.566 | 14.75 | 4.540 | 0.0471 | 0.424 | r5 10.2 | 358.0-380.7 |

**Pot H 02 — what the two surfaces are, and where the base went.** Both kept surfaces are **wall**,
not base: Surface_0 is the interior wall arc (13 of 36 bins, 22.8-89.4 mm from the axis, plane 10.6 deg
off the axis, 1.43 mm rms — curved), Surface_1 the exterior wall arc (9 bins, 50.5-92.0 mm, 22.2 deg,
1.21 mm rms). The base **is** present in the cloud and it is c2: 3392 points, |n.axis| 0.997, its own
plane within **4.19 deg** of the axis, thickness **0.108 mm** (flat to a tenth of a millimetre — a formed
surface, not a fracture), 1.8 mm axial spread, radius 16.0-39.9 mm — a 24 mm-wide plate, three times the
piece's 7.4 mm wall (Surface_0 to Surface_1 median 7.432 mm). It was **dropped**, and not by the
two-largest rule alone: it stands **6.158 mm** from the nearest kept point and of the 1011 unassigned
points within 2 mm of it, **none** is also within 2 mm of kept material — the band between the plate and
the walls is empty of points, so no merge pair can form at rho_d 1.0 mm, and it is also third by size.
Two more flat chips sit above it (c8 167 and c9 128 points, planes 0.68 and 1.78 deg off the axis, 0.037
and 0.033 mm rms, radius 45-51 mm) and are dropped at 1.37 and 1.43 mm. **The authors' lines do not use
the base**: their Bl0 dots are 0.819 mm from kept c0 and 28.4 mm from the base plate, their Bl1 dots
0.823 mm from kept c1 and 36.2 mm from it. So on H 02 the dropped base costs these two lanes nothing.

**Pot H 10 — what the two surfaces are, and the base is kept.** Surface_0 **is the base face**: 4484
points, all **36 of 36** bins, |n.axis| 0.999, its plane within 7.71 deg of the axis, radius 4.4-37.5 mm
with the axis-normal part on a 15.07 mm ring, and it was kept by the paper's rule because classify put
its interior fraction at 0.841 against 0.034 for c1 — the two are the inside and the outside of the same
foot (median separation 8.14 mm). What is dropped on H 10 is the broken band around that foot: c2 1685
(74.3 deg to the axis), c3 745 (88.0), c4 744 (87.0), c6 186 (81.3) — steep, 0.25-0.80 mm rms, i.e.
fracture faces — plus the 629-point ribbon c5 (45.0 deg, 0.879 mm rms) 0.3191 mm from kept c1.
The authors' Bl0 line is the **rim of the base face**, 0.820 mm from kept c0, and we reproduce it at
100% coverage. Their Bl1 line runs on the outside of the same foot, 0.823 mm from kept c1.

### 5. Classification per lane (Phase 2 item 4)

| lane | class | the number that decides it |
|---|---|---|
| H02 Bl0 | **agree**, no defect | 156/156 author dots within 2 mm of our line, median 0.5945 mm |
| H02 Bl1 | **(S) same face, different contour** | the 35 uncovered dots are 0.2169 mm from kept material and sit at 8.85 deg median max angular gap (smooth interior, threshold 108 deg) while the reference follows a 14.13 deg fold; the face they belong to is Surface_1, which we kept |
| H10 Bl0 | **agree**, no defect | 101/101 within 2 mm, median 0.6656 mm |
| H10 Bl1 | **(K) partition mismatch** | 13 of the 20 uncovered dots' nearest clustered point is dropped cluster c5 (629 points, 0.3191 mm from the kept face), refused at merge Step 2 by nrm 0.9315 < rho_n 0.9500 |

Neither failing lane is solved by keeping a third surface: on H 02 the third surface exists (the base
plate) and the reference line does not touch it; on H 10 the base is already kept and the line misses
by 0.32 mm of unmerged material. Both failures are **placement**, not existence, and the two are
different mechanisms — a shallow fold the walk chords across (H 02) and a sliver the merge refuses
(H 10).

### 6. What is still unknown

1. **Why H 02's base plate stands 6.16 mm off the walls with an empty band.** The cloud cannot say
   whether the sherd is actually broken between base and wall or the band is a scan shadow. Nothing
   bridges it, so under the paper's own step-1 distance rule no merge can ever join it.
2. **Whether H 02 Bl1's 14.13 deg fold is a rim the edge stage should follow.** Its amplitude in
   millimetres along the line is not measured here; ticket 280 swept 16 detector settings and
   recovered 0 of 35 dots, so a detector change alone is not the answer.
3. **Whether H 10's ribbon would give the right line if it merged.** Its own shape (21.66 x 3.20 x
   1.76 mm at 45.0 deg to the axis) says fracture ridge; the line it carries may be a break edge, not
   the rim the author drew. Nobody has merged it and looked.

### Evidence

Run directory `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2027_034b0dd_p286-bothfaces/` at
commit 034b0dd, tag p286-bothfaces; job **33746207** COMPLETED 0:0 (54 s, partition cascade, account
punim2657); earlier iterations of the same script 33746131, 33746142, 33746171, 33746184, 33746190.
No re-mesh, no re-run of the edge stage, no code change, no default change.

Inputs (md5 in `inputs/inputs.md5`): frozen sheets H02 Surface_0 `9de492c98873204572919961b7d7dba8`,
Surface_1 `638a22194203c6b356e52a066c656ab3`; H10 Surface_0 `07ba2430d3ed975b8df20d29569dbe03`,
Surface_1 `ee79326ee6c6ef45ca1447b4d3a7699f`; axes `f90e8c18f121ab25f7c2b509624e7b26` (H02) and
`723002c8925cc7bb4ce1705946d1429b` (H10); our lines `ours_b0/b1.pcd` are the 280 run's `*_norm` lane
outputs (binary `62ddd28f4476e9cdf5b27cf0ee01c2f0`, ticket 280, `strings | grep -c WALK-275` = 0);
reference lines `auth_b0/b1.pcd` md5 `8c476163e4fc6556141f0e43adf03d93`, `56f422f6159426e770e4f7bdcb760a06`
(H02) and `3113b1c00c05ff4a0f5413c0f96152eb`, `c787c64a0a2d310609108c9bb94f9fa9` (H10).

Self-checks in `logs/a286.log`: dump/normals alignment max abs dxyz 0.000e+00 on both pieces; unit
normals confirmed (median length 1.0000); the script reproduces the published 280 lane numbers to the
digit (medians 0.582 / 0.864 / 0.661 / 0.641 mm, coverage 100.00 / 74.45 / 100.00 / 77.27).
Tables behind every number above: `out/disc_numbers.tsv`, `out/cluster_adjacency.tsv`,
`out/gap_bridge.tsv`, `out/lanes.tsv`, `out/cluster_pull.txt`, `out/auth_*.tsv`, `out/ours_*.tsv`.

## Acceptance

- Four PNGs exist, each showing surfaces + our line + the authors' line, at a scale where the failing
  stretch is legible; paths reported.
- Per-lane classification (K / S / W) with the deciding number.
- Per piece, a plain statement of what the two surfaces are (which face, is either the base) and where
  the authors' line runs relative to them.
- If the answer is "the bases are only partly surfaced on both", say so and say which step loses
  them — with the numbers that show it.

## Lead verdict (2026-10-24)

**Accepted.** The conservator asked two questions — does the authors' line run on a face we kept,
and if so what went wrong — and both now have an answer with a deciding number, on four lanes of two
pieces.

**1. The premise in this ticket was wrong, and the worker said so.** I wrote "the bases are only
partly surfaced on both". The measurement says the two pieces are opposite cases: on **Pot H 02 the
base is dropped whole** (cluster c2: 3392 points, |n·axis| 0.997, plane within 4.19 deg of the axis,
0.108 mm thick — a formed plate, not a fracture), standing **6.158 mm** from the nearest kept point
with an empty band, so no Appendix A pair can form at rho_d 1.0 and the two-largest rule would
exclude it anyway; on **Pot H 10 the base IS one of the two surfaces** (Surface_0, 4484 points,
36/36 azimuth bins) and we reproduce its rim at 100 %. The brief's framing had to be replaced by the
measurement, which is the right outcome of the ticket.

**2. Neither failure is about the base, and the two failures have different mechanisms.**
- **H 02 Bl1 = (S) same face, different contour.** The 35 uncovered author dots (indices 32-66) are
  *closer* to kept material than the covered ones (0.2169 mm against 0.8226 mm) and sit at an 8.85 deg
  median maximum angular gap — smoother than the 108 deg boundary threshold requires — while the
  reference follows a **14.13 deg fold** into a V-notch. Our surface spans the mouth of that notch;
  the line therefore cuts straight across it. This is not a filter that can be tuned: ticket 280's
  16-detector-setting sweep recovered 0 of 35, and a per-step growth gate cannot resolve a fold the
  surface itself bridges.
- **H 10 Bl1 = (K) partition mismatch**, the same class as ticket 279: 13 of the 20 uncovered author
  dots have a **dropped** cluster as their nearest clustered point — c5, 629 points, **0.3191 mm**
  from the kept face, refused at merge Step 2 by nrm 0.9315 < rho_n 0.9500 (ticket 283). The line we
  draw is correct for the face we kept; the face we kept is missing the ribbon the fold lives on.

**3. Both interior lanes agree** (H02 Bl0 156/156 author dots within 2 mm, median 0.5945 mm; H10 Bl0
101/101, 0.6656 mm), so on these two pieces the defect is confined to the exterior lane — the reverse
of the C01/J01 situation in ticket 285. Recorded because it would be easy to over-generalise either
piece's failure to its sister lane.

**4. Weight.** Two pieces, one pot, four lanes, one growth angle (3.4), one binary
(62ddd28f4476e9cdf5b27cf0ee01c2f0). The pictures were reviewed by the lead and show what the numbers
say: on H02 Bl1 the green line runs straight across the notch the black line follows; on H10 Bl1 the
black line steps inward at the foot while green stays outside. This is a settled **diagnosis** of two
lanes, not a claim about Pot H as a whole — the other eight Pot H pieces have not been looked at this
way.

**5. What it changes.** The "extent family" (H02 73.19 % and H10 72.83 %) is not one family and not a
detector setting: one lane needs a shape-level criterion (does the kept surface bridge a fold?), the
other needs the ribbon kept (merge Step 2, already characterised with its overturn condition in
ticket 283). Neither is a candidate for retuning theta, rho_d or the boundary radius, and none should
be attempted before the walk-seed change (ticket 287) lands, because that change alters which lumps a
lane is even traced from.

**6. Kept as unknown, honestly:** why H02's plate stands 6.16 mm off the walls with an empty band (a
real break or a scan shadow — nothing in the cloud bridges it); the millimetre amplitude of H02 Bl1's
fold, which decides whether a shape-level criterion is even well-posed; and whether H10's c5 ribbon,
if merged, would carry the author's rim or a fracture ridge.
