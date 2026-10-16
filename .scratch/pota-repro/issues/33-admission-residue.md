# 33: Admission residue — C3 coverage check, then C4 back to S100

**What to move:** strict from 10–11/15 (ORIG) / 9–11/15 (fresh) toward 15/15.

**Answers:** E1

**Blocked by:** 32-refinement-residue (position below).

**Status:** results-in — C3 spent (same site as P22FIX, no run burnt); C4 moves nothing (O strict 10/15 ORIG + 9/15 fresh, D-identical to 0.005mm); admission residue is neither veto

**Starting position (tickets 29–32):** refinement singles are spent (C8/C9/C10/Cauchy/iters/RejectOutlier/weighting) — the floor is not in refinement. The ablation base is fork @ 11f4827 + P22FIX + P22FIX2 + abl2. Two admission-stage deltas may still be live: C3 (RegistrationPruning `overlap || has_intersection` veto, fork root ab85ea3 + 869e696) — FIRST verify whether P22FIX (feature_matching.cpp:1989, drop `|| overlap_`) already covers this site; read both sites and prove same-or-second before burning any run. C4 (MergeOverlapTest S 100→50, 3ff4f8d) is covered by neither hunk — ablate it back to S100. The `isSimilarTrans` chunk-merge threshold (C1) stays HELD for a combination ticket — no runs on it here.

**Valid-run rule (tightened, ticket-32 M proof):** pruned counts are DEMOTED — 61/105 on D-identical geometry proves they are tally-side like the binary score. A run is valid when asserts pass (LINK-SHIM-OK + DRIVER-SHIM-OK), snapshots are non-empty, and ORIG snapshots-strict lands in the 9–11/15 band. Fresh snapshots-strict is the score to move. Stop at the first strict 15/15 with valid ORIG.

**Rules:** shim-driven k=5/b=3; base = abl2 + nothing else; no commits; reuse tickets 29–32 bundle, scripts, fetch discipline.

- [ ] C3 coverage: P22FIX site vs C3 veto site(s) — same (C3 spent, no run) or second live site (ablate it, one run)
- [ ] C4 back to S100 (one run, only if C3 moves nothing or is spent): strict table + seating render
- [ ] Laptop poll per sbatch via sacct directly; job IDs + sacct states; Comments-only ticket edits

**Successor:** if both move nothing, a combination ticket (C1 + weighting variants); then land the full set on the reproduced strict run; then B–J E2E on admitted fragments.

## Comments (worker, 2026-10-16)

**Verdict: ordered list exhausted, no 15/15 anywhere. C3 is spent without a run (same veto P22FIX already removed — proof §0); C4 (arm O, job 33169041, COMPLETED 0:0) is D-identical to 0.005mm with strict 10/15 ORIG + 9/15 fresh. The ~7–9mm translation floor survives both admission-stage deltas. No commits anywhere.**

**0. C3 same-or-second proof — SAME site, no run burnt (laptop `structure-from-sherds-pp @ 11f4827` + P22FIX, read-only `git blame` + greps).**
- P22FIX veto = `RegistrationPruning` removal loop `feature_matching.cpp:1989`: pre-fix `if ((iter->score_ > 10) || (iter->overlap_))`, post-fix `if ((iter->score_ > 10))` (base line blames to fork root `ab85ea3`; P22FIX hunk uncommitted; matches `artifacts/pota28/pota28_asm.patch` exactly).
- C3 per ticket 29 §2 = the `overlap || has_intersection` IntersectionDetector veto: the flag write is `:1957 `iter->overlap_ = overlap || has_intersection;`` (blame `869e696`; surrounding `OverlapCheck_3d` block lines 1948/1951/1958–60 blame to `ab85ea3` — exactly the "fork root ab85ea3 + 869e696" provenance).
- The `:1957` flag has exactly ONE reader in the function: the `:1989` veto P22FIX deleted. Repo-wide `.overlap_` readers: only `:1797` (`PairwisePruning`'s `else if (iter->overlap_)`, which reads the flag as set at `:1722` by pure `OverlapCheck_3d` with no intersection term — a different function, upstream behavior, not a fork delta and outside C3 scope). No other `RegistrationPruning` (`:1829–2005`) veto touches `overlap_`/`has_intersection` (full-function read). So `has_intersection` can only act through the flag whose sole RP consumer is gone: C3 ≡ P22FIX site, spent. C4 upstream check (provenance for the run): upstream `sfs_main/sfs_p22fix_src @ 9195c01 :1912` MergeOverlapTest passes bare `100`; fork `:2028` passes `50` (PAPER-CONFIG 3ff4f8d, "was 100").

**1. O — MergeOverlapTest S back to upstream 100 on abl2/D-base (job 33169041, COMPLETED 0:0, ~13 min). VALID run, strict-identical to D.** Pruned exact 63 ORIG / 103 fresh; LINK-SHIM-OK + DRIVER-SHIM-OK both arms, 8 T-files each. Binary 8/8+14/15 ORIG, 7/8+10/15 fresh. Strict: ORIG **10/15**, fresh **9/15**, every edge within 0.01 of D; snapshots D-identical (max abs diff 0.005mm ORIG, 0.001mm fresh). Render `artifacts/pota33/pota33_seating_O.png` eye-checked: both rings closed, all 8 loops seated.
- O-orig strict 10/15: 1-2 1.41/8.17 PASS; 1-3 2.27/8.91 PASS; 1-4 1.46/6.91 PASS; 1-5 3.06/20.68 fail; 1-6 1.93/9.87 PASS; 1-7 1.07/6.24 PASS; 2-4 2.35/4.31 PASS; 2-5 3.72/26.70 fail; 2-8 2.62/10.92 fail; 3-5 0.84/6.34 PASS; 3-6 3.04/10.37 fail; 4-6 2.06/11.06 fail; 4-7 1.66/7.49 PASS; 4-8 1.43/8.19 PASS; 6-7 1.19/7.85 PASS.
- O-fresh strict 9/15: 1-2 1.12/2.35 PASS; 1-3 1.96/7.37 PASS; 1-4 0.92/7.13 PASS; 1-5 3.28/23.00 fail; 1-6 1.36/8.01 PASS; 1-7 0.67/1.31 PASS; 2-4 1.60/5.47 PASS; 2-5 4.11/29.10 fail; 2-8 2.76/13.79 fail; 3-5 1.39/10.82 fail; 3-6 1.90/11.82 fail; 4-6 1.32/9.29 PASS; 4-7 0.85/4.05 PASS; 4-8 3.72/18.00 fail; 6-7 0.97/5.50 PASS.

**2. Tally (binary ORIG / strict ORIG / binary fresh / strict fresh; D = ticket-30 reference):** D 8/8+13/15 / 10 / 7/8+10/15 / 9 · O 8/8+14/15 / 10 / 7/8+10/15 / 9. Failing strict edges: translations on 1-5, 2-5 (20–29mm) ± 2-8/3-5/3-6/4-6/4-8 (10–18mm); rotations pass everywhere (worst 4.11°).

**3. Jobs (sacct):** 33169041 (O) COMPLETED 0:0. Poll was `sacct` directly throughout (never `slurm_poll.sh`). In-job guards passed (asm HEAD 11f4827, diff = 2 files, `was 100` S50 line gone, POTA33-O ×1, contamination-free, bundle md5 OK).

**4. Evidence (laptop `artifacts/pota33/`):** `o_fetch.tgz` + unpacked `pota29_fetch/` (T_O_*, P30_O_*.txt, GT, rims_fresh); `p33_render_O.py`; `pota33_seating_O.png`. Spartan: `/data/gpfs/projects/punim2657/pota30/` (`src_O`, `run_pota33_o.sbatch`), `sfs_main/pota33o_run_33169041` RUNDIR. No commits in either repo (laptop `structure-from-sherds-pp` still holds only the pre-existing P22FIX/P22FIX2 uncommitted hunks; `SfSpp_preprocessing` only this ticket file; Spartan additions are untracked scratch).

**Proposal for lead:** (a)+(b) are spent — C3 never existed as a second site, C4 reproduces D geometry to 0.005mm. Admission-stage singles are exhausted (C2 landed, C3 covered, C4 inert, C5 CheckGraph-S was never authorized here). Per the ticket successor: the floor now needs the combination ticket (C1 + weighting variants).
