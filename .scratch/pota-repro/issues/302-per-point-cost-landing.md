# 302: Land the per-point Cao cost (kill the scalar collapse) + regression vs MATLAB + Juglet assembler E2E

**What to build:** the sfs_axes port returns, for every candidate axis, the authors' per-point Cao cost — not one whole-cloud number — so axis ranking actually ranks. Landing it must keep the port equal to the authors' MATLAB on Pot A, keep the Pot A regression green (8/8 pieces, 15/15 joins), re-run the corpus axes, and put the corrected axes through the Juglet assembler.

**Answers:** E1

**Blocked by:** none — the diagnosis is complete (lead session 2026-11-04); this ticket only lands and extends it.

**Status:** in-progress

**Working in:** DSH worker session sfs302 (2026-11-04)

**Worker:** sfs302

**Budget:** large 8

**Hand-over:** Claude — needs Spartan compute (MATLAB on a compute node, licence refused on login), the corpus, and the Juglet assembler; a single session runs the whole chain.

**Diagnosis this ticket lands (lead, 2026-11-04 — verified in that session, re-verify while landing):**
`SfSpp_preprocessing/sfs_axes/cao.py:65` (and the Jacobian path at `cao.py:72`) collapses `fwd ** 2` with `np.sum` into ONE whole-cloud scalar, then feeds it through the log-sum-exp robustifier at `s = 100`. MATLAB's `compute_cao_error.m:40` computes `sqrt(sum(T2.^2) ./ sum(T3.^2))` where MATLAB `sum` with no dimension collapses ONE dimension — a per-point vector, not a scalar. The scalar docstring ("Single-output MATLAB behaviour returns a scalar… s = 100") records a misreading of MATLAB as the authors' intent. Measured consequences: at the released axis the robustified score is 1.99999998 and identically ~2.0 for every candidate — ranking is noise, inlier count `int(abs(err) < 1.0)` on a scalar gives 0/1, the good axis is in the pool and never wins.

Lead-session validation of the per-point fix (against the authors' own MATLAB, run on a Spartan compute node):
- Pot A, 8/8 pieces: 0.000030–0.000635 deg from the MATLAB axis, radial 0.000000–0.000007 mm, same K candidates.
- 10 pieces across 10 pots: median 0.000089 deg, worst 0.476 deg (Pot C 03, whose released axis is itself broken).
- Corpus, 163 pieces: median error to released axes 49.5 deg → 6.19 deg; 46% within 5 deg.
- Stability, 10 seeds on Pot A (8 pieces): worst direction spread 4.41 deg (piece 2), most under 0.02 deg — the authors' chain is not unstable.
- Known residuals, NOT this ticket's blocker: (a) corpus disagreement concentrates where released axes are themselves wrong (92 pieces within 5° of truth agree 71%; 30 worse-than-15° agree 3%) — provenance question, parked; (b) both released and our faithful axes sit 8–17 mm off the true axis line on sound Pot A pieces — that offset is in the authors' method, parked; (c) on the Juglet the corrected port ties ticket 68's hybrid on median (12.35° vs 12.31° mutual consistency) and LOSES the tail (piece 8: 34.4° vs 16.4°; piece 9: 55.6° vs 23.8°; piece 3: 20.1° vs 10.8°) — report honestly, do not oversell.

**Starting position:** read `SfSpp_preprocessing/AGENTS.md` (corpus caveats before quoting any score — Pot C 01/J 01 interior lines measure the input; Pot J 09 and Pot C 03 Bl1 excluded from bar tallies; Pot D 18/29 released axes are wrong), this ticket, `sfs_axes/cao.py`, the MATLAB twins (compute_cao_error.m / compute_biaxial_cao_error.m), and `../structure-from-sherds-pp/docs/e2e-obj-to-reassembly.md`. Open the ticket branch with `C:/PR/scripts/ticket_start.sh SfSpp_preprocessing .scratch/pota-repro/issues/302-per-point-cost-landing.md`; runs go under `/data/gpfs/projects/punim2657/SfSpp/runs/` with `run.json` + index.tsv row; stage inputs by symlink (`scripts/stage_piece.sh`), copy no geometry; every sbatch gets `scripts/slurm_poll.sh <JOBID>` and its sacct State/ExitCode recorded here.

**Rules:** MATLAB stays the reference — the port must match it, never the other way round. No corpus files change: corrected axes go to NEW output paths under the run directory; corpus md5s unchanged. Read the run-to-run determinism note (AGENTS.md — mesh stage unseeded rays) before claiming byte-identity. Renders before/after for any geometry claim the conservator will read. Comments-only ticket edits (`## Comments (worker, 2026-11-04)`), checkboxes and Status stay with the lead. Commit nothing; lead commits.

- [ ] Fix: per-point cost in both paths of compute_biaxial_cao_error (cao.py:65, cao.py:72); the scalar-collapse docstring deleted; comment states the MATLAB per-point semantics
- [ ] Unit proof vs MATLAB on ≥3 pieces: per-point cost vectors agree (rel tol ≤1e-9 or documented float gap), including the Jacobian path
- [ ] Pot A regression: 8/8 pieces within 0.01 deg / 0.01 mm of the MATLAB-run axis, same K; reassembly 15/15 joins
- [ ] Corpus re-run (163 pieces): corrected axes written under the run dir; median + %-within-5° table in the Comments, split by released-axis quality tiers as in the diagnosis
- [ ] Juglet assembler E2E with corrected axes: pieces seated, mutual-consistency numbers beside ticket 68's hybrid (median AND tail, pieces 3/8/9 named), best-of-N reported if N>1
- [ ] Job IDs + sacct State/ExitCode for every sbatch, recorded in Comments
- [ ] Branch merged into main and pushed by lead, worktree removed, branch deleted (lead)
