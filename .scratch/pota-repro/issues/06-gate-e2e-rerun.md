# 06: Gate + E2E re-run with pristine controls

**What to build:** the scored proof that the fresh chain reproduces the authors' input: Gate 15/15 + end-to-end 8/8 + 15/15 at k=5/b=3 Table V Pot A, pristine controls alongside.

**Answers:** E1

**Blocked by:** 03-header-writer-fix, 04-surface-interior-first, 05-sfs-axes-port.

**Status:** results-in — SHORTFALL. Gate met, E2E bar not met; follow-up ticket 11 cut. Lead verification 2026-10-15: jobs 33051437/33054720/33055873 all COMPLETED 0:0 per sacct (execution confirmed); scored numbers rest on worker log reads (lead has not re-read logs); render PNG not in this checkout (worker-local artifacts/, unseen by lead).

## Comments (worker one-shot 558c2362, 2026-10-15; pasted by lead — worker's checkout lacked pota-repro/)

2026-10-15 POTA-06 run (jobs 33051437/33054720/33055873, fork HEAD `14ccae6`): Gate **15/15** on fresh _0 rims (strict d<2mm & n·n>0.85; weakest pairs involve p2: 1-2 has 3 inliers, 2-8 has 2); E2E fresh **4/8 + 3/15** vs ORIG **8/8 + 15/15** in the same assembly job (33054720, same binary — authors' result reproduced through the untouched program). Exchange pattern as predicted (p1,2 kept; p3–8 swapped; p2 fails both guards, ratio 0.015<0.10, margin 1.43<2.0). Headers byte-format-faithful (`# 5 193 0` vs `# 5 208 0` style); all 8 headers `# <n> <m> 0` valid. Correct core {1,6,7} (edges 1-6, 1-7, 6-7); 4,5,8 misplaced (54–161°, 146–677 mm); 2,3 unplaced. Hypothesis forest 522 fresh vs 124 ORIG (pruned 57 vs 70). Prime suspect (hypothesis, not fact): ticket-14 patch-rim segments + tickets-05/06 resampling changed p02–p05 rims (byte-different vs Sept-28; p01,p06–p08 identical); a header-less short-rim bundle previously assembled 8/8+15/15 through the same binary, so rim length/content — not `#` headers — flipped the outcome. p2 alone does not explain it: observed 3/15 far worse than ticket 04's ~11/15 prediction. **E2E bar not met — follow-up: ablate ticket-14 patch segments on p2–p5 and re-run E2E (ticket 11).** Compile check of `edgeline_extraction.cpp` @ `88bf1eb` lineage: syntax-only in-container g++, PASS exit 0 (33055873) — closes 03's deferred compile proof. Control note: `d5ee6865` appears nowhere on Spartan; the control actually used is the pinned pristine assembly tree `9195c01` (task-3 recipe) + same-binary ORIG arm. Spartan leftovers: `pota06_fresh/`, `pota06_bundle/SfS_pp/`, `sfs_main/pota06_verify_33054720/`, sbatches `run_pota06_all` / `run_pota06_assembly` / `compile_check_88bf1eb`. Render (unseen by lead): worker-local `artifacts/pota06/pota06_gt_vs_estimated.png`.

Lead reading: **the rims are right, the search gets lost** — method-failure lead on current-HEAD rims (category 1), not a broken ruler. Gate 15/15 means every fresh rim sits on its true join within tolerance; the graph search then drowns the 3 true edges in 522 noisy hypotheses. E1 `Where it stands` proposal for lead: fresh chain reproduces author *input format* + gate, not yet the *reassembly*.

**Lead revision (2026-10-15, ticket 05 verdict):** ticket 05 proved anchor-parity unreachable by the reference algorithm itself (winners 5–70× lower Cao cost than NURBS anchors, 10–86° off; MATLAB method-2 refine a silent no-op). This ticket runs on the authors' NURBS/ORIG axes. Piece 2 guard-kept by design — disposition required in Comments.

- [ ] Fresh chain vs ORIG arm on Pot A gate probe (per-pair 15/15) + full E2E (8/8 + 15/15)
- [ ] Pristine-pin controls at `d5ee6865` on both sides; laptop poll per sbatch with final sacct State/ExitCode in ticket
- [ ] Geometry render before/after for the fix that moved the number (view resolves the tested scale) + measurement pair
- [ ] E1 `Where it stands` update proposed in ticket Comments for lead to write into intent/ (worker does not edit intent/)
