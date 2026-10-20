# 186 - Bundle the thin-loop C01 input, E2E x3 (p180 pattern)

Status: dispatched
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
Rebuild the C_180-style bundle with the 185 v3 thin loop (204 pts, .scratch/pota185_repro/p185_thin_walk_v3.npy) as the ONLY C01-Bl_0 change, then E2E x3 on Spartan and beat the 98 bar (2/3+1/3) with C01 seated -- same bar 180 cleared.

## Method (follow the 180 relay pattern)
Laptop legs: verify walk md5, bundle-build script (98-SXC base + Bl_0 install, byte-proofs, only-Bl_0-diff, veto-absence record), stage .scratch/pota186_repro/ + sbatch (A_orig/A_fresh/C_orig/C_186 arms, same asserts/shim/k5-b3/GT-stub as 176/180). Lead relays to Spartan: upload, login-node build, sbatch x3 + poll + sacct tallies vs 179 bar (Total 100-125, pruned 30-40, C01 pairs surviving, edges >=2/3).

## Constraints
Lead holds the spec; worker runs chores. COMMIT NOTHING (worker). Spartan relay via lead.

## Acceptance
Total + pruned + sherd/edge tallies x3 with C01 seated (T_0to_0 present), controls green (A 8/8+15/15, C_orig as before), falsifier owned in advance.

## Required evidence
Staged scripts + md5s + job IDs + per-run tallies + honest verdict vs bar.
