# 30: Translation floor — ablate C9, then C8/C10, one at a time

**What to move:** strict from 10/15 toward 15/15 on the repo-traceable shim binary.

**Answers:** E1

**Blocked by:** 29-assembly-provenance (position below).

**Status:** results-in — floor survives C8/C9/C10 (best strict 10/15 ORIG + 9/15 fresh, every arm); binary ORIG control proven invalid as a run gate

**Starting position (ticket 29, jobs 33152327/33153903):** restoring the pairwise axis gate to true-upstream 0.436 moves ORIG 0/8→8/8+14/15 binary, but laptop strict stalls at 10/15 (fresh 9/15) — rotations pass almost everywhere (worst 4.1°), failures are pure translation (10.4–26.7mm) over a systematic ~7–9mm floor. Provenance list lives in ticket 29 §2: C9 (registration-correspondence floor `>3→>8`, two sites, 869e696) thins true correspondences before ICP and is the prime suspect; C8 (CountInlier floor) and C10 (solver numerics) follow. Plus a noise caveat from 29 §3: identical code scored ORIG 0/8 vs 2/8 across runs while fresh reproduced exactly — size the ORIG noise band with a same-binary repeat before judging 14/15-vs-15/15.

**Rules:** shim-driven k=5/b=3 with LINK-SHIM-OK + DRIVER-SHIM-OK asserts every run; non-empty transform snapshots; same-binary ORIG control (ORIG ≠ 8/8+15/15 voids that run); ONE ablation per run (C9 first — revert one or both sites? one variable: do one site, then the other only if the first moves nothing); no commits in either repo; reuse ticket 29's bundle, strict script (`artifacts/pota29/p29_strict.py`), and render script.

- [ ] Same-binary repeat of the abl2 C arms: ORIG noise band on binary + strict
- [ ] C9 ablation (site-by-site): ORIG control decides each; strict table + seating render per moving arm
- [ ] C8, then C10, only if C9 moves nothing — stop at the first arm that reaches strict 15/15 with ORIG 8/8+15/15 valid
- [ ] Laptop poll per sbatch via sacct directly; job IDs + sacct states; Comments-only ticket edits

**Successor:** land the full set on the reproduced strict run; then B–J E2E on admitted fragments.

## Comments (worker, 2026-10-16)

**Verdict: ordered list exhausted, no 15/15 anywhere. The ~7–9mm translation floor survives C9 (all three sites), C8, and C10 (tolerance + isConverge gate). Headline finding: the binary ORIG tally is decoupled from output geometry and cannot gate runs — bit-identical snapshots score 8/8+13/15 in one run and 7/8+7/15 in another. Stable validators are pruned counts (63 ORIG / 103–104 fresh, every run) + laptop strict tables (ORIG 9–10/15, fresh 9/15, same failing edges throughout). No commits anywhere.**

**0. Correction to ticket 29 §2: C9 has THREE `>8` sites, not two.** Fork `reconstruction.cpp` vs upstream `sfs_p22fix_src` (all four upstream sites `> MINIMUM_NUMBER/2`): site 1 line 534 `MakeSingleCorres`, site 2 line 673 `MakeMultiCorres`, site 3 line 746 `MakeCorWithSur` (the `> MINIMUM_NUMBER/2` at ~599 `MakeMergeCorres` is untouched). Ablated one site per run (E/F/G). C10 split in two: I = tolerance, J = isConverge site-4 gate.

**1. D — same-binary repeat of abl2 C (job 33156112, COMPLETED 0:0). ORIG noise band sized.** D-orig 8/8+13/15 binary (C was 8/8+14/15), strict **10/15** — edge-for-edge identical failing set to C (1-5, 2-5, 2-8, 3-6, 4-6; t = 10.4–26.7mm). D-fresh 7/8+10/15, strict **9/15** (= C-fresh). So on this binary: sherds 8/8 stable (2/2 runs), binary edges 13–14/15, strict 10/15 ORIG / 9/15 fresh. 15/15 is outside the noise band. Full D tables (reference for all arms below):
- D-orig strict 10/15: 1-2 1.41°/8.17 PASS; 1-3 2.28/8.91 PASS; 1-4 1.46/6.91 PASS; 1-5 3.06/20.68 fail; 1-6 1.93/9.87 PASS; 1-7 1.07/6.24 PASS; 2-4 2.35/4.31 PASS; 2-5 3.72/26.70 fail; 2-8 2.62/10.92 fail; 3-5 0.83/6.34 PASS; 3-6 3.04/10.37 fail; 4-6 2.06/11.06 fail; 4-7 1.66/7.49 PASS; 4-8 1.43/8.19 PASS; 6-7 1.20/7.85 PASS.
- D-fresh strict 9/15: 1-2 1.12/2.35 PASS; 1-3 1.96/7.37 PASS; 1-4 0.92/7.13 PASS; 1-5 3.27/23.00 fail; 1-6 1.36/8.01 PASS; 1-7 0.67/1.31 PASS; 2-4 1.60/5.47 PASS; 2-5 4.11/29.10 fail; 2-8 2.76/13.79 fail; 3-5 1.39/10.82 fail; 3-6 1.90/11.82 fail; 4-6 1.32/9.29 PASS; 4-7 0.85/4.05 PASS; 4-8 3.72/18.00 fail; 6-7 0.97/5.50 PASS.

**2. E — C9 site 1 revert (job 33156112). VOID by binary (0/8+0/15) but geometry = D.** Snapshots match D-orig to 0.001mm (one global X shift; `check_shift2.py`), strict **10/15** with edge values identical to D-orig to 0.01. Render `pota30_seating_Evoid.png`: E-orig ring seats exactly like D-orig — the 0/8 is scored, not geometric. Site 1 never binds on Pot A (no pair in the 4–8 window). Moves strict nowhere.

**3. F — C9 site 2 revert (job 33158166, COMPLETED 0:0). VOID by binary (7/8+9/15); only site that binds, weakly.** Snapshots shift ≤1.1mm vs D; strict **9/15** (D 10/15; only change: 1-6 9.87→10.11 flips over the line). F-fresh 7/8+11/15 binary, strict **9/15** (same failing set as D-fresh; 4-8 18.00→12.19 the only notable move). Render `pota30_seating_F.png` eye-checked: closed ring, no dropped piece visible. Site 2 binds somewhere but moves strict the wrong way (-1).

**4. G — C9 site 3 revert (job 33159434, COMPLETED 0:0). VOID by binary (7/8+9/15); geometry = D.** Snapshots match D-orig to 0.008mm; strict **10/15** edge-identical to D-orig; G-fresh strict **9/15** edge-identical to D-fresh. Site 3 never binds. C9 conclusion: sites 1+3 inert on Pot A, site 2 weakly active; none moves strict toward 15/15.

**5. H — C8 floor removal (job 33160726, COMPLETED 0:0). Dead code confirmed empirically.** Static: `inlier<MIN→0` lives in `CountInlier` overload-1, which has zero callers in `class/` + `hpc/` (live path calls overload-3 at `reconstruction.cpp:804/843`, no floor). Empirical: H-orig snapshots are **bit-identical** to D-orig (max diff 0.0 all pieces) yet binary tally reads **7/8+7/15** vs D's 8/8+13/15 — the smoking gun that the log tally does not track saved geometry. Strict **10/15** (= D); H-fresh strict **9/15** (= D-fresh). C8 moves nothing, as predicted.

**6. I — C10 tolerance 1e-6→CERES_FUNC_TOL=1e-3, 5 Solve sites (job 33163233, COMPLETED 0:0). Real solution change, same strict counts.** I-orig binary 7/8+9/15 (void), strict **10/15** with membership churn (2-8 flips to PASS 9.98, 1-6 flips to fail 11.03); snapshots a genuinely different local minimum (|T| diffs to 465mm vs D — different global frame, not comparable piece-wise). I-fresh binary 7/8+10/15 (pruned **104** vs 103 everywhere else — one extra pair admitted), strict **9/15**. Looser tolerance moves the minimum, not the floor: failing edges still 1-5/2-5/3-6/4-6 at 20–28mm.

**7. J — C10 isConverge site-4 gate 0.02/0.2→upstream 0.05/1.0 (job 33164457, COMPLETED 0:0). Seats 8/8 both arms; strict still 9/15.** J-orig 8/8+13/15 binary, strict **9/15** (1-6 10.04 borderline fail; snapshots = D-orig + sub-mm jitter ≤1.0mm). J-fresh **8/8+10/15 binary** (first fresh 8/8 since the cure) but strict **9/15** — piece 8 seats per the loose binary bar while its joins 2-8/4-8 still fail strict at 11–12mm. Render `pota30_seating_J.png` eye-checked (J-fresh = different global frame + reseated p8 vs D-fresh). The gate revert seats the 8th piece without touching the floor.

**8. Tally table (binary ORIG / strict ORIG / binary fresh / strict fresh; * = void by 8/8+15/15 letter):** D 8/8+13/15 / 10 / 7/8+10/15 / 9 · E 0/8+0/15* / 10 / 7/8+11/15 / 9 · F 7/8+9/15* / 9 / 7/8+11/15 / 9 · G 7/8+9/15* / 10 / 7/8+10/15 / 9 · H 7/8+7/15* / 10 / 7/8+10/15 / 9 · I 7/8+9/15* / 10 / 7/8+10/15 / 9 · J 8/8+13/15 / 9 / 8/8+10/15 / 9. Failing strict edges every arm: translations on 1-5, 2-5 (±2-8, 3-6, 4-6, 1-6 borderline); rotations pass everywhere (worst 4.11°).

**9. Jobs (sacct):** 33155661 FAILED 1:0 + 33155823 COMPLETED 0:0 (stillborn — sbatch RUNDIR/guard bugs, no arms built, superseded same day); 33156112 / 33158166 / 33159434 / 33160726 / 33163233 / 33164457 all COMPLETED 0:0 (D+E / F / G / H / I / J). Poll was `sacct` directly throughout. Every arm LINK-SHIM-OK + DRIVER-SHIM-OK, 8 T-files each.

**10. Evidence (laptop `artifacts/pota30/`):** `pota30_de/fetch+f_fetch/g_fetch/h_fetch/i_fetch/j_fetch` fetch dirs + `.tgz`; `p30_strict.py` (multi-arm scorer), `check_shift.py`/`check_shift2.py` (global-frame tests); renders `pota30_seating_D.png` (D-orig+D-fresh seat), `pota30_seating_Evoid.png` (0/8 binary, seated ring), `pota30_seating_F.png`, `pota30_seating_J.png` (8th fresh piece seats). Spartan: `/data/gpfs/projects/punim2657/pota30/` (`src_E/F/G/H/I/J`, six sbatches), `sfs_main/pota30_run_33*` RUNDIRs. Both repos uncommitted-wise untouched (git status clean); `pota29/abl2` reused unmodified for D.

**Proposal for lead:** (a) retire the binary ORIG tally as a run gate — it scores a different candidate than the snapshots (E/G/H proof); gate on pruned counts + strict instead. (b) The floor is not C8/C9/C10: every surviving failing edge involves pieces 5/6/8 (±2) at 10–29mm with rotations ≤4.1° — i.e. a systematic translation bias in pairwise/refinement, not correspondence thinning or solver tolerance. Next hypotheses outside this ticket: the `RejectOutlier(20, 0.7)` tightening (Row-3 adopted, never ablated against the floor), `MINIMUM_NUMBER/2` vs `>3` at the *fourth* site, or the refinement weighting — all need new tickets. Nothing to land.
