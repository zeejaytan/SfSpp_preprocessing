Status: done

# Ticket 238: restore working root-edge source to main

Answers: E1 (Pot A/E2E chain needs tree-built edge lanes).
Needs-eye: no.

## Goal
Make main's own tree build working edge lanes again. The good reference binary dc472b0e was built from root edgeline_extraction_headless.cpp at exp-218 commit 885f433 (file md5 89ab05b1, verified by lead); main's current file (md5 ce76a872, 154-era content) builds STUB lanes (proven 236/237). Restore the good source, verify, commit.

## Boundary
- Exactly 1 file: the ROOT edgeline_extraction_headless.cpp (not the vendored subdir copy, not mesh, not old path, not flags).
- Take the file content at commit 885f433 (branch exp-218, reachable on origin). If its ifdef defaults differ from plain-old behavior, keep default = old behavior (all arms off) -- verify by reading the flags.
- Fresh worktree + fresh Spartan copy. Main worktree (user 204-edit) off limits except final commit + push.

## Constraints
- Rebuild the root edge binary in the container. Verify FIRST against dc472b0e: binary md5 match if the build is deterministic, else lane-diff on P22+P12 (must be full lanes: P22 ~176/177-class, P12 both lanes; stubs = FAIL, stop and report).
- Then Pot A short re-proof on the paper path (fresh arm minimum; 236 numbers are the bar: 8/8+15/15, strict 8/8). Drop => STOP, no push.
- Commit message states: which source restored (885f433/md5), why (main's file built stubs), what verified it.

## Acceptance
- origin/main root edge file md5 = 89ab05b1. Tree-built edge binary yields full lanes (not stubs). Pot A holds. No other files touched.

## Lead verdict (2026-10-22)
ACCEPT PASS. R6: 4/4 jobs sacct COMPLETED 0:0; tree-built root edge md5 dc472b0e == reference BYTE-IDENTICAL; lanes P22 135/155 + P12 153/158 = REF (no stubs); paperA all 8 = 237 counts, slots straight; seat FRESH 8/8+15/15 ORIG valid, strict 8/8. Main's tree now builds its whole chain. Next: sweep, then Pot D E2E.

## Required evidence to report
Restored file md5; edge binary md5 (+ dc472b0e comparison); lane counts P22/P12; Pot A tallies; job IDs + sacct states; verdict in ticket Comments; Status results-in; self-contained completion message to parent agent session-1ca83938-6e86-4736-bb84-2f4e58807e35.

## Comments (worker 2026-10-22 -- PASS, root edge restored, Pot A holds)

**Verdict: PASS.** Root edgeline_extraction_headless.cpp restored from exp-218 commit 885f433 (blob md5 89ab05b1); main's file (ce76a872) built STUB lanes. Tree-built binary is BYTE-IDENTICAL to reference dc472b0e; full lanes everywhere; Pot A 8/8+15/15 fresh, ORIG valid, strict 8/8. Pushed to origin/main.

**1. Restore (laptop fresh worktree .scratch/.wt-238 + Spartan fresh copy sfs-fix-238).** `git show 885f433:edgeline_extraction_headless.cpp` -> root file, worktree md5 89ab05b1 both sides, exactly 1 file changed. ifdef defaults = old behavior verified by reading: ARM B fixed-4mm radius under #else (main carried 6x/3-50 adaptive), keep-all veto FACE_ALIGN_VETO=2.0 always passes, ARM A/C filter blocks under #ifdef with plain push-through #else, diagnostic boundary_Sx.pcd block triple-guarded. No flag = old behavior.

**2. Spartan base note (reported, not a blocker).** Main-checkout `pull --ff-only` blocked by documented skip-worktree live file (mesh_processing_headless.cpp, S-flag, 0 SFS_PAPER_CHAIN = old-path variant, live research input -- left untouched per AGENTS.md). NOT a history divergence: `git ls-remote origin main` = 292c535 = laptop origin/main = laptop HEAD. Fresh copy sfs-fix-238 cloned + `fetch github main`, checked out 292c535 (verified hash), restored edge from local 885f433 object (md5 89ab05b1). Subdir build not redone (needs untracked alglib scaffolding present only in old dirs; out of mandate -- root only).

**3. Rebuild (container pcl_191_nurbs.sif).** 33629957 COMPLETED 0:0. Root mesh d72979aaa0055885a4dc88bb51a172e7 == v3 evidence binary BYTE-IDENTICAL (restore touched edge only). Root edge dc472b0e87c934b6c487ff8637209864 == reference dc472b0e BYTE-IDENTICAL (deterministic). strings: 0 T14/T27 (append-free, skip-free).

**4. Lanes: FULL, REF-identical (stubs would have STOPPED the ticket).** 33630854 COMPLETED 0:0 (all exits 0). P22 NEW 135/155 = REF 135/155; P12 NEW 153/158 = REF 153/158 (both lanes present; stub signature 78/35-class absent). Pot A paperA 33631146 COMPLETED 0:0: P01 218/221, P02 176/177, P03 159/162, P04 161/158, P05 159/156, P06 154/154, P07 69/71, P08 65/68 -- all 8 EXACTLY the 237 edgeRef full-lane counts, from the tree-built binary. Slots all 8 STRAIGHT (freshBl0->authBl0 cov 0.987-1.000, med 0.37-0.81mm; cross ~0) -- NO swap.

**5. Pot A paper path (fresh arm + ORIG control, 210 protocol).** Seat 33631833 COMPLETED 0:0. FRESH Sherd 8/8 Edge 15/15 (FRESH-VERDICT 8/8+15/15); ORIG 8/8+15/15 VALID. Bundle pota238_paper_bundle_v1 (16/16/8/8, md5 recorded). Strict (5deg/10mm, Kabsch-on-2..8, artifacts/pota238/strict_238.py): 1|1.18|7.07 2|1.75|3.69 3|0.79|3.75 4|0.43|3.22 5|1.37|8.48 6|1.23|3.12 7|1.41|7.46 8|0.73|2.91 -- STRICT-SHERD 8/8.

**6. Spartan leftovers (all mine, sibling-safe):** sfs-fix-238/ (sources @292c535+edge restore, build-238root, run sbatches, build/lanes/paperA/seat logs), pota238_P22/P12_NEW/REF, pota238_paper_P01..P08, pota238_paper_bundle_v1, pota238_e2e/pota238_run_33631833. Main checkout, pota234/236/237 trees, sfs-merge-237: read-only, unmodified. Laptop: this ticket + artifacts/pota238/ (strict_238.py + T_0..7); .scratch/.wt-238 holds the pre-commit restore worktree.
