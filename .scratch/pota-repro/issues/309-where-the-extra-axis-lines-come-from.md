# 309: Where do the authors' extra axis lines come from?

**Answers:** E1
**Blocked by:** none
**Status:** wontfix (lead 2026-11-05) — superseded by ticket 310; this ticket's premise was the lead's mis-framing
**Working in:** chat on Thinkbook16 (2026-11-05)
**Branch:** 309-where-the-extra-axis-lines-come-from, in /c/PR/worktrees/sfs/309
**Worker:** sfs309
**Budget:** large 8
**Hand-over:** Claude (Spartan compute node, MATLAB, assembler E2E)

## What to build

Answer one question with measurement, then act on the answer:

> **On the 13 pieces where the released `Axes/` files carry MORE lines than ours, where do those extra
> lines come from — are they stationary points of the cost on a surface set we do not have, or are they
> in a pool our sampler never proposes?**

and the follow-up that decides whether it matters: **does having them change seating on the sample pots?**

### Why this ticket, in one paragraph

Ticket 308 left the sample pots at 7/8 + 13/15 (Pot A, paper axis set) with the authors' axes on the same
breaklines at 8/8 + 15/15. The line-count story has FLIPPED since ticket 305: over all 163 pieces ours now
writes **238** lines against the released **220** — more on 30 pieces, equal on 120, and fewer on only 13.
So 'the authors have more lines' is no longer true in general; it is true on a named 13, and one of them is
Pot A 07 — the piece whose missing third line ticket 306 already showed is in no candidate pool we generate
(nearest draw 8.55 deg away). This ticket finds out what generates those 13 lines, because if it is an input
we are not reproducing, no amount of tuning our sampler will ever produce them.

### The census this ticket starts from (ticket 307 default, `SFS_AXES_COST_PRUNE=0`, no equal-count cut)

`runs/20261105-0406_e6adf69_t307a-axes/out/census_b1.tsv` — ours = `out/axes_b1`, released = the authors'
`Axes/`. Pieces where **released > ours** (13):

| piece | ours | released |
|---|---|---|
| Pot_A_07 | 2 | 3 |
| Pot_D_17 | 1 | 2 |
| Pot_D_24 | 3 | 4 |
| Pot_D_30 | 3 | 5 |
| Pot_E_21 | 1 | 2 |
| Pot_E_31 | 2 | 3 |
| Pot_E_34 | 2 | 3 |
| Pot_F_07 | 2 | 3 |
| Pot_H_06 | 1 | 3 |
| Pot_H_09 | 2 | 6 |
| Pot_J_11 | 1 | 3 |
| Pot_J_13 | 1 | 3 |
| Pot_J_14 | 1 | 5 |

Per pot, ours / released: A 12/11 · B 16/10 · C 10/7 · D 45/45 · E 38/41 · F 10/9 · G 7/7 · H 23/24 ·
I 40/33 · J 37/33. **Pot A 07 is the only sample-pot piece in the list that matters for Pot A seating.**
(The other Pot A differences are ours-more: A06 2/1, A08 3/2.)

### What is already excluded, so do not re-measure it

1. **The 1.1 cost prune is not it.** `sfs_axes/potsac.py:145` `keep = cost < cost[0] * 1.1` is off by
   default since ticket 307 (`SFS_AXES_COST_PRUNE=0`). With it off we emit 238 lines against their 220 —
   the prune only ever deletes lines, so it cannot be why they have more.
2. **The equal-count cut is not it, on the whole corpus.** Off by default since ticket 306. On Pot A 08 the
   cut changes the basin structure (ticket 304: refine from the released line gives 5.2280 deg on the full
   cloud and 88.15 deg on the cut cloud), so keep the switch in the matrix for the 13, but do not expect it
   to add lines anywhere else.
3. **The step rule is not it for Pot A 07.** `Pot_A_07` has n = 3,490 points, under 5,000, so both the
   authors' rule (`run_potsac.m:18-20`, ff40fc9) and ours (`potsac.py` `effective_step`) use step = 1. It IS
   a candidate for the bigger pieces in the list — check each piece's n before ruling it out.
4. **More lines is not automatically better.** Ticket 306 measured that giving Pot A 07 a second line
   collapses the assembly from 7/8 + 12/15 to 4/8 + 5/15 — with our line, with the authors' released line 1
   verbatim, and with their whole three-line file. So this ticket must never report 'line count improved' as
   success. Seating is the only measure.

## Stage A — is each released line a stationary point of some surface set we can build? (no E2E)

For each of the 13 pieces, for **each** released line (point p, direction d):

- **A1 stationarity.** For each surface variant V below, run the port's own LM refine starting FROM (p, d)
  on V's points and report the angle and the point offset between the start and the refined optimum, plus
  the cost at the start and at the optimum. A released line that IS a stationary point of V stays put
  (ticket 302 measured the port agreeing with MATLAB to 1e-4 deg on genuine ones, so 'stays put' means
  <= 0.5 deg); a line that is not a minimum drifts away, and the drift is the evidence.
  Report per line: `IN` (stays within 0.5 deg) or `OUT` (drifts, with the drift in deg).
- **A2 Pottmann residual.** For the same (p, d) on each V, measure how far the pair is from satisfying the
  symmetry constraint the sampler uses (`sfs_axes/pottmann.py`, `compute_pottmann_axis`), i.e. the smallest
  singular value relative to the largest over V's points. This says whether the line is even admissible
  under the method's own constraint on that surface set.
- **A3 provenance of each line's cost.** Report the robustified per-point cost (ticket 302's per-point form)
  at each released line on each V, normalised per point, and compare with the cost at our own best line on
  the same V. If a released line is cheaper than ours on V, our search should have found it and did not.

The variants, all on the pieces' own surfaces (never on anything derived from the released axis file):

- **V1** the shipped `Surface_0`/`Surface_1` xyz, equal-count cut OFF (our default).
- **V2** the same surfaces, cut ON (`--truncate`), since the authors' `read_surfaces.m:34-37` equalises.
- **V3** the B-spline resampled surfaces the paper describes at `papers/text/sfspp-2502.13986v1.md:155`
  ('B-Spline fitting is performed for each cluster to refine surface boundaries and uniformly sample the
  point cloud'). The workspace has its own NURBS path (`AxisExtraction/extract_axis_nurbs.m`,
  `read_surfaces_nurbs.m`, added by commit c358220 — OURS, not the authors'; do not call it theirs). If the
  resampled surfaces for these 13 pieces are not on disk, regenerate them, record their md5s and point
  counts, and treat V3 as unavailable if the generator cannot be made to run — say so rather than guessing.

Deliverable A4: a table, one row per released line (13 pieces, 44 lines total), columns: piece, line index,
V1, V2, V3 verdicts (`IN`/`OUT (xx.x deg)`/`n/a`), Pottmann residual per V, and one line of interpretation.

## Stage B — does our sampler ever propose them on the variants where they are stationary?

For the lines that came back `IN` on any V: dump the **pre-dedup** candidate pool on that V (the 1,000 draws
before `_dedup`, exactly as ticket 306 Stage A did), cluster at 10 deg, and report for the nearest cluster:
cluster size, rank by cost, cost ratio to the best cluster, and the angle to the released line.

Two outcomes and they mean different things — state which one holds, per line:

- **proposed but deleted** (cluster exists, rank > 10 or cost ratio > 1.1): a shortlist rule problem, which
  ticket 307 already removed for the cost prune; if it is still happening, say which rule does it.
- **never proposed** (no cluster within 10 deg, or only single draws like ticket 306's 8.55 deg): the sampler
  does not reach that basin from these points, and the cause is upstream of the shortlist.

## Stage C — the authors' own chain as the arbiter

Run the authors' MATLAB `AxisExtraction/run_potsac.m` (as shipped, title-cased provenance recorded with
`git log --format='%h|%an|%ad|%s' -- <file>` first, since that file carries local fixes) on the 13 pieces,
on V1 and V2, at the authors' step rule, and report for each piece: how many lines it returns, and the angle
from each returned line to each released line.

This is the decisive measurement. Three possible verdicts, and the ticket must name the one that holds:

- **MATLAB returns the released extra lines too** — then the released files ARE reproducible on the shipped
  surfaces and our port differs from the `.m` somewhere Stage A will have localised. That is a port bug.
- **MATLAB does not return them** — then the released files were made on a surface set that is not in the
  repo (their `read_surfaces.m:15` reads a working copy, `D:/SFS_BB_temp/Plt_A`), the reference was made with
  data we do not have, and no tuning of our chain can reproduce those lines. Say so plainly; that is claim
  type (3) and it does not license explaining away seating misses.
- **MATLAB returns them only on V3** — then the paper's B-spline step is what generates them, and adopting
  it is paper-derived rather than fitted.

## Stage D — does the difference change seating on the sample pots?

One job, axes-only substitution proved by `diff -rq` (the only files that may differ are under `Axes/`),
`NP` quoted with every number, >= 3 seeds, no best-of-N unless stated with N:

- **D1 Pot A** at the 307 default (paper set): our set as-is (2 lines on Piece 07) vs ours with the released
  third line added to Piece 07 only vs the released Pot A files. Report sherds and joins per seed.
- **D2 the pots the 13 belong to**, at least D, E, F, H, J: our set vs our set with the missing released lines
  substituted for those pieces only. Report the 305/308 style table (sherds + joins, best of the repeats,
  N stated) and name any pot that moves.
- **D3 the honest null**: if adding the lines makes no pot better, say so. Ticket 306 already found that one
  extra line on Pot A 07 makes the assembly worse, so a null here is the expected result and is still the
  answer the ticket exists to get.

## Stage E — land it, or land the finding

- **E1** if the answer is a port deviation from the `.m`: fix it, keep it behind the paper-faithful default,
  and prove no regression (E2 below).
- **E2** if the answer is 'the released lines are not reproducible from the shipped data': ship nothing. Write
  the finding into `intent/E1-do-our-breaklines-let-sfs-find-joins.md` (dated entry above the 308 entry plus
  a Where-it-stands bullet), and state in the ticket exactly what would be needed to settle it.
- **E3** if the answer is V3 (B-spline resampling): do not ship it on this ticket's evidence alone — report
  the runtime cost for 163 pieces and the seating delta, and let the lead decide.

## Acceptance

- [ ] A1 the 44-line stationarity table (V1/V2/V3, with `IN`/`OUT (deg)` per line).
- [ ] A2 the Pottmann residual per line per variant.
- [ ] A3 cost per point at each released line vs our best line, per variant.
- [ ] A4 one sentence naming which variant explains each of the 13 pieces, and the ones it does not.
- [ ] B1 the pre-dedup cluster table for every `IN` line, with 'proposed but deleted' vs 'never proposed'.
- [ ] C1 the MATLAB arbiter run: per piece K and the angle to each released line, on V1 and V2.
- [ ] C2 the verdict named as one of the three in Stage C, with the measurement behind it.
- [ ] D1 Pot A sherds+joins at >= 3 seeds for the three axis sets, NP quoted.
- [ ] D2 the D/E/F/H/J table for Stage D2, with repeats and N stated.
- [ ] E1-E3 the landing decision executed, `python -m pytest tests/ -q` green, and ticket 302's MATLAB
      parity bar (rel tol <= 1e-9 on the unit checks) re-run if any cost or refine code was touched.
- [ ] Corpus unchanged: `logs/corpus_before.md5` == `logs/corpus_after.md5`, 652 paths, `corpus.diff` 0
      bytes. New axis output to NEW paths, never over `Axes/`.
- [ ] Every job has its `sacct -j <id> --format=State,ExitCode` in Comments and an `runs/index.tsv` row
      (`verdict` and `human_note` left empty).
- [ ] Renders for any geometry claim, to `SfSpp_preprocessing/artifacts/pota309/`.

## Rules for the worker

- Read this ticket first, then `C:/PR/AGENTS.md` and `C:/PR/SfSpp_preprocessing/AGENTS.md`, then
  `intent/E1-do-our-breaklines-let-sfs-find-joins.md`.
- `C:/PR/scripts/ticket_start.sh SfSpp_preprocessing <.scratch/pota-repro/issues/309-....md>` first. If it
  refuses, stop and report instead of improvising a worktree.
- SSH is `/c/Windows/System32/OpenSSH/ssh.exe spartan`, and the whole remote command must be single-quoted.
- Heavy work on a compute node, never the login node; MATLAB only on a compute node.
- Runs as `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_<tag>/` with `run.json`,
  `submit.sbatch`, `logs/`, `out/`, plus a row in `runs/index.tsv`.
- Reuse the instruments in `.scratch/pota-repro/306-stage/`, `307-stage/` and `308-stage/` before writing new
  ones; label every arm with `NP` and with which axis files it used.
- The released `Axes/` files and the GT poses may be read ONLY to score and diagnose. They may never enter
  a shipped selection rule, and nothing may be fitted to them.
- No corpus file changes. Ticket edits in Comments only. Commit nothing, push nothing.
- Budget: 8 failed acceptance checks. On the 8th failure, stop and report what is blocked.
- Report: the Stage A/B tables, the Stage C verdict with its measurement, the Stage D tables with NP, the
  exact diff with its paper or `.m` warrant, the corpus md5, and every job id with its sacct line.

## Comments

### Lead, 2026-11-05 — superseded before any measurement was reported

This ticket was dispatched and stopped the same evening, at the conservator's direction, because its premise was
wrong in a way that changes what the next ticket must measure. Recording it rather than deleting it.

**What the ticket assumed.** That the gap between our axes and the authors' on the sample pots is partly a
missing-candidate problem, because the authors' files carry more lines on 13 of 163 pieces.

**What is actually true, measured by the lead on the ticket-308 run
`runs/20261105-0532_d330469_t308a-axes/out/pota/paper_s0..s7`:** our own chain already produces the correct
Pot A axis, and Pot A seats 8/8 + 15/15 whenever it does. Per seed, the angle from each line in
`Pot_A_Piece_08_Axis.xyz` to the good axis (direction from ticket 304's step-1 file, 5.23 deg from the
released line 1), and the seed's seating result:

| seed | Piece 08 lines, deg from the good axis | seated |
|---|---|---|
| 0 | 68.77, 89.36, 38.28 | 13/15 |
| 1 | 68.77, 48.85, 89.36, **0.19**, 30.41 | **15/15** |
| 2 | 68.77, 89.36, 33.56 | 13/15 |
| 3 | 48.85, 89.36, 38.28, 26.01 | 13/15 |
| 4 | 68.77, 89.36, 43.23, **0.00** | **15/15** |
| 5 | 68.77, 48.85, 89.36, **0.00** | **15/15** |
| 6 | 48.85, 89.36, 26.01 | 13/15 |
| 7 | 68.77, 48.85 | 13/15 |

The three seating seeds are exactly the three whose file contains the good line, and in those seeds the file
carries 4-5 lines including three wrong ones — MORE than the authors' 2 — and still seats 15/15. So on this
piece extra lines are not the problem, a missing correct line is, and the correct line is our own product:
ticket 304 recovered it with our code at step 1 with the equal-count cut off.

**So the question is not where the authors' extra lines come from. It is why our own sampler finds the correct
axis in 3 draws in 8 and not in the other 5** — a selection problem inside our own output, which is what
ticket 310 measures.

### What this ticket did before it stopped

- Worker `sfs309` was stopped after ~10 minutes, at the conservator's direction, with no measurement reported.
- It had submitted exactly one Slurm job, **34393029** (`t309a-axes`, Stage A stationarity with a B-spline
  resample). The lead cancelled it: `sacct -j 34393029` -> `CANCELLED+ 0:0`, elapsed `00:01:08`
  (`batch` CANCELLED 0:15, `extern` COMPLETED 0:0). No result was used from it.
- Its instruments were kept because they are reusable: `.scratch/pota-repro/309-stage/` holds
  `bspline309.py` (B-spline resampling of a piece's two surfaces) and `stagea309.py` (refine-from-a-given-line
  stationarity harness), plus `submit309a.sbatch`/`.sh`.
- Nothing was landed and no corpus file was touched.
