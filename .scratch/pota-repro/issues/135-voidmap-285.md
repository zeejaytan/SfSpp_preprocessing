# Void-map refresh on 285 — eight spans left, name them all

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 134 (LAND: M134d walk 278/282 unique, gate 4.2488, uncovered 8, spans [(36,37),(46,47),(96,97),(165,165),(173,173)]) + 130 (void-map precedent + hit-list discipline)

**Status:** ready-for-agent

**What to deliver:** the 130 analysis re-run on the M134d walk over the 285 bag (282 + R133's 3 wide dots). Classify each of the 8 uncovered ORIG spans: VOID vs EATEN vs BRIDGED; owner per span; what the 133 dots + 134 recovery moved. Then PRIORITIZE: ordered hit-list ranked cheapest-first (detection remnant > named-span bridge), one-line rule-sketch per span. No new dots, no new walks — reading ticket ending in an ordered hit-list. Success bar: all 8 classified with owners AND ordered hit-list with rule-sketches, OR explicit unknown-owner statement.

**Starting position:** .scratch/pota134_repro/ (285 bag, M134d walk, uncovered-8 list), pota130_repro/ (void-map precedent). Login-node numpy only — no Slurm, no E2E. New scratch pota135_repro/; render under laptop artifacts/pota135/ (uncovered-8 map with owners, hit-list).

**Rules:** reproduce 134's uncovered-8 list first or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits.

- [ ] Uncovered-8 reproduced + 130 taxonomy restated
- [ ] Per-span classification with owner
- [ ] Ordered hit-list with rule-sketches
