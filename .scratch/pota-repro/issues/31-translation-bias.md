# 31: Translation bias — RejectOutlier, fourth site, refinement weighting

**What to move:** strict from 10/15 (ORIG) / 9/15 (fresh) toward 15/15.

**Answers:** E1

**Blocked by:** 30-translation-floor (position below).

**Status:** results-in — all three handles exhausted, no 15/15 (best strict 11/15 ORIG K-arm + 11/15 fresh L-arm); translation floor survives (a) and (c), (b) killed by provenance

**Starting position (ticket 30, jobs 33156112–33164457):** the ~7–9mm floor is not correspondence thinning (C9 sites 1+3 inert, site 2 weakly wrong-way), not a dead floor (C8), not solver tolerance or the converge gate (C10 moves the minimum, not the floor). Every surviving failing edge involves pieces 5/6/8 (±2) at 10–29mm with rotations ≤4.1° — a systematic translation bias in the pairwise/refinement stage. Candidate handles, one at a time: (a) the `RejectOutlier(20, 0.7)` tightening (adopted in Row-3, never ablated against the floor) — first establish whether its values are upstream or fork-new (provenance before ablation); (b) `MINIMUM_NUMBER/2` vs `>3` at the fourth correspondence site; (c) refinement weighting. Stop at the first arm that reaches strict 15/15 with a valid ORIG.

**New valid-run rule (lead decision, ticket 30 proof):** the binary log-tally is RETIRED — bit-identical snapshots scored 8/8+13/15 in one run and 7/8+7/15 in another, so it tracks beam-selection luck, not geometry. A run is valid when (1) pruned counts match the reference exactly (63 ORIG / 103 fresh; I-arm's 104 flagged, not voided), and (2) ORIG laptop-strict lands in the 9–10/15 noise band. Fresh strict is the score to move. Past E/G/H arms count as valid negatives under this rule.

**Rules:** shim-driven k=5/b=3 with LINK-SHIM-OK + DRIVER-SHIM-OK asserts; non-empty snapshots; provenance (upstream value + introducing commit) BEFORE ablating each handle; no commits; reuse ticket 29/30 bundle, scripts, and fetch discipline.

- [ ] Provenance per handle (upstream value? which commit changed it? validated or drift?)
- [ ] One ablation per run in the order (a)→(b)→(c); strict table + seating render per moving arm
- [ ] Laptop poll per sbatch via sacct directly; job IDs + sacct states; Comments-only ticket edits

**Successor:** land the full set on the reproduced strict run; then B–J E2E on admitted fragments.

## Comments (worker, 2026-10-16)

**Verdict: ordered list exhausted, no 15/15 anywhere. Best strict 11/15 (K-orig) + 11/15 (L-fresh). The ~7–9mm translation floor survives (a) and (c); (b) died in provenance — no fork delta exists, so no run was burnt. No commits anywhere.**

**0. Provenance per handle (upstream = `sfs_main/sfs_p22fix_src/`, fork = `pota29/asm @ 11f4827`; all read-only diffs + `git blame`).**
- (a) `RejectOutlier(20, 0.7)`: UPSTREAM values — `sfs_p22fix_src/class/reconstruction.cpp:460,524,587` all `(20, 0.7)`. Row-3 commit `98a18985` (2026-10-09) re-adopted them from lineage `(2.0, 0.85)` after a same-node A/B headline tie (jobs 32610367 vs 32613911). VALIDATED upstream, not fork-new. Ablation direction: restore lineage `(2.0, 0.85)` at the 3 live sites (arm K).
- (b) Fourth site (`MakeMergeCorres`): NO DELTA — fork `:599` and upstream `:530` are both `if (cor_line.cor.size() > MINIMUM_NUMBER / 2)`, `MINIMUM_NUMBER=6` in both trees (`reconstruction.h:24`), i.e. `>3` in both. The `>3`-vs-`MINIMUM_NUMBER/2` distinction does not exist. Killed without a run.
- (c) Refinement weighting (`IcpIncGraphAxis` block only): FORK-NEW, unvalidated, bulk commit `869e696` — weights `1.0/3.0/1.0→2.0/5.0/3.0`, `w_a 0.1→1.0`, Cauchy `5.0/2.0/2.0/2.0→1.0/0.5/1.0/1.0` (dist/norm later made env-tunable by `a6bbb99` keeping fork defaults). All OTHER refinement sites already match upstream or are validated lanes: Icp-site + Registration5-site weights = upstream (E3 reverted, ticket-07 jobs), their Cauchy = `4.0/1.8×3` (cauchy-scales ticket 07, validated), iters/tolerance/trust-region/threads = validated, isConverge = ablated (ticket-30 J). Ablation: restore upstream weighting at the IcpIncGraphAxis site only (arm L).

**1. K — RejectOutlier lineage `(2.0, 0.85)` on abl2/D-base (job 33165329, COMPLETED 0:0). VALID (63 ORIG / 103 fresh pruned, LINK-SHIM-OK + DRIVER-SHIM-OK both arms, 8 T-files each, `[GATE] reject_dist=2.0 reject_norm=0.85` live).** Binary 8/8+14/15 BOTH arms (first fresh 14/15). Strict: ORIG **11/15** (D 10/15; only change: 2-8 10.92→9.32 flips to PASS), fresh **9/15** (same failing set as D-fresh: 1-5, 2-5, 2-8, 3-5, 3-6, 4-8 at 10–28mm). Tighter rejection seats the ring slightly better but the floor stands. Render `artifacts/pota31/pota31_seating_K.png` eye-checked: both rings closed, all 8 loops seated.
- K-orig strict 11/15: 1-2 1.56/8.35 PASS; 1-3 2.13/7.06 PASS; 1-4 0.93/6.74 PASS; 1-5 2.79/19.16 fail; 1-6 1.69/9.93 PASS; 1-7 1.27/6.39 PASS; 2-4 1.92/5.06 PASS; 2-5 3.35/23.80 fail; 2-8 2.22/9.32 PASS; 3-5 0.72/5.63 PASS; 3-6 2.86/11.92 fail; 4-6 1.97/11.45 fail; 4-7 1.73/8.76 PASS; 4-8 1.39/8.09 PASS; 6-7 0.71/5.13 PASS.
- K-fresh strict 9/15: 1-2 0.96/2.32 PASS; 1-3 2.00/7.08 PASS; 1-4 0.85/6.63 PASS; 1-5 3.21/22.60 fail; 1-6 1.05/6.47 PASS; 1-7 0.71/2.20 PASS; 2-4 1.41/3.91 PASS; 2-5 3.84/27.49 fail; 2-8 2.69/12.33 fail; 3-5 1.32/10.30 fail; 3-6 2.29/10.61 fail; 4-6 1.51/8.12 PASS; 4-7 0.69/2.86 PASS; 4-8 2.43/12.63 fail; 6-7 1.23/8.37 PASS.

**2. L — upstream IcpIncGraphAxis weighting on abl2/D-base (job 33165822, COMPLETED 0:0). Valid execution, decisive NEGATIVE (`[GATE] axis_weight=0.1 cauchy_dist=5.0 cauchy_norm=2.0` live; asserts + pruned 63/103 + 8 T-files all OK).** Binary 7/8+11/15 ORIG, 7/8+10/15 fresh — upstream weighting LOSES a sherd on ORIG. Strict: ORIG **6/15** (D 10/15; new fails 1-2 12.46, 1-3 11.66 join the floor set), fresh **11/15** (best fresh strict yet, but paired with an ORIG outside the 9–10/15 band — not landable). The fork's heavier weighting is load-bearing for seating; upstream values are not the cure. Render `artifacts/pota31/pota31_seating_L.png` eye-checked: L-orig shows a visibly dropped loop (7/8), L-fresh seats.
- L-orig strict 6/15: 1-2 2.00/12.46 fail; 1-3 2.54/11.66 fail; 1-4 1.23/9.32 PASS; 1-5 3.01/20.31 fail; 1-6 1.68/10.49 fail; 1-7 1.15/3.67 PASS; 2-4 2.19/9.30 PASS; 2-5 3.77/26.63 fail; 2-8 2.40/10.67 fail; 3-5 0.94/7.00 PASS; 3-6 2.61/10.64 fail; 4-6 1.96/10.01 fail; 4-7 1.53/7.45 PASS; 4-8 2.04/10.56 fail; 6-7 1.17/7.79 PASS.
- L-fresh strict 11/15: 1-2 1.12/7.66 PASS; 1-3 1.96/7.17 PASS; 1-4 0.79/6.42 PASS; 1-5 3.53/24.36 fail; 1-6 1.09/6.89 PASS; 1-7 0.79/0.90 PASS; 2-4 1.26/6.86 PASS; 2-5 3.91/28.14 fail; 2-8 1.84/8.06 PASS; 3-5 1.65/12.12 fail; 3-6 1.79/7.48 PASS; 4-6 1.10/5.69 PASS; 4-7 0.74/2.94 PASS; 4-8 1.88/10.76 fail; 6-7 1.11/7.76 PASS.

**3. Tally (binary ORIG / strict ORIG / binary fresh / strict fresh; D = ticket-30 reference):** D 8/8+13/15 / 10 / 7/8+10/15 / 9 · K 8/8+14/15 / 11 / 8/8+14/15 / 9 · L 7/8+11/15 / 6 / 7/8+10/15 / 11. Failing edges every arm: translations on 1-5, 2-5 (20–29mm) ± 2-8/3-5/3-6/4-6/4-8 (10–13mm); rotations pass everywhere (worst 4.11° across all arms).

**4. Jobs (sacct):** 33165329 (K) + 33165822 (L), both COMPLETED 0:0. Poll was `sacct` directly throughout. Every arm LINK-SHIM-OK + DRIVER-SHIM-OK, 8 T-files each.

**5. Evidence (laptop `artifacts/pota31/`):** `k_fetch.tgz` / `l_fetch.tgz` + unpacked `pota29_fetch/` (T_K_*, T_L_*, P30_*.txt, GT, rims_fresh); `p31_render.py` / `p31_render_L.py`; `pota31_seating_K.png`, `pota31_seating_L.png`. Spartan: `/data/gpfs/projects/punim2657/pota30/` (`src_K`, `src_L`, `run_pota30_k.sbatch`, `run_pota30_l.sbatch`), `sfs_main/pota30_run_33165*` RUNDIRs. Note: K sbatch shipped with a stale fetch loop (`for TAG in J`, carried from the J template) — caught on download, repacked from RUNDIR snapshots, fetch verified (8 T-files/arm); fixed in the L script before submit. Both repos uncommitted-wise untouched (only this ticket file edited on the laptop; Spartan additions are untracked scratch).

**Proposal for lead:** (a)+(c) are spent — K's +1 edge is noise-band-adjacent, L is decisively negative. Remaining floor suspects outside tickets 29–31: the fork-tightened Cauchy at the Icp/Registration5 sites (4.0/1.8 vs upstream 5.0/2.0, ticket-07 lane — validated on old binary, never re-ablated post-gate-fix), `max_iteration` 150/200 vs upstream 50/100, or the `isSimilarTrans` chunk-merge threshold (C1 exonerated as sole cause, not as contributor). Nothing to land.
