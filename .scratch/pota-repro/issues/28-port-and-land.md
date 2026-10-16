# 28: Port the cure set into the tree, reproduce, land

**What to build:** the landable proof — every staged fix as committed source, reproducing the cure from a repo-built binary.

**Answers:** E1

**Blocked by:** 24, 27 (staged fixes below); 22 (relaxations); 23 (determinism, already committed).

**Status:** results-in — VOID (ORIG control 2/8+1/15 with repo-built binary; pipeline half reproduced, fork search deltas named for lead)

**Starting position:** the cure is proven but lives in Spartan worktrees, not the repo. Port each hunk into the laptop tree with its SFS-T tag and ticket reference, rebuild from the repo state, and reproduce ticket 27's numbers with a repo-built binary:
1. SFS-T24: skip `ticket14_append_patch_rims` for Pot_A_Piece_02 (ticket 24; Spartan worktree `sfs_preprocessing_pota24`, tracked diff = only T24)
2. SFS-T27: extend the skip to Pot_A 03/04/05 (ticket 27; worktree `sfs_preprocessing_pota27` @ 2465a47, +22 lines 1 file)
3. RP overlap-kill ablation (`feature_matching.cpp:1865`, P22FIX) + CheckGraph overlap veto 50→150 (P22FIX2) — both ORIG-validated repeatedly; staged in `sfs_main/sfs_p22fix_src/` (verify diff = prints + P22FIX + P22FIX2 only; port WITHOUT the diag prints)
4. Base already committed: SFS-T21 (wall split), SFS-T23a/b (tmp_path + determinism)

**Rules:** port hunks exactly (no drive-by changes; diag/print lines stay out). Rebuild the pipeline AND the assembly from the repo tree on Spartan (fresh clone/pull to the port commit — no worktree binaries). Same-binary ORIG control in the same job (must reproduce 8/8+15/15 or void). Acceptance: repo-built gate 15/15 + binary 8/8+15/15 + STRICT relative-edges 15/15 (gauge overlay as corroboration, not acceptance).

- [ ] Four hunks ported with tags; diff per hunk in the ticket
- [ ] Repo-built cure run: gate + E2E k=5/b=3, all three bars; ORIG control valid
- [ ] Laptop poll per sbatch (`sacct` directly); seating render + measurement pair; no commits (lead lands the set); Comments-only edits

**Successor:** B–J E2E on admitted fragments (same protocol per pot), then the Juglet question re-opens with a working chain. Note the successor runs on the deterministic pipeline (T23b committed) — bundle-to-bundle comparisons are now signal.

## Comments (worker, 2026-10-16)

**Verdict: VOID — the ORIG control did not reproduce, so no acceptance bar can be claimed. Repo-built pipeline fully reproduces the cure at rim level (gate 15/15, zero teleports, byte-familiar Bl0 sizes); the repo-built assembly binary does not (ORIG 2/8+1/15, fresh 2/8+1/15). Cause named: the structure-from-sherds-pp fork carries live search-behavior deltas vs the upstream tree the cure was proven on. Details below. No commits anywhere; all hunks uncommitted for lead review.**

**0. Hunk verification (per-hunk diffs, all match sources exactly).**
- SFS-T24+T27 (prep): laptop uncommitted hunk `edgeline_extraction_headless.cpp` (+22, blob 28d34bc) is byte-identical to worktree `sfs_preprocessing_pota27`'s committed-diff hunk (same base blob 560f4de). Synced to Spartan two ways: (a) prior worker's fresh clone `pota28_repro/prep` @ a5d9ccd + `pota28_prep.patch` (identical to laptop hunk — diffed, no delta); (b) this worker pulled repo checkout `sfs_preprocessing` 1dd8c1d→a5d9ccd and applied the same patch (diff identical).
- P22FIX (RP overlap-kill ablation, `feature_matching.cpp:1989`): laptop tree already held exactly `if ((iter->score_ > 10)) { // P22FIX: ...` (1 line, no diag prints, no signature change) — matches fix-src's functional line; the P26DIAG print wrappers and `step_counter` signature widening were correctly left out. Synced to `pota28_repro/asm` @ 11f4827 (prior worker) and to repo checkout `sfspreproc-docker` (this worker, after pulling eb6c389→11f4827; 6 colliding untracked pristine-harness files were byte-identical to origin/main, removed to unblock the ff-pull, restored by the pull itself).
- P22FIX2 (CheckGraph 50→150, `ranking_system.cpp:1838`): same story, 1 line; second `50)` site at :1997 (REDUCED-20 context) correctly untouched.

**1. Prior-worker recovery.** Found `pota28_repro/` staged (clones + patches + sbatches) and job 33142401 FAILED 1:0 in 59s (edge link error). Two faults fixed: (a) prep clone's tracked top-level `alglib/` (37 files) was deleted post-clone — restored via `git checkout -- alglib` (nested `original_nurbs_preprocessing/alglib/` was intact throughout); (b) the real killer: stale `build_pota28/` configured with an EMPTY PROJ_DEP GLOB (link.txt: 0 alglib objects vs pota27 build's 15) despite identical CMakeLists/sources — root cause not established, but a fresh `build_dbg2` configured+linked clean (job 33143145). Fix: script now `rm -rf "${BUILD}"` before cmake. Debug jobs: 33142997 (captured the `alglib::clusterizer` undefined-reference log), 33143145 (fresh build OK, binary carries SFS-T27+SFS-T13, 13 alglib objects linked).

**2. Pipe job 33143346 (run_pota28.sbatch) COMPLETED 0:0 in 6:14.** All in-job guards passed (both checkouts at port bases, diffs exactly the hunks, SFS-T21/T23b + P22FIX/P22FIX2 present, PC_/DIAG counts 0). T21 fired exactly once (p2); T04 exchange on 02–08; zero T14 appends on 02/03/04/05 (4× skip lines); Bl0 wall-only 155/146/140/135 pts — EXACTLY the p27 sizes, deterministically. Bundle `pota28_bundle/SfS_pp` (16 breaklines + 16 surfaces, md5 recorded).

**3. Stage job — VOID.** 33143863 COMPLETED 0:0 but both arms exit 2: `make -j8` (all targets) trips on the fork's broken sibling `Hierarchy-Clear-Original` (undefined `TwoPhaseAssemblyCoordinator`/GGCE link) while `Hierarchy-Clear` itself built. 33144425 FAILED 2:0 in 3s — my inserted comment's apostrophe (`fork's`) broke the container `bash -c '...'` quoting (fixed, `bash -n` clean). 33145079 COMPLETED 0:0 in 28:52 with `make -j8 Hierarchy-Clear`: ORIG arm exit 0, fresh arm exit 0 — tallies **ORIG 2/8+1/15 (Total 124, remaining 71), fresh 2/8+1/15 (Total 420, remaining 142)**. Same hypothesis-space sizes as p27 (124/420) but wrong final selection → scoring/selection differs. ORIG ≠ 8/8+15/15 → **void**.
- Log note: both arms place 8/8 pieces in State #0 (score ~808/805) with only 2 correct — full ring, wrong poses.

**4. Diagnosis (read-only): the fork is not upstream + hunks.** vs `sfs_p22fix_src` (upstream lineage): (a) LIVE delta — `ranking_system.cpp:327` `isSimilarTrans(T_c,T_i, 0.2, 20.0)` "BEAM SEARCH FIX: Tightened from 0.436" in chunk-merge (both via bulk commit 869e696 "SFS++ research enhancements"); (b) `CheckOpposingNormals` + `<map>` added to `feature_matching.cpp` but its only call site is commented out (:1806) — dead, exonerated; (c) GGCE leftovers (`connectivity_optimizer.h`, `combined_score` tie-break path, ticket-12 row-7 removal note). The 0.2 merge threshold is the prime suspect for the selection shift. Proposed follow-up (lead call, NOT done): ablate the 0.2→0.436 in a scratch build only, or port the cure onto a clean upstream-based tree.

**5. Laptop measurement (pipeline half, `artifacts/pota28/p28_gate.py` on `pota28_fetch`): teleports 0 in all four Bl0 files; gate 15/15, min 7 (pair 1-3 = 47 — matches p27's wall-only prediction exactly).** So the repo-built pipeline reproduces the rim cure; only the assembly binary diverges.

**6. Gaps / leftovers.** No seating render and no STRICT numbers: the fork binary writes transforms to a cwd-relative `results_*/Result/` dir (container `/tmp`, ephemeral — lost with the job), so `*_Result_snapshot/` dirs are empty and the snapshot protocol silently captured nothing. Rerun-with-capture is possible if the lead wants the failed seating rendered. Also: `Hierarchy-Clear-Original` broken independent of this ticket; stale-GLOB-build mystery (see §1) worth one line in lessons. Jobs (sacct State/ExitCode): 33142401 FAILED 1:0; 33142997 COMPLETED 0:0; 33143145 COMPLETED 0:0; 33143346 COMPLETED 0:0; 33143863 COMPLETED 0:0 (arms exit 2); 33144425 FAILED 2:0; 33145079 COMPLETED 0:0 (VOID: ORIG 2/8+1/15, fresh 2/8+1/15). Spartan leftovers: `pota28_repro/` (clones+builds+both sbatches+logs), `pota28_patches/`, `sfs_main/pota28_cure_33143863|33145079/`, `pota28_fetch.tgz`; laptop `artifacts/pota28/` (patches, sbatches, `p28_gate.py`, fetch). Poll was `sacct` directly throughout (`slurm_poll.sh` untouched).
