# 201 - Do our thinned loops speak the author\u2019s words (laptop leg)

Status: open
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
