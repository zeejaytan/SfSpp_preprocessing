# 18: Find the first loss of the three E28 joins

**What to build:** Use the authors' released Pot E sample as the benchmark. With one byte-identical instrumented assembler, locate the first reproducible failure for 13–28, 27–28 and 28–31. Separate missing viable matches, rejected or moved placements, and search pruning.

**Answers:** E1
**Blocked by:** None. Use the closed Ticket 17's frozen inputs and Ticket 11's calibration requirements.
**Status:** ready-for-agent
**Worker:** unassigned
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
