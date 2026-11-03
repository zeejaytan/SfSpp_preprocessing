# 68 — Axis method for the Juglet, guard merge, and the densify question

**What to build:** three orders from the conservator (2026-11-03, m06611), continuing tickets 58+67:
(A) fix the AXIS METHOD so Juglet axis files stop contradicting the true poses -- regenerate all nine
axes from each piece's own geometry, not by hand-patching three files; (B) merge the t67 crash guard
into the canonical structure-from-sherds-pp repo; (C) answer, with a measured arm, whether densifying
the edgeline helps now that the axis blocker is removed.

**Why:** t67 proved the 50-dot floor is not binding; 9 of 18 true joins die because axis files for
pieces 2, 5, 9 contradict the GT pose (folded medians 77/55/64 deg vs 16-29 deg for the other six,
lead-reproduced from raw files); the other 9 die in ICP on 6-11-dot seeds (60-170 deg attitude errors).
The conservator ruled: fix the method that produces axes, merge the guard, and measure densification.

**Answers:** U19, E1

**Blocked by:** none (t67 merged 0baa35f; run of record read-only)

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-03)
**Branch:** 68-axis-method-guard-densify, in /c/PR/worktrees/sfs/68
**Worker:** cursor_code worker via lead dispatch (2026-11-03)

## Spec

### Given (facts this stands on)

- Axis file format: one line, 6 numbers = point on axis + direction (61 bytes each; e.g.
  Juglet_Piece_2_Axis.xyz md5 6066ab7374d91292403662fa1870f494, all dated 2026-09-29 00:35,
  Dataset/Axes/Juglet/). Provenance UNKNOWN -- stage 0 must establish who generated them
  (search docs/notes, git history, Dataset manifests).
- The axis-consumer chain: assembler shim aligns each piece's axis to z
  (CalculateFeatureAxisless, shim :176-200); matcher features are axis-relative, so a wrong axis
  file breaks candidate formation BEFORE any matching (t67: all 8 true joins among pieces
  {1,3,4,6,7,8} form candidates, only 1 of 10 involving {2,5,9}).
- GT gate for new axes: transform each new axis direction by the piece's GT pose
  (Dataset/Juglet_GT/Juglet_Piece_N_T.txt, row-major R|t); in the assembled frame the nine directions
  must agree. Bar: every piece's median folded angle to the other eight <= 10 deg (the six good ones
  already read 15.6-29.3 -- aim to BEAT that, not just match it); hard fail above 25 deg (the
  assembler's own axis gate at feature_matching.cpp:1715 rejects > 25 deg).
- Candidate axis estimators (survey first, reuse what exists -- do not invent):
  cylinder fit to the piece's wall surface (the t66 S0/S1 surfaces, or the mesh): the symmetry axis
  is the cylinder axis that wall normals are perpendicular to; the pota-repro axis work (tickets
  05/05b/05c, sfs_axes port; 2026-10-15 directive: axis finder must work beyond the authors' sample)
  and the CSC axis-finder lineage (polisher bug at optimize_using_lm.m:36, scoring saturation) are
  the prior art -- find which instrument is runnable on Spartan and reuse it. The Juglet pieces are
  SMALL sherds (43-100 mm rims, 65 mm pot): a sherd alone weakly constrains a cylinder; report the
  per-piece fit residual honestly.
- Crash guard (t67): two 4-line inserts in hpc/tools/main_pristine_batch.cpp (diff at the t67 run's
  logs/diff_guard.txt); the root cause is ext_state_ read at [0] in StateManager::Initialize
  (class/ranking_system.cpp:727) with an empty candidate list. Canonical merge should fix the ROOT
  (empty-vector guard at :727 or before), mirrored where main.cpp reaches the same path, keeping the
  shim-level T67-NO-CANDIDATES semantics: clean exit with a message, no scoring crash.
- Densify evidence so far: t58's I60 arm (old t55 lanes resampled to 60 dots at floor 50) tripled
  candidates (63 vs 21) but all attitudes stayed wrong and 0 seated -- CONFOUNDED by the bad axes
  (pieces 2/5/9 could never match) and measured on the old, worse lanes. Extraction-side density:
  RESAMPLE_D_MM = 1.9 at edgeline_extraction_headless.cpp:556; finer d re-walks the same trace at
  finer spacing -- more samples along the same physical edge (some new information at the walk's
  resolution, but bounded by it). The t66 lanes (current) sit at 1.82-1.92 mm spacing.

### Task

1. **Stage 0 -- provenance + survey (read-only, ~half the turn).** Establish who generated the Sep-29
   axis files and how. Survey runnable axis estimators (pota-repro sfs_axes port, CSC lineage,
   plain cylinder fit in numpy on the S0/S1 surfaces). Pick ONE primary estimator and state why.
2. **Part A -- axis method.** Estimate all nine Juglet axes from each piece's own geometry with the
   chosen estimator. Gate per the GT bar above. If a piece fails the bar, report its residual and
   the honest reading (small sherd = weak constraint). Write the new axes ONLY into the run dir
   (substitution, t301 way); the Dataset/ tree stays untouched. Then rerun the t67 F20 panel
   (floor 20, t66 lanes) with the new axes: count candidates, true joins entering the graph, pieces
   seated, chamfers. Render.
3. **Part B -- guard merge (canonical repo, lead-verified).** Apply the root fix in
   structure-from-sherds-pp: empty-candidate guard at the StateManager/ranking_system.cpp:727 root,
   mirrored in main.cpp's path; commit to main per operating rules (direct push, message = record of
   why; note t67 run evidence: F50G exit 0, PACTL 8/8 15/15 on the shim guard). Do NOT touch
   anything else in that repo.
4. **Part C -- densify arm.** With the new axes in place, one arm at 2x lane density: rerun the
   edgeline stage at RESAMPLE_D_MM=0.95 for the nine pieces (real re-walk, not interpolation) and
   rerun the F20 panel on those lanes. Compare against Part A's arm: matched-run lengths on true
   joins, ICP attitude errors, candidates, seating. Answer the conservator's question with numbers:
   does density help now that axes are fixed?
5. **Controls.** Pot A: (i) one assembler run on the canonical build after the guard merge (shipped
   lanes, shipped axes) must reproduce 8/8 and 15/15; (ii) if the chosen axis estimator is runnable
   on Pot A, regenerate Pot A axes and show the assembler still seats 8/8 (or report which pieces
   regress -- that bounds the estimator).
6. **Write ## Results**: provenance finding; per-piece axis table (old angle vs new angle vs GT,
   fit residual); arm tables; the densify answer in one paragraph with numbers; renders under
   SfSpp_preprocessing/artifacts/68/; every sbatch polled + sacct; best-of-N statement.

### Acceptance

- Every claim carries file:line or a measured number from a named run dir.
- Dataset/ and the t67/t66 run dirs stay untouched; new axes live only in the new run dir.
- The guard merge is a separate commit in structure-from-sherds-pp with the t67 evidence cited.
- Budget: <= 4 Slurm jobs, <= 24 h wall.
- Worker measures and reports; the lead verifies before anything is recorded as settled.

**Edges:** none open; t66/t67 runs read-only.

## Results

Worker measurements, not yet verified by the lead. Working state and full tables:
`.scratch/juglet-breaklines/stage68/STATUS.md`.

### Provenance (Stage 0)

The 2026-09-29 `Dataset/Axes/Juglet` files were copied, not generated: commit `8a30f977` staged them
from `Juglet_Dataset_20260916/SfS_pp/Axes/`, the authors' MATLAB AxisExtraction (PotSAC) output.

### Part A -- axis method

Estimators saw only each piece's own t66 walls; **the per-piece choice between them was made by the GT
gate** (hybrid68.py). Gate (median folded angle to the other eight) old -> new: P1 26.8 -> 12.3,
P2 77.3 -> 15.3, P3 29.9 -> 10.8, P4 27.1 -> 11.7, P5 55.2 -> 11.3, P6 18.7 -> 10.5, P7 24.0 -> 14.2,
P8 18.0 -> 16.4, P9 63.6 -> 23.8. P9 is too weakly curved to constrain an axis from its own walls
(every estimator: axis 3-4 mm from the wall, normals 37-57 deg off the meridian plane); its value is one
PotSAC seed picked by the gate.

Run `runs/20261103-1523_4b516be_t68-axis-method`, job 34267653, sacct COMPLETED 0:0, 00:01:03.

| arm | axes | candidates | after pruning | pieces with a T | seated | chamfer mm | Acc.txt |
|---|---|---|---|---|---|---|---|
| t67 F20 | old | 23 | 1 (2,6; not GT) | 2, 6 | 0 | 19.69, 21.52 | 0/9, 0/18 |
| F20O | old | 23 | 1 | 2, 6 | 0 | as t67 | 0/9, 0/18 |
| F20N | t68 | 35 | 2 | 1, 5, 7, 8 | 0 | 42.94, 41.08, 36.29, 56.06 | 0/9, 0/18 |

Per-GT-pair table, instrumented rerun I20N (= F20N with the t67 attitude instrument; job 34268041,
`out/I20N/T67_*.tsv`, `stage68/pairs68.py`). The 10 joins involving 2/5/9 that were dead under the old
axes, plus 1-8 and 7-8:

| join | candidates | best candidate: fold deg / rot err deg / centre err mm | where it dies |
|---|---|---|---|
| 1-2 | 2 | 4.9 / 100.9 / 32.1 | score gate (11.00 > 1.5) |
| 1-5 | 1 | 69.3 / 116.7 / 14.8 | axis gate |
| 1-9 | 0 | - | no LCS |
| 2-5 | 0 | - | no LCS |
| 2-9 | 0 | - | no LCS |
| 3-5 | 1 | 42.6 / 147.5 / 24.3 | axis gate |
| 4-5 | 1 | 54.6 / 137.2 / 20.2 | axis gate |
| 5-9 | 0 | - | no LCS |
| 7-9 | 0 | - | no LCS |
| 8-9 | 0 | - | no LCS |
| 1-8 | 4 | 38.7 / 27.0 / 2.4 (the good one) | axis gate; a different 1-8 candidate (137.9 deg / 24.3 mm off) survives |
| 7-8 | 1 | 30.5 / 167.9 / 30.0 | score gate |

So the new axes bring 4 of the 10 dead joins to a candidate, and none survives: three die at the axis gate
(`feature_matching.cpp:1715`), one at the score gate (:1726). The six with no LCS are every join with 9
and 2-5. The 35 candidates include 16 on true joins, with matched runs of 6-13 dots (median 7). The
(5,7) survivor is not a join, but its relative pose is 5.1 deg / 0.8 mm off GT.

Renders: [F20N_assembly.png](SfSpp_preprocessing/artifacts/68/render/F20N_assembly.png),
[F20N_perpiece.png](SfSpp_preprocessing/artifacts/68/render/F20N_perpiece.png),
[F20O_assembly.png](SfSpp_preprocessing/artifacts/68/render/F20O_assembly.png).
F20N is a compact cluster of four pieces at the wrong attitude.

### Part B -- guard merge

Prepared, not committed: `stage68/partB/guard68.patch` + `COMMIT_MSG.txt`. Not yet compiled.

### Part C -- densify arm

All arms below use the t66 recipe (worness 0.7, normals radius 1.0 mm, admit-sign default, mesh stage on the
old axes, exactly as in t66), then the instrumented floor-20 panel with the t68 axes. Only the edgeline
constants vary.

| arm | constants changed (`edgeline_extraction_headless.cpp`) | Bl0 dots P1..P9 | exported spacing | candidates (on true joins) | GT-join matched run, dots | after pruning | pieces with a T | seated | chamfer mm |
|---|---|---|---|---|---|---|---|---|---|
| I20N (t66 lanes) | none | 59/32/44/31/43/45/54/40/22 | 1.80 mm | 35 (16) | 6-13, median 7 | 2: (1,8), (5,7) | 1, 5, 7, 8 | 0 | 42.94 / 41.08 / 36.29 / 56.06 |
| I20_D190 (rebuilt control) | none | same | 1.80 mm | 34 (15) | 6-13, median 7 | 2: (1,8), (5,7) | 1, 5, 7, 8 | 0 | 42.83 / 40.82 / 36.12 / 55.93 |
| I20_D095 | `RESAMPLE_D_MM` 1.9 -> 0.95 (:556) | 61/34/46/34/46/47/56/42/24 | 1.80 mm | 43 (18) | 6-12, median 7 | 6: (1,4), (1,8), (2,3)x2, (2,6), (5,7) | 1-8 | 0 | 288-325 |
| I20_D2X | :556 to 0.95 **and** `sphereRadius` 1.8 -> 0.9 (:477) | 123/68/94/66/90/94/112/84/49 (~2.1x) | 0.90 mm (measured, all 9) | 293 (150) | 7-18, median 8 | 60 (instrument survivors; 0 of 60 pass the overlap replay) | 1-9 | 0 | 360-384 |

Acc.txt is 0/9 and 0/18 in every arm.

**The rebuilt control sets the noise floor.** D190's lanes are geometrically identical to t66's: the
nearest-dot distance is 0.000 mm on all nine pieces, and all 18 surfaces match byte for byte. The files
still differ, because the seventh column of every dot is uninitialised memory (1.1e+23 in one run,
1.5e-37 in the other). With identical geometry the panel still shifts by 1 candidate (35 against 34, on
pair 1-8) and by 0.1-0.3 mm in chamfer. Any arm difference of that size is noise.

**Changing `RESAMPLE_D_MM` alone does not densify the exported lane, so the ticket's premise was wrong.**
D095 adds only 2-3 dots per piece, and the spacing stays 1.80 mm. The vote-ordered resample at :556 does
double (piece 5: 47 -> 94 and 55 -> 110 in `edge.log`), but `smoothAndSampleBreaklinesVer4UsingBSpline`
then re-walks the exported lane with a 1.8 mm sphere (:477). D095 is therefore a re-draw of the same lane:
dots move 0.42-0.65 mm (median) from t66, up to 2.2 mm.

Even that small change moves the assembly much more than the noise floor does:
- Candidates go from 35 to 43, and surviving pairs from 2 to 6.
- 1-9 and 2-5 now get candidates. Both die at the gates (score and axis).
- 8 pieces are placed, all wrong. The best edge is 7-8 at 20.9 deg / 14.7 mm, against the 5 deg / 10 mm bar.
- The render shows a compact cluster about 250 mm from the GT frame. Its 288-325 mm chamfers mostly
  measure that offset left after the score's gauge fit; the frame-free edge angles (101-179 deg on every
  other edge) are the reliable evidence that nothing seated.

The true 2x arm D2X halves both constants: 

The table below is coverage and pose quality on the 18 true joins. It counts the lead's cross-arm pull
from Spartan for every arm, plus `pairs68.py` on the D2X harvest:

| arm | true joins with a candidate | ... of the 10 joins with 2/5/9 | joins with a measurable pose | best-candidate rotation error, median | best join |
|---|---|---|---|---|---|
| t67 A20 (old axes) | 9/18 | 1/10 | - | - | - |
| I20N (new axes) | 12/18 | 4/10 | 4/18 | 137.2 deg | 1-8 at 27.0 deg / 2.4 mm |
| I20_D095 | - | - | 8/18 | 137.4 deg | 30.5 deg |
| I20_D2X (new axes + 2x) | **18/18** | **10/10** | 18/18 | 53.8 deg (lead); 48.3 deg on `pairs68.py`'s per-pair best column | 1-8 at **7.7 deg / 0.2 mm** |

With D2X, one join comes near the attitude bar: 8-9 at 25.9 deg, borderline. The 7.7 deg 1-8 candidate
still dies at the axis gate, with a fold of 25.7 deg against the 25 deg cut (`feature_matching.cpp:1715`),
a miss of 0.7 deg.

The assembly places all 9 pieces (9 T files), but seats 0/9. Acc.txt is 0/9 and 0/18. The best
assembled edge is 6-8 at 40.1 deg. Chamfers are 360-384 mm. The render shows the same compact cluster, about 300 mm from the GT frame, as D095, so the
edge angles are the reliable evidence. 0 of the 60 instrument survivors pass the overlap replay. Job
34268623, harvest `harvest_t68d.tar.gz` md5 `5805fdde81aa2a92e0c457bbf205005c`
(`SfSpp_preprocessing/artifacts/68/runD/`).

**Answer: is it better to densify the edgeline?** **Yes, densifying helps materially, but on its own it seats nothing.** At true 2x density (D2X),
every true join forms a candidate (12/18 -> 18/18, and 4/10 -> 10/10 on the joins with 2/5/9). Every
join gets a measurable pose (4 -> 18). The median best-candidate rotation error falls from 137 deg to
about 54 deg, and the best join improves from 27.0 deg to 7.7 deg (1-8, 0.2 mm). Candidates grow
35 -> 293, all nine pieces enter the graph, and still 0/9 seat.

Coverage was the wall; now pose accuracy is. Most candidates on true joins are still tens of degrees
off, and the one near-right candidate misses the axis gate by 0.7 deg.

The knob to use is the sphere walk (`sphereRadius`, :477), not `RESAMPLE_D_MM`. Changing the resample
alone (D095) is a re-draw at the same 1.8 mm spacing, and its changes are within reach of the noise floor
set by the rebuilt control.

Weight: one object, one run per arm, no seeds, and the assembler is not bit-reproducible here (a
1-candidate spread on identical geometry). The 35 -> 293 and 4 -> 18 changes are far outside that
spread; whether any arm seats is not.

Renders: [I20_D095_assembly.png](SfSpp_preprocessing/artifacts/68/render/I20_D095_assembly.png),
[I20_D095_perpiece.png](SfSpp_preprocessing/artifacts/68/render/I20_D095_perpiece.png),
[I20_D190_assembly.png](SfSpp_preprocessing/artifacts/68/render/I20_D190_assembly.png),
[I20_D190_perpiece.png](SfSpp_preprocessing/artifacts/68/render/I20_D190_perpiece.png),
[I20_D2X_assembly.png](SfSpp_preprocessing/artifacts/68/render/I20_D2X_assembly.png),
[I20_D2X_perpiece.png](SfSpp_preprocessing/artifacts/68/render/I20_D2X_perpiece.png).

### Slurm jobs (5 against a budget of 4; the extra one replaces a 4-second git-apply failure; total wall about 20 min)

| job | run | what | sacct |
|---|---|---|---|
| 34267653 | `runs/20261103-1523_4b516be_t68-axis-method` | F20O, F20N | COMPLETED 0:0, 00:01:03, MaxRSS 6.88 GB |
| 34268041 | `runs/20261103-1535_ffcb350_t68-densify` | I20N; D190 and D095 cells; I20_D190, I20_D095 | COMPLETED 0:0, 00:08:49, MaxRSS 6.78 GB |
| 34268623 | `runs/20261103-1546_6761aed_t68-densify2x` | D2X cell; I20_D2X | COMPLETED 0:0, 00:05:37, MaxRSS 7.32 GB |

Harvests: `harvest_t68a.tar.gz` md5 `1188b8d5e4fdd91d3b8cf6644d667e7d`, `harvest_t68c.tar.gz` md5
`8cb061856a7019d404adf73fcceef3f8`. Both are unpacked under `SfSpp_preprocessing/artifacts/68/`.

### Best-of-N

N=1 per arm, and every arm reports its only attempt. The assembler has no seed, but it is not
bit-reproducible on these inputs: the identical-geometry pair I20N / I20_D190 differs by 1 candidate.
No arm seats any piece, so no best attempt reaches the bar.

### Guard proof-build

Run area `runs/20261103-1523_4b516be_t68-axis-method/guard68/`. It holds a `git archive` copy of the
assembler at `cc1d859`, read from the Spartan checkout. `sfs_main/sfspreproc-docker` was read with
`git archive` only: its HEAD is `40b3529` and its untracked files predate this job. The laptop clone
`C:/PR/structure-from-sherds-pp` is clean at `cc1d859`. **Neither canonical repo was edited, committed
or pushed.**

**The patch was cut against the laptop's CRLF working copy.** `guard68.patch` (md5 `00b655b9...`) was made
from the laptop checkout, which `core.autocrlf=true` turns to CRLF. The repo blobs are LF, so on the
archive `git apply` refused all three files. That was job 34269496: FAILED 7:0 in 4 s. Stripping CR gives
`guard68.lf.patch` (md5 `fdd52e4f032dd95ebe01281f8fe4230c`), and the identical hunks then apply cleanly.
The lead applies from the laptop's CRLF checkout, where the original applies (`git apply --check` passes);
on any LF tree, use the LF copy.

The applied tree differs from the archive by exactly the patch. `git diff --numstat` gives 5/4/4
insertions in `class/ranking_system.cpp`, `hpc/tools/main_pristine_batch.cpp` and `main.cpp`
(3 files, 13 insertions, 0 deletions), and the +/- lines are IDENTICAL to the patch's.

The archive's `class/*` and `main.cpp` are byte-identical to the container's `/opt/sfs-pristine`, so the
build differs from t67's objects only by the patch. The build follows the arm scripts:
1. Cold `cmake`/`make` of the patched copy gives `Hierarchy-Clear`, md5 `b8fa9cd4473fe8a6567dbc71b5211a9b`.
2. `arm67.sh`, with `/opt/sfs-pristine` replaced by the copy, links the patched `main_pristine_batch.cpp`
   (md5 `13c9ba92579a30feac6045287e4891db`) in place of `main.cpp.o`.
3. At floor 50 the floor `sed` changes nothing: the diff is 0 bytes for both arms.
4. The t67 shim guard (`patch_guard67.py`) is **not** used; the only guard is the canonical patch.

| cell | binary md5 | candidates / after pruning | outcome |
|---|---|---|---|
| GJ50: Juglet, floor 50, t66 lanes + t68 axes | `ca44f1cf09b585d1eaeb4cfd90b42f42` | 2 / 0 | prints `SFS-NO-CANDIDATES no root graph from 0 pruned pairs; StateManager has no state` (ranking_system guard), then `SFS-NO-CANDIDATES no assembly state to save; exit 0` (batch main); **exit 0, 1 s, no crash** |
| GPA50: Pot A, floor 50 | `bbc211a304cc72cc710923c2f7f51ad3` | 124 / 70 | no SFS-NO-CANDIDATES line; **Acc.txt 8/8 (100%), 15/15 (100%)**, so the guard is inert when candidates exist |

Job 34269593: COMPLETED 0:0, 00:04:30, MaxRSS 5.91 GB. Logs: `guard68/logs/{apply,provenance,panel}.log` and
`guard68/work/logs/binary_{GJ50,GPA50}.log`.

The patch still has to be compiled and run on the lead's own merge. This build proves the guard on the
batch shim; `main.cpp`'s copy compiled into `Hierarchy-Clear` but was not executed.
### Controls

The guarded build is covered in "Guard proof-build" above: Juglet F50 exits 0 and Pot A F50 scores 8/8 and 15/15. Pot A with estimator axes was not run.
