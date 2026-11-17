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
**Status:** resolved
**Working in:** chat on Thinkbook16 (2026-11-17)
**Branch:** 333-axis-criterion-must-span-the-wall, in /c/PR/worktrees/sfs/333
**Worker:** dsh one-shot subagent w333
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

## Comments (worker, 2026-11-17) - w333

**Stage A — the baseline reproduces to the digit.** Job 35238715 (`submitA.sbatch`, sacct `COMPLETED 0:0`, 00:09:51): the shipped 1x geometry lane returns rank-0 `0.919388 13.163785 28.390410 3.441515 3.722610 1.844563 47.922394 3.047941 4.563711` (6 of 9), and its 172-file set is byte-identical to `axes323` (`sameA2=172 diffA2=0`, plain `cmp`). The nine Juglet files carry 13 lines (p5 also 28.499, p7 also 2.556829, p9 also 59.339 and 32.182).

**What the measurements decided** (run dir `runs/20261117-1317_e436f92_t333-axes`):

- **The shipped statistic is locally sound and globally degenerate.** On 9 of 9 pieces the GT key is the minimum of the shipped k=24 cost over a 32-tilt ladder (a 10-deg tilt costs 2.06-4.86x the key), yet cheaper wells exist elsewhere in the 4-dof space: p2's 11.92-deg line costs 0.0360 against the key's 0.0459; p7's 47.92-deg line 0.0612 against a 2.56-deg line's 0.0653. The mechanism is ticket 332's, confirmed: tilting makes each z slab cut a narrower azimuthal wedge, so a *wrong* axis measures thinner. "The (r,z) image is thin" cannot separate a surface of revolution from a flat patch.
- **p2 is an attractor, not noise.** 60 of its 120 pool lines are the same 11.91-deg line to 4 dp (the fixed point of `refine_axis_normalized`), and it beats the key under four independent thinness statistics (k=24 width 0.78x, apparent thickness 0.93x, azimuthal uniformity 0.84x, occupancy 0.87x) at a 0.61 mm offset — no per-piece geometric cost outvotes it.
- **The refinement walk is a third defect.** p8 passes today only because its cheapest pool line is 16.24 deg and the unbounded Nelder-Mead walks it to 3.05; p7 fails the mirror way (5.86 start walked to 47.92). Re-sorting by the *refined* cost is what lets the walk outvote the statistic.
- **25 statistics were ranked against the same 120-line pool** (k-neighbour width; width/rho at k=12..1200; width/rho^2; rho; log-log slopes; azimuthal uniformity and its mean form; three band normalisations; occupancy of (z,r) and (z,phi) grids; gap CV; sign flips; sphere/cylinder normal residuals; shape-operator uv shear; products and composites). None puts a <=10-deg line in its top 8 on all nine. The best of them is apparent wall thickness.

**Design shipped — design 2, made a shell statistic.** `sfs_axes/profile.py` gains `profile_band` = median over `PROFILE_SLABS=10` z slabs of the p90-p10 spread of the radial distance of *both* walls' points, pooled (apparent wall thickness, mm); a `PROFILE_POINTS` env override for bar 6; and a bounded polish (tilt capped in norm at `PROFILE_TILT_DEG=5`, foot shift at `PROFILE_SHIFT*0.1*size`). `SFS_AXES_WIDTH_SCALE` defaults on; `0` restores `wall_thickness` and the unbounded walk bit-for-bit. `select.py` is untouched. Design 1 was rejected on measurement: a 12-deg error on p2 measures *thinner* (0.0223 at k=12) than the truth (0.0310) and its ladder is non-monotone, so no wall-scale-derived window repairs it. Design 3 was measured as one of the 25: every multi-scale ratio variant puts p2's good line at rank 45-68 and its own argmin at 17.3 deg.

**Bars** — 79 per-piece rows in `artifacts/t333/gate333.tsv`.

| bar | measured | verdict |
|---|---|---|
| 1 — 1x within 10 deg on 9/9 | 5/9 (p2 11.59, p3 10.92, p7 21.04, p8 19.22) | fail |
| 2 — 3x within 10 deg, constants untouched | 2/9 (only p1, p7) | fail |
| 3 — pots do not move | 0 of 163 pot files byte-identical; rank-0 direction delta median 40.0 deg, max 89.8; corpus 33/172 within 10 deg against 137/172 for the same code switched off | fail |
| 4 — criterion separates | clause 1 0/9 (the key costs 0.02-0.43 mm *more* than the delivered line on every piece); clause 2 pool 4/5 decidable (p3 fails; p2/p7/p8/p9 have no <=5-deg pool line); clause 2 ladder 5/9 | fail |
| 5 — key refinement stays within 5 deg | 9/9, max 5.00 deg | pass |
| 6 — density 1200 and 5000 both 9/9 | 6/9 and 5/9 | fail |
| 7 — switch off = axes323 172/172 + old 6/9 | 172/172 byte-identical, old table reproduced | pass |

**Per-piece rank-0 deg** (1x 2500, 1x 1200, 1x 5000, 3x):

| piece | 1x 2500 | 1x 1200 | 1x 5000 | 3x |
|---|---|---|---|---|
| p1 | 1.52 | 1.20 | 1.01 | 2.67 |
| p2 | 11.59 | 11.03 | 11.59 | 8.65 |
| p3 | 10.92 | 10.87 | 10.92 | 16.17 |
| p4 | 9.06 | 9.14 | 9.06 | 20.19 |
| p5 | 7.00 | 5.57 | 5.69 | 12.68 |
| p6 | 2.01 | 4.68 | 2.92 | 12.06 |
| p7 | 21.04 | 0.98 | 21.18 | 4.76 |
| p8 | 19.22 | 18.82 | 16.86 | 20.96 |
| p9 | 4.50 | 4.50 | 4.50 | 89.45 |
| within 10 | 5/9 | 6/9 | 5/9 | 2/9 |

The density sweep moves pieces but not the level: the statistic is *density*-stable (6/9 and 5/9 around the 5/9 at 2500, mean 8.4 / 8.6 / 10.4 deg) and yet not *scale*-stable — the 3x cloud, where the same piece is 3x bigger with the same constants, is 2/9 against the old path's 7/9. Bar 6's invariance holds; bar 6's level does not.

**Bar 3 — the byte comparison, command and output.**

```
A=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0740_d628fc0_t323-axes/out/axes323
B=/data/gpfs/projects/punim2657/SfSpp/runs/20261117-1317_e436f92_t333-axes/out/axesG_172
same=0; diff=0
for f in $(ls $A); do if cmp -s "$A/$f" "$B/$f"; then same=$((same+1)); else diff=$((diff+1)); fi; done
echo "plain_cmp same=$same diff=$diff"
```

switch on: `plain_cmp same=0 diff=172`; switch off (`axesG_off172`): `plain_cmp same=172 diff=0`. The nine Juglet files are expected to differ; the 163 pot files are not, and none of them survives. Rank-0 direction deltas by pot (max / median, deg): A 84.68/40.96, B 59.75/51.79, C 89.21/61.07, D 87.81/36.39, E 89.83/33.47, F 79.38/58.27, G 51.36/41.75, H 89.29/51.59, I 88.43/21.98, J 88.36/46.00, Juglet 46.75/7.83. Line counts differ by at most 2 per file: the 1.2x rule compares costs on a new scale, so it keeps a different number of lines.

**Switch-off identity.** `SFS_AXES_WIDTH_SCALE=0` on the same 172 pieces gives 172/172 byte-identical to `axes323`, rank-0 delta max 0.000000, identical line counts, and the old 6/9 table (1.52 -> 0.92 etc., row `bar7_switchoff`). The off path is the ticket-324 code.

**Render, looked at** — `artifacts/t333/render333_axis.png`: p2, p3, p7 walls in the *key's* (r,z) frame (blue/orange walls, key black at r=0, delivered line red) plus Pot A 01 as the switch-off control. What the eye adds: on p2 and p3 the two wall bands are flat and parallel at r = 14.1-18.1 mm and the delivered line runs down the empty middle at r = 0.5-1.9 mm, so an 11-12 deg error produces *no* visible crossing — it looks like a correct axis; on p7 the walls curve from r = 0.1 to 16.6 mm and the delivered line visibly cuts across both bands; on the pot control the switch-off line lies flat on the vessel axis. The Juglet's failure mode is a wrong tilt inside a nearly cylindrical shell, which is why degrees are the only evidence and why a "thinner band" statistic is fooled.

**Pipeline language (E).** A consumer of `out/axes*/` reads one file per piece, rows of position-then-direction. With the switch on the number of lines per file changes and the rank-0 line moves by up to 90 deg on the pots, so the assembler would load different lines and seat differently — that is the reason not to merge. `run_potsac` and the paper chain (`AxisExtraction/*.m`) are untouched: the change is inside `sfs_axes/profile.py`, which the MATLAB chain does not import, and `scripts/run_benchmark_172.py` was not edited.

**Next ticket material.** The measurement says the statistic is not the only ceiling, so the cheaper variant worth measuring properly is the cut, not the cost: with the shipped cost, a bounded polish and "a refined line may not be promoted above a line that started better" (start+refined cost ordering), the same nine pieces measure 7/9 at 1x — `0.98 13.16 28.39 5.49 3.72 1.86 2.56 3.59 4.56` (job 35240144) — and the corpus barely moves, because the bound stops the p8 rescue that the change above loses. It was not shipped here: it does not replace the statistic, and its 3x lane was not measured.

**Artifacts.** `artifacts/t333/gate333.tsv` (79 rows), `artifacts/t333/render333_axis.png`, `artifacts/t333/diag_p2.png` (p2 with key, the 11.91 clone and the 6.61 line), `artifacts/t333/dumps/` (score tables, bar4/bar5 probe). Heavy data stays on Spartan in `runs/20261117-1317_e436f92_t333-axes` (`out/axesG_*`, `out/score_*.tsv`, `out/bar45_G.tsv`, `work/*.py`, `logs/`, `slurm-35240863.out`).

**Jobs, all polled and all `COMPLETED 0:0`:** 35238715 (Stage A, 00:09:51), 35240022 (three-statistic pipeline run, 00:00:35), 35240242 (first full suite, 00:11:32), 35240863 (final suite G, 00:11:11), 35241282 (four-view render, 00:00:07); earlier probes 35239255 (tilt ladder), 35239381 (pool dump), 35239430/35239602/35239628/35239671/35239777/35239880/35239909/35239980/35240053/35240070/35240144 (candidate statistics, cut simulations, p2 diagnostic, bar4/bar5 prototype).

Reading: axis-criterion-still-cannot-separate

**End state:** the ranking statistic is replaced (apparent wall thickness behind a default-on `SFS_AXES_WIDTH_SCALE`, with a 5-deg-capped polish) and the change is left uncommitted; bars 5 and 7 pass, bars 1, 2, 3, 4 and 6 fail (1x 5/9, 3x 2/9, 0 of 163 pot files identical, the key is not a sherd's own minimiser, 6/9 and 5/9 at 1200/5000), so it must not be merged as-is — the pool's ordering and, on p2, the input are the ceiling, and `git status --short` shows `M sfs_axes/profile.py` and `M` this ticket.

---

## Verdict (lead, 2026-11-17)

**Reading accepted — `axis-criterion-still-cannot-separate` — and the ticket's own hypothesis is refuted, not
merely unproven. Nothing ships: the candidate statistic breaks the ten pots so badly that it would corrupt
every seating result in the corpus, and on the Juglet it is no better than what it replaced. The change was
discarded in the worktree (`git checkout -- sfs_axes/profile.py`); the record is this ticket.**

### What I checked myself

- **The nine delivered angles, recomputed from the run's own output** (`out/axesG_1x/Juglet_Piece_N_Axis.xyz`
  against `Dataset/Juglet_GT`, my own code): 1.52, 11.59, 10.92, 9.06, 7.00, 2.01, 21.04, 19.22, 4.50 deg —
  **5 of 9 within 10 deg**, piece for piece the gate's row. Bar 1 fails as reported, and the failure *moved*:
  p3 improved 28.4 -> 10.9 and p2 13.2 -> 11.6, while **p7 went 47.9 -> 21.0 and p8 broke, 3.1 -> 19.2**.
- **Bar 2 is 3 of 9, not 2** (the closing message says 2/9): `gate333.tsv` records `3/9` with p1 2.67, p2 8.65
  and p7 4.76 passing, and p9 **89.45 deg**. The gate's number is the record.
- **The pots, `cmp` run by me on Spartan**, `out/axesG_172` against `axes323` over the 163 pot files:
  **163 of 163 differ** — rank-0 direction delta median 39.99 deg, max 89.83 (Pot_E), per-pot medians 22.0-61.1.
  Not a shift of the corpus by one tilt: the corpus's axes are replaced by different axes.
- **Bar 7 is true**: `out/axesG_off172` against `axes323`, **172 of 172 identical, 0 differ** — the switch-off
  path is exactly the shipped one, so the corpus was never at risk from the branch.
- **The render, looked at before this verdict**: p2's two walls sit as flat bands at r = 15-17.5 mm and the
  delivered line's r drifts only 0.2 -> 1.6 mm across the whole piece; p3 the same; p7 shows a steeply curved
  profile where the delivered line runs 6.5 mm down to 0. That is the geometry behind p2: **on a nearly
  cylindrical patch an 11.6 deg axis error displaces the wall by well under a millimetre, so no thinness
  statistic has anything to bite on.** Pot A 01 with the switch off shows our line sitting on the key down a
  70 mm profile — the identity is real, and the contrast between the two panels is the whole finding.

### The finding, in the ticket's own terms

**Bar 4 is the decisive result, and it is not about tuning.** On **all nine** pieces the GT axis costs *more*
than the delivered line: `cost(key) - cost(delivered)` = +0.12 to +0.39 mm. The vessel's axis is not the
minimiser of apparent wall thickness on a sherd, and cannot be: a wall patch of a surface of revolution is
locally almost as thin about any nearby axis, so the statistic rewards whichever axis makes the patch look
flattest. A better statistic in this family finds a *different* wrong line, not the right one. That closes the
"reweight the profile thinness" family (ticket 322's design included) and explains why every variant moved the
answer around without landing on the key: p2's pool holds ~60 clones of one 11.9 deg line — the fixed point of
its own refiner — and that line beats the true axis under four independent thinness statistics.

**Two things this ticket did establish, and they should not be lost:**

1. **The 5 deg bound on the polish is right.** Bar 5 passes **9 of 9, max 5.00 deg**: the refiner can no longer
   walk the key 13 deg away from itself. Today's p8 "pass" (3.05 deg) was a walk artefact, so the current 6 of 9
   is partly luck and must not be quoted as a capability.
2. **Density independence is achievable but not sufficient**: 6 of 9 at 1,200 points, 5 of 9 at 5,000 — the
   statistic is no longer sampling-bound, and still does not find the axis.

### What it means for the pipeline

The axis stays oracle-fed: the 3x lanes keep reading `Dataset/Juglet_large`, and that loan is now **named
unrepayable by this route**, not merely unpaid. The next attempt must use evidence that is not the shell's
thickness — the rim or base ring (the only places a vessel's axis is directly observable), the piece's own
boundary curvature, or consistency across several pieces at once. That is a design decision and it is the
conservator's to make; nothing in this ticket presumes it.

**No code ships. `sfs_axes/` is unchanged on `main`; the pot corpus is untouched by the branch; the failed
statistic is recorded here with its numbers so that it is not tried again.**

