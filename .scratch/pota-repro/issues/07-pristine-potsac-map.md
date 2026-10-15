# 07: Pristine PotSAC map (paper §IV-B2 → author files)

**What to build:** the map the repair stands on — every step of paper §IV-B2 (axle estimation) traced to the exact pristine file and line that implements it, or marked MISSING.

**Answers:** E1

**Blocked by:** none. **Blocks:** 08, 09.

**Status:** results-in — lead review 2026-10-15: all four acceptance items present (per-step map with file:lines, I/O chain, constants table, Comments appended). Headline: `refine_axis` (called run_potsac.m:34,66) is MISSING from pin d5ee6865 — the paper's refinement stage has no implementation in the released tree; `load_root_dir.m` also missing and coded `Plt_*`/`D:/` paths cannot address shipped `Pot_A_*`. Routes to 08 (repro) then 09 (repair-or-kill).

**Pristine-only rule (binding):** paper text + pristine checkout (`sfs_main/archive_2025_sfs_modified_src @ 9195c01`, upstream `DominicoRyu/SfSpp_preprocessing @ d5ee6865`) only. Do NOT open any `SfSpp_preprocessing` fork code, `sfs_axes/`, `notes/task3-axes-plan.md`, or issues/05. A ticket citing them fails review.

- [ ] For each §IV-B2 step (surface input → profile sampling → PotSAC vote → robust refinement → axle output): pristine file + line, or MISSING with what the paper says it should do
- [ ] Inputs/outputs per step: format, units, coordinate frame; where the shipped Pot A axle files (`Axes/Pot_A_Piece_0i_Axis.xyz`, position-first per `data_structure.cpp:146–187`) come out of the chain
- [ ] List every hardcoded constant in the axle path with file:line and the paper value it should match (if the paper gives one)
- [ ] Comments section: numbered gap table (paper-step → file:line or MISSING), no fix proposals

## Comments (worker, 2026-10-15)

Source tree actually read: upstream https://github.com/DominicoRyu/SfSpp_preprocessing @ d5ee6865
(cloned to C:\Temp\potsac-pristine; `git rev-parse HEAD` = d5ee6865ab1e585d18175670a0cd834e846d4490,
log "d5ee686 250306_v2"). All file:line below = AxisExtraction/*.m in that clone unless noted.
The Spartan `sfs_main/archive_2025_sfs_modified_src` checkout is assembly-side layout (class/,
main.cpp, CMakeLists) — no MATLAB AxisExtraction files there, so the upstream clone is the
sole code source. Pot A data + shipped axles listed from
`sfs_main/original_samples/SfS_pp/` (Axes, Surfaces, Mesh, Breaklines, Ground Truth Axes).
Paper refs = C:\PR\papers\text\sfspp-2502.13986v1.md:169-177 (§IV-B2). No fix proposals per ticket.

Gap table (paper-step → pristine file:line or MISSING):
1. Surface input (interior+exterior clouds with normals) → read_surfaces.m:21-32
   (C0/C1 rows 1:6 from Surfaces/*_Surface_{0,1}.xyz); produced by upstream
   mesh_processing.cpp:1743-1757 via convertPLYtoXYZ (:1329-1339, 6 cols x y z nx ny nz).
2. Profile sampling (10% subsample for candidates) → run_potsac.m:17 (C(:,1:10:end))
   and :34. Matches paper "initially sample only 10%".
3. PotSAC vote (MLESAC + minimal 6-point Pottmann solver) → compute_axis_of_symmetry.m:1-53
   (1000 iters, randsample 6, demean/rescale :18-23, compute_pottmann_axis.m:10-25 SVD,
   rescale + tangent projection :25-27, biaxial Cao error + GM robustifier :29-32, min-cost
   sort :48-50). Note: inlier_threshold=1.0 (:12) is counted (:31,34) but selection is pure
   min-cost sort — paper calls it "MLESAC-based", reported as observed.
4. Robust refinement (extended Cao–Mumford, both surfaces, nonlinear opt) → MISSING FILE:
   run_potsac.m:34,66 call refine_axis(...), defined nowhere in the pin (grep: only those two
   call sites). Nearest existing parts: compute_biaxial_cao_error.m:1-43 (soft-min s=100 over
   fwd/rev normals), compute_cao_error.m:1-56, optimize_using_lm.m:1-94 (hand-rolled LM, zero
   callers in tree), cao_update_func.m:1-21, apply_robustifier.m:1-25, robustifier_gm.m,
   robustifier_huber.m. Also cao_update_func.m:18 as shipped has an extra closing paren:
   `vt(4:6) = vt(4:6) - vt(1:3) * (vt(1:3)' * vt(4:6));` — quoted verbatim, not judged.
5. Multi-axis select/prune → run_potsac.m:21-82 (top 10 :21; Huber biaxial cost :38-44; dedup
   dot>0.9848=cos10° :52-55; keep cost<cost(1)*1.1 :60; full-data refine :65-67; re-dedup
   :70-79; sort :81-82). Matches paper (top 10, ≤10° dupes dropped by higher robustified
   residual cost, all-points refinement).
6. Axle output → write_axis.m:8-10 writes vt([4 5 6 1 2 3],:)' = POSITION-FIRST rows to
   Axes/*_Axis.xyz; consumed by BreakLine::ReadAxis
   (C:\PR\structure-from-sherds-pp\class\data_structure.cpp:146-187, x y z nx ny nz loop).
   Shipped Pot A: pieces 01-06 single axis (1 line each), piece 07 three axes, piece 08 two
   axes — multi-axis shipped output fits the modified-PotSAC design.
7. Rim detection → check_base_and_rim.m:13-16,115-122. Thresholds match paper (std h/r ≤1.0;
   |mean dr/dh|<0.1; ≥20 pts at :116). Nuance: paper says "average variation ... between
   adjacent points"; code uses mean of signed diffs mean(dr(2:end-1)) (:40-43), which
   telescopes — reported, not judged.

I/O chain: Mesh/Pot_A_Piece_0i_Mesh.obj (mm, scanner frame) → mesh_processing.cpp surfaces →
Surfaces/Pot_A_Piece_0i_Surface_{0,1}.xyz (ascii space-delim, 6 cols x y z nx ny nz + trailing
space; Pot A counts 1576–19463 pts/surface; mm; mesh frame) → extract_axis.m:6-8 →
run_potsac → Axes/Pot_A_Piece_0i_Axis.xyz (ascii, one 6-number line per axis:
px py pz dx dy dz; mm position + unit-ish direction; same frame). Internal axis repr vt is
6x1 [direction; position] with direction·position=0 enforced
(compute_axis_of_symmetry.m:27, cao_update_func.m:18). E.g. piece 01 line 1:
`-55.46 -133.90 62.44 0.228 0.332 0.915`.

MISSING glue / externals in the axle path (reported, not judged): load_root_dir.m (called by
read_surfaces.m:15, read_axis.m:14, write_axis.m:7, read_breakline.m:15, write_surfaces.m:8,
check_surface_inversion_v2 path, write_breakline.m — defined 0 times; coded root is the
absolute `D:/SFS_BB_temp/Plt_A` with `Plt_*_Piece_*` names, while shipped files are
`Pot_A_Piece_*`, so as-pinned helpers cannot address shipped Pot A paths);
frag_type_to_base_and_rim.m (called read_breakline.m:36, defined nowhere);
align_point_cloud (called check_base_and_rim.m:57, defined nowhere); tmult (tensor toolbox,
used by compute_cao_error.m, compute_biaxial_cao_error.m, apply_robustifier.m,
compute_rim_errors.m); randsample (MATLAB Statistics toolbox). compute_rim_errors.m has zero
callers, and its nargout>1 Jacobian branch names variables never defined in that function
(cross_T1, T5, cross_nhat, norm_T2_by_T3, cross_vhat) — quoted as observed.

Constants (file:line → paper §IV-B2 value): 10% subsample run_potsac.m:17,34 → "sample only
10%" ✓; top-10 :21 → "top 10 candidate axes" ✓; dupe angle dot>0.9848 (=cos10°) :52,73 →
"10 degrees or less" ✓; keep ×1.1 :60,77 → "higher cost ... removed" ✓-ish (code refs first
survivor's cost); 6-pt sample + 1000 iters compute_axis_of_symmetry.m:7,9 → "minimal 6-point
solver" ✓ (1000 not in paper); inlier 1.0 (:12), soft-min s=100
(compute_biaxial_cao_error.m:12), Huber/GM width 1.0 (robustifier_huber.m:16,
robustifier_gm.m:14), LM init 1e-1/min 1e-14/max 1e14/20 trials (optimize_using_lm.m:25-28),
refine (300,1e-3)→(300,1e-9) (run_potsac.m:34,66) → no paper values; rim std 1.0 / dr-dh 0.1 /
≥20 pts (check_base_and_rim.m:13-16,116) → 1.0mm / 0.1mm / 20 points ✓; base thresholds radius
25.0 / normal 10.0° / angle-diff 30.0° / z-bin 5.0mm / counts>100 / std 0.25 (:52-55,99-100) →
no §IV-B2 values; inversion z-tolerance 1e-9 (check_surface_inversion_v2.m:24) → none.

Could not pin down: positional args of the missing refine_axis (vt,C,2,[],[],300,1e-3) —
meaning of `2` and `[]`s unknowable without the file; which code revision produced the shipped
Pot A axles (no provenance file in the pin; coded names are Plt_*, shipped are Pot_A_*);
units are inferred mm (data scale + paper mm thresholds), no explicit units line in code.
