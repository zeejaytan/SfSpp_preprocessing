# Lip density — is the true edge under-sampled, and does feeding it cure the walk?

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 110 (filter removed 5mm-connectivity — no honest walker spans the rim) + 109 (curvature admission 40->5) + 103 (cleaned bag 4.68) + 99 (71/343 never visited)

**Status:** ready-for-agent

**What to deliver:** the standing note across six tickets says the next variable is upstream (mesh/sample density at the lip). MEASURE FIRST, then test: (a) compare sampling density along the true lip arc (author-seated regions of the 103 cleaned bag) vs the row region — dot spacing + underlying mesh edge lengths in both regions, numbers stated before any fix; (b) if the lip is under-sampled, densify ONLY the lip sampling (one variable — e.g. finer boundary-test output, midpoint fill on the cleaned bag, or mesh-side densification; state the rule before running) and walk + gate it with greedy+T13. Success bar: greedy >=197 pushes with T13 behaving (not suppressed), gate at/below 4.68mm, ROW40 admission reported (curvature filter may be applied as stated pre-registered step, not a second variable — declare it). If the lip is NOT under-sampled, refute fast with the density numbers — that kills the upstream hypothesis and forces a rethink.

**Starting position:** pota103/109_repro/ (cleaned + filtered bags), C01 fragment mesh, 99 checkpoints. Login-node numpy only — no Slurm, no E2E. New scratch pota111_repro/; render under laptop artifacts/pota111/.

**Rules:** control reproduces 103-cleaned-bag first (green control) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; measure-first, rule-stated-before-run.

- [ ] Density measured (lip arc vs row: dot spacing + mesh edge lengths)
- [ ] Rule stated, densified bag (or fast refutation)
- [ ] Walk + gate vs 4.68 bar
- [ ] Verdict + recipe or refutation
