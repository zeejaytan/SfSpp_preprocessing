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

Per-GT-pair table for the 10 joins involving 2/5/9 (candidates / pruning / axis gate / rotation error):
TODO -- needs the t67 attitude instrument on the axes68 tree (job 2 of 4).
Renders: [F20N_assembly.png](SfSpp_preprocessing/artifacts/68/render/F20N_assembly.png),
[F20N_perpiece.png](SfSpp_preprocessing/artifacts/68/render/F20N_perpiece.png).
Best-of-N: the assembly path has no RNG; N=1 per arm (F20O reproduces t67 F20's transform set).

### Part B -- guard merge

Prepared, not committed: `stage68/partB/guard68.patch` + `COMMIT_MSG.txt`. Not yet compiled.

### Part C -- densify arm

TODO.

### Controls

TODO (Pot A on the guarded canonical build; Pot A axes from the estimator).
