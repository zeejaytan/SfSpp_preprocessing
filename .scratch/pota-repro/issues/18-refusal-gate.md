# 18: Refusal gate for unidentifiable fragments + H base-cap renders

**What to build:** the admission test ticket 17 prescribed — teach the finder to refuse fragments it cannot identify, and prove the refusal with a confusion matrix. Plus the eye-check on the base-cap claim.

**Answers:** E1

**Blocked by:** 17-poth-diagnosis (mechanism + thresholds + protocol below).

**Status:** results-in

**Starting position (from 17, jobs 33108716/33108743/33109148):** Pot H's collapse is a stack of three proven effects — base-type fragments (H01–H04: normals 2–25° off-axis, fragments touch the axis) with truth support 6–17% under the 10% minfrac floor; vote dilution + x1.1 dedup kills on multi-axis pieces; per-axis support below any identifiability floor (vote-best GM 1.6–1.85/pt on H vs ≤1.2 on all passing). Proposed gate (finder-observable only, no shipped key): REFUSE when BOTH (1) vote-best GM cost > 1.4/pt AND (2) round-1 peel-winner share < 0.20. Thresholds provisional — confirm on the full B–J distribution (especially J tails) in this ticket.

- [ ] Implement the gate in a Spartan-side experiment copy (new `p18-stage/`; `p15-stage/` stays frozen); run ALL B–J pieces (155); report the confusion matrix: refusals among current fails (want ≥9/11 H + D30/J-tail fails) vs refusals among current dirpass pieces (want ZERO — especially G07, D32, small-J passes)
- [ ] If thresholds need moving to meet the confusion bar, move once with the full matrix before/after; no second tuning round on your own
- [ ] Renders: H01–H04 meshes with shipped axis drawn, top + side views, mm scale, equal aspect, to `artifacts/pota18/` — the base-cap geometry claim needs the lead's eye before H3 closes (Needs-eye:)
- [ ] Job IDs + sacct states; no commits; Comments-only ticket edits

**Successor:** E2E gate proof on admitted fragments (refusals excluded by rule, not by hand).

## Comments (worker, 2026-10-16)

**Gate implemented and run over all 155 B–J pieces.** `af_gate.m` (new file in the
run dir, NOT in `axle_finder/`) replicates `af_find_seq` round-1 exactly on the
full cloud — vote 6000/raw seed+1, cluster top-1000 maxk=1, orient, refine top-1
sub then full, tight-inlier share — then REFUSE iff cost_pt > thr AND share < thr
(cost_pt = vote-best raw GM cost per 10%-subsample point; share = refined
round-1 winner inliers / N0; both finder-observable, no shipped key). `p18_run.m`
refuses (chain skipped) or runs frozen `af_find_all` + scores vs shipped (test
key only). Sanity: G-pot gate stats reproduce ticket-17 reference values exactly
(G07 0.985/0.503 vs 0.98/0.503), and every admitted chain reproduces the
ticket-10 dirpass verdict piece-for-piece. Frozen provenance: Spartan
`potsac-p18-run/axle_finder` is a `cp` + `diff -r`-verified copy of
`potsac-p10-run/axle_finder`; laptop `af_find_all.m` MD5 matches it
(1ec3b33802aceca5580e24acd216df0c). `p15-stage/` untouched. Staging: laptop
`.scratch/pota-repro/p18-stage/` mirrors Spartan `potsac-p18-run/`.

**BEFORE matrix (provisional thr cost>1.40, share<0.20) — 15 refused:** all 11 H
(H01 1.770/0.090, H02 1.790/0.115, H03 1.774/0.085, H04 1.820/0.060, H05
1.668/0.151, H06 1.610/0.172, H07 1.666/0.152, H08 1.658/0.143, H09 1.678/0.137,
H10 1.698/0.108, H11 1.641/0.149) + C03 (1.619/0.159), D28 (1.607/0.125), I30
(1.477/0.185), J03 (1.638/0.152). Against frozen ticket-10 verdicts (117
dirpass / 38 fails): fails-caught 12/38 (H-fails x10 + D28 + I30); false
refusals 3/117 (H10, C03, J03 — all direction-pass/position-over pieces).
D30 (1.542/0.217) misses by 0.017 of share; every J-tail/D-tail/count/landscape
fail sits at share 0.25–0.74 with cost 0.88–1.46 — inside the pass cloud.

**Threshold move (the single allowed one): share 0.20 → 0.22, cost stays 1.40.**
Candidates that also catch J-tails (share<~0.30) refuse ~15+ passes (E15
1.489/0.232, I03 1.434/0.268, J04 1.407/0.281, C06 1.286/0.252 …); candidates
that drop the 3 false refusals (share<0.15, or cost>1.65) lose D28/I30 and keep
H10 anyway. 0.22 takes exactly one more piece — D30, the ticket's named piece —
with zero new false refusals and zero lost fails.

**AFTER matrix (cost>1.40, share<0.22) — 16 refused, measured (D-pot rerun job
33110638, all other gate stats bit-identical, deterministic same-seed):**
fails-caught 13/38 (H-fails x10 + D28 + D30 + I30); false refusals 3/117
unchanged (H10 — the documented luck-pass, 0.108 clears the 0.10 floor by 0.008
per ticket 17; C03, J03 — direction-pass/position-over). Sensitivity 13/38
(34%), specificity 114/117 (97.4%), H-recall 11/11 refused.

**Honest remainder for the successor (not tunable here):** the gate isolates the
H-type wholesale-collapse family (flat GM landscape, per-mode support below any
floor — costs 1.61–1.82 vs ≤1.35 on nearly all passes) but is blind by
construction to the other two fail families, which show HEALTHY round-1 support:
count/selection misses (C02 1.414/0.281, F07 0.909/0.597, J08/J11/J13/J14
0.26–0.38) and landscape pockets (B03 1.158/0.405, D27 0.880/0.546, J16/J17).
The ticket bar's "D30/J-tail" half conflates mechanisms — no AND-threshold on
these two statistics reaches the J-tails without mass pass refusals. A
count/landscape signal (not round-1 support) is needed for those; the E2E gate
proof should scope itself to the identifiability (H-type) refusals.

**Renders (Needs-eye for the lead):** `artifacts/pota18/H01..H04_axis.png` —
each H01–H04 mesh (Meshlab OBJ, 8.5–21k verts) with its shipped axis drawn, top
(along axis) + side (perp) views, mm ticks, 10mm scale bar, equal aspect.
Measured along the way: H01–H04 carry exactly ONE shipped axis each (nA=1).
Worker eye-check: all four read as thin plates/patches pierced nearly
perpendicularly by the shipped axis — H01 shows a foot-ring-like arc ridge in
the top view; H02/H04 are thin slivers/plates in side view — consistent with
the H3 base-cap claim. Caveat: H02's top panel is mostly empty (long axis line
dominates auto-zoom); the side panels carry the evidence. Render bug caught and
fixed: Meshlab OBJs store `v x y z r g b` — sscanf cycled the 3-spec format
into 6 columns and `patch` rejected it (probe jobs 33110062/33110451); fix keeps
xyz only.

**Jobs (all COMPLETED 0:0, `sacct` direct):** 33109695 p18G 00:02:18 (smoke);
33109696 p18render 00:01:26 (attempt 1, render bug); 33109949 p18B 00:02:22;
33109950 p18C 00:02:56; 33109951 p18D1 00:06:06; 33109952 p18D2 00:03:16;
33109953 p18E1 00:05:08; 33109954 p18E2 00:02:59; 33109955 p18F 00:02:14;
33109956 p18H 00:02:06; 33109957 p18I1 00:06:38; 33109958 p18I2 00:02:17;
33109959 p18J 00:03:10; 33109960 p18render 00:01:11 (attempt 2, same bug);
33110062 p18probe 00:01:33 + 33110451 p18probe 00:01:39 (diagnosis);
33110638 p18D2b 00:02:14 (after-matrix, thr 1.4/0.22); 33110639 p18render
00:02:02 (4 PNGs). No commits; Comments-only edit.
