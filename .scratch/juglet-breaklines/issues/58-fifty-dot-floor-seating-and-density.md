# 58 — The 50-dot floor: what it throws away, and whether fewer points still seat

**What to build:** a measured answer to whether the assembler's hard 50-dot floor
discards seatable Juglet pieces, and which of the two cures is right — remove/scale the
floor, or increase dot density — including what the correct way to densify is if density
is chosen. One experimental assembly run set (never merged) plus one interpolation control
that separates "the matcher needs count" from "the matcher needs information".

**Why now (2026-11-02, conservator):** "less than 50 points edgeline is thrown away and
not attempted. It is strange a hard limit is set. Investigate if it is affecting the
seating downstream with less points. The option is remove this limit, or increase the
density, and if increase density what is correct way to do it."

**Answers:** U19 (does the pipeline put the Juglet back together), E1 (do our breaklines
let SfS find joins)

**Blocked by:** none (uses the t55 run of record read-only; runs alongside 57 — different
repo; do NOT write inside the t55 run dir)

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-02)
**Branch:** 58-fifty-dot-floor-seating-and-density, in /c/PR/worktrees/sfs/58
**Worker:** unassigned

## Spec

### Given (measured facts this stands on)

- The gate: `structure-from-sherds-pp/main.cpp:86-90` — inside the load loop,
  `if (shard[i].edge_line_.point_.cols() < 50) { shard_on_off[i] = false;
  shard[i].edge_line_.Remove(); continue; }`. The piece is dropped from assembly
  entirely (not attempted, exactly as the conservator put it).
- Provenance of the 50: created in the repo's first commit `ab85ea3` (authors' import;
  `git log -L 86,90:main.cpp` shows no later edit). No rationale comment; the paper text
  (papers/text/sfspp-2502.13986v1.md) states no 50-point minimum anywhere.
- `MINIMUM_NUMBER 6` at `structure-from-sherds-pp/class/reconstruction.h:24` (same first
  commit; semantics untraced — it sits beside `INLIER_THRESHOLD 1.5` and
  `ANGLE_THRESHOLD 0.262`, so it may be a correspondence-count floor, not a piece count).
- At the t55 run of record (SFS_WORNESS=0.7), Bl0 dot counts J1..J9 =
  28/32/38/32/47/46/54/41/23 — only J7 (54) clears the floor. Loop lengths 41.7–98.3 mm,
  spacing ~1.8 mm (paper d = 1.9 mm "an empirically optimized value",
  `SfSpp_preprocessing/edgeline_extraction_headless.cpp:556`). At paper density the floor
  means: any break shorter than ~95 mm of edge is never attempted — 8 of 9 Juglet pieces.
  Pot A loops are 110–372 mm, so every Pot A piece clears it; the floor may simply encode
  "Pot-A-sized breaks".
- The Juglet wiring exists (`#ifdef JUGLET`, `data_path.h:1498-1604`): SHARD_NUMBER 9,
  expects under JUGLET_BASE `Breaklines/`, `Mesh/`, `Axes/`, `Surfaces/` (S0/S1 as
  .xyz + Surface_F .pcd), `Ground Truth/` per-piece `_T.txt` + `Juglet_simple_graph.txt`;
  the comment at data_path.h:1494 records "GT is REAL (derived ticket 01)". JUGLET_BASE
  (`data_path.h:1502`) points at `/data/gpfs/projects/punim2657/sfs_preprocessing/Juglet_Dataset_20260916/SfS_pp/`
  which is NOT on Spartan any more — locate the surviving copy of that dataset (GT, Axes,
  Surface_F) before any run; if GT truly no longer exists, seating claims downgrade to
  join-quality + renders and the ticket says so explicitly.
- Known interplay (ticket 56, resolved): fresh Bl0 headers over-count points by the segment
  count, and the reader's per-segment ranges are only dereferenced when `is_seg_rim_` is
  set — today's writer hard-codes the flag to 0, and `NO_RIM_INFO` (main.cpp:100-104)
  forces it false anyway. Lowering the floor admits more files carrying that latent header
  defect; verify in the experimental build that no code path newly dereferences those ranges.
- Prior lesson on short-lane matching (Pot A, ticket 45): the LCS edge matcher needed
  ~45+ honest inliers to form a join — if short lanes starve the MATCHER, the failure is
  matching, not seating. Name which claim each measurement supports.
- The Spartan assembler build is NDEBUG (-O3): out-of-range reads are undefined behaviour,
  not an abort. Watch dot-index loops on short lanes.

### Task

1. **Trace the gate (read-only).** Where `shard_on_off` is consumed and what a false
   entry skips; every use of `MINIMUM_NUMBER` (grep, file:line) and whether assembly can
   run with 2–3 active pieces; what `NUM_MIXED_SHERD 1` does; whether 50 or 6 appears in
   the paper or the upstream twins (`original_nurbs_preprocessing/`, edgeline twins).
   Locate the surviving Juglet 20260916 dataset (or successor) for GT/Axes/Surface_F.
2. **Floor-removal experiment (experimental build, never merged).** Build the assembler in
   the run area with the floor lowered (10) and separately removed (0); record both md5s
   and the diff; stage a compatibility JUGLET_BASE directory from t55 outputs plus the
   located GT/Axes/Mesh (stage copies — never edit inside the t55 run dir). Run assembly
   best-of-N (report the best attempt and how many attempts reached it, per AGENTS).
   Measure per piece: seated or not, join residual (mm), pairwise LCS inlier counts,
   and against GT if it exists (5°/10 mm strict bar). Render every result for the
   conservator's eye check.
3. **Density analysis + the interpolation control.**
   a. Per piece: d needed for 50 dots at its loop length (J9: ~0.83 mm ≈ 2.3× paper
      density); state honestly that finer resampling of the SAME traced lane interpolates
      — it adds count, not boundary information; the walk's dot count is bounded by
      loop length / d. Check whether the paper's 1.9 mm was tied to pot scale.
   b. Control arm: resample the t55 Bl0 lanes at the d that gives each piece ≥50 dots
      (pure interpolation, no rerun of steps 3–4) and assembly-run them at the STANDARD
      floor 50. If interpolated-50 seats where real-23 did not, the floor is about count;
      if neither seats, the binding constraint is elsewhere (matcher/geometry) and both
      cure options miss it. This control decides between the conservator's two options.
4. **Write `## Results`** in this ticket: gate-trace table (constant → consumed where →
   effect), experiment table (arm × piece × seated/residual/inliers), density table
   (piece, loop mm, dots at 1.9, d for 50), and the options with what each costs —
   the conservator decides, the worker does not recommend.

### Acceptance

- Every claim carries file:line or a measured number from a named run dir.
- Experimental binaries: md5 recorded, diff attached to the ticket, never merged, built
  only inside the run area; the canonical assembler and preprocessor sources are untouched.
- Renders (workspace-relative links under `SfSpp_preprocessing/artifacts/`) for every
  seating claim; best-of-N stated with attempt counts.
- Every sbatch polled (`scripts/slurm_poll.sh`) and final sacct State/ExitCode recorded.
- Budget: ≤3 Slurm jobs, ≤24 h wall.
- Worker reports measurements only; the conservator chooses the cure.

**Edges:** shares the t55 run dir with ticket 57 READ-ONLY; Spartan budget is separate.
