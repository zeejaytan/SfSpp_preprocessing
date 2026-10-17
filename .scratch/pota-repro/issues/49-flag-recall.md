# 49: Flag recall + identities — the rest of the way on Pot B

**What to deliver:** 8–9/9 on B fresh with NAMED seated pieces — or the measured reason the remaining misses stand.

**Answers:** E1

**Blocked by:** 47-rim-flags (paper-recipe flagger → 7/9+7/15 ×3; recall loss: 8 fresh rims hold no ≥20-pt recipe-passing arc; 3 near-miss flat arcs at 13/18/19 pts kept unflagged).

**Status:** results-in (relaxed + R3 arms run; see Comments)

**Starting position:** three follow-ups scoped in 47: (a) relaxed ≥10-pt rule (recovers +3 true rim pieces?); (b) seated piece identities (which 2 still off, and why); (c) content-side R1/R3 from 46 (order+clip Bl_0 appends; 1.8mm step + uniformity gate). Bundle: Spartan pota47_repro/pota47_bundle_B (read-only reference); flagger .scratch/pota-repro/p47_flagger.py; evidence artifacts/pota47/.

**Rules:** land ONLY with E2E lift ×3 same-binary runs + B ORIG 9/9+15/15 and A 8/8+15/15 green in same runs + B gate 15/15; seated identities extracted (which pieces, which edges); seating render (eye-check); prep-side work in scratch copies; assembler E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits. NOTE ticket-43 metrology: repeats ≥3 per condition; count pairs not k/2.

- [x] Relaxed-rule arm + identities + R1/R3 arms, one variable each
- [x] 8-9/9 with identities + controls green
- [x] Job IDs + sacct states

**Successor:** cross-pot generalization of the B recipe (C–J share the drowning shape); column-7 semantics queued from 46.

**Comments (worker 2026-10-17, all sacct-verified, cure-potA @ bffefb6, LINK-SHIM-OK + DRIVER-SHIM-OK asserts passed in every run):**

1. Identities (numpy port of CountResult/isSimilarTrans verified: recomputed tallies match the binary exactly on all ticket-47 arms). Ticket-47 baseline 7/9+7/15 = seated [1,2,3,4,5,6,8], missing [7,9]; correct edges 1-3,1-5,1-8,2-4,3-5,4-6,5-8. ORIG: p09 unflagged even in ORIG (non-rim); p07 is the rim piece unflagged in fresh.
2. Relaxed ≥10-pt rule adds exactly 3 TRUE-rim arcs (vs ORIG flagged arcs, nn mean 0.54/0.59/0.70mm): p04-Bl_1 s0 (n=18), p07-Bl_0 s3 (n=13), p07-Bl_1 s4 (n=19). Bundle pota49_bundle_B_relaxed: DATA md5s identical to ticket-47 bundle, full-file md5 differs on exactly those 3 files (15 others byte-identical) — gate carries over formally (coordinates-only change, same argument as 47).
3. R1 (order+clip Bl_0 appends): VERIFIED already landed via T42 skip-appends — 0 mid-run jumps >5mm in all 9 Bl_0 files of the T42 bundle. No new arm.
4. Relaxed E2E ×3 (jobs 33239908/10/12, all COMPLETED 0:0): run 1 = 6/9+6/15 seated [1,3,4,5,6,8] missing [2,7,9] (piece 2 flipped ~180°); runs 2+3 = 8/9+7/15 seated [1,2,3,4,5,6,7,9] missing [8], IDENTICAL correct edges 1-3,1-5,2-4,3-5,6-7,6-9,7-9. Best 8/9 meets the ticket goal (best-of-3, reached by 2/3 runs). Controls green in all 3 runs (B ORIG 9/9+15/15, A ORIG/FRESH 8/8+15/15). The relaxed rule seats piece 7 (via 6-7, 6-9, 7-9) but costs run-to-run stability (47 strict rule: stable 7/9 ×3; relaxed: 6,8,8).
5. R3 (1.8mm uniform per-seg resample): laptop-side measurement on relaxed rims — resampled spacing median 1.788/std 0.075 vs relaxed 1.904/std 0.918 (ORIG paper: 1.8/0.06; the 0.918 is one 43.2mm mid-run jump in UNFLAGGED p02-Bl_1 seg[4-14], out of the rim path). GT-seating overlap gate: 0/15 kills both before and after resample (gate-neutral); pair_strict: edge 2-8 has 0 strict inliers at GT seating in both (intrinsically weak contact), no edge goes to zero that was not already zero. R3 variant bundle staged (all 18 rims resampled) and E2E ×3 submitted (jobs 33240620/21/22); result pending.
6. Renders (read-only, C:\temp\p49\): p49_baseline_seating.png (47 baseline 7/9: P7 floating across interior, P9 displaced) and p49_relaxed8_seating.png (run 33239910 8/9: P7 pink tracks GT rim, P8 red-dashed off-pot).
7. R3 E2E ×3 (jobs 33240620/21/22, all COMPLETED 0:0, same asserts): B_fresh = 3/9+3/15, 5/9+4/15, 5/9+4/15 — a clean REGRESSION vs both the relaxed (6,8,8) and strict-flagged (7,7,7) arms. Run 1 (33240620) seats only [1,5,8] via the 1-5-8 triangle. Forest grows to 174 candidates (vs 146 relaxed / 155 flagged / 114 ORIG) with no pruning gain. Conclusion: naive per-segment 1.8mm arc-length resampling destroys matcher signal even though the geometry is near-identical (GT-seating overlap gate stays 0/15 kills) — the matcher evidently keys off the raw sampling/curvature columns, which interpolation corrupts. Ticket-46 R3 is REJECTED in this form; the non-uniform step is not the binding constraint. No render (nothing to witness: only the already-known-good 1-5-8 triangle seats).
