# Instrumented C_176 run: per-pair survivors + GT-force score

GOAL: DECIDE WHETHER THE FIX IS SEARCH-SIDE OR SCORER-SIDE, BY MEASUREMENT.

**Answers:** E1

**Blocked by:** 177 (mechanism: C01 dies upstream of scoring; P1 confirmed 40/8 vs 45/8, survivors exact; P2/P3 need this run), 176 (439-dot TRUE walk + staged bundle).

**Status:** ready-for-agent

**What to deliver (laptop-side prep; worker has no SSH, lead relays the run):** (1) Patch logging into the relay vehicle (HEAD bffefb6 + staged 176 build): per-pair LCS survivors into/out of PairwisePruning + winner "Score :" per state (ranking_system.cpp:507 path), keyed by pair. (2) GT-force harness: seat the 439-dot C01-Bl_0 TRUE walk at author GT pose, recompute state_score_ through the same scorer. (3) Prediction ledger from 177: P2 = C01 pairs contribute 0 of 8 survivors; P3 = GT-forced C01 state_score_ EXCEEDS winner Score. Stage the patched build + run script in .scratch/pota178_repro/ for lead relay (same pattern as 176: p176_build.py + run sbatch).

**Bar:** staged instrumented bundle that reproduces the 176 C_176 tally unpatched (control), then the two measurements (P2 counts, P3 score comparison) with numbers. If P3 fails (GT-forced below winner), say so plainly -- the fix goes to scorer weights.

**Rules:** dataset read-only; production checkout foreign-WIP dirty, never touch -- relay worktree only, restore byte-identical; COMMIT NOTHING; tickets 39-177 read-only; edit this ticket's Comments section ONLY; same-binary ORIG control alongside.

- [ ] Logging patch + GT-force harness staged
- [ ] Control reproduces 176 tally
- [ ] P2/P3 measured with numbers
