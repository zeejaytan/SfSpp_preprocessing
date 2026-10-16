# 36: Cure-tree rebuild — reproduce the 15/15 or overturn it

**What to decide:** whether the ticket-27 strict 15/15 reproduces on its own tree.

**Answers:** E1

**Blocked by:** 35-joint-refinement (position below).

**Status:** ready-for-agent

**Starting position (tickets 29–35):** every fork-delta single is spent and joint-refinement moves nothing-or-wrong. The chase now turns around: instead of subtracting fork deltas from the fork tree, rebuild the tree that scored strict 15/15 in ticket 27 (upstream @ 9195c01 + staged files, job record in ticket 27's Comments) and test whether IT reproduces on the same bundle with today's snapshots-strict ruler.

**Steps:**
1. RECOVER THE RECIPE FIRST (no building yet): read ticket 27's Comments and write down the exact cure-tree recipe — base commit, every staged file/hunk (assembly-side AND bundle-side), beam settings, scoring method. If the recipe is not fully recoverable from the record, STOP and report that as the result (do not guess a tree).
2. Diff the reconstructed cure tree against the current ablation base (fork @ 11f4827 + P22FIX + P22FIX2 + abl2) — the complete remaining delta list, each with introducing commit.
3. Rebuild the cure tree, run BOTH arms (ORIG + fresh) on the same md5-verified p28 wall-only bundle, shim k=5/b=3 with LINK-SHIM-OK + DRIVER-SHIM-OK asserts, non-empty snapshots, snapshots-strict scoring.
4. Verdict: reproduces strict 15/15 on fresh with valid ORIG → the floor is real and lives in the step-2 delta list (successor: bisect forward, porting fork deltas cluster-by-cluster onto the cure tree). Does NOT reproduce (lands ~10/15 like D) → the 27 result was beam luck or era-scored; do NOT ablate further — report non-reproduction with both arms' strict tables and stop for lead bar review.

**Valid-run rule:** asserts pass + snapshots non-empty; ORIG recorded (its strict decides reproduce/not alongside fresh — both tables required either way). Pruned counts and binary tallies recorded, non-gating.

**Rules:** no commits in either repo; reuse tickets 27–35 bundle, scripts, fetch discipline; laptop poll per sbatch via sacct directly; job IDs + sacct states; Comments-only ticket edits; seating render of both arms.

**Successor:** reproduce → ticket 37 (forward bisect from the cure tree); not reproduced → lead bar review (no new ablation without a lead decision).
