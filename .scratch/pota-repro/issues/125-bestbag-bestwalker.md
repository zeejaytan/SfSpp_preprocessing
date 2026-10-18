# Best bag with best walker — the grown rim walked with direction

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 124 (grown-278 bag: 8 admitted, junk 0, gate 4.31, walk 205) + 116 (GUARD-116: heading + post-stall recovery, 195/270, gate 4.52, 0 jumps) + 117 (family closed for greedy-step, but the BAG has changed since — 8 voids filled) + 103 (cleaned-bag baseline)

**Status:** ready-for-agent

**What to deliver:** walk 124's grown-278 bag with GUARD-116 (heading cone + post-stall recovery tier, verbatim ports, one variable total = the bag). Rationale: 113-117 proved no one-step rule threads the 270-bag; but the bag has since gained 8 stepping-stones in 3 void spans — the bridges that starved 116 may now be walkable. State the GUARD-116 port + recovery trigger before running (armed point re-derived on the new bag, rule same). Success bar (all must hold): pushes >=205 AND walks through BOTH stall dots AND gate at/below 4.31mm AND zero jumps >=40mm AND leftover count below 116's 75. If the walk still strands at the same far-arc dot, report coverage delta vs 116 (progress = the 8 dots extending the road; same-dot = the stall is structural, owned by the remaining voids [25]/[32..37]/[46..50]/[165]/[173], and the ticket should say which void spans bound it).

**Starting position:** .scratch/pota124_repro/ (grown-278 bag + admission recipe), pota116_repro/ (GUARD-116 scripts, trigger rule, stall freezes). Login-node numpy only — no Slurm, no E2E. New scratch pota125_repro/; render under laptop artifacts/pota125/ (path vs guard-116-on-270, stall dots, gate CDF).

**Rules:** control reproduces 124-grown greedy first (99/278, 205, gate 4.31) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; walker-verbatim-bag-changed.

- [ ] 124-grown reproduced + GUARD-116 port stated
- [ ] Guarded walk on grown bag (pushes, stalls, gate, leftovers)
- [ ] Verdict + recipe or structural verdict with bounding voids named
