# Re-anchor on 279 — the latch follows the road

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 128 (LAND greedy: 279/206/gate 4.3107/uncovered 15; GUARD-126 with stale S126 FAILS on 279: 203, gate 4.3122, 0 takes, armed-late — 125 family) + 126 (rule-FORM: freeze the directed walk on the new bag, derive anchor from its own route, never port)

**Status:** ready-for-agent

**What to deliver:** the 126 rule-form applied to the 279 bag. Freeze GUARD-113-on-279 (or GUARD-126 minus stale latch — state choice first), derive the bag-relative anchor from the freeze's own approach run, arm a staged latch, walk. Success bar (all must hold): pushes >=206 AND gate at/below 4.3107 AND 0 jumps >=40mm AND leftover below 73 AND latch provably live (arms + >=1 genuine take). If the freeze strands with the same absolute signature (all distinct groups sequenced, leftovers twins) and no latch candidacy, say so with the autopsy — that result stands as the 279 absolute and the lane moves to the remaining spans (32,37)/(46,50)/(96,97)/(165,165)/(173,173).

**Starting position:** .scratch/pota128_repro/ (279 bag, R128 rule, greedy-279 + stale-guard numbers), pota126_repro/ (rule-form: freeze/anchor/latch procedure), pota116_repro/ (recovery tier verbatim). Login-node numpy only — no Slurm, no E2E. New scratch pota129_repro/; render under laptop artifacts/pota129/ (latch-arm plot, paths, gate, step spectra).

**Rules:** control reproduces 128-greedy first (206, gate 4.3107) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; NO ported coordinates (anchor derived from THIS bag's freeze).

- [ ] 128-greedy reproduced + freeze choice stated
- [ ] New anchor derived (bag-relative rule, no 270/278/279 absolutes)
- [ ] Re-anchored walk vs full bar
- [ ] Verdict + recipe or 279-absolute with autopsy
