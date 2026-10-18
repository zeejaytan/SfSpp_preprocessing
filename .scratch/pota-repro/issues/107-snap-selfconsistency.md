# Snap self-consistency — reverted dots must pass the test that admitted them

GOAL: MATCH AUTHOR'S INPUT.

**What to deliver:** after the unmodified K=1 snap, run the PCL empty-sector boundary test ON THE SNAPPED DOTS THEMSELVES (same 0.6pi rule, same radius): any snapped dot that fails — i.e. its new neighbourhood is full all round, proving it sits mid-face — reverts to its pre-snap boundary coordinates. Rationale: a dot the snap drags into the middle of a face cannot pass the boundary test there; the test becomes its own firewall. Walk + gate the resulting bag vs control.

**Answers:** E1

**Blocked by:** 106 (duel numbers: cap 1.38502mm, ROW40 29 S0/11 S1, typical snap 2.19mm) + 103 (row-deleted bag, gate 4.68mm) + 99 (walk checkpoints)

**Status:** ready-for-agent

**Success bar (all must hold):** ROW40 admission ~0/40 AND walk gate at/below 4.68mm med AND no new stall/death (greedy >=93, final pushes >=197, T13 jumps reported). If the bar is not met, refute with numbers — no recipe then.

**Starting position:** /data/gpfs/projects/punim2657/pota106_repro/ (control bags, ROW40 definition, walk replay) + 102/103 replay scripts. Login-node numpy only — no Slurm, no E2E. New scratch pota107_repro/ (108/109 likewise); renders under laptop artifacts/pota10X/ matching the ticket number.

**Rules:** control reproduces 106-control first (green control) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); one variable (the fix under test).

- [ ] Control reproduces 106-control
- [ ] Self-consistency bag (revert count, ROW40 admission, walk, gate)
- [ ] Verdict + recipe (file + line + rule) or refutation
