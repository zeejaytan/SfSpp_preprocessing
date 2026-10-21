Status: ready-for-agent

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

## Required evidence to report
Merge commit hash; which root-edge source kept + how verified; job IDs + sacct states; binary md5s; Pot A tallies (fresh/ORIG/strict/slots); verdict in ticket Comments; Status results-in; self-contained completion message.
