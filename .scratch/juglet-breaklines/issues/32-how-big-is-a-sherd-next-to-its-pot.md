# 32: How big is a sherd next to its pot, and does the angle follow that ratio?

**Status:** done
**Working in:** chat on Thinkbook16 (2026-10-27)
**Branch:** 32-how-big-is-a-sherd-next-to-its-pot, in /c/PR/worktrees/sfs/32
**Answers:** U19
**Blocked by:** none
**Blocks:** none

## Why this ticket exists

Ticket 30 measured the angle the region growing has to work with, and showed the sherds carry
4-27x the local curvature the pot piece does. Two explanations survived: the points are sparser,
or the sherds are small relative to the vessel they came from. Ticket 30 and the reply after it
killed the first one by measurement — the Juglet at native density has point spacing of
0.211-0.258 mm against Pot A's 0.223 mm, and still carries 7-15 deg. The second explanation has
never been measured.

There is a catch to settling it. The radius the angle follows today is 0.78-5.13 mm, while the
Juglet's own vessel radius is 32.5 mm (65 mm vessel). So the quantity being measured today is
local folding, not the pot's shape. If the angle is to be tuned on "how big is the sherd next to
its pot", the radius has to be measured over a window big enough to see the vessel, and no
measurement we have varies the window in physical units.

## What to measure

**Part A — sizes, from geometry and ground truth.**

For each Juglet sherd (9) and each Pot A piece (8, the ones this project controls against):

- the sherd's own extent: the diagonal of its bounding box, in mm, from its cloud;
- the sherd's surface area, in mm2, from its mesh (sum of face areas);
- **the vessel's own extent**, in mm, computed from the ground truth:
  - Juglet: from `Dataset/Juglet_GT/Juglet_Piece_1..9_T.txt` plus the nine meshes, place every
    piece at its reference pose and take the extent of the union. Report the extent and the method.
    This should land near 65 mm — the number every seating tolerance in this project is quoted
    against — and if it does not, that is a finding, not an error to fix silently.
  - Pot A: the same procedure from `Ground Truth/Pot_A_simple_graph.txt` and the released
    transforms. **This number does not exist anywhere in this workspace or in the paper**
    (checked: no Pot A dimension in `C:/PR/papers/text/sfspp-2502.13986v1.md`), so it is the
    first measurement of it.
- **the ratio: sherd extent / vessel extent**, per piece.

**Part B — the same statistic at a physical window instead of a neighbour count.**

Today the curvature radius is fitted over the 30 nearest neighbours, whose physical size differs
between clouds (about 0.68 mm on the pot, 1.3-2.2 mm on the crushed sherds). Replace "30 nearest"
with "every point within w mm", for w = 1, 2, 3 and 5, and report per piece and per window:

- the median number of neighbours actually in the window;
- the median local curvature radius (same quadric fit as ticket 30's part A: local PCA frame,
  radius = 1 / max(|k1|,|k2|)), with its p25 and p75 and the share at the flat cap;
- the median neighbour-normal angle over pairs inside the window (ticket 29's arithmetic);
- the mesh-normal noise floor at that window (median folded angle to the nearest mesh vertex
  normal), so noise and signal stay separable.

**Part C — the two arms that make the pot like-for-like.**

Measure Pot A twice: at its native density, and subsampled to the Juglet's native spacing
(~0.25 mm), so the window contents are comparable. If the pot's numbers move between those two
arms, that movement is the price of density and belongs in the answer.

## Data and arms

- Juglet clouds: derived from the nine meshes as the pipeline derives them (ObjToPcd), not from
  `Dataset/Axes/Juglet` and not from the swept 2026-09-25 bundle, which is gone.
- Pot A clouds: the released corpus clouds under
  `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp` (read-only).
- Arms: `J` (Juglet, mesh-derived, native), `PA_native` (Pot A released cloud, native),
  `PA_025` (the same subsampled to 0.25 mm). Windows 1/2/3/5 mm on every arm.
- Everything runs on compute nodes. Nothing runs on the laptop or the login node.

## Evidence to produce

1. `out/sizes32.tsv`: piece, arm, n_points, extent_mm, area_mm2, vessel_mm, ratio, method notes.
2. `out/windows32.tsv`: piece, arm, window_mm, n_neighbours_median, rho_median_mm, rho_p25_mm,
   rho_p75_mm, share_at_cap, angle_p50_deg, angle_p10_deg, angle_p90_deg, noise_floor_deg.
3. One figure, 300 dpi, with a scale note: panel 1 the angle against the sherd/vessel ratio at
   each window (pot and sherd points distinguishable), panel 2 the fitted radius against the
   window width, one line per piece, with the vessel radius drawn as a reference line.
4. The vessel extents for both pots, with the command and the method that produced them.
5. Input md5 lists before and after; `/opt/sfs-pristine` recorded ABSENT if absent; corpus
   unchanged, proven by comparing the two md5 lists.
6. Geometry deleted at the end with a counted record (files, bytes, per extension), written
   before the delete; the tables, figure and logs kept.
7. An index row with `verdict` and `human_note` left EMPTY.

## Acceptance

- Both tables exist, one row per piece per arm per window, no row with a missing value silently
  dropped (a value that cannot be computed is written as `na` with the reason in a column).
- The vessel extents are derived, not assumed: the Juglet number is computed from the ground truth
  in this ticket, not copied from a note.
- The figure resolves what it claims to show — legible at the stated scale, with the pot and the
  sherds told apart, and the vessel-radius reference line labelled.
- Every number is traceable to a command in the run directory.
- No tracked source file changes. If the measurement cannot be made without changing tracked
  source, stop and report instead.
- Run directories under `/data/gpfs/projects/punim2657/SfSpp/runs/`, named by the usual
  convention; at most 3 jobs; CRLF checked before every submit.

## What this cannot settle

It will not say which threshold to use. It measures whether the ratio predicts the angle — the
reading is the lead's, and the threshold decision comes after it. It also cannot separate "the
sherd is a big piece of a small pot" from "the sherd is mostly broken edge", because both produce
a tight fitted radius; the ratio and the edge-fraction would have to be measured together for that,
and the edge fraction is not in this ticket.

## Lead reading — 2026-10-27 (verified first-hand, not taken from the worker's report)

### The question this answers

The conservator asked (2026-10-27) whether the sherd-to-vessel size ratio could be the reason the
Juglet's neighbourhood angles are high, and whether it might be "a measurement we can use to tune the
angle". Both halves are answered below, and one of them is answered no.

### The vessel, measured for the first time

No vessel size was recorded anywhere for either pot. Applying each pot's own ground-truth transforms to
its pieces and taking the union bounding box gives the assemble:

| pot | sides (x, y, z) mm | cube diagonal mm | other two conventions tried |
|---|---|---|---|
| Juglet | 41.508968 / 36.772109 / **65.000479** | **85.441470** | 1501.230117 and 1352.150514 |
| Pot A | 193.418983 / 194.118357 / 56.476264 | **279.789935** | 1310.093549 and 1130.251195 |

The convention is identified rather than chosen: the alternatives put the pieces 1.3-1.5 m apart, i.e.
they scatter the vessel, and only Rp+t assembles it. Independent agreement on the Juglet: the 65.00 mm
side is the vessel height this project has been quoting all along, and the corner-diagonal reading of
that side matches to 0.0005 mm.

**Caveat on the Juglet's ground truth, recorded not explained.** In the assembled pose, the piece nearest
to a Juglet sherd is its *declared* mate for only 6 of 9 pieces, and undeclared pairs are closer than
declared ones (median 0.039886 mm against 0.323939 mm). Pot A is 8 of 8 with declared mates at
0.011250 mm and undeclared neighbours 75 mm away. So the Juglet's transforms are sound enough to build a
compact 65 mm vessel, while its adjacency graph under-declares which pieces touch. That matters for
scoring joins, not for the size measurement.

### The answer to the size-ratio question: the ratio does not separate the pieces that work from those that fail

Sherd extent (bounding-box diagonal) over vessel extent:

| | ratios |
|---|---|
| Juglet | 0.737981, 0.331324, 0.392970, 0.374965, 0.497243, 0.461820, 0.515052, 0.403995, 0.275003 (mean 0.443) |
| Pot A | 0.616893, 0.490349, 0.472599, 0.415840, 0.432089, 0.471820, 0.209358, 0.193265 (mean 0.413) |

The two ranges overlap heavily, the means are 7 % apart, and the two Juglet pieces that produce no
surface at all (2 at 0.331, 9 at 0.275) are **relatively larger** than two Pot A pieces that work
perfectly well (07 at 0.209, 08 at 0.193). Whatever governs the angle, the sherd/vessel ratio is not it,
and tuning a threshold on that ratio would not have the physical meaning it looks like it has.

### Sparsity, asked again at fixed physical windows: also no

Ticket 30 answered this on the 0.6 mm cloud; this ticket asked it without a neighbour count at all, at
windows of 1, 2, 3 and 5 mm:

| | neighbours at 1 mm | median angle at 1 mm | at 5 mm |
|---|---|---|---|
| Juglet | 15-32 | 19.8-25.8 deg | 49.9-69.7 deg (469-684 neighbours) |
| Pot A | 135-1718 | 0.84-1.60 deg | 4.9-30.4 deg (3403-61314 neighbours) |

At every window the vessel's angle is an order of magnitude above the pot's, on clouds whose point
spacing at native density is the same 0.21-0.26 mm against the pot's 0.223 mm. Finance and density are
not what the angle is measuring.

### What it is measuring: local folding, at a radius far below the vessel

Fitted curvature radius at a 1 mm window: Juglet 0.67-5.25 mm, Pot A 13.8-27.8 mm. The vessel radii are
42.72 mm and 139.89 mm. Both sets are far below their own vessel radius, so the angle tracks how sharply
the surface turns within a millimetre or two — on these sherds, the fold at a broken edge — and not the
shape of the pot. That is the reason no ratio to the vessel can anchor it.

### The 50-point floor, asked of the pipeline itself

The conservator's proposal was that piece 2 may simply never reach 50 points. The pipeline says it does
not, and says what happens when the floor is forced down (ticket 23's switches, floor set to a fraction
of the piece's own point count):

| piece | floor | clusters | largest | one-surface write | its extent | its coverage |
|---|---|---|---|---|---|---|
| 2 | 72 / 48 | 0 (no count line printed at all) | — | — | — | — |
| 2 | 24 | 1 | 32 | 220 points | 11.49 mm | 28.4 % |
| 9 | 59 / 39 | 0 | — | — | — | — |
| 9 | 20 | 1 | 21 | 277 points | 13.76 mm | 42.5 % |
| 3 | 98 / 65 / 33 | 1 | 289 | 1115 points | 31.41 mm | 92.6 % |

So the floor is exactly the mechanism that turns "nothing" into "no surface" — the conservator was right
about that — and lowering it does make the pipeline write a surface for pieces 2 and 9. But what it
writes is a corner patch: 11.5 mm and 13.8 mm across, on sherds 28.3 mm and 23.5 mm wide.

The same question on the replica, where the floor can be set independently: at a floor of 10 points the
vessel's largest surviving region is 46 points for piece 2 (8.4 mm, 20 % coverage) and 16 points for
piece 9 (4.1 mm, 7 % coverage), while Pot A 07 keeps its 3093-point region (36 % of the cloud, 52.8 mm)
among 18 survivors. Lowering the floor gives gravel on the vessel and the same face on the pot.

### One thing I did not expect, and am not yet willing to record as a conclusion

This ticket's noise column measures the normals **as shipped in the point cloud**. Ticket 30's measured
the **pipeline's own** re-estimated normals. Against the same meshes they are not the same number: the
shipped normals sit 0.414-1.635 deg from the mesh on the Juglet and 0.455-0.616 deg on Pot A, while the
pipeline's sit 3.39-8.10 deg on the Juglet (ticket 30, table A). Both readings are mine, on both sides;
what differs is which producer's normals were measured.

If that gap is real it is a better lead than anything else in this ticket: the shipped clouds carry
normals good to about 1 deg, the growth's admission test is 3.4 deg, and the normals it actually uses are
4-6 deg off the same surface. It is not yet a conclusion because the two numbers come from different
runs with different clouds on one side, and the comparison has not been made inside a single job on the
same points. It is recorded here as the next thing to measure, not as a finding.

### Where this ticket's jobs went wrong

Six jobs against a three-job cap (four after I raised it): 33869737 FAILED 5:0 (selftest caught an ASCII
PCD reader bug before any measurement), 33869853 FAILED 5:0 (a manifest check hard-coded 1,000,000 points
where Pot A 01 has 999,810 and 03 has 1,000,087), 33869854 COMPLETED 0:0 but produced **nothing**
(`xargs -d "\n" -n 2` split inside a line), 33870012 FAILED 1:0 (`OUT` used before it was set under
`set -u`), 33870148 COMPLETED 0:0 6:30 with 69 of 70 cells, and 33870776 COMPLETED 0:0 1:09 recomputing
the one missing cell. The miss was the Pot A vessel extent: the corpus file is `Pot_A_simple_graph.txt`
and the instrument asked for `PotA_simple_graph.txt`. The fixup job copied the other 69 cells
byte-for-byte and recorded the superseded md5s.

### verified: the artefact behind each load-bearing claim

- verified: `cat out/vessel32.tsv` -> Juglet Rp+t 85.441470 mm (41.508968 / 36.772109 / 65.000479), pR+t 1501.230117, inv 1352.150514; PotA Rp+t 279.789935 mm (193.418983 / 194.118357 / 56.476264), pR+t 1310.093549, inv 1130.251195.
- verified: same file, mate columns -> Juglet n_closest_is_mate 6, mate_min_median 0.323939, nonmate_min_median 0.039886; PotA 8, 0.011250, 75.093122.
- verified: `awk` over out/sizes32.tsv -> Juglet ratios 0.737981 / 0.331324 / 0.392970 / 0.374965 / 0.497243 / 0.461820 / 0.515052 / 0.403995 / 0.275003; PotA 0.616893 / 0.490349 / 0.472599 / 0.415840 / 0.432089 / 0.471820 / 0.209358 / 0.193265.
- verified: `awk` over out/partE32.tsv -> Piece_2 floor=24 clusters=1 sizes=32, single write surf0=220 diag0=11.49 cov0=0.2838; Piece_9 floor=20 sizes=21, surf0=277 diag0=13.76 cov0=0.4245; Piece_3 floor=33/65/98 sizes=289, surf0=1115 diag0=31.41 cov0=0.9264; floors 48/72 (piece 2) and 39/59 (piece 9) give clusters=0 with clusters_lines=0.
- verified: `awk` over out/floorsweep32.tsv -> Juglet_Piece_2 floor 10 largest 46 (frac 0.017934, 8.3805 mm, coverage 0.204678); Juglet_Piece_9 floor 10 largest 16 (0.007641, 4.1089, 0.066380); Pot_A_Piece_07 arm PA floor 10 largest 3093 (0.359735, 52.8084, 0.484066) with 18 survivors.
- verified: `awk` over out/growth32.tsv -> Juglet_Piece_2 J regions 1906 largest 46 n_ge_50 0; Juglet_Piece_9 J regions 1562 largest 16 n_ge_50 0; Pot_A_Piece_07 PA_025 regions 2844 largest 18315 n_ge_50 6; fail_curv_total 0 on every row.
- verified: `cat out/anchors32.tsv` -> 24 rows, every one MATCH (B/J2 regions 661, largest 36, fail_angle 4703; B/J3 survivors_50 [169, 99]; E/J7 regions 4054, largest 1162; PA survivors_50 [3093, 2850, 203, 170, 134, 120, 73, 71]).
- verified: `wc -l out/windows32.tsv` -> 101 lines (100 data rows, header carries noise_floor_deg); `grep -n mesh_floor instruments/partB32.py` -> :149 `A30.mesh_floor(pts, c["nrm"], verts, vnorm, rng)` and `load_cell` returns `cl["nrm"]` straight from `io32.read_pcd`, i.e. the normals as shipped, not re-estimated.
- verified: `sacct -j 33869737,33869853,33869854,33870012,33870148,33870776` -> FAILED 5:0 / FAILED 5:0 / COMPLETED 0:0 00:01:09 / FAILED 1:0 / COMPLETED 0:0 00:06:30 / COMPLETED 0:0 00:01:09.
- verified: `diff -q` of out/inputs_before.md5 against inputs_after.md5 (207 rows) and of corpus_before.txt against corpus_after.txt (1803 rows), in both the grid run and the fixup run -> identical; out/pristine.txt records /opt/sfs-pristine ABSENT.
- verified: `ls -l out/figure32.png` -> 676860 bytes, PNG header 3900x1620; fetched to C:/PR/SfSpp_preprocessing/artifacts/juglet-p32/figure32.png and opened. Panel A plots the angle against the ratio with the four window widths: the vessel's points sit at 11-70 deg, the pot's at 0.8-6 deg, at overlapping ratios — the separation is by vessel, not by ratio. Panel B plots fitted radius against window: the vessel's curves run 0.67-10.79 mm and the pot's 13.8-49.6 mm at 1 mm, converging near 5 mm, both far below their vessel-radius lines (42.72 and 139.89 mm).
- verified: mesh_processing_headless.cpp:738-758 (`getNormalsOnSurface`) reads x, y, z **and the three normal components** from file and then computes only the curvature, keeping the normals as given; :635 prints the neighbour count used by the step that produced them.

### What this does not settle

It does not say which threshold to use, and it does not say the ratio is useless — a ratio to the vessel
is still the right way to state how big a sherd is, it simply does not predict this angle. It cannot
separate "the sherd is a big fraction of a small pot" from "the sherd is mostly broken edge": both give a
tight fitted radius, and the edge fraction was not measured here. It says nothing about pots other than A
and the Juglet, and nothing about the three Juglet pieces (3, 8, 9) whose failure is not the floor. The
shipped-versus-pipeline normal gap is stated as a lead, deliberately not as a result, because the two
numbers came from different jobs.
