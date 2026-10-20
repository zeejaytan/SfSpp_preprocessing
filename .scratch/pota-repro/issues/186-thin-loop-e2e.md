# 186 - Bundle the thin-loop C01 input, E2E x3 (p180 pattern)

Status: DONE

## Lead verdict (2026-10-20)
- C01 SEATED x6: worker chain (33482185/86/87) + lead duplicate chain (33482198/99/200),
  all COMPLETED 0:0, tallies IDENTICAL: C_186 155/24, 3/3+3/3, T_0to_0 present everywhere.
- 179 falsifier NOT triggered (155, not ~40). Bar partially met: seating + edges pass;
  pruned 24 below 30-40 band -- gate is now pruning-side, not input-side. No further
  input-side iteration without new evidence.
- Controls green both chains (A 8/8+15/15, C_orig 4/4+5/5).
- Standing answers: workers CAN ssh Spartan themselves (worker ran full chain after probe)
  -- brief full-chain henceforth. Handoff discipline: file + final output, never child messaging.
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

## Comments (worker, 2026-10-20 -- thin-loop input staged, E2E STAGED-READY but NOT RUN; COMMIT NOTHING)

**Status: laptop legs COMPLETE, E2E STAGED-READY -- this worker has no SSH (no submit). No verdict on the 179/180 bar yet; this is a staging report, not a landing.**

**0. Boundary kept.** Dataset read-only; production checkout never entered; tickets 39-185 read-only (numbers quoted from 179/180/185 Comments only); no assembler source touched (not even read); nothing committed (tracked diff empty); only this Comments section added to the ticket file.

**1. 185 v3 walk verified (laptop numpy, byte proofs).** p185_thin_walk_v3.npy: 204x3, md5 57e7077cec514c5e7511de63547bf35a. Seated frame (rim-truth seated med 0.64 = 185 lead gate repro; mesh-mesh med 351 = cross-frame, as expected). Arc-steps 365.0 (5% short of author 380.0, smoothing shrink), closure 1.79 (<=2 PASS), med/max 1.79/3.23, gaps>5mm 0, zero-steps 0. D-tokens (0.15 bins) distinct 2, top (11:203, 21:1), closed-loop longest run 132 (steps-only 131 per v3 log). Rim-truth seated: ours-vs-author med 0.64, <2mm 97.1%, max 3.35; author-vs-ours med 0.65, cov 203/211. Key-free declaration holds (185 DONE verdict; author key used CHECK-ONLY for rim-truth).

**2. Frame conversion (ONLY structural delta vs 180).** 180 single was mesh-frame; 185 v3 is seated-frame. Laptop-side inverse-T (176 s7a, T = Pot_C_Piece_1_T.txt): roundtrip max err 0.0005mm (float32 T, negligible). Staged mesh walk p186_C01_thin_walk.npy = 204x3, md5 32b80e8b55adeb3a6579a3a77a5e2347; seated byte-copy kept as p186_C01_thin_walk_seated.npy (md5 = v3 md5). Spartan build therefore needs no T and is a line-for-line 180 port (NNEW 204).

**3. Slot-hygiene (md5, laptop reference = 7x fetched CSXC rims + new Bl_0).** ONLY C01-Bl_0 differs (d4793a55 -> 1b891676); other 7 slots bit-identical (Bl_1 fa3805fe, C02-Bl_0 cb5c2ec5, C02-Bl_1 7d48c6c7, C03-Bl_0 9d2d6183, C03-Bl_1 32541c25, C04-Bl_0 f04f5cf9b, C04-Bl_1 b5dcec46 -- same base md5s as 180). G0 curvature uniq 1, val 1.905766e-42; G0-donor mesh-mesh med 0.64, n>5mm 0; segs rescaled 402->204, head # 1 15 0, tail # 200 204 0. Spartan build repeats this proof live vs 98-SXC + records veto-absence.

**4. Staged for lead relay (.scratch/pota186_repro/, 180 pattern).** p186_C01_thin_walk.npy + p186_C01_thin_walk_seated.npy + p186_make_pcd.py (rerunnable: verify+convert+reference bundle, py_compile OK) + p186_build.py (py_compile OK; WALK_MD5 32b80e8b..., NNEW 204, veto-absence + only-Bl_0-diff + 98-SXC guards) + run_pota186_stage_AC.sbatch (bash -n OK; 4 arms A_orig/A_fresh STEPS 8 + C_orig/C_186 STEPS 4, same asserts/shim k5-b3/GT-stub/overlay/bundle-guard/fetch as 180) + RELAY.txt runbook + p186_BL_md5.txt + p186_report.txt/p186_pcd.txt logs + ref_bundle/ reference. Renders eye-checked: artifacts/pota186/p186_01_thin_vs_ref.png (red thin loop rides green author ring; known kink-sector stray at left x~-50 + right-curl wiggle, same class as 180's qualification), p186_02_order_trace.png (one clean circuit, markers 0/68/136 even, small jag at kink), p186_03_station_sweep.png (monotonic single wrap, wrap at order ~115, jog at order ~140 = stations 24-31 gap). Same-binary ORIG control (C_orig arm) is in-job. Lead runbook: ship 3 stage files -> login-node python3 p186_build.py (expect BUILD DONE, only-Bl_0-diff, 98-SXC ALL-OK) -> sbatch x3 + poll + sacct State/ExitCode -> tally vs bar below.

**5. Bar + falsifier (same 179 bar 180 beat).** Predict: Total 40 -> 100-125 band, pruned 8 -> 30-40 band, C01 pairs >=1 survivor, C01 seated (edges 1/3 -> >=2/3), controls green (A 8/8+15/15, C_orig 4/4+5/5). FALSIFIER owned in advance: Total stays ~40 -> thin-loop input is NOT the gate (assembler-side or segment-window cause), proposal refuted -- report honestly, no further input-side iteration without new evidence.

**6. Evidence.** .scratch/pota186_repro/ (scripts + both walk npys + reference pcds + md5 + logs + RELAY.txt) + artifacts/pota186/ (3 renders). No repo sources touched, dataset read-only, COMMIT NOTHING.

## Comments (worker, 2026-10-20 -- E2E x3 COMPLETE, mixed vs bar; COMMIT NOTHING)

Parent follow-up granted Spartan SSH; full chain executed from this worker. COMMIT NOTHING held (tracked diff empty apart from this section).

**S1. Relay.** ssh_exec spartan OK (spartan-login2.hpc.unimelb.edu.au). Recon: 98-SXC base present, vehicle HEAD bffefb6 (assert passed). Uploaded 3 stage files; arrival walk md5 32b80e8b... match. First login-node build FAILED on a worker porting bug (P39 pointed at .../pota39_repro/asm instead of .../prep/pota39_bundle_C/SfS_pp); fixed in .scratch/pota186_repro/p186_build.py (py_compile OK), re-uploaded, BUILD DONE exit 0: WALK GREEN 204x3, G0 med 0.64, segs 402->204, ONLY C01-Bl_0 differs (e1e59c->ef922d), 98-SXC intact ALL-OK. Note: Spartan Bl_0 md5 (ef922d) differs from the laptop reference (1b891676) by CRLF line-endings ONLY (laptop write tool emits CR; equal-modulo-CRLF True, verified by download+diff); in-job bundle guard uses the Spartan-side manifest, self-consistent.

**S2. Jobs.** sbatch x3: 33482185, 33482186, 33482187 -- all COMPLETED 0:0 (11-17 min). Run dirs /data/gpfs/projects/punim2657/sfs_main/pota186_run_<JOBID>/, per-run pota186_fetch.tgz present (e.g. 41896 bytes in run 185).

**S3. Tallies (identical x3 -- deterministic).** A_orig 124/70 + 8/8 + 15/15; A_fresh 420/119 + 8/8 + 15/15; C_orig 125/40 + 4/4 + 5/5 (matches C_orig as-before); C_186 155/24 + 3/3 + 3/3. T-files x3 identical: T_0to_0 + T_1to_1 + T_3to_3 (C_186 lacks T_2to_2; T_0to_0 pose differs from C_orig as expected with new input).

**S4. Verdict vs bar (honest, mixed).** PASS: controls green (A 8/8+15/15, C_orig 4/4+5/5); C01 seated (T_0to_0 present x3); edges 3/3 clears >=2/3; literal falsifier NOT triggered (Total 155, not ~40 -- the input moves the needle). FAIL: pruned 24 below 30-40 band and below control 40; one fewer seated pair (3 vs 4, missing T_2to_2); Total 155 overshoots 100-125 band. Net: thin loop generates MORE hypotheses (+30 raw) but FEWER survive pruning -- C01 itself seats, the gate is now pruning-side (or segment-window), not input-side. No further input-side iteration proposed without new evidence.
