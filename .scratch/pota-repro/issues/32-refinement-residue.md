# 32: Refinement residue — Cauchy scales, then max_iteration, back to upstream

**What to move:** strict from 10–11/15 (ORIG) / 9–11/15 (fresh) toward 15/15.

**Answers:** E1

**Blocked by:** 31-translation-bias (position below).

**Status:** results-in — both handles exhausted, no 15/15 (M strict 10/15 + 9/15, N strict 10/15 + 9/15, all four edge-identical to D); refinement residue is neither Cauchy scale nor iteration count

**Starting position (ticket 31, jobs 33165329/33165822):** RejectOutlier is upstream (K: +1 edge, noise-adjacent, floor stands); the fourth site has no delta; the IcpIncGraphAxis weighting is fork-new and load-bearing (L: restoring upstream craters ORIG to 6/15 yet lifts fresh to 11/15 — best fresh yet). So the floor lives in the refinement stage, and neither weighting is the answer. Remaining refinement deltas, one at a time: (a) Cauchy scales at the Icp/Registration5 sites, fork-tightened 4.0/1.8 vs upstream 5.0/2.0 (ticket-07 lane — validated on the old binary, never re-ablated post-gate-fix); (b) `max_iteration` 150/200 vs upstream 50/100. The `isSimilarTrans` chunk-merge threshold (C1, exonerated as sole cause) is HELD for a combination ticket — do not burn runs on it here.

**Valid-run rule (from ticket 30):** pruned counts exact (63 ORIG / 103 fresh) + ORIG laptop-strict in the 9–11/15 band. Fresh strict is the score to move. Stop at the first strict 15/15 with valid ORIG.

**Rules:** shim-driven k=5/b=3 with LINK-SHIM-OK + DRIVER-SHIM-OK asserts; non-empty snapshots; provenance (upstream value + introducing commit) confirmed per handle before ablating; base = abl2 (pairwise 0.436) + nothing else; no commits; reuse tickets 29–31 bundle, scripts, fetch discipline.

- [ ] Cauchy scales back to upstream 5.0/2.0 at the Icp/Registration5 sites: strict table + seating render
- [ ] max_iteration back to upstream 50/100 — only if Cauchy moves nothing
- [ ] Laptop poll per sbatch via sacct directly; job IDs + sacct states; Comments-only ticket edits

**Successor:** land the full set on the reproduced strict run; then B–J E2E on admitted fragments.

## Comments (worker, 2026-10-16)

**Verdict: ordered list exhausted, no 15/15 anywhere. M strict 10/15 ORIG + 9/15 fresh, N strict 10/15 ORIG + 9/15 fresh — all four arms edge-identical to the D reference down to 0.01mm. The ~7–9mm translation floor survives both remaining refinement deltas. No commits anywhere.**

**0. Provenance per handle (upstream = `sfs_main/sfs_p22fix_src/class/reconstruction.cpp`, fork = `pota29/asm @ 11f4827`; read-only diffs + `git blame`).**
- (a) Cauchy scales: UPSTREAM 5.0/2.0/2.0/2.0 at all 5 Solve sites (upstream :1215-18, :1417-20, :1610-13, :1783-86, :1970-73). Introducing commit = bulk fork `869e696` (`CauchyLoss(4.0)` + `1.8×3` at the Icp/Registration5/Registration6 blocks, commented "RELAXED ... was 3.0/1.5, original 5.0/2.0" — fork-new, unvalidated at introduction). Ticket-07 validation context (assembly `.scratch/cauchy-scales/`, NOT pota-repro-07): ticket 06 Arm H ran a Huber diagnostic at the solver-01-root scales (`34cf112`); ticket 07 (`b4ff2c4`, 2026-10-14) reverted the E-6 Huber experiment back to Cauchy at the same 4.0/1.8 scales, validated by confirming run 32948918 reproducing the E-6 control exactly (2/8+1/15) with pair 1-4 seating again — i.e. validated on the old assembly binary's sherd metric, never re-ablated post-gate-fix on the shim k=5/b=3 strict metric. Ablation (arm M): restore upstream 5.0/2.0/2.0/2.0 at the Icp + Registration5 blocks only (the two sites the ticket names); Registration6 block left at fork 4.0/1.8 as the control.
- (b) `max_iteration`: UPSTREAM 50 outer / 100 ceres at Icp + 2×Registration (upstream :1132, :1337, :1521), 100/100 at the last two sites (:1737, :1925). Introducing commits: Icp 150 = `6d17fc7` (PAPER-CONFIG 2026-10-01, paper line 240 ICP max 150); Registration 150s = `2de281a` (CONTROL WON 2026-10-02, job 32087141: 0/8 at 50 vs 2/8 at 150 — validated then, on the old binary); axis-site 200/200 = bulk `869e696` ("FIXED: More iterations", unvalidated). Ablation (arm N, authorized because M moved nothing): 150→50 outer at the 3 pairwise sites (ceres already upstream 100), axis-site 200/200→100/100; IcpFine already upstream (100/100), untouched.

**1. M — Cauchy upstream at Icp+Reg5 on abl2/D-base (job 33166638, COMPLETED 0:0). Strict-identical to D; geometry-identical to D.** Binary 8/8+14/15 ORIG, 7/8+10/15 fresh. Strict: ORIG **10/15**, fresh **9/15**, every edge within 0.01 of D (M-orig max snapshot diff vs D-orig 0.71mm on one piece, M-fresh vs D-fresh 0.001mm). Pruned counts 61 ORIG / 105 fresh (FLAGGED vs the 63/103 rule — yet geometry is D-identical, further proof the log count does not track saved geometry; cf. ticket-30 E/G/H). LINK-SHIM-OK + DRIVER-SHIM-OK both arms, 8 T-files each. Render `artifacts/pota32/pota32_seating_M.png` eye-checked: both rings closed, all 8 loops seated.
- M-orig strict 10/15: 1-2 1.41/8.17 PASS; 1-3 2.27/8.91 PASS; 1-4 1.46/6.91 PASS; 1-5 3.06/20.68 fail; 1-6 1.93/9.87 PASS; 1-7 1.07/6.24 PASS; 2-4 2.35/4.31 PASS; 2-5 3.72/26.70 fail; 2-8 2.62/10.92 fail; 3-5 0.84/6.34 PASS; 3-6 3.04/10.37 fail; 4-6 2.06/11.06 fail; 4-7 1.66/7.49 PASS; 4-8 1.43/8.19 PASS; 6-7 1.20/7.85 PASS.
- M-fresh strict 9/15: 1-2 1.12/2.35 PASS; 1-3 1.96/7.37 PASS; 1-4 0.92/7.13 PASS; 1-5 3.28/23.00 fail; 1-6 1.36/8.01 PASS; 1-7 0.67/1.32 PASS; 2-4 1.60/5.47 PASS; 2-5 4.11/29.10 fail; 2-8 2.76/13.79 fail; 3-5 1.39/10.82 fail; 3-6 1.90/11.82 fail; 4-6 1.32/9.29 PASS; 4-7 0.85/4.05 PASS; 4-8 3.72/18.00 fail; 6-7 0.97/5.50 PASS.

**2. N — max_iteration upstream (50/100) on abl2/D-base (job 33167222, COMPLETED 0:0). VALID run (pruned exact 63/103); strict-identical to D.** Binary 8/8+14/15 ORIG, **8/8+14/15 fresh** (first fresh 8/8+14/15 — yet strict still 9/15: more tally/geometry decoupling). Strict: ORIG **10/15**, fresh **9/15**, edge-identical to D (N-vs-D snapshot max diff 0.017mm ORIG, 0.001mm fresh). LINK-SHIM-OK + DRIVER-SHIM-OK both arms, 8 T-files each. Render `artifacts/pota32/pota32_seating_N.png` eye-checked: both rings closed, all 8 loops seated both arms.
- N-orig strict 10/15: 1-2 1.41/8.17 PASS; 1-3 2.28/8.91 PASS; 1-4 1.46/6.91 PASS; 1-5 3.06/20.68 fail; 1-6 1.93/9.87 PASS; 1-7 1.07/6.24 PASS; 2-4 2.35/4.31 PASS; 2-5 3.72/26.70 fail; 2-8 2.62/10.92 fail; 3-5 0.84/6.34 PASS; 3-6 3.04/10.37 fail; 4-6 2.06/11.06 fail; 4-7 1.66/7.49 PASS; 4-8 1.43/8.19 PASS; 6-7 1.20/7.85 PASS.
- N-fresh strict 9/15: 1-2 1.12/2.35 PASS; 1-3 1.96/7.37 PASS; 1-4 0.92/7.13 PASS; 1-5 3.27/23.00 fail; 1-6 1.36/8.01 PASS; 1-7 0.67/1.31 PASS; 2-4 1.60/5.47 PASS; 2-5 4.11/29.10 fail; 2-8 2.76/13.79 fail; 3-5 1.39/10.82 fail; 3-6 1.90/11.81 fail; 4-6 1.32/9.29 PASS; 4-7 0.85/4.05 PASS; 4-8 3.72/18.00 fail; 6-7 0.97/5.50 PASS.

**3. Tally (binary ORIG / strict ORIG / binary fresh / strict fresh; D = ticket-30 reference):** D 8/8+13/15 / 10 / 7/8+10/15 / 9 · M 8/8+14/15 / 10 / 7/8+10/15 / 9 · N 8/8+14/15 / 10 / 8/8+14/15 / 9. Failing strict edges every arm: translations on 1-5, 2-5 (20–29mm) ± 2-8/3-5/3-6/4-6/4-8 (10–14mm); rotations pass everywhere (worst 4.11°).

**4. Jobs (sacct):** 33166638 (M) + 33167222 (N), both COMPLETED 0:0 (~13 min each). Poll was `sacct` directly throughout (never `slurm_poll.sh`). Process notes: N sbatch shipped without the POTA32-M contamination-grep guard (a `sed` delimiter miss, caught post-submit) — harmless: `src_N` was built fresh from `src_K`+checkout and verified M-marker-free (0 hits) with diff --numstat = 3 before submit; all other N guards passed in-job. `pota29/asm` shows a pre-existing uncommitted P22FIX hunk (mtime 12:21, before this session) — not mine, untouched.

**5. Evidence (laptop `artifacts/pota32/`):** `m_fetch.tgz` / `n_fetch.tgz` + unpacked `pota29_fetch/` (T_M_*, T_N_*, P30_*.txt, GT, rims_fresh); `p32_render_M.py` / `p32_render_N.py`; `pota32_seating_M.png`, `pota32_seating_N.png`. Spartan: `/data/gpfs/projects/punim2657/pota30/` (`src_M`, `src_N`, `run_pota32_m.sbatch`, `run_pota32_n.sbatch`), `sfs_main/pota32_run_33166638` + `sfs_main/pota32n_run_33167222` RUNDIRs. No commits in either repo (laptop `git status` clean apart from this ticket file; Spartan additions are untracked scratch).

**Proposal for lead:** (a)+(b) are spent — both restores reproduce D geometry to ≤0.71mm with strict edge-identical. The refinement residue is neither loss scale nor iteration budget. Remaining floor suspects outside tickets 29–32: the `isSimilarTrans` chunk-merge threshold (C1, held for a combination ticket), the fork's IcpIncGraphAxis weighting itself (ticket-31 L proved it load-bearing but wrong — neither fork nor upstream values seat strictly), or the pairwise stage upstream of refinement. Nothing to land.
