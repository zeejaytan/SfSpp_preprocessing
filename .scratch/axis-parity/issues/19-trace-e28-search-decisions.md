# 19: Find what happens to a sound E28 placement in the Pot E search

**What to build:** Trace the exact placement the assembler keeps or discards for 13–28, 27–28 and 28–31. Determine whether an out-of-tolerance placement reaches the final assembly because no sound candidate formed, a geometric check rejected it, or the search dropped a sound alternative.

**Answers:** E1
**Blocked by:** None. Ticket 18 closed with direct-matching evidence and an unresolved search decision.
**Status:** in-progress
**Working in:** DSH: SfS++ axis-parity Ticket 19 (2026-11-24) (2026-11-24)
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
