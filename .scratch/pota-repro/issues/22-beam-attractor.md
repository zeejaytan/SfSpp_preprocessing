# 22: Break the ~102° piece-2 false attractor

**What to build:** a search-side fix for the beam's preferred false seating of p2 — the last barrier to strict 8/8 + 15/15.

**Answers:** E1

**Blocked by:** 21-piece2-wall-recovery (controlled comparison below).

**Status:** ready-for-agent

**Starting position (ticket 21, job 33119652, ORIG control valid):** with stub, patched, AND full true-wall p2 rims, the beam seats p2 at the same ~102°/232mm false pose and drags pieces 1,6,7,8 with it as a rigid ~74° block (relative-vs-ORIG pieces 0/8, edges 2/15). Yet ticket 20's swap (ORIG p2 rim in the fresh bundle) seated p2 4/4 strict. Two confounds to control before touching the search: (1) the beam is nondeterministic run-to-run (pruned 70/72/74/75, false pose 10° vs 103° on identical inputs); (2) the mesh stage is nondeterministic run-to-run (ticket 21 landmine), so bundle-to-bundle rim comparisons are noisy.

**Rules:** within-bundle swaps ONLY for every comparison (same bundle, only the p2 rim files exchanged — the ticket-20 protocol that controlled both confounds). No pipeline/finder source changes in this ticket; search-side changes only, minimal, with the ablated arm alongside. Same-binary ORIG control in the same job (must reproduce 8/8+15/15 or void). Acceptance is the STRICT bar only (5°/10mm relative-edge).

- [ ] First reproduce the attractor within one bundle: fresh bundle + its own p2 rim variants (stub vs full-wall) swapped file-wise; confirm the beam prefers ~102° for both while ORIG p2 rim in the SAME bundle seats
- [ ] Then diagnose: what does the beam score the true vs false p2 seating (which pairs, which costs)? Candidate directions only after measurement: pair-weight of p2's short edges, beam-width starvation at the p2 decision,0 or the rigid-block coupling 1-6-7-8
- [ ] Fixed arm: strict 15/15 fresh at k=5/b=3
- [ ] Laptop poll per sbatch (`sacct` directly); before/after seating render + measurement pair; no commits; Comments-only edits

**Successor:** B–J E2E on admitted fragments (same protocol per pot), then the Juglet question re-opens with a working chain.
