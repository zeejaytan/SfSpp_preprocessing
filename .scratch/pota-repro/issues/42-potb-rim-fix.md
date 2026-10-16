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

## Comments worker (2026-10-17, pota42 worktree, COMMIT NOTHING)

RIM DELIVERABLE: DONE. B gate 15/15 on real pipe output (exp3 33217089,
COMPLETED 0:0 7m32s), 2-4 = 7 strict pairs. E2E: NOT AT BAR — B_fresh 4/9 +
2/15 ×2 (33217561 24m09s, 33217562 13m09s, both COMPLETED 0:0), B_orig
9/9+15/15 ×2 (valid controls), A_orig/A_fresh 8/8+15/15 in same runs
(no-regression intact).

What the fix was (SFS-T42, prep-side only, asm vehicle untouched):
- Pipe stages shipped Pot_B axes pre-edge -> SFS-T04 interior-first vote
  fires (p1/p2 KEPT, p3-p9 EXCHANGED, zero tables): side convention pinned,
  labels restored (all Bl_0 -> ORIG-Bl_0 0.52-0.75mm), teleports gone.
- Edge skips T14 appends for Pot_B_* except p2 (appends were the teleport
  source: every jump sat at a wall->append junction).
- p2-Bl_0 := decorative-walk runs (spike dropped) resampled to 1.9mm wall
  spacing (T42c): raw 1.1mm steps fall in the LCS quantization deadband
  (+-0.15), longest Cond1-3 run 2 raw vs 9/11 resampled; mesh: fixed 3mm
  boundary radius for p2's patch only (adaptive estimator returned ~158mm).
- Root causes found: boundary_radius estimator (spacing*6 capped [1,50])
  pins 50mm on patches; rim-flagged LCS window is inert (header always 0).

Why E2E stops at 4/9+2/15 (evidence, assembler-authoritative where stated):
- p2 candidates 0 -> 93 (Node Sequence last; others 323-795; ORIG p2: 731).
- GT-seated p2x4 overlap area 6 (~ORIG 2): geometry FITS; seeds present.
- Beam (width 5, inlier-sum) never seats p2: only edges 1-3, 1-4 correct.
- Run-length gap is structural: ORIG p2 profiles run 18-34, resampled
  walk 9-15 (80%/row feature agreement, but ~1-in-5 rows out-of-bin breaks
  every run); smoothing tested, no gain; ORIG equally promiscuous (seeds
  everything) yet assembles — so pruning/search CAN handle ambiguity with
  smooth rims, but a 149-pt partial arc with short runs starves (93 vs 256+).
- Outcome identical across three different p2 rims (wall-97, raw runs,
  resampled) -> E2E insensitive to further rim-content polish.

PROPOSED NEXT (needs parent call): exp4 = wall-face lip-component
selection for p2-Surface_0 (honest wall-smooth geometry), OR assembler-lane
beam work (width/order/starvation). No further rim-side move changes this.
Worktree: /data/gpfs/projects/punim2657/pota42_repro/prep (e90d0ab + 3-file
SFS-T42 delta); scripts run_pota42_pipe_B.sbatch / run_pota42_stage_BA.sbatch.
