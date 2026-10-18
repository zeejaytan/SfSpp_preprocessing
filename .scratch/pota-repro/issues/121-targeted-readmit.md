# Targeted re-admission — keep the 8 arc dots, none of the wall

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 120 (ROR-3 trade: +9 arc for 9 wall junk, gate 4.85; 8 on-arc newly-kept in p120_newX.npy, seats 26/31/33/50/94) + 109 (curvature separates inverted: lip curved vs flat — candidate rule) + 119 (7 void spans) + 103 (cleaned bag, gate 4.68)

**Status:** ready-for-agent

**What to deliver:** ROR-6 stays (load-bearing), plus targeted re-admission of the arc dots it wrongly deletes. MEASURE FIRST: do the 8 on-arc dots separate from the 9 wall-junk dots on a stated feature — pipe curvature (109's split: arc curved vs wall flat?) or seated-distance-to-local-arc or neighbour-count band — rule stated before running. Then build the re-admitted bag (ROR-6 + rule-kept dots) and walk + gate it (plain greedy K34+T13, pre-registered, same both arms). Success bar (all must hold): uncovered ORIG count below 119's 32 AND newly admitted junk ~0 (admitted dots majority within 5mm of ORIG) AND gate at/below 4.68mm AND walk >=197 pushes. If no clean separating feature measures (overlap like 106/108), refute fast with the overlap numbers — that says the 8 must be grown mesh-side, not filtered.

**Starting position:** .scratch/pota120_repro/ (p120_newX.npy: 8 on-arc seats; junk seats; ROR-6 port), pota103/109/119_repro/ (cleaned bag, curvature values, void spans). Login-node numpy only — no Slurm, no E2E. New scratch pota121_repro/; render under laptop artifacts/pota121/ (admitted dots coloured by feature value, voids before/after, walk vs control).

**Rules:** control reproduces ROR-6 bag first (270, gate 4.68) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; feature-measured-then-rule-stated.

- [ ] Feature measured (8 arc vs 9 wall separation or overlap)
- [ ] Rule stated, re-admitted bag (admission accounting, junk count)
- [ ] Walk + gate vs full bar
- [ ] Verdict + recipe or overlap refutation
