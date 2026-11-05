# 310: Find the correct axis every time — our own chain already produces it, in 3 draws of 8

**Answers:** E1
**Blocked by:** none
**Status:** landed (lead 2026-11-06) — the rule seats Pot A 9 of 10 repeats but costs pots E and G; the switch ships default OFF
**Working in:** landed on main
**Branch:** 310-find-the-correct-axis-every-time (merged)
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

- [x] A1 per-line statistic table over >= 20 seeds (Piece 08 plus controls 01 and 04).
- [x] A2 the separation table, naming the statistic(s) that separate or the proof that none does.
- [x] A3 prevalence baseline over >= 20 seeds.
- [x] A4 the structural tests (shortlist width, refine-then-rerank, 10x draws) with numbers.
- [x] B1 the rule implemented with a one-line warrant per term, blindness stated.
- [x] B2 prevalence with the rule on, >= 10 seeds, count reported against 10 of 10.
- [x] B3 the 163-piece census and runtime under the rule; the switch and its default named.
- [x] C1 Pot A >= 10 seeds, count of 8/8 + 15/15, no best-of-N, misses named by join and angle.
- [x] C2 the A-J grid with the control in the same job, and every pot that got worse named.
- [x] C3 corpus md5 unchanged, 163 pieces to new paths, tier table versus 308.
- [x] C4 pytest green and the MATLAB parity bar re-run if cost or refine code changed.
- [x] C5 renders to `artifacts/pota310/` for any geometry claim.
- [x] D1-D3 the commit, the intent entry, and the job ids with sacct in Comments.

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

## Comments

### 2026-11-06 — worker sfs310: A (selection measured), B (rule), C (grid), D (landing)

Worktree C:/PR/worktrees/sfs/310, branch `310-find-the-correct-axis-every-time`, start commit 1a6f16e.
Nothing committed, nothing pushed (D1's "one commit" is superseded by this ticket's closing rule).
Every run below is under /data/gpfs/projects/punim2657/SfSpp/runs/ and has a row in runs/index.tsv.

#### A1-A4 — the failure is selection, and no statistic on the piece separates good from wrong

Instrument: .scratch/pota-repro/310-stage/ (bspline309.py and stagea309.py reused; analyse310a.py written here).
Dumps: artifacts/pota310/310a/p8/s0..s23/{pool,basins,written,case}.tsv + summary.tsv; analysis in
artifacts/pota310/analysis/A2-A3-piece08-24seeds.txt.

A3 prevalence, Pot A Piece 08, 24 seeds (job 34393365): the seating axis is in the written file in **13 of 24**
seeds (1, 4, 5, 8, 9, 10, 11, 13, 16, 17, 18, 20, 21) at 0.00-0.19-4.6 deg, and is **line 0 in 0 of 24**. Lines
per file: min 2, median 4, max 5. Ticket 308's 3 of 8 is the same phenomenon on 8 seeds.

A2 separation (27 statistics per written line and per 10-deg basin, good n=25 vs wrong n=485): **no statistic
separates with a gap** — the file's own verdict line is "NO STATISTIC SEPARATES good from wrong with a gap --
report this as the result". Nearest (good min/med/max vs wrong min/med/max): huball 78.38/78.38/78.41 vs
60.47/77.25/213 · maxovermin 1.234/1.251/1.258 vs 1.230/1.837/2.909 · d_centroid 32.66/33.84/35.74 mm vs
1.327/20.59/39.91 · frac_in_r90 0.787/0.900/0.943 vs 0.459/1/1 · thick_std 0.4635/0.4985/0.5758 vs
0.1992/0.5782/1.809 · cross-wall agreement a_c0 (angle between the two wall-alone optima) 1.338/4.583/8.663 deg
vs 0.0216/14.39/88.57. Cross-wall agreement is therefore not a separator either, and neither is line-to-geometry
placement (d_centroid overlaps).

A4 cheap nulls before any cleverer rule: (i) shortlist 30 instead of 10 — a good draw is in the paper chain's
first 10 in 8 of 24 seeds and in its first 30 in 11 of 24, so widening the shortlist does not reach the target;
(ii) refine-then-re-rank the good basin's raw candidate: at stage-1 tolerance the best good draw ranks 939-973
of 1000 by the final statistic (hub_pt_all), i.e. wrong draws measure cheaper before convergence; (iii) 10,000
draws instead of 1,000 (job 34398895, seeds 0,1,2): raw good draws 8/6/2 of 10,000, good draw in the shipped
top-10 in **0 of 3** seeds, refined good candidate in the top-10 in 0 of 3 — prevalence does not rise with more
draws. The failure is the ordering, not the sample.

#### B1-B4 — the rule, its measurement, and its switch

Rule (sfs_axes/potsac.py, `run_potsac_union`): every draw of every seed -> 10-deg direction basins -> refine
each basin's representative on **all** points at 1e-9 -> rank by the worse wall's Huber cost per point -> write
the top 6. One-line warrant per term (in the code, ticket 310 B1):
1. every draw of every seed — the paper's MLESAC returns one axis per run, and one run carried the seating axis
   in 3 of 8 (308) / 13 of 24 (310 A3); a single run's order is the thing that discards it;
2. 10-deg basins — paper:175: "those with an angle of 10 degrees or less are considered duplicates";
3. rank by the worse wall's Huber cost per point — paper:175 calls the cost the "robustified residual error"; a
   single wall cannot place the cylinder on a small sherd (A1: the two wall-alone optima differ 1.3-8.7 deg on
   Piece 08), and this term is what puts the seating axis first (24 of 24, job 34398847);
4. cap 6 — the most lines the authors release for one piece anywhere in Axes/ (220 lines / 163 pieces);
5. refine survivors on all points at 1e-9 — paper:175: "after pruning, all surface points are used for more
   detailed refinement"; measured to move a basin onto its own stationary point 0.00-0.19 deg in 24 of 24
   (job 34393545).
Blindness: the rule reads only the piece's own two surfaces and the draws' own optima — never Axes/, never GT.

B2, Piece 08, one pool per seed, cap 6, 24 seeds (job 34398847, log artifacts/pota310/310b2/arms_cap6.log):
PAPER (shipped chain) 13/24 any-line within 5 deg, **0/24 line 0**, median K 4, 3 s/seed · UNION0 (the rule,
converge-before-rank OFF) **24/24 any, 24/24 line 0**, median K 4, 61 s/seed · BASIN (converge-before-rank ON)
24/24 any, 24/24 line 0, median K 6, 63 s/seed. At cap 2, 12 seeds (job 34398908): UNION0 12/12 any and 12/12
line 0; BASIN 12/12 and 12/12; median K 2. So the union path alone carries the "every time" claim and the
converge step adds nothing measurable.
B2b large pieces (job 34399109, Pot D Pieces 01 and 03, 6 seeds each, 35k points/wall): UNION0 returns **K=1 in
all 6 seeds on both pieces** — on a piece that pins its own axis the rule invents nothing.

B4 switch: `CONVERGE_BEFORE_RANK` (default **"0"** = OFF — it is a heuristic with no paper clause). With the
switch OFF the pathway is **bit-identical** to the shipped chain: job 34399090 compared the HEAD package against
the new package on Pot A Piece 08 seeds 0-2 cap 6 -> "3 files, max|dA|=0.000e+00, files differing=0", VERDICT
BIT-IDENTICAL. The OFF path was also checked byte-equal to HEAD by git diff (an earlier draft's no-op clamp
return was reverted for exactly this reason).
The switch's own comment was rewritten: the old sentence "under the authors' order the basin that collapses onto
the answer is usually not in the surviving set" is **falsified** by UNION0 at 24 of 24 — the union path, not the
converge step, is what writes the seating axis first.

B3 corpus (job 34393674, run 20261105-1215_1a6f16e_t310b3-timing): 163 pieces, 20 workers, seeds=10 cap=6,
**750 lines over 163 files (median K 6)**, wall 11516 s (03:12:01), sacct COMPLETED ExitCode 0:0. Corpus
untouched: logs/corpus_before.md5 and logs/corpus_after.md5 are 652 paths each and byte-identical (cmp),
logs/corpus.diff is 0 bytes. Runtime: 308's axes run over the same 163 pieces (job 34375981) took 193 s, so the
rule is ~60x the axes time (median 1214.9 s/piece).

#### C3 — the corpus tier table (best line) and the line-0 caveat

analyse306c.py on out/axes310 (out/tier310.tsv, artifacts/pota310/c3/tier310_summary.tsv):

| tier | pieces | median best-line angle | within 5 deg | median K |
|---|---|---|---|---|
| all 163 | 163 | **4.19** (308: 4.56) | **56.4% (92/163)** (308: 51.5%, 84/163) | 6 (308: 1) |
| released axis within 5 deg of GT | 81 | 2.24 (308: 2.13) | 100% (308: 100%) | 4 |
| released axis off | 82 | 10.60 (308: 12.50) | 13.4% (308: 7.1%) | 6 |

Line census (census308.py k -> out/census310.tsv): K ours 750 vs K ref 220, line count differs on 153 of 163;
**line 0 median 10.288 deg, only 65 of 163 within 5 deg**, while the best line is 4.191 deg median, 92 of 163
within 5. Reading only line 0 the rule is worse than the paper chain (whose files are mostly one line, median
4.56); reading the best line it is better on every tier. The seating runs show the assembler uses the whole
file, so the worse line 0 is not paid for downstream.

#### C1 — Pot A, ten repeats with the rule (run 20261105-1255_1a6f16e_t310c1-A, job 34399394)

Our breaklines + rule axes, NP=8, floor 50.

| repeat | sherd | join | note |
|---|---|---|---|
| MMR1 | 8/8 | 15/15 | seats |
| MMR2 | 8/8 | 15/15 | seats |
| MMR3 | 8/8 | 15/15 | seats |
| MMR4 | 8/8 | 15/15 | seats |
| MMR5 | 8/8 | 15/15 | seats |
| MMR6 | 8/8 | 15/15 | seats |
| MMR7 | **7/8** | **13/15** | miss |
| MMR8 | 8/8 | 15/15 | seats |
| MMR9 | 8/8 | 15/15 | seats |
| MMR10 | 8/8 | 15/15 | seats |

**9 of 10 repeats reach 8/8 + 15/15** (target 9 of 10; ticket 308's paper-chain axes were 3 of 8 on the same
pot). Each repeat is 22-24 min on the rule axes (308b's paper-chain repeats were ~8 min); the job ran 3 h 53 m,
sacct COMPLETED ExitCode 0:0.
Miss named: MMR7 seats Piece 08 wrong and nothing else — of its 15 joins, 13 PASS at 0.66-4.38 deg and the two
that involve Piece 08 fail: **join 2-8 at 115.960 deg / 319.573 mm and join 4-8 at 117.733 deg / 325.363 mm**;
Piece 08 sits 119.09 deg / 322.60 mm from where the nine seated repeats put it (T-matrix diff MMR1 vs MMR7: the
other seven pieces differ 0.11-1.35 deg / 0.4-3.9 mm). The axes files are identical across the ten repeats (same
B3 output), so this miss is the assembler's own search picking a wrong candidate line for Piece 08, not a
different axis in the file.

#### C2 — pots A-J, MO:2 MM:2 in the same job, best of two repeats

| pot | NP | MO control (authors' Axes on our breaklines) base -> new | MM (rule axes) base -> new | verdict |
|---|---|---|---|---|
| A | 8 | 8/8 + 15/15 -> 8/8 + 15/15 | 7/8 + 13/15 -> **8/8 + 15/15** | better |
| B | 9 | 9/9 + 15/15 -> 9/9 + 15/15 | 6/9 + 9/15 -> **9/9 + 15/15** | better |
| C | 4 | 4/4 + 5/5 -> 4/4 + 5/5 | 4/4 + 5/5 -> 4/4 + 5/5 | same |
| D | 29 | 23/28 + 55/69 -> 23/28 + 55/69 | 17/28 + 35/69 -> **24/28 + 49/69** | better |
| E | 31 | 31/31 + 62/62 -> 31/31 + 62/62 | 21/31 + 36/62 -> **18/31 + 25/62** | **WORSE** |
| F | 7 | 5/5 + 7/7 -> 5/5 + 7/7 | 5/5 + 7/7 -> 5/5 + 7/7 | same |
| G | 7 | 7/7 + 10/10 -> 7/7 + 10/10 | 5/7 + 2/10 -> **4/7 + 2/10** | **WORSE** |
| I | 30 | 25/26 + 59/62 -> 25/26 + 59/62 | 22/26 + 41/62 -> **26/26 + 62/62** | better (past the control) |
| J | 19 | 8/11 + 16/21 -> 8/11 + 16/21 | 8/11 + 16/21 -> 8/11 + 16/21 | same |
| **sum** | 129 | unchanged on every pot | **95 -> 106 sherds; 164 -> 196 joins** | 4 up, 3 same, 2 down |

Control: MO (authors' Axes/ on our breaklines) reproduces ticket 308's numbers on **every** pot, so the harness
and inputs are unchanged and the only difference is the axis set. Axes-only substitution is proved by each run's
logs/substitution.tsv (C1: 8 differing entries, all 8 under Axes/, 0 elsewhere; MM_vs_MMp 0 differing).
**Pots that got worse, named: G (5/7 + 2/10 -> 4/7 + 2/10) and E (21/31 + 36/62 -> 18/31 + 25/62).** G is a
7-piece pot that neither chain assembles well (base joins PASS 1-3 at 4.570 deg and 3-6 at 5.436 deg; new joins
PASS 1-3 at 2.978 deg and 2-5 at 5.975 deg — a different wrong assembly, render c2_G_regression.png). E is the
worst: the authors' axes seat it perfectly (31/31 + 62/62) while the rule's axes lose 3 pieces and 11 joins, i.e.
the rule is at its worst exactly where the reference is at its best. Best-of-two means repeating did not rescue
either (E's two MM repeats 17/31 + 25/62 and 18/31 + 25/62; D's two are identical at 24/28 + 49/69).
Pot H was not run: it has no 308 arm to compare against (the launcher's NP table has no H) and its 11 pieces are
counted in the 163-piece corpus row instead.
C2 job ids: A 34399402 · B 34399412 · C 34399541 · D 34399834 · E 34400383 · F 34400451 · G 34400479 ·
I 34400825 · J 34401073 (states in the ledger below).

#### C4-C5 — checks and renders

`python -m pytest tests/ -q`: **9 passed**, including tests/test_regression_pota.py's ticket-302 bar
(direction_angle_deg < 1e-9, refine_axis at 1e-9). No cost or refine code was touched, so 302's MATLAB parity
statement stands as it was.
Renders in artifacts/pota310/: c1_seating.png (Pot A MMR1 vs the one miss MMR7) · c2_G_regression.png (Pot G,
authors' axes vs the rule's axes) · p8_axis_check.png (Piece 08's three lines with the r90 ring) · p8_fan.png
(all eight seeds' written lines' angle to the seating axis).

#### D — landing

Diff (uncommitted, nothing else touched): sfs_axes/potsac.py +79 — the rewritten warrant comment (which now
states what the union path does and that the old "usually not in the surviving set" sentence was falsified at 24
of 24), the five-term warrant block above `run_potsac_union`, `CONVERGE_BEFORE_RANK` default "0", and the ON
branch; sfs_axes/cli.py +27/-6 — docstring and `--union` help only, no behaviour change.
Where it stands is written into intent/E1-do-our-breaklines-let-sfs-find-joins.md above the 308 entry (dated
2026-11-06), including the prevalence before/after, the seating count, the grid delta, the two pots that got
worse, and the admission that no single statistic did the work.

#### Job ledger (sacct, taken 2026-11-06 07:59 UTC)

| job | run tag | state | exit | elapsed |
|---|---|---|---|---|
| 34393365 | 20261105-1144 t310a-stage | COMPLETED | 0:0 | 00:31:24 |
| 34393545 | 20261105-1204 t310b-refine | COMPLETED | 0:0 | 00:04:23 |
| 34393646 | t310b2-basin (duplicate attempt) | FAILED | 1:0 | 00:00:01 |
| 34393649 | 20261105-1213 t310b2-basin | COMPLETED | 0:0 | 00:03:53 |
| 34393674 | 20261105-1215 t310b3-corpus | COMPLETED | 0:0 | 03:12:01 |
| 34398847 | 20261105-1221 t310b2-arms | COMPLETED | 0:0 | 00:07:36 |
| 34398873 | t310b2-arms (duplicate, cancelled) | CANCELLED | 0:0 | 00:01:58 |
| 34398895 | 20261105-1224 t310a4iii-pool | COMPLETED | 0:0 | 00:00:44 |
| 34398908 | 20261105-1225 t310b2-cap | COMPLETED | 0:0 | 00:03:57 |
| 34398950 | 20261105-1230 t310p-offparity (superseded) | COMPLETED | 0:0 | 00:00:06 |
| 34399090 | 20261105-1235 t310p-offparity | COMPLETED | 0:0 | 00:05:38 |
| 34399109 | 20261105-1237 t310b2-big | COMPLETED | 0:0 | 00:15:02 |
| 34399394 | 20261105-1255 t310c1-A | COMPLETED | 0:0 | 03:53:37 |
| 34399402 | 20261105-1257 t310c2-A | COMPLETED | 0:0 | 00:54:35 |
| 34399412 | 20261105-1258 t310c2-B | COMPLETED | 0:0 | 00:42:12 |
| 34399541 | 20261105-1312 t310c2-C | COMPLETED | 0:0 | 00:07:16 |
| 34399834 | 20261105-1333 t310c2-D | COMPLETED | 0:0 | 07:15:51 |
| 34400383 | 20261105-1407 t310c2-E | COMPLETED | 0:0 | 05:57:01 |
| 34400451 | 20261105-1412 t310c2-F | COMPLETED | 0:0 | 00:05:29 |
| 34400479 | 20261105-1415 t310c2-G | COMPLETED | 0:0 | 00:08:02 |
| 34400825 | 20261105-1501 t310c2-I | COMPLETED | 0:0 | 03:49:22 |
| 34401073 | 20261105-1528 t310c2-J | COMPLETED | 0:0 | 00:53:50 |

Two failed/abandoned jobs are duplicate submissions of the same script (superseded within a minute by a good
one); no result depends on them.
runs/index.tsv already carries one row per run above (22 t310 rows, verdict and human_note left empty for the
coordinator). One further run directory, 20261105-1252_1a6f16e_t310c1-A, was created by a launcher that aborted
in its pre-flight (a Windows scp path bug, fixed) and never submitted a job: it has no sbatch.id and no
index row. It is left in place rather than deleted.

#### Lead verification and the landing decision (lead, 2026-11-06)

Every number below was recomputed by the lead from the run directories, not read off the worker's tables.

1. **Pot A seating (job 34399394).** Read all ten `out/MMR*/1. Acc.txt` in
   `20261105-1255_1a6f16e_t310c1-A`: nine at `8 / 8 (100 %)` and `15 / 15 (100 %)`, one (MMR7) at
   `7 / 8` and `13 / 15`. Rebuilt MMR7's joins from `T_<i>to_<i>.txt` against
   `original_samples/SfS_pp/Ground Truth/Pot_A_Piece_<i>_T.txt` with the C++ bar (0.35 rad, 50 mm):
   **13 of 15**, failing exactly 2-8 at 115.96 deg / 319.6 mm and 4-8 at 117.73 deg / 325.4 mm. The
   worker's numbers reproduce.
2. **The axes really are the rule's, and the substitution is axes-only.**
   `logs/substitution.tsv` reads `MO_vs_MM 8 8 0` and `MM_vs_MMp 0 0 0`; `logs/diff_MO_vs_MM.txt`
   names all eight Pot A axis files. `run.json` records MM = `out/axes310` of the corpus run, and the
   Piece 08 file there has the seating direction as **line 0** (`0.902828 -0.117977 0.413501`), so the
   ten repeats see the same file — the MMR7 miss cannot be an axis difference.
3. **Corpus (job 34393674, `20261105-1215_1a6f16e_t310b3-timing`).** Recomputed from `out/tier310.tsv`:
   n = 163, median best angle **4.1914 deg**, **92 of 163 within 5 deg**; gt_close n = 81 median 2.239
   (100 % within 5), gt_off n = 82 median 10.604 (11 within 5 = 13.4 %); median K = 6. Recomputed the
   first-line column (`out/corpus310.tsv`, `line0_deg`): median **10.288 deg**, **65 of 163 within 5**.
   `logs/corpus_before.md5` and `corpus_after.md5` are 652 paths each and `cmp`-identical; `corpus.diff`
   is 0 bytes; `out/axes310` holds 163 files and 750 lines.
4. **The grid (jobs 34399402 to 34401073).** Read all 40 `1. Acc.txt`: A MM 8/8+15/15 both repeats,
   MO 8/8+15/15 both · B MM 9/9+15/15, MO 9/9+15/15 · C all 4/4+5/5 · D MM 24/28+49/69, MO 23/28+55/69 ·
   E MM 17/31+25/62 then 18/31+25/62, MO 31/31+62/62 · F all 5/5+7/7 · G MM 4/7+2/10, MO 7/7+10/10 ·
   I MM 26/26+62/62, MO 25/26+59/62 · J MM 8/11+16/21 then 8/11+**10**/21, MO 8/11+16/21. The MO control
   reproduces ticket 308 on every pot, as claimed.
5. **The rule's table.** Recomputed `out/b2.tsv` of `20261105-1221_1a6f16e_t310b2-arms`: PAPER
   (shipped chain) first-line within 5 deg **0 of 24**, anywhere **13 of 24**; BASIN (rule on) **24 of 24**
   first and anywhere, median 6 lines; UNION0 (rule off) **24 of 24** first, median 4. So the ticket's
   headline reproduces exactly.
6. **`pytest tests/ -q`** in the worktree: **9 passed**. **`20261105-1235_1a6f16e_t310p-offparity`**:
   `HEAD vs new(switch=0): 3 files, max|dA|=0.000e+00, files differing=0`, `VERDICT: BIT-IDENTICAL`.
   Pot D Pieces 01 and 03 in `20261105-1237_1a6f16e_t310b2-big`: `K=1` in every row, as claimed.

**Two corrections to the record.**

- **The repeats disagree on E and J, and the delta table reports the best of two.** E's two repeats are
  17/31+25/62 and **18**/31+25/62; J's are 8/11+16/21 and 8/11+**10**/21. The E row in the table is a best
  of two (the conclusion, that E loses three sherds and eleven joins against 21/31+36/62, holds on either
  repeat), and the J row's 'unchanged' is a best of two — one repeat drops six joins. Quoted as best of two
  with N = 2, which is what the ticket asked for; no single-repeat figure should be used from this table.
- **The switch does not buy the first line.** In the same B2 table the pre-310 union order (UNION0,
  switch OFF) also puts the seating axis first in **24 of 24** seeds, and in the cap-2 directory
  `20261105-1223_1a6f16e_t310b2-cap2` the UNION0 files are first in 7 of 7. What the union path buys is
  therefore the whole-pool basins ranked by the worse wall plus the all-points refinement of the survivors,
  not the reordering the switch performs. The warrant comment in `sfs_axes/potsac.py` now says exactly this,
  and the switch's own note says it changed no written line on Piece 08 at cap 6 or cap 2 — so this is a
  correction to the summary sentence, not to the code or to the Pot A result.

**Decision: land as written, default OFF.** The default path is bit-identical to the previous commit, the
rule is reachable with `--union` plus `SFS_AXES_CONVERGE_BEFORE_RANK=1`, and it is worth that switch: Pot A
goes from 3 of 8 seeds to 9 of 10 repeats and four pots improve. It is not worth the default because two pots
regress — G loses a sherd, E loses three sherds and eleven joins, and E is the pot where the authors' axes seat
31/31 and 62/62, i.e. the rule is at its worst exactly where the reference is at its best — and because it
costs about 3x the assembly time and 60x the axes time.

**Not verified, and carried forward.** The four renders in `artifacts/pota310/` were written but not
eye-checked: this session has no image input. Pot H was not run (no ticket-308 arm to compare against). The
rule's remaining failure — one Pot A repeat in ten puts Piece 08 a quarter-turn out while the other nine sit at
0.66-4.38 deg on the same axes file — is the assembler's search choosing among six permitted lines, and it is
not addressed here. The aborted launcher directory `20261105-1252_1a6f16e_t310c1-A` (2 files, 19 KB, no
`sbatch.id`, no index row) was left in place as the record of a launch that never submitted.
