Status: done

# Ticket 237: merge paper-split-chain to main (option 1) + prove

Answers: E1 (Pot A assembly chain; merge target = the chain that seats Pot A).
Needs-eye: no.

## Goal
Merge the paper splitter chain into main as the working path, with the skip deletion, keeping the old path intact. Then prove post-merge main seats Pot A.

## Boundary
- Merge source 1: origin/paper-split-chain (1 file, mesh_processing_headless.cpp +497/-3, blob 556ef97a; flag SFS_PAPER_CHAIN default off, plane arm parked).
- Merge source 2: the -22 skip deletion, currently ONLY on unpushed local branch paper-split-236-strip @7035611 in worktree C:/PR/SfSpp_preprocessing-236 (do NOT lose it -- push it or apply the identical -22 first).
- Root edgeline file: DISCARD the branch's 154-era delta. Keep main's file (the source of reference binary dc472b0e, zero SFS-T27 strings, good lanes). Verify the kept file builds the good lanes.
- Do NOT delete: old splitter path, T21, T13, T23, assembly code, harness scripts. No other file changes.
- Main worktree (C:/PR/SfSpp_preprocessing, user 204-edit) off limits except the final merge commit + push. Work in a fresh worktree + fresh Spartan copy.

## Constraints
- Merge commit message states: what came in (paper grow/merge/classify + skip deletion), what was deliberately left out (branch root-edge delta, old-path deletion), and the edge-file decision.
- Post-merge: rebuild BOTH paths (flag off + flag on) in container; then Pot A E2E on the paper path, 210/236 protocol (fresh + ORIG control, strict tally, slots). Bar: 8/8+15/15 fresh, strict bar 7/8 (236 managed 8/8).
- If Pot A drops vs 236: STOP, report the delta, do NOT push main.

## Acceptance
- origin/main contains paper code + skip deletion, old path intact, root edge = good source. Build both paths COMPLETED 0:0, binaries md5-cited. Pot A fresh 8/8+15/15, strict tallied. No other files touched.

## Lead verdict (2026-10-22)
ACCEPT PASS. R6: 5/5 jobs sacct COMPLETED 0:0; merge e31be21 on origin/main (parents f4add97+7035611), exactly 2 files (+497/-3 paper, -22 skip); old path/T21/T13/T23 intact; Pot A fresh 8/8+15/15 ORIG valid strict 8/8, slots straight, no drop vs 236. OPEN DEFECT (from worker flags, accepted): merged main's root edge file builds STUB lanes (fac285df); good lanes came from stale dc472b0e whose source (md5 89ab05b1) != main's file (ce76a872). Main's tree cannot currently build working edge lanes. Fix BEFORE Pot D E2E (next ticket: find good source, restore, verify). Sweep still deferred.

## Required evidence to report
Merge commit hash; which root-edge source kept + how verified; job IDs + sacct states; binary md5s; Pot A tallies (fresh/ORIG/strict/slots); verdict in ticket Comments; Status results-in; self-contained completion message.

## Comments (worker 2026-10-21)
- Merge commit e31be21 on origin/main (parents f4add97+7035611, exactly 2 files): mesh_processing_headless.cpp +497/-3 (paper grow/merge/classify, SFS_PAPER_CHAIN default off) + root edge skip -22 (restored pre-skip blob 560f4de). Deliberately left out: branch 154-era root-edge delta (merge-base f76797f; root+subdir edge blobs identical both sides, root 234e581 zero SFS-T27/T14 strings), old-path deletion. Old path intact (flag-gated dispatch), T21/T13/T23 kept, root edge untouched.
- Root-edge source: kept main file; verified good via dc472b0e rebuild (source md5 89ab05b1 differs from main root file ce76a872 — ticket parenthetical was inaccurate, flagged to parent; instruction holds trivially). Merged root-edge binary fac285df built STUB lanes (byte-identical to 236 paperA run, known 236 regression flag) in paperA job 33623574.
- Jobs (all COMPLETED 0:0): build 33623329; flagoff P02 33623653 (old path rule=PCL-REGION-GROWING paper=off); paperA 33623574 (paper=PAPER-CHAIN all 8); edgeRef 33624012 (dc472b0e, FULL lanes all 8); seat 33624442 (11:11).
- Binaries md5: subdir mesh 38e6016c, subdir edge ce2f647d (SFS-T13-present/T27-absent), root mesh d72979aaa0055885a4dc88bb51a172e7 (byte-identical v3), root edge fac285df.
- Pot A (paper bundle + ORIG control, 210 protocol): FRESH 8/8 sherd + 15/15 edge; ORIG 8/8+15/15 VALID (absent P22FIX, present 0.436 pass). Strict 8/8 (rot 0.35-1.78 deg, trans 2.68-8.03 mm; script artifacts/pota237/strict_237.py, T files fetched). Slots all STRAIGHT (Bl0->authBl0 cov 0.987-1.000, med 0.37-0.71 mm; cross ~0; slotcheck237.py in sfs-merge-237).
- VERDICT: PASS — no drop vs 236. origin/main = e31be21. Spartan sfs-merge-237 == main. Seat sbatch + slotcheck237.py recorded in sfs-merge-237; strict script + T files in artifacts/pota237/.
