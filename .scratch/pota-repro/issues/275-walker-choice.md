# 275 — Pick the walker from the shape of the largest component

Answers: E1
Status: ready-for-agent
Working in: C:/PR/worktrees/sfs/275 (worktree at the dispatch commit) + Spartan runs/ directory; main source read-only
Needs-eye: no

## Why

Ticket 273's matrix (commit 6194959) shows the two walkers own different lane classes, and that no single
global switch serves both:

- The 247 arm (largest component + clock sort + CCW vote — today's `SFS_FULL_WALK=0` path) is clean and
  complete on the Pot C / Pot J piece-01 lanes: 208 / 226 / 170 / 184 dots, median 0.46-0.54 mm, **100%
  precision and 100% author-side coverage**, maxjump <= 4.4 mm, zero jumps.
- The same arm explodes on the braid bags: P03 Bl1 18255 dots / cov 5.74 / 86 jumps; P22 Bl0 2176 / 15.3;
  P22 Bl1 1904 / 16.1.
- The full walk + stop (shipped) is the only thing that holds P03 Bl1 (339 / 0.523 / 99.12) and P22 Bl1
  (143 / 0.552 / 96.5) — and it collapses the Pot C / Pot J lanes to 11 / 82 / 25 dots.
- The component structure explains the split. On Pot C / J the rim IS the largest component (711 of 1000,
  815 of 1074, 586 of 844, 629 of 723) and the rest is debris the walk has no business visiting. On P03 Bl1
  the largest component is 1045 of 1121 and is a double-cover braid, so keeping it and clock-sorting it is
  the failure.

## What

**Phase 1 — measure, change no behaviour.**

Instrument BOTH candidate loops on the ten lanes of ticket 273 plus the six guard lanes (16 lanes, edge stage
only, frozen sheet pairs, md5s recorded), and print per candidate:

- n after resample, arclength L, RMS radius R;
- `turnSum / (2*pi)` and `L / (2*pi*R)`;
- closure gap `|last - first|` and maxjump.

Candidates: (a) 247 arm = largest component, clock sort, vote; (b) full walk + stop (today's default).

No default changes in Phase 1. **GATE: if these four quantities do not separate the four Pot C / J lanes from
P03 Bl1 and P22 Bl1 on every lane, STOP and report.** Do not wire a selector that cannot be shown to work.

**Phase 2 — wire the choice.** Only if Phase 1 separates. Build both loops, score each with the rule
Phase 1 justifies, keep the better one, and continue through the existing resample. One printed line per
lane: `[WALK-275] chose=<arm> turn=<> Lr=<> gap=<> maxjump=<>`. The selector is code, not a new global
env switch.

## Phase 0 (added by the lead, 2026-10-24) — the five lanes are not comparable yet

The 273 matrix's five frozen sheet pairs were not all built at the same theta:

| lane | tree | mesh log says |
|---|---|---|
| Pot C 01 | `pota251_paper_Pot_C_01` | `thetaDeg=4.00000` |
| Pot J 01 | `pota259_paper_Pot_J_01` | `thetaDeg=4.00000` |
| Pot D 03 / 22 / 01 | `pota271T1_*` | `thetaDeg=3.40000` (T1 sheets; the older `mesh.log` in those trees holds the 4.0 run) |

So the four "collapsed" lanes are on the **old** sheets and the guards on the new ones. Bracket the
comparison before drawing anything from it: rebuild the mesh for Pot C piece 01 and Pot J piece 01 at the
shipped theta (3.4), then re-run the same four configs on those sheets. If the collapse survives on 3.4
sheets, the walker comparison stands; if it does not, the walker question shrinks and the finding is that
theta had a second effect.

**Mechanism already measured on the 4.0 sheets** (lead, from the two bags in `Temp/Temp_edge/`, 5 mm
components, seed = dot nearest the cloud centroid):

- Pot C 01 Bl1: 1,074 dots in 2 lumps, **815 (rim) + 259 (satellite)**. The seed lands in the **259-dot
  satellite**, 27.19 mm from the rim. The walk consumed exactly those 259 dots and stopped — the log's
  `step=258` and `left=815` match this to the dot.
- Pot J 01 Bl0: 844 dots in 4 lumps, **586 / 130 / 76 / 52**. The seed lands in the **130-dot lump**,
  26.10 mm from the rim and 16.21 mm from the 76-dot lump. The log says `step=129`, `left=714`,
  nearest fresh **16.206 mm** — the same 16.21 mm, measured independently.

So on these two pieces the walk is not stopping "early on the rim": it never reaches the rim at all,
because the seed chooses a debris lump that happens to sit nearer the centroid. Phase 1 must therefore
report **which lump the seed lands in** and that lump's distance to the largest lump, per lane — a
selector that cannot see that will keep choosing the wrong arm for the same reason.

## Pre-registered acceptance

Phase 2 is accepted only if ALL of:

1. C01 Bl0/Bl1 and J01 Bl0/Bl1 reach bar — cov >= 90, med <= 2.0 mm, zero jumps > 10 mm — with author-side
   coverage >= 99%.
2. P03 Bl1 holds cov >= 99.0 and med <= 0.6; P22 Bl1 holds cov >= 96.0 and med <= 0.6.
3. P03 Bl0 (216 / 0.354 / 100.0) and P22 Bl0 (131 / 0.668 / 87.8) do not move beyond n +-2, med +-0.15,
   cov +-1.0.
4. P01 Bl0 (334 / 0.621 / 99.4) and P01 Bl1 (346 / 1.011 / 95.7) do not move beyond the same tolerance.
5. The scorer prints BOTH directions (ours->author and author->ours). A lane row without both is not accepted.
6. The arm that is NOT chosen reproduces its 273 column, so the choice is the only change.

If any of 1-4 fails: report which and stop. Do not retune a threshold to fit.

## Constraints

- Edge stage only. No mesh run, no mesh rebuild.
- Frozen sheet pairs; record their md5s in the ticket.
- Run directory `SfSpp/runs/<YYYYMMDD-HHMM>_<sha7>_p275-walker/` with `run.json`, `submit.sbatch`,
  `logs/`, `out/`; append ONE `runs/index.tsv` row with verdict and human_note empty.
- No numbered tree copies. A Spartan-side build worktree goes at `sfs_preprocessing.wt/275`.
- Do not change the `SFS_STOP_NOFRESH` or `SFS_FULL_WALK` defaults; the stop rule stays as shipped.
- Keep the 274 clamp.

## Evidence to return

Phase 1 table (16 lanes x 2 candidates x the four quantities) and the separation verdict; then the Phase 2
table with both coverage directions, the `[WALK-275]` lines, the run id, and `git diff --stat`.
