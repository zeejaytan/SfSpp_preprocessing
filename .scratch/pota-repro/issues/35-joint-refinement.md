# 35: Last single + joint refinement — interaction gets its fair trial

**What to move:** strict from 10–11/15 (ORIG) / 9–11/15 (fresh) toward 15/15.

**Answers:** E1

**Blocked by:** 34-c1-retest (position below).

**Status:** results-in — both handles exhausted, no 15/15 (S strict 10/15 + 9/15 D-identical, T strict 8/15 + 9/15); CheckGraph-50 and joint-refinement move nothing

**Starting position (tickets 29–34):** every fork-delta single is spent except one: the CheckGraph-plausibility site, currently at the validated relaxation 150, whose TRUE upstream is 50 (ticket-34 correction — fork-root blame-verified; do NOT test →100, that was never upstream anywhere). Handle #1 is that single: 150→50.

Handle #2 is the first principled combination, justified by single-exhaustion rather than guessed at: the JOINT-REFINEMENT arm — Cauchy (Icp/Reg5/Reg6) + max_iteration + tolerance + isConverge ALL at upstream SIMULTANEOUSLY, on the abl2 base, with the fork IcpIncGraphAxis weighting KEPT (ticket-31 L proved the fork weighting load-bearing on ORIG; an arm without it is predictably ORIG-negative). Each single was neutral alone; this tests interaction within the refinement stage. If it moves strict, the successor bisects within; if not, refinement is closed as a stage and the search moves to admission×refinement interaction or the cure-tree diff.

Explicitly OUT (lead decision, recorded so no future ticket re-proposes): C1×weighting cells — P covered fork-weighting+C1-upstream (neutral), L covered upstream-weighting+C1-fork (ORIG-negative), and both-upstream is predictably ORIG-negative by L. C6 stays (validated fix); C7 stays (inert); C9-site2 stays fork (F proved upstream worse).

**Valid-run rule:** asserts pass + snapshots non-empty + ORIG snapshots-strict in 9–11/15; pruned counts recorded, non-gating; fresh strict is the score; stop at the first strict 15/15 with valid ORIG.

**Rules:** shim-driven k=5/b=3; base = abl2 + nothing else; ONE variable-set per run (the joint arm is one arm, not stepwise); no commits; reuse tickets 29–34 bundle, scripts, fetch discipline.

- [ ] CheckGraph site 150→50 (one run): strict table + seating render
- [ ] Joint-refinement arm (one run, only if the single moves nothing): strict table + seating render
- [ ] Laptop poll per sbatch via sacct directly; job IDs + sacct states; Comments-only ticket edits

**Successor:** bisect the joint arm if it moves; else re-derive from the cure tree (upstream + P22FIX + P22FIX2 = 15/15) by forward-porting remaining fork deltas one commit-cluster at a time; then land the full set; then B–J E2E on admitted fragments.

## Comments (worker, 2026-10-16)

**Verdict: ordered list exhausted, no 15/15 anywhere. S strict 10/15 ORIG + 9/15 fresh (both edge-identical to the D reference at printed precision), T strict 8/15 ORIG + 9/15 fresh (fresh failing set = D-fresh; ORIG −2 the wrong way). The last fork-delta single is spent, and the refinement stage is now closed as a combination too: every refinement single was neutral alone (tickets 30–34), and all-upstream-simultaneously moves nothing toward 15/15. No commits anywhere.**

**0. Provenance (read-only; ticket-34 blame re-confirmed in-tree).** CheckGraph `:1838` line carries the P22FIX2 comment `(was PAPER-CONFIG S=50)` and ticket-34 fork-root blame-verified the value line's root as 50 — upstream 50, NOT 100. Arm S restored exactly that (150→50, one line, `POTA35-S` marker). Joint arm T = 22 transplanted lines from the four proven single-arm sources, value-identical (line-number transplant from src_M/src_R-Reg6/src_N/src_I/src_J with only the marker tag re-stamped `POTA35-T`): Cauchy 5.0/2.0×3 at Icp (`:1453-56`) + Reg5 (`:1702-05`) + Reg6 (`:1918-21`); max_iteration 150→50 outer at the 3 pairwise sites (`:1354/:1615/:1820`) + axis 200/200→100/100 (`:2060`); tolerance 1e-6→CERES_FUNC_TOL at all 5 Solve sites (`:1496/:1745/:1968/:2167/:2374`); isConverge 0.02/0.2→0.05/1.0 at site 4 (`:2198`). Fork IcpIncGraphAxis weighting KEPT and asserted in-job (`CauchyLoss(cauchy_dist)` + `loss_axis 1.0` present). Base both arms = abl2 + nothing else (S diff = 2 files, recon untouched, `CauchyLoss(4.0)` count = 3; T diff = 3 files, recon +22/−22).

**1. S — CheckGraph 150→50 on abl2 base (job 33173718, COMPLETED 0:0, ~12 min). VALID (LINK-SHIM-OK + DRIVER-SHIM-OK both arms, 8 T-files each, pruned exact 63 ORIG / 103 fresh) + NEGATIVE, D-identical.** Binary 7/8+9/15 ORIG, 7/8+11/15 fresh (fresh binary +1 edge vs D with byte-identical strict — more tally/geometry decoupling). Strict: ORIG **10/15**, fresh **9/15**, every edge identical to D at printed precision. Render `artifacts/pota35/pota35_seating_S.png` eye-checked: both rings closed, all 8 loops seated.
- S-orig 10/15: 1-2 1.41/8.17 PASS; 1-3 2.27/8.91 PASS; 1-4 1.46/6.91 PASS; 1-5 3.06/20.68 fail; 1-6 1.93/9.87 PASS; 1-7 1.07/6.24 PASS; 2-4 2.35/4.31 PASS; 2-5 3.72/26.70 fail; 2-8 2.62/10.92 fail; 3-5 0.84/6.34 PASS; 3-6 3.04/10.37 fail; 4-6 2.06/11.06 fail; 4-7 1.66/7.49 PASS; 4-8 1.43/8.19 PASS; 6-7 1.19/7.85 PASS.
- S-fresh 9/15: 1-2 1.12/2.35 PASS; 1-3 1.96/7.37 PASS; 1-4 0.92/7.13 PASS; 1-5 3.27/23.00 fail; 1-6 1.36/8.01 PASS; 1-7 0.67/1.31 PASS; 2-4 1.60/5.47 PASS; 2-5 4.11/29.10 fail; 2-8 2.76/13.79 fail; 3-5 1.39/10.82 fail; 3-6 1.90/11.82 fail; 4-6 1.32/9.29 PASS; 4-7 0.85/4.05 PASS; 4-8 3.72/18.00 fail; 6-7 0.97/5.50 PASS.
- src = `pota30/src_S`, sbatch `run_pota35_s.sbatch`, RUNDIR `sfs_main/pota35s_run_33173718`.

**2. T — JOINT-REFINEMENT all-upstream on abl2 base (job 33190496, COMPLETED 0:0, ~10 min). Geometry valid (asserts + 8 T-files each, both rings seated, no collapse) + NEGATIVE; ORIG strict 8/15 sits just below the 9–11/15 validity band, fresh 9/15 = D.** Binary 0/8+0/15 ORIG (scored, not geometric — render shows a seated ring, same decoupling as ticket-30 E/G), 7/8+10/15 fresh. Pruned 62 ORIG / 106 fresh (off-reference, recorded non-gating per ticket). Strict: ORIG **8/15** (D's 5 fails + 1-6 9.87→10.92 and 4-7 7.49→11.17 flip over the line — a genuinely different, slightly worse minimum, not noise: two edges move 1–3.7mm the wrong way); fresh **9/15** with the exact D-fresh failing set (1-5, 2-5, 2-8, 3-5, 3-6, 4-8). Render `artifacts/pota35/pota35_seating_T.png` eye-checked: T-orig and T-fresh both closed rings, all 8 loops present.
- T-orig 8/15: 1-2 1.51/6.63 PASS; 1-3 2.46/8.48 PASS; 1-4 1.61/7.64 PASS; 1-5 3.04/20.77 fail; 1-6 1.86/10.92 fail; 1-7 1.83/8.59 PASS; 2-4 2.77/4.08 PASS; 2-5 3.83/27.58 fail; 2-8 2.59/11.16 fail; 3-5 0.76/6.05 PASS; 3-6 3.05/11.55 fail; 4-6 2.35/14.68 fail; 4-7 2.53/11.17 fail; 4-8 1.45/7.15 PASS; 6-7 0.72/3.95 PASS.
- T-fresh 9/15: 1-2 0.99/2.02 PASS; 1-3 2.01/7.10 PASS; 1-4 1.03/7.84 PASS; 1-5 3.22/22.68 fail; 1-6 1.06/6.51 PASS; 1-7 0.76/2.14 PASS; 2-4 1.62/5.90 PASS; 2-5 3.93/27.99 fail; 2-8 2.34/10.68 fail; 3-5 1.31/10.20 fail; 3-6 2.32/10.67 fail; 4-6 1.62/8.09 PASS; 4-7 0.82/3.70 PASS; 4-8 2.32/11.39 fail; 6-7 1.24/8.43 PASS.
- src = `pota30/src_T`, sbatch `run_pota35_t.sbatch`, RUNDIR `sfs_main/pota35t_run_33190496`.

**3. Tally (binary ORIG / strict ORIG / binary fresh / strict fresh; D = ticket-30 reference):** D 8/8+13/15 / 10 / 7/8+10/15 / 9 · S 7/8+9/15 / 10 / 7/8+11/15 / 9 · T 0/8+0/15 / 8 / 7/8+10/15 / 9. Failing strict edges every arm: translations on 1-5, 2-5 (20–29mm) ± 2-8/3-5/3-6/4-6/4-8 (10–18mm); rotations pass everywhere (worst 4.11°).

**4. Jobs (sacct):** 33173718 (S) + 33190496 (T) COMPLETED 0:0. 33189930 FAILED 1:0 in 6s — stillborn, my T-sbatch `SRC_T` variable pointed at `src_S` (sed renamed the variable, not its value); the in-job 3-file guard caught it before any build, fixed + resubmitted same hour. Poll was `sacct` directly throughout (never `slurm_poll.sh`). No contaminated arms exist.

**5. Evidence (laptop `artifacts/pota35/`):** `s_fetch.tgz` / `t_fetch.tgz` + unpacked `pota29_fetch/` (T_S_*, T_T_*, P30_*.txt, GT, rims_fresh); `p35_render_S.py` / `p35_render_T.py`; `pota35_seating_S.png`, `pota35_seating_T.png`. Spartan: `/data/gpfs/projects/punim2657/pota30/` (`src_S`, `src_T`, `run_pota35_{s,t}.sbatch`), `sfs_main/pota35s_run_33173718` + `sfs_main/pota35t_run_33190496` RUNDIRs. No commits in either repo (laptop `SfSpp_preprocessing` only this ticket file; Spartan additions are untracked scratch).

**Proposal for lead:** per the ticket successor, refinement is closed as a stage (singles neutral in tickets 30–34, joint moves nothing-or-wrong). Next is the cure-tree re-derivation: forward-port remaining fork deltas one commit-cluster at a time from (upstream + P22FIX + P22FIX2 = 15/15). Nothing to land.
