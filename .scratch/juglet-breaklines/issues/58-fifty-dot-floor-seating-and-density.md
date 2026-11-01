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

**Status:** resolved — worker measurements verified by the lead (see "### Lead verification (2026-11-02)"); the conservator chooses the cure (Table 4)
**Working in:** the t58 panel run, /data/gpfs/projects/punim2657/SfSpp/runs/20261101-1913_d8f716f_t58-floor-density-panel
**Branch:** 58-fifty-dot-floor-seating-and-density, in /c/PR/worktrees/sfs/58
**Worker:** DSH subagent (ticket-58 worker; parent session-c0abfc6a-6cd6-4e92-b125-08490211931c) — wrote the instruments, ran the 7-arm panel (job 34175117), scored and rendered it, appended ## Results; nothing committed (the lead commits)

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
   the run area with the floor lowered (10) and separately removed (0), and with an
   intermediate floor (45) so the 1-to-3-active-piece regime is also sampled; record both md5s
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

**Acceptance ticked:** gate trace Table 1 (file:line); arm table + per-arm Acc.txt; density Table 3 + the I60 interpolation control; renders F10 / I60 / PA10; jobs 34175087 FAILED 1:0 and 34175117 COMPLETED 0:0 with sacct; budget 2 of 3 jobs, 4m39s of 24 h. Binaries md5-recorded under work/shim/, never merged. Pot A control reproduces 8/8 and 15/15.

**Edges:** shares the t55 run dir with ticket 57 READ-ONLY; Spartan budget is separate.

## Results

Worker measurements only; no recommendation (the conservator chooses the cure).

**Run of record:** `/data/gpfs/projects/punim2657/SfSpp/runs/20261101-1913_d8f716f_t58-floor-density-panel`
(`run.json`, `submit.sbatch`, `logs/`, `score/`, `out/`, `trees/stage_manifest.txt`, `work/shim/*.cpp`).
Harvested copy: `SfSpp_preprocessing/artifacts/t58/run_t58/`.

**Slurm (acceptance: sbatch polled + final sacct State/ExitCode)**
| jobid | state | exit | elapsed | MaxRSS | note |
|---|---|---|---|---|---|
| 34175087 | FAILED | 1:0 | 00:00:06 | 33804K | attempt 1: two bugs in my own sbatch (unquoted `Ground Truth` path; `arm.sh` never copied into the /panel bind). Kept as `submit.attempt1.sbatch`. |
| 34175117 | COMPLETED | 0:0 | 00:04:33 | 6737324K | attempt 2, the 7-arm panel below |

Both polled with `scripts/slurm_poll.sh` and re-read with `sacct -j 34175087,34175117 -P -o JobID,JobName,State,ExitCode,Elapsed,MaxRSS`.
Budget used: 2 of 3 jobs, 4m39s of 24h wall.

**Best-of-N.** The assembly path carries no RNG, so each arm is N=1; the repeat arm proves it. Arm F10R is a second run of F10 in the same job:
identical result inventory and byte-identical files (`Edgeline_2 c9a7acd238d2444d8773d5f583b50db6`, `OBJ_2 51954ccb39566b87b5525e7f854d4b65`, `Edgeline_4 52f186ba6722f42647f936ec92e64c47`, `OBJ_4 a54fb478d47bb9b854a97ca25f64f918`, `T_1to_1 cf1318e7c000a038a061ece9df894523`, `T_3to_3 3e423308328628b6d995f26c5ade5308`; `logs/determinism.log` prints `SNAPSHOT CONTENT IDENTICAL`).
Headline numbers below are therefore single-attempt, not best-of-many.

**Experimental binaries (never merged; built only inside the run area).** Each variant is the shipped shim `hpc/tools/main_pristine_batch.cpp` with the single literal at line 86 rewritten by `sed`; `work/shim/diff_*.txt` holds the one-line diff for each.

| variant | floor | md5 | diff |
|---|---|---|---|
| F50 | 50 | `fb26e8ab49e9c00f7e8d02de44f6eea5` | empty (byte-identical to the shipped shim) |
| I60 | 50 | `fb26e8ab49e9c00f7e8d02de44f6eea5` | empty |
| F45 | 45 | `5e0ac02edb559a187a9148921c5d1b17` | `-point_.cols() < 50` / `+point_.cols() < 45` |
| F10 / F10R | 10 | `eba77838faaf969a1987daf67dbbd8b3` | `-... < 50` / `+... < 10` |
| F0 | 0 | `1bf9cb2fdfc48f76e2a2599c92449dd5` | `-... < 50` / `+... < 0` |
| PA10 | 10 | `eba77838faaf969a1987daf67dbbd8b3` | same as F10 |

The canonical assembler and preprocessor sources are untouched; the variants exist only under `$RUN/work/shim/`. The staged inputs are copies (Juglet lanes from the t55 run READ-ONLY; Pot A hardlinks) — nothing was written into the t55 run dir.

### Table 1 — Gate trace (constant → consumed where → effect)

| constant | defined / tested at | consumed at | effect |
|---|---|---|---|
| `50` | `structure-from-sherds-pp/hpc/tools/main_pristine_batch.cpp:86` (`if (shard[i].edge_line_.point_.cols() < 50)`); mirrors `main.cpp:86` and `.scratch/pristine-pot-a-control/upstream_main_9195c01.cpp:86` | `:84` guard → skips `CalculateLineNormal`, `LoadSurface(surface_in,surface_out,surface_fr)` and `is_matching_=true` at `:91-95`; `:149` zeroes the piece's GT row **and** column; `:162` skips `MakePointCloud`/`MakeMesh`; `:176` skips the axis-to-z block; `:238`/`:245` set `right_sherd` | the piece is never matched, never in the GT reference, and gets no saved `T`. `shard[i].edge_line_.Remove()` (`class/data_structure.cpp:451-465`) leaves a 1-dot placeholder and clears the axis vectors. **Measured consequence:** in arm F50 the printed GT matrix is all zeros, so `CountResult` (`class/data_structure.cpp:970-1040`) runs with denominator 0. |
| `MINIMUM_NUMBER 6` | `structure-from-sherds-pp/class/reconstruction.h:24` | called as the LCS window at `hpc/tools/main_pristine_batch.cpp:209` `FeatureComp(shard, LCS_out, 25, MINIMUM_NUMBER, 0)`; acceptance at `class/feature_matching.cpp:294` `if (LCSuff(i, j) > windowsize)`. Also `reconstruction.cpp:727`/`:763` (`inlier < MINIMUM_NUMBER → return false`), `:465`/`:530`/`:593`/`:666` and `feature_matching.cpp:1015`/`:1045` (`> MINIMUM_NUMBER/2` = >3), `:1198`/`:1397`/`:1589`, `ranking_system.cpp:795`/`:833` | with 6 as the LCS window the shortest admissible matched run is **7 dots**. Every t55 lane carries 23–54 dots, and all 18 GT-adjacent pairs have `min(dots_i, dots_j) ≥ 23`, so this floor is **not** binding on the Juglet. It is the number that matters for a genuinely tiny lane, not for these. |
| `10` | `structure-from-sherds-pp/class/reconstruction.cpp:72` `if (numberOfPoints < 10) return;` inside `AxisAlignment` | returns **without setting** `R_out`/`t_out`; callers `ranking_system.cpp:781` and `:1735`; the shim calls it at `:182` | a second, undocumented lane floor. No t55 lane is under 10 dots, so it did not fire here; it is a separate hidden gate, not part of the 50. |
| `NUM_MIXED_SHERD 1` | per-dataset block of `class/data_path.h` | only the GT-load loop in the batch main (`shim:127`) — the number of GT graph files to concatenate | no algorithmic effect; it is 1 for the Juglet (`Juglet_simple_graph.txt`). |
| paper `50` | `papers/text/sfspp-2502.13986v1.md:329` verbatim: "In the dataset preparation process, we exclude very small fragments comprising fewer than 50 points in the respective surface edge lines (with a perimeter of approximately 9cm) and special parts such as the handle, nose, or ornament. This results in removing 1 piece from pot C, 2 pieces from pot D, 4 pieces from pot E, 2 pieces from pot F, 3 pieces from pot I, and **8 pieces from pot J**." | — | the paper states the 50 as a **corpus-exclusion rule**, and for pot J it removes 8 of 9 pieces — the same 8-of-9 the assembler's load-time gate removes from our corpus. The paper gives no algorithm for the assembler's own floor, and no 50 appears in `SfSpp_preprocessing/edgeline_extraction_headless.cpp`; the only other 50 in the twin `original_nurbs_preprocessing/edgeline_extraction_headless.cpp:584` selects a smoothing radius, not a piece filter. |

**Does assembly run with 2–3 active pieces?** Not on this corpus. The shipped floor 50 leaves one active piece (J7, 54 dots); floor 45 leaves three (J5 47, J6 46, J7 54). Both arms produced **zero** candidate LCS pairs and then **segfaulted** at `structure-from-sherds-pp/class/ranking_system.cpp:727` `num_init_prio_ = ext_state_[0].total_priority_.size();` — reached from `StateManager::Initialize` (`:665-728`), where `ext_state_` is only appended at `:720` when `isroot && !root_state.graph_.empty()`, so an empty candidate list leaves it empty and `[0]` is out of range. Piece count and candidate count are confounded in both arms (both had 0 candidates), so this run cannot separate them; it can only say that with 1 or 3 active pieces and no candidate pairs the batch exits 139 (SIGSEGV) before scoring. This is the same family as the incident already recorded at `class/data_path.h:45`.

### Table 2 — Experiment (arm × piece × seated / residual / inliers)

Staging: `Breaklines/` = the t55 run-of-record Bl0 lanes verbatim; `Surfaces/` = the same run's S0/S1 converted from ASCII PLY to bare 6-number `.xyz` (the reader `class/data_structure.cpp:781-843` cannot parse a PLY header); `Mesh`, `Axes`, `Ground Truth` from `Dataset/{Mesh/Juglet, Axes/Juglet, Juglet_GT}`. `trees/stage_manifest.txt` records every lane md5 and every surface vertex count. Pot A binds its own bundle; it was hardlinked into `trees/pota/` so the shared 4.7G bundle is never written.

Arm-level:

| arm | floor | tree | active pieces | LCS candidates / pruned | graph | saved `T` files | binary's own Acc.txt | exit | wall s |
|---|---|---|---|---|---|---|---|---|---|
| F50 | 50 | t55 lanes | {7} | 0 / 0 | never builds | none | — (crash) | **139** | 42 |
| F45 | 45 | t55 lanes | {5,6,7} | 0 / 0 | never builds | none | — (crash) | **139** | 11 |
| F10 | 10 | t55 lanes | all 9 | 21 / 1 | 1 merge `2 to 1`, then "Priority list empty" | 2 (pieces 2, 4) | `2 / 9`, `0 / 18` | 0 | 13 |
| F0 | 0 | t55 lanes | all 9 | 21 / 1 | identical to F10 | 2 (2, 4) | same as F10 | 0 | 13 |
| F10R | 10 | t55 lanes | all 9 | 21 / 1 | identical to F10 | 2 (2, 4) | same as F10 | 0 | 13 |
| I60 | 50 | lanes resampled to 60 dots | all 9 | **63 / 12** | 5 states over 4 steps | 7 (2,3,4,5,6,8,9) | `0 / 9`, `0 / 18` | 0 | 28 |
| PA10 | 10 | Pot A (unchanged lanes) | all 8 | 124 / 70 | "All shards are matched" | 8 | `8 / 8`, `15 / 15` | 0 | 142 |

Per piece against the full 9-piece GT (scorer `score58.py`, validated offline against the 2026-10 prior run's `2/9`+`0/18` before submission). "seated" = own place, chamfer below 7.07 % of the 65 mm Juglet = **4.596 mm**.

| arm | piece | dots | saved `T`? | raw rot ° | raw trans mm | chamfer mm | seated | strict 5°/10 mm edge |
|---|---|---|---|---|---|---|---|---|
| F10 / F0 / F10R | 2 | 32 | yes | 107.39 | 778.60 | 27.543 | no | — (no GT edge to its only partner) |
| F10 / F0 / F10R | 4 | 32 | yes | 141.61 | 1020.55 | 13.278 | no | — |
| I60 | 2 | 60 | yes | 66.83 | 397.73 | 468.480 | no | 4 directed edges, all fail |
| I60 | 3 | 60 | yes | 144.31 | 375.00 | 466.730 | no | 2, all fail |
| I60 | 4 | 60 | yes | 143.28 | 806.75 | 474.073 | no | 4, all fail |
| I60 | 5 | 60 | yes | 164.55 | 923.58 | 475.185 | no | 6, all fail |
| I60 | 6 | 60 | yes | 166.89 | 463.10 | 462.050 | no | 4, all fail |
| I60 | 8 | 60 | yes | 149.47 | 776.02 | 458.631 | no | 4, all fail |
| I60 | 9 | 60 | yes | 140.33 | 248.81 | 465.899 | no | 4, all fail |
| PA10 (control) | 1–8 | 60–218 | yes, all 8 | — | — | 0.961–2.364 | **all 8** | 30/30 directed, all pass |

**Inliers.** The binary never prints a per-pair inlier count, and `LCSIndex::inliner_` is set downstream (`class/reconstruction.cpp:1491`, `:1700`) and consumed only by the ranking path (`ranking_system.cpp:1079`, `:1100-1101`); no run artefact carries it. The honest surrogate available from the saved geometry is the per-pair **join residual** (median nearest-neighbour distance between the two posed lanes) and the count of lane points in contact:

| arm | GT-adjacent undirected pair | join residual mm | contact points < 2 mm | relative rot ° | relative trans mm | passes |
|---|---|---|---|---|---|---|
| I60 | (2,9) | 5.88 / 4.84 rev | 16 / 21 | 159.66 | 1026.94 | no |
| I60 | (3,5) | 6.52 / 10.59 rev | 20 / 18 | 138.57 | 949.87 | no |
| I60 | (6,8) | 10.97 / 8.25 rev | 14 / 15 | 163.09 | 975.86 | no |
| I60 | (2,5) | 22.65 / 29.61 | 0 | 165.61 | 896.80 | no |
| I60 | (5,9) | 39.09 / 31.35 | 0 | 63.30 | 325.42 | no |
| PA10 | the 15 GT edges | 0.14–0.81 (all) | — | <1 | <1 | **all 15** |

So in I60 three GT-adjacent pairs have their lanes physically nearly touching (5.9–11.0 mm, 14–21 contact points) while the two pieces face **138–163° away from the correct relative orientation**. That is a matching result, not a seating result: the pieces come close but in the wrong attitude.

**One arm's own number could not be reproduced from its artefacts (recorded, not hidden).** F10/F0/F10R report `Sherd accuracy : 2 / 9`. But the `g` block of `hpc/tools/main_pristine_batch.cpp:318-337` saves a `T` file only for a piece that appears in a graph node, and F10's graph is a single merge of pieces 2 and 4 — yet `Juglet_simple_graph.txt` has `GT(2,4) = 0`. So (a) the one join the matcher made is not a GT pair at all, and (b) the binary's `2/9` rests on internal transforms for pieces that were never seated in the graph and have no saved transform; it cannot be independently reproduced from the run's files. The prior 2026-10 run's `2/9` is the same class of number (its single passing directed pair was GT edge (1,6)), and there the saved files did cover all nine pieces — which is why my scorer reproduces that run exactly and cannot reproduce this one.

### Table 3 — Density (closed-polyline convention, from `trees/stage_manifest.txt`)

| piece | dots (t55) | loop (closed) mm | d now = loop/dots mm | d needed for 50 dots mm | dots if d = 1.9 mm | 50 dots reachable at paper d? |
|---|---|---|---|---|---|---|
| J1 | 28 | 53.798 | 1.9214 | 1.0760 | 28 | no |
| J2 | 32 | 60.602 | 1.8938 | 1.2120 | 32 | no |
| J3 | 38 | 71.644 | 1.8854 | 1.4329 | 38 | no |
| J4 | 32 | 60.148 | 1.8796 | 1.2030 | 32 | no |
| J5 | 47 | 86.581 | 1.8421 | 1.7316 | 46 | no |
| J6 | 46 | 85.253 | 1.8533 | 1.7051 | 45 | no |
| J7 | 54 | 100.085 | 1.8534 | 2.0017 | 53 | yes (d 2.00 > 1.9) |
| J8 | 41 | 74.816 | 1.8248 | 1.4963 | 39 | no |
| J9 | 23 | 43.469 | 1.8900 | 0.8694 | 23 | no |

The t55 lanes already sit at 1.82–1.92 mm, i.e. **at or finer than the paper's d = 1.9 mm** (`SfSpp_preprocessing/edgeline_extraction_headless.cpp:556`, "paper constant"). So for 8 of 9 pieces the short dot count is not under-sampling — it is loop length: a 43 mm break cannot hold 50 dots at 1.9 mm. Reaching 50 dots on J9 needs d = 0.87 mm, **2.2× finer than the paper value**; that is resampling of the *same traced line*, so it adds point count and no new boundary information (the trace is bounded by the walk's resolution, and the emitted loop is not closed — the last sample falls one spacing short of the first, matching `edgeline_extraction_headless.cpp:797-810`).

### Table 4 — The two cure options, as measured

(the conservator decides; no recommendation given)

| option | what was run | measured outcome | what it costs |
|---|---|---|---|
| **A. lower or remove the floor** | floor 10 (F10), floor 0 (F0), floor 45 (F45), floor 50 (F50) | floor 10: all 9 pieces active, 21 candidates, the graph never grows past one merge, 2 pieces saved, **0 seated**, the one join made is (2,4) which is not a GT edge. floor 0: byte-identical to floor 10 (smallest lane 23 dots). floor 45 (3 active): 0 candidates → **SIGSEGV 139**. floor 50 (1 active): all-zero GT, 0 candidates → **SIGSEGV 139** | one-line edit, no new data. But on this corpus it produces no correct pose, and at 1–3 active pieces the batch crashes before scoring. It does not by itself make the Juglet assemble. |
| **B. raise the density** | I60: the same t55 lanes resampled to 60 dots each, run at the **shipped** floor 50 | all 9 active, **63 candidates** (3× F10), 12 pruned, graph grows to 5 states over 4 steps, **7 pieces saved** — visibly more matcher activity and more pieces in the graph than F10 — yet **0 seated** (chamfers 458–475 mm, ~half a metre from home) and **0 of the 16 testable GT edges** pass; the binary's own edge number falls from F10's 1/36 to 0/36 | resampling only, no re-extraction of the boundary. It raises count and candidate volume but, in this arm, does not convert into correct relative poses. |
| **C. leave it** | F50 = the shipped configuration on this corpus | 1 of 9 pieces survives the gate, the GT denominator becomes 0, 0 candidates, **exit 139 SIGSEGV** at `ranking_system.cpp:727` | nothing to build; the shipped configuration does not produce an assembly of this corpus today. |

**The control that keeps these readable.** PA10 (floor-10 binary, Pot A, unchanged lanes) reproduces the positive control exactly: `8 / 8 (100 %)` and `15 / 15 (100 %)` in its own `Acc.txt`, 30/30 directed pairs in my replay, all 8 pieces own-place with chamfers 0.96–2.36 mm against a 13.72 mm bar (7.07 % of Pot A's 194.1 mm reference extent). The floor edit therefore does not disturb a case that works — the Juglet outcome above is not an artefact of the experimental binary.

### Renders (workspace-relative, for the eye check)

| arm | picture | pairs with |
|---|---|---|
| F10 (= F0, F10R) | [F10_assembly.png](SfSpp_preprocessing/artifacts/t58/run_t58/render/F10_assembly.png), [F10_perpiece.png](SfSpp_preprocessing/artifacts/t58/run_t58/render/F10_perpiece.png) | spread: estimate bbox diagonal 41.2 mm vs reference 52.2 mm; largest piece-centroid separation 12.4 mm (est) vs 27.5 mm (ref); centroid offset 17.3 mm |
| I60 | [I60_assembly.png](SfSpp_preprocessing/artifacts/t58/run_t58/render/I60_assembly.png), [I60_perpiece.png](SfSpp_preprocessing/artifacts/t58/run_t58/render/I60_perpiece.png) | estimate bbox 77.1 mm vs reference 68.0 mm; separation 39.4 vs 29.8 mm; **centroid offset 476.0 mm** |
| PA10 (control) | [PA10_assembly.png](SfSpp_preprocessing/artifacts/t58/run_t58/render/PA10_assembly.png), [PA10_perpiece.png](SfSpp_preprocessing/artifacts/t58/run_t58/render/PA10_perpiece.png) | estimate bbox 276.1 mm vs reference 279.7 mm; separation 154.4 vs 157.2 mm; centroid offset 12.0 mm |

F50 and F45 have no `T` files, so there is nothing to pose; their result dirs are empty. The saved `OBJ_<i>.obj` files are **not** posed (their vertices equal the source mesh), so every render poses the original mesh from the saved `T`; `render58.py` does that. What the pictures show: in F10 the two saved pieces form one compact overlapping cluster where the reference separates them into two clouds; in I60 the seven pieces are compact among themselves but sit ~330–350 mm higher than the reference; PA10's two panels match.

### Instrument caveats (measured, reported)

- `score58.py` hard-codes the 36-directed / 18-undirected denominator in its `countresult` block. The correct per-arm denominators, recomputed from the GT graph restricted to each arm's active set, are: F50 **0**, F45 **2**, F10/F0/F10R/I60 **36** (18 undirected). The F50/F45 denominators are wrong in the scorer's JSON as published.
- The gauge used for the per-piece rotation/translation figures is one global rigid fit over the **translation triplets** of the active pieces. It needs ≥3 active pieces and falls back to identity otherwise (F10 and F0 hit that fallback, so their raw and gauge numbers are identical). It can absorb a translation error into an apparent rotation error — visible in I60, where the corrected figure is worse than the raw one.
- Cubes/bboxes above are the same numbers `spread58.py` writes to `artifacts/t58/run_t58/spread.json`; `density_table.json` holds Table 3.

**Sources of the staged inputs** (all read-only for the t55 run): Bl0 lanes `…/runs/20261101-2004_05be12c_t55-worness07-breaklines/out/geom/Juglet_Piece_N.Bl0` (md5s in `stage_manifest.txt`, e.g. J1 `9aacd9f30ed795508b1e37ef686fae6c`); meshes `Dataset/Mesh/Juglet/Juglet_Piece_N_Mesh.obj`; axes `Dataset/Axes/Juglet/`; GT `Dataset/Juglet_GT/`; Pot A `sfs_main/original_samples/SfS_pp/`.


### Lead verification (2026-11-02)

Re-read at the line each claim rests on, and recomputed what can be recomputed.

**verified: papers/text/sfspp-2502.13986v1.md:329 ->** verbatim "we exclude very small fragments comprising fewer than 50 points in the respective surface edge lines (with a perimeter of approximately 9cm) ... This results in removing 1 piece from pot C, 2 pieces from pot D, 4 pieces from pot E, 2 pieces from pot F, 3 pieces from pot I, and 8 pieces from pot J." The 50 is the paper's corpus-exclusion rule and costs pot J exactly 8 of its 9 pieces, as recorded.

**verified: structure-from-sherds-pp/hpc/tools/main_pristine_batch.cpp:86 ->** `if (shard[i].edge_line_.point_.cols() < 50) { shard_on_off[i] = false; shard[i].edge_line_.Remove(); continue; }`; the same literal at structure-from-sherds-pp/main.cpp:86. Only these two files match `point_.cols() < 50`.

**verified: structure-from-sherds-pp/class/ranking_system.cpp:720/:727 ->** `ext_state_.emplace_back(root_state);` sits inside `if (isroot && !root_state.graph_.empty())` (:720), and :727 is `num_init_prio_ = ext_state_[0].total_priority_.size();` — an empty candidate list leaves `ext_state_` empty, so `[0]` is out of range. Logs confirm both crashing arms reached "----- Make root graph -----" with "Total number : 0".

**verified: structure-from-sherds-pp/class/reconstruction.cpp:72 ->** `if (numberOfPoints < 10) return;` inside `AxisAlignment`, returning before `R_out`/`t_out` are set — the second, undocumented lane floor. **verified: class/reconstruction.h:24 ->** `#define MINIMUM_NUMBER 6` beside `INLIER_THRESHOLD 1.5` / `ANGLE_THRESHOLD 0.262`.

**verified: per-arm `1. Acc.txt` ->** F10 / F0 / F10R `Sherd accuracy : 2 / 9 (22.2222 %)` and `0 / 18 (0 %)`; I60 `0 / 9` and `0 / 18`; PA10 `8 / 8 (100 %)` and `15 / 15 (100 %)`. **verified: logs/binary_*.log ->** candidate totals F10 21 / pruned 1, I60 63 / pruned 12, PA10 124 / pruned 70; F50 and F45 both print "Total number : 0" and "Total number pruned : 0" before the crash.

**verified: run determinism ->** F10, F0 and F10R emit byte-identical geometry and transforms — `Edgeline_2 c9a7acd238d2444d8773d5f583b50db6`, `Edgeline_4 52f186ba6722f42647f936ec92e64c47`, `T_1to_1 cf1318e7c000a038a061ece9df894523`, `T_3to_3 3e423308328628b6d995f26c5ade5308`, and `logs/determinism.log` prints `SNAPSHOT CONTENT IDENTICAL`. (Their `1. Acc.txt` files differ only in the embedded `Time :` line.)

**verified: Grid/GT ->** the Juglet ground-truth graph `Dataset/Juglet_GT/Juglet_simple_graph.txt` (md5 `ccae01dd9c897e92beb0d507baa45cea`) is 36 directed / 18 undirected, and `GT(2,4) = 0` — so the single join F10 makes is not a ground-truth edge. Restricted to each arm's active set the correct denominators are F50 **0**, F45 **2** (edge (6,7)), F10/F0/F10R/I60 **36**; the scorer's JSON prints 36 for every arm, so its F50/F45 denominators are wrong as flagged.

**verified: renders ->** F10_assembly.png shows the two saved pieces (2, 4) posed as one compact overlapping cluster against a reference that separates them; PA10_assembly.png shows the two panels matching. Pictures agree with the numbers.

**Corpus fact confirmed, and it is the reason for the staging route.** `Dataset/Breaklines/` on Spartan holds only `Pot_A` and `Pot_A_backup_5x` — the Juglet breaklines no longer exist as files anywhere under `Dataset/`. Ticket 58 therefore staged the t55 run-of-record Bl0 lanes READ-ONLY, which is the only surviving copy. The dataset the ticket's Given block named (`JUGLET_BASE`) is not present; `Dataset/Juglet_GT/`, `Dataset/Axes/Juglet/` and `Dataset/Mesh/Juglet/` are.

**Lead-verified headline.** The floor is the paper's own corpus-exclusion rule, not an algorithmic threshold; lowering or removing it seats nothing (the one join made is not a GT edge); resampling the same lanes to 60 dots triples the matcher's candidates and grows the graph but seats nothing either (0 of 16 testable GT edges, chamfers ~0.46 m); and at 1–3 active pieces with no candidates the shipped batch segfaults before scoring. Pot A's positive control reproduces 8/8 and 15/15 exactly, so the experimental binary does not disturb a working case. All of the worker's flagged anomalies are recorded above and stand: F10's own 2/9 is not reproducible from its artefacts, per-pair LCS inliers are unavailable, and the gauge can absorb translation into apparent rotation.
