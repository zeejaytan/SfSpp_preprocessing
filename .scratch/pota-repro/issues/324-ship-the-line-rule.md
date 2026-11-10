# Ticket 324 — Ship the 1.2x line rule in `sfs_axes`, so the axis writer produces axes323 by itself

**Status:** resolved (2026-11-10)
**Answers:** E1
**Depends on:** 323 (the rule and the set that proved it), 322 (the profile cost it is built on)
**Blocks:** none
**Worker:** cursor_code (dispatched 2026-11-10, model grok-4.7); verified and landed by the lead
**Budget:** medium

> **In one line.** Ticket 323 showed that handing the assembler fewer, better lines holds all ten pots
> at floor at once, but the rule lives only in `.scratch/pota-repro/t323/build_axes323.py` — a post-filter
> over a directory someone else built. This ticket moves the ranking and the rule into `sfs_axes` itself,
> so a plain run of the shipped axis writer produces that set, and proves it by reproducing the proven
> bytes or by re-running the assembly.

## What was proven (do not re-derive; the numbers are in ticket 323)

Rule: each piece keeps its profile-ranked **first** line, plus every later candidate line whose profile
cost (mean wall thickness, `sfs_axes/profile.py`) is at most **1.2x** that piece's own first-line cost,
capped at **3** lines. Ratio only — no millimetres, no per-pot constant.

End-to-end, twenty of twenty runs at or above floor; the authors'-axes control beaten on D (26/28 63/69
against 23/28 55/69) and H (11/11 17/17 against 8-10/11, 9-10/17) and tied on the other eight. Pot E
31/31 62/62 twice (three lines gave 20-29/31; one line gave 26/31).

The set that did it: `/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0740_d628fc0_t323-axes/out/axes323`
(172 files, 251 lines total). Its parent: `.../20261110-0415_d628fc0_t322-axes/out/axes322` (181 files,
865 lines) and the ranking behind it, `.../t322-axes/out/profile_rank.json`.

**axes323 is a pure deletion from axes322**: line 1 identical on 172 of 172 pieces, all 251 kept lines
present verbatim, 248 dropped, nothing re-estimated or re-ranked (ticket 323, checkpoint 13, re-checked
by the lead).

## The seam (this is where the code has to go)

- `sfs_axes/profile.py` already has the cost (`wall_thickness`, `profile_cost`) and the refinement
  (`refine_axis_profile`), and its docstring ends "Not called by run_potsac or run_potsac_union: no
  shipped path ranks by this cost." That sentence is the thing this ticket deletes.
- The production axis writer is `scripts/run_benchmark_172.py:73` —
  `ps.run_potsac_union(C0, C1, seeds=..., step=step, max_candidates=cap, normalized=True)` — which is
  what wrote axes318/axes320/axes322. The CLI path is `sfs_axes/cli.py:62` (the `--union` branch of
  `extract_piece`). Both write whatever `run_potsac_union` returns, unranked by profile.
- The ticket-322 ranking that axes322 came from is `.scratch/pota-repro/t322/profile_rank.py`: for every
  basin (raw and normal-cost refinement), cost each wall by profile thickness, average the two walls,
  15-degree dedup, Nelder-Mead refine the top `--refine-k` (8) on the same cost, re-score, 15-degree
  dedup, sort. Read it; it is the specification, not a sketch.

## What to build

1. **A shipped ranking and selection API** in `sfs_axes` — new module (e.g. `sfs_axes/select.py`) or an
   extension of `profile.py`, your call, but it must be importable and tested, not a script:
   - `rank_by_profile(vt, walls, centre, size, refine_k=8, dedup_deg=15.0)` → the candidates reordered and
     refined exactly as `profile_rank.py` does it, and **the per-line costs it used** returned alongside.
     Return the costs: the rule below needs them, and a caller must be able to check the ratio itself.
   - `keep_lines(costs, tau=1.2, kmax=3)` → the indices to keep, pure arithmetic, no I/O.
   - One entry point that does both over a `run_potsac_union` result, so callers do not have to know the
     order of the steps.
2. **Wire it into both writers**: `scripts/run_benchmark_172.py` (line 73) and the `--union` path of
   `sfs_axes/cli.py` (line 62). The rule is the **default** there; keep an explicit switch to the old
   behaviour (`--no-line-rule` / `SFS_AXES_LINE_RULE=0`, your call) so the previous output stays
   reproducible. Say in the ticket which switch you chose and why.
3. **Do not touch the paper chain** (`paper_chain=True`, `run_potsac`): it is the MATLAB-faithful path and
   its output is the reference this work is measured against. The rule applies to the union path only.
4. **Unit tests** in `tests/` for `keep_lines`: costs at 1.19x and 1.21x the first, a cap of three against
   a cheaper fourth, one line only, all-equal costs, and a first line already worst (must still keep line
   1 — the rule never drops the first line). Plus one test that the selection never returns an index that
   was not offered.

## Acceptance — the ladder, in this order

1. **Unit tests pass**, and the rest of `tests/` still passes.
2. **Byte identity to the proven set.** Run the shipped path on the 172 pieces and compare with
   `axes323` above: the acceptance is `cmp` on all 172 files. Report the count, the per-pot line means,
   and any file that differs with the differing line.
   - **If all 172 are identical**, the merge is done and no assembly job is needed — the bytes that scored
     20 of 20 are the bytes the shipped code now writes. Say so plainly.
   - **If any file differs**, the identity claim fails and the merge is not proven. Then (and only then)
     run the ten-pot end-to-end from the shipped output, two repeats, the same arms and floors as ticket
     323, and report it as a new run with its own job IDs. A file that differs because the candidate pool
     differs is a finding, not a rounding error: name which candidates entered or left.
3. **The old behaviour still works**: with the switch off, reproduce `axes322` byte for byte on the pieces
   you have time to check (at least one pot, all its pieces) — the point is that nothing silently changed
   for anyone still asking for the old set.
4. **Nothing else changes**: no corpus file written (the jobs print `CORPUS-UNCHANGED`), no change to the
   paper chain's output, `git status` clean of stray files, CRLF not introduced into any file you edited
   (ticket 322 hit this: a CRLF rewrite made a 31-line diff look like 390).

## Constraints

- **Spartan compute nodes only** for the 172-piece run; `apptainer` needs its full path on compute nodes
  (`/usr/local/bin/apptainer` or whatever `t323/make_e2e_323.sh` uses — read it, tickets 323 and 322 both
  lost a job to that).
- **The corpus never changes.** `Dataset/` and `original_samples/` are read-only inputs.
- **Two repeats** for any assembly you run; the assembler is not deterministic on identical input, so one
  repeat is not a result.
- **One code path.** No per-pot tables, no thresholds in millimetres, no special cases for the Juglet or
  for base pieces. If the rule needs an exception to reproduce the set, the exception is a finding: report
  it and stop.
- **No commits.** The lead reviews and commits. Leave the tree with your changes in place and `git status`
  readable.
- Keep any run directories, scripts and sbatch files you create inside `.scratch/pota-repro/t324/`.

## Hand-over

Report back with: the API you shipped and where it is called from (file:line), the switch name, the unit
test names, the 172-file identity count, and — if you had to run an assembly — job IDs with their final
`sacct` State and ExitCode. If identity failed, lead with that, with the file that differs.

## Comments

### 2026-11-10 12:05 - worker: API in, identity run submitted

- API: `sfs_axes/select.py` - `rank_by_profile` (:55), `keep_lines` (:79), `select_union_lines` (:92);
  `run_potsac_union(..., line_rule=None)` (`sfs_axes/potsac.py:420`, calls it at :479).
  Call sites: `scripts/run_benchmark_172.py:73`, `sfs_axes/cli.py:66` (`--union`).
- Switch: rule on by default; off with `SFS_AXES_LINE_RULE=0` or `--no-line-rule` (both writers). Both, because
  the env var matches every other `SFS_AXES_*` switch in potsac.py and the flag is what a person reading
  `--help` finds. The ticket 313-320 branch is kept behind `SFS_AXES_UNION_RANKER=normal` (axes318/320 only).
- Tests: `tests/test_select.py`, 10 tests; `pytest tests` 33 passed (laptop).
- Basin set: same as `t322/dump_basins.py` (10 seeds x 1000 draws, step 10, `_cluster_union`, 60 most-drawn,
  Cr at 12 000 points; `basins_all.json` holds 60 basins on 171/172 pieces). The offline normal refinement's
  `--iters` is unrecorded (default 40; shipped 60), and the axes323 cut used `profile_rank.json` costs, not
  in-run ones. Five pieces sit within 0.015 of 1.2 there (H 11 1.201, J 08 1.198, I 30 1.204, D 18 1.188,
  D 21 1.213): a flip on any of them fails identity.
- Identity run: job **34636308**, run `/data/gpfs/projects/punim2657/SfSpp/runs/20261110-1202_e94d8fb_t324-axes`
  (`submit.sbatch` = `t324/submit_axes324.sbatch`). Pass 1 rule on -> `out/axes324`, cmp vs axes323
  (`out/cmp_axes323.txt`); pass 2 `--no-line-rule` -> `out/axes324_off`, cmp vs axes322 on all pots
  (`out/cmp_axes322.txt`); `CORPUS-UNCHANGED` by listing before/after. Code staged in `impl/`: every module
  byte-equal to axes322's `impl/` except cli.py, potsac.py, profile.py (this ticket) and the new select.py.
  sacct: pending.

### 2026-11-10 12:25 - lead: identity verified independently; ticket closed

Verified by the lead from the run's own files, not from the worker's cmp output:

- Job **34636308** COMPLETED 0:0 in 00:08:17 (`sacct -j 34636308`).
- `diff -rq out/axes324 <axes323>` -> **0 files differ**, 9 "only in" (the legacy
  `Pot_JUGLET_Piece_NN_Axis.xyz` names axes323 did not write). A per-file `cmp` loop over all 172
  axes323 names printed no BAD line. Line totals 264 vs 251; the 13 extra are in the 9 JUGLET files.
- `diff -rq out/axes324_off <axes322>` -> **no output at all**: 181 files identical.
- So the shipped path reproduces BOTH proven sets byte for byte, ladder step (2) is met and **no assembly
  job is needed**. The log prints `CORPUS-UNCHANGED`; its own scoring table is 137/172, 149/172, 154/172.
- Code read by the lead: 5 tracked files, 58 insertions / 9 deletions; new `sfs_axes/select.py` 124 lines;
  `pytest tests` re-run on the laptop -> **33 passed**; 0 carriage returns in all six touched files.
- Shipped surface: `rank_by_profile` (:55), `keep_lines` (:79), `select_union_lines` (:92) in
  `sfs_axes/select.py`; `run_potsac_union(..., line_rule=None)` at `sfs_axes/potsac.py:420` calling it at
  `sfs_axes/potsac.py:479`; writers `scripts/run_benchmark_172.py:73` and `sfs_axes/cli.py:66`.
  Off switch `SFS_AXES_LINE_RULE=0` / `--no-line-rule`; the ticket 313-320 regime stays reachable as
  `SFS_AXES_UNION_RANKER=normal`, which is how axes318/320 stay reproducible. `run_potsac` (paper chain) untouched.

**Verdict: the rule is merged as the shipped default, and the proof is byte identity on both sides of the switch.**
Identity held even though the offline refinement's iteration count was never recorded and five pieces sat
within 0.015 of the 1.2 cut (H 11 1.201, J 08 1.198, I 30 1.204, D 18 1.188, D 21 1.213) — so the shipped
costs agree with the offline ones on the side of the cut that matters.

Committed by the lead (the worker did not commit), with `.scratch/pota-repro/t324/submit_axes324.sbatch`.

