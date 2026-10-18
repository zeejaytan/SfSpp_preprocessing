# Bridge reservation — protect the onward arc from side bites

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 114 (invariant: seqpos-28 branch decides fate; re-entry ruled out; next = bridge-reservation) + 112 (step 53 passes within 2.3mm of ORIG[27] then bites off-arc) + 113 (GUARD-113: 190/270, gate 4.31) + 103 (cleaned bag, gate 4.68)

**Status:** ready-for-agent

**What to deliver:** implement bridge-reservation on the 103 cleaned bag under GUARD-113 heading: when the walk first passes within a stated distance of onward-arc dots (e.g. seated-on-true-arc candidates ahead), mark those dots RESERVED — excluded from candidacy until the walk approaches them along-arc (stated re-admit rule, e.g. heading-aligned approach within the cone). Rationale (114): the bridge dies when the walk eats continuation dots from the side; reservation keeps them uneaten until the walk arrives properly. State the exact reserve/re-admit rule before running. Success bar (all must hold): greedy >=197 pushes AND walks through BOTH stall dots AND gate at/below 4.68mm AND no teleport landing >=40mm AND reserved dots re-admitted (none stranded by the rule itself — count reservations never revisited). If it strands at a third point, report where + coverage delta vs GUARD-113 (progress or same-pattern refutation).

**Starting position:** pota103/112/113/114_repro/ (cleaned bag, GUARD-113 scripts, seqpos-28 + step-53 evidence, orphan tables). Login-node numpy only — no Slurm, no E2E. New scratch pota115_repro/; render under laptop artifacts/pota115/ (seqpos-28 region: reserved dots, side-bite refused, path vs guard-113).

**Rules:** control reproduces GUARD-113 first (190/270, far-arc stall, gate 4.31, all to 2dp) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; rule-stated-before-run; one variable (reservation on top of GUARD-113).

- [ ] GUARD-113 reproduced + reserve/re-admit rule stated
- [ ] Reserved walk (pushes, stalls, gate, reservation accounting)
- [ ] Verdict + recipe or refutation with break point
