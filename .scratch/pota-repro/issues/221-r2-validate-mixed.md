# 221 - R2 validation on the 5 MIXED pieces + P16 re-baseline (220 follow-up)

Status: ready-for-agent
Answers: none (splitter-method trial; context 220, rulers 214/217)

## Goal
Validate the 220 R2 stopping rule beyond n=2: run the top-down ladder on the five 214-MIXED pieces (P12/P15/P22/P25/P27) plus a P16 re-baseline. Rule FROZEN from 220 (do not retune): R1 = first threshold with top2>=70% AND third<=8% AND 2nd/1st>=0.5; R2 = R1 at TWO CONSECUTIVE thresholds. Question: does R2 stop exist on each piece, and do all lanes score at bar there?

## Boundary (worker: read-only except where named)
- MAY touch (Spartan experiment copy ONLY, fresh dir sfs-fix-221): reuse the exp-220 single-shot method (branch exp-221 off origin/exp-220, unmerged); fresh run dirs (ladder + edge per piece).
- MAY run: top-down ladder (220 schedule) on P12/P15/P22/P25/P27 + P16; edge + score vs author lanes at each R2 stop (stretch is the verdict -- run it).
- Do NOT touch: main worktree (user 204-edit live), .wt-*, other branches (pristine-splitwalk, exp-220, exp-218), stashes, v0/v1 bundles, other tickets (append Comments here only).
- ORIG-free: author lanes as ruler only (214 staged inputs).

## Constraints
- P16 re-baseline is part of the verdict: record default-4.5 segmentation (cluster count, biggest, S0/S1/UN sizes) alongside the ladder, to test the 220 RED FLAG (214 logged 43/biggest 4799; 220 got 9/biggest 11261). Same for each piece vs its 214-era count where logged.
- 100% dot accounting every ladder row (clusters+UN=cloud), 220 pattern.
- Slots flip per piece (209 pattern, ourBl0->o1 typical) -- verify per piece, never blanket-swap.
- Report channel = this ticket's Comments + completion notice (no send_message downward).

## Acceptance (lead judges; numbers + cites + paths)
- Per piece (6 rows): ladder table, R2 stop (thresholds) or FAIL, lane scores at stop (bar med<2, cov>=90% both lanes), Bl0 unharmed.
- Overall: R2 generalizes n-out-of-6? P16 re-baseline vs 214-fresh (stale confirmed or overturned)?
- Landing decision explicitly NOT in scope (needs lead + user).

## Required evidence to report
- Branch exp-221 (unmerged), Spartan job IDs + sacct State/ExitCode, 6 ladder tables + accounting, lane scores at stops, segmentation-vs-214 comparison.
