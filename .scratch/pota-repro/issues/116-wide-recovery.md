# Wide recovery — pick up orphans without eating bridges

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 115 (reservation blocks through-line, forces side-bite — ruled out; exemption + reservation both exhausted) + 114 (invariant: seqpos-28 branch; candidates (a)/(b) named, (b) dead) + 113 (GUARD-113: 190/270, gate 4.31, far-arc stall) + 112 (orphan groups A/B mapped: 8 leftovers, every orphan 3.09-6.32mm from path when cone walked past)

**Status:** ready-for-agent

**What to deliver:** candidate (a) — the last untested direction. GUARD-113 + a WIDER recovery fallback: past a stated point (e.g. once past mid-arc / past the old stall dot), allow recovery steps wider than 120° (state the angle + trigger before running) so the walk can turn back for orphan groups it strode past, WITHOUT the blanket exemptions that ate bridges in 114/115. The rule must distinguish recovery (turning back onto unvisited on-arc dots behind) from bridge-eating (biting onward-arc dots from the side) — state how before running. Success bar (all must hold): greedy >=197 pushes AND walks through BOTH stall dots AND gate at/below 4.68mm AND no teleport landing >=40mm AND orphans recovered (leftover count below 113's 80). If the wider fallback re-eats a bridge, report which branch point failed — that plus 114/115 closes the greedy-step family and forces the walk-architecture question.

**Starting position:** pota103/112/113/114/115_repro/ (cleaned bag, GUARD-113 scripts, orphan tables, branch-point evidence). Login-node numpy only — no Slurm, no E2E. New scratch pota116_repro/; render under laptop artifacts/pota116/ (recovery turns: orphan pickup vs bridge regions, path vs guard-113).

**Rules:** control reproduces GUARD-113 first (190/270, far-arc stall, gate 4.31, all to 2dp) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; rule-stated-before-run; one variable (recovery fallback on top of GUARD-113).

- [ ] GUARD-113 reproduced + recovery rule stated
- [ ] Recovery walk (pushes, stalls, gate, orphan accounting)
- [ ] Verdict + recipe or family-closing refutation
