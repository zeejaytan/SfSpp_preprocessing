# Filtered thin-line walk — test the walk on the true edge alone

GOAL: WALK THE THIN LINE.

**Answers:** E1

**Blocked by:** 148 (band = inner 116 true-edge + outer 195 face-loop; ORIG-free fix = drop face-align >+0.5, ~183 dots; predicted width ~1.0, honest uncovered ~25 at (102,120)) + 144 (M144 recipe: recovery trigger + calibrated snap) + 147 (parity instrument)

**Status:** ready-for-agent

**What to deliver:** apply 148's ORIG-free face-align filter to the 314 bag (drop nearest-face align >+0.5; NO radial gating vs ORIG — production-illegal), re-derive the walk with the banked M144 machinery (heading-guard + recovery + per-bag latch + state trigger) on the ~131-dot thin bag, and report: (1) walk topology on the thin line (flips/selfint vs M144's 38/47 and parity's 2/0 — bar: at-or-better than parity with coverage held outside the honest span); (2) the honest uncovered set — predicted ~25 at (102,120) + small spans; any uncovered OUTSIDE the predicted set is a finding, not a failure; (3) whether any M144 constant needed retuning on the thin bag (retune = finding about the recipe's generality). A walk that re-zigzags on the thin line refutes density-as-mechanism and reopens the walker.

**Starting position:** .scratch/pota148_repro/ (face-align tags per dot, inner-only gate numbers), pota144/145 (M144 recipe), pota147 (parity instrument). Login-node numpy only — no Slurm, no E2E. New scratch pota149_repro/; renders under laptop artifacts/pota149/ (thin-bag walk vs author, uncovered map).

**Rules:** ORIG Bl_0 ruler-only; control = reproduce 148's filter counts (~183 dropped, ~131 kept) first or stop; COMMIT NOTHING; Comments-only ticket edits.

- [ ] Thin-bag walk (topology vs M144 + parity bars)
- [ ] Honest uncovered set vs predicted (102,120)
- [ ] Recipe-retune report
