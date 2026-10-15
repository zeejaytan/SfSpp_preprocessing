# 08: Pristine axle failure repro (no fork in the loop)

**What to build:** the honest failure — run the author's axle chain as released on Pot A and score its axles against the shipped Pot A axle files. No fork code, no NURBS, no repaired anything.

**Answers:** E1

**Blocked by:** 07-pristine-potsac-map.

**Status:** results-in — lead review 2026-10-15: exact-blocker branch of acceptance, all four items present; jobs 33063495/33063707 COMPLETED 0:0 per sacct (driver completed; MATLAB errors are the result). Verdict: NO — 0/8 pieces yield an axle. Two stacked defects: missing `load_root_dir` (0 definitions) kills the loader; past that, `compute_cao_error.m:21` dimension crash kills the vote on iteration 1; missing `refine_axis` never reached. Correction to 07 accepted: `cao_update_func.m:18` parens balanced, smoke-tested, not a defect. Routes to 09 (repair-or-kill).

**Pristine-only rule (binding):** same as 07. If the released chain cannot run as-is (missing loader, bad paths, crashes), that IS the result — record the exact error + file:line and stop that arm; do not borrow fork helpers to get it moving.

- [ ] Author-chain axles for all 8 Pot A pieces vs shipped axle files: direction error (deg) + radial position error (mm) per piece, median + worst
- [ ] Verdict with numbers: does the released chain reproduce the shipped axles (bar: ≤5° and ≤2mm on 8/8), and if not, which stage in the 07 map introduces the error
- [ ] Each claimed defect pinned to pristine file:line + observed behaviour (log/error/number), not inference
- [ ] Comments section: per-piece table + the single sentence "the author's path reproduces its shipped axles: yes/no" with the numbers attached

## Comments (worker, 2026-10-15)

Tree actually run: upstream https://github.com/DominicoRyu/SfSpp_preprocessing @ d5ee6865
("250306_v2"), cloned fresh twice — laptop C:\Temp\potsac-p08 and Spartan
/data/gpfs/projects/punim2657/Temp/potsac-p08-pristine (both `git rev-parse HEAD` =
d5ee6865ab1e585d18175670a0cd834e846d4490). All file:line = AxisExtraction/*.m in that
pin. Execution: MATLAB R2025b on Spartan compute node (jobs 33063495, 33063707, both
sacct COMPLETED 0:0 — the driver completed; the MATLAB errors below ARE the result).
Paper refs = papers/text/sfspp-2502.13986v1.md:169-177. No fork files opened, nothing
committed. Shipped answer key = sfs_main/original_samples/SfS_pp/Axes/Pot_A_Piece_0i_Axis.xyz
(pieces 01-06 one axis each, 07 three axes, 08 two axes — matches 07).

Per-piece result (no author-chain axle produced on any piece, so no direction/position
errors exist to score — acceptance falls to the exact-blocker branch):

| Piece | Arm A: extract_axis as released | Arm B: run_potsac on shipped surfaces (MATLAB-builtin load only) |
|---|---|---|
| 01 | load_root_dir undefined @ read_surfaces.m:15 | cross size mismatch, via compute_cao_error.m:21 |
| 02 | same as 01 | same as 01 |
| 03 | same as 01 | same as 01 |
| 04 | same as 01 | same as 01 |
| 05 | same as 01 | same as 01 |
| 06 | same as 01 | same as 01 |
| 07 | same as 01 | same as 01 |
| 08 | same as 01 | same as 01 |

Defects pinned to pristine file:line + observed behaviour:
1. read_surfaces.m:15 (also read_axis.m:14, write_axis.m:7) calls load_root_dir, which is
   defined nowhere in the pin (grep: 0 definitions) — observed: `Undefined function
   'load_root_dir' for input arguments of type 'char'` on all 8 pieces via
   extract_axis.m:6. Coded root 'D:/SFS_BB_temp/Plt_A' + Plt_* names cannot address
   shipped Pot_A_* files regardless.
2. compute_cao_error.m:19-22 — `vt = reshape(vt,6,1,[])` then T1 = bsxfun(@minus,
   X(1:3,:), vt(4:6,:,:)) is 3x(n>1), but cross() at :21 does not implicitly expand the
   3x1x1 axis slice — observed on all 8 pieces: `A and B must be same size`
   (MATLAB:cross:InputSizeMismatch), stack compute_cao_error.m:21 <-
   compute_biaxial_cao_error.m:16 <- compute_axis_of_symmetry.m:29 <- run_potsac.m:17.
   The MLESAC vote crashes on iteration 1 for every real multi-point input, so the
   run_potsac.m:34,66 refine_axis calls (also MISSING, 0 definitions — 07 confirmed) are
   never even reached.
3. Toolbox note (observed, info only): randsample present (Statistics), tmult missing
   (no Tensor Toolbox) — tmult sits only in the nargout>1 Jacobian branch, never reached.
4. Correction to 07: cao_update_func.m:18 has balanced parens in d5ee6865 and executes
   (smoke-tested: 6x1 in -> 6x1 out) — the "extra paren" note is not a live defect.

The author's path reproduces its shipped axles: NO — 0/8 pieces yield an axle; the
released chain errors out at the surface-loader stage (missing file) and, past that, at
the vote-cost stage (dimension crash), before any refinement or output.
