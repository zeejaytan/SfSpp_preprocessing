# 75 — Where sherd 7's last off-lip dots enter, and why the chord growth turns the 6-7 join into a fold

**What to build:** first a read-only stage that says *how* the 29 dots that still sit off the
inner wall on sherd 7 survived the chord growth, and *what* happened to the 6-7 pair under it;
then exactly **one** default-off arm, chosen by that stage, that closes the leak the stage
found. Ticket 74 established that the growth is the strong lever (sherd 5 21 -> 0, 6 3 -> 0,
7 54 -> 29, 8 9 -> 0 as dot counts, sherd 7's off-lip contour 31.80 -> 17.40 mm) and that it
costs the 6-7 pair its sign. Neither of those is explained yet, and both are cheap to explain
offline before another cell is run.

**Answers:** E1
**Depends on:** 74 (the three doors, landed fad4e5f), 73 (the re-admission path, landed
9ff83e7), 72 (the trim, landed c27284c), 348 (the measured contact set), 328 (the wall side)
**Budget:** small-medium. One read-only stage, one build, three or four 3x cells, two 1x
control cells, one Pot A cell.

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-16)
**Branch:** 75-where-sherd-7s-remainder-enters-and-why-growth-folds-the-6-7-join, in /c/PR/worktrees/sfs/75
**Worker:** dsh one-shot subagent w75, dispatched 2026-11-16 by the lead

## Given — what the numbers already say

1. **The growth is where the break face dies on three of the four sherds, and it stops half
   way on sherd 7.** Off-lip dots at the conservator's 0.8 mm cut (`gate74.tsv`, arm G,
   3x Juglet, one draw):

   | arm | sherd 5 | sherd 6 | sherd 7 | sherd 8 |
   |---|---|---|---|---|
   | `off` | 21/150 | 3/141 | 54/173 (31.80 mm) | 9/126 |
   | Arm M (merge gate) | 0/147 | 3/138 | 49/165 (29.56 mm) | 9/124 |
   | Arm G (chord growth) | 0/145 | 0/130 | **29/170 (17.40 mm)** | 0/120 |
   | Arm GM | 0/145 | 0/130 | 28/171 (16.80 mm) | 0/120 |

2. **The same thing with the refinement gate stripped** (the lead's control cells, job
   `35132483` for 3x and Pot A, `35132554` for 1x): `Mnr` 0/146, 3/142, 52/174 (30.60 mm),
   9/125; `Gnr` 0/143, 0/134, **30/171 (17.40 mm)**, 0/123; `ref` (the gate alone, no switch)
   20/149 (12.00 mm), 3/138, 49/165 (29.57 mm), 9/124. So the growth's own effect, with nothing
   else armed, is 5 21->0, 6 3->0, 7 54->30, 8 9->0.

3. **Sherd 7 keeps about 17 mm of line on the outside**, which is 5.4 mm above the 12 mm bar,
   in every arm including GM — so the two doors together do not reach it, and the remaining
   dots are **not** the ones the merge gate refused (the gate fires once on sherd 5 only).

4. **The 6-7 pair changes sign under the growth alone.** Median normal dot over paired dots
   (|dp| < 3 mm): `off` **-0.997** (n=44, 34 opposed), `M` -0.998 (n=46, 39), `G` **+0.551**
   (n=31, 2), `GM` +0.563 (n=32, 2). In the control cells with no refinement gate: `Gnr`
   **+0.657** (0 opposed), `Mnr` -0.997 (42 opposed), `ref` -0.998 (39 opposed). Ticket 328
   recorded -0.786 at this pair, and ticket 348 measured 6-7 as a **real back-to-back join**
   (median normal dot -0.985 there, in the measured contact set). A positive median at a
   back-to-back join means the two lines now face the same way, i.e. one of them has moved to
   the other face or the paired population has changed.

5. **The growth's own test, as it stands after Ticket 74** (`mesh_processing_headless.cpp`,
   ticket-74 file, 279 923 B): the base branch computes the mean normal of the claimed points
   within `baseU73` (1.5 mm x `SFS_TREE_UNITS_PER_MM` = 4.5 tree units) and uses it **only
   when at least 3 claimed points fall in that ball** (`cnt73 >= 3`, `used73`); otherwise it
   falls back to the legacy per-step comparison against the current front point's own normal
   (`fallback73`). Arm G then requires both the chord bound (`candAng73 > g_growBaseTheta`
   refuses) and the legacy per-step test. The refusal path is at `growPaper234` around
   :3662-3694; Arm G's two-test block is :3698-3748; the switch parser (`t74::ensure74`) is
   :2504-2520.

6. **The refinement adds points back after the growth**, and Ticket 73 measured that it
   re-admits 39 of the 69 off-lip dots in a run where the trim was on (Stage 0,
   `attrib73.tsv`). Ticket 74's gate on that step (`SFS_REFINE_ADD_GATE=1`,
   `SFS_REFINE_ADD_ANGLE_DEG=12`) is what moved Pot A (4 of 8 pieces) and sherd 1's ruler in
   ticket 74's armed cells — so **the gate is not the tool to reach for here**: any arm in this
   ticket must be measured against a no-gate cell, and Pot A must be run with no gate.

7. **Where the dots come from is already instrumented.** `SFS_DUMP_STAGE=<dir>` with
   `SFS_DUMP_PIECES=<list>` (armed by `g_dumpOn25`, :1882-1929) writes `r2_clusters_premerge.ply`,
   `r3_after_merge.json`, and the per-rung cloud files used by `attrib73.py`/`attrib74.py`.
   Ticket 73's `attrib74.py` (in this ticket's run or copied from
   `C:/PR/artifacts/t74/attrib74.py`) fixes the branch order that made "merged" unreachable.

## Part A — Stage 0, read-only: how did those dots survive?

No switches, no new cells needed for A1 and A2 if the 3x `off` and `Gnr` geoms and a fresh
dump are available (a dump-armed cell of the `Gnr` arm is acceptable and cheap; run
`SFS_DUMP_STAGE` on it).

**A1 — the remainder census `remainder75.tsv`**, one row per off-lip dot on sherd 7 in the
`Gnr` arm (**29 or 30 dots**), columns:

```
dot_index  x  y  z  chord_turn_1p5_deg  chord_turn_3p0_deg  chord_turn_5p0_deg
d_inner_mm  d_outer_mm  growth_origin  cnt73_at_decision  base_used_flag
refine_added_flag  present_in_off_flag  off_lip_in_off_flag  nn_to_off_mm
```

with `growth_origin` one of `grown`, `grown_fallback`, `refined_added`, `merged`,
`inherited` (present in `off` and still off-lip), and `cnt73_at_decision` read from the
growth's own log line (print it: `[SFS-75] GROWDEC piece dot cnt used fallback angle chord`
for every refused-or-accepted candidate within 1 mm of a surviving off-lip dot, so the table
can be reconstructed rather than guessed).

**A2 — the 6-7 fold `fold75.tsv`**, one row per paired dot of the 6-7 seam in the `off` arm
and in the `Gnr` arm: `piece  dot_id  x y z  nx ny nz  dot_product  dp_mm  matched_off_dot
matched_off_dot_product`. Match **by dot identity against the off arm** (nearest dot within
0.5 mm), so the table shows whether *the same pairs* changed their dot product (the line
moved) or *the population* changed (different dots pair now). Report both medians.

**A3 — the decision table `stage75_summary.md`.** For sherd 7, the share of the 29 dots by
`growth_origin`, and for the fold, the same-pairs vs new-population split, each with a number.
Write one of these slugs and stop there:

- `the-growth-falls-back-and-the-fallback-is-the-leak` — most surviving dots were accepted
  with `cnt73 < 3` / `fallback73` true, so the chord test never judged them;
- `the-refinement-puts-them-back` — most surviving dots are `refined_added` (refused by the
  growth, re-admitted by the refinement);
- `the-turn-is-genuinely-under-the-bound` — most are `grown` with `base_used` and a chord
  turn below 25 deg at 1.5 mm, so the bound is wrong for that stretch, not bypassed;
- `the-fold-is-the-same-dots-moved` / `the-fold-is-a-different-population` — for 6-7;
- `no-single-cause` — **stop rule**: if no origin reaches 50% of the dots, stop here, send the
  shares and do not build Part B.

## Part B — one default-off arm, chosen by A3

Build **only** the arm the A3 slug names. All of them print `[SFS-75] ...` lines with the
counts that justify themselves, and all default to today's path with the switch unset.

- **Arm F (fallback known to be the leak)** — `SFS_GROW_BASE_FALLBACK=refuse|legacy`, default
  `legacy`. With `refuse`, a candidate whose base ball holds fewer than 3 claimed points is
  **refused** instead of being judged by the per-step angle; print `[SFS-75] BASEFALL piece
  dot cnt` per refusal and a `[SFS-75] BASEFALL-SUM piece refusals` line. Same place in
  `growPaper234` as the `cnt73 >= 3` branch.
- **Arm R (the refinement is the leak)** — `SFS_REFINE_LOCAL_GUARD=1`, default off. The
  refinement's add-back decision additionally refuses a point whose **chord turn at 1.5 mm
  about that point** (the same chord the growth uses, on the refined cluster's own normals)
  exceeds 25 deg; print `[SFS-75] REFADD piece point angle refused`. This is **not**
  `SFS_REFINE_ADD_GATE`: that gate compares against the nearest cluster point's normal and is
  the thing that moved Pot A; this one reuses the growth's own geometric test.
- **Arm L (the turn really is under the bound)** — `SFS_GROW_BASE2_MM` (default 0 = off, use
  3.0) and `SFS_GROW_BASE2_THETA_DEG` (default 45.0): a **second, longer** chord test that
  refuses a candidate whose turn at 3.0 mm exceeds 45 deg (the measured wall turn at 3 mm is
  26.7 deg, the off-lip turn 48.9 deg, so 45 separates them), applied **in addition** to the
  existing 1.5 mm / 25 deg test. Print `[SFS-75] CHORD2 piece dot chord2 bound`.

If A3 returns `the-fold-is-the-same-dots-moved`, Part B also runs the same arm and reports the
6-7 median; if it returns `different-population`, no new arm is needed for 6-7 — record that
the pair statistic must be matched by dot identity from now on, and gate on that.

## Part C — cells and gates

Cells (one draw each; the `off` and `Gnr` numbers already exist and may be reused):

| cell | what | why |
|---|---|---|
| `off_3x` | nine 3x sherds, no switch | the baseline (exists) |
| `arm_3x` | nine 3x sherds, the chosen switch | the cure |
| `pota_arm` | eight 1x Pot A pieces, the chosen switch, **no** `SFS_REFINE_ADD_GATE` | no harm |
| `j1_arm` | 1x Juglet piece 1, the chosen switch | the frozen ruler |

Use the ticket-73/74 cell recipe (`stage66/run_cell66.sh` with the ticket-74 `submit_cells.sbatch`
as the model; 3x inputs in run `20261112-0218_b1e1580_t331-large`: `mesh_large/`,
`cloud_mesh/`, `pins/MANIFEST_JUGLET_LARGE.tsv`, `AXIS_DIR Dataset/Juglet_large`,
`WORNESS=0.7`; Pot A pins from its own clouds, no manifest exists).

Gate table `gate75.tsv` with columns `group  metric  piece  off  arm  ref  verdict`, groups
`primary`, `pairs`, `j1_ruler`, `pota`, `coverage`, `identity`. Bars:

- **primary**: sherd 7's off-lip contour < 12 mm; sherds 5, 6 and 8 stay at 0 off-lip dots;
  pooled dots not worse than 29 of 565;
- **pairs**: 1-4 positive with 0 opposed (as in the no-gate cells); **6-7 negative again,
  median <= -0.9 with at least 30 opposed dots** (it is a measured back-to-back join); every
  other pair within 0.10 of `off`;
- **j1_ruler** at 1x: no column worse by more than 10% against the `off` arm
  (`blindDeg`, `farS0`, `ring_cov_deg5`, `f2r_le1`, `r2f_le1`);
- **pota**: 8 of 8 pieces within 1 dot of `pota_off` (this is the bar the ticket-74 gate failed,
  and the reason Pot A runs without it);
- **coverage**: S0/S1/Bl0/Bl1 exported on 9 of 9 pieces;
- **identity**: with the switch unset, the 1x surfaces byte-identical and the 3x surfaces
  within the piece's own run-to-run spread (the unseeded 30-point ray cast moves piece 1's
  Surface_1 by 2.418 mm and 3x has no pristine twin — state the bound you used).

## Part D — readings

Write exactly one, with the numbers that support it:

- `the-fallback-is-the-leak-and-refusing-it-cures-sherd-7`
- `the-refinement-puts-the-line-back-and-guarding-it-cures-sherd-7`
- `the-turn-is-under-the-bound-and-a-longer-chord-cures-sherd-7`
- `the-remainder-survives-every-door` — an honest miss, with the shares;
- `no-single-cause` — the stop rule fired and Part B was not built.

## Part E — acceptance

- [ ] Stage 0 runs before any cell, and its slug is quoted verbatim in the ticket
- [ ] `remainder75.tsv` has one row per surviving off-lip dot on sherd 7 (29 or 30) and every
      column filled, `NA` only where the quantity is undefined and the reason stated
- [ ] `fold75.tsv` reports both medians (same dot identity, current pairing) and the counts
- [ ] exactly one Part B switch exists, default-off, with its `[SFS-75]` print lines
- [ ] the switch unset reproduces the `off` arm (state the identity bound you got)
- [ ] `gate75.tsv` carries every group and every bar above, with PASS/FAIL per row
- [ ] Pot A runs **without** `SFS_REFINE_ADD_GATE`, and 8 of 8 pieces are within 1 dot
- [ ] every job's `sacct` State/ExitCode is in the ticket, and the run directory holds
      `run.json`, `submit.sbatch`, `logs/`, `out/`
- [ ] the render `render75_before_after.png` (sherd 7 before/after, and the 6-7 seam before and
      after under the chosen arm) is written and looked at before the reading is written
- [ ] no commit is made by the worker; the lead lands it

## Out of scope

- the trace guard (Pot A tickets 75/78) — closed by the conservator's ruling of 2026-11-15;
- `SFS_REFINE_ADD_GATE` / `SFS_REFINE_ADD_ANGLE_DEG` as the cure: measured in ticket 74 to
  cost Pot A four pieces of eight and sherd 1's `r2f_le1` column;
- sweeping `SFS_GROW_BASE_THETA_DEG` or `SFS_PAPER_RHOINN` as a dial;
- anything under `class/`, `hpc/` or the assembler; any edit to `run_cell66.sh` itself;
  any edit under `Dataset/` or `px3/`.
