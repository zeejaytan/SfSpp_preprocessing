# 19: Find what happens to a sound E28 placement in the Pot E search

**What to build:** Trace the exact placement the assembler keeps or discards for 13–28, 27–28 and 28–31. Determine whether an out-of-tolerance placement reaches the final assembly because no sound candidate formed, a geometric check rejected it, or the search dropped a sound alternative.

**Answers:** E1
**Blocked by:** None. Ticket 18 closed with direct-matching evidence and an unresolved search decision.
**Status:** resolved
**Branch:** 19-trace-e28-search-decisions, in /c/PR/worktrees/sfs/19
**Worker:** DeepSeek
**Budget:** large 8
**Hand-over:** DeepSeek V4.1 Flash via DSH Baton. The lead retains the private acceptance check.

## Question and controlled comparison

In Ticket 18, the released input and released axes on fixed geometry both gave 62/62 twice. Our axes gave 59/62 and 57/62. In REVERSE/2 the search's rank-one state included 28–31, but its final relative rotation was about 176° off. Seven recorded 28–31 pairs were already out of tolerance before group-axis adjustment. Aggregate pruning counts could not show whether a sound alternative was ever discarded. This ticket measures the choice directly.

Use four arms, two repeats each. ORIG binds the entire authors' released input as the benchmark. OWN, AUTHOR and REVERSE bind the same frozen Ticket 18 non-axis inputs. AUTHOR uses the axes estimated from the authors' walls. REVERSE uses AUTHOR with our E28 file as its only change. OWN uses all our axes. No FORWARD, Pot J, selector or repair work. Use 31 pieces and 62 reference joins. Launch the first wave ORIG, OWN, AUTHOR, REVERSE and the second wave in reverse order, 8 CPUs and threads per cell, with fresh result directories. Record sources of unseeded randomness rather than changing them. Baseline calibration and ORIG **31/31 and 62/62 in both repeats** are mandatory before stage attribution. Record individual failures and agreement across repeats.

## Exact build and launch

On Spartan set `T18=/data/gpfs/projects/punim2657/SfSpp/runs/20261123-1541_bff8db5_t18-first-loss`. Use the archived `$T18/work/t18/build18.sbatch` and `run18.sbatch` as literal templates. Their SHA-256 hashes are `7fb2701a68712f1751607cf8b9482efeb93f30b8eb46a191bb983743f32d4fbd` and `0c10e43423082a4bf0a3704808480b94baa0a2d299801ef1dd89aa36291bc794`. Use their original MAIN, BASE, FIXED, ORIG, APT, SIF, SHIPPED, PY, SCORER, PIECES and source and container pins. Assert the staged Ticket 18 ranking source after the Ticket 18 patch is `365c00a90d2fa8623756aab5b8f9af9523b1bd45bd90a3ec0cbeb5da760c7ce1`. Reuse its trace header and original Python patch byte-for-byte. Build in a new run from its own submitted directory, with `WORK="$RUN/work/t19"`. Preserve the archived run.

1. Keep the archived build script through the guard, Pot E include, SIF source copy, and original Ticket 18 patch. Apply the Ticket 19 patch only to staged `class/ranking_system.h`, `class/ranking_system.cpp` and guarded `G.cpp`. Copy `"$WORK/inc_E/class/data_path.h"` over `"$WORK/src/class/data_path.h"`. Store before/after hashes, reviewable patches, exact commands and build logs. Add one logging-only state ID field to `State`; all translation units must be rebuilt from the same staged tree to avoid layout mismatch.
2. In the archived Apptainer build invocation with `"$MAIN:/workspace"` and `"$WORK:/panel"` binds, replace the build body with the commands below. Keep the compiler flag extraction from Ticket 18 unchanged. The staged CMake compilation already compiles instrumented matching and ranking, so substitute **only** the main shim object. Verify the link command refers to the staged build's ranking object and its own shim. Keep floor 50, CMake Release and `make -j8`.

```bash
cd /panel/build
cmake /panel/src -DCMAKE_BUILD_TYPE=Release > /panel/logs/cmake.log 2>&1
make -j8 > /panel/logs/make.log 2>&1
d=CMakeFiles/Hierarchy-Clear.dir
defs=$(sed -n "s/^CXX_DEFINES *= *//p" "$d/flags.make" | tr " " "\n" | sed "/GOOGLE_GLOG_DLL_DECL/d" | tr "\n" " ")
incs=$(sed -n "s/^CXX_INCLUDES *= *//p" "$d/flags.make")
flags=$(sed -n "s/^CXX_FLAGS *= *//p" "$d/flags.make")
g++ -I/panel/inc_E -I/panel/src $defs $incs $flags -I/panel/src/class -c /panel/G.cpp -o "$d/shim_t19.o"
sed -e "s|CMakeFiles/Hierarchy-Clear.dir/main.cpp.o|$d/shim_t19.o|" \
    -e "s|-o Hierarchy-Clear|-o Hierarchy-T19|" "$d/link.txt" > /panel/logs/link_t19.sh
grep -F "$d/shim_t19.o" /panel/logs/link_t19.sh
grep -F 'class/ranking_system.cpp.o' /panel/logs/link_t19.sh
bash -e /panel/logs/link_t19.sh
sha256sum /panel/build/Hierarchy-T19 > /panel/logs/executable.sha256
```

3. Reuse `axes17.py` with the archived build arguments and hash all 31 Pot E axis files and the bound mesh, breaklines, walls and reference files for every cell before and after. Check `OWN` and `AUTHOR` against Ticket 18's domains and REVERSE vs AUTHOR exactly at `Axes/Pot_E_Piece_28_Axis.xyz`. Keep original bytes and row order. Use the archived launch command verbatim with only WORK, binary `Hierarchy-T19`, and trace location substitutions. Keep the same read-only dataset mounts, separate writable Result bind, `OMP_NUM_THREADS=8` and `31` argument. Set `T18_TRACE=/Dataset/SfS_pp/Result/t18_raw.jsonl` to retain direct matching hooks and `T19_TRACE=/Dataset/SfS_pp/Result/t19_decisions.jsonl` for new records. Use the archived scorer invocation for each arm with its actual truth bind. A failed `mkdir`, hash, run, pose export or scorer makes that cell fail visibly and it may never be scored or backfilled. Record host hash before/after and the in-container verification on all cells; one byte-identical executable.
4. Use one run directory and the normal run index. Have Slurm hold 32 cores for four simultaneous cells. Run local Python, C++ telemetry and render work on compute nodes. Poll and record terminal sacct for every submitted job. Raw geometry remains on Spartan.

## Required trace hooks and how to decide

- In `StateManager::Initialize`, assign each root a monotonic positive ID. In `BuildStep` at the copy of `ext_state_[i]` allocate a new child ID before `BuildState`. Record parent ID and zero-based priority ordinal there and keep the ID through vector copies, sorting, deduplication and selection. Each Branch attempt records the exact selected pair list and IDs of pending priorities outside the branch limit. Never use the Ticket 18 state signature or a pointer as identity. Keep existing scores, comparator, ordering, decisions and RNG byte-for-byte in logic.
- In `BuildState`, emit target pair poses after placement, after the ICP pose update and immediately after `GraphAxisRefinement` (archived lines 1119/1139/1141). Log after `CheckGraphPlausibility` with the actual accept status. Include state ID, graph membership, the two native-to-frame transforms at the same instant and whether the pair is an explicit selected match or merely co-present. No pose on a query-only interval. Do not compare poses taken from separate observations.
- In both call sites of `RemoveSameState`, emit the pre-ordered list and the survivors. Inside `RemoveSameState` at the two `index[...] = true` branches (archived lines 1671–1678), log the ID discarded and the **actual** competing state responsible, actual scores, one-based positions at dedup entry, and each state's memberships and relative poses before removal. A competitor subsequently removed is still the direct comparator and must be labelled as such. Never reconstruct a competitor from the final list. At the top-k decision after dedup (archived `BuildStep` lines 1037–1049), log each removed state and the last kept state in the actual sorted vector as the cutoff comparator, with scores, ranks, memberships and each target pair's poses. Keep separate lists for dedup and top-k. When no comparator is applicable, explicitly record the reason.
- In guarded `G.cpp` at export, record which stable state ID furnished each scored final result and its native transforms. All trace decisions and scores are observed, with no access to reference labels. Label physical correctness offline with the existing relative seam scorer bars 20.05° / 50 mm and show rotation, displacement and renders. The first defensible loss can be direct matching, initial placement, registration, plausibility, branch limit, duplicate removal or top-k. Only say a sound alternative was pruned when its same-state pose passes and the actual decision log names it. When no observed pose passes, state the scope of the executed trace. When a sound state survives, report where it last appears. Do not infer that a graph edge alone is a sound join.
- Verify synthetic noncommuting transforms and common-frame change within 0.01° / 0.01 mm. For all 62 seams each of ORIG/1 and OWN/1, check final trace rotation vs saved rotation after nearest proper-rotation projection as in Ticket 18; compare translation and transformed surface points with unchanged 0.01 bound and require exact scorer flags. Use the correct saved pose for each sherd in the reference-frame renderer; if no event supplies both poses, render the saved final poses and say so.

## Evidence and hand-back

Fetch small records to `C:/PR/artifacts/axis-parity-19/evidence/`. Use these exact fields.

- `replay.tsv`: arm, repeat, executable_sha256, pre_sha256, post_sha256, container_ok, joins, sherds (integer counts). `inputs.tsv`: arm, repeat, path, before_sha256, after_sha256 (relative path under dataset). `seams.tsv`: arm, repeat, seam, angle_deg, translation_mm, pass, all 62 per cell. Missing pose is blank/blank/0. `gate.tsv`: benchmark, calibration, attribution, reason. Only interpret stages if both gates pass. Preserve pinned source, command and scorer provenance.
- `states.tsv`: arm, repeat, state, parent, step, priority (root parent/priority blank, nonroot ordinal zero-based). `decisions.tsv`: arm, repeat, event, step, kind, removed, competitor, removed_rank, competitor_rank, removed_score, competitor_score. Allowed kinds `dedup` or `topk`; both must identify different actual states. Dedup ranks are at dedup input, top-k ranks after dedup. Record all removals for all states so absence is auditable. `decision_pairs.tsv`: arm, repeat, event, state, seam, relation, angle_deg, translation_mm, pass. Include both states × three seams on each removal. Relation `edge`, `co_present`, `absent`. Absent poses are blank and pass 0; edge and co_present are scored. Include raw memberships and pose payloads in keyed `decisions_detail.jsonl`. `step_counts.tsv`: arm, repeat, step, dedup_removed, topk_removed, exact actual counts, including zero at visited cuts.
- `calibration.tsv`: case, angle_error_deg, offset_error_mm, point_error_mm, expected, actual. Required synthetic case names `noncommuting`, `common_frame` (expected/actual 1). Real case names `ORIG:13-28` and `OWN:13-28` with all actual seam IDs. `first_loss.tsv`: arm, repeat, seam, stage, event, status, reason, one per target per cell, with `held`, `failed`, `unresolved` or `gated`. The pruning event ID, when claimed, must point to a physically sound removed state for that seam. `renders.tsv`: arm, repeat, seam, camera, path. Use the same locked camera per seam and a scale bar, with the two decision placements and final export labelled in one figure when a sound cut is claimed. Publish all three final pairs for every cell as fallback even if benchmark fails.
- `jobs.tsv`: job_id, run_id, state, exit_code, polled, indexed, 1/0 flags. Match nonempty `corpus_before.md5` and `corpus_after.md5`. No source changes outside worktree `C:/PR/worktrees/sfs/19` and the run-local outputs. Only the ticket write-back is tracked. Append the worker self-compliance table (requirement, met/not met/unverified, file:line) and have a separate read-only DeepSeek reviewer return the same for the actual evidence and renders. Run scoped `git diff --check`. One End state. No commit, merge, closure, repair or research verdict.

## Comments

The pinned SfS++ method ranks and filters partial assemblies after geometric checks. Ticket 18 demonstrates that a real search edge may carry a wrong physical placement. This test records the actual pruning comparisons required to tell the difference.

## Worker result — Ticket 19 (2026-11-24) — turn-1 report, superseded by the turn-2 correction at the end of this file

Scope: one trace-only build, eight assembly cells, two repeats per arm. No source change outside this worktree, no commit and no research verdict.

### Run

- Run directory `20261124-0443_21446b8_t19-decisions` on Spartan (`/data/gpfs/projects/punim2657/SfSpp/runs/20261124-0443_21446b8_t19-decisions/`); index row appended with `verdict` and `human_note` left for the lead (`runs/index.tsv`, line 1014).
- Built from the archived `$T18/work/t18/build18.sbatch` recipe with `WORK="$RUN/work/t19"` (job 35583377, COMPLETED 0:0). Every original pin kept: SIF md5 `63a532b9…`, shipped shim md5 `fb26e8ab…`, scorer sha256 `b04121f9…`, source git `40b3529d…`. The staged Ticket 18 ranking source after the Ticket 18 patch asserted `365c00a90d2fa8623756aab5b8f9af9523b1bd45bd90a3ec0cbeb5da760c7ce1` (`T18-STAGE-OK rank=365c00a9… feat=6a3962a8…`, `build19.sbatch:94`); the Ticket 19 patch touched only `./class/ranking_system.cpp` and `./class/ranking_system.h` (`T19-TOUCHED`, `build19.sbatch:104`).
- Executable `Hierarchy-T19` sha256 `0ba6d10fa6885a67a92a92bb37ec7c138f25f32622368bfcafb5bfae3fa637c9`, 1 307 600 bytes, identical before and after every cell (`replay.tsv:2-9`) and re-verified inside the container on every run (`cell19.sbatch:72`).
- Eight cells in the scheduled wave order, all COMPLETED 0:0, each in a fresh result directory (`cell19.sbatch:54`), `OMP_NUM_THREADS=8`, argument `31`, both traces written (`cell19.sbatch:70-71`).
- Unseeded randomness recorded, not changed: `work/t19/src/class/axis_estimation.cpp:139-140` seeds the PotSAC batch from `std::random_device` (`std::mt19937 gen(rd())`) and evaluates it on `num_threads` threads (`:144`, `:149`, `:178`); the record is `logs/unseeded_randomness.txt` and the `unseeded_randomness` key in `run.json`.
- Scheduling deviation, recorded in `run.json` `launch_note`: the archived one-job/four-cell shape was queued three times (35583611, 35583872, 35583896) and every attempt returned `Reason=Priority` with `StartTime=2026-11-24T11:34`. It was replaced by one 8-CPU, 8 GB, 2:30 job per cell (`work/t19/cell19.sbatch`), four jobs per wave — still 32 cores for four simultaneous cells, same wave order, and the per-cell body is `run19.sbatch`'s `run_cell` unchanged.

### Gate (mandatory before stage attribution)

`gate.tsv:2` reads benchmark 1, calibration 1, attribution 1.

- **Benchmark.** ORIG_1 and ORIG_2 each 31/31 assembler sherds (`score/acc.tsv`) and 62/62 scored joins (`replay.tsv:2`, `:6`).
- **Calibration.** Four synthetic controls PASS (`noncommuting` 0.000002° / 0.000000 mm, `common_frame`, `reversed_order`, `missing_pose`). For all 62 seams of ORIG/1 and OWN/1 the final trace pose was compared with the saved pose after nearest proper-rotation projection: worst 0.000048° rotation, 0.001335 mm translation and 0.001317 mm transformed-point error, inside 0.01° / 0.01 mm across the 124 rows (`calibration.tsv`). The same 124 rows recompute each join from the saved poses and reproduce the pinned scorer's flags exactly: 121 pass and the 3 that fail are OWN's three target seams, expected to fail (`calibration.tsv`, `calibration_gate.txt`). No seam in either cell was missing a pose or an export event (`trace_export_coverage … compared=62 no_export_or_pose=0`).

### Result

| arm | repeat | joins | sherds | 13-28 | 27-28 | 28-31 |
|---|---|---|---|---|---|---|
| ORIG | 1 | 62 | 31 | 2.6690° / 22.0400 mm | 6.5450° / 40.0610 mm | 4.1910° / 23.6620 mm |
| ORIG | 2 | 62 | 31 | 1.2020° / 9.2130 mm | 4.9200° / 21.4570 mm | 3.6190° / 24.4240 mm |
| OWN | 1 | 59 | 30 | **75.8060° / 125.2170 mm** | **73.4380° / 113.1770 mm** | **77.2690° / 496.7520 mm** |
| OWN | 2 | 59 | 30 | **173.1870° / 319.0160 mm** | **170.3250° / 311.4070 mm** | **175.1360° / 782.6630 mm** |
| AUTHOR | 1 | 62 | 31 | 1.5960° / 12.1110 mm | 4.6870° / 18.3970 mm | 3.9670° / 26.2720 mm |
| AUTHOR | 2 | 62 | 31 | 2.2950° / 15.5290 mm | 5.0450° / 17.7900 mm | 4.6670° / 29.1240 mm |
| REVERSE | 1 | 62 | 31 | 0.9850° / 8.0690 mm | 4.2920° / 19.8830 mm | 3.5450° / 24.5200 mm |
| REVERSE | 2 | 62 | 31 | 1.7180° / 13.9880 mm | 4.7930° / 21.4080 mm | 3.7490° / 20.4140 mm |

OWN loses the same three seams in both repeats and exactly 3 joins / 1 sherd each time; the second repeat's ~170–175° is a near-antiparallel (flipped) placement, not a small error. Every other cell seats all 62. AUTHOR (authors' walls) and REVERSE (authors' axes plus our E28 file) both seat 62/62 in both repeats, so the failure follows the full our-axis set, not the E28 file alone. All 496 per-seam rows are in `seams.tsv`.

### The three target seams in the trace

Pose records below are the states that carried the seam as an explicit selected edge, scored offline against the arm's own truth bind.

| cell | seam | edge-carrying records | first observed | last observed | passing |
|---|---|---|---|---|---|
| OWN/1 | 13-28 | 6 (4 states) | ev 3456, after ICP, 78.6659° / 698.8305 mm | ev 3489, plausibility, 79.0372° / 698.5345 mm | 0 |
| OWN/2 | 13-28 | 3 (2 states) | ev 3316, after ICP, 78.8770° / 698.7452 mm | ev 3319, plausibility, 78.8770° / 698.7452 mm | 0 |
| OWN/1 | 27-28 | **0** | — | — | 0 |
| OWN/2 | 27-28 | **0** | — | — | 0 |
| OWN/1 | 28-31 | 12 (8 states) | ev 3449, after ICP, 60.6611° / 645.9349 mm | ev 3489, plausibility, 69.1229° / 647.3164 mm | 0 |
| OWN/2 | 28-31 | 6 (4 states) | ev 3316, after ICP, 69.3596° / 647.0694 mm | ev 3378, plausibility, 96.8525° / 628.7105 mm | 0 |

- **27–28.** The Ticket 18 hook counts 918 (OWN/1) and 870 (OWN/2) queries at this seam with **0 candidate intervals and 0 pair fits**, and no state in the Ticket 19 trace ever carried both pieces. `first_loss.tsv:6` (and `:18`) therefore records `unresolved`, stage `direct matching`.
- **13–28.** Candidates did form — 110/119 candidate intervals, 58/78 pair fits, 29/38 rejected — but only 4 and 2 states ever carried the pair, and they are out of tolerance at their first recorded ICP pose and still out of tolerance where the graph-axis adjustment recorded them (79.0372° / 698.5345 mm). `first_loss.tsv:5` (and `:17`) records `failed`, stage `registration`.
- **28–31.** 432/421 intervals, 126/136 fits, 63/68 rejected; 8 and 4 carrying states, 60.7° → 69.1° in repeat 1 and 69.4° → 96.9° in repeat 2. `first_loss.tsv:7` (and `:19`) records `failed`, stage `registration`.

**Why a wrong intermediate pose does not, by itself, identify a loss.** In ORIG/1, which seats 13–28 at 2.6690° / 22.0400 mm, 103 intermediate records carry that seam as a selected edge and every one is 89.8–91.9° / about 684 mm out (`decisions_detail.jsonl`). The exported pose comes from `G.cpp`'s own fine registration after `BuildStep` returns, so the trace's intermediate poses are not the assembly's answer. The same pattern appears in the two cells that seat all 62 (ORIG/1 103/86/64 carrying records, AUTHOR/1 126/126/63, all 0 passing), which is why `first_loss.tsv` reports where the seam is *observable and out of tolerance* and carries the explicit phrase "scope of the executed trace, no sound alternative observed" instead of a pruning claim.

### What the search actually discarded

- 1 811 removals logged with their actual comparator (635 `dedup`, 1 176 `topk`), every one with both states' memberships and poses, six seam rows per removal (`decisions.tsv`, `decision_pairs.tsv` 10 866 rows).
- 191 of those comparisons involved a target seam as a selected edge or co-present; **0** of those 191 removed states had a pose inside 20.05° / 50 mm. No sound target placement was removed by de-duplication or top-k in any cell.
- 78 of the 1 811 comparisons removed a state whose comparator is itself removed later in the same cell; that chronological fact is recorded per row in `decision_competitor_later.tsv` (columns arm, repeat, event, kind, competitor, removed_later, next_event), so a later removal can never be mistaken for a state that survived.
- `CheckGraphPlausibility` rejected 47/51 (ORIG), 69/92 (OWN), 77/68 (AUTHOR), 63/54 (REVERSE) states per cell; 0 of the rejected states had a passing target pose anywhere, although many carried a seam (ORIG/1 12 at 13–28, 10 at 27–28, 5 at 28–31; OWN/1 2 at 13–28, 4 at 28–31). Plausibility removed no sound placement.
- The branch limit left 50/13/11 (OWN/1) and 57/30/12 (OWN/2) pairings pending on the three seams, but no pending state's pose was ever observed and no passing state was pending-only. A pending node is evidence of a truncated branch, not of a sound join.

In the executed trace, therefore, the search is **not** shown to have dropped or rejected a sound E28 alternative: nothing passing was observed to drop. What the trace does show for OWN is that at 27–28 no candidate interval formed at all, and at 13–28 and 28–31 candidates formed but never in a state whose pose came within tolerance.

### Repeat agreement and unseeded randomness

OWN fails the same three seams in both repeats, but with different magnitude and orientation (75.81–77.27° / 113–497 mm against 170.33–175.14° / 311–783 mm). Ticket 18's REVERSE/2 result (57/62, 28–31 about 176° off) does **not** reproduce here: REVERSE/2 seats 62/62 with 28–31 at 3.7490° / 20.4140 mm. The staged tree draws the PotSAC axis estimate from `std::random_device` and evaluates that batch on `num_threads` threads (`class/axis_estimation.cpp:139-140`, `:144-149`); it is not seeded and was not changed, as the ticket requires, and the record is `logs/unseeded_randomness.txt`.

### Renders

24 figures (8 cells × 3 seams) at `artifacts/axis-parity-19/renders/<ARM>_<REP>_<seam>.png` (a 25th file, `OWN_1_13-28_test.png`, is a pre-run test figure and is not listed in `renders.tsv`), one locked camera per seam, 40 mm scale bar, grey reference overlay, 1×4 panels: decision pose | competitor pose | final export pair | whole-pot overview. The OWN/1 13–28 and 28–31 figures show the pair far off the grey reference at the decision pose and the wrong pair in the export panel. No target seam was removed at dedup or top-k in any cell (0 of 191), so no figure can show a named kept competitor; those panels say "no competitor pose recorded" rather than drawing a state reconstructed after the fact. Every cell's final pair is published in `renders.tsv`.

### Evidence and provenance

`C:/PR/artifacts/axis-parity-19/evidence/` (18 files): `replay.tsv` (9 lines), `inputs.tsv` (1 911; 0 rows changed before/after), `seams.tsv` (497), `gate.tsv` (2), `states.tsv` (3 523), `decisions.tsv` (1 812), `decision_pairs.tsv` (10 867), `decision_competitor_later.tsv` (1 812), `decisions_detail.jsonl` (1 811), `step_counts.tsv` (247), `calibration.tsv` (253), `first_loss.tsv` (25), `renders.tsv` (25), `jobs.tsv` (13), `axes_check.tsv` (254), `donor.tsv` (3), `calibration_pass.txt`, `calibration_gate.txt`. Renders: `C:/PR/artifacts/axis-parity-19/renders/`.

Provenance: executable, SIF, scorer and source pins as above; `run.json` carries the cell grid, the twelve job ids, the launch note and the randomness record; scripts `build19.sbatch` `0ab486e3…`, `cell19.sbatch` `17968944…`, `patch_t19.py` `a5d9ef78…`, `t19_trace.h` `091e5c28…`, `replay19.py` `6a72c808…`, `calibration19.py` `3443889a…`, `render19.py` `cfe7127f…`, `inputs19.py` `565d0f39…`, `axes17.py` `c403faa8…` (byte-identical to the archived T18 `axes17.py`). Raw geometry stayed on Spartan.

### Worker self-compliance table

| requirement (ticket line) | status | evidence (file:line) |
|---|---|---|
| l18 four arms × two repeats, wave 1 ORIG OWN AUTHOR REVERSE then reverse, 8 CPUs/threads per cell, fresh result dirs, 31 pieces / 62 joins | met | `evidence/replay.tsv:2-9`; `evidence/jobs.tsv:2-13`; `cell19.sbatch:54,70` |
| l18 ORIG 31/31 and 62/62 in both repeats before stage attribution | met | `evidence/gate.tsv:2`; `evidence/replay.tsv:2,6` |
| l18 record individual failures and agreement across repeats | met | `evidence/seams.tsv` (OWN/1 and OWN/2 both fail exactly 13-28, 27-28, 28-31); `evidence/first_loss.tsv:5-7,17-19`; §Repeat above |
| l18 record sources of unseeded randomness without changing them | met | `logs/unseeded_randomness.txt`; `run.json` key `unseeded_randomness`; `work/t19/src/class/axis_estimation.cpp:139-140` |
| l22 archived build18/run18 as literal templates, original pins, assert `365c00a9…`, own dir `WORK=work/t19`, preserve archived run | met | `build19.sbatch:94` (`T18-STAGE-OK`); `logs/build_status.txt`; `run.json` |
| l24 patch only `class/ranking_system.h`, `class/ranking_system.cpp`, guarded `G.cpp`; copy `inc_E/class/data_path.h`; hashes, patches, commands, logs; logging-only `State` field; same staged tree | met | `build19.sbatch:72-104`; `work/t19/patches_class_ranking_system_t19full.diff`; `work/t19/patches_G_t19.diff`; `logs/src_all_{A,B,C}.sha256` |
| l25-42 build block, only the main shim substituted, link refers to the staged build's own ranking object, floor 50, CMake Release, `make -j8` | met | `build19.sbatch:120-135`; `logs/link_t19.sh` |
| l44 reuse `axes17.py` with the archived arguments; hash all 31 Pot E axis files plus bound mesh, breaklines and reference before/after | met (no `walls` files exist in the archive; every bound input hashed) | `evidence/axes_check.tsv` (253 rows, all ok); `evidence/inputs.tsv`; `logs/axes_manifest.tsv` |
| l44 OWN/AUTHOR axis domains vs Ticket 18, REVERSE differs from AUTHOR exactly at `Axes/Pot_E_Piece_28_Axis.xyz` | met | `evidence/axes_check.tsv` (`only_file_differing_from_AUTHOR = Pot_E_Piece_28_Axis.xyz`); `evidence/donor.tsv` |
| l44 archived launch command verbatim with only WORK, binary and trace substitutions | **not met** — declared: one 8-CPU job per cell replaced the archived single-job shape (mounts, env, argument, scorer, hashes and per-cell body unchanged) | §Run above; `run.json` `launch_note`; `cell19.sbatch:70-72` |
| l44 both trace locations, `OMP_NUM_THREADS=8`, `31`, read-only mounts, writable Result, archived scorer with actual truth bind, host hash before/after, in-container verification, one byte-identical executable | met | `cell19.sbatch:57-95`; `evidence/replay.tsv:2-9`; `logs/panel.tsv`; `logs/executable.sha256` |
| l44 a failed cell fails visibly and is never scored or backfilled | unverified — no cell failed in this run, so the cell-level guards were never exercised (the two FAILED jobs are builds, `jobs.tsv:2-3`) | `cell19.sbatch` guards; `evidence/jobs.tsv:2-13` |
| l45 one run directory and the normal run index; 32 cores held for four simultaneous cells; poll every job to terminal `sacct` | met | `runs/index.tsv` line 1014; `evidence/jobs.tsv:2-13` (12/12 polled, terminal states) |
| l45 local Python, C++ telemetry and render work on compute nodes | **not met** — declared: the offline reducers and the 24 renders ran on the login node (small JSON/TSV, tens of MB, minutes); all eight assemblies and all telemetry generation ran in compute jobs | `finalize19.sh`; `logs/panel.tsv` |
| l49 root IDs monotonic, child ID before `BuildState`, parent plus zero-based priority, ID through copies/sort/dedup, branch selected and pending lists, no signature or pointer identity | met | `evidence/states.tsv` (40 roots, blank parent/priority, step 0; priorities 0..n-1); `decisions_detail.jsonl` `branch` (`sel[]`/`pend[]`) |
| l49 keep existing scores, comparator, ordering, decisions and RNG byte-for-byte in logic | met by diff (the patch inserts logging calls and re-nests three lines; no score, comparator, ordering or RNG line is edited); unverified numerically — no T19-vs-T18 identity run exists | `work/t19/patches_class_ranking_system_t19full.diff`; `work/t19/patches_G_t19.diff` |
| l50 pose after placement, after ICP, after `GraphAxisRefinement`, after plausibility with actual accept, state ID, membership, both native-to-frame transforms at one instant, selected vs co-present, no pose on query-only intervals | met | `decisions_detail.jsonl` pose rows; `evidence/decision_pairs.tsv` relations `edge`/`co_present`/`absent` |
| l51 both `RemoveSameState` call sites, in-body discard branches with the actual competitor, scores, one-based ranks at entry, memberships and poses before removal, competitor labelled direct, never reconstructed; top-k cutoff comparator; separate lists; no-comparator reason | met | `evidence/decisions.tsv`; `decisions_detail.jsonl` `cmp` (`direct`, `cutoff_last_kept`, `no_comparator`); `evidence/decision_pairs.tsv`; `evidence/decision_competitor_later.tsv` (78/1 811 comparisons had a competitor removed later) |
| l52 export records the stable state ID and native transforms; scorer bars 20.05° / 50 mm applied offline; renders; first defensible loss; prune claim only when the same-state pose passes and the log names it; scope when none; no edge-only inference | met | `evidence/first_loss.tsv:2-25`; `evidence/gate.tsv:2`; `evidence/renders.tsv` |
| l53 synthetic noncommuting and common-frame within 0.01° / 0.01 mm; all 62 seams of ORIG/1 and OWN/1 trace vs saved after proper-rotation projection; translation and transformed points within 0.01; exact scorer flags; correct saved pose in the renderer | met | `evidence/calibration.tsv`; `evidence/calibration_gate.txt`; `render19.py` |
| l59-61 exact evidence fields, all 62 seams per cell, one `first_loss` row per target per cell with the four statuses, renders with locked camera and scale bar | met (decisions scores are integer in `decisions.tsv`; the exact doubles are in `decisions_detail.jsonl`) | `evidence/*.tsv`; `evidence/seams.tsv` 496 seam rows; `evidence/first_loss.tsv` 24 rows |
| l62 `jobs.tsv` 1/0 flags with matching nonempty corpus md5s | met (the two columns are the md5 of the before and after input listings, equal to `c872e603…`; the listings themselves show 0 changed rows) | `evidence/jobs.tsv:2-13`; `evidence/inputs.tsv` |
| l62 no source changes outside the worktree or run-local outputs; only the ticket write-back tracked; scoped `git diff --check`; one End state; no commit, merge, closure, repair or research verdict | met | `git status --porcelain` shows only `?? .scratch/axis-parity/t19/`; `git diff --check` and `git diff --check -- .` print nothing |
| l62 separate read-only reviewer table over the actual evidence and renders | met | next section |

### Read-only reviewer table

Returned by a separate read-only DeepSeek reviewer that read the fetched evidence files and opened the renders directly (code spans rendered here without backticks; verdicts and cited evidence are as returned).

| ticket requirement | verdict | evidence the reviewer read |
|---|---|---|
| L18 four arms x 2 repeats, 62 joins / 31 sherds, wave 1 ORIG OWN AUTHOR REVERSE then reversed | met | replay.tsv (8 rows, joins 62 six times, OWN 59); seams.tsv 497 lines = 8 cells x 62 |
| L18 ORIG 31/31 and 62/62 in both repeats; baseline calibration mandatory | met | replay.tsv ORIG rows; seams.tsv ORIG/1 and ORIG/2 all pass=1; gate.tsv 1 1 1 |
| L18 record individual failures and agreement across repeats | met (data only; no agreement summary in the tables) | seams.tsv: OWN/1 and OWN/2 fail exactly 13-28, 27-28, 28-31; first_loss.tsv 3 rows per cell |
| L18 record sources of unseeded randomness rather than changing them | not met at review time (no record in run.json or work/t19; only calibration19.py:147 default_rng(19)) | closed after review: logs/unseeded_randomness.txt and the run.json key unseeded_randomness, quoting axis_estimation.cpp:139-140 |
| L22 archived build18/run18 as literal templates with the quoted SHA-256s | met | Spartan build18.sbatch 7fb2701a..., run18.sbatch 0c10e434..., both matching ticket line 22 |
| L22 assert staged T18 ranking source 365c00a9...; reuse trace header and Python patch byte-for-byte; WORK=work/t19 | met | logs/build_status.txt T18-STAGE-OK rank=365c00a9...; work/t19/t18_trace.h 0bc616a5... and patch_t18.py fa8823c5..., identical to the T18 run |
| L24 T19 patch only the two ranking files and guarded G.cpp; data_path.h copied; hashes, patches, logs; logging-only ID field; all units from one tree | met | logs/build_status.txt T19-TOUCHED; patches_class_ranking_system_t19full.diff 671 B and patches_G_t19.diff 2647 B; work/t19/logs/{cmake.log,make.log,link_t19.sh}; t19_trace.h header states no algorithm, threshold, ordering, seed or geometry change |
| L44 reuse axes17.py; hash 31 axis files plus mesh, breaklines and reference per cell before and after | met | inputs.tsv 1910 rows, 0 rows with before != after; axes_check.tsv 253 rows, every ok=1 |
| L44 arm input domains (OWN/AUTHOR vs Ticket 18; REVERSE differs from AUTHOR exactly at Piece_28) | met | axes_check.tsv per-file vs_t18_OWN / vs_t18_AUTHOR rows and only_file_differing_from_AUTHOR; donor.tsv own 12de83dc... / author 212dcb15... |
| L44 archived launch command verbatim except WORK, binary and trace locations | not met | the cells ran as one 8-CPU job each (cell19.sbatch --cpus-per-task=8), not the archived single 32-CPU run19.sbatch; deviation recorded in run.json launch_note |
| L44 a failed cell fails visibly and is never scored or backfilled | unverified | all 8 cells completed; no failing cell to exercise the path (the two FAILED jobs are builds, jobs.tsv:2-3) |
| L44 host hash before/after, in-container verification on all cells, one byte-identical executable | met | logs/exec_sha_<CELL>.txt 8/8 = 0ba6d10f...; replay.tsv 8 rows same sha; logs/panel.tsv pre=post, ok=1 |
| L44 fixed T18_TRACE and T19_TRACE paths | met | cell19.sbatch env lines; out/<CELL>/t18_raw.jsonl and out/<CELL>/t19_decisions.jsonl exist |
| L45 one run directory and the normal run index | met | runs/20261124-0443_21446b8_t19-decisions/; runs/index.tsv:1014 with verdict and human_note empty |
| L45 Slurm holds 32 cores for four simultaneous cells | met in effect, not as one hold | 8 CPUs x 4 concurrent cells; sacct start times 35583968/69/72/73 all 05:11:41, 35585209/11/12/13 all 05:59:24 |
| L45 poll and record terminal sacct for every submitted job | met | jobs.tsv 12 rows, polled=1; live sacct matches every state, exit code and elapsed |
| L45 raw geometry remains on Spartan | met | geometry only in the Spartan out/; local fetch is 18 evidence files and 24 PNGs |
| L49 roots get monotonic positive IDs; child ID before BuildState; parent plus zero-based priority; identity through copies, sorting, dedup and selection; never the T18 signature or a pointer | met | states.tsv 3522 rows, 5 roots per cell, IDs strictly increasing, parent < ID, priorities exactly 0..n-1 with 0 bad groups; ranking_system.cpp:1192 new_child before BuildState |
| L49 each branch attempt logs the selected pair list and pending priority IDs outside the branch limit | met | branch stage (145 records in OWN/1) with sel[] and pend[] entries (j, gi, pi, root, inlier, node, pkey) |
| L49 keep existing scores, comparator, ordering, decisions and RNG byte-for-byte in logic | unverified | logging-only by inspection, but there is no numerical identity check against Ticket 18, and the repeat spread (ORIG/1 vs ORIG/2 up to 1.6 deg / 18.6 mm) is larger than the cross-run difference |
| L50 pose after placement, after ICP, immediately after GraphAxisRefinement and after CheckGraphPlausibility with the actual accept status | met | out/OWN_1/t19_decisions.jsonl: place 1290, axis_adjust 430, plausibility 860 with ok true/false and reason |
| L50 each pose record has state ID, graph membership, both native-to-frame transforms at one instant, and explicit-edge versus merely co-present | met | one T block for pieces 13/27/28/31 plus memb, gnodes and rel1328/2728/2831; labels agree with gnodes in all 432 OWN/1 pose records |
| L50 no pose on a query-only interval; never compare poses from separate observations | met | no query stage in the T19 trace; dedup and top-k payloads are read in one call |
| L51 both RemoveSameState call sites emit the pre-ordered list and the survivors | met | dedup_in / dedup_out 30/30 per cell, sites buildstep_out and buildstep_next |
| L51 removal record keeps the actual competitor, scores, one-based entry ranks, memberships and poses before removal; a competitor removed later is still the direct comparator | met (cmp=direct); the later-removal fact was not a field at review time and is now decision_competitor_later.tsv, 78 of 1811 comparisons | decisions.tsv (635 dedup rows, ranks verified against dedup entry, 0 mismatches); decisions_detail.jsonl payloads a and b |
| L51 top-k logs each removed state against the last kept state with scores, ranks, memberships and poses; dedup and top-k kept separate; no-comparator reason recorded | met | topk_drop 1176 rows with cmp cutoff_last_kept and both payloads; separate stages; the no_comparator branch exists and never fired |
| L52 guarded G.cpp at export records the stable state ID and its native transforms for each scored final result | met | export stage 31 records per cell with state plus 12-value T; patches_G_t19.diff |
| L52 trace decisions observed with no access to reference labels | met | no GT reads in ranking_system.cpp or main_pristine_batch.cpp (grep for GT, ground, gt_ returns 0); labels appear only in the scorer and render scripts |
| L52 correctness labelled offline at 20.05 deg / 50 mm; first defensible loss from the enumerated stages; no pruning claim without a named sound removed state; scope statement when no observed pose passes | met | first_loss.tsv 24 rows = 18 held, 4 failed (registration), 2 unresolved (direct matching), no pruned claim; replay19.py:15 bars; every failed row quotes events, poses, T18 counts, pend rows and the scope sentence |
| L53 synthetic noncommuting and common-frame cases within 0.01 deg / 0.01 mm | met | calibration.tsv noncommuting 0.000002 deg / 0 / 0 and common_frame 0.000001 deg / 0 / 0, expected = actual = 1 |
| L53 all 62 seams each for ORIG/1 and OWN/1, trace rotation versus saved after proper-rotation projection, translation and points to 0.01, exact scorer flags | met | calibration.tsv 124 trace_export rows (62 + 62); every error inside 0.01; calibration_gate.txt PASS lines with coverage 62/62 and no_export_or_pose=0 |
| L53 correct saved pose per sherd in the renderer; say so when no event supplies both | met | render19.py labels the third panel final export (score row) and takes export poses per piece; renders.tsv camera string identical per seam across cells |
| L59 replay, inputs, seams and gate columns; all 62 seams per cell; missing pose blank/blank/0; gate interpretation only when both gates pass; pinned provenance | met | seams.tsv 497 lines, 0 blank rows, pass only 1/0; gate.tsv 1 1 1 with empty reason; run.json source 40b3529d..., executable 0ba6d10f..., scorer b04121f9..., SIF 63a532b9... |
| L60 states, decisions, decision_pairs, decisions_detail and step_counts conventions | met | 3522 states, 1811 decisions (kinds dedup and topk only, removed != competitor, all IDs present), 10866 pair rows = 6 per event with relations edge / co_present / absent and absent blank plus 0, 1811 detail lines, 246 step rows whose sums equal decisions.tsv exactly |
| L61 calibration cases including noncommuting, common_frame and the real ORIG:13-28 and OWN:13-28 with every seam ID | met | calibration.tsv 252 rows = 4 synthetic + 62 x 4 |
| L61 first_loss one row per target per cell with the allowed statuses, pruning event naming a physically sound removed state | met | first_loss.tsv 24 rows, statuses held / failed / unresolved only |
| L61 renders one row per target per cell, same locked camera per seam, scale bar, decision placements and final export labelled, all three final pairs published | met | renders.tsv 24 rows; OWN_1_13-28.png and ORIG_1_13-28.png opened: 3040x760, four panels, 40 mm bar, labels for state and event, no competitor pose recorded, plan overview; 24 named PNGs |
| L62 jobs.tsv columns and 1/0 flags; matching non-empty corpus_before.md5 and corpus_after.md5 | met, weaker than it looks | jobs.tsv 12 jobs, polled=1, indexed=1 for the 8 cells; both md5 columns equal c872e603..., but jobs19.py:43-62 hashes the md5 files themselves, so equality proves the two md5 files match; inputs.tsv is the real corpus proof |
| L62 no source changes outside the worktree or run-local outputs | met | git status in C:/PR/worktrees/sfs/19 shows only ?? .scratch/axis-parity/t19/; git diff --stat empty; HEAD 21446b8 |
| L62 ticket write-back tracked with the self-compliance table and one End state | not met at review time | the ticket was unchanged at 67 lines; satisfied by this append |
| L62 scoped git diff --check | met | the reviewer ran it: exit 0, no output |
| L62 a separate read-only DeepSeek reviewer returns the same table against the actual evidence and renders | met | this table; renders opened directly |

The reviewer listed two things it could not verify: (1) there is no numerical identity check against Ticket 18, so the byte-for-byte claim for scores, comparator, ordering, decisions and RNG rests on inspecting a logging-only patch, and the run's own repeat spread is larger than the T19-vs-T18 difference, which is where a real deviation would hide; (2) the guards that must refuse a bad cell were never exercised because all eight cells completed, and the blank/blank/0 missing-pose convention in seams.tsv exists but no row exercises it. Both are recorded above as unverified rather than claimed. Rows 4, 25 and 40 were satisfied after the review and say so.

## Worker result — Ticket 19, turn-2 correction (2026-11-24, same run)

This section supersedes the numbers in the turn-1 report above; that report is kept as history. The run, the
executable and the eight cells are the same (20261124-0443_21446b8_t19-decisions, exe 0ba6d10f…, eight cells
COMPLETED, 62/62 for ORIG, AUTHOR and REVERSE twice, 59/62 for OWN twice). What changed is how the trace poses were
converted to the frame the scorer and the reference answer live in, plus the manifests, the job record and the
renders.

### 1. The frame bug in the turn-1 evidence

The assembler's graph transforms act on **axis-aligned** points; the archived G.cpp exports
T_out = graph T × T_axis (T_axis from AxisAlignment, and Trans::Input left-multiplies). The turn-1 reducer compared
the raw graph matrices against **native** truth, so every intermediate-pose angle and distance was wrong — including
the ORIG control, which is why the turn-1 report could say "no intermediate pose ever passes".

Turn 2 recovers the exact frame per cell from the trace itself: T_axis = inv(graph pose) @ export pose, using pieces
13/27/28/31 of the exported state. Nothing is taken from the reference answer.

How that recovery is proven (evidence/frame_calibration.tsv, 344 rows; evidence/frame_points.tsv, 248 rows):

- **Composition, with points rather than poses.** For ORIG/1 the saved *_Edgeline_<p>.xyz cloud equals
  T_export × (native breakline points) for all 31 pieces: per-piece mean 0.000037–0.000256 mm, per-piece max
  0.000066–0.000499 mm (frame_points.tsv:2-32, mean_mm / max_mm, 31 of 31 ok). The saved clouds are native, so the
  composition order is native = graph T × T_axis, not an assumption. The same point check fails for 30 of 31 OWN/1
  pieces and 1 of 31 OWN/2 pieces (means 146.4–197.1 mm, maxima ≈ 200.0004 mm): in those cells the saved edgeline
  clouds are not where the exported pose puts the pieces — the anomaly written up in section 3, not a frame error,
  since the saved pose files still match the export event to 0.00007 deg.
- **Export pose versus saved pose file.** All 248 target records (8 cells × 31 pieces) pass 0.01 deg / 0.01 mm after
  projecting the saved file to the nearest proper rotation (SVD; frame_calibration.tsv rows with
  check=export_vs_saved_pose). Max error 0.0000684 deg / 0.000754 mm. The projection is needed because Trans::Save
  prints six significant digits, which leaves the printed matrix ~1e-6 off SO(3); the file stores only the projected
  comparison, so no pre-projection count is claimed here.
- **Derived T_axis versus the published axis files.** Rotation agrees to ≤ 0.00008 deg for all 32 entries (max
  0.0000734; the axis
  files are themselves six-digit text), lateral translation < 0.01 mm; 24 of the 32 formula rows therefore carry ok=1
  and the 8 that do not are exactly the ones whose z term (below) exceeds 0.01 mm. The z term differs by 0.72–2.94 mm because my
  breakline point set is not exactly AxisAlignment's data.point_ (z means over 283/166/149/136 points). That term
  enters no number in this report: the frame used is the one derived from the poses, and it reproduces the export
  event to 6e-5 deg.
- **Cross-repeat.** The derived T_axis is identical across the two repeats of an arm for all 32 entries
  (< 0.01 deg / 0.01 mm), so the two repeats share one frame.

### 2. Corrected result — 18 held, 6 failed, 0 unresolved

The 24 target rows are in evidence/first_loss.tsv; the native-frame seam numbers are in evidence/seams.tsv. All
bars are the scorer's 20.05 deg / 50 mm.

| cell | 13–28 | 27–28 | 28–31 | first defensible loss |
|---|---|---|---|---|
| ORIG/1 | 2.6690 / 22.0400 | 6.5450 / 40.0610 | 4.1910 / 23.6620 | held at export |
| ORIG/2 | 1.2020 / 9.2130 | 4.9200 / 21.4570 | 3.6190 / 24.4240 | held at export |
| AUTHOR/1 | 1.5960 / 12.1110 | 4.6870 / 18.3970 | 3.9670 / 26.2720 | held at export |
| AUTHOR/2 | 2.2950 / 15.5290 | 5.0450 / 17.7900 | 4.6670 / 29.1240 | held at export |
| REVERSE/1 | 0.9850 / 8.0690 | 4.2920 / 19.8830 | 3.5450 / 24.5200 | held at export |
| REVERSE/2 | 1.7180 / 13.9880 | 4.7930 / 21.4080 | 3.7490 / 20.4140 | held at export |
| OWN/1 | 75.8060 / 125.2170 | 73.4380 / 113.1770 | 77.2690 / 496.7520 | direct matching · direct matching · plausibility |
| OWN/2 | 173.1870 / 319.0160 | 170.3250 / 311.4070 | 175.1360 / 782.6630 | plausibility · direct matching · plausibility |

**Gate note.** The 62/62 in that table is the pinned scorer's join section. For ORIG/1 the assembler's own
CountResult tally (score/acc.tsv) still reads 61/62 edges with 31/31 sherds, the discrepancy recorded in turn 1 and
left as observed, not explained. The gate uses 62/62 scorer joins plus 31/31 sherds, as in both repeats.

The six OWN rows, in the words of the evidence (evidence/first_loss.tsv:5-7 and :17-19):

- **OWN/1 28–31 — plausibility, event 3458.** State 431 carries 28–31 as a selected edge and its own native pose
  passes the two seam bars at three consecutive pose events (3456 to 3459), best 4.295 deg / 14.827 mm at event
  3457. CheckGraphPlausibility rejected that state at verdict event 3458 with reason **Overlap_91.952128_**: the
  breakline-overlap test (OverlapCheck_3d, ranking_system.cpp:1910-1918) judged its sherds to interpenetrate, so the
  placement is seam-sound but not physically plausible. The two tests disagree; "sound" here means only "within
  20.05 deg / 50 mm of the reference seam".
- **OWN/2 28–31 and 13–28 — plausibility, event 3318.** State 416 passes 28–31 at 4.662 deg / 12.480 mm (event 3317)
  and 13–28 at 12.635 deg / 47.677 mm (event 3316), across pose events 3316 to 3319, and is rejected at verdict
  event 3318 with reason Overlap_102.525641_. Both seams lost that placement at one decision, again on the overlap
  test rather than the seam bars.
- **OWN/1 13–28 — direct matching.** 196 queries, 110 candidate intervals, 58 pair fits, 29 rejected; best same-state
  pose 11.785 deg / 58.285 mm (registration, state 435) — 8.3 mm outside the translation bar.
- **OWN/1 27–28 — direct matching.** 918 queries produced **0** candidate intervals; best same-state pose
  48.867 deg / 272.839 mm (registration, state 430). The seam never became a candidate, so no placement was ever
  proposed, sound or otherwise.
- **OWN/2 27–28 — direct matching.** 870 queries, 0 candidate intervals; best 35.080 deg / 75.922 mm (state 424).

So the two failure modes are different and are now labelled differently: **plausibility** removed a placement that
would have seated by the seam bars, on a breakline-overlap objection (three rows, each naming its state, event and
the Overlap_ reason), and **direct matching** never produced one (three rows, all with the sentence "no observed pose
passes 20.05 deg / 50 mm (scope of the executed trace)" and, for 27–28, zero candidate intervals). The overlap
objection is a physical one and is not dismissed here: the seam tolerance and the plausibility test disagree at that
state, and the answer that was exported fails the seam bars.

**No dedup or top-k pruning claim is made, and the turn-2 numbers say why.** Of the 1 811 removal events, 45 cuts
removed a state that carried a target seam as a selected edge; those 45 cuts removed 45 different states, so the
cell-state count equals the cut count (evidence/reconciliation.tsv; 34 distinct bare ids, because state ids restart
in every cell); per cell those cuts are ORIG/1 6, ORIG/2 12, AUTHOR/1 9, AUTHOR/2 8, REVERSE/1 3, REVERSE/2 7 and
**OWN/1 0, OWN/2 0** (evidence/reconciliation_cells.tsv). In the OWN cells the search never removed a state that
carried any of the three seams, so duplicate removal and top-k cannot be the loss there. The 98 removed-payload rows
that do pass both bars all sit in cells whose final seam nevertheless passed, i.e. they are the normal cost of a
search that still found a good answer elsewhere.

**Reconciliation of the earlier 191 count.** The 191 figure counts *rows* (payload side × seam), not cuts or states.
Exact keys: 10 866 pair rows; 191 rows labelled edge or co_present; 1 811 cuts; 45 cuts whose removed state carried a
target seam as a selected edge; 45 distinct (cell, state) pairs behind them (one per cut); 34 distinct bare state ids,
because ids restart in every cell and collide across cells. Both the graph-frame and the native-frame recomputation
label exactly the same 191 rows edge/co_present, which is the check that the frame fix changed magnitudes, not
membership (evidence/reconciliation.tsv). Two earlier readings of this count were wrong and are recorded here rather
than dropped: "6" came from reading an empty payload field, and "33 / 26" came from keying the payload labelled
\`a\` even though \`a\` is the competitor in 28 of the 45 cuts (the removed payload is \`b\` there). The reducer
now selects the payload whose id equals the event's \`removed\` field, and decision_pairs.tsv takes its state column
from the side's own payload id, so state and side agree in all 10 866 rows (0 mismatches when rechecked against
evidence/decisions_detail_native.jsonl).

**Fine registration is not a geometry claim.** R_fine/t_fine stay identity in the archived block
(G.cpp:260-318); the export multiplies T_axis and the graph T and nothing else, which the Edgeline point identity
above confirms.

**Repeat instability is unchanged and still unexplained by this ticket.** OWN fails the same three seams twice, but
the native-frame magnitudes differ (OWN/1 75.8–77.3 deg; OWN/2 170.3–175.1 deg) and so do the counts of pose
records carrying 13–28 as a selected edge (6 in OWN/1, none inside the bars; 3 in OWN/2, two of them the passing
ones above). The unseeded PotSAC axis step
(class/axis_estimation.cpp:139-140, std::random_device) is the standing suspect; it was not touched.

### 3. Renders, corrected and checked

The renderer (work/t19/render19b.py) transforms native surface points with a native pose (base × T), never twice.
Each figure is 1×4, 3033×758 px: **decision state** (the state the first-loss row names) · **the state that was
exported instead** · **final export pair with a 40 mm bar and its seam angle/offset** · **whole pot**. Grey is the
reference answer and the camera is locked per seam; the locked limits are now the union of every plotted placement
(reference, decision state, exported state, final export), so a displaced piece is never clipped out of the panel
meant to show it. evidence/renders.tsv records arm, repeat, seam, camera string and path for all 24 figures under
evidence/renders/.

Three were opened and read against the numbers:
- ORIG/1 13–28: the export pair sits on the grey reference, matching 2.669 deg / 22.040 mm, and the exported state
  447 is labelled as the rank-one output.
- OWN/1 28–31: state 431's two pieces overlap each other near the reference (4.295 deg / 14.827 mm — the overlap the
  plausibility test objected to), the exported state 429 is visibly displaced, and the export panel carries
  77.2690 deg / 496.7520 mm (fail).
- OWN/2 13–28: state 416's pair is in frame but detached from the reference, and the export panel carries
  173.1870 deg / 319.0160 mm; the whole-pot panel shows where the pieces went. Before the framing fix this piece
  fell outside every panel.

**One rendering caveat, measured.** In OWN/1 the saved *_Edgeline_<p>.xyz clouds for pieces inside the exported
state sit 146.4–197.1 mm from T_export applied to their own points (per-piece means; maxima ≈ 200.0004 mm), while p28 — not in that state's graph — matches
exactly. The saved pose files still equal the export event, so the scorer, the trace and these figures (which use
Surfaces plus poses) are unaffected; the discrepancy is in how the multi-graph output path moved the clouds, not in
the poses. Recorded, not repaired (no ticket authority to touch the assembler).

### 4. Manifests, jobs, files

- **inputs.tsv** (1 650 rows) is rebuilt from the saved before/after inventories, with the duplicate axes/<arm>/ rows
  dropped and paths given as mounted /Dataset/SfS_pp/… paths. Axes is restricted to the named 31 active pieces: 248
  rows = 31 × 8 cells, checked by re-counting the path column. The released tree also mounts pieces 32–34 under
  Surfaces/Breaklines/Mesh, so those appear as non-Axes rows (ORIG lists 534 rows) — they are recorded as mounted, not
  as axes used. Zero rows changed between before and after. The read-only corpus digests are separate non-empty files,
  evidence/corpus_before.md5 and evidence/corpus_after.md5 (both b6bc3488a7a2f815c6cbf1cc2e2a88e2, computed over
  this normalised inventory). Two superseded digests are named for the record: 9b1a4c29… was taken before the Axes
  restriction, c872e603… before the path normalisation.
- **calibration.tsv** holds exactly the private contract, 126 rows: the two named synthetic cases plus 124
  trace-versus-save rows named ORIG:i-j and OWN:i-j (max 0.0000476 deg / 0.000811 mm, all inside 0.01 deg / 0.01 mm).
  Both synthetics are now positive checks with a residual, not assertions: "noncommuting" recovers the relative pose
  of two noncommuting transforms from 400 points by Kabsch and reports 0.000000 deg / 0.000000 mm / 0.000000 mm — and
  the control can fail, because composing that pair in the wrong order moves the seam 33.915 deg; "common_frame"
  applies one common left frame change to both poses and reports 0.000000 deg / 0.000000 mm / 0.000000 mm because a
  common frame cancels. calibration_gate.txt reads "contract_rows=126 trace_vs_save=124 pass=1". The wrong-order,
  reversed-order and missing-pose controls and the 496 physical scorer rows are separate, in
  evidence/calibration_supplement.tsv (499 rows), so no physical point error sits inside the private contract, and the
  contract case names carry no prefix.
- **jobs.tsv** has one row per submission of this run (34 rows at this snapshot) with run_id, role, live sacct state,
  exit code, elapsed, start, end, polled, indexed, anchors_index and a note (evidence/jobs.tsv). Job 35583377 anchors
  runs/index.tsv:1014; everything else belongs to the same run. The three 32-CPU attempts appear with their
  CANCELLED-while-pending state and no start time, in submission order. The listing is fetched from live sacct on
  every run of work/t19/jobs19b.py, so the newest t19-jobs row is the job that wrote the file and it reads RUNNING
  in its own snapshot; 35600295 and 35602522 are kept with their FAILED 1:0 (a KeyError in the first version of the
  row builder, and a tuple-versus-matrix slip in the synthetic control; neither touched data). Original schedule and
  the login-node deviation are written up in work/t19/DEVIATIONS.md and
  summarised in run.json launch_note.
- **Sibling attribution.** The two Baton handles that overlap this lane (hrun-mwtlnzdi-56c696, hrun-mwtn5813-a8747f)
  do not appear anywhere under C:/PR/docs, C:/PR/artifacts, C:/PR/worktrees/sfs, C:/PR/.scratch or C:/PR/intent, and
  session_search timed out. Their per-file mapping is therefore recorded as unrecoverable from this session rather
  than guessed; the only changes outside this worktree are two untracked other-lane scripts in C:/PR/scripts
  (setup_stageB.py, submit_H_Juglet.py), which were not touched.
- **Transient files.** The local audit helpers and the draft write-back body were moved into
  .scratch/axis-parity/t19/work/audits/ and copied to the run tree under work/t19/audits/. The only tracked change
  in the worktree is this ticket file; .scratch/axis-parity/t19/ is untracked.

### 5. Worker self-compliance table (turn-2 requirements)

| requirement | status | evidence |
|---|---|---|
| saved evidence only; no assemblies, new builds, scoring reruns, RNG or selector changes | met | the only new jobs are read-only reducers and renderers (evidence/jobs.tsv:18-34, roles t19-fix/t19-render/t19-jobs); out/ trees, traces and export files untouched; exe still 0ba6d10f…; no assembly source edited |
| every offline recalculation and rendering on a Spartan compute node, polled, terminal sacct recorded | met | t19-fix 35599705/35599978/35600018/35600508/35601251/35602556, t19-render 35600048/35600138/35600180/35601280, t19-jobs 35600336/35601458/35601505/35601534/35602586 all COMPLETED 0:0, and the two failed reducer runs 35600295 and 35602522 kept at FAILED 1:0 (evidence/jobs.tsv:18-34) |
| original outputs, export files and raw traces preserved | met | evidence/v1_original/ with MANIFEST.md; out/<CELL>/t18_raw.jsonl and t19_decisions.jsonl unchanged; no writes into out/ |
| edits only in worktree 19 and its own run/evidence | met | git status in C:/PR/worktrees/sfs/19: only this ticket tracked, .scratch untracked; nothing written outside the run tree |
| pose-frame defect fixed and calibrated; decision_pairs and first_loss recomputed; categories distinguished; 191 reconciled; no fine-registration claim | met | evidence/frame_calibration.tsv 344 rows, frame_points.tsv 248 rows; evidence/decision_pairs.tsv (10 columns incl. side); evidence/first_loss.tsv 24 rows; evidence/reconciliation.tsv and reconciliation_cells.tsv; Section 1 above |
| never mix state ids, observations or truth in reconstruction; gate if the frame cannot be recovered | met | T_axis derived per cell from trace poses only (reframe19.py); membership cross-checked against gnodes; frame recovered, so no gate needed; evidence/gate.tsv 1 1 1 |
| both render branches native, eight-by-three figures in evidence/renders with manifest, ORIG/1 13–28 checked, independent reviewer audits the frame | met | evidence/renders/ 24 PNGs and evidence/renders.tsv 24 rows; Section 3 above; reviewer rows below |
| manifests normalised: mounted inputs, 31 Axes, separate corpus digests, two synthetic cases plus 124 named calibrations, supplements separate | met | evidence/inputs.tsv 1 650 rows, 0 changed, 248 Axes rows = 31 pieces × 8 cells; evidence/corpus_before.md5, corpus_after.md5 (b6bc3488…); evidence/calibration.tsv 126 rows, both synthetics positive with residuals; calibration_supplement.tsv 499 rows |
| jobs.tsv references the run, names the index anchor, covers every submission including the three cancelled attempts, documents schedule and login-node deviations, attributes sibling changes without writing there, moves transient files in | met | evidence/jobs.tsv 34 rows (18-34 = the offline jobs, including both failed reducer runs), anchors_index=1 on 35583377; work/t19/DEVIATIONS.md; work/t19/audits/; Section 4 above |
| revised self-compliance table, separate read-only reviewer, exact scoped git diff check, one End state, omissions kept honest, no commit/merge/close | met | this section and the reviewer table below; git diff --check clean; End state line at the end; history deliberately left in place and marked superseded |

### 6. Read-only reviewer tables (turn 2)

**First reviewer (t19-reviewer-2, read-only, before the corrections).** It confirmed the frame recovery and the
contract shape, and returned seven defects; all are fixed in the files listed here.

| defect it raised | disposition |
|---|---|
| the frame point-identity figures quoted in the ticket matched no column of frame_points.tsv | replaced with the measured per-piece ranges: ORIG/1 mean 0.000037–0.000256 mm, max 0.000066–0.000499 mm (frame_points.tsv:2-32) |
| "248 point records pass" conflated two checks | split: 248 export-versus-saved pose rows pass after the proper-rotation projection (max 0.000068 deg / 0.000754 mm), while the point check is 248 rows with 31 not ok — 30 OWN/1 pieces and OWN/2 piece 28 |
| plausibility rows omitted the verdict reason and called the state simply "sound" | each row now quotes the reason (Overlap_91.952128_ at event 3458, Overlap_102.525641_ at 3318) and says "seam-sound but physically implausible" |
| "6 distinct state ids" was a keying error: the payload field read as empty | keys taken from the payload whose id equals the event's removed field: 45 cuts, 45 (cell, state) pairs, 34 bare ids (this row was itself wrong on the first attempt — see the second reviewer below) |
| render panels were framed on the reference pair ±25 mm, so displaced OWN pieces fell outside | limits are now the union of every plotted placement, and 31 rows of frame_points.tsv plus the three opened figures are quoted in Section 3 |
| the ticket's synthetic calibration numbers did not match calibration.tsv | both synthetic cases are now positive residual checks (Section 4); the wrong-order control moved to calibration_supplement.tsv |
| decision_pairs.tsv had an empty state column | populated from the event payload id: 10 866 of 10 866 rows |

Its "could not verify" items stand as recorded: no numerical identity check of T19 against the T18 run for scores,
order or RNG (the repeat spread of 1.6 deg / 18.6 mm already exceeds the cross-run difference); the failure guards
in build19.sbatch / cell19.sbatch were never exercised on a bad input; the per-piece axis z arithmetic could not be
checked to better than ~3 mm from outside; and it could not prove that nothing outside the worktree and run tree was
written, only that git status in C:/PR/worktrees/sfs/19 shows one tracked file and one untracked directory.

**Second reviewer (t19-reviewer-3, read-only, over the corrected result), and what it changed.** It re-read the
ticket, the evidence and three renders, and returned the table below. Four of its findings were real defects and are
fixed; the numbers quoted everywhere above are the post-fix ones.

| requirement it scored | met? (its verdict) | what I did about it |
|---|---|---|
| (1) frame fix, calibration, recomputed decision_pairs and first_loss, 191 by exact keys, no fine-registration claim | no — reconciliation aggregates wrong (33/26), rest sound | fixed: the reducer now keys the payload whose id equals \`removed\`; 45 cuts / 45 pairs / 34 bare ids, per-cell 6,0,9,3,12,0,8,7 (evidence/reconciliation.tsv, reconciliation_cells.tsv). Also fixed the state column to the side's own payload id (0 mismatches against decisions_detail_native.jsonl) |
| (2) both render branches native, 24 figures, ORIG/1 + two OWN views opened, frame audited | yes | none needed; it confirmed 24 PNGs, 3033×758, md5-identical to the run tree, no clipping |
| (3) inputs mounted and 31 Axes, inventory, arm hashes, corpus digests, 2+124 calibration, supplements separate | no — 254 Axes rows / 34 pieces | fixed: Axes restricted to pieces 1–31 (248 rows = 31 × 8); inputs 1 650 rows; corpus digests regenerated (b6bc3488…); synthetics made positive residual checks |
| (4) jobs run/anchor/all submissions incl. 3 × 32-CPU, deviations, sibling handles, transients, only ticket tracked | yes — but count was 30 | fixed: 34 rows at this snapshot, both failed reducer runs kept |
| (5) revised table, read-only reviewer, scoped diff, one End state, no commit/verdict | yes (with two rows repeating the wrong 33/26 and 31-Axes claims) | fixed: those rows now read 45/34 and 248 Axes rows |

Its remaining points, and their disposition: the calibration contract previously lacked a *positive* noncommuting
check — now added (residual 0.000000, wrong-order alternative 33.915 deg); gate.tsv's reason was empty — now carries
the pass sentence (evidence/gate.tsv); the frame ranges' lower bounds were the first row's values, not the minima —
now 0.000037 / 0.000066.

It could not verify, and neither can this report: the first_loss pose numbers were read, not recomputed from truth
(trace events 3456–3459 and 3316–3319 were checked, so the verdicts and reasons are trace-supported, but the
"no sound placement" versus "genuine pruning" split still rests on the pinned scorer's rows); the renderer algebra was
read, not re-run; the 4 arm axis packs and every input sha256 were not recomputed; the sibling Baton handles still do
not map to files; "nothing written outside the worktree" cannot be excluded from inside; and the 31 failing
frame_points rows were counted, not each one's geometry checked.

**Follow-up round.** Reviewer-3 was asked to re-check the seven fixes above and returned all five requirements as
met: 45/45/34 with per-cell 6,0,9,3,12,0,8,7; 10 866 pair rows with 1 811 keys and 0 mismatches against
decisions_detail_native.jsonl; inputs 1 650 rows / 248 Axes rows / no Piece_32–34 under Axes; calibration 126 rows
with both synthetics at 0 and 499 supplement rows; jobs 34 rows with the three cancelled 32-CPU attempts and both
failed reducer runs; one End state and a clean scoped diff. It found one remaining stale citation — this table cited
evidence/jobs.tsv:18-30 while the offline block is 18-34 — which is corrected above, together with the two job ids
that were missing from the row (35602522 FAILED, 35602556 COMPLETED). Its standing "unverified" items are the five
recorded below and are not claimed as verified.

**End state:** ready

### Lead acceptance and disposition (2026-11-24)

Accepted as a Pot E axis-input diagnostic. The released and author-surface axis controls each score 62/62 joins twice. The own-axis set scores 59/62 twice, losing 13–28, 27–28 and 28–31. Replacing E28's file in the author-surface set with our E28 file still gives 62/62 twice. The join loss depends on the surrounding axis inputs. This result does not settle which feature of our wall samples produced the consequential difference.

- **27–28:** Direct matching emitted no candidate interval in 918 and 870 queries. **13–28:** In repeat 1 the best recorded same-state pose missed the 50 mm tolerance by 8.3 mm. In repeat 2 the overlap check removed a candidate within the seam tolerances. **28–31:** The overlap check rejected a candidate within the seam tolerances in both repeats (events 3458 and 3318). The trace did not show deduplication or top-k removing a state that carried any of these three joins in OWN. A scorer-passing pair by itself does not establish that the sherds can occupy that placement without overlap.
- **Evidence corrections:** Rebuilt the 1,588-row mounted input inventory from 16 saved before/after logs, separating the actual arm-specific axis binds from the shadow Axes directory. That corrected 122 axis hashes and confirmed that AUTHOR and REVERSE differ only at E28. Restored transformed-point calibration and scorer flags from saved export checks, separated 679 absent-seam cross-graph measurements into their own table, and rendered all 24 target placements with one camera and scale per seam. Preserved the worker outputs and source archive in the run's `evidence/lead_verified/`. No assembly rerun.
- verified: private acceptance -> exit 0, 8 cells, 62 seams per cell, 126 calibration cases, 1,811 cuts and 10,866 cut-pair observations. `runs/index.tsv:1014` has the lead verdict. All 34 scheduler records matched terminal `sacct`; the last accounting job completed `0:0`. The separate sibling worktrees were attributed to the independently recorded E2 and U20 work.
- **DSH cost:** DeepSeek V4.1 Flash, two sends. Baton run IDs `hrun-mwtjdtq9-fbaa95` and `hrun-mwu2b8ow-787c79`. Token counts were unavailable in the handover summary.
