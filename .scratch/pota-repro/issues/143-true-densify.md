# True densify — fresh dots on the true edge, not midpoints of old dots

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 111 (interpolation-densify +19 midpoints: greedy 93->112, gate 4.22, stall dot IDENTICAL — midpoints add no true edge info; upstream hypothesis named) + 121 (filter level exhausted) + 137 (floor proof: 8 is the floor under point-gate on this bag) + 139 (O37 open, upstream re-extraction named as the forward)

**Status:** ready-for-agent

**What to deliver:** denser TRUE dots, sampled from the mesh — not interpolated between existing dots. Problem: every densify so far interpolated the existing bag (midpoints inherit the bag's errors and add zero new edge information). True density means going back upstream: re-run the extraction stages (boundary re-run at finer scale per 123's r1 finding + snap with the 2.5 leash per 124) with finer lip-gap sampling so new dots land on mesh the current bag never sampled, esp. spans C36/C46/C96/C173 + O37. Measure: new-bag size, new dots' distance-to-ORIG (must be sub-mm on-arc or they are junk, junk count stated), then greedy walk + gate vs 4.3107 and uncovered vs 15. Success bar: uncovered strictly below 8 (break the floor — proof of new information) with junk 0 and gate at/below 4.3107. If finer sampling yields no new on-arc dots (extraction already saturated), refute with the saturation evidence — owner moves to mesh resolution itself.

**Starting position:** .scratch/pota123_repro/ (r1 un-blinds), pota124_repro/ (disp<=2.5 leash), pota130_repro/ (void map), ticket 89 (author 1.8mm uniform resample = the density reference). Login-node numpy only — no Slurm, no E2E. New scratch pota143_repro/; renders under laptop artifacts/pota143/ (new dots vs old bag vs ORIG, new-dot close-ups per span).

**Rules:** control reproduces 128/279's marks first or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); each new dot sub-mm or declared junk; COMMIT NOTHING; Comments-only ticket edits.

- [ ] Finer extraction stated + new bag (size, on-arc share, junk)
- [ ] Walk + gate vs 4.3107, uncovered vs 8 (floor broken?)
- [ ] Verdict + saturation refutation if empty
