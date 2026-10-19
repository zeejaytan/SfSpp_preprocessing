# Why is BoundaryEstimation silent at the gap stations?

GOAL: NAME THE MECHANISM THAT SUPPRESSES EMISSION AT EACH COVERAGE GAP.

**Answers:** E1

**Blocked by:** 168 (all 13 gaps owned UPSTREAM ADMISSION: bag holds no dot <2mm at gap stations; walk complete vs bag), 163 (substrate = PCL BoundaryEstimation on PointNormal sheet from cleanSamples), 160/149 (labels, thin-line bag, gate scripts).

**Status:** ready-for-agent

**User direction (2026-10-20):** look at BoundaryEstimation -- why did it skip those spots.

**What to deliver:** for EACH of the 13 gap stations from 168 (residue ledger + coverage plot artifacts/pota168b/p168b_coverage.png; gap-station list in .scratch/pota168b_repro/): reconstruct the estimator's decision at that site -- neighbourhood it saw (support count/radius vs local sheet density), angular-gap score vs threshold, normal quality, sheet state (overextended? hole-adjacent? fold?). Per gap, one of: (i) MECHANISM NAMED with numbers (e.g. support shortfall N<M at radius r; angular gap g<theta; normal flip), or (ii) estimator FIRED but dot lost downstream (say where: snap, veto, dedup) -- then the gap is mis-owned and say so honestly.

**Bar:** every gap station carries a measured cause (numbers from the estimator's inputs, not adjectives); any fix proposed is gated on the same 98-frame (fresh bar 5.61/22.9) and must not regress Pot A. A station whose cause cannot be measured lands as unmeasured-with-reason, not as a story.

**Starting position:** 168 Comments (gap ledger, coverage, bag definitions); 163 Comments (BoundaryEstimation call-chain + code sites); 155 Comments (worktree + build, if a probe variant is needed); 160/162 Comments (labels, gate scripts). New scratch pota169_repro/; renders artifacts/pota169/.

**Rules:** estimator inputs read-only unless a probe variant is built (worktree-local, restore byte-identical); same-binary ORIG control alongside or void; COMMIT NOTHING; tickets 39-168 read-only; Comments-only ticket edits; sacct recorded; eye-check renders.

- [ ] per-gap-station estimator decision reconstructed with numbers
- [ ] each gap: mechanism named OR honestly unmeasured OR mis-owned (lost downstream, where)
- [ ] any fix gated both pots, no Pot A regression
- [ ] Verdict + render paths
