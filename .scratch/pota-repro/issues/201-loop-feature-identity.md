# 201 - Do our thinned loops speak the author\u2019s words (laptop leg)

Status: landed (lead 2026-10-20: B09/A07 INTRINSIC -- thin halved word agreement; B04/J03 exonerated -- downstream; thickness leg inconclusive)
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
User decision (m04641, option 1): LAPTOP LEG FIRST. The D chain improved rim geometry (rim-truth med) but improved rims do not seat. The assembler scores (a) LCS token features over ordered xyz and (b) thickness gating (0.8mm Cond4 tolerance) -- neither is visible in the mesh overlays of 199/200. Measure, on the LAPTOP, whether our thinned loops carry the SAME features the author\u2019s loops carry for the same piece. No E2E in this ticket.

## Legs (all laptop-side, numpy, read-only inputs)
1. LCS-feature identity: replicate the assembler\u2019s LCS token extraction (feature_matching.cpp -- read the pinned source, do not guess the token rule) and run it over (i) our thinned loop, (ii) the author\u2019s ORIG loop, for the same piece. Report token-level agreement (shared LCS length / content), for B09 (gate-green, dropped), B04 (reshaped, dropped), J03 (cured, unseated), A07 (improved, dropped), C01 (cured, SEATED -- positive control). If C01 agrees strongly and the dropped four do not, the fault is intrinsic to our loops; if all five agree, the fault is downstream (competition/pruning).
2. Thickness validity: replicate GetThickness() (as ticket-53 did on Pot A) on the thinned loops + their meshes; report valid rate and median vs the author loop\u2019s. A systematic shift >= 0.8mm fails true pairs by construction.
3. Confounders list: start-point offset, travel direction, spacing uniformity, smoothing shrink (arc delta) per loop -- each quantified, so a mismatch in leg 1 can be attributed (e.g. \u201csame words, different start point\u201d vs \u201cdifferent words\u201d).

## Boundary
Laptop only. Inputs read-only: thinned loops (.scratch/pota194_repro/, artifacts/pota193/, 196 artifacts), author loops (ORIG/from pota41 tgz), meshes, pinned SFS++ source for the token + thickness rules. New scripts + numbers under .scratch/pota201_repro/ + artifacts/pota201/ (untracked) only. Do NOT touch tracked files except this ticket. COMMIT NOTHING.

## Constraints
Do NOT reimplement the token rule from memory -- cite file + line of the replicated logic. C01 MUST be run as the positive control (it seats; its agreement level calibrates what \u201cmatch\u201d means). If a dropped piece agrees at C01\u2019s level, say so plainly -- that exonerates the loop. No E2E, no sbatch, no bundle changes in this ticket.

## Acceptance
Per-piece (B09, B04, J03, A07 + C01 control): LCS agreement numbers, thickness valid-rate + median vs author, confounder table. One verdict line per piece: intrinsic (loop speaks different words / fails thickness) vs exonerated (matches at C01 level -- fault downstream). Plus the cross-piece verdict: does leg 1 explain the seating pattern (C01 seats, four do not)?

## Required evidence
Comments: script paths, source lines cited for token + thickness rules, per-piece numbers table, per-piece verdicts, cross-piece verdict. Final output: same, self-contained.

## Comments (lead 2026-10-20: worker finished silent -- numbers in artifacts/pota201/p201_numbers.json, lib cites feature_matching.cpp:72-95/215-320/1479-1490 + filter.cpp:50-265, verbatim replication; lead verdict below)

Metric: longest run of matching quantized (Dist/Height/Theta) tokens vs author loop, as fraction of min length (fwd_cov); cond4_cov = same run additionally requiring thickness agreement (GetThickness repl with mesh-vert proxy -- documented deviation, ticket-53 method).

| piece | thin_fwd | fresh_fwd | thin_cond4 | fresh_cond4 | thick shift (mm) | verdict |
|---|---|---|---|---|---|---|
| B09 (dropped) | 0.286 | 0.600 | 0.114 | 0.600 | 0.01 | INTRINSIC: thin HALVED word agreement (0.60->0.29). Fresh rim already spoke author words; resample rewrote them. Geometry gate-green, words damaged. |
| A07 (dropped) | 0.475 | 0.762 | 0.475 | 0.524 | 0.07 | INTRINSIC: same story (0.76->0.48). Thin improved rim-truth 0.45->0.35 while damaging the token run the assembler reads. |
| B04 (dropped) | 0.535 | 0.559 | 0.333 | 0.346 | 0.15 | EXONERATED at loop level: words unchanged at seating level. Dies downstream (competition/pruning). |
| J03 (unseated) | 0.556 | 0.434 | 0.062 | 0.063 | 0.27 | EXONERATED: thin improved words to C01 level, still unseated. Search-basin miss stands (193). |
| C01 (SEATS, control) | 0.544 | 0.028 | 0.049 | 0.028 | 0.07 | Calibrator: seating needs fwd ~0.5+; fresh doubled 0.028 seats nothing, thinned 0.544 seats. |

Cross-piece: fwd agreement predicts seating (C01 0.544 seats; J03 0.556 + B04 0.535 at that level but fail downstream; B09/A07 damaged below it by the thin itself). cond4_cov is low even for seating C01 (0.049) -- thickness leg INCONCLUSIVE under the mesh-vert proxy; do not cite thickness as the driver.
Answer to m04633: improved geometry != improved words. Resampling rewrites the quantized token sequence; rim-truth (distance) and word agreement moved in OPPOSITE directions on B09/A07. That is why closer-to-author lines do not assemble.
