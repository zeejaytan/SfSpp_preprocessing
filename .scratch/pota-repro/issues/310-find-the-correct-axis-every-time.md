# 310: Find the correct axis every time — our own chain already produces it, in 3 draws of 8

**Answers:** E1
**Blocked by:** none
**Status:** ready-for-agent
**Worker:** sfs310
**Budget:** large 12
**Hand-over:** Claude (Spartan compute node, assembler E2E)

## What to build

Make the axis extractor return the correct axis for a piece on **every** draw, not on three draws in eight,
and prove it by seating Pot A without best-of-N. The correct axis is not missing from our output and does not
come from the authors: **when it is present, our own axes seat Pot A 8/8 sherds and 15/15 joins.**

### The measurement this ticket starts from (lead, 2026-11-05, from the ticket-308 Pot A run)

`runs/20261105-0532_d330469_t308a-axes/out/pota/paper_s0..s7` holds eight independent draws of the same
pipeline on the same surfaces, one per seed. For each seed, the angle from every line in
`Pot_A_Piece_08_Axis.xyz` to the good axis (the direction ticket 304 recovered at step 1 with the equal-count
cut off — 5.23 deg from the released line 1), and that seed's assembly result on Pot A
(`runs/20261105-0548_d330469_t308b-A/out/PAs<seed>/1. Acc.txt`):

| seed | lines in Piece 08, deg from the good axis | joins |
|---|---|---|
| 0 | 68.77, 89.36, 38.28 | 13/15 |
| 1 | 68.77, 48.85, 89.36, **0.19**, 30.41 | **15/15** |
| 2 | 68.77, 89.36, 33.56 | 13/15 |
| 3 | 48.85, 89.36, 38.28, 26.01 | 13/15 |
| 4 | 68.77, 89.36, 43.23, **0.00** | **15/15** |
| 5 | 68.77, 48.85, 89.36, **0.00** | **15/15** |
| 6 | 48.85, 89.36, 26.01 | 13/15 |
| 7 | 68.77, 48.85 | 13/15 |

Three facts, and every stage below follows from them:

1. **The three seeds that seat are exactly the three whose file contains the good line.** Nothing else differs
   between seeds — same commit, same surfaces, same breaklines, same binary.
2. **Extra lines are not the problem, a missing correct line is.** Seeds 1, 4 and 5 carry 4-5 lines each,
   including three wrong ones, which is MORE lines than the authors' 2 — and they still seat 15/15. So the
   earlier reading that 'extra lines hurt' (ticket 306, which added a line to Piece 07) was about a different
   piece and must not be generalised here.
3. **The wrong basins recur, the right one does not.** 68.77, 89.36 and 48.85 appear in most seeds; 38.28,
   33.56, 30.41 and 26.01 come and go. The good basin appears in 3 of 8. Ticket 306 found the same on this
   piece from the other side: the global cost minimum on Piece 08 is a WRONG basin (529 of 1,000 draws, 30.2
   deg off), while the good basin ranks 13th-38th and was deleted by the top-10 cut or the 1.1 prune.

So the failure is **selection**: our sampler and shortlist prefer recurring wrong basins whose cost is
lower than the correct one's. The assembler is not implicated — it seats 15/15 on the same binary given the
good line. **Do not touch the assembler.**

### What is already known, so it is not re-measured

- The equal-count cut is off by default (ticket 306) and the 1.1 cost prune is off by default (ticket 307);
  the paper's top-10 + 10-deg dedup is the shipped rule. The good line still goes missing in 5 draws of 8.
- The good axis IS a stationary point of the full-cloud cost on Piece 08 (ticket 304: refine from it stays at
  5.2280 deg; ticket 302's parity check puts our refinement within 1e-9 relative of MATLAB), so it is not a
  fitting artefact and not a tolerance problem.
- Giving Piece 07 a second line collapsed an earlier assembly to 4/8 + 5/15 (ticket 306, with our line, with
  the authors' line 1 verbatim, and with their whole three-line file). Whatever this ticket ships must be
  tested on all eight Pot A pieces, not just Piece 08.
- Reusable instruments from the stopped ticket 309: `.scratch/pota-repro/309-stage/bspline309.py` (B-spline
  resampling of a piece's two surfaces) and `stagea309.py` (refine from a given line and report stationarity).
  306/307/308-stage hold the pool-dump, scorer and E2E harnesses.

## Stage A — what statistic separates the good line from the recurring wrong ones? (no E2E)

**A1 the per-line table.** Over >= 20 seeds on Pot A Piece 08 (with Pieces 01 and 04 as controls), dump the
pre-dedup candidate pool and the written file, and record for every written line, computed from the piece's own
two surfaces only:

- cost per point on wall 0 alone, wall 1 alone, and the paper's combined cost;
- the GM/Huber inlier fraction on each wall separately (same threshold both walls);
- the Pottmann constraint residual on each wall;
- **cross-wall agreement**: refine the line on wall 0 only and on wall 1 only, then report the angle and the
  point offset between the two independent optima. This is the one statistic the current cost does not encode:
  a true pot axis is a joint minimum of both walls, while a basin fed by one wall's noise should split.
- **radius-profile consistency**: in cylindrical coordinates about the line, the radius as a function of height
  should describe the two walls of one vessel — report the spread of (r_inner - r_outer) and the roughness of
  r(h) on each wall; a wrong axis shears the profile.
- line-to-geometry placement: distance from the line to the piece's centroid, to its bounding-box centre, and
  the fraction of the piece inside the cylinder of radius r90 — recorded as a descriptor, not as a rule;
- cluster occupancy: how many of the 1,000 draws landed within 10 and 25 deg of the line, and its rank by cost.

**A2 the separation table.** For each statistic, report how well it separates the good line from the wrong
lines across all seeds where both are present (e.g. seeds 1, 4, 5 and any more found): median and range for
each class, and whether a threshold exists with no overlap. **Name the statistic(s) that separate, with the
numbers.** If none separates, say so plainly — that is a result and it redirects the ticket to A4.

**A3 prevalence.** How many of >= 20 seeds write a line within 5 deg of the good axis (the 308 count is 3 of
8). Report the count and the seeds. This is the baseline the rule must beat.

**A4 if no single statistic separates.** Test the two structural hypotheses the record already suggests, and
report each with a measurement: (i) the good basin is being lost at the **shortlist** stage, not the sampler —
re-run the shortlist with 30 candidates kept instead of 10 and see whether the good line then survives; (ii) it
is being lost at the **refine** stage — refine the good basin's raw candidate on all points and re-rank. Also
test simply raising the draw count (1,000 -> 10,000) on this piece and report whether prevalence rises; that is
the cheap null and it must be measured before any cleverer rule is proposed.

## Stage B — the blind rule

Turn the winning separator from A into a selection rule in `sfs_axes/`, and prove it is blind:

- **B1** the rule may use only the piece's own surfaces, breaklines and the candidate's own optima. It may NOT
  read the released `Axes/` files, the ground-truth poses, or the known-good direction, and nothing may be
  fitted to them. State in one line which paper clause or which measured mechanism warrants each term.
- **B2** with the rule on, over >= 10 seeds on Pot A Piece 08, count how many seeds write a line within 5 deg
  of the good axis. Target: 10 of 10. Report the count, not the best.
- **B3** with the rule on, write the full 163-piece set to NEW paths and report the line-count census against
  ticket 307's 238 lines / 163 files and the released 220. Report the runtime.
- **B4** keep the MATLAB-faithful behaviour reachable behind a switch, and say which value the default takes.

If the rule cannot be made paper-faithful — i.e. it is a heuristic with no clause behind it — still land it
behind a switch, default OFF, and say so; the seating measurement then decides whether the lead turns it on.

## Stage C — does it seat? (the only measure that counts)

- **C1 Pot A, no best-of-N**: >= 10 seeds with the rule on, our breaklines and our axes, floor 50, `NP` = 8.
  Report the count of seeds at 8/8 + 15/15 and, for any seed that misses, the piece and the join angles.
  Target 9 of 10 or better; a lower count is reported as the result with the blocker named.
- **C2 the sample pots**: pots A-J with arm `MM` (our breaklines + our axes) and the control in the same job
  (the authors' `Axes/` on our breaklines), >= 2 repeats, axes-only substitution proved by `diff -rq`. Report
  the table against ticket 308's numbers and **name every pot that got worse**.
- **C3 the corpus**: 163 pieces to new paths, `corpus_before.md5` == `corpus_after.md5` (652 paths) and
  `corpus.diff` empty, plus the tier table against 308 (84 of 163 within 5 deg, median 4.56 deg) and the
  per-piece line count under the rule.
- **C4 parity**: `python -m pytest tests/ -q` green, and ticket 302's MATLAB parity bar (relative tolerance
  <= 1e-9 on the unit checks) re-run if any cost or refine code changed.
- **C5** renders for any geometry claim, to `SfSpp_preprocessing/artifacts/pota310/`.

## Stage D — land it and write it down

- **D1** the diff, one commit, with its warrant; the switch and its default; nothing else touched.
- **D2** a dated entry in `intent/E1-do-our-breaklines-let-sfs-find-joins.md` above the 308 entry, plus a
  Where-it-stands bullet: the prevalence before and after, the seating count, the grid delta, and the one
  statistic that did the work (or the admission that none did).
- **D3** ticket Comments: the A/B/C tables, every job id with its `sacct -j <id> --format=State,ExitCode`,
  and an `runs/index.tsv` row per run with `verdict` and `human_note` left empty.

## Acceptance

- [ ] A1 per-line statistic table over >= 20 seeds (Piece 08 plus controls 01 and 04).
- [ ] A2 the separation table, naming the statistic(s) that separate or the proof that none does.
- [ ] A3 prevalence baseline over >= 20 seeds.
- [ ] A4 the structural tests (shortlist width, refine-then-rerank, 10x draws) with numbers.
- [ ] B1 the rule implemented with a one-line warrant per term, blindness stated.
- [ ] B2 prevalence with the rule on, >= 10 seeds, count reported against 10 of 10.
- [ ] B3 the 163-piece census and runtime under the rule; the switch and its default named.
- [ ] C1 Pot A >= 10 seeds, count of 8/8 + 15/15, no best-of-N, misses named by join and angle.
- [ ] C2 the A-J grid with the control in the same job, and every pot that got worse named.
- [ ] C3 corpus md5 unchanged, 163 pieces to new paths, tier table versus 308.
- [ ] C4 pytest green and the MATLAB parity bar re-run if cost or refine code changed.
- [ ] C5 renders to `artifacts/pota310/` for any geometry claim.
- [ ] D1-D3 the commit, the intent entry, and the job ids with sacct in Comments.

## Rules for the worker

- Read this ticket first, then `C:/PR/AGENTS.md`, `C:/PR/SfSpp_preprocessing/AGENTS.md`, and
  `intent/E1-do-our-breaklines-let-sfs-find-joins.md`.
- `C:/PR/scripts/ticket_start.sh SfSpp_preprocessing <.scratch/pota-repro/issues/310-....md>` first. If it
  refuses, stop and report instead of improvising a worktree.
- SSH is `/c/Windows/System32/OpenSSH/ssh.exe spartan`, and the whole remote command must be single-quoted.
- Heavy work on a compute node, never the login node.
- Runs as `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_<tag>/` with `run.json`,
  `submit.sbatch`, `logs/`, `out/`, and one row in `runs/index.tsv`.
- Reuse `.scratch/pota-repro/306-stage/`, `307-stage/`, `308-stage/` and `309-stage/` instruments first.
- The released `Axes/` files and the GT poses are for scoring and diagnosis ONLY. No shipped rule may read them
  and nothing may be fitted to them; the 'good axis' above is a diagnostic label, not a target to match.
- No corpus file changes. Ticket edits in Comments only. Commit nothing, push nothing.
- Budget: 8 failed acceptance checks. On the 8th, stop and report what is blocked.
- Report: the A1/A2 tables, the A3/A4 counts, the rule with its warrant, the B2 prevalence, the C1 seating
  count, the C2 delta table with NP per arm, the corpus md5 comparison, and every job id with its sacct line.
  State plainly which claim type it is — the method, the measurement, or the reference.
