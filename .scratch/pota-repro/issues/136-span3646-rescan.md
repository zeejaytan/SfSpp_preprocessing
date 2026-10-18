# Span rescan (36,37)+(46,47) — new mids, fresh license

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 135 (hit-list #2: R36/R46 rescan to new void-mids O36/O46; candidates UNKNOWN on file; zero-yield promotes both spans to chaining-class) + 132 (O41 license excludes these by construction; wide-license precedent) + 131 (pool-empty precedent: state pool first)

**Status:** ready-for-agent

**What to deliver:** the rescan tested. Rule (ORIG-free, stated before running): ROR-6 rejects + r1 empty-sector PASS (123 verbatim) + disp<=2.5 + dmid<=5 to NEW void-mids O36 and O46 (fresh span license — 133's O41 license excludes these by construction) + dedupe + ROW40-exclusion. Candidate pool stated first (133's reject-seat list seats nothing at 36/37/46/47 — verify on the 282 bag). Test: admit survivors, walk + gate (greedy AND M134d-form recovery only if greedy lands — state choice first). Success bar: uncovered below 8 AND junk 0 AND gate at/below 4.2488 AND unique >=278. If pool empty at license or survivors strand, refute with the sequencing — both spans promote to chaining-class (C36/C46) and detection closes on the remnant.

**Lead note:** hit-list #1 (R165 verbatim) is NOT re-run: 131 already spent that exact rule on this neighbourhood (pool empty, no operating point) and the 282 bag changes nothing near O165. Repeat discarded with reason, not silently.

**Starting position:** .scratch/pota135_repro/ (span owners, new-mid license), pota133_repro/ (reject-seat list, 282 bag), pota134_repro/ (M134d recovery form). Login-node numpy only — no Slurm, no E2E. New scratch pota136_repro/; render under laptop artifacts/pota136/ (pool, survivors, walk vs M134d, coverage delta).

**Rules:** control reproduces 134's marks first (290/278u/gate 4.2488/uncovered 8) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; fresh license only.

- [ ] M134d reproduced + R36/R46 stated with pool
- [ ] Admitted bag (accounting, junk)
- [ ] Walk + gate vs 134's marks
- [ ] Verdict + recipe or chaining-class promotion
