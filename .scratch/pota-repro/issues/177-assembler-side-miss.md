# Assembler-side miss: gated rim ties the bar, search does not move

GOAL: FIND WHY THE POT C ASSEMBLY DOES NOT SEAT WITH A CORRECT RIM, AND FIX IT.

**Answers:** E1

**Blocked by:** 176 (rim fix proven per-piece, E2E x3 honest negative: C_176 2/3+1/3, controls A_orig 8/8+15/15 + C_orig 4/4+5/5), 145 (cured-314 bundle also 2/3+1/3), 174 (edge side closed as not-the-blocker).

**Status:** results-in

**Standing evidence (do not re-derive):** (a) 176 C01 rim gated 0.95 vs author, installed in bundle (build log p176_build.txt, Spartan stage). (b) C_176 T estimates byte-identical to 145's to 0.01 -- a corrected rim did not perturb the search at all. (c) ORIG control (author rims) seats 4/4+5/5 in the same vehicle: the assembler CAN seat this pot. (d) Ferried inputs in .scratch/pota177_repro/inputs/ (T_1to_1/T_3to_3 + Acc for 176 C_176/C_orig run 33449864 and 145 C_FIN run 33398092). Staged Spartan logs: pota176_run_33449864/*_binary.log + slurm-33449864.out (hypothesis counts, scores, timing).

**What to deliver (analysis first, no new E2E until the mechanism is named):** (1) Mine the staged 176/145 logs: hypothesis counts per edge, score of the chosen seating vs the true seating (GT from bundle Ground Truth, ferried? -- fetch if missing), where C01's true placement loses (gated out? never hypothesized? outscored?). (2) Name the single mechanism: does the rim change fail to reach the scorer (feature caching/discretization?), does the true seating lose on score, or is it never generated? (3) Propose the minimal fix with a falsifiable prediction (e.g. score recompute on GT seating beats/misses chosen by X). STOP after the mechanism + proposal; the instrumented run is a follow-up ticket.

**Bar:** the mechanism named with numbers from the staged logs (hypothesis counts + scores, not adjectives), and a fix proposal with a numeric prediction. No new Spartan submissions in this ticket (worker has no SSH; lead relays only after the mechanism lands).

**Rules:** dataset read-only; tickets 39-176 read-only; edit this ticket's Comments section ONLY; COMMIT NOTHING; lead eyes every render/claim before write-back.

- [x] Log mining (hypotheses + scores, 176 vs 145)
- [x] Mechanism named with numbers
- [x] Fix proposal with numeric prediction
## Comments (worker, 2026-10-20 -- ANALYSIS, no new E2E; COMMIT NOTHING)

**Status: results-in (mechanism named with numbers + fix proposal with numeric prediction below). One gap owned: 176's P-file hypothesis counts + binary-log "Score :" lines are not on the laptop (only 9 T/Acc files ferried); P1 predicts them with no new run.**

**0. Log availability (honest record).** The staged-log paths (pota176_run_33449864/*_binary.log + slurm-33449864.out) do not exist laptop-side (searched .scratch + artifacts); this worker has no SSH. What IS staged: the 9 ferried T/Acc files (176 C_176/C_orig run 33449864 + 145 C_FIN run 33398092) + 145 fetch tgzs in artifacts/pota145 (P145_C_FIN.txt / P145_C_orig.txt hypothesis counts + GT_C ground truth + CSXC rims, extracted to .scratch/pota177_repro/fetch145/; fetch T_C_FIN cmp-identical to ferried inputs). All numbers below recomputed laptop-side, script .scratch/pota177_repro/pose_compare.py.

**1. Hypothesis counts + scores.** 145 C_FIN: Total number 45 -> pruned 8 -> 2/3+1/3 (P145_C_FIN.txt). 145 C_orig: 125 -> 40 -> 4/4+5/5. 176 C_176: P-file NOT ferried, counts unverified laptop-side. PREDICTION P1: Total 45 / pruned 8, identical to 145 (deterministic binary, bit-identical-x3 precedent in 145; T output identical per s2). Lead-checkable on Spartan stage with zero new runs. Per-edge counts + "Score :" lines (ranking_system.cpp:507 writes Score per state; main_pristine_batch.cpp:210/216 the totals) are Spartan-only; no score claim below rests on them.

**2. The search did not move -- numbers.** 176-vs-145 chosen T: T_1to_1 rot-diff 0.033deg / trans-diff 0.10; T_3to_3 0.040deg / 0.05 (matrix maxabs 0.098 / 0.048). Frame-invariant rel-edge T_1-vs-T_3: 88.86deg / 671.92 in BOTH (exact to 2 decimals; reproduces 145 s2 identity numbers) vs GT 02-04 90.67deg / 683.18: the counted edge sits 1.81deg / 11.26 off GT, unchanged. Same 2 T files present (T_1to_1 + T_3to_3); C01 unseated (no T_0to_0) in both. Wall time moved without decisions moving: C_176 3760s vs C_FIN 9331s (Acc files) -- 2.5x faster, same answer (the rim change reached feature-computation cost, not search decisions). Installed-rim delta (bundle, ONLY C01-Bl_0 differs in both): 145 = 310-pt M144 trace (gate med 3.97, cov2 31.9%) -> 176 = 439-dot TRUE walk (verified laptop-side: shape (439,3), steps max 14.8 / med 1.36 / n>5 3 = 176 s1 exact; bundle rim-truth med 0.95, <2mm 93.2% per 176 s7). ~3mm median improvement + 129 on-arc points changed NOTHING downstream.

**3. Mechanism (single): C01 dies upstream of final scoring -- the corrected rim never reaches a scored state.** LCS hypothesis generation (feature_matching.cpp:1473: quantized D/H/Theta 0.15, curvature 0.2, window MINIMUM_NUMBER) + pairwise pruning decide C01-involving pairs before sub-mm rim accuracy can matter; in both runs no C01 placement survives to a saved transform, so the final state-score ranking ("Score :" = sum graph_score_, ranking_system.cpp:455-457) never compares a corrected-C01 seating against the winner -- there is no outscoring event, only an absence. Residual branch owned: never-generated vs pruned needs per-edge LCS counts from binary.log (follow-up run logs them); the fix direction does not depend on it (both are search-side, pre-scoring).

**4. Fix proposal + numeric predictions.** Instrumented single C_176 run (no bundle change): (a) log per-pair LCS survivors into/out of PairwisePruning + winner "Score :"; (b) GT-force: seat the 439-dot Bl_0 at author GT pose, recompute state_score_. P1 (no new run): 176 P-file = 45 total / 8 pruned. P2: C01-involving pairs contribute 0 of the 8 pruned survivors. P3: GT-forced C01 state_score_ EXCEEDS the winner's "Score :" -- the scorer would prefer the truth if search ever visited it, so the fix goes to the search side (LCS quantizer/window or pruning threshold for C01 pairs; basin widening per 73/74 family), NOT scorer reweighting. If P3 fails (GT-forced scores below), the fix goes to scorer weights instead -- either way the measurement decides. STOP per ticket: the instrumented run is a follow-up ticket.

**6. Lead P1 check (2026-10-20, Spartan stage).** slurm-33449864.out C_176 block: Total number 40 / pruned 8 vs P1's 45/8 -- survivors EXACT (8/8), total off by 5 (rim change removed 5 generated hypotheses, none survived pruning anyway). Mechanism stands: no C01 placement reaches scoring either way.

**5. Evidence.** .scratch/pota177_repro/ (inputs/ 9 ferried files + pose_compare.py + fetch145/ extraction of pota145_fetch_33398092.tgz) + artifacts/pota145/ (P-files, GT_C, CSXC rims). Dataset read-only; tickets 39-176 untouched; nothing committed. No renders: no geometry moved (numeric analysis only), nothing to eye-check under AGENTS.md.


**Evidence-path note (2026-10-23):** paths under .scratch/pota1xx_repro/ and .scratch/pota22x/ cited above were removed by the scratch cleanup of this date (untracked intermediates; not recoverable). The numbers, quotes and verdicts in this ticket stand as recorded -- do not chase those paths or re-derive from them.
