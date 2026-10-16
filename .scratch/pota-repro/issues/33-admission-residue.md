# 33: Admission residue — C3 coverage check, then C4 back to S100

**What to move:** strict from 10–11/15 (ORIG) / 9–11/15 (fresh) toward 15/15.

**Answers:** E1

**Blocked by:** 32-refinement-residue (position below).

**Status:** ready-for-agent

**Starting position (tickets 29–32):** refinement singles are spent (C8/C9/C10/Cauchy/iters/RejectOutlier/weighting) — the floor is not in refinement. The ablation base is fork @ 11f4827 + P22FIX + P22FIX2 + abl2. Two admission-stage deltas may still be live: C3 (RegistrationPruning `overlap || has_intersection` veto, fork root ab85ea3 + 869e696) — FIRST verify whether P22FIX (feature_matching.cpp:1989, drop `|| overlap_`) already covers this site; read both sites and prove same-or-second before burning any run. C4 (MergeOverlapTest S 100→50, 3ff4f8d) is covered by neither hunk — ablate it back to S100. The `isSimilarTrans` chunk-merge threshold (C1) stays HELD for a combination ticket — no runs on it here.

**Valid-run rule (tightened, ticket-32 M proof):** pruned counts are DEMOTED — 61/105 on D-identical geometry proves they are tally-side like the binary score. A run is valid when asserts pass (LINK-SHIM-OK + DRIVER-SHIM-OK), snapshots are non-empty, and ORIG snapshots-strict lands in the 9–11/15 band. Fresh snapshots-strict is the score to move. Stop at the first strict 15/15 with valid ORIG.

**Rules:** shim-driven k=5/b=3; base = abl2 + nothing else; no commits; reuse tickets 29–32 bundle, scripts, fetch discipline.

- [ ] C3 coverage: P22FIX site vs C3 veto site(s) — same (C3 spent, no run) or second live site (ablate it, one run)
- [ ] C4 back to S100 (one run, only if C3 moves nothing or is spent): strict table + seating render
- [ ] Laptop poll per sbatch via sacct directly; job IDs + sacct states; Comments-only ticket edits

**Successor:** if both move nothing, a combination ticket (C1 + weighting variants); then land the full set on the reproduced strict run; then B–J E2E on admitted fragments.
