# E2E Pot C with the finished bundle — does the traced rim seat sherds?

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 134 (finished walk M134d 278/282, gate 4.2488) + 138 (segment-credit honest, 7/8 banked, O37 the honest single) + 98 (last Pot C E2E: 2/3+1/3 with swapped C02/C04, C01 placed-but-wrong — the mark to beat) + 89 (author-regime recipe)

**Status:** ready-for-agent

**What to deliver:** end-to-end Pot C assembly with the finished C01 bundle. Bundle: C01 = M134d 282-bag trace (frozen from 134, byte-verified) + C02/C04 swapped per 98 + C03 control + Pot C ORIG + A controls (same controls as 98). Bar (same as 98, must beat): seating above 2/3+1/3 with C01 seated AT GT (not placed-but-wrong). E2E x3 runs (nondeterminism noted in 90). Slurm via established pattern (sbatch + laptop-side poll record + sacct State/ExitCode in ticket). Render: seating view eye-checked (green seated / red miss, GT gray, same style as 98).

**Starting position:** .scratch/pota134_repro/ (frozen 282 bundle + M134d sequence), pota98_repro/ (Pot C E2E recipe, controls, bar). New scratch pota141_repro/; renders under laptop artifacts/pota141/.

**Rules:** bundle byte-verified against 134's frozen files first or stop; same-binary ORIG control alongside; COMMIT NOTHING; Comments-only ticket edits; sacct-verified jobs.

- [ ] Bundle frozen + verified, controls stated
- [ ] E2E x3 with job records
- [ ] Seating vs 98's bar (C01 at GT?)
- [ ] Verdict + render paths
