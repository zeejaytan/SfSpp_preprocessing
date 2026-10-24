# 278 — What is the band that holds Pot C 03's whole rim reference?

Answers: E1
Status: results-in (diagnostic only — no C++ change; findings in `Results` below)
Working in: nothing under version control; reuse the ticket 276 dumps
Needs-eye: no

## Where this comes from

Ticket 276 Phase 3a (run `20261024-1223_0ab0935_p276-phase3a`, job 33737576) established that Pot C 03
Breakline_1's author reference — **119 of 120 dots** — sits on a cluster that the classify step can
never keep:

- the band is the **third** cluster by size (13265 points, against 17245 and 23446 for the two that
  become surfaces), and `classifyAndOrderPaper234` keeps `pclusters[0]`/`pclusters[1]`
  (`mesh_processing_headless.cpp:2105-2118`, the paper's two-largest rule at
  `C:/PR/papers/text/sfspp-2502.13986v1.md:155`);
- the band stands **2.4872 mm** from the kept pair at theta 3.4 (1.9306 mm at 4.0) with **zero point
  pairs within 2 mm** and only 41 within 3 mm, against a 0.3067 mm sampling spacing inside the band.
  So no Appendix A test is ever reached on it: the pair fails on distance long before normals or
  curvature are asked.

The reference breaklines are the authors' own pipeline output, produced under the same two-largest
rule, so in their run a kept surface reached the rim. Ours does not. The merge is not implicated and
theta is not implicated. The open question is what this band physically is.

## Goal

Characterise the band on Pot C 03, and the analogous dropped clusters on Pot H 10, well enough to say
which stage owns the defect.

## Method (reuse the dumps; no new mesh run unless one is genuinely needed)

1. **Orientation.** For the band's points, the median absolute dot product of their normals with the
   kept exterior face's normals. Near 1 = a sheet lying parallel to the face; near 0 = a cross-section.
2. **Shape and extent.** Is it a closed ribbon following the rim, or a patch? Report its extent along
   the rim and across it, and whether its boundary meets the kept face anywhere.
3. **Relation to the author's line.** For the 120 author dots: their distance to the band's own outer
   and inner boundary, and whether they sit on the band's edge nearest the face, its middle, or its
   far edge.
4. **The gap itself.** Is the 2.49 mm separation a hole in the cloud or a real fold? Count the
   unclustered points inside the slab between the band and the face, and report whether the band's
   nearest approach to the face is a point-to-point contact or a gap everywhere along its length.
5. **Pot H 10**, which got worse at 3.4 (96.59% -> 79.55% kept): the same four summaries for the
   dropped clusters carrying its author dots (c2 1.2253 mm, c3 1.3183 mm, c4 1.2868 mm).

## Pre-registered read (written before the measurement)

- **Parallel (`|dot| > 0.8`) and offset by 1-2.5 mm** => the band is a second sheet of the same wall
  (inner surface, or a scan layer behind the outer face). The defect is then upstream — in the cloud
  or in how region growing separates the sheets — and the fix belongs there, not in the merge.
- **Perpendicular (`|dot| < 0.4`)** => the band is the break face (the wall's cross-section at the
  rim). The author's line then sits on the break face while ours stops at the edge — a placement
  difference owned by the edge stage, and the mesh stage is doing its job.
- **In between** => report the distribution rather than forcing a side; that is a real answer too.

## Acceptance

- The four summaries above for Pot C 03, plus item 5 for Pot H 10.
- One line naming which stage owns the defect, drawn only from the pre-registered read.
- Every number traceable to a file in a run directory, with the dump paths and their md5s.

## Evidence to report

- the orientation and shape table, with the band and the face identified by cluster size
- the gap census (unclustered points in the slab; where contact occurs, if anywhere)
- the one-line verdict, plus the single measurement that would overturn it

## Results

### Where the numbers come from

Both pieces were meshed at `SFS_PAPER_THETA=3.4` with the natural merge (no split) and `SFS_MERGE_DIAG=1`, in ticket 276 Phase 3a (job 33737576, run `20261024-1223_0ab0935_p276-phase3a`). No mesh run and no code change was needed for this ticket.

| input | path | md5 |
|---|---|---|
| Pot C 03 dump (69666 points) | `…/runs/20261024-1223_0ab0935_p276-phase3a/out/C03_diag/mergeDiag276_Pot_C_Piece_03.txt` | e9b05214c43e2c48903fac224d619ff4 |
| Pot H 10 dump (16387 points) | `…/out/H10_diag/mergeDiag276_Pot_H_Piece_10.txt` | 38b62daff15f9eb7a300c76604e998a7 |
| Pot C 03 axis | `…/stage/C03_diag/Dataset/Axes/Pot_C_Piece_03_Axis.xyz` | c5cce01ee33448a74c91d2ef33f7c9fe |
| Pot H 10 axis | `…/stage/H10_diag/Dataset/Axes/Pot_H_Piece_10_Axis.xyz` | 723002c8925cc7bb4ce1705946d1429b |
| author Pot C 03 Bl0 / Bl1 (191 / 120 dots) | `…/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_03_Breakline_{0,1}.pcd` | 22c8f0e396814cc920d42368e74c31bc / d0d8cb0a74ad9eb4a347d5ba09d12607 |
| author Pot H 10 Bl0 / Bl1 (101 / 88 dots) | `…/Pot_H_Piece_10_Breakline_{0,1}.pcd` | 3113b1c00c05ff4a0f5413c0f96152eb / c787c64a0a2d310609108c9bb94f9fa9 |

Scripts and their raw output are in `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1243_0ab0935_p278-band/`: `a278.py` → `a278.out` (orientation, shape, relation to the author's dots, slab), `a278b.py` → `a278b.out` (per-cluster frame table), `a278d.py` → `a278d.out` (plane-fit roughness, continuity), `a278f.py` → `a278f.out` (corner-ring spacing), `a278g.py` → `a278g.out` (outer-edge radius profile). Normals are PCA over 20 neighbours, checked against the PCD's own normals: median |dot| 0.9999 / 0.9990 / 0.9996 / 0.9995 and frac > 0.9 = 1.000 on the four clusters tested. The dump carries 69666 of the input PCD's 701177 points (9.94 %, Pot C 03) and 16387 of 163150 (10.0 %, Pot H 10), so every millimetre distance below is exact while every point spacing quoted is an upper bound on the cloud's own.

### Pot C 03 — census

| cluster | points | kept | radial p5/p50/p95 | axial p50 | \|n·rad\| | \|n·ax\| | 10° bins | λ2/λ1 | λ3/λ1 | what it is |
|---|---|---|---|---|---|---|---|---|---|---|
| c-1 | 13659 | unclustered | 33.96/43.37/58.83 | 438.97 | 0.459 | 0.755 | 36 | 0.5611 | 0.1116 | corner ring and cut faces |
| c0 | 23446 | Surface_0 (interior) | 10.21/32.41/51.62 | 437.29 | 0.210 | 0.977 | 36 | 0.3763 | 0.0434 | dished interior face |
| c1 | 17245 | Surface_1 (exterior) | 37.25/44.53/59.29 | 436.93 | 0.788 | 0.615 | 36 | 0.2392 | 0.0451 | exterior wall |
| c2 | 13265 | no | 7.68/24.37/32.54 | 431.04 | 0.056 | 0.998 | 36 | 0.9601 | 0.0044 | **the band: the outside of the base** |
| c3 | 603 | no | 50.16/53.08/55.68 | 450.66 | 0.745 | 0.662 | 3 | 0.1996 | 0.0087 | debris outside the wall |
| c4 | 521 | no | 42.12/47.23/54.31 | 443.66 | 0.745 | 0.489 | 6 | 0.0175 | 0.0003 | debris |
| c5 | 497 | no | 38.86/45.64/52.69 | 442.18 | 0.485 | 0.681 | 6 | 0.0173 | 0.0004 | debris |
| c6 | 224 | no | 37.80/39.06/40.71 | 437.50 | 0.741 | 0.665 | 3 | 0.0360 | 0.0003 | debris |
| c7 | 206 | no | 46.90/49.68/52.11 | 443.88 | 0.510 | 0.786 | 3 | 0.0229 | 0.0008 | debris |

(Radial and axial coordinates are relative to the pot axis in the axis file above; |n·rad| near 1 means normals pointing outward from the axis, |n·ax| near 1 means normals along the axis.)

### 1. Orientation — perpendicular to the wall, parallel to the bowl

Between each band point and its nearest point on a kept face:

| pair | median \|dot\| | q10 | q90 | frac > 0.8 | frac < 0.4 |
|---|---|---|---|---|---|
| band vs c1 (exterior, 17245) | 0.3141 | 0.0991 | 0.4187 | 0.000 | 0.844 |
| band vs c0 (interior, 23446) | 0.9973 | 0.7010 | 0.9997 | 0.806 | 0.000 |

The band's own normals point along the pot axis: median |n·axis| 0.9982, median |n·radial| 0.0555. Offsets: band → c1 2.4872 mm, band → c0 5.0493 mm; to the nearest kept point at all 2.4872 mm (p10 5.1163, p50 5.6285, p90 6.3690, max 7.2571).

So the band is a face lying in the pot's cross-sectional plane: perpendicular to the exterior wall and 5.05 mm from, and parallel to, the interior bowl — **the outside of the base, with the interior bowl as the inside of the same slab of clay.**

### 2. Shape and extent — a whole face, not a ribbon

- fills 36 of 36 ten-degree bins (a full 360° ring), arc length ≈ 153 mm at the median radius;
- extends 7.68 → 32.54 mm in radius (24.86 mm across), with 3.82 mm of axial relief;
- PCA eigenvalues λ1 295.3, λ2 283.5, λ3 1.3: λ2/λ1 0.9601, λ3/λ1 0.0044 — a disc, not a strip;
- outer-edge radius per bin: median 32.529 mm, min 30.875, max 33.672 (spread 2.797, sd 0.783), the bin median axial height varying by 0.893 mm — a manufactured base edge, not a fracture rim (for comparison the debris clusters c3–c7 occupy 3–6 bins with λ2/λ1 0.017–0.20);
- contact with the kept pair: 41 of 13265 band points within 3 mm, in 6 of 36 bins (a 60° sector); elsewhere the gap is p50 5.6285 mm. **No point-to-point contact anywhere.**

### 3. The author's dots inside the band

Pot C 03 Bl1 (120 dots): 119 within 2 mm of the band (median 0.8821, max 1.9826). All 119 sit in the lowest quartile of the band's own distance-to-kept-face distribution (median percentile 0.025) at median radial percentile 0.976 inside the band — **0.963 mm from the band's outer boundary against 26.588 mm from its inner boundary**: face-side 119, middle 0, far edge 0.

So the reference line runs along the band's outer edge, the corner where the base face meets the exterior wall. It is not a line across the band.

Pot C 03 Bl0 (191 dots): no single band holds it — 12 dots within 2 mm of c3 (603 points), 21 of c4 (521), 20 of c5 (497), 9 of c6 (224), 8 of c7 (206). Bl0 follows the debris round the wall, which is why Bl0 scores med 0.354 / cov 100.00 while Bl1 does not.

### 4. The gap — a fold with a hole in the labelling, not in the cloud

- strict slab test (an unclustered point within 1.35 mm of both the band and the kept pair): **0 points**.
- between band and kept pair there is, however, a sampled ring: 1175 of the 13659 unclustered points lie within 3 mm of both, at radius 34.09/35.30/36.65 mm and axial height 426.59/427.17/427.58 mm, in all 36 angular bins, with median nearest-neighbour spacing 0.3556 mm among themselves (p90 0.5865, max 0.8029);
- the band's nearest unclustered point is 0.1744 mm away, and that ring's nearest kept point 0.2173 mm — but **0 of the 1175 lie within 1 mm of both sides** (101 within 1 mm of the band, 108 within 1 mm of the kept pair).

So the object is continuous there: a re-entrant corner between the base and the wall, sampled at 0.36 mm. What is discontinuous is the labelling — the corner ring belongs to no cluster, so the band's nearest *kept* point is 2.4872 mm away and no Appendix A pair can form. It is not a hole in the cloud (a hole would be missing points; the ring's own spacing is 0.36 mm) and not a second sheet.

### 5. Pot H 10 — the same summaries

| cluster | points | author dots | median \|dot\| vs c0 / c1 | dmin | p50 gap | ≤2 mm | bins | λ2/λ1 | \|n·rad\| / \|n·ax\| | reading |
|---|---|---|---|---|---|---|---|---|---|---|
| c2 | 1685 | 22 Bl0 (all face-side) | 0.2757 / 0.1845 | 1.2253 | 7.3139 | 3.3 % | 13 | 0.1116 | 0.681 / 0.274 | broad patch, not a ribbon; cross-section-like |
| c3 | 745 | 25 Bl0 + 21 Bl1 (24 / 21 face-side) | 0.1077 / 0.0719 | 1.3183 | 2.8916 | 12.1 % | 12 | 0.0165 | 0.823 / 0.122 | thin ribbon ⊥ both kept faces = **break face** |
| c4 | 744 | 18 Bl0 + 13 Bl1 (18 / 13 face-side) | 0.0701 / 0.1250 | 1.2868 | 3.2426 | 12.9 % | 10 | 0.0431 | 0.762 / 0.088 | thin ribbon ⊥ both kept faces = **break face** |
| c5 | 629 | 21 Bl1 (14 face-side, 7 middle) | 0.5321 / **0.8153** | **0.3191** | 1.2505 | — | 15 | 0.0218 | 0.266 / 0.518 | parallel to c1 at 0.32 mm = **a piece split off the exterior face** |
| c6 | 186 | 10 Bl0 + 10 Bl1 | 0.1243 / 0.1188 | 1.4905 | 0.8083 | — | 2 | 0.0391 | 0.128 / 0.067 | small break face |

Pot H 10's kept pair is two near-parallel horizontal faces 8.2 mm apart in the axial direction (|n·ax| 0.999 and 0.965) — the two sides of the base slab; the merge joined four pairs in pass 1 ("merge 376 into 777", "merge 278 into 1153", "merge 254 into 1431", "merge 142 into 603").

### The pre-registered read, applied

**Pot C 03 — the perpendicular branch fires; its mechanism does not survive.** The band's median |dot| against the kept exterior face is 0.3141, below 0.4. But the band is not the wall's cross-section: a cross-section is a narrow strip through the wall's thickness, and this is a face 24.86 mm across covering 360°, planar to λ3/λ1 0.0044, running parallel to the *other* kept face at 5.05 mm, with its normals along the pot axis rather than across the wall. The perpendicularity is simply that base and wall meet at 90°. The parallel branch's pattern is close (median 0.9973 against the interior face) but at 5.05 mm rather than 1–2.5 mm, so it cannot be read as a second scan sheet either. Reported rather than forced, as the ticket's in-between clause asks: **the band is the pot's exterior base face.**

**Pot H 10 — the perpendicular branch applies with its mechanism intact.** c3, c4 and c6 score 0.07–0.12 against both kept faces with λ2/λ1 0.017–0.043: thin ribbons, i.e. break faces, and the author's dots on them sit at the face-side edge. The reference line runs along the fracture surface just inside the edge where our kept surfaces stop.

### The stage verdict

**Pot C 03: the mesh stage owns it — the partition, not the placement.** The band is a genuine face of the object (the outside of the base), it holds 119 of the 120 reference dots, and it never becomes a surface: region growing leaves the base-to-wall corner ring (1175 points, all 36 bins) in no cluster, so the band's nearest kept point is 2.4872 mm — about 2.5 × rho_d — and no Appendix A pair can form; and at 13265 points against 23446 and 17245 it is third by size, outside the two-largest rule in any case. The edge stage never receives the face the reference line is drawn on.

**Pot H 10: the edge stage owns its placement question, with one partition element.** c3/c4/c6 are break faces the mesh stage is right to drop, and the author's line is drawn on the break face rather than at its edge; but c5 — a piece of the exterior face itself, 0.3191 mm away and parallel (median |dot| 0.8153) — was dropped too (5th by size, 21 of H10's 88 Bl1 dots on it).

### The single measurement that would overturn it

The verdict turns on the band being a face of the object rather than a fracture surface. The measurement: **the band's outer-edge radius profile round the 36 bins.** A manufactured base edge runs round at a near-constant radius and closes; a fracture rim wanders and does not close. Measured: median 32.529 mm, min 30.875, max 33.672 (spread 2.797, sd 0.783) with the bin axial height varying by 0.893 mm — closed and near-circular. Had that spread been tens of millimetres with the ring open, the band would be a fracture face, the read's perpendicular branch would apply with its mechanism intact, and Pot C 03 would fall to the edge stage exactly like Pot H 10.

### Boundaries respected

No C++ edit, no default change, no mesh re-run (the 276 Phase 3a dumps sufficed), `C:/PR/worktrees/sfs/275` untouched, nothing committed. The only file added on Spartan is the run directory named above.

