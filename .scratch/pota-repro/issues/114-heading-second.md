# Heading guard second iteration — past the far-arc stall

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 113 (guard walks through old stall at seq 166, stops 7 short at far-arc stall [25.13,66.52,424.99]; strides-over-then-strands-beyond) + 112 (REFUSAL pattern) + 103 (cleaned bag, gate 4.68)

**Status:** ready-for-agent

**What to deliver:** iterate the heading guard against the NEW break point. Diagnose the far-arc stall the same way 112 did (K-net freeze at the stop: visited fraction, nearest fresh + its angle, ORIG-seat of the stop) and state a revised rule before running — candidates: wider recovery fallback past 120° once the walk has passed mid-arc, bridge-reservation (dots seated on the onward arc marked reserved when first passed so the walk cannot eat them from the side), or re-entry permission (allow one ~180° turn if it lands on unvisited on-arc dots). One variable change from GUARD-113, stated before the run. Success bar (all must hold): greedy >=197 pushes AND walks through BOTH stall dots AND gate at/below 4.68mm AND no teleport landing >=40mm. If it strands at a third point, report where + whether total coverage grew (progress) or the same pattern repeated (refutation with the invariant).

**Starting position:** pota103/112/113_repro/ (cleaned bag, GUARD-113 scripts, both stall freezes). Login-node numpy only — no Slurm, no E2E. New scratch pota114_repro/; render under laptop artifacts/pota114/ (both stall regions: path vs control/guard-113).

**Rules:** control reproduces GUARD-113 first (190/270, far-arc stall, gate 4.31, all to 2dp) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; rule-stated-before-run.

- [ ] GUARD-113 reproduced + far-arc stall frozen
- [ ] Revised rule stated, second-iteration walk (pushes, stalls, gate)
- [ ] Verdict + recipe or refutation with invariant
