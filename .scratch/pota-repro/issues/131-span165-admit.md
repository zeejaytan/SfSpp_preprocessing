# Span-localized (165,165) — snap-drag's span, r1's eyes

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 130 (hit-list #1: (165,165) snap-drag owner; rule-sketch R165 = span-localized r1@r0/2 + SURF-C1 disp cap 2.0->3.5) + 123 (r1 un-blinds; snap-drag owns [164..165] per 122) + 128 (span-localized precedent: 1 dot, junk 0, greedy bar)

**Status:** ready-for-agent

**What to deliver:** the R165 rule-sketch tested. Rule (ORIG-free, stated before running): span-localized to void mid (165,165) (dmid<=5mm) + r1 empty-sector PASS (123 code verbatim) + SURF-C1 disp cap 3.5 (up from 124's 2.5 — span-localized, so the geography does wall-exclusion per 127) + dedupe + ROW40-exclusion. Candidate pool: snap-dragged rejects near the span + ROR-6 rejects near the span — state pool first. Test: admit survivors, walk + gate (greedy AND GUARD-129-form... no: greedy first, guarded second with FRESH re-anchor per 126 rule-form only if greedy lands — state choice). Success bar (all must hold): uncovered below 15 AND junk 0 AND gate at/below 4.3107 AND walk >=206. If pool is empty or survivors strand unvisited, refute with the sequencing and (165,165) joins the chaining list.

**Starting position:** .scratch/pota130_repro/ (span owners, (165,165) precision), pota123_repro/ (r1 verbatim), pota124_repro/ (snap caps, SURF-C1), pota128_repro/ (R128 precedent, 279 bag). Login-node numpy only — no Slurm, no E2E. New scratch pota131_repro/; render under laptop artifacts/pota131/ (pool, survivors, walk vs 279, coverage delta).

**Rules:** control reproduces 128-greedy first (206, gate 4.3107, uncovered 15) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; span-localized.

- [ ] 128-greedy reproduced + R165 stated with pool
- [ ] Admitted bag (accounting, junk)
- [ ] Walk + gate vs 128's marks
- [ ] Verdict + recipe or chaining-list refutation
