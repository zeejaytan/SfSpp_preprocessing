# Task-3 axes plan handoff (for POTA-05)

Source: sfs-axes-planner report 2026-10-15 (read-only audit, no edits).

## 1. Per-file gap table (released chain = SfSpp_preprocessing/AxisExtraction/*.m; vendored original_nurbs_preprocessing/AxisExtraction/ stale, do not build from it)

- G1 read_surfaces.m:8-15 — loader missing + Windows paths. Only live lines 15,21-22,30-32: root_dir = load_root_dir('D:/SFS_BB_temp/Plt_A', extended), reads Surfaces/Pot_%s_Piece_%02d_Surface_0/1.xyz. No configurable input path.
- G2 load_root_dir.m:1-12 — fork shim (hardcoded /data/gpfs/.../sfs_preprocessing), absent upstream.
- G3 read_axis.m:12-15 + write_axis.m:6-10 — Plt_/Pot_ naming split + Windows root. Assembly expects Axes/Pot_A_Piece_0{1..8}_Axis.xyz (data_path.h:1417-1426). extract_axis.m:22 writes ../axis_output/Pot_... (third convention). None parameterised.
- G4 compute_cao_error.m:21-33 — dimension error on current MATLAB (bare cross(T1,vt) fails 6x1 vs 6xN); repmat fix is cluster ff40fc9, absent upstream. catch_actual_error.m is the fork's 20-seed hunt for this.
- G5 refine_axis.m (60 lines) + compute_biaxial_cao_error.m + optimize_using_lm.m + cao_update_func.m — fork-only refinement (Huber + LM 300 iters, reprojection). run_potsac.m:46-48,78-80 call it twice (10% then full-C). Without it, paper L175 final refinement has no implementation.
- G6 run_potsac.m:10-12,18-30 — sampling drift: paper says 10% (L175); code uses adaptive step (1 if <5k, ceil(n/10k) if >50k, else round(n/10k)). Integer-half fix also cluster, not upstream.
- G7 compute_axis_of_symmetry.m:1-53 + compute_pottmann_axis.m:9-25 — core solver sound but MATLAB-locked (MLESAC 1000x6-pt + Pottmann 6x6 eigen, smallest singular vector). No Python equivalent in repo.
- G8 edgeline_extraction.cpp:2603,2865 — preprocessing-side axis consumer dead-or-hardcoded (C:\Users\cpp\... path; ../Dataset/Axes/ gate). Axis only re-labels rim segments (50% rule), never blocks geometry. Low blast radius.

Paper method (IV-B2, L169-177): PotSAC = MLESAC + 6-pt Pottmann, extended Cao-Mumford error on BOTH surfaces, trust-region optimisation; top-10 with <=10deg dedup; 10% for candidates, all points for final refine. Rim: sigma<=1.0mm, delta<=0.1mm, >=20 pts.

## 2. Reimplementation file plan: new package SfSpp_preprocessing/sfs_axes/ (numpy+scipy only)

- io_surfaces.py — replaces read_surfaces.m + load_root_dir.m (G1/G2). Config-driven loader, Pot_A_Piece_%02d_Surface_{0,1}.xyz N×6 (x y z nx ny nz, mm). Equal-count truncation kept as explicit option, flagged for removal.
- plucker.py — euc2plucker.m, cross2mat.m, tmult.m ports, unit-tested vs MATLAB.
- pottmann.py — compute_pottmann_axis.m (G7). 6-pt solver (M-reduction + SVD + vt=[v;cross(v,vbar)]).
- cao.py — compute_cao_error.m + biaxial (G4/G5). Biaxial log-sum-exp s=100; repmat becomes broadcasting.
- robust.py — huber/gm/cauchy + apply. GM candidacy, Huber refinement.
- potsac.py — compute_axis_of_symmetry.m + run_potsac.m (G6/G7). MLESAC 1000×6-pt, 10% sampling (paper letter; adaptive-step as CLI flag), top-10 + 0.9848/10deg dedup + 10% cost prune, seeded RNG.
- refine.py — refine_axis.m + optimize_using_lm.m + cao_update_func.m (G5). scipy least_squares huber + unit-direction/orthogonal-position reprojection; two-stage preserved.
- io_axes.py — read_axis.m + write_axis.m + extract_axis save (G3). Single ORIG-compatible writer/reader; Plt_/axis_output variants deleted.
- cli.py — extract_axis.m + 8× run_axis_piece_*.m. `extract-pot-a --surfaces DIR --out DIR --seed N`.
- tests/test_regression_pota.py — ORIG-anchored regression.

Non-goals: no change to assembly ReadAxis; no edgeline rim-rule change; no MATLAB shim maintenance.

## 3. I/O contract (Pot A, 8 axes)

- Input per piece: Surfaces/Pot_A_Piece_0i_Surface_0.xyz + _Surface_1.xyz, ascii N×6 (x y z nx ny nz, mm).
- Output per piece: Axes/Pot_A_Piece_0i_Axis.xyz, ascii K×6 (px py pz dx dy dz, position mm + unit direction, row1 = best/lowest cost). write_axis.m:8 convention (vt([4 5 6 1 2 3],:) position-first) = what ReadAxis parses (data_structure.cpp:146-187, multi-line = multi-axis). K>=1, cost-ordered (run_potsac.m:94-95 sort).
- Binding: data_path.h:1391-1426 SHARD_NUMBER 8, axis_path[8] alongside Breaklines/Mesh/Surfaces/GT. Output must drop into these 8 paths byte-compatible (6 cols/line, %.12f+).
- Reference anchors (read in place, do not copy): authors' ORIG axes + Ground Truth Axes Pot_A 8 files.

## 4. Acceptance (Table V tauR=20deg/taut=50mm + gate needs)

- Direction <=5deg vs ORIG (cos>=0.9962). Rationale: 2×5=10 worst-case leaves 10deg headroom inside 20deg gate; dedup scale is 10deg so acceptance is half that.
- Position radial <=2.0mm, axial <=2.0mm. Rationale: taut=50mm loose; binding constraint is rim gate (sigma<=1.0mm) + strict seam gate 2.0mm; 2mm is ceiling not target.
- Completeness 8/8 K>=1, untouched ReadAxis loads count>=1, no warnings.
- Functional: (a) rim-label agreement with ORIG-axis labelling >=7/8; (b) (h,r,alpha) recomputed with fresh axes keeps ORIG 15/15 strict-gate self-consistency (min-disp median 0.77mm max 1.30mm).
- Proof order: ORIG surfaces FIRST (quarantines task-2 +Z shift), THEN fresh surfaces separately with shift disclosed — never mix.

## 5. Risks

R1 trust-region port fidelity (MATLAB vs scipy step acceptance) — port update literally, lock seed + tolerances (1e-3 stage-1, 1e-9 stage-2). R2 normal-sign ambiguity — must port both biaxial branches (s=100), naive single-side biases to cylinders. R3 RNG non-equivalence — seed-sweep >=3 seeds, acceptance on best-cost. R4 surface-shift contamination — two-stage proof exists for this. R5 stale-vendored trap — import only root AxisExtraction/ pins. R6 licence/quota — zero MATLAB licence (static audit only); Python needs numpy/scipy on laptop.
