# Presplit+select on the cleaned bag — plan then sequence

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 117 (greedy-step family closed: exemptions eat bridges, reservation bars roads, early trigger derails; architecture question = plan-then-sequence per 75) + 116 (detour worked only with no branch downstream) + 110 (presplit shattered the curvature-filtered bag — connectivity was removed; the cleaned 270-bag HAS connectivity) + 103 (cleaned bag, gate 4.68) + 75 (presplit+select lands loops on sparse inputs)

**Status:** ready-for-agent

**What to deliver:** replay the T75 presplit+select recipe on the 103 CLEANED bag (270 dots, row deleted — connectivity intact, unlike 110's filtered bag). Rationale: the family verdict says no one-step rule threads this rim because every bridge is also a branch; splitting the bag into components first (plan) and chaining/selecting second (sequence) never faces both at once. State the presplit radius + select/chain rule before running (start from the 75 recipe verbatim, one variable if it must change). Success bar (all must hold): landed loop covering >=197 pushes-equivalent AND gate at/below 4.68mm AND no teleport landing >=40mm AND the loop walks through BOTH stall dots. If presplit shatters the cleaned bag too, report component stats vs 110's 38 — that says the bag itself lacks chainable structure and the ticket should name what input step owns that.

**Starting position:** pota103/75/110_repro/ (cleaned bag, T75 recipe, 110's shatter stats for contrast). Login-node numpy only — no Slurm, no E2E. New scratch pota118_repro/; render under laptop artifacts/pota118/ (components, chained loop vs guard-116, stall dots).

**Rules:** control reproduces 103-cleaned greedy first (93/270, 197, 4 jumps, stall dot 2dp) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; recipe-stated-before-run.

- [ ] Control reproduced + presplit/select rule stated
- [ ] Presplit stats (component count vs 110) + chained loop (coverage, gate, stalls)
- [ ] Verdict + recipe or structural refutation with owner named
