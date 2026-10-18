# Heading-guard replay — stop the walk eating its own bridge

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 112 (REFUSAL: step 53 passes within 2.3mm of ORIG[27], leaves down-arc, returns into own footprints; stall 34/34 visited) + 103 (cleaned bag, gate 4.68) + 99 (T75 forward-cone exists) + 105 (face-guard died at 44 — this is HEADING not face, different variable)

**Status:** ready-for-agent

**What to deliver:** replay greedy on the 103 cleaned bag with a heading guard added — prefer dots continuing the current direction, refuse (or strongly de-prefer) steps that reverse heading ~180° / re-approach from the side the walk already covered (the step-53 bridge-eating move). State the exact rule before running (e.g. T75's forward-cone inside greedy rather than after presplit; angle + fallback stated). Success bar: greedy >=197 pushes AND walks THROUGH the 112 stall dot (not stopping there) AND gate at/below 4.68mm AND continuation dots survive (no 44.7mm teleport landing). If the guard strands elsewhere, report where + whether the stall moved on-arc (progress) or the walk still eats bridges (refutation with the new break point).

**Starting position:** pota103/112_repro/ (cleaned bag, walk replay, stall freeze, step-53 evidence), T75 cone rule from 99. Login-node numpy only — no Slurm, no E2E. New scratch pota113_repro/; render under laptop artifacts/pota113/ (stall region: guarded path vs control, step-53 move kept or refused).

**Rules:** control reproduces 103-cleaned stall first (same dot 2dp) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; rule-stated-before-run; one variable (the heading guard).

- [ ] Control reproduces stall + step-53 bridge move
- [ ] Rule stated, guarded walk (pushes, stall behaviour, gate)
- [ ] Verdict + recipe or refutation with break point
