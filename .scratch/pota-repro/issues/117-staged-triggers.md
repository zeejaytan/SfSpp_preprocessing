# Staged triggers — arm recovery before the bottom arc

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 116 (recovery works post-trigger but group-B orphans' last chance t=94 is pre-arm — unrecoverable by construction; next = staged triggers) + 114 (candidate (a) is the live direction) + 113 (GUARD-113: 190/270, gate 4.31) + 103 (cleaned bag, gate 4.68)

**Status:** ready-for-agent

**What to deliver:** stage the recovery trigger so it covers the bottom arc. 116's latch arms only once the walk is within 5mm of the old stall (t=166); group B's last chance passes at t=94, pre-arm. Design a staged/earlier trigger — e.g. arm once the seqpos-28 bridge is seated (the on-arc choice made, road-ahead known) rather than once the old stall is reached — and re-run. State the trigger + recovery rule before running. The rule must keep 114's lesson (no blanket exemption that re-eats the bridge) and 115's lesson (no reservation that bars the through-line). Success bar (all must hold): greedy >=197 pushes AND walks through BOTH stall dots AND gate at/below 4.68mm AND no teleport landing >=40mm AND group-B orphans recovered (leftover count below 116's 75, B-group accounted). If the earlier trigger re-eats the bridge, report where — that closes the greedy-step family per 114, and the ticket should name the walk-architecture question explicitly.

**Starting position:** pota103/112/113/114/115/116_repro/ (cleaned bag, GUARD-116 scripts, orphan tables, t=94 last-chance evidence). Login-node numpy only — no Slurm, no E2E. New scratch pota117_repro/; render under laptop artifacts/pota117/ (t=94 region: B-orphan pickup vs bridge safety, path vs guard-116).

**Rules:** control reproduces GUARD-116 first (195/270, same far-arc stall, gate 4.52, all to 2dp) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; rule-stated-before-run; trigger staging is the one variable.

- [ ] GUARD-116 reproduced + staged trigger stated
- [ ] Staged walk (pushes, stalls, gate, orphan accounting incl. group B)
- [ ] Verdict + recipe or family-closing verdict with the architecture question named
