# 293 — The two miss families the corpus re-score exposed

Status: done (accepted: three partition-mismatch lanes, eight lanes in three causes; no walk fix)
Working in: main (worktree closed 2026-10-25)
Branch: 293-miss-families, in /c/PR/worktrees/sfs/293
Answers: E1
Created: 2026-10-25
Follows: 292 (the baseline: 281/292 sound lanes at bar), 286 (H02/H10 mechanism), 278/279 (base-band partition)

## Why

Ticket 292 measured every lane of the frozen corpus at the shipped defaults. Eleven sound lanes are
below bar and they are not one thing. Eight keep the reference's route and length and differ over one
stretch; three are different contours. This ticket names both families so a later session does not
re-measure them, and answers the one question the numbers cannot: **is the eight-lane family one
mechanism or several?**

## The lanes

Different contours -- three lanes where our line and the reference are both real edges of the
same sherd, taken differently (ticket 294 read this off the pictures and off the authors' own mesh):

| piece | lane | n ours/auth | median mm | cov ours/auth | len ours/auth mm |
|---|---|---|---|---|---|
| Pot_C_Piece_03 | 1 | 337/120 | 11.327 | 18.40 / 50.83 | 607.34 / 273.69 |
| Pot_I_Piece_25 | 0 | 58/69 | 6.910 | 0.00 / 0.00 | 105 / 124 |
| Pot_I_Piece_25 | 1 | 67/60 | 6.951 | 0.00 / 0.00 | 121 / 106 |

`Pot_C_Piece_03` Bl1: ours is the sherd's outer rim, theirs a closed ring on the flat of the same
face about 11 mm inside. `Pot_I_Piece_25`: ours a small closed triangle, theirs a larger loop,
6.9 mm apart in 3D and crossing only in projection.

The picture (`C:/PR/SfSpp_preprocessing/artifacts/pota292/png/Pot_I_Piece_25_Bl0.png`) shows our
closed loop crossing outside a smaller closed reference loop. Both are on the piece; they are not the
same curve.

One-stretch family -- eight lanes (median well under the 2 mm bar, coverage 62-86%):

| piece | lane | median mm | cov ours | len ratio |
|---|---|---|---|---|
| Pot_D_Piece_22 | 0 | 0.757 | 86.40 | 0.92 |
| Pot_D_Piece_27 | 0 | 0.673 | 73.21 | 1.20 |
| Pot_D_Piece_27 | 1 | 0.798 | 62.07 | 1.21 |
| Pot_E_Piece_16 | 0 | 0.676 | 72.97 | 1.01 |
| Pot_H_Piece_02 | 1 | 0.688 | 72.46 | 1.01 |
| Pot_H_Piece_10 | 1 | 0.728 | 72.22 | 1.05 |
| Pot_I_Piece_06 | 1 | 0.883 | 70.22 | 1.01 |
| Pot_I_Piece_13 | 1 | 0.734 | 82.61 | 1.02 |

(`Pot_H_Piece_02` Bl1 and `Pot_H_Piece_10` Bl1 were already diagnosed in ticket 286 -- (S) same
face different contour, and (K) partition mismatch -- so they are members with a known reading, not
open cases.)

## Phase A -- Pot I 25, what are the two curves

Use the instrument of ticket 278/286, on a fresh mesh at theta 3.4 with `SFS_AXIS_FILE` set (quote
the `[PAPER-234] classify` line; ticket 277's trap). Deliver:

1. Per-cluster census for both lanes: points, azimuth bins filled, `l3/l1`, `edge_cv`, axial spread,
   `|n.axis|`, distance to the kept surface.
2. Every author dot and every one of our dots assigned to a surface/cluster; report the share that
   lands on nothing.
3. Per lane a picture `C:/PR/SfSpp_preprocessing/artifacts/pota293/png/p293_I25_Bl<k>.png`
   (3D + X-Y + X-Z + Y-Z + a zoom on the divergence, style as ticket 286).
4. One class per lane: (K) partition mismatch, (S) same face different contour, (W) walk,
   (X) our line is right and the reference wrong -- with the evidence that decides it. A reference
   ruling is the conservator's to make, not the worker's: state the case, do not close it.

## Phase B -- the one-stretch family, one mechanism or several

Same instrument, one table row per lane above: where along the reference the >2 mm stretch sits
(start/end index, arc length, share of the loop), how far it goes (max, mean), and whether at that
stretch **our kept surface spans a feature the reference turns into** (a fold, a notch, a step) or
**our line leaves the surface** (rides an edge the reference does not use). Ticket 286 already showed
both happen (H02 (S) vs H10 (K)); the question is the mix across eight lanes.

Pieces to mesh: Pot_C 03, Pot_D 22, 27, Pot_E 16, Pot_H 02, 10, Pot_I 06, 13, 25 -- nine
pieces, one job (Phase A's three-piece run and Phase B's seven overlap on four).

## Constraints

- Inputs: the frozen corpus only (`/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/`),
  staged by `scripts/stage_piece.sh` (symlinks; a fresh cloud is refused by design, ticket 291).
- No C++ change, no default change, no threshold retune, no re-run of the corpus.
- The mesh stage is piece-dependently non-deterministic (unseeded `std::random_device`,
  `mesh_processing_headless.cpp:1526-1527`): report each piece's own run-to-run spread if a claim
  rests on a sub-millimetre difference, and land all identity claims on fixed inputs.
- Build with the committed recipe (`git archive` + cmake + sbatch); never `build.sh --target nurbs`
  (ticket 282 -- it compiles the pre-247 duplicate).
- Run directory under `/data/gpfs/projects/punim2657/SfSpp/runs/` with `run.json`, and an index row.
- Geometry dies with the ticket: delete the stage trees and any `.pcd/.xyz/.obj/.ply` output before
  reporting, write `out/GEOMETRY_DELETED.txt`, keep the PNGs, the tables and the scripts.
- Write results into this ticket in the main clone and leave it uncommitted; the lead commits.

## Acceptance

1. A table with every lane above and its class, each cell traceable to a file in the run directory.
2. One answer to "one mechanism or several" for the eight-lane family, with the split by class.
3. Pot I 25's case stated precisely enough for the conservator to rule on the reference.
4. Pictures for at least both Pot I 25 lanes and one member of each class found in Phase B.

## Amendment (lead, 2026-10-25) -- ticket 294 answered most of Phase A and B

The eleven pictures (ticket 294, `artifacts/pota294/png/`) settle the "what", so this ticket is narrowed
to the "why". Do not re-measure the geometry that is already established:

- **Established by 294, do not re-derive**: our line is the boundary of the surface we kept, the
  reference is the boundary of the surface the authors kept, in all eleven lanes. Eight lanes are the
  same face with a different reading of one stretch (18-65 mm; on `Pot_D_Piece_22` Bl0 **the reference
  is the one drawing a chord** -- 18 mm across the notch, mean gap 4.33 mm; on `Pot_H_Piece_10` Bl1 the
  reference steps 4.42 mm inside our face for 39.6 mm). Three lanes are a different partition
  (`Pot_C_Piece_03` Bl1: our outer rim 607 mm vs their inner ring 274 mm; `Pot_I_Piece_25` both lanes:
  our small closed triangle 105 / 121 mm vs their larger loop 124 / 106 mm, 6.9 mm apart in 3D and
  crossing only in projection). Every reference line sits on the authors' own DS mesh (18/18 rows,
  median 0.007-0.024 mm, max 1.386 mm, 0.00% beyond 2 mm).
- **Phase A, what remains**: for `Pot_I_Piece_25` both lanes, name the closed edge each line follows --
  which face, which boundary, and whether a second closed edge exists in the same kept surface. A
  picture exists; what is missing is the cluster/face census behind it (one run, three pieces with
  `Pot_C_Piece_03`, geometry deleted after).
- **Phase B, what remains**: why the walk chose the boundary of the whole face rather than turning where
  the reference turns. The candidates are now specific: (i) the reference is not a boundary at all in
  that stretch (it is a chord over a notch -- D22 Bl0 shows this directly), (ii) the reference follows a
  crease inside the face (H10 Bl1), (iii) our kept region spans a fold the reference turns into (H02 Bl1,
  ticket 286). Decide which of the eight each lane is, from the surfaces, and say which of the three the
  walk could ever know about from the boundary set alone.
- **Still the conservator's, not the worker's**: whether `Pot_C_Piece_03` Bl1 and `Pot_I_Piece_25`'s
  lines should count as references at all. State the case; do not close it.

Everything else in the ticket stands: no code change, frozen corpus by symlink, geometry deleted, run
directory and index row, results written into the ticket for the lead to commit.

## Results (2026-10-25)

### The run, and how the numbers were made

| item | value |
|------|-------|
| run directory | `/data/gpfs/projects/punim2657/SfSpp/runs/20261025-0456_3ada802_p293-census/` |
| commit | `3ada8027b6a16a40f97fe1b2f0250d648fa3b3b7` on `293-miss-families` (+ `e544366` for the cross-pairing script) |
| job A `p293run` | **33753655** COMPLETED 0:0, 6:06 -- build, nine pieces, eighteen lanes, manifest |
| job B `p293draw` | **33753658** COMPLETED 0:0, 2:41 -- census, eleven pictures, geometry deleted (`--dependency=afterok:33753655`) |
| index row | `20261025-0456_3ada802_p293-census  33753655  3ada8027b6a16a40f97fe1b2f0250d648fa3b3b7  p293-census` (verdict and human_note empty, index now 80 rows) |

Build: `git archive 3ada802` unpacked into `sfs-vote-248/p293-build-33753655/src`, `cp -a` of `alglib`,
`cmake -DCMAKE_BUILD_TYPE=Release`, `make -j8 EdgeLineExtractionHeadless MeshPreprocessingHeadless`
inside `pcl_191_nurbs.sif` -- the 294 recipe verbatim (`294/submit294.sbatch`), never `build.sh --target nurbs`.
Committed sources, from `out/source.md5`: `edgeline_extraction_headless.cpp`
`f0dbfe7032d90a04412d15bd1699a703` (3739 lines), `mesh_processing_headless.cpp`
`459dabe145056489829804292710b382` (2618 lines) -- **byte-identical to the ticket-294 pair**
(`f0dbfe70`/`459dabe1`), so this run is the 294 code plus one print-only patch and nothing else.
Binaries: edge `a28d10afab2b50bbe750d599ee2b7214` (the same bytes 294 built: the edge stage is untouched),
mesh `ff696f7f8072892100631b9173c690e3` (294: `0171f471d0558d2676df7c4b113c1e9d`).

**The one deviation in the build, stated here and in section Deviations:** the census needs cluster labels and
no committed binary emits them, so job A applied `.scratch/pota-repro/patches/276-merge-diag.patch`
(md5 `ff3fc86fb58e28f9ad84f86e0d482640`) with `patch -p1` after the archive and ran with `SFS_MERGE_DIAG=1`.
Evidence it changed nothing but printing: the patch is env-gated (`unset`/`0` leave it inert) and print-only,
the reverse dry-run exits 0 (exact application), the patched file is 2746 lines with 122 non-empty lines added
and 0 removed, and the eighteen re-scored lanes below reproduce 292/294 (section Deviations).

`SFS_AXIS_FILE` was set for every piece and every parse printed
`[PAPER-234] classify: face0 n=... interior_frac=... face1 n=... interior_frac=...`; theta came from
`[PAPER-234] paper grow: thetaDeg=3.40000 kappa=1.00000 nb=10` on all nine pieces (never set by hand).

| piece | classify (verbatim tail) | order on this piece |
|-------|--------------------------|---------------------|
| C 03 | face0 n=23898 interior_frac=0.8151 face1 n=17455 interior_frac=0.0000 satA=36934 satB=4419 | kept: Surface_0=interior |
| D 22 | face0 n=5642 interior_frac=1.0000 face1 n=5027 interior_frac=0.0000 satA=10669 satB=0.0000 | kept: Surface_0=interior |
| D 27 | face0 n=2500 interior_frac=0.0000 face1 n=2237 interior_frac=1.0000 satA=0.0000 satB=4737 | swapped: Surface_0=interior |
| E 16 | face0 n=14989 interior_frac=0.0000 face1 n=11081 interior_frac=0.9996 satA=4 satB=26066 | swapped: Surface_0=interior |
| H 02 | face0 n=17678 interior_frac=0.9996 face1 n=14614 interior_frac=0.0000 satA=32285 satB=7 | kept: Surface_0=interior |
| H 10 | face0 n=4872 interior_frac=0.8436 face1 n=3718 interior_frac=0.0301 satA=7716 satB=874 | kept: Surface_0=interior |
| I 06 | face0 n=23564 interior_frac=0.0000 face1 n=19380 interior_frac=0.9955 satA=... satB=... | swapped: Surface_0=interior |
| I 13 | face0 n=16463 interior_frac=0.0000 face1 n=14442 interior_frac=0.9897 | swapped: Surface_0=interior |
| I 25 | face0 n=3072 interior_frac=0.0000 face1 n=2321 interior_frac=0.9931 satA=16.0000 satB=5377.0000 | swapped: Surface_0=interior |

Eighteen lanes were scored (eleven wanted plus the seven opposite lanes, as the two-direction coverage the
brief asks for). The eleven of record, fresh against ticket 294:

| lane | ours n | theirs n | median mm (294) | cov ours pp (294) | reading |
|------|-------:|--------:|----------------:|------------------:|---------|
| C 03 Bl1 | 339 | 120 | 11.287 (11.327) | 17.99 (18.40) | reproduces, -0.040 mm / -0.41 pp |
| D 22 Bl0 | 125 | 133 | 0.757 (0.757) | 86.40 (86.40) | exact |
| D 27 Bl0 | 56 | 48 | 0.673 (0.673) | 73.21 (73.21) | exact |
| D 27 Bl1 | 58 | 49 | 0.798 (0.798) | 62.07 (62.07) | exact |
| E 16 Bl0 | 111 | 112 | 0.755 (0.651) | 72.97 (72.97) | **+0.104 mm, outside the rule** |
| H 02 Bl1 | 138 | 137 | 0.690 (0.688) | 72.46 (72.46) | reproduces, +0.014 mm |
| H 10 Bl1 | 90 | 88 | 0.728 (0.728) | 72.22 (72.22) | exact |
| I 06 Bl1 | 181 | 179 | 0.840 (0.867) | 71.27 (72.78) | **n +1, -1.51 pp, outside the rule** |
| I 13 Bl1 | 162 | 160 | 0.713 (0.707) | 81.48 (83.12) | **n +2, -1.64 pp, outside the rule** |
| I 25 Bl0 | 58 | 69 | 6.910 (6.910) | 0.00 (0.00) | exact |
| I 25 Bl1 | 67 | 60 | 6.951 (6.951) | 0.00 (0.00) | exact |

The three lanes outside the 0.05 mm / 1 pp rule are exactly the three whose dot count moved, and the six with
identical counts reproduce to <=0.040 mm and <=0.41 pp. That is the mesh stage's unseeded 30-point ray cast
(`mesh_processing_headless.cpp:1526-1527`, ticket 291), not a disagreement about the method -- compared against
each piece's own run-to-run spread, never against zero.

### Phase A -- which closed edge each line follows

#### Pot I 25: one clustering, both lanes

Both lanes ride a face from the same merge, so the census is one table (`out/clusters.tsv`; `kept` is the merge's
survivor flag; `d other kept` is the distance to the nearest point of the other kept cluster, mm).

| cluster | kept | pts | rad p5/p50/p95 | ax p5/p50/p95 | axsp | angbins/36 | edge_r | edge_cv | l2/l1 | l3/l1 | abs n.ax | abs n.rad | d kept min/med |
|---------|:----:|----:|----------------|----------------|-----:|-----------:|-------:|--------:|------:|------:|---------:|----------:|---------------:|
| c0 (our Surface_0, interior) | yes | 2321 | 3.53/12.74/22.08 | 212.12/214.39/215.59 | 3.48 | 21 | 16.890 | 0.2795 | 0.6040 | 0.0074 | 0.9813 | 0.1879 | 6.462/6.894 |
| c1 (our Surface_1, exterior) | yes | 3072 | 4.64/14.89/25.57 | 218.29/221.04/222.53 | 4.24 | 20 | 19.524 | 0.2140 | 0.5361 | 0.0059 | 0.9799 | 0.1993 | 6.462/6.926 |
| c2 | no | 987 | 2.03/10.24/23.60 | 214.50/218.06/221.15 | 6.65 | 12 | 4.446 | 0.8785 | 0.0223 | 0.0001 | 0.0709 | 0.1782 | 0.947/2.454 |
| c3 | no | 853 | 18.62/21.56/29.30 | 212.72/215.53/218.12 | 5.40 | 11 | 21.803 | 0.1528 | 0.0181 | 0.0004 | 0.3333 | 0.8046 | 1.186/2.532 |
| c4 | no | 793 | 13.58/18.44/29.15 | 212.62/215.74/218.68 | 6.06 | 10 | 17.426 | 0.2914 | 0.0317 | 0.0002 | 0.4648 | 0.7046 | 1.164/2.664 |
| unclustered | -- | 1788 | 4.03/20.35/30.73 | 211.60/216.56/222.06 | 10.46 | 26 | 20.348 | 0.4301 | 0.5127 | 0.0478 | 0.6567 | 0.5460 | 0.096/1.052 |

Both kept clusters are thin sheets nearly perpendicular to the axis (`abs n.ax` 0.98) with 20-21 of 36 azimuth
bins filled and a low `l3/l1`: two faces of one wall, each 6.5-6.9 mm from its neighbour. The dropped c2
(987 pts, `abs n.ax` 0.071, `l3/l1` 0.0001) is a slab lying 0.95 mm off the kept material -- the piece's broken
or merged material, not a face.

#### What each line follows, measured against each face's rim

`rim profile` compares a line's per-azimuth radius to the face's own p95 (outer) and p5 (inner) radius
(`out/census.json`, `phaseA`); `ring` is the share of the line's dots within 1.0 mm of the p95 rim, and the
median azimuth gap is ticket 286's boundary statistic (a boundary shows >108 deg).

| lane | line | n | len mm | face it rides | d to that face's p95 rim | d to its p5 edge | ring share | median gap deg | >108 deg share |
|------|------|---:|-------:|---------------|-------------------------:|-----------------:|-----------:|---------------:|---------------:|
| C 03 Bl1 | ours | 339 | 611.26 | c1 (Surface_1) | 0.700 | 7.540 | 0.351 | 216.3 | 99.41 |
| C 03 Bl1 | theirs | 120 | 273.69 | c1, but on unclustered material | 10.506 | 3.575 | 0.000 | 279.1 | 100.00 |
| I 25 Bl0 | ours | 58 | 104.79 | c0 (Surface_0) | 0.980 | 14.184 | 0.460 | -- | -- |
| I 25 Bl0 | theirs | 69 | 124.26 | c1 (Surface_1) | 3.903 | 16.506 | 0.032 | -- | -- |
| I 25 Bl1 | ours | 67 | 120.57 | c1 (Surface_1) | 0.981 | 15.717 | 0.400 | -- | -- |
| I 25 Bl1 | theirs | 60 | 106.28 | c0 (Surface_0) | 2.360 | 13.051 | 0.100 | -- | -- |

The kept faces are 18.55 mm (c0) and 20.94 mm (c1) wide radially; a line 0.98 mm from a face's p95 radius with
40-46% of its dots inside that 1 mm ring is tracing that face's rim. So **our Bl0 is the rim of c0 and our Bl1
the rim of c1**, and **the authors' Bl0 is a curve on c1 while their Bl1 is a curve on c0** -- each side's line
lies on the face the other side's line of the opposite index lies on.

**Is there a second closed edge in the same kept surface?** No, for either lane. Within c0 the nearest other
kept material is c1 at 6.46 mm; within c1 it is 6.93 mm. The nearest dropped cluster (c2, at 0.95 mm) is not
under either line: 0% of the 69 author dots of Bl0 and 0% of the 60 of Bl1 have a dropped cluster as nearest
label. Each face carries exactly one closed rim, and each side draws it once -- the two lanes are the same two
curves, counted twice.

#### Assignment of every dot (`out/assign_summary.tsv`, per-dot in `out/census/Pot_I_Piece_25_Bl*.assign.tsv`)

Share of dots by the label of the nearest dumped point (`d all` = median distance to that point, mm), then by
the nearest point of any kept cluster (`d kept`):

| lane | side | c0 | c1 | dropped | unclustered | nearest kept c0 / c1 | d all | d kept |
|------|------|---:|---:|--------:|------------:|---------------------:|------:|-------:|
| C 03 Bl1 | ours | 0.00 | 2.36 | 0.29 | 97.35 | 0.59 / 99.41 | 0.217 | 1.133 |
| C 03 Bl1 | theirs | 0.00 | 0.00 | 10.00 | 90.00 | 0.00 / 100.00 | 0.257 | 3.567 |
| I 25 Bl0 | ours | 1.72 | 0.00 | 0.00 | 98.28 | 100.00 / 0.00 | 0.252 | 0.660 |
| I 25 Bl0 | theirs | 0.00 | 11.59 | 0.00 | 88.41 | 0.00 / 100.00 | 0.231 | 0.715 |
| I 25 Bl1 | ours | 0.00 | 1.49 | 0.00 | 98.51 | 0.00 / 100.00 | 0.243 | 0.687 |
| I 25 Bl1 | theirs | 23.33 | 0.00 | 0.00 | 76.67 | 100.00 / 0.00 | 0.244 | 0.521 |

Nobody's dots land on nothing in the physical sense: every dot is 0.22-0.25 mm from a dumped point and
0.52-3.57 mm from kept material. What differs is which cluster owns them. 97-99% of our dots have an
*unclustered* nearest point because our line is the cut boundary of the kept set and its dots sit on the last
retained sample; that is the same signature on every piece in the corpus.

#### The measurement that decides Pot I 25: cross-pairing (`out/crosspair.tsv`)

| ours | theirs | n | median mm | cov ours / theirs | max mm | pairing |
|------|--------|---:|----------:|:-----------------:|-------:|---------|
| Bl0 | Bl0 | 58/69 | 6.910 | 0.00 / 0.00 | 7.549 | same index -- the miss |
| **Bl0** | **Bl1** | 58/60 | **0.680** | **100.00 / 100.00** | 1.420 | **cross -- at bar** |
| **Bl1** | **Bl0** | 67/69 | **0.568** | **100.00 / 100.00** | 1.752 | **cross -- at bar** |
| Bl1 | Bl1 | 67/60 | 6.951 | 0.00 / 0.00 | 7.722 | same index -- the miss |

The two sides hold the **same two closed curves** and index them oppositely. Nothing about the contour differs:
read crosswise, both I25 lanes are at bar with 100% two-way coverage and a 1.75 mm worst case.

#### Pot C 03 Bl1, for completeness

Our line (339 dots, 611.26 mm) is the outer rim of the one band we keep: c1, 17455 pts, radially 37.25-59.28 mm,
22.03 mm wide, 0.70 mm from its p95 rim, 35% of dots in the ring, 99.4% on a >108 deg boundary. Their line
(120 dots, 273.69 mm) is 10.51 mm inside that outer rim and 3.58 mm in from the band's *inner* p5 edge -- it
runs along the inner part of the band, on material we left unclustered (90.0%) or dropped (10.0%, the c2 base
plate 3.10 mm from kept material). Their other line is 6.19 mm from ours, so unlike I25 there is no
cross-pairing rescue here: C03's difference is a partition of the same band, not a naming swap.

The piece's whole clustering, for the record (`out/clusters.tsv`, same columns as the I25 table above):

| cluster | kept | pts | rad p5/p50/p95 | ax p5/p50/p95 | axsp | angbins/36 | edge_r | edge_cv | l2/l1 | l3/l1 | abs n.ax | abs n.rad | d kept min/med |
|---------|:----:|----:|----------------|----------------|-----:|-----------:|-------:|--------:|------:|------:|---------:|----------:|---------------:|
| c0 | yes | 23898 | 10.16/32.40/51.57 | 436.43/437.29/456.52 | 20.09 | 36 | 40.114 | 0.1571 | 0.3752 | 0.0432 | 0.9775 | 0.2086 | 4.780/7.668 |
| c1 (our Bl1's face) | yes | 17455 | 37.25/44.74/59.28 | 429.33/437.08/460.99 | 31.66 | 36 | 44.935 | 0.1623 | 0.2257 | 0.0445 | 0.6132 | 0.7893 | 4.780/6.048 |
| c2 (base plate) | no | 13499 | 7.73/24.36/32.47 | 427.82/431.04/431.61 | 3.79 | 36 | 32.457 | 0.0218 | 0.9599 | 0.0043 | 0.9982 | 0.0563 | 3.097/5.631 |
| c3 | no | 748 | 37.98/41.19/52.21 | 436.70/439.53/448.23 | 11.53 | 8 | 42.656 | 0.1247 | 0.0130 | 0.0008 | 0.6743 | 0.5204 | 1.459/2.623 |
| c4 | no | 612 | 50.19/53.08/55.72 | 447.33/450.63/453.42 | 6.08 | 3 | 55.797 | 0.0076 | 0.1993 | 0.0091 | 0.6627 | 0.7443 | 1.477/3.088 |
| c5 | no | 405 | 43.09/47.47/53.02 | 439.09/444.23/451.25 | 12.15 | 5 | 47.242 | 0.0804 | 0.0163 | 0.0004 | 0.4713 | 0.7294 | 1.377/2.649 |
| unclustered | -- | 14430 | 34.08/43.45/58.78 | 427.07/439.08/471.66 | 44.59 | 36 | 47.318 | 0.1538 | 0.5636 | 0.1101 | 0.7500 | 0.4646 | 0.080/1.806 |

Both kept clusters are broad sheets (36/36 azimuth bins, `edge_cv` 0.16) 4.78 mm apart -- two faces of a
thick wall, each carrying its own rim, with the base plate c2 as the flat the piece stands on.

#### Phase A classes

| lane | class | deciding evidence |
|------|-------|-------------------|
| C 03 Bl1 | **(K)** partition mismatch | Our line is the outer rim of the band we keep (c1, 22.03 mm wide, 0.70 mm from its p95 rim, 99.4% on a >108 deg boundary); the reference runs 3.6 mm in from that band's inner edge on material our merge left unclustered (90.0%) or dropped (10.0%). Two different boundaries of one band, not two contours of one edge. |
| I 25 Bl0 | **(K)** partition mismatch (label pairing) | Our line rides c0's single closed rim (0.98 mm, 46% ring share); the reference rides c1's rim and is 0.680 mm / 100% coverage from our *Bl1*. |
| I 25 Bl1 | **(K)** partition mismatch (label pairing) | Mirror case: our line rides c1's rim (0.98 mm, 40% ring), the reference rides c0's rim at 0.568 mm / 100% from our *Bl0*. |

**State of the I25 case, for the conservator (not closed here).** Both of our I25 lines are the boundaries of
the two faces our merge keeps, and both references are the boundaries of the same two faces, 0.57 and 0.68 mm
apart, each on the other's face. Our index is fixed by the classify swap, and on I25 that signal is as
unambiguous as anywhere in the corpus (face1 `interior_frac=0.9931` against face0 `0.0000`, the same shape of
evidence as the six pieces where our index and theirs agree). So either the corpus's `Bl0`/`Bl1` files for
I25 are inverted relative to ours, or our interior/exterior judgement is inverted for this one piece.
The first is the simpler reading, and it is a statement about the reference, not about the walk -- which is why
both lanes are (K) and not (W). Our own contribution to the difference is a label, not a line.

#### Pictures

`artifacts/pota293/png/` (mirrored in the run at `out/png/`, md5 in `out/png.md5`, 2300x1340, our line thick
green, the authors' thick dashed black, on the shaded mesh and on the extracted face, with a projection chosen
to resolve the failing stretch and a zoom):

`p293_C_03_Bl1.png`, `p293_I_25_Bl0.png`, `p293_I_25_Bl1.png` (Phase A), plus `p293_D_22_Bl0.png`,
`p293_D_27_Bl0.png`, `p293_D_27_Bl1.png`, `p293_E_16_Bl0.png`, `p293_H_02_Bl1.png`, `p293_H_10_Bl1.png`,
`p293_I_06_Bl1.png`, `p293_I_13_Bl1.png` (Phase B). The I25 pair shows the two loops crossing only in
projection -- 6.9 mm apart in 3D, on the two faces of one wall.

### Phase B -- the eight one-stretch lanes

Indices are along **our** line (dot i of n); the stretch is the longest contiguous run of our dots more than
2 mm from the reference, chosen by arc x mean gap (`out/phaseB.tsv`). `share` is that arc as a fraction of our
loop; `to mesh` is our dots' distance to the authors' own DS mesh. Classes are (i)/(ii)/(iii) as the amendment
defines them.

| lane | stretch (i0-i1 of n) | arc mm | share | max mm | mean mm | class | deciding surface evidence |
|------|----------------------|-------:|------:|-------:|--------:|-------|---------------------------|
| D 22 Bl0 | 39-49 of 125 | 18.0 | 8.07% | 5.719 | 4.335 | **(i)** reference is no boundary | The references' dots in this stretch are 8.07 mm (median) from any kept material and 57.9% of them have an *unclustered* nearest point: a straight chord across the 18 mm notch mouth. Our dots sit 0.081 mm on their own mesh -- we never leave the surface. |
| D 27 Bl0 | 16-28 of 56 | 21.6 | 21.24% | 9.921 | 6.378 | **(ii)** crease inside the face | 100% of their stretch dots have c0 as nearest kept material at 0.246 mm: the reference runs *inside* the face we keep, 6.4 mm from our line on average, following a crease/step of the face rather than its boundary. Our dots 0.023 mm on their mesh. |
| D 27 Bl1 | 0-10 of 58 | 18.0 | 17.08% | 15.586 | 9.757 | **(ii)** crease inside the face | 100% nearest c1 at 1.425 mm; the boundary statistic is 0% on their dots and 100% on ours -- they cross continuous material while we run its rim. Largest excursion in the family (15.59 mm). Our dots 0.045 mm on their mesh. |
| E 16 Bl0 | 46-75 of 111 | 52.2 | 26.04% | 11.893 | 7.869 | **(ii)** crease inside the face | 92.9% nearest c0 at 0.927 mm, 7.1% on dropped material; 92.9% of their dots sit on a >108 deg boundary of *their* run, i.e. they trace a second, inner boundary of the same face. Our dots 0.020 mm on their mesh. |
| H 02 Bl1 | 0-35 of 138 | 64.57 | 26.02% | 6.702 | 5.541 | **(iii)** our kept region spans a fold | 93.75% of their dots are nearest **c0**, the face our merge *dropped* for this lane, at 0.754 mm; only 6.25% land on our kept c1. The reference turns onto the other face at the fold, exactly as ticket 286 measured (their dots on smooth interior material at 8.85 deg max angular gap against the 14.13 deg fold). Our dots 0.034 mm on their mesh. |
| H 10 Bl1 | 67-89 of 90 | 39.6 | 24.25% | 5.678 | 4.422 | **(ii)** crease inside the face | 94.1% nearest c1 at 1.933 mm, 5.9% c0; their dots are 5.9% on a >108 deg boundary against 94.1% of ours. The reference steps 4.4 mm inside our face and runs 39.6 mm there -- ticket 286's step, on a crease of the face we keep. Our dots 0.052 mm on their mesh. |
| I 06 Bl1 | 85-103 of 181 | 32.4 | 9.94% | 5.071 | 3.450 | **(ii)** crease inside the face | 100% nearest c1 at 0.208 mm, 0% on a >108 deg boundary (ours 100%): the reference never leaves the face and never touches a rim -- it follows an interior crease while we follow the rim. Our dots 0.012 mm on their mesh. |
| I 13 Bl1 | 72-92 of 162 | 36.0 | 12.31% | 6.093 | 4.634 | **(ii)** crease inside the face | 68.75% nearest c1, 31.25% c0, median 0.295 mm to kept material; boundary share 68.75% on both sides. The reference swings across the fold between the two kept faces of this piece and back -- a crease traverse, not a boundary of the kept set. Our dots 0.010 mm on their mesh. |

Two readings the table fixes for the whole family. **Our line never leaves the surface**: on all eight lanes
our dots lie 0.010-0.052 mm (median) and 0.066-0.334 mm (max) from the authors' own DS mesh, 0.0% beyond
2 mm. And **the reference never leaves it either**: on all eight its dots are 0.21-1.93 mm from kept material
(except D22's chord, 8.07 mm). So no lane in this family is a case of one side floating; they all differ over
which curve of one surface is the edge.

On E16 the index origin rotated between runs (294 had 58-87, this draw 46-75) while the arc stayed 52.2 mm and
the mean 7.87 against 7.91: the loop's start index is not fixed, so indices are comparable within a draw, arcs
across draws.

#### Which of the three the walk could ever learn from the boundary set alone

Only (i), and only in the negative sense. A boundary set says *where material ends*; it cannot say where a
crease, step or fold *inside* continuous material is. In D 22 Bl0 the boundary set does contain the evidence
that the reference's chord is wrong -- there is no material within 8 mm of it, so a boundary-seeking walk
correctly refuses to draw it. In the other seven lanes the surface is continuous under both lines and the
difference is a curvature feature: the reference turns at a crease 0.2-1.9 mm inside the face we keep, or onto
a second face at a fold our merge joined across (H 02). The boundary set of the kept face contains no trace of
that feature, so a walk driven by boundaries alone has nothing to turn on and does the only consistent thing:
it traces the outermost boundary of the region it was given. That is what all eight rows show. The family is
therefore not a walk-logic bug that more boundary evidence would fix; to clear it the input has to carry
curvature (a crease/step detector on the kept face) or the merge has to stop joining across folds -- (iii) --
and neither is available from the boundary set alone.

### One mechanism or several

Eleven lanes, two mechanisms, and the split is by class:

- **Eight lanes are one mechanism** -- the walk follows the boundary of the whole kept region where the
  reference follows a feature inside it or a fold it turns at. Its surface cause divides three ways:
  (i) 1 lane (D 22 Bl0 -- a chord over a notch), (ii) 6 lanes (D 27 Bl0, D 27 Bl1, E 16 Bl0, H 10 Bl1,
  I 06 Bl1, I 13 Bl1 -- a crease or step inside the kept face), (iii) 1 lane (H 02 Bl1 -- our kept region
  spans the fold the reference turns into).
- **Three lanes are not the walk at all**, and are (K) on both sides of the check: I 25 Bl0 and I 25 Bl1 are
  one label-pairing mismatch counted twice (the same two closed rims, indexed oppositely by the two sides,
  0.57 and 0.68 mm apart -- at bar when read crosswise), and C 03 Bl1 is a partition of one band into outer
  and inner parts.

So the answer to the ticket's question: **one mechanism behind the eight one-stretch lanes, and two unrelated
causes behind the three different-contour lanes.** No further walk change should be argued from I25 or C03;
the eight-lane family will not yield to a boundary-routed fix at all, because in seven of the eight the
information needed to turn is not in the boundary set.

### Deviations

1. **Print-only patch in the build** (the one build deviation). `patches/276-merge-diag.patch` was applied to
   `mesh_processing_headless.cpp` so the census could see cluster labels; the job ran with `SFS_MERGE_DIAG=1`
   (`split` never used, so nothing was split). Committed source `459dabe145056489829804292710b382`, patched
   `d130da7fbcc6ed7cdecc900fb246f61b`, patch `ff3fc86fb58e28f9ad84f86e0d482640`, reverse dry-run exit 0, +122
   non-empty lines / -0, edge binary byte-identical to 294's. The eighteen re-scored lanes reproduce 292/294
   as tabulated above.
2. **Three lanes outside the reproduction rule, stated not reconciled**: E 16 Bl0 +0.104 mm (294 0.651,
   fresh 0.755), I 06 Bl1 -1.51 pp with n 181 against 180, I 13 Bl1 -1.64 pp with n 162 against 160. All three
   are lanes whose dot count moved; the six with unchanged counts reproduce within 0.040 mm / 0.41 pp. Cause:
   the unseeded 30-ray draw in the mesh stage, measured against each piece's own spread.
3. **`angbins` is not ticket 286's `bins` column.** Mine counts occupied 10-degree azimuth bins; 286 counted
   bins with >=5 points at high `abs n.axis`. Hence 286's H 10 c5 = 0 bins against my 15, and 23 against 22
   for H 10 c1. The two are not reconciled; the self-check against 286's published table (H 02 c0/c1, H 10
   c0/c5: size, abs n.ax, l3/l1, radii, axial range) matches to its printed precision -- `out/selfcheck286.txt`.
4. **C 03 Bl0 has no per-dot table.** Only the eleven lanes of record were dumped dot by dot; C 03 Bl0 was
   scored but not assigned. A `p293_stretch.py` that would have needed per-dot tables on all lanes was removed.
5. **The nine axis files were deleted with the geometry** -- they are copies of corpus inputs (`out/axis/`),
   not corpus; the corpus itself is untouched.
6. **Line 93 of this ticket says to leave the results uncommitted for the lead**; the dispatch brief instead
   orders a commit and push on `293-miss-families`, and the brief wins. The lead still owns the verdict, the
   index `verdict`/`human_note` cells and any merge.
7. **Nothing was unmeasurable** except the two items named above (C 03 Bl0 per-dot assignment) and the
   reproduction of the three moved lanes; both are stated rather than skipped.

### Where the numbers live

All under `/data/gpfs/projects/punim2657/SfSpp/runs/20261025-0456_3ada802_p293-census/out/` (md5 in
parentheses): `clusters.tsv` (`7acd46eb...`), `assign_summary.tsv` (`7c80a20c...`), `phaseB.tsv`
(`72aac2e2...`), `crosspair.tsv` (`b5569717...`), `census.json` (per-lane census and rim profiles),
`census/<piece>_Bl<k>.assign.tsv` (per-dot assignment for the three Phase A lanes), `selfcheck286.txt`,
`lanes_fresh.tsv` (18 lanes), `classify.tsv`, `pieces_run.tsv`, `png/` + `png.md5`, `source.md5`, `build.json`,
`GEOMETRY_DELETED.txt` (stage trees and all extracted geometry deleted, `STAGE_DIRS_REMAINING=0`,
`GEOM_FILES_REMAINING=0`; the nine ticket-276 cluster dumps in `out/diag/` are kept as text -- they are the
seven files over 1 MiB outside `bin/` and are the census record, not geometry).

Pictures are mirrored locally at `C:/PR/SfSpp_preprocessing/artifacts/pota293/png/` and `crosspair.tsv` at
`C:/PR/SfSpp_preprocessing/artifacts/pota293/`.


## Lead verdict (2026-10-25)

**Accepted.** The two families now have their "why", and one of them turns out not to be a family at
all. Seven points.

1. **Pot I 25 is a label inversion, not a contour difference.** The cross-pairing measurement
   (`out/crosspair.tsv`) is decisive and I checked it against two numbers that do not depend on the
   pairing algorithm: our Bl0 is 0.680 mm from their **Bl1** (coverage 100 / 100, max 1.420 mm) and our
   Bl1 is 0.568 mm from their **Bl0** (100 / 100, max 1.752), while the same-index pairs sit at 6.910
   and 6.951 mm with zero coverage both ways. The counts (58 against 60, 67 against 69) and the arc
   lengths (104.79 against 106.28, 120.57 against 124.26) pair **crossed** as well, so the result is not
   an artefact of the nearest-neighbour scorer. Each side draws both rims; the two lanes are one curve
   pair counted twice, and whoever's index is inverted, our line is the correct rim.
2. **Consequence for the tally, recorded and not applied.** If the conservator accepts the reference
   labels as swapped on this piece, both Pot I 25 lanes are at bar by a wide margin and the corpus moves
   from **281 of 292 to 283 of 292 (96.2% to 96.9%)**. I have not changed the headline; this is the same
   class of ruling as Pot J 09 and it is the conservator's call, not mine.
3. **Pot C 03 Bl1 (K) is confirmed by a route independent of ticket 279.** Our line is the outer rim of
   the exterior wall we keep (0.700 mm from its p95 rim, 35.1% ring share, 99.41% on a boundary); theirs
   runs 10.51 mm inside that rim and 3.58 mm in from the band's inner edge, on material the mesh stage
   left unclustered (90.0%) or dropped (10.0%). That is the same dropped base band 279 identified as the
   authors' own Surface_1, measured here from cluster membership instead of from surface distance. Two
   methods, one verdict.
4. **The eight one-stretch lanes are one mechanism with three surface causes**: (i) one, D 22 Bl0, where
   the reference draws an 18 mm chord over a notch mouth and its own dots are 8.07 mm from any kept
   material; (ii) six, D 27 Bl0, D 27 Bl1, E 16 Bl0, H 10 Bl1, I 06 Bl1, I 13 Bl1, where the reference
   runs inside continuous material of the face we keep (0.208-1.933 mm from it, 0-6% of its dots on a
   boundary against 94-100% of ours); (iii) one, H 02 Bl1, where our kept region spans the 14.13 deg fold
   ticket 286 measured and the reference turns at it.
5. **The load-bearing sentence is the learnability answer, and it closes a question.** Only (i) is
   visible in a boundary set, and only negatively -- no material under the chord. In the other seven the
   turning feature lies inside continuous material, so the boundary set carries no trace of it. A
   boundary-routed change (another walk rule, another stop rule, another seed) therefore cannot close
   this family; it would need curvature evidence on the kept face, or a merge rule that refuses to join
   across a fold. Recorded so the next session does not build a walk arm for it.
6. **Reproduction and the three exceptions.** Six of the eleven lanes reproduce ticket 294 within the
   pre-set rule; E 16 Bl0 (+0.104 mm), I 06 Bl1 (-1.51 pp) and I 13 Bl1 (-1.64 pp) are outside it, and
   they are exactly the three whose dot count moved -- the unseeded 30-ray mesh draw, whose piece
   dependent spread (0.1-0.9 mm) the project already records. Stated rather than reconciled, which is
   the right handling; a difference that small is the instrument, not a finding.
7. **Deviations accepted, one ticket line superseded.** The print-only ticket-276 diagnostic patch is
   acceptable on the evidence given (edge binary byte-identical to 294's, +122/-0 lines, reverse dry-run
   exit 0, eighteen lanes reproducing); the `angbins` against ticket 286's `bins` definition difference
   is disclosed and unreconciled (`out/selfcheck286.txt`); C 03 Bl0 has no per-dot table because only
   the eleven lanes of record were dumped. Ticket line 93 says to leave results uncommitted for the lead
   to commit -- my dispatch order required a commit on the branch, so **that line is superseded**; the
   verdict, the index fields and the merge remain mine.

Verified independently before landing: branch clean at `275e47d` and equal to `origin`, run directory
`20261025-0456_3ada802_p293-census` present with `out` at 21 MB and no geometry left, index row appended
with verdict and human_note empty, and both figures read at full size -- the Pot I 25 panel shows our green
loop sitting exactly on the boundary of the surface drawn while the authors' black loop lies outside it, on
the other face, which is the inversion seen rather than argued.

No code, default, threshold or algorithm changed. Open for the conservator: whether the Pot I 25 reference
labels are accepted as swapped (which would make the tally 283 of 292), and whether the three (K) lanes stay
in the bar as references at all.
