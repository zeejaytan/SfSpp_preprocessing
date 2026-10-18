# Stall-dot autopsy — why does greedy stop at the same dot every time?

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 111 (stall dot identical in control/row-deleted/densified at [-27.26,1.05,388.81]) + 103 (driver = gap at stall dot, now disproven as density) + 99 (walk checkpoints)

**Status:** ready-for-agent

**What to deliver:** a full autopsy of the stall event, MEASURE FIRST: replay the greedy walk on the 103 cleaned bag and freeze the moment it stops. Report (a) the stall dot's K=34 net — how many unvisited, at what distances, and why none is taken (all visited? none within reach? cone/heading rule?); (b) the dot's normals + curvature vs its neighbours (does the surface direction flip here?); (c) the mesh context — fold constriction, face/segmentation label, scan border?; (d) where the TRUE arc (ORIG-seated) goes from here — does the walk stop where the author's line continues, i.e. is the next true dot simply missing from the bag (void), or present-but-refused (rule)? The verdict must name one: VOID (next true dot absent → bag-building failure at this spot) or REFUSAL (next true dot present → walk-rule failure at this spot). If REFUSAL with a one-variable resume rule, test it (walk + gate vs 4.68). If VOID, map the void's extent and say what input step owns it.

**Starting position:** pota103/111_repro/ (cleaned + densified bags, walk replays), C01 fragment mesh, 99 checkpoints. Login-node numpy only — no Slurm, no E2E. New scratch pota112_repro/; render under laptop artifacts/pota112/ (stall close-up: net, normals, void/arc context).

**Rules:** control reproduces 103-cleaned stall first (same dot to 2dp) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; mechanism named before any fix arm.

- [ ] Stall reproduced (same dot 2dp) + K-net frozen
- [ ] VOID vs REFUSAL named with numbers
- [ ] Fix arm if REFUSAL (walk + gate) or void map + owner if VOID
- [ ] Verdict + render
