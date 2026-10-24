# 276 — Does the cluster merge do the job Appendix A gives it?

Answers: E1
Status: results-in (Phase 0b reported and accepted; Phase 1 split control done — 2 PASS / 2 FAIL, see below; Phases 2 and 3 held pending the lead)
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


## Lead verdict (2026-10-24) — Phase 1 accepted; the merge is fine until the cluster is big

**Checked, not taken on trust.** I read the two split-run logs on Spartan myself
(`SfSpp/runs/20261024-1121_0ab0935_p276-merge/logs/p276_split_33736894.out` and
`.../p276_split2_33736960.out`) and every number in the table above reproduces, including the
classify lines the cascade claim rests on:

- C03 aimed at the rim cluster (rank 2, 13474 pts): `pass 1 done: 9 clusters`, then
  `classify: face0 n=23709 interior_frac=0.8173 face1 n=17695 interior_frac=0.0001` -> `kept`.
  The cut halves rejoined.
- Pot_H_02 (control): `pass 1 done: 12 clusters`, `face0 n=17193 interior_frac=0.9994
  face1 n=14189` -> `kept`. Rejoined.
- C03 rank 0 (the face, 23709 pts): `Number of clusters is equal to 10`, `pass 1 done: 10 clusters`,
  then `classify: face0 n=17695 interior_frac=0.0001 face1 n=13474 interior_frac=0.7326
  satA=3604.0000 satB=27565.0000` -> `swapped -> Surface_0=interior`. The halves stayed apart,
  and the previously dropped 13474-point cluster was **promoted into the surface slot** while both
  face halves were dropped.
- Pot_C_01: `pass 1 done: 10 clusters`, `face0 n=49245 interior_frac=1.0000 face1 n=30300
  interior_frac=0.0000` -> `kept`. No merge; Surface_1 becomes the 30300 half, the 26533 half drops.

**What Phase 1 establishes, in order of importance.**

1. **The merge is not a dead code path and it is not broken uniformly.** On the same inputs and the
   same parameters it rejoins a cut through the 13474-point rim cluster and a cut through Pot H 02's
   17193-point face. So Phase 0b's headline is a real cross-cluster decision.
2. **The rejection is size-dependent.** The two FAILs are the two largest clusters tested (23709 and
   56833); the two PASSes are 13474 and 17193. Orientation cannot explain it — a plane cut leaves the
   two halves with near-identical normals, which is the easiest possible case for rhoN and rhoC.
3. **A failed merge is not a silent drop, it re-orders the surfaces.** Both FAILs move the classify
   line, and on C03 the wrong cluster is promoted to `Surface_0` while both real face halves are
   dropped. That is exactly the picture Phase 0b measured on the unmodified C03 run. So "c2 never
   joined Surface_1" and "the rim never became a surface" are one event, not two, and the edge stage
   was handed a wall whose rim belonged to a cluster nobody kept.

**Pre-registered hypothesis for Phase 2 (written before the dump exists).** The pair search is
starved, not the tests. tryMergePair234 caps the search at 200 pairs
(`mesh_processing_headless.cpp:1884`) and keeps only the nearest partner per boundary point
(`:1887`). A large cluster's boundary is dominated by its long outer rim, so the first 200 pairs may
never include the pairs along the cut, and the `>= 3 pairs within rhoD` rule then fails on evidence it
never looked at. Size ordering matches the observation exactly: the two failures are the two largest
clusters. **What would overturn it:** the per-pair dump showing >= 3 qualifying pairs within rhoD on a
FAIL lane, rejected on rhoN or rhoC. Then the tests are the defect and the cap is innocent.

**Phase 2 approved in the cheap form, and scoped.** Per-pair dump of the five test values (distance,
normal dot, curvature delta, inner-point result) on four lanes: **C03 rank 0 and C01 rank 0 as FAIL
contrasts, C03 rank 2 and H02 rank 0 as PASS contrasts**. One diag build, no production default
touched, no edge-stage run. The PASS lanes are in because a mechanism must explain the difference, not
just the failures. Phase 3 stays held.

**Diag code is deliberately NOT in main.** It stays in `C:/PR/worktrees/sfs/276` and is preserved as
`.scratch/pota-repro/patches/276-merge-diag.patch` (149 lines, md5 `ff3fc86fb58e28f9ad84f86e0d482640`).
Main's `mesh_processing_headless.cpp` remains pristine (md5 `b2b1b7088e75a9c3340ca484bf8d38ac`). Reason:
the 275 precedent — five rejected arms are still being paid for in a file they no longer serve — so
scaffolding lands with the fix, or not at all.


## Lead addendum (2026-10-24, after Phase 2) — hypothesis dead, paper rule exonerated, and one confound to settle first

**Phase 2 accepted.** The pair cap is innocent and the pre-registered hypothesis is dead; the
worker reported the overturn in the terms it was asked to, including the one precision that
matters (the rejecting test is Step 3 `rhoInN`, not `rhoN`/`rhoC`). The recorded numbers are
enough to rebuild the argument without the run: C03 r0 refuses at `inner=-0.0142` with
`nrm=1.0000` and `curv=0.0024`; C01 r0 refuses at `inner=-0.1481` with `nrm=0.9997`; the two
PASS contrasts score `inner=0.9796` and `0.9922`. The cap engaged once in the whole batch
(C01 c0-c9, 200 pairs, 634 of 940 boundary points cut) and the loop can only stop at 200
*qualified* pairs, so it can bias which pairs feed the averages but cannot starve the >=3 rule.

**No Step 3 fix is authorised, for two reasons.**

1. **Step 3 as coded is the paper's rule, not a mis-port.** Appendix A at
   `C:/PR/papers/text/sfspp-2502.13986v1.md:479`: each cluster selects "a representative
   internal point ... the median point sorted by perpendicular distance to the principal axis",
   and the decision compares "the normals and curvatures of these internal points" at
   `rho_in,n = 0.75` / `rho_in,c = 0.25`. That is exactly
   `medianInternal234` + the dot product at `mesh_processing_headless.cpp:1916-1925`.
2. **The obvious "fix" is Step 2 wearing a hat.** Comparing normals at the pair members is
   precisely what Step 2 already does (`nrm = 1.0000` / `0.9997` on the two FAIL lanes), so
   adopting it would silently delete Step 3 — the paper added Step 3 *because* "boundary
   conditions alone may not fully overcome noise or inaccuracies near the boundaries". A
   deviation of that size needs a stated reason and a measured gain, and we have neither.

What Phase 2 actually establishes is a limit: Step 3 compares two points tens of millimetres
apart on one surface, so on a strongly curved face their normals legitimately differ by ~91-98
degrees. It passes on gentle patches, which is the exact PASS/FAIL split measured. The threshold
is not the problem — no value of `rho_in,n` between 0 and 1 both admits a 91-degree pair and
still means anything.

**The confound that outranks it.** Every theta line in the Phase 0b, Phase 1 and Phase 2 run
directory reads `thetaDeg=4.00000` (6 of 6; `grep -c 'thetaDeg=3.4'` = 0). Phase 0b therefore
measured Pot C 03's lost rim at the growth angle ticket 271 removed, whose signature is exactly
a lip welded into the face. The 13474-point cluster carrying 119 of that lane's 120 author dots
may be that lip rather than a piece of the wall. Until the same measurement is repeated at 3.4,
the phrase "the rim is lost in the mesh stage" is not a finding about the setting we intend to
ship.

**Phase 3a (lead-added, dispatched), pre-registered read:**
- Re-mesh the four Phase 0b pieces at `SFS_PAPER_THETA=3.4` from the same `inputs/` copies, with
  `SFS_AXIS_FILE` set and the classify line confirmed, then repeat the cluster/surface mapping.
- **If the author's Bl1 dots land on a KEPT surface at 3.4** where they did not at 4.0, the mesh
  loss was a theta artifact: nothing to fix in the merge, and ticket 276 closes with that.
- **If they still land on a DROPPED cluster**, the next measurement is the true gap between that
  cluster and the face (minimum distance, and how many point pairs fall within 1 / 1.5 / 2 / 3 mm)
  against the cloud's median nearest-neighbour spacing. That decides whether `rho_d = 1.0` suits
  our sampling — a question about a parameter, not about the paper's tests.
- Phase 3 proper (any C++ change) stays held until 3a reports.


## Lead verdict (2026-10-24) — Phase 3a accepted; the merge line closes, the partition question opens

**Both explanations I had are dead, and the ticket is better for it.**

- **Theta is not the cause.** At `SFS_PAPER_THETA=3.4` the band still carries 119 of Bl1's 120 author
  dots and `kept = 0.00%`, unchanged from 4.0. Every log reads `thetaDeg=3.40000`, every run prints
  the axis `classify:` line, and the inputs are byte-identical copies of the 4.0 trees, so theta was
  the only variable.
- **My lip story is dead too**, and by its own number: at 4.0 that band already stood **1.9306 mm**
  clear of the kept pair. A welded lip sits at contact distance. This band was never part of the face
  at either angle.

**`rho_d` is answered and must not be tuned.** Sampling spacing on these pieces is 0.29-0.37 mm, so
`rho_d = 1.0` is already 3-3.5 spacings. The dropped bands that carry author dots sit **1.2-2.5 mm**
away — 4-8 spacings — with essentially nothing inside 1 mm. Reaching C03's band would take a threshold
of about 3 mm, ten spacings: that is a different regime, not a correction. The one exception in four
pieces is H10's c5 (629 pts, 21 Bl1 dots, 0.3191 mm gap, 35 points inside 1 mm), the only dropped
cluster where boundary pairs can form at the shipped threshold — and the merge still refused it. One
counter-example is not a rule; Step 3 remains the only refusing test we have caught in the act.

**What actually decides it, and it is not in the merge at all.** `classifyAndOrderPaper234` compares
`pclusters[0]` and `pclusters[1]` — the two largest after merging
(`mesh_processing_headless.cpp:2105-2118`), which is the paper's own rule ("we consider the two
largest clusters as the inner and outer surfaces", `C:/PR/papers/text/sfspp-2502.13986v1.md:155`).
On C03 the band carrying **every one** of Bl1's reference dots is the **third** cluster by size
(13265 against 17245), so it was never a candidate for a surface slot at either angle.

Now put that together with where the reference came from: these breaklines are the authors' own
pipeline output, produced under the same two-largest rule. So in their run a kept surface reached the
rim. Ours partitions the rim off into a third cluster. **The merge and the classify are both faithful;
what differs is the partition itself** — how region growing splits this piece. That moves the question
upstream, to the growing stage and the cloud it runs on, not to Appendix A.

**Two precisions carried forward, both the worker's own.**
1. Phase 0b's "kept Surface_1 carries 5 of 120" was measured against the written sheet; on cluster
   membership the count is 0 of 120. The cluster metric is the one that decides surfacing, and it is
   the one quoted from here on.
2. Theta 3.4 is **not free**: Pot H 10 Bl1 falls from 96.59% to 79.55% kept because its cluster
   structure moves the reference rim onto small dropped clusters, while C01 and H02 improve slightly
   (Bl1 93.48 -> 97.39, 94.89 -> 96.35). Any default decision must weigh that.

**Status: closed.** No C++ change, no default change, no Step 3 deviation. Ticket 278 takes the next
question — what that band physically is.
