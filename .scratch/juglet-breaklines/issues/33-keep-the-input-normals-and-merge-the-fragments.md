# 33: Can the normals the scan already carries — and a merge of the fragments — give sherds 2 and 9 a face?

**Status:** done
**Working in:** chat on Thinkbook16 (2026-10-27)
**Branch:** 33-keep-the-input-normals-and-merge-the-fragments, in /c/PR/worktrees/sfs/33
**Answers:** U19, E1
**Blocked by:** none
**Blocks:** none

## Why this ticket exists

Two leads, both pointing at the same two sherds, and the conservator asked for them together
(2026-10-27, "1, let's see if sherd 2, 9 can yield a valid surface with cluster merge").

**Lead 1 — the scan already carries good normals, and the pipeline throws them away.** Ticket 32 measured
the normals stored in the point cloud files against each piece's own mesh: **0.414–1.635°** on the Juglet,
**0.455–0.616°** on Pot A. Ticket 30 measured the normals the pipeline computes for itself against the same
meshes: **3.39–8.10°** on the Juglet. The growth admits a neighbour only within **3.4°**
(`mesh_processing_headless.cpp:3026` area, theta 3.4). Why they differ is visible in the code:
`getNormalsOnSurface` (`:604`) writes the sampled points to an XYZ file **positions only** (`:615`), reads
them back (`:622-630`), and re-estimates normals from scratch with CGAL PCA at
`nb_neighbors = std::max(5, std::min(20, (int)points.size() / 1000))` (`:634`, `:659-662`). At Juglet point
counts that is 5 neighbours — a patch about 1–2 mm across on a surface that folds over a few millimetres.

**Lead 2 — the fragments may be mergeable.** Piece 2 and piece 9 grow many small regions and no face:
ticket 28's replica gave 661 and 1562 regions with the largest 36 and 16 points, and ticket 32 forced the
pipeline's own floor down and got single regions of 32 and 21 points. But `mergePaper234` (`:3186`) is
the step that is supposed to join fragments of one surface, and it has **never been asked to merge
fragments**, because the floor normally kills them first. Its test needs **at least 3 boundary pairs**
hardcoded at `:3142`; all six thresholds already have env switches
(`SFS_PAPER_RHOD/RHON/RHOC/RHOINN/RHOINC`, `:4365-4369`).

The conservator's question is the one to answer: with the good normals restored **and** the merge allowed
to work on fragments, does sherd 2 (or 9) yield a surface that is a face rather than a corner patch?

## What to build

Two switches, both defaulting to today's behaviour:

1. `SFS_NORMAL_SOURCE=reestimate|input` (default `reestimate`). In `input` mode the normals of the
   incoming cloud are carried through the sampling step instead of discarded: for each sampled point,
   average the unit normals of the source points within one sampling radius and normalise; if none are in
   range, fall back to the nearest source point's normal. Points with no usable source normal are reported
   and counted, never silently filled. Print one line per call:
   `[NORMAL-33] call=N source=input npts=... carried=... nearest=... missing=... median_dev_to_pca_deg=...`.
   The curvature field still has to be computed as today — this switch changes normals only.
2. `SFS_MERGE_MIN_PAIRS=<int>` (default 3), replacing the literal at `:3142`, printed in the existing
   `[PAPER-234]` line.

Rules:
- With neither switch set, the pipeline must reproduce today's output exactly (the defaults proof below).
- A carried normal must be a **unit** vector whose sign agrees with the source cloud's, not flipped to a
  convenient hemisphere; MST orientation is not applied in `input` mode, and that is a decision to state
  in the log line, not to hide.

## Arms and cells

Pieces: Juglet 2 and 9 (the target), 3, 5, 7 (the ones that already surface, as controls) and
Pot_A 07 (the reference). Four arms:

| arm | normals | floor | merge |
|---|---|---|---|
| A | reestimate (today) | today | today |
| A2 | reestimate | today | today — repeat, to measure the piece's own spread |
| B | input | today | today |
| C | input | forced down so fragments survive (`SFS_SPACING_POLICY=piece SFS_COUNT_SCALE=auto SFS_FLOOR_CEILING` stepped until the reported floor is at most 2 % of the cloud) | today (min pairs 3) |
| D | input | as C | `SFS_MERGE_MIN_PAIRS=2` |

If a C or D cell still returns one region, say so plainly: the fragments did not meet the merge's own
criteria, and the pair counts that refused them are the evidence.

## The measurement that decides it

For every surface the pipeline writes, on the sherd's cloud and mesh:

- point count, extent (bbox diagonal), and **2 mm coverage** — the fraction of the cloud within 2 mm of the
  surface. A face is most of the sherd; piece 3's today is 92.6 % and pieces 2/9's forced-floor patches were
  28.4 % and 42.5 % (ticket 32).
- median folded angle of the surface's points to the nearest mesh vertex normal.
- the corrected pair statistic (nearest-point vector split along/across the Surface_0 normal, coincidence at
  1 micron) where two surfaces are written — the mean-normal dot test is retired (ticket 24).
- every `[NORMAL-33]`, `[PAPER-234]`, `[WINDOW-26]`, `[FLOOR-23]` and `[STATUS-23]` line for the cell.

## Acceptance criteria

1. Both switches exist, are documented in the run's `run.json`, and print their value per cell.
2. **Defaults proof**: with no switch set, every surface is byte-identical to the pre-change binary's, and
   the point set is identical after sorting — the same proof shape tickets 22, 23, 24, 26 and 30 used.
3. The carry is proven to be a carry: report the median angle between the carried normal and the pipeline's
   PCA normal at the same points, and the median angle of the carried normal to the mesh.
4. Every arm × piece cell reports: exit code, region count, region sizes, merge decisions with pair counts
   and which criterion refused a merge, surfaces written with the measurements above.
5. Pot A 07 in arm B and C keeps **8 of 8** two-surface pieces (whole pot, all eight pieces) and its pair
   statistics stay in the band 3.55–7.13 mm along / 0.24–0.27 mm across / coincidence 0.0000.
6. Corpus and staged inputs md5 identical before and after; `/opt/sfs-pristine` recorded ABSENT, never
   created.
7. Geometry outside the written surfaces deleted with a counted record written **before** the delete;
   surfaces, logs and tables kept for the lead.
8. Index rows appended with `verdict` and `human_note` EMPTY.
9. No verdict, no merge, no write to `intent/`, no change to any tracked file except
   `mesh_processing_headless.cpp` and `.scratch/juglet-breaklines/stage33/`.

## Limits

Four jobs maximum (a ticket's usual cap is three; the extra is for the defaults proof), compute nodes only,
never the laptop and never the login node. CRLF-check every script before submitting — two grids have
already died on `set: pipefail: invalid option name`. Report what you measured and what would have to be
true for it to mean something; the reading is the lead's.

## What this cannot settle

It cannot show that restoring the input normals is sufficient anywhere but on these six pieces, and it
cannot make a face out of a sherd that never had one on its mesh. If arm D still returns fragments, the
honest reading is that the merge's criteria are built for surfaces larger than these fragments, not that
the sherds are unprocessable — the next question would be a merge criterion that measures fragment
adjacency rather than surface normals, and that is a different ticket.

## Lead reading — 2026-10-27 (verified first-hand, not taken from the worker's report)

### The question, and the answer in one line

No — sherd 2 does not become a face, and sherd 9 does not produce a surface at all. Sherd 2 writes two
surfaces once the floor is lowered enough to keep its fragments (36 points instead of 50), but they are two
patches **12.1 and 11.8 mm across a 28.3 mm sherd**, covering **30.0 %** and **35.4 %** of it within 2 mm,
and they sit **11.9 mm apart across the surface** rather than the ~0.25 mm a real inner/outer pair shows.
Sherd 9 grows **no region at any setting tried**, including a floor of 39 points on a 1,972-point cloud.

### Sherd by sherd, all four arms (run 2, 36 cells, job 33874829)

| piece | A / A2 / AO (today) | B (input normals) | C (input normals + floor forced) | D (C + merge min pairs 2) |
|---|---|---|---|---|
| 2 | 0 clusters, 21 retries | 0 clusters, 21 retries | floor 36 (from 405, capped), pre 2 → [43, 39] | identical to C |
| 3 | pre 2 → [268], no surface | pre 2 → [275], no surface | floor 65, [352], no surface | identical |
| 5 | pre 1 → [679], no surface | pre 2 → [82, 659], two surfaces 235 / 1 559 | floor 113, [699], no surface | identical |
| 7 | pre 5 → [403, 263, 68, 65], two surfaces 1 012 / 829 | pre 6 → [80, 912, 56], two surfaces 295 / 2 552 | floor 149, [1 004], no surface | identical |
| 9 | 0 clusters, 21 retries | 0 clusters, 21 retries | floor 39, 0 clusters, 21 retries | identical |

The surfaces that were written, measured against the mesh (diagonal, 2 mm coverage, median folded angle):

- C, piece 2: **226 points / 12.120 mm / 29.98 % / 1.597°** and **203 / 11.790 / 35.36 % / 1.641°** — the
  surfaces are geometrically right and cover a third of the sherd.
- B, piece 5: 235 / 15.600 / 11.24 % / 0.981° and 1 559 / 39.615 / 46.74 % / 0.875°.
- B, piece 7: 295 / 16.804 / 9.14 % / 1.155° and 2 552 / 43.112 / 49.57 % / 1.509°.
- A, piece 7: 1 012 / 27.482 / 19.69 % / 1.124° and 829 / 28.240 / 16.78 % / 1.157°.

The corrected pair statistic (nearest-point vector split along / across the Surface_0 normal, coincidence at
1 µm) — the mean-normal dot test is retired (ticket 24):

| arm, piece | along | across | coincidence |
|---|---|---|---|
| A / A2 / AO, piece 7 | 0.643 mm | 4.295 mm | 0.263 |
| B, piece 5 | 2.944 | 9.693 | 0.091 |
| B, piece 7 | 4.189 | 12.367 | 0.102 |
| C and D, piece 2 | 6.360 | 11.856 | 0.000 |

Every Juglet "pair" in this ticket has an **across of 4–12 mm**: they are patches in different places, not two
faces of one wall. Pot A's pairs sit at 0.24–0.27 mm across, which is what a pair looks like.

### The merge did nothing, and acceptance criterion 4 is unmet

**Arm D is identical to arm C in every cell, every size and every surface.** Changing the boundary-pair floor
from 3 to 2 changed no outcome anywhere. Why it refused is **not in evidence**: the binary prints only the
merges it makes (`[PAPER-234] pass N: merge <j> into <i>`), and the worker's offline replay computed the gates
but its writer dropped them. So the reading is "the merge did not fire and we did not capture why", not "the
merge criterion is wrong". The counting structure implies piece 2 offered exactly one cluster pair.

### My premise about the normals was wrong at the shipped spacing — and the cause is the averaging ball

Median folded angle of each cloud's normals to its own mesh, per arm (deg):

| piece | A (pipeline PCA) | B (carried, 0.6 mm ball) | C (carried, ball = the piece's own spacing) |
|---|---|---|---|
| 2 | 8.101 | 9.441 | **3.274** |
| 3 | 6.107 | 7.034 | **2.887** |
| 5 | 4.003 | 4.491 | **2.080** |
| 7 | 3.392 | 3.867 | **1.788** |
| 9 | 9.011 | 9.953 | **3.458** |
| Pot A 07 | 0.713 | 0.694 | **0.588** |

At the shipped 0.6 mm spacing the carry is **worse on all five Juglet pieces** (by 0.47–1.34°), which refutes
the premise this ticket was written on. But in arm C, where the sampling radius shrinks to the piece's own
spacing (0.14–0.39 mm) and the carry ball shrinks with it, the carried normals are **1.79–3.46°** — better than
the pipeline's best on any piece, and at or below the 3.4° gate for four of five. The knob is therefore the
**ball**, not the source: averaging unit normals across a 0.6 mm patch on a surface folding over 0.7–5.3 mm
mixes directions across the fold and across the broken edge. The untested cell this points at is a carry with
**no averaging at all** (nearest source normal), which should land near the 0.41–1.64° the input clouds
themselves carry.

### The finer spacing that rescues sherd 2 costs the sherds that already worked

In arms C and D the spacing policy tightens the sampling to the piece's own spacing. That is what lifted sherd
2's fragments over the floor — and it simultaneously took pieces 3, 5 and 7 from one-or-two clusters to **one
cluster each**, so **no surfaces at all** for pieces 3, 5 and 7, where arm A writes piece 7's pair. A repair
that trades four pieces for one patch is not a repair.

### Pot A, the reference (run 3, 40 cells, job 33875527)

**8 of 8 pieces give two surfaces in both arm B and arm C.** Arm B: along 3.548–7.079 mm, across
0.236–0.266 mm, coincidence 0.000000. Arm C keeps along and coincidence and tightens pieces 07 and 08 to
**0.131 / 0.133 mm** across. Ticket 30's recorded band is 3.55–7.13 / 0.24–0.27, so arm B reproduces it (piece
04 sits 0.0037 mm below the recorded lower bound — inside the same-binary spread this ticket measured).

### The defaults proof, and where my ticket's wording was wrong

With the switches unset, `<piece>_SampledWithNormals.ply` — the artefact the normal switch acts on — is
**byte-identical and sorted-point-set identical, 16 of 16 rows, in both pairings (AO vs A, A vs A2)**, max
absolute difference 0.0 over x, y, z, nx, ny, nz, curvature.

The **surface** PLY are never byte-identical, not even between two runs of the same binary: an uninitialised
curvature column (max |d| up to 4.0e37 on Pot A 02), row order on piece 03, and 1–3 points moving between
Surface_0 and Surface_1 on pieces 03, 05, 06. My ticket asked for "every surface byte-identical" — that was not
a thing that can be asked, and the honest proof is the sampled cloud plus the A-vs-A2 spread.

### Where the jobs went wrong

33874615 FAILED 1:0 in 2 min 50 s — `line 206: BIN: unbound variable`, no cell ran. 33875391 FAILED 2:0 in
3 s — the rendered `submit.sbatch` lost the opening brace of every expansion (`line 27: [: 6SHA}: integer
expression expected`), no cell ran. The two completed jobs are 33874829 (36 cells) and 33875527 (40 cells).
Both failed submissions now have index rows.

### What I take from it

1. **The floor is the first wall for sherd 2 and the last for sherd 9.** Sherd 2's fragments exist (43 and 39
   points) and surface cleanly; sherd 9 has no region to keep at 39 points on 1,972.
2. **Neither sherd's problem is the merge.** With two clusters the merge has one pair to test and it did not
   merge; lowering the required pairs to 2 changed nothing.
3. **What 2 and 9 need is a different growth, and the normals are now a live lead with a known mechanism** — the
   ball, not the source. Nearest-normal carry is one cheap cell away.
4. **The merge as a fragment repair is still untested**, because no arm produced two fragments close enough for
   its 1.0 mm boundary criterion to have a chance. A repair aimed at fragments would have to change that
   criterion (a hardcoded metric, in the conservator's terms), not the pair count.

### verified: the command or file:line behind each load-bearing claim

- `git -C /c/PR/worktrees/sfs/33 diff --stat main...HEAD` -> 44 files, +`7 397`/−22, `mesh_processing_headless.cpp`
  +226/−20, everything else under `.scratch/juglet-breaklines/stage33/`.
- `sacct -j 33874615,33874829,33875391,33875527` -> FAILED 1:0 00:02:50 / COMPLETED 0:0 00:03:23 / FAILED 2:0
  00:00:03 / COMPLETED 0:0 00:02:13, nodes spartan-bm165 and spartan-bm170.
- `awk` over `results/run3/run2/run2_surface.tsv` -> `C Juglet_Piece_2 s0 pts=226 diag=12.120 cov=0.2998`,
  `s1 pts=203 diag=11.790 cov=0.3536`; `B Juglet_Piece_5 s1 pts=1559 diag=39.615 cov=0.4674`.
- `awk -F'\t' '$4=="Juglet"'` over `measure30-run2.tsv` -> piece 2 `no_pair` in A/A2/AO/B; `C|Juglet_Piece_2|ok|
  ...|6.35968|11.8561|0.000000`; `A|Juglet_Piece_7|ok|1012|829|0.643408|4.295400|0.262967`.
- `awk -F'\t' '$4=="Pot_A" && ($2=="B"||$2=="C")'` over `measure30-run3.tsv` -> arm B across
  0.265588/0.247465/0.243148/0.236308/0.248802/0.253708/0.248935/0.250013, arm C pieces 07/08
  0.130820/0.133493, along 3.548413–7.078858 in both.
- `awk` over `results/run3/out/defaults33b.tsv` -> 16 `SampledWithNormals` rows, `md5_equal=1` on all 16;
  `Pot_A_Piece_01_Surface_0.ply` md5 differs with `max_abs_diff 1.6296649e+37`.
- `awk` over `carried33.tsv` (r1_downsampled rows) -> A 8.100984/6.106812/4.002534/3.392134/9.011419, B
  9.441063/7.034291/4.490551/3.866934/9.952567, C 3.274198/2.887216/2.080003/1.787737/3.458438, Pot A 0.712556
  → 0.694484 → 0.587776.
- `ls` + `awk` over `results/run3/out/cells33.tsv`... (the Juglet grid is `results/cells33.tsv`) -> arm C piece 2
  `pre 2 -> 2 [43,39] floor 36 capped yes`, piece 9 `0 -> 0 none floor 39 capped yes`; arm D identical.
- `wc -l` on the branch tables -> `cells33b.tsv` 41 lines (Pot A 40 cells), `measure30-run2.tsv` 37 lines
  (36 Juglet cells), `carried33.tsv` 73 lines.
- `awk -F'\t' 'NF!=6'` over the Spartan `runs/index.tsv` -> 0 rows of 302; the two ticket-33 rows carry empty
  verdict and human_note.
- The `[NORMAL-33]` lines quoted in the worker's report were re-read by me from `results/run3/out/lines33b.tsv`
  for Pot A (`carried=npts nearest=0 missing=0`, `mst=not_applied`).

### What this does not settle

It does not test a nearest-normal carry, so "the ball is the cause" is a mechanism consistent with three arms
(0.6 mm ball worse than PCA, smaller ball better than PCA, Pot A unaffected) and not yet a measured rule. It
does not explain sherd 9's silence at any setting. It does not establish that the merge's 1.0 mm boundary
criterion is what refused the two fragments of piece 2 — that needs the binary to log refusals, which is a small
change nobody has made. And it says nothing about pieces 1, 4, 6 and 8, which were not in this grid.
