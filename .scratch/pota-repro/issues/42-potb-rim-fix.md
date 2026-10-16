# 42: Pot B rim-content fix — ordering, p1, 2-4 seam, side convention

**What to deliver:** B rims that gate clean + B fresh E2E at the paper bar.

**Answers:** E1

**Blocked by:** 41-potb-diagnosis (kill site: fresh Bl_0 content/order).

**Status:** ready-for-agent

**Starting position:** fresh B Bl_0 has ordering teleports in 8/9 pieces (p1 garbage, ~12mm off), 8/15 GT-true edges exceed SingleOverlapTest@100 (1.7–49×) vs 0/15 shipped; 2-4 has zero rim support; fresh Bl_0 ≈ shipped Bl_1 side on all 9 pieces. ORIG 9/9+15/15 ×4 runs (method exonerated). Search gates explicitly NOT to be relaxed. Ticket-27's skip-cure fixed A's ordering but does not generalize to B — find why the walk fails here (different failure mode, not the T14 append).

**Work in scratch copies first; land pipeline edits only when B gates clean AND A has no regression (A gate 15/15 + cure-potA numbers intact).**
- [ ] B Bl_0 ordering: kill teleports (all 9 pieces, zero jumps like ORIG)
- [ ] p1 content: rim must match a shipped side within tolerance (not ~12mm off)
- [ ] 2-4 seam support restored
- [ ] Pin Bl_0 side convention (deterministic; no Bl_0≈Bl_1 flips)
- [ ] B gate 15/15 + B fresh E2E 9/9+15/15 with valid ORIG control (repeats ×2)
- [ ] A no-regression proof in the same runs
- [ ] Job IDs + sacct states; Comments-only ticket edits

**Successor:** roll the generalized rim fix across C–J per 39's tables.
