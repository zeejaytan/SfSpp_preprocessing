# 34: C1 retest on the abl2 base, then C5 true-upstream, then Reg6

**What to move:** strict from 10–11/15 (ORIG) / 9–11/15 (fresh) toward 15/15.

**Answers:** E1

**Blocked by:** 33-admission-residue (position below).

**Status:** results-in — all three handles exhausted, no 15/15 (P strict 10/15 + 9/15 D-identical, Q strict 10/15 + 9/15 D-identical, R strict 9/15 + 9/15); C1 soundly exonerated on a working base, C5 + Reg6 move nothing

**Starting position — a lead catch on the C1 exoneration (ticket 29 §3 reread):** the ablation-1 arms that "exonerated" the chunk-merge threshold ran on the port-state base whose pairwise gate was still the collapsed fork 0.610 (A arms scored ORIG 0/8 — the collapse signature; the abl2 restore came later in job 33153903). On a base where the pairwise stage vetoes everything, chunk-merge cannot show an effect either way — the exoneration is UNSOUND. C1 (RS:327 `isSimilarTrans` 0.2→0.436) has never been tested on a working base. That retest is handle #1.

**Handles in order:** (1) C1 0.2→0.436 on the abl2 base (fork + P22FIX + P22FIX2 + abl2 + nothing else); (2) C5 CheckGraph site2 back to TRUE upstream — P22FIX2 set 150 (a validated relaxation), upstream is 100, current value is neither-confirmed; restore 100, one run; (3) Reg6 Cauchy scales to upstream — first confirm the fork delta exists at Reg6 (M held it at fork values; if upstream ≡ fork there, kill with no run). C6 stays (validated fix); C7 stays (inert). No combinations in this ticket.

**Valid-run rule:** asserts pass + snapshots non-empty + ORIG snapshots-strict in 9–11/15; pruned counts recorded, non-gating; fresh strict is the score; stop at the first strict 15/15 with valid ORIG.

**Rules:** shim-driven k=5/b=3; base = abl2 + nothing else; no commits; reuse tickets 29–33 bundle, scripts, fetch discipline.

- [x] C1 retest on abl2 base: strict table + seating render
- [x] C5 site2 → 100 (only if C1 moves nothing): strict table + seating render
- [x] Reg6 Cauchy provenance + conditional ablation (only if prior handles move nothing)
- [ ] Laptop poll per sbatch via sacct directly; job IDs + sacct states; Comments-only ticket edits

**Successor:** if all three move nothing, a combination ticket (C1 × weighting, justified by single-exhaustion); then land the full set; then B–J E2E on admitted fragments.

## Comments (worker, 2026-10-16)

**Verdict: ordered list exhausted, no 15/15 anywhere. P strict 10/15 ORIG + 9/15 fresh (D-identical), Q strict 10/15 ORIG + 9/15 fresh (D-identical to 0.007mm), R strict 9/15 ORIG + 9/15 fresh. The ~7–9mm translation floor survives C1, C5, and Reg6. The C1 exoneration now stands on a working base (it was unsound in ticket 29, it is sound now). No commits anywhere.**

**0. Provenance (all read-only; upstream root = fork root `ab85ea3`, SeongJong-Yoo 2025-02-06).**
- C1: fork `ranking_system.cpp:327` = 0.2 (bulk 869e696); cure tree `sfs_p22fix_src:320` = 0.436 ("ICCV->Hierarchy 0.436 -> 0.35"). True upstream 0.436 confirmed.
- C5 CORRECTION to the ticket mandate: "upstream is 100" is true ONLY of the SingleOverlapTest site (fork-root = 100; PAPER-CONFIG 3ff4f8d 100→50 via REDUCED 20; current 50). The P22FIX2-touched CheckGraphPlausibility pairwise site (`:1838`, current 150) has fork-root = 50 — upstream 50, NOT 100. The `:1838` blame confirms it (structure lines `^ab85ea3`, value line uncommitted P22FIX2). So arm Q ablated SingleOverlapTest 50→100 with P22FIX2-150 untouched — the only reading of "site2 → 100" consistent with true-upstream values. If a future ticket wants the CheckGraph site at upstream, that is 150→50, NOT →100 (out of scope here; 150 is validated).
- Reg6: fork `reconstruction.cpp:1918-21` (Registration6 Solve block) = 4.0/1.8×3; upstream `sfs_p22fix_src:1783-86` = 5.0/2.0×3. Delta EXISTS → run authorized. Site is LIVE (inside the 6-arg `Registration` overload `:1804`, called from `feature_matching.cpp:1884` merge path). Ticket-32 M left exactly this block at fork values as control. Arm R restored 5.0/2.0 at Reg6 only (Icp `:1453` + Reg5 `:1702` verified still fork 4.0, `CauchyLoss(4.0)` count = 2; cosmetic `LogE0Residuals` line left untouched).

**1. P — C1 0.2→0.436 on abl2 base (job 33170950, COMPLETED 0:0, ~14 min). VALID (LINK-SHIM-OK + DRIVER-SHIM-OK both arms, 8 T-files each, pruned 63 ORIG / 103 fresh) + NEGATIVE, D-identical.** Binary 8/8+14/15 ORIG, 6/8+10/15 fresh. Strict: ORIG **10/15**, fresh **9/15**, every edge identical to the D reference (ticket-30 §1) at printed precision. Render `artifacts/pota34/pota34_seating_P.png` eye-checked: both rings closed, all 8 loops seated (fresh 6/8 binary seats — more tally/geometry decoupling). Base = abl2 + nothing else (diff vs HEAD 11f4827 = 2 files: fm P22FIX+ABL2, rs P22FIX2+C1; reconstruction.cpp untouched; no-C1+C2 joint: guards assert single markers). src = `pota30/src_P`, sbatch `run_pota34_p.sbatch`, RUNDIR `sfs_main/pota34p_run_33170950`.

**2. Q — C5 SingleOverlapTest 50→100 on abl2 base (job 33171566, COMPLETED 0:0, ~15 min). VALID (asserts + 8 T-files each, pruned exact 63/103) + NEGATIVE, D-identical to 0.007mm.** Binary 8/8+14/15 ORIG, 7/8+10/15 fresh. Strict: ORIG **10/15**, fresh **9/15**; snapshots vs D max abs diff 0.0073mm ORIG / 0.001mm fresh. Render `artifacts/pota34/pota34_seating_Q.png` eye-checked: both rings closed, all 8 loops seated. No-C1 + P22FIX2-150-intact asserted in-job (no joint arm). src = `pota30/src_Q`, sbatch `run_pota34_q.sbatch`, RUNDIR `sfs_main/pota34q_run_33171566`.

**3. R — Reg6 Cauchy 4.0/1.8→5.0/2.0 on abl2 base (job 33172719, COMPLETED 0:0, ~14 min). VALID ORIG (9/15 in-band) + moves nothing toward 15/15.** Binary 7/8+9/15 ORIG, 8/8+14/15 fresh. Strict: ORIG **9/15** (D 10/15; only churn: 1-6 9.87→10.77 flips to fail; failing set otherwise the same translation edges), fresh **9/15** (= D-fresh). Render `artifacts/pota34/pota34_seating_R.png` eye-checked: R-fresh ring closed all 8 seated; R-orig all 8 loops present, no collapse. Full R tables:
- R-orig 9/15: 1-2 1.40/8.24 PASS; 1-3 2.29/7.71 PASS; 1-4 1.35/6.50 PASS; 1-5 2.96/20.15 fail; 1-6 1.94/10.77 fail; 1-7 1.31/7.92 PASS; 2-4 2.24/4.20 PASS; 2-5 3.56/25.54 fail; 2-8 2.44/10.15 fail; 3-5 0.76/5.79 PASS; 3-6 3.05/10.36 fail; 4-6 2.00/11.68 fail; 4-7 1.80/8.64 PASS; 4-8 1.35/7.67 PASS; 6-7 0.86/5.90 PASS.
- R-fresh 9/15: 1-2 0.92/2.86 PASS; 1-3 1.89/6.94 PASS; 1-4 0.78/6.19 PASS; 1-5 3.27/22.91 fail; 1-6 1.39/8.20 PASS; 1-7 0.72/1.43 PASS; 2-4 1.25/3.06 PASS; 2-5 3.78/26.68 fail; 2-8 2.57/11.83 fail; 3-5 1.44/11.06 fail; 3-6 1.90/11.90 fail; 4-6 1.38/9.83 PASS; 4-7 0.92/4.22 PASS; 4-8 2.28/12.14 fail; 6-7 0.92/5.18 PASS.
- src = `pota30/src_R` (diff = 3 files: recon Reg6 4-line swap + inherited fm/rs), sbatch `run_pota34_r.sbatch`, RUNDIR `sfs_main/pota34r_run_33172719`.

**4. Tally (binary ORIG / strict ORIG / binary fresh / strict fresh; D = ticket-30 reference):** D 8/8+13/15 / 10 / 7/8+10/15 / 9 · P 8/8+14/15 / 10 / 6/8+10/15 / 9 · Q 8/8+14/15 / 10 / 7/8+10/15 / 9 · R 7/8+9/15 / 9 / 8/8+14/15 / 9. Failing strict edges every arm: translations on 1-5, 2-5 (20–29mm) ± 2-8/3-5/3-6/4-6/4-8 (10–18mm); rotations pass everywhere (worst 4.11°).

**5. Jobs (sacct):** 33170876 FAILED 1:0 (stillborn — my P-sbatch contamination guard listed POTA34-P as forbidden while the bulk rename put it there; no arms built, fixed + resubmitted same hour); 33170950 (P) + 33171566 (Q) + 33172719 (R) all COMPLETED 0:0. 33172507 FAILED 1:0 (stillborn — my R-guard `CauchyLoss(4.0).*Registration` regex matched the pre-existing Icp/Reg5 lines it was meant to protect; replaced with count=2 check, resubmitted same hour). Poll was `sacct` directly throughout (never `slurm_poll.sh`). Two stillborns were worker-side script bugs, both caught by the in-job guards before any build — no contaminated arms exist.

**6. Evidence (laptop `artifacts/pota34/`):** `p_fetch.tgz` / `q_fetch.tgz` / `r_fetch.tgz` + unpacked `pota29_fetch/` (T_P_*, T_Q_*, T_R_*, P30_*.txt, GT, rims_fresh); `p34_render_{P,Q,R}.py`; `pota34_seating_{P,Q,R}.png`. Spartan: `/data/gpfs/projects/punim2657/pota30/` (`src_P`, `src_Q`, `src_R`, `run_pota34_{p,q,r}.sbatch`), `sfs_main/pota34{p,q,r}_run_33170*` RUNDIRs. No commits in either repo (laptop `structure-from-sherds-pp` still holds only the pre-existing P22FIX/P22FIX2 uncommitted hunks; `SfSpp_preprocessing` only this ticket file; Spartan additions are untracked scratch).

**Proposal for lead:** per the ticket successor, the floor now needs the combination ticket (C1 × weighting variants — singles are exhausted across tickets 29–34: C2 landed, C1/C3/C4/C5/C8/C9/C10/Cauchy/iters/RejectOutlier/weighting/Reg6 all spent as singles). Nothing to land.
