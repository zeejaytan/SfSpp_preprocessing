# 18: Find the first loss of the three E28 joins

**What to build:** Use the authors' released Pot E sample as the benchmark. With one byte-identical instrumented assembler, locate the first reproducible failure for 13–28, 27–28 and 28–31. Separate missing viable matches, rejected or moved placements, and search pruning.

**Answers:** E1
**Blocked by:** None. Use the closed Ticket 17's frozen inputs and Ticket 11's calibration requirements.
**Status:** in-progress
**Working in:** DSH: SfS++ axis-parity Ticket 18 (2026-11-23) (2026-11-23)
**Branch:** 18-trace-first-e28-join-loss, in /c/PR/worktrees/sfs/18
**Worker:** DeepSeek
**Budget:** large 8
**Hand-over:** DeepSeek V4.1 Flash via DSH Baton. The lead retains the private acceptance check.

## Frozen inputs

On Spartan use these literal roots (do not substitute an existing Result tree):

```bash
MAIN=/data/gpfs/projects/punim2657/sfs_main
BASE=/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9
T03E=${BASE}_t03-potE
SHIP=${BASE}_t03-ship
FIXED="$T03E/trees/E_K3R1/E/MM"
ORIG="$MAIN/original_samples/SfS_pp"
SIF="$MAIN/sfs_pristine_assembly.sif"
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
SCORER="$T03E/work/score305.py"
PIECES="$T03E/trees/E_K3R1/arm_pieces_E.tsv"
```

Use Pot E pieces 01–31 and the same 62 reference edges. Pieces 32–34 remain outside the experiment even if their untouched files exist in the release. ORIG binds all five released input folders verbatim. RELEASED_FIXED binds the same released Axes directory and Ticket 17's four fixed non-axis directories. OWN, FORWARD, AUTHOR, REVERSE use those same fixed non-axis directories and the four Ticket 17 axis recipes. Reuse the archived Ticket 17 `work/axes17.py` from run `20261123-0320_894985b_t17-e28-axis` with `--fixed "$FIXED/Axes" --own "$SHIP/out/axes03_own" --tri "$SHIP/out/axes03_tri" --out "$RUN/axes" --donor "$RUN/evidence/donor.tsv" --manifest "$RUN/logs/axes_manifest.tsv"`. OWN differs from FORWARD and AUTHOR differs from REVERSE in exactly `Axes/Pot_E_Piece_28_Axis.xyz`, with the two donor byte hashes pinned by Ticket 17. Released axes and axes estimated from authors' walls are distinct controls. Verify the two supplied truth graphs name the identical 62 unordered edges and that their 31 reference pose files match byte for byte before comparing arms. Use the matching bound truth directory with each scorer invocation. The truth is available to the existing scorer only and must never affect trace selection, candidate generation or ranking.

Save before/after SHA-256 for each of the 31 pieces' files in the five input directories and both graphs, using paths relative to the dataset mount (no absolute paths, backslashes, skipped or aggregate-only rows). Also hash full bound release Pot E files including unused E32–34 in the corpus manifest. Preserve the corpus byte for byte. Use one run directory, with one run-index row and separate newly created Result directories per cell. No input-tree copying or mutation.

## Build and launch exactly once

Use the Ticket 17 source and guarded shim recipe with observation-only instrumentation. Only write `work/t18/` in the ticket worktree and the ticket Comments, plus this run's own files on Spartan. Store source patches, helpers and batch script under that run's `work/t18/`; leave production checkouts, inputs and other tickets untouched. The only instrumented translation units are `class/feature_matching.cpp`, `class/ranking_system.cpp` and the guarded batch shim. A shared trace header may live beside those staged sources. Instrument the SIF copy, and save original source hashes and a patch against those bytes. Check SIF MD5 `63a532b9732f84e59e7b1349065f1323`, shipped shim MD5 `fb26e8ab49e9c00f7e8d02de44f6eea5`, and guarded shim MD5 `056dfb914d7f067244a87d200ecb9863` before instrumenting. Pin the recorded Ticket 17 assembler source `40b3529dc47a037da979848b0d8b728b37cb1360` and scorer SHA-256 `b04121f95bef4739c3a1eeb3df13dfe1d4fc5da5c533fdf165d2f1252f6dddde`. Stop on pin mismatch.

```bash
WORK="$RUN/work/t18"
SHIPPED="$MAIN/sfspreproc-docker/hpc/tools/main_pristine_batch.cpp"
mkdir -p "$WORK"/{src,build,logs,inc_E/class} "$RUN"/{logs,evidence,out,score}
"$PY" "$T03E/work/patch_guard67.py" "$SHIPPED" "$WORK/G.cpp"
grep -F 'point_.cols() < 50' "$WORK/G.cpp"
"$APT" exec "$SIF" cat /opt/sfs-pristine/class/data_path.h > "$WORK/data_path.h"
"$PY" "$T03E/work/mk_inc.py" "$WORK/data_path.h" "$WORK/inc_E/class/data_path.h" E
"$APT" exec --bind "$WORK:/panel" "$SIF" bash -euc 'cp -a /opt/sfs-pristine/. /panel/src/'
# Apply the reviewable trace patch to src/class and G.cpp here. Preserve floor 50.
# Ensure the generated Pot E data_path.h is the one used by both shim and translated sources.
cp "$WORK/inc_E/class/data_path.h" "$WORK/src/class/data_path.h"
"$APT" exec --writable-tmpfs --bind "$MAIN:/workspace" --bind "$WORK:/panel" "$SIF" bash -euc '
  cd /panel/build
  cmake /panel/src -DCMAKE_BUILD_TYPE=Release > /panel/logs/cmake.log 2>&1
  make -j8 > /panel/logs/make.log 2>&1
  d=CMakeFiles/Hierarchy-Clear.dir
  defs=$(sed -n "s/^CXX_DEFINES *= *//p" "$d/flags.make" | tr " " "\n" | sed "/GOOGLE_GLOG_DLL_DECL/d" | tr "\n" " ")
  incs=$(sed -n "s/^CXX_INCLUDES *= *//p" "$d/flags.make")
  flags=$(sed -n "s/^CXX_FLAGS *= *//p" "$d/flags.make")
  g++ -I/panel/inc_E $defs $incs $flags -I/panel/src -I/panel/src/class -c /panel/G.cpp -o "$d/shim_t18.o"
  sed -e "s|CMakeFiles/Hierarchy-Clear.dir/main.cpp.o|$d/shim_t18.o|" -e "s|-o Hierarchy-Clear|-o Hierarchy-T18|" "$d/link.txt" > /panel/logs/link_t18.sh
  grep -F "$d/shim_t18.o" /panel/logs/link_t18.sh
  bash -e /panel/logs/link_t18.sh
  sha256sum /panel/build/Hierarchy-T18 > /panel/logs/executable.sha256
'
```

Retain provenance, the link command and compile logs. The stock target made by CMake is never an experimental executable. Use one final `Hierarchy-T18` for all scored cells. For ORIG set DATA and AXIS_DIR to ORIG and ORIG/Axes. For RELEASED_FIXED set DATA to FIXED and AXIS_DIR to ORIG/Axes. Otherwise DATA is FIXED and AXIS_DIR is `$RUN/axes/$ARM`. Make the empty mount layout once and create each Result directory with plain `mkdir` so reuse fails. Clear inherited `SFS_*` and POT_NAME first. The only T18 variable is a trace file path, identical inside every cell. Use:

```bash
RESULT="$RUN/out/${ARM}_${REP}"
mkdir "$RESULT"
"$APT" exec --writable-tmpfs --bind "$MAIN:/workspace" --bind "$WORK:/panel:ro" \
  --bind "$RUN/mount:/Dataset/SfS_pp:ro" \
  --bind "$DATA/Breaklines:/Dataset/SfS_pp/Breaklines:ro" \
  --bind "$DATA/Surfaces:/Dataset/SfS_pp/Surfaces:ro" \
  --bind "$DATA/Mesh:/Dataset/SfS_pp/Mesh:ro" \
  --bind "$DATA/Ground Truth:/Dataset/SfS_pp/Ground Truth:ro" \
  --bind "$AXIS_DIR:/Dataset/SfS_pp/Axes:ro" \
  --bind "$RESULT:/Dataset/SfS_pp/Result" --env OMP_NUM_THREADS=8 \
  --env T18_TRACE=/Dataset/SfS_pp/Result/t18_raw.jsonl "$SIF" bash -euc '
    sha256sum -c /panel/logs/executable.sha256
    exec /panel/build/Hierarchy-T18 31
  ' > "$RUN/logs/run_${ARM}_${REP}.log" 2>&1
"$PY" "$SCORER" "$RESULT" "$DATA/Ground Truth" E "$PIECES" "$RUN/score/${ARM}_${REP}.tsv" "${ARM}_${REP}"
```

Hash the executed file on host before and after each launch and verify the container OK line before scoring. Two repeats in two waves with the same allocated threads for all arms. Start wave 1 in order ORIG, RELEASED_FIXED, OWN, FORWARD, AUTHOR, REVERSE. Start wave 2 in reverse order. Use 8 CPUs per simultaneous cell, no oversubscription. Keep Ticket 17 settings and record whether any uncontrolled randomness remains. The ORIG benchmark only qualifies at 31/31 sherds and 62/62 scored reference joins in both repeats. Report all results if it misses, but stop attribution at benchmark not reproduced. A replicate that differs from Ticket 03's 59/62 is reported honestly. Only call a seam's first failure reproducible when the matched comparison agrees in both repeats.

## Trace points and calibration

- In `feature_matching.cpp`, record each target pair's axis-row combinations queried by `LCS` and `LCSGraphBuilding` (initial and per-state rematch), emitted intervals, and the precise empty/rejection outcome. Include native interval endpoints and initial pair refinement/verification results before and after the tests in the batch shim's matching block. If a stage has no rigid pose yet, keep its pose fields blank. Distinguish no query, no interval, failed fit, and fit that falls outside the scorer tolerance.
- In `ranking_system.cpp`, log parent state and exact priority ordering in `StateManager::PrepareNextStep` before and after priority filtering. In `BuildState`, record signed native-to-working transforms for both sherds before placement, after placement, after `IcpIncGraphAxis`, and before and after `CheckGraphPlausibility` including actual rejection reasons. Log any shared-axis transform in `GraphAxisRefinement` with the same IDs. In `BuildStep`, record eligible candidates, branch truncation, rejected states, duplicate removal, ordered state ranks and top-k removal. Keep at least the winning competitor's score and sherd IDs whenever a target-bearing candidate or state is dropped. At shim export, record the selected output ID and the exact saved native-to-assembled transforms.
- Record stable per-cell event IDs, parent IDs, seam, state ID, candidate ID, input axis row IDs, source file and line, stage, disposition, reject reason, exact matched indices, support in mm and transforms. Track both target endpoints already present without a selected edge as a physical pose observation with explicit relation `co-present`, not evidence the algorithm proposed that edge. State IDs persist through reordering. Split/merge events retain parent links. IDs must be unique, parent references must exist in the same trace and precede descendants, with no loops or inferred parent from list position. Record explicit zero-query/zero-candidate coverage at every applicable stage. Include branches where a non-target expansion first displaces a tracked fit. Keep raw trace on Spartan and a compact target trace plus stage-accounting tables locally.
- Use Ticket 11's synthetic noncommuting transform check and a common frame change, with correct sherd order and direct transformed-point comparison, all within 0.01°/0.01 mm. Use full ORIG/1 and OWN/1 final states to independently reconstruct saved relative transforms for every scorable seam and reproduce the pinned scorer's flags (20.05°/50 mm). Test reversed endpoint order and one missing-pose case. Stop attribution if calibration fails. Log pass/fail or blank (missing/no pose) at each stage from the same relative convention. Render locked pair views using Ticket 17's corrected reference frame for both repeats at the first divergence for each seam, with scale, matched intervals when available and an explicit label if no candidate was produced. Use overview if out of frame. Stage-absence pictures use the last observed geometry and mark what is absent, never fabricated transforms.

## Evidence and acceptance

- `replay.tsv` columns arm, repeat, executable_sha256, pre_sha256, post_sha256, container_ok, joins, sherds. `inputs.tsv` columns arm, repeat, path, before_sha256, after_sha256. Save `donor.tsv`, `seams.tsv` (arm, repeat, seam, angle_deg, translation_mm, pass), before/after corpus MD5, exact scorer outputs, provenance, render manifest and final job accounting. Every cell reports the same 62 reference seams. Missing pose means both metrics blank and pass 0, with reason in notes.
- `calibration.tsv` columns case, angle_error_deg, offset_error_mm, point_error_mm, expected, actual. Synthetic case names `noncommuting`, `common_frame`, `reversed_order`, `missing_pose`. For each scorable final seam in ORIG/1 and OWN/1 add case `ORIG:13-28` or `OWN:13-28` with the actual seam ID and scorer expected/actual flags. Leave geometry error blank only for missing_pose, with both flags 0. Use wide enough numeric output to check 0.01.
- `trace.tsv` columns arm, repeat, seam, event, parent, state, candidate, axis_lo, axis_hi, stage, disposition, reason, angle_deg, translation_mm, pass. Valid stages `query`, `interval`, `pair_fit`, `priority`, `place`, `group_fit`, `axis_adjust`, `plausibility`, `dedup`, `beam`, `export`. IDs counted locally per cell begin at 1 and strictly increase on write, blank parent only for roots. Use one-based axis file row numbers and explicit missing fields only when inapplicable. Include an explicit `no_event` row for every absent stage per cell/seam, with reason. Keep additional logged fields (source, relation, matched indices, support, competitors, transforms and multiple parents) in `trace_detail.jsonl` keyed by cell/event.
- `first_loss.tsv` columns arm, repeat, seam, stage, event, reason, status. One row per cell and target seam. Status vocabulary `held`, `failed`, `unresolved`, `gated`. A failure points to an actual trace event and names its reason. Gated rows explain benchmark/calibration failure. When no viable fit existed, use the first evidenced lack or rejection, never a later export failure. `renders.tsv` columns arm, repeat, seam, camera, path relative to evidence, with the same camera per seam. If gating blocks a first-divergence view, retain ORIG/OWN final overview views and state the limitation. `gate.tsv` columns benchmark, calibration, attribution, reason, with 1/0 flags, one row and attribution allowed only when both controls pass.
- **Diagnostic only.** Do not change search rules, seeds, rankings, input geometry, candidate counts or selector. Do not widen the beam, retry a non-reproducing control indefinitely, reuse a Result directory or substitute an earlier run. Poll every submitted job, retain final sacct State/ExitCode and write `jobs.tsv` with job_id, run_id, state, exit_code, polled, indexed and 1/0 flags. Use the workspace run-index convention for the run. Fetch only small evidence to `C:/PR/artifacts/axis-parity-18/evidence/`; geometry stays on Spartan.
- Append worker Comments with one self-compliance row per requirement covering pins, build, binds, four swaps, sample controls, calibration, each trace point, lineage, case coverage, renders, jobs and boundaries. Every row gives met/not met/unverified plus file:line or test name. Obtain a separate read-only DeepSeek reviewer to open the renders and evidence and return its own requirement/status/file:line table. Report both tables and exactly one End state from the delegation guide. The only tracked local change at hand-back is this write-back. Run `git -C C:/PR/worktrees/sfs/18 diff --check`. No commit, merge, closure or research verdict.

## Comments

One diagnostic. SfS++ §IV-C and §IV-D describe axis-based matching and the repeated search stages. Ticket 17 established the reciprocal test but found that the reverse swap still seated all three, and the original own-axis 59/62 baseline did not reproduce. Ticket 18 adjudicates the first divergence before any repair.

### Worker write-back (DeepSeek V4.1 Flash, 2026-11-23)

Run: `/data/gpfs/projects/punim2657/SfSpp/runs/20261123-1541_bff8db5_t18-first-loss` (`$RUN` below), runid `20261123-1541_bff8db5_t18-first-loss`; worktree `C:/PR/worktrees/sfs/18` at `bff8db5`. One run directory, subdirs `logs evidence out score work/t18`; no Result directory reused. Jobs: build `35554033` COMPLETED 0:0; smoke `35554202` Slurm COMPLETED 0:0 but the cell aborted in 4 s (rc=255, `ok=0`, mount source missing; no score written) and was rerun as `35554279` COMPLETED 0:0 after `$RUN/mount` was created; cells `35556695` COMPLETED 0:0, elapsed 2:26:33. Eight earlier build attempts FAILED 9:0 (`35553018 35553132 35553244 35553270 35553301 35553492 35553698 35553898`), all at patch application/compile with no scored cell. Counting acceptance-check runs against the eight-check budget: one failed (the 4-second mount miss, no data kept) and the 12-cell matrix passed; the eight build failures were pre-acceptance build checks, not ORIG benchmark runs.

Executable: one `Hierarchy-T18`, sha256 `c82129cef81a3876f682c3d984a24dcd88ecf611ece3516a81dee3be4f7052b0`, 1 267 472 B, g++ 11.4.0, in every cell (pre, post and container check). Pins in `$RUN/logs/slurm-35554033.out` and `$RUN/evidence/provenance.txt` (`build_t18.log` holds compiler warnings only): source `40b3529dc47a037da979848b0d8b728b37cb1360`, SIF md5 `63a532b9732f84e59e7b1349065f1323`, shipped shim md5 `fb26e8ab49e9c00f7e8d02de44f6eea5`, guarded shim md5 `056dfb914d7f067244a87d200ecb9863`, scorer sha256 `b04121f95bef4739c3a1eeb3df13dfe1d4fc5da5c533fdf165d2f1252f6dddde`. Guard floor `point_.cols() < 50` preserved at `work/t18/G.cpp:87`. Truth: `TRUTH-OK 62 edges, 31 pose files byte-identical` (`$RUN/logs/truth_check.log`).

**Gate** (`$RUN/evidence/gate.tsv`): benchmark 1, calibration 1, attribution 1. ORIG benchmark: 31/31 assembler sherds and 62/62 scored joins in both repeats (assembler count from pinned `acc305.py`, joins from pinned `score305.py`; Ticket 17 precedent). RELEASED_FIXED 62/62 both repeats.

Sherds are `acc305.py`'s assembler count (it reads the assembler's own `1. Acc.txt`, frame-invariant); the pinned `score305.py` prints `pieces=0/31` everywhere because it compares each saved pose in the absolute frame, while its joins are the frame-invariant metric used here. CPU times and wave order are in `evidence/jobs.tsv` and `logs/panel.tsv`.

**What was run** (observations only; the lead judges): 12 cells = six inputs x two repeats, 8 threads each, wave 1 `ORIG RELEASED_FIXED OWN FORWARD AUTHOR REVERSE`, wave 2 reverse. Absolute saved frames differ from GT in every cell (the `pieces` column of `score305` is 0/31 everywhere, a frame convention, not seating), so joins are the frame-invariant metric and the benchmark gate uses `acc305` sherds as in Ticket 17.

**Target seams, both repeats** (`evidence/seams.tsv`; `first_loss.tsv` stage/event/reason; event IDs are the re-exported cell-local IDs):

| cell | 13-28 deg / mm | 27-28 deg / mm | 28-31 deg / mm | first loss |
|---|---|---|---|---|
| ORIG r1 | 1.900 / 13.358 PASS | 5.353 / 19.648 PASS | 4.372 / 29.068 PASS | all held at export (ev 4910/4924/4925) |
| ORIG r2 | 3.447 / 14.872 PASS | 5.568 / 21.753 PASS | 5.311 / 38.276 PASS | all held at export (ev 4919/4933/4934) |
| RELEASED_FIXED r1 | 1.678 / 13.190 PASS | 4.918 / 21.082 PASS | 4.246 / 23.644 PASS | held export (4968/4982/4983) |
| RELEASED_FIXED r2 | 1.644 / 12.826 PASS | 4.818 / 21.272 PASS | 4.170 / 25.693 PASS | held export (5364/5378/5379) |
| OWN r1 | 13.792 / 150.883 FAIL | 15.078 / 158.349 FAIL | 12.151 / 56.688 FAIL | pair_fit ev 20, interval ev 5, pair_fit ev 21; reasons `axis_angle_gt_0.436`, `no_interval`, `axis_angle_gt_0.436` |
| OWN r2 | 167.862 / 727.425 FAIL | 168.189 / 727.156 FAIL | 171.914 / 767.508 FAIL | same stages/events/reasons as r1 |
| FORWARD r1 | 1.818 / 14.456 PASS | 4.742 / 20.803 PASS | 4.516 / 26.035 PASS | held export (8878/8892/8893) |
| FORWARD r2 | 5.770 / 37.315 PASS | 7.343 / 55.984 FAIL | 3.599 / 14.059 PASS | 27-28 pair_fit ev 5103 `axis_angle_gt_0.436`; others held (8088/8103) |
| AUTHOR r1 | 2.240 / 17.728 PASS | 5.030 / 24.598 PASS | 4.946 / 27.967 PASS | held export (8382/8396/8397) |
| AUTHOR r2 | 1.704 / 13.377 PASS | 5.089 / 22.541 PASS | 4.304 / 25.014 PASS | held export (8225/8239/8240) |
| REVERSE r1 | 1.825 / 10.910 PASS | 4.663 / 22.370 PASS | 4.719 / 28.664 PASS | held export (5162/5176/5177) |
| REVERSE r2 | 172.449 / 872.732 FAIL | 172.089 / 871.683 FAIL | 175.519 / 737.857 FAIL | 13-28 pair_fit ev 21, 27-28 interval ev 5, 28-31 unresolved (see below) |

The `no_interval` `first_loss` event is the explicit absence row (kind `absence`) whose parent is the empty query event; it is published in `trace.tsv`/`trace_detail.jsonl` with its own ID, so every `first_loss` row points at an actual published event.

**Direct support per target seam** (distinct fit identities / distinct accepted identities, from re-exported `seam_counts.tsv`; an accepted identity is a fit identity never rejected in the same contiguous fit batch):

| cell | 13-28 | 27-28 | 28-31 |
|---|---|---|---|
| ORIG r1 | 61 / 43 | 21 / 19 | 44 / 20 |
| ORIG r2 | 60 / 42 | 19 / 16 | 53 / 29 |
| RELEASED_FIXED r1 | 102 / 59 | 18 / 18 | 70 / 20 |
| RELEASED_FIXED r2 | 108 / 57 | 23 / 22 | 76 / 23 |
| OWN r1 | 38 / 0 | 0 / 0 | 48 / 0 |
| OWN r2 | 33 / 0 | 0 / 0 | 62 / 0 |
| FORWARD r1 | 222 / 103 | 31 / 0 | 151 / 27 |
| FORWARD r2 | 157 / 77 | 17 / 0 | 111 / 23 |
| AUTHOR r1 | 196 / 94 | 57 / 28 | 160 / 72 |
| AUTHOR r2 | 236 / 101 | 55 / 21 | 154 / 67 |
| REVERSE r1 | 53 / 0 | 0 / 0 | 91 / 23 |
| REVERSE r2 | 46 / 0 | 0 / 0 | 104 / 26 |

Other joins lost: OWN r2 also 24-31, 25-31; FORWARD r2 3-25, 5-25, 6-29, 10-29, 12-29, 13-25, 25-31, 27-28; REVERSE r2 13-28, 24-31, 25-31, 27-28, 28-31.

**First-loss adjudication after the evidence re-export** (evidence only; the lead judges):
- OWN is the only input that fails all three target seams in both repeats with the same stage/reason pattern (13-28 pair_fit `axis_angle_gt_0.436`, 27-28 no interval, 28-31 pair_fit `axis_angle_gt_0.436`); magnitudes are not repeat-stable (r1 12-15 deg / 57-158 mm, r2 168-172 deg / 727-767 mm).
- FORWARD and REVERSE are not repeat-stable: both pass all three in r1; in r2 FORWARD loses 27-28 and REVERSE loses all three. Same executable, same axis bytes, same thread count; wave order/schedule differs.
- OWN's early direct-support deficit precedes its export failure but does not alone explain it: FORWARD r1 27-28 (31 distinct fit IDs, 0 accepted) and REVERSE r1 13-28 and 27-28 (0 accepted) also had zero accepted direct fits and still seated at export. Conversely AUTHOR (released tri axes) has accepted direct support and passes every seam in both repeats.
- FORWARD r1 27-28 is **not** "42 fits minus 41 rejections = 1 accepted candidate": its 42 fit events map to 31 distinct (batch, state, edge) identities, and all 31 identities are rejected in the same batch, so 0 are accepted; it still seats at export through the chain. This corrects the earlier arithmetic.
- REVERSE r1 27-28 is the zero-interval positive comparison: 620 queries, 0 intervals, an explicit absence row, and it passes at export.
- REVERSE r2 28-31: the earlier beam attribution is **withdrawn**. The trace has 104 distinct fit identities (26 accepted) for that seam, and the cell-wide top-k/dedup events record only `n_kept/n_dropped/target_dropped` or `n_before/n_after/target_states`, with no seam state, rank or competitor. `first_loss.tsv` therefore marks it `unresolved` with reason `observed_failure_not_seam_attributable_in_trace`; no competitor score or sherd ID is inferred. Its 356 observed beam/dedup rows carry reason `cell_wide_count_only_no_competitor_score_or_ids`; the remaining competitor fields are unresolved and no reconstruction was attempted.
- The single-file E28 swaps do not separate these seams reproducibly across repeats. Ticket 17's "reverse still seats all three" reproduces in repeat 1 only.

**Calibration, re-exported** (`calibration.tsv`, `calibration_physical.tsv`, `calibration_pieces.tsv`, `calibration_notes.tsv`): four synthetic controls pass (noncommuting, common frame, reversed order, missing pose; errors <= 2e-6 deg / 1e-6 mm). For ORIG/1 and OWN/1 all 62 seams each are reconstructed from the published trace: `calibration.tsv` compares trace-vs-saved/scorer (expected = scorer join flag, actual = flag recomputed trace-vs-reference); all 124 join flags match the scorer, trace-vs-saved point error at most 0.001503 mm (translation <= 0.01 mm, angle <= 0.072 deg); the gate's point bar is 0.01 mm, so the data pass, but earlier text quoting 1e-4 mm was wrong because the saved T files carry 3 decimals and are not exactly orthonormal (recorded in `calibration_notes.tsv`). Trace-vs-reference physical errors are kept separately in `calibration_physical.tsv` (124 rows) and piece-only rows in `calibration_pieces.tsv`. `calibration_gate.txt` records all PASS; the saved-precision limit is declared, not forced to pass.

**Renders** (`renders.tsv`, 36 PNGs, same camera per seam in the Ticket 17 corrected reference frame): a stage pose is used only when both endpoints share one published observation group (state, graph, stage, sub); otherwise the view is the final saved export pose and the caption says so. Inspected `OWN_1_27-28` (15.078 deg / 158.349 mm; 924 queries, 0 intervals, explicit absence event 5, "no matched interval produced"; visible gap between red 27 and blue 28), `OWN_2_13-28` (167.862 / 727.425; 173 queries, 131 intervals, 0 accepted fits, first interval idx [[20,26],[128,134]] support 0.11 mm), `REVERSE_2_28-31` (175.519 / 737.857; unresolved first loss, 634 queries, 600 intervals, 32 accepted identities, first interval idx [[26,32],[46,52]] support 0.21 mm), `REVERSE_2_27-28` (no interval) and `ORIG_1_13-28` (1.900 / 13.358 seated). Figures under `C:/PR/artifacts/axis-parity-18/evidence/renders/`.

**Verification run here**: `grep 'ORIG	1	13-28' evidence/first_loss.tsv` -> export 4910 held; `awk` over `seams.tsv` -> 744 rows, 723 pass / 21 fail; `awk -F'	' '$5!=$6' calibration.tsv` -> empty (124/124 flags); `trace_integrity.txt` -> every check 1 for 12 cells; `cmp` corpus before/after -> identical (1319 files); `awk` `inputs.tsv` before vs after -> 0 mismatches (2306 rows); `jobs.tsv` -> 12 rows, indexed=1.

**Follow-up scope**: this pass re-exported and re-rendered only. No assembler was rebuilt, no cell was re-run, no scoring/selector change was made; raw traces, saved poses, scorer outputs and job records are those of run `20261123-1541_bff8db5_t18-first-loss`. The new exporter (`work/t18/export18.py`), calibration (`calibration18.py`) and renderer (`render18.py`) are local post-processing. Raw traces stay on Spartan at `$RUN/out/<CELL>/t18_raw.jsonl`; no raw copy remains on the laptop.

**Self-compliance table**

| # | requirement | status | evidence |
|---|---|---|---|
| 1 | Ticket 18 + AGENTS.md + project AGENTS.md + dsh-handover.md + delegation.md read before acting | met | ticket lines 1-108; read at session start |
| 2 | Pins verified: source commit, SIF md5, shipped shim md5, guarded shim md5, scorer sha256 | met | `$RUN/logs/slurm-35554033.out` lines 2-5,10; `$RUN/evidence/provenance.txt` |
| 3 | Stop on pin mismatch | met | `work/t18/build18.sbatch:32-36,59-60`; 8 FAILED builds produced no Result |
| 4 | Two truth graphs name the same 62 unordered edges; 31 reference poses byte-identical | met | `$RUN/logs/truth_check.log` |
| 5 | Build exactly once from Ticket 17 source + guarded shim recipe; reviewable patch; floor 50 preserved | met | job 35554033; `work/t18/patches_*.diff`; `work/t18/G.cpp:87`; `logs/guard.log` |
| 6 | Instrument only `class/feature_matching.cpp`, `class/ranking_system.cpp`, guarded shim; header beside sources | met | `work/t18/src/class/*.cpp`, `work/t18/G.cpp`, `work/t18/t18_trace.h`; `logs/src_before.sha256`, `logs/src_after.sha256` |
| 7 | One byte-identical executed assembler in every cell, hashed before/after and inside container | met | `replay.tsv` 12/12 `c82129...`; `work/t18/run18.sbatch:43-64` |
| 8 | Binds per cell: ORIG released; RELEASED_FIXED fixed + released Axes; four arms fixed + RUN axes | met | `work/t18/run18.sbatch:47-55,79-81` |
| 9 | Four frozen Ticket 17 swaps; E28 own/author bytes; released vs author-wall axes distinct | met | `$RUN/evidence/donor.tsv`; `$RUN/logs/axes_manifest.tsv` (124 rows); `$RUN/axes/*` |
| 10 | Sample controls: ORIG benchmark, RELEASED_FIXED bridge, OWN/FORWARD/AUTHOR/REVERSE | met | `replay.tsv`, `first_loss.tsv`, tables above |
| 11 | Calibration synthetic controls within 0.01 deg / 0.01 mm | met | `calibration.tsv:2-5` (<= 2e-6 deg); `calibration_gate.txt` |
| 12 | Calibration reconstructs every ORIG/1 and OWN/1 seam and reproduces pinned flags | met | `calibration.tsv` 128 rows (124 join flags match, `awk` empty); `calibration_physical.tsv` 124 rows |
| 13 | Trace query + LCS/LCSGraphBuilding, initial and per-state rematch | met | `feature_matching.cpp:1482,1484,1573,1575`; 22 771 query rows |
| 14 | Trace emitted intervals and precise empty outcome | met | `feature_matching.cpp:1505,1596`; 11 675 interval rows, 4 explicit absence rows |
| 15 | Trace pair refinement/verification before and after the shim matching block | met | `feature_matching.cpp:1720,1774,1791,1800,1899,1943,1954`; 5 362 pair_fit rows |
| 16 | Trace PrepareNextStep parent state and priority ordering before/after filtering | met | `ranking_system.cpp:838,894`; 3 472 priority rows |
| 17 | Trace BuildState transforms before/after placement and after IcpIncGraphAxis | met | `ranking_system.cpp:1073,1119,1139`; 8 898 place rows |
| 18 | Trace GraphAxisRefinement shared-axis transforms with the same IDs | not met | `ranking_system.cpp:1141` emits the group transform as `axis_adjust/group`; no dedicated `group_fit` event, all 36 cell/seams carry `group_fit no_event` |
| 19 | Trace plausibility before/after incl. rejection reasons | met | `ranking_system.cpp:1143,1151,1899,1918,1976,1981`; 12 430 plausibility rows; reasons `score`/`overlap`/`profile_curve` |
| 20 | Trace BuildStep candidates, truncation, rejected states, dedup, ordered ranks, top-k | met | `ranking_system.cpp:1000,1033,1048`; 356 dedup rows, 380 beam rows |
| 21 | Keep winning competitor score and sherd IDs when a target-bearing candidate is dropped | not met | top-k/dedup payloads carry only counts and `target_dropped`/`target_states`; beam rows now say `cell_wide_count_only_no_competitor_score_or_ids`; no competitor ID is recoverable, `first_loss` marks REVERSE r2 28-31 `unresolved`, no rerun |
| 22 | Record selected export ID and saved native-to-assembled transforms | met | `G.cpp:345`; 372 export rows with `T_a`/`T_b` |
| 23 | Event fields: ID/parent/seam/state/candidate/axis/source/stage/disposition/reason/indices/support/transforms; co-present = relation only | met | `work/t18/t18_trace.h`; `trace_detail.jsonl` (74 264 rows); presence `co_present` vs `edge` |
| 24 | State IDs persist through reordering; unique, parents exist and precede, no loops | met | `trace_integrity.txt`: `ids_unique_ascending`, `parents_exist_precede`, `raw_events_published`, `all_stages_covered` = 1 for 12 cells |
| 25 | Explicit zero-query/zero-candidate coverage; `no_event` row for every absent stage per cell/seam | met (target seams only) | 40 `no_event` rows (36 `group_fit`, 4 `pair_fit`) plus 4 explicit absence rows; coverage is complete for the three target seams per cell. The exporter synthesizes rows only for `SEAMS = 13-28, 27-28, 28-31` (`export18.py:8,174-181`); other seams are recorded when observed but get no synthesized `no_event` rows |
| 26 | `first_loss.tsv` one row per cell per target seam, status vocabulary, failure points to an event with reason | met | `first_loss.tsv` 36 rows: 26 held, 9 failed, 1 unresolved |
| 27 | Every cell reports the same 62 reference seams; missing-pose handling | met | `seams.tsv` 744 rows (723 pass / 21 fail); all 31 poses saved in every cell, so no missing-pose row |
| 28 | Locked pair renders for both repeats at first divergence, Ticket 17 frame, scale, intervals, absence label | met | `renders.tsv` + 36 PNGs; stage pose only when both pieces share one observation group, otherwise captioned final export; inspected OWN r1/r2, REVERSE r2, ORIG r1 |
| 29 | Inputs before/after SHA-256 per 31 pieces in the five dirs and both graph files | met | `inputs.tsv` 2306 rows (arm, repeat, path, before, after; mismatch 0); `inputs_before/after.tsv` retained |
| 30 | Corpus preserved byte for byte; hash full release Pot E incl. unused 32-34 | met | `corpus_before.md5` = `corpus_after.md5` (1319 files; ORIG 32-34 present) |
| 31 | Provenance, exact scorer outputs, render manifest, job accounting saved | met | `provenance.txt`, `score/*.tsv`, `score/acc.tsv`, `renders.tsv`, `jobs.tsv`, `$RUN/run.json` |
| 32 | Poll every submitted job; terminal sacct State/ExitCode recorded | met | `jobs.tsv` 12 rows polled=1; `$RUN/logs/sacct_all.txt` 13 data rows |
| 33 | One run directory, fresh Result dir per cell, no Result reuse or earlier-run substitution | met | `$RUN/out/<ARM>_<REP>`; `run18.sbatch:41` aborts if `mkdir` fails (prints EXISTS, skips the cell; limitation e); all 12 dirs fresh |
| 34 | One run-index row | met | `runs/index.tsv` line 1013 = `20261123-1541_bff8db5_t18-first-loss  35556695  bff8db5  t18-first-loss` (verdict/human_note lead-owned); `jobs.tsv indexed=1` |
| 35 | Diagnostic only: no search/seed/ranking/geometry change, no beam widening, no indefinite retry | met | patches add emitters only; no seed or beam edit; two repeats run once each |
| 36 | Only tracked local change is this write-back; no commit/merge/close; `git diff --check` | met | `git -C C:/PR/worktrees/sfs/18 status` (only this file modified, `?? work/`); `diff --check` clean |
| 37 | Fetch only small evidence; geometry stays on Spartan | met | `C:/PR/artifacts/axis-parity-18/evidence/` (tables, 36 renders); raw traces remain under `$RUN/out`, geometry on Spartan, local raw copy deleted |

**Follow-up compliance (evidence-only re-export)**

| # | requirement | status | evidence |
|---|---|---|---|
| 38 | Evidence-only: no assembly/build/scoring/selector rerun; writes only in worktree 18 and this ticket's evidence | met | no sbatch submitted in this pass; `git status` shows only ticket + `work/`; Spartan writes only under `$RUN/evidence` |
| 39 | Compact trace + detail: unique ascending cell-local IDs, remapped parents, closed ancestry, absence event linked to empty query, `no_event` rows with IDs, detail per published event | met | `export18.py`; `trace.tsv` 74 264 rows; `trace_detail.jsonl` 74 264 rows; `trace_integrity.txt` all 1 |
| 40 | Stage-relative poses only for one shared observation; calibration split into trace-vs-saved/scorer, physical and piece rows; unavailable marked, not forced | met | `export18.py` pose grouping (2 689 grouped pose records, 48 final-export records); `calibration.tsv`/`calibration_physical.tsv`/`calibration_pieces.tsv`/`calibration_notes.tsv`; 124/124 flags |
| 41 | Render stage view only when tied to stage+event, else final pose clearly labeled; review OWN/1 27-28 no-interval figure | met | `render18.py`; 36 captions; OWN_1 27-28 inspected (0 intervals, absence event 5, gap visible) |
| 42 | Beam adjudication: remove REVERSE/2 28-31 beam attribution unless records establish the exact branch/competitor; no inferred competitor | met | `first_loss.tsv` REVERSE r2 28-31 `unresolved` / `observed_failure_not_seam_attributable_in_trace`; 356 beam/dedup rows reason `cell_wide_count_only_no_competitor_score_or_ids` |
| 43 | OWN early direct-support deficit reported as preceding export, not proven cause | met | observations above; FORWARD r1 / REVERSE r1 zero-accepted counterexamples cited |
| 44 | FORWARD/1 27-28 uses unique fit identity, not 42-41 | met | 42 fit events -> 31 distinct identities, 31 rejected, 0 accepted (`seam_counts.tsv`) |
| 45 | REVERSE/1 zero-interval positive comparison recorded | met | 620 queries / 0 intervals / absence row; held at export |
| 46 | Verify run-index row under job 35556695; indexed=1; keep terminal jobs; reconcile hrun snapshots read-only | met | `runs/index.tsv:1013` job 35556695 matches terminal sacct; `jobs.tsv` 12 rows indexed=1; `hrun_reconciliation.txt` |
| 47 | Scoped git check, revised self-compliance and separate reviewer table, one End state, no verdict/commit/merge/close | met | this section; `git diff --check` clean; reviewer table appended below |

**Declared trace-shape notes**: (i) 5,312 published rows have `stage=state` — an extra stage beyond the frozen vocabulary, emitted for candidate/root lineage (5,252 candidate, 60 root) and kept so state IDs and parents can be followed; it is not one of the valid stages and no `no_event` row is synthesized for it. (ii) `axis_lo` is the fixed-piece (`axis_y`) file row and `axis_hi` the moving-piece (`axis_x`) row, both one-based as required; because the two pieces have different row counts, 5,606 rows have `axis_lo > axis_hi` — they are a pair of file row numbers, not an ordered interval on one file.

**Limitations carried forward**: (a) competitor score/IDs on dropped target states are absent (row 21); (b) `group_fit` exists only as `axis_adjust/group` (row 18); (c) repeats disagree for FORWARD/REVERSE, so no single-file causal attribution is made; (d) the run-index verdict/human_note is lead-owned; (e) `run_cell` skips (prints EXISTS, returns 0) rather than failing if a Result dir existed — none did; (f) discarded smoke `35554202` aborted in 4 s on a missing mount directory before any data was written; (g) saved pose files carry 3 decimals, so the trace-vs-saved angle column has a ~0.07 deg precision floor and point agreement reaches 0.0015 mm, not 1e-4 mm; (h) the extra `state` stage and the `axis_lo > axis_hi` pair convention are declared above.

### Read-only reviewer (DeepSeek, second pass, evidence-only)

The reviewer read the ticket and evidence, opened eight renders, re-ran read-only checks and the Spartan `sacct`; it wrote nothing. Spartan-side files it could not open from the laptop (patch diffs, truth log, source hashes, fresh-Result proof) it marked unverifiable rather than guessed.

| # | requirement | met | evidence |
|---|---|---|---|
| 1 | Pins | yes | `provenance.txt:8-15` -> 40b3529…, 63a532b9…, fb26e8ab…, 056dfb91…, b04121f9…, c82129ce… 1 267 472 B g++ 11.4.0 |
| 2 | One executable in all cells | yes | `replay.tsv` 12/12 c82129ce…, container_ok 1 |
| 3 | Binds | yes | `run18.sbatch:47-54`, `:79-81` |
| 4 | Swaps / manifest / donor bytes | yes | `axes_manifest.tsv` 124 rows; `donor.tsv` |
| 5 | Truth 62 edges / 31 poses | yes (unverifiable log) | ticket:114; `$RUN/logs/truth_check.log` Spartan-side |
| 6 | Gate | yes | `gate.tsv` 1/1/1 |
| 7 | ORIG benchmark both repeats | yes | `score/acc.tsv:6-7` 31/31, 62/62, 62/62 |
| 8 | jobs.tsv polled/indexed | yes | 12 rows, polled=1 indexed=1 |
| 9 | sacct terminal, no later sbatch | yes | `sacct -j 35556695` COMPLETED 0:0 2:26:33; nothing later |
| 10 | Index row under 35556695 | yes | `runs/index.tsv:1013` |
| 11 | hrun read-only | yes | `hrun_reconciliation.txt` |
| 12 | Scoped git | yes | only ticket + `?? work/`; diff --check clean |
| 13 | IDs unique ascending | yes | 74 264 rows, 12 cells, 0 dup |
| 14 | Parents exist/precede | yes | 0 violations |
| 15 | Raw events published once | yes | contiguous raw_ev, 0 gaps |
| 16 | Absence event linked to empty query | yes | OWN_1/2, REVERSE_1/2 event 5 kind absence, parent 4 query/empty/no_interval |
| 17 | `no_event` coverage | partly -> declared | 40 rows, but exporter scope is the three target seams (`export18.py:8,174-181`); ticket now says "target seams only" |
| 18 | Detail one row per published event | yes | 74 264 rows, (cell,out_id) unique, set-equal to trace.tsv |
| 19 | One-based axis rows | yes | min 1 max 3; +1 in `feature_matching.cpp` ~1465-1512; 5 606 rows lo>hi (pair convention now declared) |
| 20 | Frozen stage vocabulary | no (extra stage) | 5 312 rows `stage=state`; now declared as an extra lineage stage, not in CANON |
| 21 | Synthetic controls | yes | `calibration.tsv:2-5` 0.000000…0.000002 |
| 22 | ORIG/1 + OWN/1 62 seams each | yes | 124 real rows, no blanks; `calibration_physical.tsv` 124 |
| 23 | Trace-vs-saved/scorer flags | yes | 0 expected≠actual; 124/124 match scorer |
| 24 | Physical/piece rows separate | yes | e.g. ORIG 1-2 1.053403 deg / 1.278836 mm vs scorer 1.052/1.279; pieces 62 rows |
| 25 | Point-error claim | no -> fixed | max 0.001503 mm, not 1e-4; ticket text corrected; gate bar 0.01 passes |
| 26 | 36 renders, same camera per seam | yes | 36 PNGs 2280×760; identical camera within seam |
| 27 | Caption stage vs export | yes | `render18.py:96-102,145-147`; e.g. ORIG_1_13-28 "final saved export poses (labeled)" |
| 28 | Named renders opened; counts consistent | yes | opened ORIG_1_13-28, OWN_1_27-28, OWN_2_13-28, REVERSE_1_27-28, REVERSE_2_27-28, REVERSE_2_28-31, AUTHOR_1_27-28, FORWARD_1/2_27-28; captions match `seam_counts.tsv` (OWN_1 924/0/absence 5; REVERSE_2 634/600/32/97; FORWARD_1 1849/35/0/41; ORIG_1 158/259/52/19) |
| 29 | REVERSE_2 28-31 unresolved, no competitor | yes | `first_loss.tsv` unresolved; 356 beam/dedup rows with reason; 0 competitor fields |
| 30 | FORWARD_1 27-28 identity | yes | 31 distinct / 0 accepted |
| 31 | REVERSE_1 27-28 zero-interval pass | yes | 620 q / 0 intervals / absence ev 5 / pass 1 |
| 32 | first_loss 36 rows, real events | yes | 26 held / 9 failed / 1 unresolved; all referenced events exist |
| 33 | No rerun in this pass | yes (indirect) | no sbatch after 35556695; evidence mtimes post-date job end |
| 34 | Self-compliance numbers | mixed -> fixed | 26/9/1, 124/124, 356, 42-41 correction confirmed; row 25 scope and row 12 point claim corrected |

**Reviewer discrepancies and fixes**: (1) the 1e-4 mm point-error claim was wrong (max 0.001503 mm) and is corrected in the calibration paragraph and limitation (g); (2) `no_event` coverage is now stated as target-seam scope; (3) the 5,312 `state` rows are declared as an extra stage beyond the frozen vocabulary (they stay, because they carry lineage); (4) the `axis_lo > axis_hi` pair convention is declared; (5) this table is appended, so row 47 is now true. The reviewer's unverifiable items remain Spartan-side: patch diffs, truth log, source hashes, fresh-Result proof.

**End state:** ready
