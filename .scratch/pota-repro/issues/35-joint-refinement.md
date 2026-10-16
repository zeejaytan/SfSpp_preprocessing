# 35: Last single + joint refinement — interaction gets its fair trial

**What to move:** strict from 10–11/15 (ORIG) / 9–11/15 (fresh) toward 15/15.

**Answers:** E1

**Blocked by:** 34-c1-retest (position below).

**Status:** ready-for-agent

**Starting position (tickets 29–34):** every fork-delta single is spent except one: the CheckGraph-plausibility site, currently at the validated relaxation 150, whose TRUE upstream is 50 (ticket-34 correction — fork-root blame-verified; do NOT test →100, that was never upstream anywhere). Handle #1 is that single: 150→50.

Handle #2 is the first principled combination, justified by single-exhaustion rather than guessed at: the JOINT-REFINEMENT arm — Cauchy (Icp/Reg5/Reg6) + max_iteration + tolerance + isConverge ALL at upstream SIMULTANEOUSLY, on the abl2 base, with the fork IcpIncGraphAxis weighting KEPT (ticket-31 L proved the fork weighting load-bearing on ORIG; an arm without it is predictably ORIG-negative). Each single was neutral alone; this tests interaction within the refinement stage. If it moves strict, the successor bisects within; if not, refinement is closed as a stage and the search moves to admission×refinement interaction or the cure-tree diff.

Explicitly OUT (lead decision, recorded so no future ticket re-proposes): C1×weighting cells — P covered fork-weighting+C1-upstream (neutral), L covered upstream-weighting+C1-fork (ORIG-negative), and both-upstream is predictably ORIG-negative by L. C6 stays (validated fix); C7 stays (inert); C9-site2 stays fork (F proved upstream worse).

**Valid-run rule:** asserts pass + snapshots non-empty + ORIG snapshots-strict in 9–11/15; pruned counts recorded, non-gating; fresh strict is the score; stop at the first strict 15/15 with valid ORIG.

**Rules:** shim-driven k=5/b=3; base = abl2 + nothing else; ONE variable-set per run (the joint arm is one arm, not stepwise); no commits; reuse tickets 29–34 bundle, scripts, fetch discipline.

- [ ] CheckGraph site 150→50 (one run): strict table + seating render
- [ ] Joint-refinement arm (one run, only if the single moves nothing): strict table + seating render
- [ ] Laptop poll per sbatch via sacct directly; job IDs + sacct states; Comments-only ticket edits

**Successor:** bisect the joint arm if it moves; else re-derive from the cure tree (upstream + P22FIX + P22FIX2 = 15/15) by forward-porting remaining fork deltas one commit-cluster at a time; then land the full set; then B–J E2E on admitted fragments.
