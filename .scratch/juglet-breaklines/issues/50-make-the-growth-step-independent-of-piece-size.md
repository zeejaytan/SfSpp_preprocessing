# 50: Make the growth step independent of piece size

**What to build:** the growth step `S` stops being derived from a sherd's bounding-box
diagonal and becomes one absolute physical length for every piece, so that "turn per step"
means the same thing on a big sherd and a small one. Then the 17 corpus pieces are swept
again at that single step to see whether their break thresholds converge.

**Answers:** U19

**Blocked by:** None (can start immediately)

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-10-31)
**Branch:** 50-make-the-growth-step-independent-of-piece-size, in /c/PR/worktrees/sfs/50

**Worker:** unassigned
<!-- Who executes it: the dispatcher replaces `unassigned` with the worker's agent id or a
short session label. `lead — <why>` plus `ticket_close.sh --lead-executed` is the recorded
lapse, for the case where the session that wrote the ticket had to run it. -->

- [ ] `S` no longer depends on the piece's bounding box; every piece in a run grows at the
      same step unless the cloud is too sparse to support it
- [ ] All 17 corpus pieces swept at that one step, per-piece break threshold measured
- [ ] Pot A PA01 and PA08 thresholds converge (they are 9.9 and 4.3 deg today, a 2.3x split
      on one pot, and the split is the defect this ticket removes)
- [ ] Code tickets: branch merged into main and pushed, no job still running from it,
      worktree removed, branch deleted locally and on GitHub

## Why — the measurement this ticket rests on

Run `20261031-2145_158ddc6_t50-threshold` (job 34115578) swept the real pipeline over all
17 pieces at 0.5 deg resolution. Per-piece break thresholds ("largest angle still giving two
face-sized clusters") came out 4.3 deg to >8.0 deg. The low outlier is **Pot A Piece 08 at
4.3 deg**, and it is not a worn edge — the conservator confirmed PA08 is freshly broken.

Diagnostics on the run's own growth clouds (jobs 34119158, 34119280, 34119558):

| piece | bbox diag | diag/200 | S used | capped | break threshold | threshold / S |
|---|---|---|---|---|---|---|
| PA01 | 172.6 | 0.863 | 0.600 | yes | 9.9 | 16.5 |
| PA02 | 137.2 | 0.686 | 0.600 | yes | 9.6 | 16.0 |
| PA03 | 132.2 | 0.661 | 0.600 | yes | 8.2 | 13.7 |
| PA04 | 116.3 | 0.582 | 0.582 | no | 8.4 | 14.4 |
| PA05 | 120.9 | 0.605 | 0.600 | yes | 8.3 | 13.8 |
| PA06 | 132.0 | 0.660 | 0.600 | yes | 8.1 | 13.5 |
| PA07 | 58.6 | 0.293 | 0.293 | no | 6.7 | 22.9 |
| PA08 | 54.1 | 0.271 | 0.270 | no | 4.3 | 15.9 |

Threshold / S is **14.8 +- 1.3 (cv 8.5 pct) across Pot A**; PA08's 15.9 is dead average.
In other words PA08 is an outlier only in degrees, not in the physical quantity that governs
the growth rule. It glues at 4.3 deg because its step is 0.27 mm, not because its edge is
different: the same break, walked in steps less than half as long, turns less per step.

The cause is `mesh_processing_headless.cpp:4526-4540` (ticket 37's adaptive rule):

```cpp
double sRaw     = diagMM / static_cast<double>(spacingSamples);   // spacingSamples = 200
double sClamped = std::min(0.6, std::max(s0MM, sRaw));
```

`diagMM/200` asks for "about 200 samples across the piece", which is a uniform number of
samples per *sherd*, not a uniform density per millimetre. Two sherds of the same pot then
grow at steps up to 2.2x apart. The angle that breaks a fresh edge is proportional to the
step (ticket 43's law, and the table above), so a single angle cannot be right for both.

The corpus does not cause this: all eight Pot A clouds are 1,000,000-point resamplings
(999,810 to 1,000,087). The divergence is introduced here, in the step rule.

## What to change

In `mesh_processing_headless.cpp`, the `piece` policy keeps its name but loses the bounding
-box term:

```cpp
// TICKET 50: the step is one absolute length, not a fraction of the piece.
// diagMM/200 made the step a property of sherd size, so two sherds of one pot grew at
// steps 2.2x apart and the angle that breaks an edge (proportional to the step) split
// with them: PA01 9.9 deg vs PA08 4.3 deg on the same pot, same fresh break.
// The measured spacing stays as a floor only, so a sparse cloud is never sampled finer
// than its own data.
double sUniform = 0.6;                       // SFS_SPACING_MM overrides
double sClamped = std::max(sUniform, s0MM);  // std::min(0.6, ...) cap is gone
```

Requirements:

1. `SFS_SPACING_MM` (default 0.6) sets the uniform step. `SFS_SPACING_POLICY=fixed` keeps
   working exactly as today (0.6, no measurement). `piece` keeps its name for continuity
   and is the default.
2. The `[SPACING-22]` log line must keep reporting `diagMM`, `s0MM`, `rawMM` and `S` so the
   change is auditable from a run log, and must add `uniformMM=` and `floorFrom=` (`uniform`
   or `s0`).
3. No other threshold, tolerance, growth rule or merge rule moves. `g_effectiveSpacingMM`
   and `g_pieceDiagMM` keep their meaning; `[COUNT-22]`, `[GROWTH-45]` and the merge scale
   factor keep reading them.

## What to run

One sweep, all 17 pieces, one uniform step, the same instrument shape as
`runs/20261031-2145_158ddc6_t50-threshold` (`submit50c.sbatch` is the template: stage with
`stage_synth_p40.sh` in `REAL-RELEASED-CLOUD` mode, run the binary per theta, `rm -rf Temp`
between thetas, parse `[STATUS-23]`).

- Step: `SFS_SPACING_MM=0.6` for all 17.
- Juglet thetas: 4, 6, 8, 10, 12, 14, 16 (the threshold is predicted to rise, because the
  step rises for the fine-sampled pieces).
- Pot A thetas: 4, 6, 8, 10, 12.

**Prediction to test, stated before the run:** with one step for all, every Pot A piece
reaches its threshold at the same angle, and that angle is about **8.9 deg** (14.8 x 0.6).
PA08 in particular moves from 4.3 deg to within 1 deg of PA01's 9.9 deg. If PA08 stays near
4.3 deg while PA01 stays near 9.9 deg, the step rule was **not** the cause and this ticket's
diagnosis is wrong — say so in the ticket rather than adjusting the numbers.

## Evidence to return

1. The `[SPACING-22]` line for all 17 pieces, showing one `S` value.
2. `threshold50b.tsv`: piece, theta, outcome, cluster sizes — the raw sweep.
3. A per-piece threshold table with the threshold/S column recomputed.
4. A statement of whether PA01 and PA08 converged, with both numbers.
5. Job ID, run directory, `sacct` State/ExitCode.

Do not commit, do not push, do not edit `intent/`. Report into `## Comments` at the bottom.
