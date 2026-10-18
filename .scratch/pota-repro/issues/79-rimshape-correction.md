# 79: C02/C04 rim-shape correction

**What to deliver:** 02-04 seated without the 17mm slide via corrected rim content.

**Answers:** E1

**Blocked by:** 77 (landed WHY-NOT-MEASURED, 12 jobs COMPLETED: all 4 reweight arms NULL, seat bit-identical 2.52deg/17.37mm; slide wins on rim-coincidence count NOT 3D overlap; reweighting family EXHAUSTED over 21 repeats with 76) + 76 (gates + refinement null, 9 jobs) + 74 (valley bound: fresh overlap 24.3% at GT vs 45.2% at search seat; user chose rim-shape correction over new-criterion / parking C, 2026-10-18).

**Status:** ready-for-agent

**Starting position:** correct the C02/C04 rim SHAPE prep-side so the overlap hill peaks at truth — the search stays untouched (proven over 21 repeats). Candidate directions, one variable each: (a) re-walk C02/C04 lips with the 75 guard recipe (they sit off-lip ~5-6mm med — the hill shift may shrink with on-lip content); (b) lip-face-constrained densification toward ORIG spacing (1.8mm uniform, zero teleports — 46 H1 recipe, no ORIG points); (c) your own shape correction. Prep-side scratch copies; S24 swaps as the base bundle (73/74 read-only). Zero ORIG points in any fix; ORIG evidence-only (gate ruler).

**Rules:** land with fresh-vs-ORIG overlap share at GT at/above ORIG-at-GT 42.7% AND 02-04 relative translation toward <=10mm at same rotation + E2E at or above 2/3+1/3 x3 same-binary + controls green (C ORIG 4/4+5/5, A 8/8+15/15) in same runs; renders (eye-check); E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats >=3 per condition; SingleOverlapTest@100/RP/CheckGraph-150 stay unless the shape mechanism names them.

- [ ] Shape-correction arms, one variable each
- [ ] Gate (overlap share at GT) + E2E rerun x3 or measured why-not
- [ ] Job IDs + sacct states

## Comments (lead landing, 2026-10-18 — worker silent post-completion, tallies collected by lead)

E2E 33302163/64/65 all COMPLETED 0:0. C_B = C_C = C_S24base = 2/3+1/3 x3 bit-identical; C_orig 4/4+5/5; A 8/8+15/15. NULL: shape arms did not move the pair. Render artifacts/pota79/C79_gate_overlays.png eye-checked — B arm overlays S24base exactly on C02+C04: the guard re-walk reproduced the same off-lip loop, so re-walking cannot correct this shape; a different loop (not a re-walk) is needed. C02 stays a shape problem per 80 (fused, swap will not cure).
