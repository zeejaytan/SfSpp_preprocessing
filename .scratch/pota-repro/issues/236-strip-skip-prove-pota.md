Status: done
Answers: E1

# Ticket 236: strip the 27-skip on paper-split-chain, prove Pot A without it

## Goal
Remove the superseded 27-skip (T24+T27 appendage-skip, +22 lines) in branch paper-split-chain, then prove Pot A still seats 8/8+15/15 on the paper path without it. If Pot A holds, the skip is proven dead code and stays out (user rule: superseded fixes are removed, not kept).

## Boundary
- Branch paper-split-chain ONLY, new worktree. Main, other branches, other worktrees untouched.
- Do NOT touch T21, T13, T23, or the old splitter -- their fate is decided at merge time, not here.
- Read-only on tickets 27/234/235/210; edit only this ticket (append Comments, Status results-in). No commits, no pushes.

## Constraints
- Locate the skip (+22 lines from ticket 27) and every call site it guards. Remove it branch-wide (the branch is the paper-arm vehicle; the old path in this branch is not under test).
- Rebuild (container build, cite binary md5). Same-source check for everything else.
- No-op proof first (cheap): lane diff skip-present vs stripped on P22 + P12 -- expect byte-identical lanes. If they differ, STOP and report (the skip was load-bearing somewhere).
- Then Pot A E2E on the paper path, 210 protocol (strict bar 8/8+15/15, same k/b, ORIG control must reproduce or void).

## Acceptance
- Pot A 8/8+15/15 strict on the paper path with NO skip code in the branch. sacct COMPLETED for every job; binary md5 cited.
- Verdict: SKIP-DEAD (Pot A holds -- removal stands) or SKIP-LIVE (Pot A drops -- report the delta, revert the removal, skip stays).
- No-op lane diff result either way.

## Lead verdict (2026-10-22)
ACCEPT SKIP-DEAD. R6: 6/6 jobs sacct COMPLETED 0:0; removal exactly -22 lines 1 file (subdir edgeline file); repo-wide grep clean; no-op lanes byte-identical (P22/P12); Pot A 8/8+15/15 strict 8/8 on paper path with no skip (beats 210 strict 7/8); ORIG control valid. Key finding stands: skip never ran in production (root builds contain zero skip code; 210 already proved Pot A without it). Merge decision (scope) put to user; sweep deferred to merge landing (strip branch unpushed, lives in the 236 worktree).

## Required evidence to report
Job IDs + sacct states; binary md5; the lane-diff result; Pot A strict tallies; verdict in ticket Comments; Status results-in; self-contained completion message to the parent.

## Comments
## Comments (worker, 2026-10-22 -- SKIP-DEAD, Pot A 8/8+15/15 on the paper path with no skip code in the branch)

**Verdict: SKIP-DEAD.** The +22 skip is removed branch-wide (exact -22-line revert, blob 28d34bc back to pre-skip 560f4de); Pot A seats 8/8+15/15 on the paper path with strict 8/8 (better than 210 strict 7/8). No commits, no pushes; main and other branches/worktrees untouched; laptop tree changed only in this ticket + gitignored artifacts/pota236/.

**1. Where the skip actually lived (read-only finding).** The +22 SFS-T24/T27 block (commit 48ca2c0) guards ONE call site: ticket14_append_patch_rims in original_nurbs_preprocessing/edgeline_extraction_headless.cpp. It compiles ONLY via the subdir build (cmake original_nurbs_preprocessing -- ticket 27 cure binary; CMAKE_HOME_DIRECTORY + SFS-T27 strings verified). Every production E2E (208/210/234/235) builds the ROOT CMakeLists, whose edgeline_extraction_headless.cpp (ce76a872) has ZERO T14/append code -- verified: sfs-e2e-pristine/build-e2e binary 0 SFS-T27 strings; reference binary dc472b0e 0 strings. So the skip NEVER ran in any production seating: 210s 8/8+15/15 already proved Pot A without it.

**2. Removal (new worktree C:/PR/SfSpp_preprocessing-236, local branch paper-split-236-strip @7035611, NOT pushed).** Spartan fresh copy sfs-fix-236 (local clone + fetch github paper-split-chain, checkout 7035611, clean tree, mesh md5 556ef97a == v3). Skip spliced out (asserted block 3415-3438, LF preserved); git diff exactly -22 lines, 1 file; repo-wide grep: no SFS-T27 in any .cpp/.h. T21/T13/T23/mesh untouched; no other ticket files edited.

**3. Rebuilds (container pcl_191_nurbs.sif, same-source checks).** 33619626 subdir SKIP: mesh 8d75adb4, edge 3be1d9b5 (SFS-T27 in binary OK; alglib nested-copy fix per ticket 27). 33619970 COMPLETED 0:0 (3:16): subdir STRIPPED mesh 8d75adb4 + edge 90e2ffa2 (SFS-T13 present, SFS-T27 absent OK); root mesh d72979aaa0055885a4dc88bb51a172e7 == v3 evidence binary BYTE-IDENTICAL; root edge fac285df rebuilt from branch ce76a872. (33619466 FAILED on my wrong strings-guard only; 33618911 root-edge build fine.) REGRESSION FLAG for the lead (out of mandate): branch root edge (pota-154 split-walk era) yields STUB lanes everywhere vs reference dc472b0e (stale 89ab05b1 from sfs-fix-221): P22 78/35 vs full, P02 79/missing vs 176/177. The E2E below uses the 234/235 reference edge dc472b0e (skip-free, 0 SFS-T27 strings); the branch edge-file delta is a separate merge-time call.

**4. No-op proof: PASS, byte-identical.** 33620274 COMPLETED 0:0 (42s). Subdir edge SKIP (3be1d9b5) vs STRIPPED (90e2ffa2) on 234 paper-mesh trees pota234_edgeP22_paper3 / pota234_edgeP12_paper3 (genuine 8-9s edge runs each): diff -r Breaklines clean -- P22 BYTE-IDENTICAL, P12 BYTE-IDENTICAL. (First attempt 33620273: my unquoted heredoc ate the vars; cancelled, resubmitted.)

**5. Pot A paper path (root paper mesh d72979aa + ref edge dc472b0e, 210 protocol): 8/8+15/15, strict 8/8.** 33620511 COMPLETED 0:0 (2:13): paper mesh x8 (theta=4/kappa=1/nb=10, Appendix-A merge values): clusters healthy (top2 ~99%), classify votes clean 98-100%, S0=interior. 33621238 COMPLETED 0:0 (38s): edge rerun with dc472b0e -- FULL lanes all 8 (P01 218/221, P02 176/177, P03-P06 154-162, P07 69/71, P08 65/68, at/above author counts). Slots all 8 STRAIGHT (freshBl0->authBl0 cov 99-100%, med 0.37-0.81mm; cross-slots ~0%) -- NO swap needed. Bundle pota236_paper_bundle_v1 (16/16/8/8 + surfaces, md5 recorded). 33621605 COMPLETED 0:0 (11:18): scorer pristine b56bc80, guards green both arms (HEAD/clean/P22FIX-absent/0.436/SHIM-O-FOUND/DRIVER-SHIM-OK). (First attempt 33621456 failed: my seat script dropped 210s shim.o link substitution; restored verbatim, resubmitted.) Fresh: Sherd 8/8 (100%), Edge 15/15 (100%) -- FRESH-VERDICT 8/8+15/15. Acc.txt: Time 402200 Sec, same tallies. ORIG same job: 8/8+15/15 -- ORIG VALID, not void.

**6. Strict (5deg/10mm, 208 Kabsch-on-2..8 recipe, artifacts/pota236/strict_236.py on fetched T_0..T_7):** 1|1.17|7.09 2|1.75|3.56 3|0.89|4.27 4|0.45|3.33 5|1.46|8.98 6|1.19|3.21 7|1.44|7.84 8|0.94|3.50 -- STRICT-SHERD 8/8 (210 managed 7/8 with P5 at 11.19mm; paper seats P5 at 8.98 PASS). Eye-check artifacts/pota236/seat_fresh236_vs_gt.png (side+top, GT gray + attempt color): coherent vessel, all 8 on the GT shell -- judged good.

**7. Spartan leftovers (all mine, sibling-safe):** sfs-fix-236/ (sources, build-236A/B/root, run sbatches, lanecomp.py/slotcheck.py, logs), pota236_paper_P01..P08 + P02ref + P22fac copies, pota236_noop_P22/P12A/B, pota236_paper_bundle_v1, pota236_e2e/pota236_run_33621605 (L/O logs, snapshots, Acc). pota234/235/208/210 trees, sfs-fix-221/232/234/235, sfs-e2e-pristine, pota27 worktree: read-only, unmodified. Laptop: this ticket + artifacts/pota236/ (T_0..7, strict/render scripts, seat render); worktree C:/PR/SfSpp_preprocessing-236 holds the uncommitted -22 removal for lead review.
