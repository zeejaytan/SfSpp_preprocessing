# 302: Land the per-point Cao cost (kill the scalar collapse) + regression vs MATLAB + Juglet assembler E2E

**What to build:** the sfs_axes port returns, for every candidate axis, the authors' per-point Cao cost — not one whole-cloud number — so axis ranking actually ranks. Landing it must keep the port equal to the authors' MATLAB on Pot A, keep the Pot A regression green (8/8 pieces, 15/15 joins), re-run the corpus axes, and put the corrected axes through the Juglet assembler.

**Answers:** E1

**Blocked by:** none — the diagnosis is complete (lead session 2026-11-04); this ticket only lands and extends it.

**Status:** landed (lead 2026-11-04) — code on main; gate 4 result says do not swap Pot A axes; renders await the conservator's eye
Working in: DSH worker session sfs302 (2026-11-04); landed by lead session 2026-11-04
Branch: 302-per-point-cost-landing — merged into main (9b2fdef), worktree removed, branch deleted locally and on GitHub (lead 2026-11-04)


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

- [x] Fix: per-point cost in both paths of compute_biaxial_cao_error (cao.py:65, cao.py:72); the scalar-collapse docstring deleted; comment states the MATLAB per-point semantics — verified: read the merged diff of `sfs_axes/cao.py` (np.sum(..., axis=0), np.minimum, elementwise log-sum-exp in both paths) and `sfs_axes/potsac.py` (per-point GM robustify, sum ranking, per-point inlier count)
- [x] Unit proof vs MATLAB on ≥3 pieces: per-point cost vectors agree (rel tol ≤1e-9 or documented float gap), including the Jacobian path — 9/9 cells, R1 rel ~5e-15, Jacobian ≤7.6e-13 (job 34290017)
- [x] Pot A regression: 8/8 pieces within 0.01 deg / 0.01 mm of the MATLAB-run axis, same K; reassembly 15/15 joins — verified: recomputed from artifacts/pota302/pota302.tsv, 8/8 any-seed PASS (worst 5.18e-5 deg, 1.41e-4 mm). Reassembly 15/15 holds for the CORPUS-axis control arm; with corrected axes substituted it is 13/15 (gate 4)
- [x] Corpus re-run (163 pieces): corrected axes written under the run dir; median + %-within-5° table in the Comments, split by released-axis quality tiers as in the diagnosis — verified: recomputed corpus302.tsv seed 0, n=163, median 6.809954 deg, 44.2% ≤5 deg; axes to out/axes302, corpus md5 unchanged
- [x] Juglet assembler E2E with corrected axes: pieces seated, mutual-consistency numbers beside ticket 68's hybrid (median AND tail, pieces 3/8/9 named), best-of-N reported if N>1 — 0/9 seated for both arms; median 12.35 vs hybrid 12.31, tail loses (P3 20.05/10.78, P8 34.36/16.43, P9 55.61/23.83); best-of-3 identical at every seed
- [x] Job IDs + sacct State/ExitCode for every sbatch, recorded in Comments — 13 jobs, ledger in the worker comment and in /data/gpfs/projects/punim2657/SfSpp/runs/index.tsv
- [x] Branch merged into main and pushed by lead, worktree removed, branch deleted (lead) — merge commit on main; worktree closed with scripts/ticket_close.sh

## Comments (worker, 2026-11-04)

**Deviation at start:** `ticket_start.sh` refused (lead dispatch commit 1899e62 had
already set Status: in-progress), so the worktree
`C:/PR/worktrees/sfs/302-per-point-cost-landing` (branch `302-per-point-cost-landing`,
commit 01bff01, pushed -u) was created manually replicating the script's steps.

**Code (worktree, UNCOMMITTED per rules — lead commits):**
- `sfs_axes/cao.py` `compute_biaxial_cao_error`: cost_fwd/rev = `np.sum(R**2, axis=0)`
  per-point, elementwise min/log-sum-exp; same in the Jacobian path (g_fwd/g_rev
  weighted by the base softmax exactly as compute_biaxial_cao_error.m does); docstring
  states the MATLAB per-point semantics; returns R (n,), J (1,6,n).
- `sfs_axes/potsac.py`: `compute_axis_of_symmetry` now MATLAB-faithful — GM-robustify
  the per-point vector, rank by sum, count per-point cost < 1.0 (was degenerate
  `int(abs(err) < 1)` on a scalar). Docstring updated.
- `sfs_axes/refine.py`: stale "refine is silent no-op (PROVENANCE FINDING)" comment
  was a port artifact — in real MATLAB the residual is 1×n, shapes are consistent,
  method-2 LM refine genuinely runs; with the per-point fix both refine stages run.
- `tests/test_regression_pota.py`: noop test replaced by
  `test_refine_method2_converges_per_point`; Pot A thresholds 0.01°/0.01 mm (measured
  0.0031°/0.0012 mm). All 8 tests PASS on the laptop.

**Gate 1 — unit proof vs MATLAB: PASS.** Run `20261103-1608_01bff01_t302-unit-matlab`,
jobs 34289975 (FAILED: writematrix .tsv needs FileType/Delimiter) + 34290017
(COMPLETED 0:0, 39 s). 9/9 cells (Pot A 01/04/07 × released/+2°/+5° probes, n=355–3661):
R1 rel ~5e-15, Jacobian rel ≤7.6e-13, R3 rel ~5e-15 — far inside the 1e-9 bar.
Verified: read `logs/slurm-34290017.out` PASS lines directly.

**Gate 2 — Pot A regression vs MATLAB run_potsac on the CORPUS clouds: PASS (8/8,
best-of-10 seeds).** Run `20261103-1655_01bff01_t302-pota-ml`, jobs 34290299 (FAILED:
fprintf newline) + 34290387 (FAILED exit 1 — scoring bug in MY summary line only, see
below). MATLAB arm: shipped `run_potsac.m` (sfs_preprocessing @0724e5d, adaptive step,
rng(0)); Python arm: corrected port, adaptive step, seeds 0..9, LIVE refine.
Per piece, seeds of 10 within 0.01°+0.01 mm of the MATLAB axis: p1 6, p2 8, p3 8,
p4 5, p5 10, p6 10, p7 3, p8 7; best direction error 0°–5.2e-5°. The job's exit-1 came
from my summary picking best-by-angle-only; piece 7's angle-best seed had a position
miss (712 mm) while other seeds match both to ≤3e-4 — recomputed from
`out/pota302.tsv` (artifacts/pota302/pota302.tsv) under the any-seed criterion: 8/8
PASS. Honest caveats: the chain is multimodal — pieces 4/7/8 have 3–7/10 seeds on the
MATLAB mode; piece 7's position has near-tie modes; and vs the RELEASED axes the
faithful chain sits 0.6°–35.9° off (p6 24°, p8 36°) — consistent with the lead's
residual (a): where released axes are wrong the port disagrees with them by design.
Superseded first attempt `20261103-1612_01bff01_t302-pota-axes` (jobs 34290091 FAILED
ImportError canonicalize + 34290162 FAILED exit 1) compared the WRONG reference (2025
`axis_output` files: 500-pt clouds, different frame) — kept for the record.

**Gate 3 — corpus re-run, NEW paths: PASS (mechanics) + numbers.** Run
`20261103-1612_01bff01_t302-corpus-axes`, job 34290092 (FAILED ImportError) +
34290163 (COMPLETED 0:0, 4m10s). 163 pieces × seeds 0..4, step=10, corrected axes
written to `out/axes302/` (163 files, position-first, canonicalized); corpus md5
before == after (b1275e9853ac1b86d007ec1661429feb); corpus read-only.
Seed-0 error to released line 1: median 6.81°, 44.2% within 5° (lead's diagnosis:
6.19°, 46% — same within seed noise). Tiers (released-vs-GT ≤5°): gt_close n=92
median 3.20° (67.4% ≤5°); gt_off n=49 median 19.69° (8.2%); no_gt n=22 median 15.74°
(27.3%) — disagreement concentrates exactly where the released axes are wrong.
Seeds 1–4 stability: median 7.32°, p90 58.7°, worst 89.8° over 652 runs.

**Gate 4 — Juglet + Pot A assembler E2E: control PASS, corrected-axes arms MIXED
(honest).** Run `20261103-1620_01bff01_t302-e2e`, jobs 34290134 (CANCELLED dep),
34290170 (arms exit 127 — arm67.sh not in /panel; fixed), 34290309 (COMPLETED 0:0,
6m34s). Arms (floor, tree, exit):
- F20O Juglet@20 Dataset axes (baseline): 0, candidates 23 — equals the t67/t68
  baseline; Sherd accuracy 0/9.
- F20N Juglet@20 corrected port axes (9 Axes-only substitutions, verified by diff):
  0, candidates 23→37 (t68 hybrid: 35); Sherd accuracy 0/9 both; score58 piece 2
  raw 136.2°→17.4°, pieces with T 2→5. No seated gain.
- GPA50 Pot A@50 corpus axes (control): 8/8 placed, 15/15 joins — control HOLDS
  (= guard68).
- GPA50N Pot A@50 corrected axes302 substituted (8 Axes-only, verified): **7/8,
  13/15 — a regression vs the control.** The faithful per-point chain moves Pot A
  axes 0.6°–36° off the released ones (p6 24°, p8 36°), and the assembler loses one
  piece and two joins. Claim: (2) the corrected axes are faithful to MATLAB but the
  RELEASED Pot A axes are the better input for assembly — do not swap Pot A axes on
  the strength of this ticket.
Juglet mutual consistency (fit68 gate, in-job `juglet302.py`, seeds 0/1/2 identical):
old Dataset axes median 27.1° (worst 77.3); corrected port median 12.35° (ties t68
hybrid 12.31) but tail LOSES as predicted: P3 20.05 (hybrid 10.78), P8 34.36 (16.43),
P9 55.61 (23.83). Reported best-of-3 = same at every seed.

**Renders:** run `20261103-1705_01bff01_t302-renders`, jobs 34290434 (FAILED
broadcast) + 34290594 (COMPLETED 0:0). 8 PNGs (old vs corrected vs overlay, top+side)
for Pot A 01/02 and Juglet 8/9 in `SfSpp_preprocessing/artifacts/pota302/` (laptop).
This model could not eye-check them (no image input) — lead/conservator to look.

**Jobs ledger (all sacct-checked):** 34289975 FAILED 1:0 · 34290017 COMPLETED 0:0 ·
34290091 FAILED 1:0 · 34290092 FAILED 1:0 · 34290162 FAILED 1:0 · 34290163 COMPLETED
0:0 · 34290134 CANCELLED · 34290170 COMPLETED 0:0 (arms 127) · 34290299 FAILED 1:0 ·
34290387 FAILED 1:0 (job script exit; data good, verdict recomputed) · 34290309
COMPLETED 0:0 · 34290434 FAILED 1:0 · 34290594 COMPLETED 0:0. Index rows appended in
`/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv` citing every attempt.

**Artifacts (laptop, gitignored):** `SfSpp_preprocessing/artifacts/pota302/` —
pota302.tsv, corpus302.tsv, gate302.tsv, 8 render PNGs. Stage scripts:
`.scratch/pota-repro/302-stage/`. Nothing committed; nothing pushed beyond the
ticket-start branch.

## Comments (lead, 2026-11-04 — landing and independent verification)

Landed in merge commit on main (branch `302-per-point-cost-landing`, worktree closed with
`scripts/ticket_close.sh`). What I re-checked myself rather than taking from the report:

- **The diff is the fix.** Read `sfs_axes/cao.py`: `np.sum(fwd ** 2, axis=0)`,
  `np.minimum`, elementwise log-sum-exp — in BOTH the plain and the Jacobian path; the
  false scalar docstring is gone. `sfs_axes/potsac.py`: per-point GM robustify, rank by
  `np.sum(rob)`, inliers `np.sum(np.abs(rob) < INLIER_THRESHOLD)`. Diffstat +43/−34 over
  4 files, matching the report.
- **Tests on main after the merge:** `python -m pytest tests/ -q` → `8 passed in 1.13s`.
- **Gate 2 recomputed from the TSV, not from the summary line:**
  `artifacts/pota302/pota302.tsv`, indexed by header name — 8/8 pieces pass the any-seed
  0.01° / 0.01 mm criterion (p1 0.00e+0° / 1.28e-6 mm; p7 5.18e-5° / 1.41e-4 mm;
  p4 1.09e-5°; every piece ≤0.01). `verified: artifacts/pota302/pota302.tsv -> 8/8 PASS`
- **Gate 3 recomputed:** `artifacts/pota302/corpus302.tsv` seed 0, n=163 → median
  6.809954°, 44.2% within 5°. `verified: artifacts/pota302/corpus302.tsv -> 6.81 deg / 44.2%`
- **Renders: NOT eye-checked, and that is still owed.** `read_image` refuses (this
  session's model has no image input) and `modlens_read_image` returned Gemini 503
  UNAVAILABLE twice. I could only confirm the 8 PNGs are 1540×476 with both overlay
  colours present (red ~255,0,0 and blue ~0,0,255; 676–2048 saturated pixels each) — that
  proves the panels rendered, NOT that the axes land on the morphology. **Needs-eye:
  conservator to look at the four pieces (Pot A 01/02, Juglet 8/9), top and side.**

**What this ticket establishes, in order of confidence:**
1. The port now computes what the authors' MATLAB computes — the scalar collapse was a
   translation error, and the saturation it caused (score ≈1.99999998 for every candidate,
   i.e. all axes ranking the same) is gone. Units prove it to 1e-13, Pot A to 5e-5°.
2. The corpus axes are corrected on disk at `out/axes302` (163 pieces), corpus md5
   unchanged.
3. **Claim (2), measurement finding, stated plainly:** the MATLAB-faithful axes are not the
   better input for the assembler. Substituting them on Pot A takes the control from 8/8
   placed and 15/15 joins down to 7/8 and 13/15. So the released Pot A axes stay, and this
   ticket changes no corpus data. That is a real limit on what "faithful to the paper"
   buys us, not a reason to distrust the fix.
4. On the Juglet the corrected chain still does not seat a single piece (0/9, same as the
   baseline) and it trades t68's hybrid: tie on median mutual consistency (12.35° vs
   12.31°), worse in the tail (P8 34.36° vs 16.43°). No gain to claim.

**Correction to an earlier lead claim, recorded so it is not repeated:** the pre-ticket
note that the corrected port "beats" ticket 68 was wrong — it ties on the median and loses
the tail.

**New finding worth its own line:** `sfs_axes/refine.py` carried a "PROVENANCE FINDING:
refine is a silent no-op" comment. That too was a port artefact — the no-op followed from
the scalar collapse making the residual shape inconsistent. With per-point residuals both
method-2 LM refine stages genuinely run. Anything previously reasoned from "refine never
runs" should be re-read.

**Close-out (lead, 2026-11-04).** `ticket_close.sh` passed every check ("merged into
origin/main, nothing uncommitted, every commit on GitHub, Status: landed") and removed the
worktree; it tripped on deleting the branch because the worktree still held it, so the branch
was deleted by hand after re-proving `git merge-base --is-ancestor refs/heads/302-per-point-cost-landing
origin/main` → merged (was 312708f), locally and on GitHub. Board rebuilt: 12 checks, 10
passed, 2 skipped, 719 tickets.

The script's Spartan reminder could not be discharged from this session — `ssh spartan`
returns "Permission denied (publickey…)" here, so `squeue` was not read. That is safe: all
13 jobs in the ledger above are sacct-terminal (COMPLETED/FAILED/CANCELLED), so none of them
can still be running. Worth one `squeue -u $USER` the next time a session has the key.
