# 333: The axis criterion must span the wall — make the delivered line match the key on 2, 3 and 7, and keep the pots byte-identical

**What to build:** a **fix** in the axis finder's ranking that makes the delivered rank-0 line match
`Dataset/Juglet_GT/Juglet_Piece_N_Axis.xyz` within 10 deg on **all nine** Juglet pieces, with the ten pots
byte-identical to `axes323` and **no Juglet-specific constant**. Ticket 332 named the mechanism and is closed;
this ticket replaces the criterion it blamed and proves the replacement on the same tables. No assembly run:
the axis keeps its own gate, and a seating re-run is a later ticket once the axis is honest.

**Answers:** E1
**Blocked by:** None. Ticket 332 (closed) supplies the diagnosis; ticket 325 (status `results-in`, branch
`325-scale-free-axis-finder`, **not merged**) changes `normalized.py`'s clearance gates — **do not merge it and
do not build on it**; this ticket works from `main` at the commit that carries 332, and its own non-regression
gate is the 172-pot `cmp` against `axes323`.
**Status:** ready-for-agent
**Worker:** unassigned
**Budget:** medium 5
**Hand-over:** DeepSeek — dsh one-shot subagent w333, dispatched 2026-11-17 by the lead. Check path: the lead
re-reads `artifacts/t333/gate333.tsv` (nine rows, deg per piece), re-runs the 172-file `cmp` itself against
`axes323`, re-reads the density-sweep rows, and **looks at** `artifacts/t333/render333_axis.png` before the
Reading is recorded. The hidden acceptance is the 172/172 identity plus rank-0 within 10 deg on 9 of 9 — both
are mechanical and are re-run by the lead, not accepted from the report.

## Given (verified by the lead, 2026-11-17 — do not re-derive as if new)

Ticket 332 measured the failure and named its cause. These are its own numbers, re-checked by the lead:

- **The delivered line, from `runs/20261110-0740_d628fc0_t323-axes/out/axes323`, first line of each
  `Juglet_Piece_N_Axis.xyz`, undirected angle against the key:** p1 0.92, **p2 13.16**, **p3 28.39**,
  p4 3.44, p5 3.72, p6 1.84, **p7 47.92**, p8 3.05, p9 4.56 deg. **6 of 9 within 10 deg.**
- **The pool is not the ceiling.** A basin representative within 10 deg of the key exists on **9 of 9** pieces
  in all three settings (1x geometry 0.79-8.68 deg; corpus; 3x). After `refine_axis_normalized` only
  **5 of 9** (1x geometry), 1 of 9 (corpus), 1 of 9 (3x) survive.
- **The good line is thrown away before refinement.** `rank_by_profile` (`sfs_axes/select.py:55-76`) refines
  only the **8 cheapest distinct** (`PROFILE_REFINE_K = 8`, `select.py:36`); the good line sits at pre-refine
  cost rank **64 / 79 / 100 of 120** on p2, p7/corpus, p9/3x.
- **The window is narrower than the wall it measures.** `wall_thickness` (`sfs_axes/profile.py:38-51`) takes the
  smallest principal std of the **k = 24** nearest neighbours (`PROFILE_K = 24`, `profile.py:28`) in the (r, z)
  plane of a **2500-point stride** (`PROFILE_POINTS = 2500`, `profile.py:30`; `stride` at `:33`). Measured
  (`probe_cost.json`): p1 wall **2.007 mm**, p2 wall **2.328 mm**; the k=24 neighbourhood radius is
  **0.116 mm** and **0.175 mm** — a tenth of the wall. Cost at the key then grows with k like a sampled arc
  (p1: **0.0644** at k=12 -> **0.3041** at k=384) instead of flattening at the wall.
- **So the score cannot separate the answers.** On p2 our 13-deg-wrong line costs **0.00595** against the
  key's **0.04594** — the criterion prefers it by 7.7x. Where a good line does get refined it loses by
  3.8-6.7 %; the key refined by the same optimiser sits 6.1-13.1 deg from where it started while costing the
  same to 0.1-2 %, so the optimiser's own direction is wrong too.
- **Units are not the cause.** The finder on the 3x cloud with constants untouched gives 7 of 9 rank-0
  (p3 10.11, p9 29.81 deg); the old ranker at 3x gives 0 of 9.
- **The pots do not move today**: 172 of 172 files byte-identical to `axes323`.

Read the ticket-332 Comments for the per-piece tables; they are the baseline this ticket must beat.

## What the fix must achieve

The criterion has to measure **the same object at every scale and every sampling density**: a wall is a curve
in the (r, z) plane, and its thickness is the distance across that curve, which is a property of the wall — not
of the k-th neighbour. Today's statistic is a sampling artefact: its value is set by the stride (2500 points)
and by k=24, so it changes when the cloud is resampled and cannot see a 2 mm wall on a 33 mm vessel.

The ticket does **not** prescribe the formula. It prescribes the **properties** the replacement must have, and
three candidate designs to try in this order (any one that passes is the answer; a fourth design is allowed if
it passes the same bars and its reasoning is written down):

1. **Neighbourhood at the wall's own scale.** Derive the window from the data instead of from k: estimate the
   local inter-wall spacing first (e.g. the smallest gap between the two walls' (r, z) curves, or the point
   spacing times a factor), then take the neighbourhood radius as a multiple of that estimate and iterate once.
   A fixed k must not survive: the same k means different physical windows on different densities.
2. **A cost that spans both walls.** Score the *pair* of curves: for each wall point, the distance to the other
   wall's (r, z) curve at matched z (a two-curve distance), not the thinness of one cloud. This is what the
   module docstring already claims ("every point of a wall maps onto one curve") and what makes the statistic
   a property of the vessel's profile.
3. **Multi-scale and normalised.** Compute the width at several k (e.g. 12, 48, 192, 768, 3072) and use a
   statistic that is flat at the true axis and growing at a wrong one — e.g. the ratio width(k)/r_k(k), or the
   knee of width against neighbourhood radius. Report the curve for each of the nine pieces so the property is
   visible, not asserted.

Whatever is chosen, **the refinement must be judged on the same bars** — `refine_axis_profile`
(`profile.py:59-82`) currently drifts the key by 6.1-13.1 deg; a cost whose own minimum is 13 deg from the key
(p2) will keep losing however the cut is set.

## Stages

**A — Reproduce (must pass before any code change).** From `main`, rebuild the nine 1x Juglet axes with the
shipped path on a compute node (reuse `runs/20261110-0320_41494d0_t320b-juglet`'s driver), score rank-0
against `Dataset/Juglet_GT`, and reproduce **6 of 9** (p2 13.16, p3 28.39, p7 47.92) and the 172-pot `cmp`
172/172 against `axes323`. If the baseline does not reproduce byte-for-byte on the pots, stop:
`blocked: baseline does not reproduce`.

**B — Make the statistic scale-free (the fix).** Implement the chosen design in `sfs_axes/profile.py` (and
`select.py` only where the cut must change), behind **one** default-on env switch `SFS_AXES_WIDTH_SCALE=1`
(name it as you build it; off must reproduce `axes323` byte-for-byte). No literal in mm, no per-pot number, no
size branch, and `grep -rn "Juglet" sfs_axes/` must return **nothing** when you are done.

**C — Bars (all are pass/fail, all are reported per piece).**

1. **Delivered rank-0 within 10 deg of the key on 9 of 9**, on the 1x corpus lane the assembler would consume
   (today 6 of 9).
2. **3x lane: 9 of 9 within 10 deg** from the same code, constants untouched (today 7 of 9; p3 10.11, p9 29.81).
3. **The pots do not move:** 172 of 172 files byte-identical to `axes323` (`cmp`), and the ten pots' own
   direction table unchanged to 0.00 deg.
4. **The criterion separates, measurably:** for each piece report cost(key), cost(delivered) and cost of the
   best wrong line more than 20 deg from the key; require **cost(key) < cost(delivered after refinement)** for
   the pieces that now pass, and **no piece where a line more than 20 deg off scores better than a line within
   5 deg** (today p2 fails this outright).
5. **The key does not drift:** refining the key with the same optimiser must stay within **5 deg** of itself on
   9 of 9 (today 6.1-13.1 deg).
6. **The answer does not depend on the sampling density:** run the nine at `PROFILE_POINTS` 1200 and 5000 and
   report the delivered deg per piece; both must stay within 10 deg on 9 of 9. This is the property that makes
   the fix a fix rather than a retune, and it is the one bar a relabelled constant cannot pass.
7. **Switch off = identity:** `SFS_AXES_WIDTH_SCALE=0` reproduces `axes323` 172/172 and the old 6-of-9 table.

**D — Report and look.** `artifacts/t333/gate333.tsv`, one row per bar per piece, columns
`group piece metric value reference verdict note`. A four-view render `artifacts/t333/render333_axis.png`:
p2, p3, p7 as (r, z) profiles with the key line and the delivered line, plus one pot piece as the control that
did not move. **Look at it before writing the Reading**, and say in one sentence what the eye adds that the
table cannot.

**E — Say what changed in the pipeline's own language.** The line the assembler reads is the file; state whether
a consumer of `out/axes*/` sees any change in its inputs, and whether `run_potsac` (the paper chain,
`AxisExtraction/`) is touched at all (it must not be).

## Readings (pick one, verbatim, on a `Reading:` line)

- `axis-criterion-now-matches-the-key-on-all-nine` — bars 1-7 pass; the fix is in and the pots are identical.
- `axis-criterion-fixed-but-the-pots-move` — bars 1-2 pass, bar 3 fails: report the diff, do not ship.
- `axis-criterion-still-cannot-separate` — the statistic is replaced, bars 1 or 2 still fail: the pool or the
  input is the ceiling, and say which with the per-piece numbers.
- `axis-criterion-needs-a-redesign-beyond-this-ticket` — all three designs fail bar 6 or bar 4; write what the
  next design would have to be.

## Out of scope

- **Any assembly or seating run** (Juglet or Pot A) — the axis gets its own gate; the seating re-run is a later
  ticket, and no `gate`/seat number is produced here.
- Merging or building on ticket 325's branch; changing its gates.
- The union pool's generation (`run_potsac_union`, `potsac.py`), the 1.2x line rule (`keep_lines`,
  `tau = 1.2`, `kmax = 3`) and `PROFILE_BASINS = 60` — unless a bar above cannot pass without them, in which
  case change one at a time and show the pots gate after each.
- `Dataset/` writes, the MATLAB paper chain (`AxisExtraction/*.m`), the breakline and wall-side work, the
  3x lane wiring.
- New dependencies; anything that needs a GPU.

## Definition of done

`gate333.tsv` with every bar marked pass/fail and each verdict matching its number; the 172/172 `cmp` re-run
in the report with its command; the density sweep (1200/5000) table; the render, looked at; `git status`
showing only `sfs_axes/` files and this ticket; one `Reading:` line and one `End state:` line.
