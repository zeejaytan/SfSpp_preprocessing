# Double-twice densify — two doublings of the 314 bag, zigzag must fall

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 143 (314 bag via ladder 10->0/0->21->1; user steer: saturated rung alone never refutes) + 144 (M144 recovery: uncovered 0 but walk still weaves — eye verdict, user 2026-10-19: still zigzag) + 142 (flips 32/selfint 33 baseline on 282 — the zigzag metric to beat)

**Status:** ready-for-agent

**What to deliver:** TWO doublings of true dots, each rung walked and measured. Rung A: ~630 dots (2x of 314) via further upstream sampling (finer grids than X4, and/or Aperture widening per 132's calibration — dmid<=18 admitted 4 junk-0; wider honest apertures may bank more). Rung B: ~1260 dots (2x again). Each new dot sub-mm on-arc or declared junk (junk count stated per rung; a rung that buys dots with junk is not a doubling). Per rung: greedy walk + gate + uncovered + 142's topology counts (flips, self-intersections) + render. Success bar per rung: flips+selfint strictly down vs the previous rung AND gate at/below 3.9736 AND junk 0. If a rung saturates (no new on-arc dots at any aperture/scale), report the saturation curve per the standing rule — saturation at every setting is the refutation, one setting is not. Stop rule: two doublings attempted; bank whichever rung is best by (gate, topology) even if the second doubling fails.

**Starting position:** .scratch/pota143_repro/ (ladder method, X2/X4 grids, aperture calibrations), pota144_repro/ (M144 rule-form for the walk per rung), pota142_repro/ (topology counters). Login-node numpy only — no Slurm, no E2E. New scratch pota146_repro/; renders under laptop artifacts/pota146/ (per-rung walk vs ORIG + topology counts on-plot).

**Rules:** 144's M144 marks reproduced on 314 first or stop; read-only inputs, zero ORIG points (ORIG Bl_0 gate-evidence + ruler only); COMMIT NOTHING; Comments-only ticket edits.

- [ ] Rung A ~630 (method, on-arc share, junk) + walk/gate/topology
- [ ] Rung B ~1260 (method, on-arc share, junk) + walk/gate/topology
- [ ] Saturation curves where empty; best rung banked
