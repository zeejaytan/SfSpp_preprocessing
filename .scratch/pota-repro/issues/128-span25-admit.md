# Span-localized [25] admission — the one dot geography clears

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 127 (cross-gate 0 admitted; [25]'s kill rej 331->O26 is r1-PASS, dmid 2.17, disp 3.09 — span-localized candidate; [96..97] filter-dead, chaining only; geographic dmid does all wall-exclusion) + 124 (caps>2.5 worthless globally — this is span-localized, not global) + 126 (205, gate 4.31, leftovers 73)

**Status:** ready-for-agent

**What to deliver:** admit the single dot geography clears. Rule (ORIG-free, stated before running): ROR-6 reject + r1-PASS + within dmid<=5mm of void mid [25] + disp<=3.5mm (127 calibrated: exactly 1 survivor at 3.5/4.0, junk 0) + dedupe + ROW40-exclusion — span-localized to [25] only. Rationale: 127 proved no GLOBAL filter-level point exists, but the geographic restriction is what excludes wall — so spend it locally where a named void owns a named kill. Test: admit rej 331, walk + gate (greedy AND GUARD-126, report both, bar on greedy first). Success bar: uncovered below 126's 16 AND junk 0 AND gate at/below 4.31 AND walk >=205. If the dot strands unvisited or the walk ignores it (coverage delta 0), refute with the sequencing — that says single dots don't move honest walks and [25] joins the chaining list.

**Starting position:** .scratch/pota127_repro/ (reject set, rule R127, calibration, rej 331 coords), pota124/126_repro/ (grown-278, GUARD-126, numbers). Login-node numpy only — no Slurm, no E2E. New scratch pota128_repro/; render under laptop artifacts/pota128/ (admitted dot on arc, walk vs 126, coverage delta).

**Rules:** control reproduces 126 numbers first (205, gate 4.31, leftovers 73) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; span-localized-one-dot.

- [ ] 126 reproduced + span rule stated
- [ ] Admitted bag (1 dot, junk accounting)
- [ ] Walk + gate vs 126's marks (greedy + guarded)
- [ ] Verdict + recipe or chaining-list refutation with sequencing
