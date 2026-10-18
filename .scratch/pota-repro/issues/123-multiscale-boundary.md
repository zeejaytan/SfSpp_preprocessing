# Span-localized multi-scale boundary — un-blind the test where it goes flat

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 122 (mesh fine everywhere; empty-sector boundary test goes FLAT on-arc at 4 void spans: [9..13], mid-[32..50], [160..161], [173]; ROR owns [25],[96..97]; snap-drag owns [164..165]) + 104 (numpy port of the boundary test exists) + 103 (cleaned bag, gate 4.68)

**Status:** ready-for-agent

**What to deliver:** the boundary test is blind at 4 spans because its single radius (6.47mm) and 0.6pi sector rule see no empty sector where the fold crowds the neighbourhood. Re-run the test MULTI-SCALE but CONFINED to void-span neighbourhoods: port-exact first at the pipe radius (reproduce which mesh verts pass/fail there), then smaller radii (state the scale ladder before running, e.g. r, r/2, r/4) applied ONLY inside the 4 blind spans' neighbourhoods, admitting dots that pass at finer scale. Snap surface-constrained (keep 122's lesson: no off-face drag; state the constraint). Seeds come from the span-localized re-run, never from filter rejects (121 stands). Walk + gate the resulting bag (plain greedy K34+T13, pre-registered, same both arms). Success bar (all must hold): uncovered ORIG count below 119's 32 AND admitted junk ~0 (majority within 5mm of ORIG) AND gate at/below 4.68mm AND walk >=197 pushes. If finer scales admit the same flat response (blind at every scale), refute with the response-vs-scale curves — that says the neighbourhood itself carries no edge signal and the span must be bridged by chaining, not detected.

**Starting position:** pota103/104/119/122_repro/ (cleaned bag, boundary-test numpy port, void spans + blind-span list, mesh verts), mesh_processing_headless.cpp:1580-1709 + caller :2040-2068. Login-node numpy only — no Slurm, no E2E. New scratch pota123_repro/; render under laptop artifacts/pota123/ (blind spans: response-vs-scale curves, newly admitted dots, walk vs control).

**Rules:** control reproduces 103-cleaned bag first (270, gate 4.68) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; port-exact-then-ladder-stated.

- [ ] Boundary port-exact at pipe radius (pass/fail reproduced in blind spans)
- [ ] Scale ladder stated, span-localized re-run (response curves, admission accounting)
- [ ] Walk + gate vs full bar
- [ ] Verdict + recipe or all-scale-blind refutation
