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
