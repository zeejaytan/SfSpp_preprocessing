# 13: Confirm the J01 swap with one executable and trace the useful axis

**What to build:** Verify the reciprocal J01 axis-file effect with one assembler executable, show the joins, and locate the stage at which the useful axis is lost on our walls.

**Answers:** E1
**Blocked by:** None. Use frozen Ticket 12 arm inputs, recorded at `04cb4a6` and Spartan run `20261121-2359_2e951d9_t12-ctl`.
**Status:** ready-for-agent
**Worker:** unassigned
**Budget:** medium 5
**Hand-over:** DeepSeek, one-shot diagnostic.

## A. Confirm the reciprocal result

- Reuse Ticket 12's pinned assembler, scorer and staging recipe. Compile **once** for fixed in-container input and output paths. Rebind each isolated arm's input/output directories to those same paths. Keep executable, container, flags, scorer, ordering, thread settings and non-axis inputs fixed. Record SHA-256 of the actual executed file for every launch and fail before scoring if any hash differs. Record checksums for the arm input manifests and confirm the reciprocal contrasts each differ by exactly one entire J01 axis file. Preserve candidate order and sign. Hold breaklines and wall clouds read by the assembler fixed. The donor is the same selector on the authors' walls, not their released or ground-truth axes.
- Run two interleaved repeats of each arm: all own-wall axes, own background with J01 donor, all author-wall axes, author background with J01 own. Reuse thread settings and document available seeding. Score each reference join by the existing relative scorer and corpus caveats. Report exact gained/lost seams, best attempt and frequency. Confirm the effect only if both forward swaps gain joins and both reverse swaps lose joins against their paired controls. Record any unstable or incomplete cells.
- Render all four arms at the same locked view and scale using scorer-aligned native meshes or wall clouds. Show seam close-ups for J01–J03 and J03–J06, which Ticket 12 recovered both times, with matching camera, sherd colours, and mm scale. Label absent or failed seams and show actual assembled poses. If those seam verdicts differ in this replay, retain the views and label what happened.

## B. Attribute the J01 axis

- A whole-file swap does not identify which candidate matters. On the own background, insert one author-wall candidate at a time into the corresponding rank slot of the own J01 file. Preserve the other slots and their bytes, candidate count, and input invariants. Run the three substitutions twice using the same assembler executable and paired controls. Record loaded rank, axis orientation and seam set. Treat a line as sufficient for the observed effect only if both attempts recover at least 10 of the full forward swap's common recovered seams with no baseline join lost. If several pass, trace all passing lines. If none pass, report that the isolated line is unresolved, trace all donor candidates, and keep candidate order or combination as an open explanation.
- Use Ticket 03 selector source `2e951d9`, its recorded settings and original frozen J01 walls. Add logging only in a run-local copy: in `sfs_axes/potsac.py:run_potsac_union` capture the raw proposals, cluster membership, representatives and shortlist; in `sfs_axes/joint.py:_select`, `merge_lines` and `orient_merged` capture arm costs, refinements, duplicate decisions, ordering, truncation and final signed lines. Inspect the stock profile arm in `select.py` for its equivalent pre/post-rank events. Retain stable source-to-output IDs. Require traced and untraced selector outputs to be byte-identical on both wall sets and compare to the frozen files before linking trace to replay. Keep original file order, frames, random draws and scales.
- Compare candidates to each traced donor line by sign-free angle and line separation measured at the same J01 centroid. Record sign separately. Pre-register a joint match within 10° and 10 mm, and give nearest distances, plus 5°/5 mm and 15°/20 mm sensitivity. For each stage report candidate count, matched IDs, cost/rank and drop reason on both wall sets. Identify absence at generation, loss in clustering/refinement, removal by ordering/dedup/cap, or survival in the exported file. If the reading changes with tolerance or no single line is attributable, report the ambiguity. Never feed reference labels into candidate generation or selection.

## Acceptance

### Required build and launch recipe (revision 2)

Run on an allocated compute node. Take `patch_guard67.py` and `mk_inc.py` from the frozen Ticket 12 run's `work/`. Use `RUN` for the absolute Ticket 13 run directory. Each `TREE` below is the staged arm's absolute Pot J dataset root, with a fresh `Result` directory. Build once, then bind each arm to the same in-container dataset name. Use unique arm roots and do not reuse an existing Result directory.

```bash
set -euo pipefail
MAIN=/data/gpfs/projects/punim2657/sfs_main
SIF="$MAIN/sfs_pristine_assembly.sif"
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
T12=/data/gpfs/projects/punim2657/SfSpp/runs/20261121-2359_2e951d9_t12-ctl
WORK="$RUN/work"
mkdir -p "$WORK"/{shim,inc_J/class,logs,build}
SHIPPED="$MAIN/sfspreproc-docker/hpc/tools/main_pristine_batch.cpp"
# Abort on mismatch with the Ticket 12 provenance.
printf '%s  %s\n' fb26e8ab49e9c00f7e8d02de44f6eea5 "$SHIPPED" | md5sum -c -
"$PY" "$T12/work/patch_guard67.py" "$SHIPPED" "$WORK/shim/G.cpp"
printf '%s  %s\n' 056dfb914d7f067244a87d200ecb9863 "$WORK/shim/G.cpp" | md5sum -c -
grep -Fq 'point_.cols() < 50' "$WORK/shim/G.cpp"
"$APT" exec "$SIF" cat /opt/sfs-pristine/class/data_path.h > "$WORK/data_path.h"
"$PY" "$T12/work/mk_inc.py" "$WORK/data_path.h" "$WORK/inc_J/class/data_path.h" J
"$APT" exec --writable-tmpfs --bind "$MAIN:/workspace" --bind "$WORK:/panel" "$SIF" bash -euc '
  cd /panel/build
  cmake /opt/sfs-pristine -DCMAKE_BUILD_TYPE=Release > /panel/logs/cmake.log 2>&1
  make -j8 > /panel/logs/make.log 2>&1
  d=CMakeFiles/Hierarchy-Clear.dir
  defs=$(sed -n "s/^CXX_DEFINES *= *//p" "$d/flags.make" | tr " " "\n" | sed "/GOOGLE_GLOG_DLL_DECL/d" | tr "\n" " ")
  incs=$(sed -n "s/^CXX_INCLUDES *= *//p" "$d/flags.make")
  flags=$(sed -n "s/^CXX_FLAGS *= *//p" "$d/flags.make")
  g++ -I/panel/inc_J $defs $incs $flags -I/opt/sfs-pristine -I/opt/sfs-pristine/class -c /panel/shim/G.cpp -o "$d/shim_t13.o"
  sed -e "s|\(/opt/sfs-pristine/build/\)\?CMakeFiles/Hierarchy-Clear.dir/main.cpp.o|$d/shim_t13.o|" -e "s|-o Hierarchy-Clear|-o Hierarchy-T13|" "$d/link.txt" > /panel/logs/link_t13.sh
  grep -Fq "$d/shim_t13.o" /panel/logs/link_t13.sh
  bash -e /panel/logs/link_t13.sh
  sha256sum /panel/build/Hierarchy-T13 > /panel/logs/executable.sha256
'

# For each staged arm set TREE and LABEL. Run from an environment with
# inherited SFS_* variables and POT_NAME cleared as in Ticket 12.
mkdir "$TREE/Result"
"$APT" exec --writable-tmpfs --bind "$MAIN:/workspace" --bind "$WORK:/panel:ro" \
  --bind "$TREE:/Dataset/SfS_pp" --env OMP_NUM_THREADS=8 "$SIF" bash -euc '
    sha256sum -c /panel/logs/executable.sha256
    exec /panel/build/Hierarchy-T13 19
  ' > "$RUN/logs/run_$LABEL.log" 2>&1
```

Score each arm's `"$TREE/Result"` with the unchanged Ticket 12 `score305.py` (arguments: result dir, frozen corpus Ground Truth dir, J, frozen own `arm_pieces_J.tsv`, score output, arm label). Reuse the executable from the already-running implementation only if its saved build, runtime binds and executable hash meet this recipe's pinned semantics. Stop and write blocked if source, SIF or recipe provenance cannot be established.

### Required logging anchors and evidence (revision 2)

- `potsac.py:_cluster_union`: record the actual first `hit[0]` in the hit branch and the new representative index in the else branch. `run_potsac_union` normalized branch: record successful `all_cands.append(vt)` with seed and draw index, then the arrays immediately after `V = np.column_stack(all_cands)` and `reps, sizes = _cluster_union(V)`.
- `select.py:select_union_lines` stock-profile branch: record membership before and after `np.argsort(-sizes, kind="stable")[:PROFILE_BASINS]`, the raw/ref pair after `refine_axis_normalized`, and the cap, `keep_lines`, and final orientation at their existing statements. In `rank_by_profile` record sorted `pool`, first `_distinct` survivors before `[:refine_k]`, output of each `refine_axis_profile`, sorted `fin` and final `kept`. In `_distinct` log each suppressed candidate and the first retained line making its existing predicate true.
- `joint.py:_candidates` and `_select`: record the basin cutoff, sorted costs and shortlist, bounded/refined geometry and fallback, and post-`_dedup` selection. In `merge_lines` record each actual append or duplicate/cap exclusion with source arm, rank and suppressing ID. In `orient_merged` record the signed result. Use the arrays before and after their existing operations, with no change to predicates, comparator order, RNG or early returns. Final IDs must map to exported file rows.
- Output contract in the evidence directory: `replay.tsv` as above, using arm names OWN, FORWARD, AUTHOR, REVERSE, SLOT1, SLOT2, SLOT3; `seams.tsv` columns arm, repeat, seam (canonical lower-ID-first with a hyphen), pass (0/1); `inputs.tsv` columns arm, repeat, path, sha256; `selector_bytes.tsv` columns wall (own/author), frozen, plain, traced (SHA-256); `trace.tsv` columns wall, id, parent_id, stage, angle_deg, offset_mm, donor_rank, rank, reason; roots use empty parent_id and stage raw, exported rows use stage exported. ID is unique within wall and donor rank. Keep a stable ID for each stage row and link its immediate predecessor. `renders.tsv` columns arm, repeat, view (assembly, 1-3, 3-6), path, camera; paths are relative to the evidence directory. At minimum render these three views for each reciprocal arm at repeat 1, plus any repeat that changes a pictured seam verdict. `jobs.tsv` columns job_id, run_id, state, exit_code, polled, indexed. Preserve failures and incomplete cells.

- [ ] Save `replay.tsv` with columns `arm`, `repeat`, `binary_sha256`, `joins`, `changed_paths` (including patch arms), per-seam scoring, input hashes, render inventory, and a candidate trace with linked stage IDs and an output byte comparison under `C:/PR/artifacts/axis-parity-13/`. Report any skipped or incomplete cells explicitly.
- [ ] Keep instrumentation patches, geometry and scripts in the isolated Spartan run record. Hold the corpus fixed and record manifest equality. Poll each submitted job, record final sacct State/ExitCode and run-index entries. Do geometry and builds on compute nodes.
- [ ] Write a factual report with one End state in this ticket on its worktree. Leave commit, merge, close and judgement to the lead. No tracked source changes.

## Comments

One-shot diagnostic. The pinned [SfS++ method](https://arxiv.org/html/2502.13986v1#S4.SS2.SSS2) generates several axis hypotheses before pruning and refinement, so final axis files alone cannot distinguish candidate generation from selection.
