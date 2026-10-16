# 32: Refinement residue — Cauchy scales, then max_iteration, back to upstream

**What to move:** strict from 10–11/15 (ORIG) / 9–11/15 (fresh) toward 15/15.

**Answers:** E1

**Blocked by:** 31-translation-bias (position below).

**Status:** ready-for-agent

**Starting position (ticket 31, jobs 33165329/33165822):** RejectOutlier is upstream (K: +1 edge, noise-adjacent, floor stands); the fourth site has no delta; the IcpIncGraphAxis weighting is fork-new and load-bearing (L: restoring upstream craters ORIG to 6/15 yet lifts fresh to 11/15 — best fresh yet). So the floor lives in the refinement stage, and neither weighting is the answer. Remaining refinement deltas, one at a time: (a) Cauchy scales at the Icp/Registration5 sites, fork-tightened 4.0/1.8 vs upstream 5.0/2.0 (ticket-07 lane — validated on the old binary, never re-ablated post-gate-fix); (b) `max_iteration` 150/200 vs upstream 50/100. The `isSimilarTrans` chunk-merge threshold (C1, exonerated as sole cause) is HELD for a combination ticket — do not burn runs on it here.

**Valid-run rule (from ticket 30):** pruned counts exact (63 ORIG / 103 fresh) + ORIG laptop-strict in the 9–11/15 band. Fresh strict is the score to move. Stop at the first strict 15/15 with valid ORIG.

**Rules:** shim-driven k=5/b=3 with LINK-SHIM-OK + DRIVER-SHIM-OK asserts; non-empty snapshots; provenance (upstream value + introducing commit) confirmed per handle before ablating; base = abl2 (pairwise 0.436) + nothing else; no commits; reuse tickets 29–31 bundle, scripts, fetch discipline.

- [ ] Cauchy scales back to upstream 5.0/2.0 at the Icp/Registration5 sites: strict table + seating render
- [ ] max_iteration back to upstream 50/100 — only if Cauchy moves nothing
- [ ] Laptop poll per sbatch via sacct directly; job IDs + sacct states; Comments-only ticket edits

**Successor:** land the full set on the reproduced strict run; then B–J E2E on admitted fragments.
