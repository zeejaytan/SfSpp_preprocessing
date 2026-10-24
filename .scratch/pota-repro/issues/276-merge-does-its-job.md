# 276 — Does the cluster merge do the job Appendix A gives it?

Answers: E1
Status: results-in (Phase 0b and Phase 1 done and landed in 91f87a8; Phase 2 done — the 200-pair-cap hypothesis is overturned, Step 3 rhoInN is the rejecting test; Phase 3a done — the Pot C 03 Bl1 mesh loss survives theta 3.4 unchanged, it is a d>2.4 mm band the merge never sees, not a theta artifact; Phase 3 held)
Working in: C:/PR/worktrees/sfs/276 + Spartan runs/ directory; main source read-only
Needs-eye: no

## Why

The paper gives cluster merging one job: repair over-segmentation. Appendix A
(C:/PR/papers/text/sfspp-2502.13986v1.md:462-479, TABLE I at :464-473) opens with
"a single continuous surface may become over-segmented into multiple clusters".

Our port is faithful in structure — mergePaper234 (mesh_processing_headless.cpp:1929-1984)
with tryMergePair234 (:1864-1927) implements Alg. 1 Step 1 (boundary pairs within rhoD,
at least 3), Step 2 (k2-average normals + curvature, rhoN/rhoC), Step 3 (internal median
point, rhoInN/rhoInC) and loops to a fixpoint (:1942-1983). It prints the paper's own
parameters, so the settings are the paper's.

What it has almost never done on our data is merge:

| piece | clusters before | after | merges fired | source |
|---|---|---|---|---|
| Pot C 01 | 9 | 9 | 0 (one pass) | mesh_Pot_C_01.log |
| Pot J 01 | 7 | 6 | 1 (162 into 332) | mesh_Pot_J_01.log |
| Pot D P03 | 9 | 9 | 0 | ticket 270 |

And the top two clusters saturate at 77.5% on Pot C 01 (face0 56833 + face1 49245 of
~136880 points), so the remaining seven clusters are never joined to anything at all.

Two readings are possible and nobody has tested which is true:

1. The remainder are genuinely separate material — detached lumps, a base fragment,
   the break face — which the merge is right to leave alone, and the merge is healthy.
2. The remainder are pieces of one continuous surface — exactly the case Appendix A
   exists for — and the merge is failing to do its paper job on them.

This is a different question from the one behind tickets 273 and 275. There, the merge
could not help: it joins mesh clusters, while the walk eats boundary-dot lumps. Here we
ask whether the mesh stage is repairing its own segmentation at all.

## The question

Does mergePaper234 join the clusters Appendix A says belong to the same continuous
surface, and keep apart the ones it says do not?

## Phase 0b (added by the lead, 2026-10-24) — where does the missing 22.5% go?

Read-only, needs no build, and it should run before the phases below.

The mesh logs record that the two classified surfaces hold only 77.49% of the cloud on
Pot C 01 ("Points in two clusters / Total Points in pointcloud: 77.4892%", face0 56833 +
face1 49245 of ~136880). The other 22.5% never enters a surface, and the edge stage only
ever sees the surfaces. Nothing downstream can see what was dropped.

Hypothesis, to verify: part of every "real unreached arc" the edge stage shows is not
missing because of the walk but because it never became surface. Candidates, all
single-lump bags with no debris to blame: Pot H 02 Bl1 (73.2% ours / 74.5% author-side),
Pot H 10 Bl1 (68.8 / 76.1), Pot C C03 Bl1 (47.6 / 47.5).

Test, on those three pieces:
1. From the mesh run's own cloud, label every point by post-merge cluster and by final
   surface (Surface_0 / Surface_1 / neither).
2. Map every dot of the author's Breakline_*.pcd for that piece to its nearest mesh point
   and record that point's label.
3. Report, per piece and per lane, the share of author dots landing on a dropped cluster,
   and whether that share matches the uncovered stretch. Report every dropped cluster's
   size and its author-dot count.

Verdict rule: if the uncovered stretch is dominated by author dots whose nearest mesh
point is in a dropped cluster, the missing arc is a mesh-stage loss and the merge is the
suspect. If those dots land on Surface_0/1 points the walk never reached, the loss is at
the edge stage after all and this ticket's answer is "merge innocent, extent family".

## Phase 1 — positive control by deliberate over-segmentation

Nobody has ever handed this code a case where merging is the right answer.

Take one piece whose top-two classification is stable (Pot C 01; Pot D P03 at
theta = 3.4 as the control). Split its single largest cluster in two by position (a plane
through that cluster's centroid), keep every other cluster unchanged, and hand the
result to mergePaper234.

- PASS: the two halves are merged back, the cluster count returns to the unsplit value,
  and the small clusters keep the decisions they had in the unsplit run.
- FAIL: the halves are not rejoined, or a pair rejected before is now accepted.

The cut is through a connected cloud, so the halves are guaranteed to have boundary
points within 1 mm of each other and the "at least 3 pairs" test is satisfiable by
construction. A FAIL therefore isolates the normal/curvature tests as the blocker.

## Phase 2 — which criterion rejects, per real pair

Instrument tryMergePair234 to print, for every cluster pair, one of
`pairs<3 | rhoN | rhoC | rhoInN | rhoInC | accepted` with the measured value and the
threshold, in Appendix A's own vocabulary.

Pieces: Pot C 01, Pot J 01, Pot D P03 (theta = 3.4 sheets), plus Pot H P01 and P02 from
the rollout misses.

Deliver the rejected-pair table and, for each piece, how many clusters are larger than
say 5% of the largest. State plainly whether the dominant rejection is "fewer than 3
boundary pairs" (clusters genuinely far apart, merge innocent), a normal test, or a
curvature test.

## Phase 3 — audit our reading of Appendix A (read, do not tune)

Three places the code goes beyond what the paper spells out. For each, say defensible or
divergence, with line numbers:

1. **Aggregate vs per-pair normals.** tryMergePair234 averages the k2-neighbour normal
   over ALL boundary pairs first, then compares the two cluster-level means
   (mesh_processing_headless.cpp:1903-1914). The paper says "for each boundary point, an
   average normal is computed using k2 neighbors"
   (C:/PR/papers/text/sfspp-2502.13986v1.md:477) — per-pair is the natural reading.
   Aggregation hides per-pair mismatches, so our version merges MORE readily, not less.
2. **Units.** rhoD = 1.0 is compared against a squared point distance in cloud units
   (:1888). State the cloud's units and what 1.0 means physically here (mm).
3. **Pair enumeration.** The 200-pair cap (:1884) and taking only the single nearest
   partner per point of the smaller boundary set (:1887).

## Phase 0b results — where the 22.5% goes, and which lane loses what

Run dir: `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1121_0ab0935_p276-merge`
(`out/<TAG>/` holds the mesh log, the written surfaces and the label dump; `stage/<TAG>/Dataset/`
holds the input copies; `a276b.py` / `a276c.py` hold the analysis). Job 33736769 (7:06,
all EXIT=0). Binary `MeshPreprocessingHeadless` md5 `fd370696d7ff738d1b1b9b5e1c5caa45` from
patched source md5 `999721b81e0e80dad35ed70ae8242f4d` (plain 0ab0935 source is
`459dabe145056489829804292710b382`; the patch is +118 lines, 0 deletions).

Diagnostic switch: **SFS_MERGE_DIAG**, read once at mesh_processing_headless.cpp:2049 inside
`mergeDiagMode276()` (helper block :2039-2156), called from the hook at :2286-2296 inside
`if (paperChain) {`. Unset, empty or "0" returns an empty string and every branch is skipped;
`=1` writes the label dump, `=split` also runs the Phase 1 artificial split.
Every run sets `SFS_AXIS_FILE` and `SFS_PAPER_THETA=4.0` (these trees were meshed at 4.0);
every log prints the axis classify line, never "no SFS_AXIS_FILE, keep size order".

### What is deterministic, and what is not

Clustering is deterministic and my reruns reproduce each tree's own `mesh.log` exactly
(Pot_H_02 13 clusters then "pass 1 done: 12 clusters", two-cluster 68.0738%; Pot_H_10 11 then 9,
53.0848%; Pot_C_03 10 then 9, 59.4321%; Pot_C_01 9, 77.4892%; face0/face1 sizes identical:
17193/14189, 4532/4167, 23709/17695, 56833/49245). The written sheets are **not**
byte-reproducible, and the mechanism is now known: `improveSurfaceBoundaryByFittingBSplineSurface`
(:810) draws `pcl::RandomSample<pcl::PointXYZ> rs; rs.setSample(10000);` at :829-833 and fits the
B-spline to that fresh random 10k sample. Pot_H_10 happened to come out byte-identical to its
tree (Surface_0 `45221f30977455980162fbbf4aa4306f`, Surface_1 `7b341d91a0d96941d13d20588745b230`),
Pot_H_02 did not (Surface_0 same count 35122, max|dxyz| 77.337 row-wise), Pot_C_03 differed
slightly. All label claims below are therefore made on cluster labels, which are stable.
Inertness of the switch, measured on identical inputs (C01_diag vs C01_nodiag): identical
"Number of clusters is equal to 9", 77.4892%, "pass 1 done: 9 clusters",
"classify: face0 n=56833 ... face1 n=49245".

### The table

| piece | lane | edge score n / med / cov ours→author / cov author→ours | mesh pts | clusters | kept s0 / s1 | dropped | unclustered | where the uncovered author dots sit |
|---|---|---|---|---|---|---|---|---|
| Pot_H_02 | Bl1 | 138 / 0.663 / 73.19 / 74.45 | 46100 | 12 | 17193 / 14189 | 8358 (18.1%) | 6360 | kept surface 34, dropped 0 |
| Pot_H_10 | Bl1 | 96 / 0.716 / 68.75 / 76.14 | 16387 | 9 | 4532 / 4167 | 3985 (24.3%) | 3703 | kept surface 17, dropped 0, unclustered 4 |
| Pot_C_03 | Bl1 | 124 / 2.028 / 45.16 / 43.33 | 69666 | 9 | 23709 / 17695 | 16212 (23.3%) | 12050 | **dropped 68**, kept 0 |
| Pot_C_01 (control) | Bl1 | not re-scorable — tree deleted, see incident | 136894 | 9 | 49245 / 56833 | 20112 (14.7%) | 10704 | kept surface, 227 of 230 author dots on s1 |
| Pot_H_02 | Bl0 | 153 / 0.680 / 100.00 / 100.00 | 46100 | 12 | 17193 / 14189 | 8358 | 6360 | uncovered 0 |
| Pot_H_10 | Bl0 | 98 / 0.642 / 100.00 / 100.00 | 16387 | 9 | 4532 / 4167 | 3985 | 3703 | uncovered 0 |
| Pot_C_03 | Bl0 | 238 / 0.738 / 99.58 / 99.48 | 69666 | 9 | 23709 / 17695 | 16212 | 12050 | uncovered 1 |
| Pot_B_01 (control) | Bl1 | **void** — tree deleted before the run (incident) | — | — | — | — | — | — |

Per-cluster author census (cluster size → author dots within 2 mm; `*` marks the cluster that
carries the lane's uncovered arc; `uncl` = points the clustering deleted outright):

| piece / lane | kept s0 | kept s1 | dropped clusters carrying author dots | uncl |
|---|---|---|---|---|
| Pot_H_02 Bl1 | 17193 → 0 | 14189 → 137 | c4 1023→15, c5 596→6, c6 580→26, c9 197→11 | 6360 → 113 |
| Pot_H_10 Bl1 | 4532 → 0 | 4167 → 88 | c3 817→23, c4 778→13, c5 256→16 | 3703 → 82 |
| Pot_C_03 Bl1 | 23709 → 0 | 17695 → **5** | ***c2 13474 → 119***, c8 179→17 | 12050 → 120 |
| Pot_C_01 Bl1 (control) | 49245 → 0 | 56833 → 227 | c3 672→37, c4 659→26, c5 459→2, c6 365→18, c7 323→13, c8 290→14 | 10704 → 230 |
| Pot_C_01 Bl0 (control) | 49245 → 193 | 56833 → 0 | c3 672→28, c4 659→23, c5 459→16, c6 365→14, c7 323→11, c8 290→12 | 10704 → 211 |

On Pot C 01 the biggest dropped cluster (c2, 17344 points) carries **no** author dot on either
lane, and the two kept clusters carry both rims.

### Verdict

The three off-bar lanes split into two different failures. On Pot H 02 Bl1 and Pot H 10 Bl1 the
mesh stage supplies the rim — the kept Surface_1 carries 137 of 137 and 85 of 88 author dots, and
every uncovered author dot's nearest mesh point is on a kept surface — so those missing arcs are
edge-stage misses, not mesh losses; the 18%/24% of the cloud dropped there holds no author rim.
Pot C 03 Bl1 is the opposite: the kept Surface_1 carries 5 of the lane's 120 author dots while a
single dropped cluster of 13474 points carries 119, all 68 uncovered author dots have their
nearest mesh point inside a dropped cluster, and the uncovered stretch is exactly that arc — a
mesh-stage loss, the arc never reached the edge stage, so no walker or stop-rule work can recover
it. Pot C 01, the piece the 22.5% question came from, is not a mesh loss at all: both rims sit on
the kept surfaces, so its dropped share is other geometry and its theta-4.0 collapse belongs to
the edge stage, consistent with ticket 275. The next ticket is about the cluster split / merge
decision on Pot C 03, not about the walker.

### Incident — the corpus cleanup deleted the staging trees mid-run

The `pota*` staging corpus is being deleted while this ticket runs (the cleanup's own records sit
in `SfSpp/runs/`: `pota-wave-{1,2,3}.list`, `pota-input-tier-wave{1,2,3}.tsv`,
`pota-root-inventory-20261024.md`, whose census records the user decision of 2026-10-24 that
"everything goes, including the staged inputs"; `ls -d pota*` went from 460 entries to 149).

- `pota253_paper_Pot_B_01` was emptied at 2026-10-24 11:31:01, in the middle of job 33736769, so
  the Pot B 01 control produced nothing (its `mesh.log` holds only
  "Total time elapsed: 0.00132091 seconds") and cannot be rerun — the inputs no longer exist.
- `pota257_paper_Pot_H_02`, `pota257_paper_Pot_H_10`, `pota251_paper_Pot_C_03`,
  `pota251_paper_Pot_C_01` and `pota271T1_P03_FULL` (the Pot D P03 Phase 1 control) are gone too.
- What survives is what these runs copied into `stage/<TAG>/Dataset/`.
  Pot C 01: `Pot_C_Piece_01_Point.pcd` `844035fef4064dd37e1f7072df73d9bf`,
  `Pot_C_Piece_01_Axis.xyz` `5804e1696f2742ce79b93e070cf7c53d`,
  `Pot_C_Piece_01_Mesh.obj` `a0a341701b252b32f789d55ab4d99e49` — the same md5s as the
  ticket-275 phase-0 record, so they are the exact inputs these numbers came from (the cloud itself
  is derived from the OBJ, see the next section). Pot C 03, Pot H 02 and Pot H 10
  are preserved the same way. The author PCDs under `sfs_main/original_samples` were untouched.

## The staging trees are gone; the point clouds are derived, not canonical

The `pota*` trees these runs read from no longer exist (deleted under this ticket, see the Phase 0b
incident). None of that loses a piece, for four reasons that a later reader needs before trying to
reproduce anything here:

(a) `*_Point.pcd` is **derived**, not a source artifact: `cc_mesh_to_pcd.sh` builds it from the
`_Mesh.obj` with CloudCompare (sample ≤1,000,000 points, SOR noise filter medium k=6 σ=1.0, normals
radius 0.5 / orient k=6, then centring), so every piece in play can be re-derived from its OBJ.
(b) The meshes that survive under `.../original_samples_backup/SfS_pp/Mesh` are **mostly the
downsampled `_Mesh_DS.obj` variants** — Pot_C_Piece_03, Pot_H_Piece_02, Pot_H_Piece_10,
Pot_D_Piece_03, Pot_C_Piece_01 and Pot_J_Piece_01 are DS-only; Pot_B_Piece_01 is the one piece in
play that still has a plain `_Mesh.obj`. A re-derivation therefore rebuilds a **coarser** piece than
the one scored here.
(c) The script strips `_Mesh` from the basename, so converting `…_Mesh_DS.obj` yields
`…_DS_Point.pcd` — which the pipeline will not pick up until it is renamed.
(d) The derivation is **not byte-reproducible by construction** (CloudCompare sampling plus SOR), so a
rebuilt cloud needs its own baseline; no number in this ticket can be reproduced by re-deriving the
cloud and re-running.

What this ticket kept at `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1121_0ab0935_p276-merge/inputs/<TAG>/`
(`Point/<Pot>/…_Point.pcd`, `Mesh/<Pot>/…_Mesh.obj`, `Axes/…_Axis.xyz`, `INPUTS.md5` in each
directory and the same values in `run.json`) is a **convenience copy** of exactly the bytes the
Phase 0b and Phase 1 numbers came from — it is what makes those numbers traceable, not the only copy
of anything:

| piece | Point.pcd | Axis.xyz | Mesh.obj |
|---|---|---|---|
| Pot_C_Piece_01 | `844035fef4064dd37e1f7072df73d9bf` | `5804e1696f2742ce79b93e070cf7c53d` | `a0a341701b252b32f789d55ab4d99e49` |
| Pot_C_Piece_03 | `1d01ad6340f8dd3c2890c5a261f91d9a` | `c5cce01ee33448a74c91d2ef33f7c9fe` | `575da29b332e880f804ddf6e576aa28f` |
| Pot_H_Piece_02 | `af309b9e450b13b39e3e474cd3861b72` | `f90e8c18f121ab25f7c2b509624e7b26` | `12882b9868661e417806498178e2ec06` |
| Pot_H_Piece_10 | `994216ee16122285607efb32e640249a` | `723002c8925cc7bb4ce1705946d1429b` | `83bd7ed63bd7945ac980ec6794156d89` |

Pot B 01 and Pot D P03 (the two controls this ticket was dispatched with) are
**control-unavailable-lost-to-cleanup**: `pota253_paper_Pot_B_01` was emptied mid-run on
2026-10-24 11:31:01 and `pota271T1_P03_FULL` is gone; the lead confirmed P03 cannot be rebuilt
from anywhere either (`Dataset/Point/` holds only Juglet, Pot_A, Pot_C, Pot_TEST; `sfs_main` has no
Point directory; `original_samples_backup` has Axes/Mesh/Surfaces/Breaklines/Ground Truth but no
point clouds; the laptop artefacts hold only Pot_D Pieces 27 and 22).

## Phase 1 — positive control (piece changed by the lead: Pot C C03 primary, Pot H 02 control)

Pot D P03 was the dispatched control and is unobtainable (see the survivor section above), so the
lead moved the primary piece to **Pot C C03** — the one piece where a 13474-point cluster holding
119 of the lane's 120 author dots failed to join Surface_1 — with **Pot H 02** as the control. Pot C
01 was run as well because its subjects survive and the run cost nothing.

Method: split one cluster in two by a plane through its centroid, normal = `pcaAxis234` of that
cluster, hand both halves to `mergePaper234` unchanged, and ask whether they are rejoined. The
split is behind the same switch (`SFS_MERGE_DIAG=split`) plus `SFS_MERGE_SPLIT_RANK`
(default 0 = the largest cluster) so the cut can be aimed at a named cluster; unset, nothing runs.
Source `d130da7fbcc6ed7cdecc900fb246f61b`, binary `ff696f7f8072892100631b9173c690e3` (job 33736952),
split runs in job 33736960 (C03 r0, C03 r2, H02 r0) and 33736894 (C01 r0), all EXIT=0.

| piece | cut cluster | halves | clusters before-split / after-split / after-merge | join | verdict |
|---|---|---|---|---|---|
| Pot_C C03 (primary) | rank 0, the face, 23709 pts | 11459 / 12250 | 10 / 11 / 10 | `pass 1: merge 239 into 533` only — the halves stayed apart | **FAIL** |
| Pot_C C03 (aimed) | rank 2, the cluster that carries the rim, 13474 pts | 6764 / 6710 | 10 / 11 / 9 | `pass 1: merge 6710 into 6764` | **PASS** |
| Pot_H 02 (control) | rank 0, the face, 17193 pts | 7903 / 9290 | 13 / 14 / 12 | `pass 1: merge 9290 into 7903` | **PASS** |
| Pot_C 01 (optional) | rank 0, the face, 56833 pts | 26533 / 30300 | 9 / 10 / 10 | no merge line at all | **FAIL** |

The cut is genuinely an adjacency, not a gulf: measured across the four cuts, the nearest
cross-half distance is 0.098–0.170 mm and 197–407 points on each side have a cross-half neighbour
within 1 mm (median nearest cross-half distance is 14–38 mm simply because most of a half is far
from the plane, which is what a plane cut does). So `rhoD` and the ≥3-pair rule are satisfiable by
construction, and on the two FAILs the rejection has to come from the normal/curvature tests — the
outcome the ticket pre-registered a FAIL to isolate.

Two consequences worth recording. First, the merge is not uniformly broken: it rejoins the c2
(=13474-point) cut and the Pot H 02 face cut on the same inputs and the same parameters, so the
C03 result in Phase 0b — c2 never joining Surface_1 — is a genuine cross-cluster rejection rather
than a dead code path, and the two FAILs are specific to the largest clusters (23709 and 56833
points). Second, on both FAILs the artificial split changes which clusters become surfaces, because
each half is now individually smaller than the next natural cluster: on C03 the classify line moves
from `face0 n=23709 ... face1 n=17695` to `face0 n=17695 ... face1 n=13474` and prints
`swapped -> Surface_0=interior`, i.e. the dropped c2 is promoted to a surface and the two face halves
are both dropped; on C01 `Surface_1` becomes the 30300-point half. A failed merge therefore
cascades straight into which arc reaches the edge stage, which is exactly the Pot C C03 mechanism of
Phase 0b.

Which of `rhoN` / `rhoC` / `rhoInN` / `rhoInC` rejects the two big clusters is not visible without
the Phase 2 per-pair instrumentation, which stays held.

## Phase 2 — which criterion rejects, per real pair (and the 200-pair cap, measured)

The lead pre-registered a hypothesis before this dump existed: *the pair search is starved, not the
tests* — the 200-pair cap (:1884) plus one nearest partner per boundary point (:1887) means a big
cluster's first 200 pairs are its outer rim, so the cut's pairs are never examined and the
`>= 3`-pair rule fails on evidence it never looked at. **The dump overturns it.** On the C03 FAIL lane
the cap never engages — all 710 boundary points of the smaller half are scanned and 197 qualifying
pairs are found — and the pair is still refused. On C01 the cap does engage (200 pairs from 306 of
940 points), and the 200 it looked at agree on normals to 0.9997 and on curvature to 0.0002; the
refusal comes from the same test as C03, with the same sign.

Switch: `SFS_MERGE_PAIRS=1`, read once at the top of `mergePaper234` (patched source
`3cf1fbfd91e87644d13e4bc4bce44b53`, binary `37086971e327bc8996ea591bf66064f5`, job 33737069).
Each line prints, per cluster pair per pass: boundary counts `bnd=A/B`, points scanned out of the
smaller boundary set `scan=`, points the cap left unexamined `cut=`, qualifying pairs `pairs=`,
`cap=1` when the 200-pair cap truncated the scan, the pair distances `dmin/dmed`, the k2-average
normal dot `nrm`, the mean-curvature delta `curv`, the inner-representative values `inner/icurv`
and the verdict. Runs in job 33737077 (out3/, 5 runs, 5:31, all EXIT=0).

**Inertness.** With `SFS_MERGE_PAIRS` unset the binary prints zero `PAIR-276` lines (0 of 0), and the
C03 rank-0 run is unchanged in every cluster decision against the pre-patch binary: 10 clusters,
sizes 13474/17695/12250/11459/772/724/610/239/214/179 with the same surface assignment, and the same
classify line `face0 n=17695 … face1 n=13474 interior_frac=0.7326 … satA=3604.0000 satB=27565.0000`.

Every pair that got past the pair threshold (all other pairs collected 0 qualifying pairs, i.e. the
two clusters are more than 1 mm apart everywhere — `pairs=0 cut=0`, the scan exhausted):

| lane | pair | bnd | scanned/cut | pairs | cap | dmin / dmed | nrm | curv | inner / icurv | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| C03 r0 **FAIL** | **c0-c10 the halves**, 11459/12250 | 782/710 | 710 / 0 | 197 | 0 | 0.1198 / 0.6175 | **1.0000** | **0.0024** | **-0.0142** / 0.0005 | **REJECT:rhoInN** |
| C03 r0 | c5-c7, 533/239 | 259/116 | 116 / 0 | 5 | 0 | 0.5817 / 0.8512 | 0.9869 | 0.0188 | 0.9959 / 0.0042 | ACCEPT |
| C03 r0 pass 2 | c0-c9 the halves again | 782/710 | 710 / 0 | 197 | 0 | 0.1198 / 0.6175 | 1.0000 | 0.0024 | -0.0142 / 0.0005 | REJECT:rhoInN |
| C03 r2 **PASS** | **c2-c10 the halves**, 6764/6710 | 514/453 | 453 / 0 | 193 | 0 | 0.0982 / 0.6564 | 1.0000 | 0.0017 | **0.9796** / 0.0000 | **ACCEPT** |
| H02 r0 **PASS** | **c0-c13 the halves**, 7903/9290 | 553/592 | 553 / 0 | 184 | 0 | 0.1695 / 0.6673 | 0.9999 | 0.0038 | **0.9922** / 0.0000 | **ACCEPT** |
| H02 r0 | c3-c8, 1471/251 | 375/180 | 180 / 0 | 3 | 0 | 0.7482 / 0.9019 | 0.6186 | 0.0264 | — | REJECT:rhoN |
| H02 r0 | c8-c10, 251/197 | 180/141 | 141 / 0 | 11 | 0 | 0.1801 / 0.5652 | 0.9808 | 0.0027 | 0.9857 / 0.0087 | ACCEPT |
| H02 r0 | c11-c12, 168/128 | 99/71 | 71 / 0 | 4 | 0 | 0.4746 / 0.9268 | 0.9337 | 0.0047 | — | REJECT:rhoN |
| C01 r0 **FAIL** | **c0-c9 the halves**, 26533/30300 | 1420/940 | **306 / 634** | **200** | **1** | 0.1635 / 0.6395 | **0.9997** | **0.0002** | **-0.1481** / 0.0051 | **REJECT:rhoInN** |
| C01 r0 | c0-c2, 26533/17344 | 1420/724 | 724 / 0 | 13 | 0 | 0.3917 / 0.7710 | 0.8980 | 0.0034 | — | REJECT:rhoN |
| C01 r0 | c1-c5, 49245/459 | 1165/142 | 142 / 0 | 4 | 0 | 0.7280 / 0.8065 | 0.9449 | 0.0010 | — | REJECT:rhoN |

**The cap, audited.** Across the four lanes the cap engaged exactly once (C01 c0-c9, `cap=1`,
`cut=634`), and the largest collected pair count is exactly 200. On every other pair, including all
three PASS contrasts and the C03 FAIL, the scan ran to the end of the smaller boundary set
(`cut=0`). So the cap can bias which pairs feed the averages; it cannot, structurally, produce a
`< 3`-pair rejection, because the loop stops only when 200 pairs have qualified — a `pairs < 3`
return therefore means the entire smaller boundary set was examined. The `>= 3`-pairs rule cannot be
starved by the cap at all; what the cap can do is decide *which* pairs the normal and curvature
averages see.

**Mechanism.** On both FAIL lanes Step 2 passes cleanly and Step 3 refuses: the normals at the two
clusters' inner representative points (chosen by `medianInternal234` along each cluster's PCA axis)
are nearly perpendicular — dot -0.0142 on C03 (~91°) and -0.1481 on C01 (~98.5°) — against
`rhoInN = 0.75`. The two PASS contrasts score 0.9796 and 0.9922 (~11.6° and ~7.2°). A dot near 0,
not near -1, is what two distant points on a curved patch give; it is not a flipped normal. Those
representative points sit far apart on the patch by construction, so the test asks whether two points
tens of millimetres apart on one surface face the same way — on a gentle patch (H02, C03's rim
cluster) they do, on a strongly curved face (C03's face, C01's face) they do not. That is the
discriminator between every PASS and every FAIL here, and it is a property of the tests, not of the
pair search.

**What follows.** A plane cut of a single surface is guaranteed to be one surface, and the merge
refuses it on C03's and C01's faces. So `mergePaper234` under-joins big curved clusters, and the
C03 Phase 0b headline (the 13474-point rim cluster never joining Surface_1) needs re-reading in that
light: that particular pair was refused at the *distance* stage (`pairs=0` — the two clusters are
more than 1 mm apart everywhere), so it is a separate, legitimate refusal, while the under-joining
defect shows up on the cut experiments. Whether Step 3 is a faithful reading of Appendix A is Phase 3,
still held.

## Phase 3a — the four pieces re-meshed at SFS_PAPER_THETA=3.4 (theta is not the cause)

Run `20261024-1223_0ab0935_p276-phase3a`, job 33737576 COMPLETED 0:0 in 4:02, binary
`37086971e327bc8996ea591bf66064f5` (the Phase 2 build, source `3cf1fbfd91e87644d13e4bc4bce44b53`; no C++
edit and no build in Phase 3a). Diag run as `SFS_MERGE_DIAG=1` — natural merge only, no split.`SFS_MERGE_PAIRS`
unset, so the Phase 2 pair instrumentation never fires: `PAIRLINES=0` on all four runs. Inputs are
byte-identical copies of the four `inputs/<TAG>/` trees the 4.0 Phase 0b run used (per-file md5s in
`out/<TAG>/inputs.md5`), so theta is the only variable. Every log prints `thetaDeg=3.40000` and every
run prints the axis `classify:` line — no run fell back to "no SFS_AXIS_FILE, keep size order".

Written sheets, 3.4 (not byte-reproducible — `pcl::RandomSample` at `mesh_processing_headless.cpp:829-833`;
every claim below is made on cluster labels, not sheet bytes):

| piece | Surface_0.xyz | Surface_1.xyz |
|---|---|---|
| Pot_C_Piece_03 | `ec43f7b45af9f7b63cd856d56425ffcf` | `0e8beec0465c18502f63a5eec4a50c62` |
| Pot_C_Piece_01 | `148132ff1f28cd7c78e2c11245186636` | `d57f777e52dafcb2c14982e3c5fe809b` |
| Pot_H_Piece_02 | `9de492c98873204572919961b7d7dba8` | `638a22194203c6b356e52a066c656ab3` |
| Pot_H_Piece_10 | `07ba2430d3ed975b8df20d29569dbe03` | `ee79326ee6c6ef45ca1447b4d3a7699f` |

### Share of the author's dots that land on a KEPT surface

"Kept" = the author dot's nearest clustered point is within 2 mm and carries label 0 or 1, the only two
clusters `classifyAndOrderPaper234` keeps (labels are the post-classify order). Unclustered and
beyond-2 mm dots count against the share, so the column is conservative.

| piece | lane | author dots | kept @4.0 | kept @3.4 | clusters @4.0 → @3.4 |
|---|---|---|---|---|---|
| Pot_C_Piece_03 | Bl0 | 191 | 88.48 % | 86.39 % | 9 → 8 |
| Pot_C_Piece_03 | Bl1 | 120 | **0.00 %** | **0.00 %** | 9 → 8 |
| Pot_C_Piece_01 | Bl0 | 211 | 90.05 % | 89.10 % | 9 → 7 |
| Pot_C_Piece_01 | Bl1 | 230 | 93.48 % | 97.39 % | 9 → 7 |
| Pot_H_Piece_02 | Bl0 | 156 | 94.23 % | 95.51 % | 12 → 13 |
| Pot_H_Piece_02 | Bl1 | 137 | 94.89 % | 96.35 % | 12 → 13 |
| Pot_H_Piece_10 | Bl0 | 101 | 92.08 % | 90.10 % | 9 → 9 |
| Pot_H_Piece_10 | Bl1 | 88 | 96.59 % | **79.55 %** | 9 → 9 |

### Pot C 03 Bl1 — the lane the theta question was asked about

| | @4.0 | @3.4 |
|---|---|---|
| clusters | 9 | 8 |
| kept pair (classify) | 23709 `interior_frac=0.8173` + 17695 `0.0001` | 23446 `0.8153` + 17245 `0.0000` |
| dropped band holding the rim | c2, **13474** pts | c2, **13265** pts |
| author Bl1 dots within 2 mm of that band | **119 of 120** | **119 of 120** |
| min distance band → kept pair | **1.9306 mm** | **2.4872 mm** |
| band points within 1 / 1.5 / 2 / 3 mm of the kept pair | 0 / 0 / 4 / 130 | 0 / 0 / 0 / 41 |
| median point spacing inside the band | 0.3044 mm | 0.3067 mm |
| median author-dot → written Surface_1 | 1.957 mm | 1.933 mm |

The pre-registered read (lead, m01241) fires its **second** branch, not its first: the author's Bl1 dots
do **not** move onto a kept surface at 3.4 — they sit on a dropped cluster at both growth angles, 119 of
120, and the band is the same band (13474 pts at 4.0, 13265 at 3.4). So the mesh loss at Pot C 03 Bl1 is
not an artifact of the growth angle ticket 271 removed, and the suspicion that the cluster is a lip welded
into the face does not survive: at 4.0 that band already stood 1.93 mm clear of the kept pair, and at 3.4
it stands 2.49 mm clear. It is a separate band that carries the whole of the author's second breakline.

### What the gap numbers say about rho_d = 1.0

Step 1 of Appendix A forms boundary pairs only within `rhoD = 1.0` mm. On the C03 band there are **zero**
point pairs within 1, 1.5 and 2 mm at 3.4 (four within 2 mm at 4.0), so at `rho_d = 1.0` the merge never
sees that band at all — the refusal is a distance refusal, not a Step 2 or Step 3 refusal, and this is the
same conclusion Phase 2 reached from `pairs=0` on the same pair.

Measured on all four pieces at 3.4, every dropped cluster that carries author dots:

| piece | cluster (size) | author dots | min distance to kept pair | points ≤ 1 / 2 / 3 mm |
|---|---|---|---|---|
| C03 | c2 (13265) | 119 Bl1 | 2.4872 mm | 0 / 0 / 41 |
| C03 | c4 (521) | 21 Bl0 | 1.3739 mm | 0 / 67 / 368 |
| C03 | c5 (497) | 20 Bl0 | 1.3161 mm | 0 / 73 / 389 |
| C03 | c3 (603) | 12 Bl0 | 1.8312 mm | 0 / 23 / 265 |
| C01 | c4 (415) | 26 Bl1 | 1.5732 mm | 0 / 32 / 293 |
| C01 | c5 (355) | 18 Bl1 | 1.5701 mm | 0 / 30 / 288 |
| C01 | c3 (431) | 15 Bl0 | 1.8699 mm | 0 / 3 / 33 |
| H02 | c4 (976) | 27 Bl0 + 14 Bl1 | 1.3876 mm | 0 / 87 / 413 |
| H02 | c5 (539) | 22 Bl0 + 25 Bl1 | 1.5098 mm | 0 / 50 / 374 |
| H10 | c3 (745) | 25 Bl0 + 21 Bl1 | 1.3183 mm | 0 / 90 / 409 |
| H10 | c4 (744) | 18 Bl0 + 13 Bl1 | 1.2868 mm | 0 / 96 / 313 |
| H10 | c5 (629) | 21 Bl1 | **0.3191 mm** | 35 / 144 / 254 |

Sampling spacing is 0.29–0.37 mm on every piece, so `rho_d = 1.0` mm is already 3–3.5 point spacings,
and the dropped bands sit 4–8 spacings out. `rho_d = 1.0` is not a marginal mismatch with our sampling:
the bands are separated from the kept faces over 1.2–2.5 mm of empty space, and to reach the C03 band a
threshold would have to go past 3 mm (about ten spacings) — a different regime, not a nudge. The single
exception is H10's c5 (0.32 mm), the only dropped cluster in the four pieces where boundary pairs can form
at the shipped threshold, and there the merge still did not join it.

### One observation, deliberately not a recommendation

`classifyAndOrderPaper234` compares exactly `pclusters[0]` and `pclusters[1]`
(`mesh_processing_headless.cpp:2105-2118`), i.e. the two largest clusters after merging. On C03 the band
that carries all 120 of the author's Bl1 dots is **third** by size (13265 against 17245), so it was never a
candidate for a surface slot at either angle. Whether a surface pair should be chosen from more than the
two largest clusters is a design question outside this ticket's boundary; it is recorded here because it is
the one measurable structural fact the theta experiment exposed.

*Instrumentation note:* the dump header's `surface` field is `((c < 2) ? 1 : 0)`
(`mesh_processing_headless.cpp:2227`) — a cruder encoding of kept/dropped, not the slot assignment. The
kept/dropped claims above rest on the per-point label plus the `classify:` line.

### Verdict

**The mesh loss at Pot C 03 Bl1 is not a theta artifact.** At `SFS_PAPER_THETA=3.4` the rim still lives in
a dropped 13265-point band holding 119 of the author's 120 dots (0.00 % kept, exactly as at 4.0), and that
band stands 2.49 mm from the kept face with zero point pairs within 2 mm, so no Appendix A test is ever
reached on it — the binding gate is `rho_d = 1.0` against a 0.31 mm sampling. 276 closes on that sentence;
the merge fix question is untouched by it. The theta change is not free either: it moves Pot H 10 Bl1 from
96.59 % to 79.55 % kept.

## Acceptance

1. Phase 1 is a PASS/FAIL with the cluster counts and the exact log lines.
2. The Phase 2 table covers 5 pieces and attributes every rejected pair to one
   Appendix A criterion.
3. Phase 3 answers the three readings with the paper's line numbers.
4. A one-paragraph verdict: is the merge doing its paper job on this data — yes / no /
   cannot tell — and which single measurement decides it.
5. If it is broken, propose the smallest change and its expected effect. Do NOT
   implement the change in this ticket.

## Boundaries

- Mesh stage only: mesh_processing_headless.cpp and the mesh logs. Do not touch
  edgeline_extraction_headless.cpp — ticket 275 owns that file.
- New instrumentation sits behind one env switch (e.g. SFS_MERGE_DIAG=1) and must be
  inert when unset: the six guard lanes of ticket 271 must reproduce bit-identically.
- Do not change rhoD / rhoN / rhoC / rhoInN / rhoInC defaults in this ticket.
- Run directory under /data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_<tag>/
  with one index row; verdict and human_note left empty.
- One writer inside .scratch/ at a time: dispatch only once 275's worker has finished.

## Required evidence to report

- cluster counts before and after per piece, quoted from the logs
- the rejected-pair table
- the Phase 1 log excerpt showing the split halves merged or not
- binary md5, cloud md5, and the thetaDeg value printed by each run
