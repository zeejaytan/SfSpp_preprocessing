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

**Status:** ready-for-agent
**Working in:** (ticket_start fills this)
**Branch:** 68-axis-method, in /c/PR/worktrees/sfs/68
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
