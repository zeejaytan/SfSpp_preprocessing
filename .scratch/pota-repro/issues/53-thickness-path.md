# 53: Thickness path — the live gate the matcher actually reads

**What to deliver:** honest edge strengths toward author scale via the thickness estimate — or the measured reason it cannot close the gap.

**Answers:** E1

**Blocked by:** 52 (column-7 DEAD — never loads, R4 killed, H4 closed; normals live but destructive-only; honest ≤ size11/inlier26 vs 45-65 frontier 6/6) + 46 (live thickness slot `feature_[6]` from `GetThickness()` — surface + normals — gating LCS via Cond4).

**Status:** results-in (worker 2026-10-17, COMMIT NOTHING)

**Starting position:** the only live content gate left is `GetThickness()`: computed per rim point from surface geometry + normals, read by the matcher through Cond4. Open questions: what does it return on OUR rims vs ORIG rims? Does OUR thickness disagree (surfaces differ — recall ticket 21's fused walls, T21 split)? Can an honest prep-side change (better normals? surface-side fix?) move it toward ORIG behaviour? ORIG evidence-only (44-asterisk rule); zero ORIG points in any fix.

**Rules:** land ONLY with honest edge-strength lift toward ORIG scale AND/OR E2E lift ×3 same-binary runs + controls green (B ORIG 9/9+15/15, A 8/8+15/15) in same runs + B gate 15/15; gate-clean (strict must not regress); render (eye-check); prep-side scratch copies; assembler E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition.

- [x] Thickness measurement: ours vs ORIG, per-rim, at GT seating
- [x] Honest prep-side arms, one variable each
- [x] Job IDs + sacct states

## Comments (worker, 2026-10-17, COMMIT NOTHING)

**Bottom line: measured why-not — no strength lift. OUR p2 thickness is systematically broken (median 1.2mm / 6 q-bins below ORIG, 33% invalid), which chops true 2-1 runs at the Cond4 gate; the defect is in OUR Surface_1 shape near the lip, and the one honest corrective arm (surface-fit normals) proved destructive 3/3. Honest 2-1 edge LOST vs T50; best honest stays size10/inlier22 vs ORIG's five 2-1 edges sizes 8-19/inliers 30-78.**

**Thickness measurement (numpy replication of assembler `GetThickness`, filter.cpp:221 — ray along breakline normal into `sur_out_` = Surface_1; rigid-invariant so native frames compare fairly; ORIG evidence-only, zero ORIG points used):**
| rim | valid | median | mean | std | max | ORIG same-rim |
|---|---|---|---|---|---|---|
| OUR p2 Bl0 (187pt) | 124/187 (66%) | 1.73 | 2.19 | 3.62 | 37.4 | 146/150 (97%), med 2.90, std 1.31, max 5.06 |
| OUR p1 Bl0 | 175/191 (92%) | 4.44 | 4.44 | 0.68 | 5.57 | 198/210 (94%), med 4.31, std 0.67 — MATCHES |
- p1 proves the pipeline CAN produce ORIG-like thickness; p2 is the broken piece, not a global bias.
- Of OUR p2's 62 invalid: 56 sign-flips (nearest surface point behind the normal ray) + 6 perpendicular-misses; 3 wild values 10–37mm (ray escapes across the pot).
- The median shift alone kills Cond4: quantized |1.6−2.8| = 1.2mm > 0.8 tolerance (4×Q_size[3]=4×0.2), so true 2-1 pairs fail the gate systematically; −1 points pass vacuously (Cond4 stays true) but carry no discrimination.
- Render `SfSpp_preprocessing/artifacts/t53_p2_surfrim.png`: OUR Surface_1 hugs the rim at ~0.5mm with spiky noise along the whole run; ORIG stands off with a smooth structured profile (3–5mm wall spans, ~1mm lip span). Eye-checked.

**Offline arm screening (no E2E spent where measurement already rejects):**
- SWAP (p2 vs Surface_0): REFUTED — Surface_1 is the outer wall on both sides (OUR p1-S0 med 0.44 = inner graze, same pattern as ORIG p2-S0 med 0.25). No T21-style wall swap; assignment correct.
- TRIM (delete p2 Surface_1 pts within R of rim): REFUTED — valid rate DROPS with R (110→75→55→41→27 for R=1.0→3.0mm). Nearby points aren't just poison; without them the ray finds nothing. Surface must be reshaped, not trimmed.
- NORMALS-CAUSE: WEAK — bad-sign indices overlap surface-fit/file-normal disagreements in only 13/62 cases. Normals aren't the driver.

**Arm SURFNORM (one variable: p2 Bl0 file normals → local-surface-fit normals from OUR Surface_1 ≤4mm plane fits, oriented to file normal; coords+col7 textually identical, 17/18 files byte-identical, surfaces untouched):**
- Offline: valid 124→135/187, Cond4 all-pairs pass 7.4%→16.1% (metric discredited as predictor — T52-NORM scored 9.8% yet killed the edge — E2E decides).
- Gate (GT-placed strict): 1-2 19/19 (no regression), total 590 (T50 592), 15/15 — GREEN.
- Render `SfSpp_preprocessing/artifacts/t53_lip_check_surfnorm.png`: mating span tracks p1 rim continuously, no divergence (coords identical to eye-checked T50). Eye-checked.

**E2E ×3** (cure-potA @ bffefb6, BASE-env, LINK-SHIM-OK + LINK-FORKMAIN-ABSENT-OK + DRIVER-SHIM-OK asserted in-script, B-bundle-match asserted; all sacct COMPLETED 0:0, ~14–15 min each):
| jobs | B fresh | p2 | controls (same runs) |
|---|---|---|---|
| 33243629/30/31 | 4/9 ×3 identical, seated {1,3,4,7}, VERBOSE pairs {1-3,1-4,3-7}, forest 85 | honest 2-1 edge ABSENT 3/3 (no x=2 LCS edge at all); best honest 5-2 size10/inlier22, 6-2/8-2 size9/22 (max inlier 22 = T50 level, wrong pair) | B ORIG 9/9+15/15, A ORIG + A fresh 8/8+15/15 ×3 |
- SURFNORM is DESTRUCTIVE in the T52-NORM direction (second confirmation that normals are live content with only a destructive direction tested): it removed the one honest 2-1 edge (T50 size9/inlier16) instead of strengthening it. Seated pieces unchanged {1,3,4,7}; forest 85 (no R3-style blowup).

**Honest-vs-ORIG scale (same-binary evidence):** ORIG 2-1 = five edges (size19/34, 11/38, 15/30, 10/36, 8/78); honest best now = size10/inlier22 on a non-1 pair, 2-5× below with the target pair absent. p2 starves deterministically 9/9 runs across T50/T52/T53.

**Successor:** the thickness path is now fully characterized but not fixable by one-variable scratch surgery — OUR p2 Surface_1 needs reshaping near the lip (surface-regeneration pipeline work, T21-class, Pot-B-side), or beam-side rerouting around the 45–65 frontier (ticket 43 lane). Prep-side point levers (sequence/50, sampling/49-R3, column-7/52, normal-smoothing/52, surface-fit-normals/53, trim/swap screened offline) are exhausted. Work dir `/data/gpfs/projects/punim2657/pota53_repro/` (measure/diag/trimtest/swaptest/gate/render scripts, SURFNORM bundle + md5s, 3 slurm outs); tickets 49/50/51/52 + p47/p49 flaggers untouched (read-only).

**Successor:** cross-pot generalization of the B recipe (C–J share the drowning shape).
