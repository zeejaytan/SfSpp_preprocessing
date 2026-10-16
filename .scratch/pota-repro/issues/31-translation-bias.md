# 31: Translation bias — RejectOutlier, fourth site, refinement weighting

**What to move:** strict from 10/15 (ORIG) / 9/15 (fresh) toward 15/15.

**Answers:** E1

**Blocked by:** 30-translation-floor (position below).

**Status:** ready-for-agent

**Starting position (ticket 30, jobs 33156112–33164457):** the ~7–9mm floor is not correspondence thinning (C9 sites 1+3 inert, site 2 weakly wrong-way), not a dead floor (C8), not solver tolerance or the converge gate (C10 moves the minimum, not the floor). Every surviving failing edge involves pieces 5/6/8 (±2) at 10–29mm with rotations ≤4.1° — a systematic translation bias in the pairwise/refinement stage. Candidate handles, one at a time: (a) the `RejectOutlier(20, 0.7)` tightening (adopted in Row-3, never ablated against the floor) — first establish whether its values are upstream or fork-new (provenance before ablation); (b) `MINIMUM_NUMBER/2` vs `>3` at the fourth correspondence site; (c) refinement weighting. Stop at the first arm that reaches strict 15/15 with a valid ORIG.

**New valid-run rule (lead decision, ticket 30 proof):** the binary log-tally is RETIRED — bit-identical snapshots scored 8/8+13/15 in one run and 7/8+7/15 in another, so it tracks beam-selection luck, not geometry. A run is valid when (1) pruned counts match the reference exactly (63 ORIG / 103 fresh; I-arm's 104 flagged, not voided), and (2) ORIG laptop-strict lands in the 9–10/15 noise band. Fresh strict is the score to move. Past E/G/H arms count as valid negatives under this rule.

**Rules:** shim-driven k=5/b=3 with LINK-SHIM-OK + DRIVER-SHIM-OK asserts; non-empty snapshots; provenance (upstream value + introducing commit) BEFORE ablating each handle; no commits; reuse ticket 29/30 bundle, scripts, and fetch discipline.

- [ ] Provenance per handle (upstream value? which commit changed it? validated or drift?)
- [ ] One ablation per run in the order (a)→(b)→(c); strict table + seating render per moving arm
- [ ] Laptop poll per sbatch via sacct directly; job IDs + sacct states; Comments-only ticket edits

**Successor:** land the full set on the reproduced strict run; then B–J E2E on admitted fragments.
