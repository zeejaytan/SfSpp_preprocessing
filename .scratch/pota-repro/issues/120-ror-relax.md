# ROR relaxation — stop deleting the rim's own dots

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 119 (7 true void spans; owner = ROR min_neighbors=6 via boundary_filter.cpp:10-33; fix = 6->3 C01-only) + 103 (cleaned bag baseline) + 111 (ROR-vs-boundary ambiguity stated — keep it: report whether relaxed ROR admits dots the boundary test itself would reject)

**Status:** ready-for-agent

**What to deliver:** exact-port the ROR step (boundary_filter.cpp:10-33, min_neighbors rule) in numpy, reproduce the 270-bag deletion at 6 first (same deleted set to the dot — green control), then rerun at 3 (one variable). Report: (a) void-span shrinkage (each of 119's 7 ORIG void ranges: coverage before/after); (b) junk accounting (newly kept dots seated vs ORIG: on-arc share — the 111 ambiguity check); (c) full-bag walk + gate vs 4.68 bar (GUARD-113 or plain greedy+T13 — state which before running, same in both arms). Success bar: void spans shrink (total uncovered ORIG count down) AND junk share small (newly kept dots majority within 5mm of ORIG) AND gate no worse than 4.68 AND walk no shorter than 197. If 3 admits a second inboard row (junk), refute with the trade numbers — that says ROR-6 was load-bearing and the voids must be filled upstream instead.

**Starting position:** pota103/119_repro/ (cleaned bag, void spans with ORIG extents, ROR port from 104/109 work if reusable), boundary_filter.cpp:10-33 + caller edgeline_extraction_headless.cpp:990-992. Login-node numpy only — no Slurm, no E2E. New scratch pota120_repro/; render under laptop artifacts/pota120/ (void spans before/after on the ORIG arc, newly kept dots coloured by seated distance).

**Rules:** control reproduces ROR-6 deletion exactly first or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; port-exact-then-one-variable.

- [ ] ROR-6 ported exact (deleted set matches)
- [ ] ROR-3 rerun (void shrinkage, junk accounting, walk + gate)
- [ ] Verdict + recipe or trade refutation
