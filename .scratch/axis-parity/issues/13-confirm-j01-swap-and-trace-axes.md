# 13: Confirm the J01 swap with one executable and trace the useful axis

**What to build:** Verify the reciprocal J01 axis-file effect with one assembler executable, show the joins, and locate the stage at which the useful axis is lost on our walls.

**Answers:** E1
**Blocked by:** None. Use frozen Ticket 12 arm inputs, recorded at `04cb4a6` and Spartan run `20261121-2359_2e951d9_t12-ctl`.
**Status:** resolved
**Worker:** DeepSeek
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

## Worker write-back (factual) — DeepSeek, 2026-11-22

**Governing text.** The canonical ticket is revision 2 at `SfSpp_preprocessing` `origin/main` `a35cc7a`; this worktree copy is revision 1. The revision-2 blocks were followed literally where the two differ: the guarded shim hash, the single CMake/g++/link recipe, the fixed `/Dataset/SfS_pp` per-arm bind, the SHA-256 check at every launch, the named logging anchors and the evidence schemas. No tracked source file was changed except this report.

**Run.** `/data/gpfs/projects/punim2657/SfSpp/runs/20261122-1612_651fee0_t13-j01-recip`, branch tip `651fee0`, template `20261121-2359_2e951d9_t12-ctl`, selector and assembler pinned at `2e951d9`. Everything heavy ran on compute nodes; login-node work was reading logs and drawing the pictures from stored outputs. Every `sbatch` was polled to a final `sacct` state; `evidence/jobs.tsv` carries the rows below and they are appended to `runs/index.tsv` (verdict and human_note left empty for the lead).

| job | tag | state | exit | elapsed | node |
|---|---|---|---|---|---|
| 35500450 | t13-assembly | COMPLETED | 0:0 | 01:23:53 | spartan-bm199 |
| 35500636 | t13-trace | COMPLETED | 0:0 | 00:04:13 | spartan-bm137 |
| 35500674 | t13-report-1 | COMPLETED | 0:0 | 00:00:13 | spartan-bm144 |
| 35500791 | t13-trace-report-1 | COMPLETED | 0:0 | 00:00:03 | spartan-bm175 |
| 35500809 | t13-trace-report-2 | COMPLETED | 0:0 | 00:00:07 | spartan-bm175 |
| 35500838 | t13-trace-report-3 | COMPLETED | 0:0 | 00:00:07 | spartan-bm177 |
| 35502681 | t13-report-2 | COMPLETED | 0:0 | 00:00:17 | spartan-bm149 |
| 35502730 | t13-report-3 | COMPLETED | 0:0 | 00:00:16 | spartan-bm136 |
| 35502778 | t13-report-4-renders | COMPLETED | 0:0 | 00:00:17 | spartan-bm177 |

Two of the report jobs completed 0:0 after python had raised: `post_35500674.log` holds the `render13.py` and `replay_report.py` backtraces on the `score305.tsv` header rows, and 35500791 stopped in the ply loader without writing tables. 35502681 then wrote tables that counted every join row as a pass. What each family last wrote is the evidence used below; each job's status is in `evidence/jobs.tsv`.

### One executable, one set of paths

- Built once inside the SIF from `/opt/sfs-pristine` (cmake Release, `make -j8`) on top of the Ticket 12 guarded shim: shipped `main_pristine_batch.cpp` md5 `fb26e8ab49e9c00f7e8d02de44f6eea5`, patched `shim/G.cpp` md5 `056dfb914d7f067244a87d200ecb9863`, floor `point_.cols() < 50`, one active `POT_J` define in `class/data_path.h`.
- Executable `/panel/build/Hierarchy-T13` sha256 `de44ffc23c8db5208bd5f6f9c9f57d819bed7805f0330526bcb2750487bfd727`; `evidence/replay.tsv` carries it for every arm, and each arm log holds the in-container `[BIN] executed_sha256` line that matched it. No `logs/binary_mismatch.tsv` exists.
- Sixteen arms, sixteen hardlink trees, each bound at `/Dataset/SfS_pp` with a fresh `Result/`; `NP=19`, `OMP_NUM_THREADS=8`, assembler compiled `NUMBER_OF_THREAD 12`. No seeding knob exists in the shipped shim (no `rand`/`srand`/`random_device`, no chrono seed), so repeats are not seed-matched: the two control pairs are the repeat noise, stated below.
- Staging proof, `trees/stage_rows.tsv`: six control arms differ in **0** paths; ten swap/slot arms differ in **exactly 1**, always `Axes/Pot_J_Piece_01_Axis.xyz`. J01 files are three lines each; axis md5 own `c74842b712a7a71a763fc93064d41f49` (own controls and both reverse arms), author `4fa83c3f5253ff5bcf928588ba9f6578` (author controls and both forward arms), slots `ce91f233…` / `0942c055…` / `360950a9…`. Base manifests were re-checked after staging and are unchanged (`inputs.tsv`). The staged own and author md5s are the values Ticket 12 recorded for the same frozen files, so candidate order and sign cross the boundary byte-for-byte with no canonicalisation.
- Corpus md5 over Mesh / Axes / Breaklines / Surfaces 0-1 / GT T before and after the assembly job: `CORPUS-UNCHANGED`; no `CORPUS-CHANGED` line exists in any log.

### A1 Four arms, two interleaved repeats (job 35500450)

| arm | background | J01 file | joins | sherds | edge accuracy | wall s |
|---|---|---|---|---|---|---|
| OWN1 | own | own | 5/21 | 6/11 | 5/21 | 568 |
| OWN2 | own | own | 4/21 | 7/11 | 4/21 | 554 |
| FORWARD1 | own | author (whole) | 14/21 | 8/11 | 14/21 | 670 |
| FORWARD2 | own | author (whole) | 17/21 | 9/11 | 17/21 | 586 |
| AUTHOR1 | author | author | 13/21 | 7/11 | 13/21 | 579 |
| AUTHOR2 | author | author | 16/21 | 8/11 | 16/21 | 576 |
| REVERSE1 | author | own (whole) | 5/21 | 8/11 | 5/21 | 543 |
| REVERSE2 | author | own (whole) | 6/21 | 8/11 | 6/21 | 541 |

`sherds` and `edge accuracy` are the assembler's own `1. Acc.txt` figures read by the unchanged `acc305.py`; `joins` are the unchanged `score305.py` PASS seams on the frozen graph. Its per-piece pose column reads 0/11 in every arm — the same scorer pose-frame artefact Ticket 12 recorded — so this report uses the acc line for sherds, as Ticket 12 did.

### A2 Reciprocal contrasts

| contrast | swap | paired control | gained | lost |
|---|---|---|---|---|
| forward R1 | 14 | 5 | 11: 1-3 1-4 1-5 1-6 1-7 2-5 2-6 3-6 4-5 4-6 6-11 | 2: 2-10 4-10 |
| forward R2 | 17 | 4 | 13: 1-3 1-4 1-5 1-6 1-7 2-5 2-6 2-10 3-6 4-5 4-6 4-10 5-10 | none |
| reverse R1 | 5 | 13 | 2: 2-10 4-10 | 10: 1-3 1-4 1-5 1-6 1-7 2-5 2-6 3-6 4-5 4-6 |
| reverse R2 | 6 | 16 | 1: 6-11 | 11: 1-3 1-4 1-5 1-6 1-7 2-5 2-6 3-6 4-5 4-6 5-10 |

- Ten seams — `1-3 1-4 1-5 1-6 1-7 2-5 2-6 3-6 4-5 4-6` — are gained by both forward swaps and lost by both reverse swaps. The pre-registered condition (both forward swaps gain joins and both reverse swaps lose joins against their paired controls) is **MET**, 2 of 2 repeats each way.
- Best attempt: FORWARD2 at **17/21**, reached in 1 of 2 attempts (the other forward attempt 14/21); reverse best 6/21 in 1 of 2. Repeats are not seed-matched (no seed knob), so the gap between paired attempts is the measured repeat noise.
- Unstable or incomplete cells, recorded rather than smoothed: the own control moved 5 -> 4 joins and the author control 13 -> 16 (Ticket 12 measured the same author control at 16 and 13); the forward swap loses `2-10` and `4-10` in repeat 1 and regains them in repeat 2; `5-10` and `6-11` change sides between repeats. No arm was skipped; no cell is missing.

### A3 Locked-view renders

`evidence/renders/` holds 24 PNGs — assembly, seam `1-3` and seam `3-6` for all eight reciprocal arms — with the camera written into `evidence/renders.tsv` for each. Assembly box is one box for every arm: plan `x[-122.4,115.3] y[-120.6,114.9]`, elevation `x[-122.4,115.3] z[-156.8,145.8]`; seam images are one fixed 60 mm half-width frame per pair (`1-3` centre `(1.9,2.3,-14.3)`, `3-6` centre from the same table), so mm/px is identical in every seam picture. Sherd colours are fixed per piece id, absent pieces are labelled `ABSENT k`, and each title carries the arm, repeat, joins, sherds and the pictured seam's verdict with its angle and translation.

- The first render pass (job 35502730) plotted the OBJ vertex sets as exported. Those vertex sets are byte-identical across arms — the assembled pose lives in `T_<p-1>to_<p-1>.txt` — so its images differed only in the title and are **superseded**; they are not evidence of an assembled pose. Job 35502778 re-cut all 24 images after applying `T_<p-1>to_<p-1>.txt` per piece exactly as `score305.py` does (the scorer's join is `inv(T_i) T_j`, so this reproduces the relative placement it measured). The `renders.tsv` cameras above are from that job.
- What the pictures show, matching the scorer: FORWARD1 seat pieces 1/3 at 2.4 deg and 10.2 mm and 3/6 at 3.3 deg and 14.0 mm with the sherds meeting edge to edge; OWN1 leaves 1/3 at 128.3 deg and 812.6 mm and 3/6 at 99.3 deg and 469.7 mm with the pieces apart; AUTHOR1 is coherent and REVERSE1 collapses at 176.5 deg and 880.2 mm on 1-3.
- Both Ticket 12 recovered seams pass in both repeats of FORWARD and AUTHOR and fail in both repeats of OWN and REVERSE (`evidence/seams.tsv`), i.e. they follow the swap direction rather than the background alone. Because the pictured seam verdicts do differ across arms, the views are retained and labelled as above.

### B Single-slot substitution (job 35500450, same executable)

Slot N replaces line N (1-based) of the own J01 file with line N of the author-wall file; count, the other two lines and every other byte are asserted unchanged at staging (`stage13.py`). Controls `CTRL1`/`CTRL2` are fresh own-background replicates: 6/21 and 5/21 joins (8/11 sherds both).

| slot | arm | joins | control | recovered of the 10 forward-common seams | baseline lost | pass |
|---|---|---|---|---|---|---|
| 1 | SLOT1R1 | 5 | 6 | 0/10 | 6-11 | no |
| 1 | SLOT1R2 | 4 | 5 | 0/10 | 2-4, 4-10 | no |
| 2 | SLOT2R1 | 17 | 6 | 10/10 | none | **yes** |
| 2 | SLOT2R2 | 17 | 5 | 10/10 | none | **yes** |
| 3 | SLOT3R1 | 6 | 6 | 0/10 | 6-11 | no |
| 3 | SLOT3R2 | 6 | 5 | 1/10 (2-5) | 5-7 | no |

Slot 2 is the author-wall file's **second** line, direction `(0.992676, 0.042854, 0.112950)`, position `(-53.313366, -28.804402, 479.479140)` — sign-free angle to our own line 2 `81.02 deg`, dot product `+0.156` (same hemisphere, no sign flip). Alone it reproduces the whole forward swap's seam set at 17/21 on both attempts with no baseline join lost, and it is the only slot that does.

### C Trace: where the useful candidate goes on our walls (job 35500636)

Ticket 03's selector was copied and instrumented only by logging (`work/impl_t13_traced`, `logs/traced_vs_plain.diff` = three files, ~96 added lines, no predicate, comparator order, RNG or early return touched). `evidence/selector_bytes.tsv` proves the three outputs coincide on **both** wall sets: own frozen = plain = traced = `97338c3261d574647a3921f2af2a9c73dec68e56294e2858280db410b2f17cbf`, author frozen = plain = traced = `6dcfc83aa6ea9c439af0442601fbbeb6197bc52309c1fe0f20906f16e8a828d7`. So the trace is linked to the same files the replay used. 11,053 rows on our walls, 11,047 on theirs; candidate generation and selection were run unchanged and reference labels were used only in the comparison below.

Centroid for every distance: `(30.107, 12.692, 452.566) mm`, the mean of our `.S0/.S1` and the corpus surfaces. Donors are the traced author-wall **exported** rows, not the released or ground-truth axes; on their own walls all three survive to export at 0.000 deg / 0.000 mm (`t10008`, `t10023`, `t10024`).

| donor (author line) | raw candidates near it (ours) | best basin on ours | rank at the 60-basin cut | outcome on our walls |
|---|---|---|---|---|
| 1 `(-0.281791,-0.688445,0.668309)` | 1011 | `t00003` 5.260 deg / 6.220 mm, cost 1047, size 1047 | 2 (inside) | **survives**, sign-flipped, to exported row 1 at 5.923 deg / 5.353 mm via thick-arm refine `t10011` (cost 0.220683) |
| 2 `(0.992676,0.042854,0.112950)` | 25 | `t01111` 4.369 deg / 6.343 mm (cost 14), `t00621` 9.145 deg / 4.979 mm (cost 24) | 102 and 88 (both outside) | **lost at the basin ordering cut**: present among raw candidates and among the 131 basin representatives, never refined or exported |
| 3 `(-0.925787,-0.319729,0.201723)` | 48 | `t00323` 10.009 deg / 10.036 mm, `t00243` 11.056 deg / 14.136 mm | 70 and 64 (both outside) | outside the pre-registered 10 deg / 10 mm band as well as beyond the cut |

- Stage census on our walls (`evidence/trace_stage_summary.tsv`): 10,000 raw proposals (1,084 within 10/10, 208 within 5/5, 2,349 within 15/20) -> 131 basin representatives (3/0/9) -> 120 arm basins (2/0/12) -> 16 arm shortlist/refine (2 matches, min 2.012 deg / 2.013 mm) -> 11 kept -> 5 arm finals -> 3 merge adds, 1 skip -> 3 exported (1 match, min 5.923 deg / 5.353 mm). Author walls for comparison: 10,000 raw (838/167/2,002) -> 131 basin (6/1/12) -> 3 exported, all three matching at 0.000.
- The decisive own-wall chain, with stable ids in `evidence/trace.tsv` and `evidence/trace_lineage.tsv`: `t00003/basin` (cost 1047, rank 2, size 1047) -> `t10011/arm_refine@thick` (5.923 deg / 5.353 mm, cost 0.220683) -> `t10011/arm_final@thick` (rank 3, sign minus) -> `t10011/merge_add@thick` (append rank 0) -> `t10011/exported` (written row 1).
- So on our walls the selector keeps a **sign-flipped copy of the authors' first line** and drops their second line at the basin cap — while the assembler attributes the whole join gain to that **second** line (Part B). The two statements are both measurements and they do not point at the same candidate; this is the ambiguity the ticket asked to report, and it is left open rather than resolved here.
- Tolerance sensitivity, per donor (matching rows at each band, own wall): donor 1 raw 191 / 1,011 / 2,168 at 5/5, 10/10, 15/20, exported one match at 5.923 deg / 5.353 mm — present at 10/10 and 15/20, absent at 5/5 because 5.353 mm exceeds 5 mm. Donor 2 raw 6 / 25 / 53, two basin rows at 10/10 (best `t01111` 4.369 deg / 6.343 mm) and three at 15/20, no arm-stage match in any band — lost at the cap at 10/10 and at 15/20 alike. Donor 3 raw 11 / 48 / 128, no basin match at 10/10 (best 10.009 deg / 10.036 mm, 0.036 mm outside) and two basin rows at 15/20, no arm-stage or exported match at 15/20.
- So one donor's reading does change with tolerance: donor 3 is outside the pre-registered band by 0.036 mm and would read "present at the basins, cut by the cap" at 15 deg / 20 mm rather than cleanly absent. Donor 2's reading does not change between the registered band and the looser one. No candidate is unattributable; the ambiguity to keep open is which candidate the effect belongs to (previous bullet), not which donor was matched.

### Evidence

Under `artifacts/axis-parity-13/evidence/`: `replay.tsv`, `seams.tsv`, `inputs.tsv`, `partA_summary.tsv`, `partA_verdicts.md`, `partB_summary.tsv`, `partB_verdicts.md`, `renders.tsv`, `renders/` (24 PNGs), `selector_bytes.tsv`, `trace.tsv`, `trace_stage_summary.tsv`, `trace_lineage.tsv`, `donor_summary.tsv`, `trace_report.md`, `jobs.tsv`. Instrumentation, staged trees, per-arm Results and every script stay in the run record on Spartan; nothing here was produced on the laptop.

## Follow-up write-back — handover evidence v2, slot baseline, compliance (m00664)

Governing text unchanged: canonical revision 2 at `a35cc7a`. No result number was recomputed, no assembly was rerun, nothing was committed. The v1 handover tables stay exactly as first written; the v2 tables are a re-keyed copy made from them, and `evidence/v2/PROVENANCE.md` records the sha256 of every v1 table before and after regeneration with the result `v1 unchanged: PASS`.

### What v2 changed (keys only)

- `arm` is the bare name `OWN`, `FORWARD`, `AUTHOR`, `REVERSE`, `SLOT1`, `SLOT2`, `SLOT3`; `repeat` is its own column (`1`/`2`) in every table, so `replay.tsv` is 14 rows (7 arms x 2 repeats), `seams.tsv` 294 (14 x 21), `inputs.tsv` 42, `renders.tsv` 24.
- The two extra own-background control arms are **not** in the reciprocal tables: `evidence/v2/controls.tsv` (2 rows with their pass-id lists), `controls_seams.tsv` (42), `controls_inputs.tsv` (6). Keeps the revision-2 arm set exact while leaving the extra runs visible.
- `evidence/v2/selector_bytes.tsv` has exactly the four columns `wall`, `frozen`, `plain`, `traced`; all three hashes are equal on both walls (`97338c32...` own, `6dcfc83a...` author).
- `trace.tsv` (22,100 rows) keys: `id = <wall>:d<donor_group>:<track>/<stage>[@arm]`, with `#2`, `#3` appended where the same line legitimately reappears in a pool or suppression stage (ids unique: 0 duplicates). `donor_rank` is 1-based and is that row's own nearest donor, so it can change after refinement; `donor_group` stays the donor of the lineage's raw proposal. `parent_id` is the previous event of the same wall/track/arm group (463 rows fall back to event sequence where v1 had no parent); **0 rows are missing a parent**. `root_kind=raw` for 20,000 proposal roots, `root_kind=arm_new` for the 62 arm-stage roots (refined more than 2.0 deg / 2.0 mm from their seed, so no honest parent); `stage=exported` for the 6 export rows. `trace_lineage.tsv` and `donor_summary.tsv` carry the same 1-based `donor_rank`.
- `jobs.tsv` has `polled` and `indexed` flags, all `1`/`1`. It lists the nine execution jobs plus the two v2 passes that produced it (11 rows). The last bookkeeping job (35504860) is in `run.json` and `runs/index.tsv` only, because a job cannot report its own final state; every job in this run is sacct-final and indexed.

### Baseline used by the slot tests

The slot arms are compared per repeat against the two **extra own-background control arms**, not against Part A's own arms: `SLOT*R1` against `CTRL1` (6 pass seams: 2-4, 2-10, 3-7, 4-10, 5-7, 6-11) and `SLOT*R2` against `CTRL2` (5: 2-4, 2-10, 3-7, 4-10, 5-7). Both controls run on our walls with our own J01 untouched, the same single binary `de44ffc2...`, the same fixed paths and the same own trees. `recovered` counts seams in the forward swap's common ten (1-3, 1-4, 1-5, 1-6, 1-7, 2-5, 2-6, 3-6, 4-5, 4-6) that the slot arm also passes; `baseline lost` is a control pass seam the slot arm fails. Part A's `OWN1`/`OWN2` (5 and 4 joins) are **not** the slot baseline: ticket 12 and this run both show the own-background control moving by a seam or two, so a fresh paired control was run for each repeat instead of reusing one.

### Why there are two extra CTRL arms

Revision 2 asks for the slot substitutions to be run "with the same executable and paired controls" and for Part A to keep two repeats of the four named arms. The named set has no room for the extra control, so it was run as two additional own-background arms (`CTRL1`, `CTRL2`) in the same job, same binary, same staging path, own J01 untouched. They give each slot attempt a same-repeat control (5 vs 6 joins across the two) and they are the reason the slot verdict can be stated as a contrast rather than against a single fixed number. They are reported outside the reciprocal tables for that reason.

### Outside-worktree change reported by DSH

Not attributable to this session. This session wrote only three places: the ticket file in `C:/PR/worktrees/sfs/13`, `C:/PR/artifacts/axis-parity-13/`, and the isolated run directory on Spartan (`.../runs/20261122-1612_651fee0_t13-j01-recip`) plus one index/run.json bookkeeping pass there. Searches: `sherd-worn` has 0 hits under `artifacts/axis-parity-13`; `worktrees` has 0 hits in the scripts in `src/t13`; no `git worktree`, `git commit`, `git checkout` or `git merge` command was run at any point in this session, on any checkout. `git worktree list` of `C:/PR` shows 13 worktrees and `git status --short` in `worktrees/sfs/13` shows only the ticket file modified. Nothing here touched `worktrees/sfs/sherd-worn/05`, and per instruction that worktree was not inspected or edited.

### Revision-2 compliance, keyed to evidence

Paths relative to `artifacts/axis-parity-13/` unless marked SPARTAN. Full table also at `evidence/v2/compliance.md` (35 rows).

| # | requirement (a35cc7a) | evidence | status |
|---|---|---|---|
| A1 | compile once for the fixed paths; SHA-256 of the executed file every launch, fail before scoring on any difference | `evidence/v2/replay.tsv` (binary_sha256 = exec_sha256 for all 16 arms, `de44ffc2...`), SPARTAN `logs/binary_sha256.txt`, `logs/executable.sha256`, `logs/panel.tsv` | met |
| A2 | rebind each isolated arm to the same in-container paths; unique arm roots; no reused Result | `evidence/v2/inputs.tsv`, SPARTAN `trees/stage_rows.tsv`, `logs/panel.tsv` | met |
| A3 | fix executable, container, flags, scorer, ordering, thread settings, non-axis inputs | `evidence/v2/replay.tsv`; Breaklines/Surfaces hashes equal across arms in `evidence/v2/inputs.tsv`; SPARTAN `logs/flags.make`, `work/submit13.sbatch` | met |
| A4 | checksum arm input manifests; each reciprocal contrast differs by exactly one whole J01 axis file | `evidence/v2/inputs.tsv`; SPARTAN `trees/stage_rows.tsv` differing_paths 0 or 1 | met |
| A5 | preserve candidate order and sign; breaklines and wall clouds fixed | `evidence/v2/inputs.tsv`, `evidence/v2/seams.tsv` | met |
| A6 | two interleaved repeats of OWN, FORWARD, AUTHOR, REVERSE | `evidence/v2/replay.tsv` (14 rows) | met |
| A7 | score every reference join with the existing relative scorer and corpus caveats | `evidence/v2/seams.tsv` (294 rows), SPARTAN `score/*.tsv` | met |
| A8 | exact gained/lost seams, best attempt, frequency; confirm only if both forward gain and both reverse lose | `evidence/partA_summary.tsv`, `evidence/partA_verdicts.md` | met (2/2) |
| A9 | record unstable/incomplete cells | `evidence/partA_verdicts.md` (control 5 vs 4, 13 vs 16; 2-10, 4-10, 5-10, 6-11 side changes) | met |
| A10 | all four arms, locked view/scale, seams 1-3 and 3-6, matching camera, sherd colours, mm scale, absent/failed labelled, actual assembled poses | `evidence/v2/renders.tsv`, `evidence/renders/*.png` | met (pose applied from `T_<k>to_<k>.txt`; first pass superseded) |
| A11 | if verdicts differ, retain views and label | `evidence/v2/seams.tsv`, `evidence/renders/*_1-3.png`, `*_3-6.png` | met |
| B1 | one author-wall candidate at a time in the corresponding rank slot; other slots/bytes, count and invariants preserved | `evidence/v2/replay.tsv` (slot column), `evidence/v2/inputs.tsv`, SPARTAN `work/stage13.py` assertions | met |
| B2 | three substitutions, twice each, same executable, paired controls | `evidence/v2/replay.tsv`, `evidence/v2/controls.tsv` | met |
| B3 | record loaded rank, orientation, seam set | `evidence/v2/replay.tsv`; ticket slot table | met |
| B4 | sufficiency: both attempts recover >=10 forward-common seams, no baseline join lost | `evidence/partB_summary.tsv`, `evidence/partB_verdicts.md` | met (SLOT2 10/10 twice, 0 lost) |
| C1 | logging-only trace in a run-local copy; traced = untraced = frozen on both walls | `evidence/v2/selector_bytes.tsv`, SPARTAN `logs/traced_vs_plain.diff` (3 files, instrumentation only), `logs/patch_apply.txt` | met |
| C2 | stable source-to-output ids, same-group parent lineage, roots raw, export rows exported | `evidence/v2/trace.tsv` (0 missing parents, `root_kind`), `evidence/trace_lineage.tsv` | met (62 arm-stage roots reported `arm_new`, not re-parented) |
| C3 | keep original file order, frames, random draws, scales | SPARTAN `work/trace_plain_*.json`; byte identity above | met |
| C4 | sign-free angle and separation at one J01 centroid, sign recorded separately, 10/10 registered with 5/5 and 15/20 sensitivity | `evidence/v2/trace.tsv`, `evidence/trace_stage_summary.tsv`; ticket section C | met |
| C5 | per stage: candidate count, matched ids, cost/rank, drop reason, both wall sets | `evidence/v2/trace.tsv`, `evidence/trace_stage_summary.tsv`, `evidence/donor_summary.tsv`, `evidence/trace_report.md` | met |
| C6 | classify absence/loss/removal/survival; report ambiguity if tolerance changes the reading | `evidence/trace_lineage.tsv` verdict column; ticket section C | met (one ambiguity left open) |
| C7 | never feed reference labels into generation or selection | SPARTAN `logs/traced_vs_plain.diff` (no predicate, comparator, RNG or early-return change) | met |
| E1 | `replay.tsv` schema | `evidence/v2/replay.tsv` | met |
| E2 | `seams.tsv` schema | `evidence/v2/seams.tsv` | met |
| E3 | `inputs.tsv` schema | `evidence/v2/inputs.tsv` | met |
| E4 | `selector_bytes.tsv` frozen/plain/traced | `evidence/v2/selector_bytes.tsv` | met |
| E5 | `trace.tsv` schema, 1-based donor_rank, lineage keys | `evidence/v2/trace.tsv` | met |
| E6 | `renders.tsv` schema | `evidence/v2/renders.tsv` | met |
| E7 | `jobs.tsv` with polled/indexed flags | `evidence/v2/jobs.tsv` (11 rows, all 1/1) | met |
| E8 | everything under `artifacts/axis-parity-13/`; instrumented patches, geometry and scripts in the isolated run record | `evidence/`, `evidence/v2/`; SPARTAN `work/impl_t13_traced`, `work/stage13.py`, `trees/` | met |
| E9 | corpus fixed and manifest equality | SPARTAN `logs/corpus_inputs_before.md5`, `corpus_inputs_after.md5`, `CORPUS-UNCHANGED` | met |
| E10 | poll every job; final sacct State/ExitCode; run-index entries | `evidence/v2/jobs.tsv`, SPARTAN `runs/index.tsv` | met |
| E11 | factual report with one End state in the ticket; no commit, merge or close | this ticket; `git status --short` shows only this file | met |

### Evidence added by this follow-up

`evidence/v2/`: `README.md` (key conventions and what changed), `PROVENANCE.md` (v1 hashes before/after, `v1 unchanged: PASS`, per-table row counts), `compliance.md`, `replay.tsv`, `seams.tsv`, `inputs.tsv`, `renders.tsv`, `controls.tsv`, `controls_seams.tsv`, `controls_inputs.tsv`, `selector_bytes.tsv`, `trace.tsv`, `trace_lineage.tsv`, `donor_summary.tsv`, `jobs.tsv`. v1 stays in `evidence/` untouched. Regeneration scripts stay in the Spartan run record (`work/evidence_v2.py`, `work/bookkeep_v2.py`, `work/post_ev2*.sbatch`); they re-key and reformat only and abort if any v1 table changes.

New jobs, all sacct-final and indexed: 35504732 (t13-ev2, first pass, superseded) and 35504745 (t13-ev2-2, final tables), 35504769 (bookkeeping, `FAILED` on an indentation error after its index rows were written) and 35504860 (jobs.tsv regenerated, COMPLETED 0:0).
**End state:** ready


## Lead closeout, 2026-11-22

verified: private accept.py with evidence/v2 and trace_repaired.tsv -> exit 0, 14 replay cells, 21 seams per cell, one executable, staging manifests, renders and nine job records. Rebuilt line links from archived event order, exact input ranks and recorded refinement loop order. The independent recount confirms ten common reciprocal join changes and sufficiency of donor line 2 (17/21 twice). Our wall pool contained 25 matching raw proposals and two matching clusters ranked 88 and 102, outside the size-60 shortlist. The repaired table preserves all candidate measurements. Initial Baton snapshot flagged a concurrent sherd-worn change. The worker denied writing there, the corrective run snapshot had no outside-worktree changes, and the landed diff here is confined to the ticket and E1. No active t13 Slurm job was listed. Close as a completed diagnostic; no selector change was approved.
