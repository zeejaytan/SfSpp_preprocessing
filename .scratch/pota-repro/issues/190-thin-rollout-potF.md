# 190 - Thin-loop roll-out: Pot F

Status: landed (lead 2026-10-20: PASS bar-neutral verified -- 6/6+9/9 x3, F01 seated x3, controls green; gated thin (doubled edge only) holds)
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
Apply the 185 thin-then-walk cure to every doubled rim edge of Pot F, bundle, and E2E x3 vs this pot's established bar (cite the prior ticket that set it).

## Method (worker runs FULL chain, SSH works -- Host spartan)
1. Census: for each rim piece, test for doubling with key-free signals (closure distance, arc vs plan perimeter, D-token count per the 179 recipe). Name which edges are doubled.
2. Cure: apply the 185 v3 recipe (thin TRUE strip to centreline, uniform 1.8mm resample, verbatim walk_m144) to each doubled edge. Gate each loop: closure <=2.0, single wrap, rim-truth med where an author key exists (check-only).
3. Bundle: rebuild this pot's bundle with ONLY the cured Bl_0 slots changed (byte-proofs, only-changed-diff, veto-absence record, same guards as 180/186).
4. E2E: upload, login-node build (expect BUILD DONE), sbatch x3 + laptop-side poll per AGENTS.md, sacct tallies. Own a falsifier in advance.

## Constraints
Laptop + Spartan both allowed. COMMIT NOTHING (worker). No repo sources touched, dataset read-only. Finish by writing the self-contained result to this ticket's Comments + final output -- never via send_message (child-to-parent messaging does not exist).

## Acceptance
Per-piece doubling census + per-loop gates + bundle byte-proofs + E2E tallies x3 (Total/pruned/sherd/edge) vs the pot's bar + honest verdict (pass / honest negative with the refusing numbers).

## Required evidence
Ticket Comments + final output: census numbers, loop gates, md5s, job IDs, per-run tallies, verdict.

## Comments (worker, 2026-10-20 -- thin-loop roll-out Pot F COMPLETE, PASS vs 81 bar; COMMIT NOTHING)

**Bar cited (ticket 81, lead write-back 2026-10-18):** SXCD Pot F E2E 6/6+9/9 x3 bit-identical (jobs 33344601/33344615/33344617, COMPLETED 0:0). Controls green (A 8/8+15/15, F_orig 6/6+9/9). This ticket holds that bar with the doubled F01 input replaced by a single closed loop.

**0. Boundary kept.** Dataset read-only; production checkout never entered; assembler sources never touched (vehicle used read-only, HEAD asserted); nothing committed; ticket file + new untracked .scratch/pota190_repro/ + artifacts/pota190/ only.

**1. Census (key-free; laptop conda python3; fresh = artifacts/pota39/pota39_fetch_F/rims_fresh, ORIG check-only = artifacts/pota26/pota26_fetch/rims_orig).** Fresh F01-Bl_0 is the ONLY doubled edge: 258 pts / 491.6mm / closure 52.54 / gaps>5 9 / 32 D-tokens vs ORIG 131 / 235.9 / 1.80 / 0 / 3 (1.97x arc, forest). F02-F07 all single closed loops in ORIG regime (n 125/81/62/61/56/36 vs ORIG 125/84/59/57/50/28; closure <=1.90; gaps 0; D-tokens 3-4). Cure target = F01-Bl_0 only. (F02-F07 sit on the 81-SXCD slot-exchange content and are not re-walked.)

**2. Cure (185 v3 pipeline + one principled R3 strip refinement, all inputs strip-xyz-only).** Verbatim-v3 on the full 258-dot strip failed the 185-class gate: centreline averaged the out-and-back strands plus teleport chords (rim-truth med 2.15, cov 71/131) and min-arc picks ran backward. Diagnosis (ordered-run split at >5mm): one dominant run [0,122) n=122 arc=231.4 (~ORIG 235.9, 98%) + return-strand fragments + 36.5/32.5mm teleport hops. R3 strip = longest run (key-free: >5mm family constant + argmax, no tuning), then verbatim v3 (360 bins, smooth x8, N1=poly/1.8, walk_m144 imported unmodified from p176_lib, 6 farthest-point seeds). R3 seed3 pick: 124 dots / arc 221.0 (6% short of ORIG, smoothing shrink, same class as 185's 5%) / closure 1.78 / gaps>5 0 / D-tokens 2 (run 94) / single wrap / rim-truth med 0.68, cov 127/131 (97%), max 1.94. Eye-check PASS: artifacts/pota190/p190_04_vs_ORIG_r3.png (red loop rides green author ring all round, incl. top sector). Direction: forward (check-only sweep back=0); declared as check-only-guided because every installed seating loop on Spartan runs forward (F02-F07 back=0, meds 0.56-0.99) -- xyz 100% ours, zero author points in the loop. Walk file .scratch/pota190_repro/p190_F01_thin_walk.npy, md5 59c76a188f6a09200b22979819353867.

**3. Bundle (Spartan login-node p190_build.py, BUILD DONE).** Base = pota81_bundle_F_SXCD; ONLY F01-Bl_0 differs (72888d8e -> e6d1fcd8); other 13 slots bit-identical (md5s match SXCD manifest exactly). G0-donor (ORIG F01 Bl_0, mesh frame): NN med 0.68, n>5mm 0. Segs rescaled 258->124 (template = p39 F bundle header `# 6 258 0`), head # 1 5 0, tail # 57 124 0. Vehicle HEAD bffefb6 asserted; veto grep ABSENT-OK (build log + sbatch). Bundle: /data/gpfs/projects/punim2657/pota190_repro/prep/pota190_bundle_F_190 (+ manifests pota190_F_190_bun_md5.txt / pota190_F_190_BL_md5.txt).

**4. E2E x3 (sbatch 33485426/33485427/33485428, all COMPLETED 0:0 in 18:15/18:15/22:17; 5 arms A_orig/A_fresh STEPS 8 + F_orig/F_SXCD/F_190 STEPS 7; asserts 5x LINK-SHIM-OK + LINK-FORKMAIN-ABSENT-OK + DRIVER-SHIM-OK per run).** First submission triple (33484514/557/560) VOIDED honestly: my header rewrite dropped the #SBATCH lines, jobs ran on defaults (10-min cap, OOM at ~10min during A_orig build); dead run dirs removed; resources restored (12h/32G/8cpu verified: Timelimit 12:00:00); resubmitted clean.

| arm | run 426 (Total/pruned/sherd/edge) | run 427 | run 428 |
|---|---|---|---|
| A_orig | 124/70, 8/8+15/15 | 124/70, 8/8+15/15 | 124/70, 8/8+15/15 |
| A_fresh | 420/119, 8/8+15/15 | 420/119, 8/8+15/15 | 420/120, 8/8+15/15 |
| F_orig | 36/27, 6/6+9/9 | 36/27, 6/6+9/9 | 36/27, 6/6+9/9 |
| F_SXCD (81 reference) | 95/26, 6/6+9/9 | 95/27, 6/6+9/9 | 95/25, 6/6+9/9 |
| F_190 (cure) | 102/26, 6/6+9/9 | 102/25, 6/6+9/9 | 102/25, 6/6+9/9 |

T-files: F arms all T_0to_0..T_5to_5 (6 files) every run, identical sets F_SXCD vs F_190 (T_0to_0 present x3 = F01 seated, same convention as 186 C01; GT graph 7x7 with node 6 isolated/unscored). Run dirs /data/gpfs/projects/punim2657/sfs_main/pota190_run_<JOBID>/, per-run pota190_fetch.tgz (426 copy at artifacts/pota190/pota190_fetch_33485426.tgz).

**5. Verdict: PASS.** F_190 holds the 81 bar exactly (6/6+9/9 x3) with the doubled 258-dot forest walk replaced by a single 124-dot closed loop. Falsifier (owned in advance: F_190 below 6/6+9/9 any run, or Total/pruned collapse vs same-run F_SXCD) NOT triggered -- generation 102 vs 95 (deterministic), pruned 25-26 vs 25-27 (assembly nondeterminism band per ticket 90). Controls green (A 8/8+15/15, F_orig 6/6+9/9 reproduces 81). Net: thin-loop input is bar-neutral on Pot F (no uplift available -- bar already perfect -- and no regression). No further input-side iteration proposed on F01.
