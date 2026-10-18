# ROR-r1 cross-gating — keep rejects the fine test calls edge

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 126 (landing: 205, gate 4.31, leftovers 73; remaining spans VOID incl. ROR-owned [25]/[96..97]) + 122 (ROR owns on-arc kills at [25] 2.17mm and [96..97] 4.94mm) + 123 (r1 un-blinds 3/4 spans) + 120 (ROR-6 load-bearing alone; ROR-3 admits wall) + 124 (grown-278 + recipe)

**Status:** ready-for-agent

**What to deliver:** cross the two filters against each other. ROR-6 deletes dots the r1 boundary test calls edge (122's [25]/[96..97] kills sit 2-5mm on-arc; 123's r1 sees edge where ROR sees noise). Rule (ORIG-free, stated before running): re-admit ROR-6 rejects that PASS the r1 empty-sector test (and the 124 snap caps: disp<=2.5, dmid<=5, dedupe, ROW40-exclusion). Rationale: two independent witnesses — neighbour-count says wall, fine-scale edge test says rim — and the rim witness is the one that un-blinded 3 spans. Test on the full bag: admission accounting per span, junk count, walk + gate (GUARD-126 recipe from 126 AND plain greedy+T13 — report both, bar on the better... no: bar on greedy first, guard second; state both). Success bar (all must hold): uncovered ORIG below 126's leftover-equivalent AND admitted junk ~0 AND gate at/below 4.31mm AND greedy walk >=205 pushes. If r1 passes the wall rejects too (no cross-separation), refute with the pass rates — that says ROR's kills are unrecoverable at filter level and [25]/[96..97] join [173] on the chaining list.

**Starting position:** .scratch/pota120_repro/ (ROR-6 port + reject set + p120_newX), pota123_repro/ (r1 test + ladder), pota124/126_repro/ (grown-278, GUARD-126, numbers). Login-node numpy only — no Slurm, no E2E. New scratch pota127_repro/; render under laptop artifacts/pota127/ (cross-admitted dots per span, junk accounting, walk vs 126).

**Rules:** control reproduces 126 numbers first (205, gate 4.31, leftovers 73) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; cross-rule-stated-first.

- [ ] 126 reproduced + cross rule stated
- [ ] Cross-admitted bag (per-span accounting, junk count)
- [ ] Walk + gate vs 126's marks (greedy + guarded)
- [ ] Verdict + recipe or chaining-list refutation
