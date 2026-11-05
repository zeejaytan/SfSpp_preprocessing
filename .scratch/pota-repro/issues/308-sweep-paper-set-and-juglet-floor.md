# 308: Sweep every pot end-to-end on the paper's axis set — and give the Juglet a fair floor

**What to deliver:** the ticket-305 pot grid re-run on the candidate set that became the default in 307
(no `cost < cost[0]*1.1` prune), with the authors' axes as the control in the same job; Pot A at enough
seeds to say how often the paper's set reaches 8/8; a **delta table against 305** so the 1.1 prune's effect
is a measurement and not an inference; and a proper Juglet answer — the F20 floor fails for our axes AND
for the authors' own, so sweep the floor instead of reporting a single zero.

**Answers:** E1

**Blocked by:** none. 302 (per-point cost), 304 (under-5,000 rule), 305 (the grid to beat), 306 (no
equal-count cut, paper chain default), 307 (cost prune OFF by default) are all on main at `eb14046`.

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-05)
**Branch:** 308-sweep-paper-set-and-juglet-floor, in /c/PR/worktrees/sfs/308
**Worker:** sfs308

**Budget:** large 12

**Hand-over:** Claude — Spartan compute, the assembler SIF, the t66 lane recipe, the corpus tree.

## Why this ticket exists (measured; do not re-derive)

- **307 changed the default axis set and nobody has run a pot since.** `SFS_AXES_COST_PRUNE` now defaults
  to OFF (`sfs_axes/potsac.py`), so every pot's axis files are a different set from the ones in ticket 305's
  grid. Pot A, the only pot measured on the new set: **7/8 13/15 · 8/8 15/15 · 7/8 13/15** at seeds 0/1/2,
  assembler `NP=8`, two internal repeats (run `20261105-0424_e6adf69_t307-b1-s*-np8`). With the prune on,
  the same binary gives 6/8 10/15 · 7/8 12/15 · 6/8 10/15. Corpus direction (163 pieces): 84/163 within
  5 deg at 4.56 deg median, against 83/163 and 4.66 deg with the prune, and 84/163 and 4.63 deg in 305.
- **305's grid is the baseline to beat, and it was measured with the prune ON** — so any pot that moves
  could be the axis set, and any pot that does not move is evidence the change is Pot-A-specific. Compare
  cell by cell, do not re-summarise: A OO 8/8+15/15 MM 6/8+10/15 · B OO 9/9+15/15 MM 7/9+10/15 ·
  C all four 4/4+5/5 · D OO 22/27+53/66 MM 19/28+33/69 (NOTE the 28: D has 32 pieces, so quote the
  denominator you actually ran) · E OO 31/31+62/62 MM 23/31+37/62 · F OO 6/6+9/9 MM 5/5+7/7 ·
  G OO 7/7+10/10 MM 5/7+2/10 · I OO 25/27+59/65 MM 18/26+26/65 · J OO 8/11+16/21 MM 5/11+7/21.
  Pot H is **excluded** (11/11 refused at the admission gate, no GT-bearing lane).
- **`NP` must be quoted with every number.** The same axis set scores 7/8 12/15 at `NP=8` and 5/8 7/15 at
  `NP=3` (307 §4). Ticket 306's "second line on Piece 07 collapses Pot A" was an `NP=3` artefact. Run the
  whole grid at one `NP` per pot and say which.
- **The Juglet lane has never been given a fair test.** At the F20 floor it seats **0/9 with our axes and
  0/9 with the authors' own Dataset axes** (307 §8 C4; identical in 305), so the zero says nothing about
  the axes. Either the floor is wrong for this object or the lane is (rims/search), and 305's own
  conclusion for the corpus was 'rims+search, not axle direction'. Sweep it.

## Stage A — the axis set, with provenance

- **A1.** Produce the 163-piece axis set from the shipped default at a known commit, into new paths under
  the run directory (`out/axes308/`). Ticket 307's `20261105-0437_e6adf69_t307f-def/out/axes_paper` is the
  same set; **you may reuse it only by proving it**: md5 every file against a freshly generated one for at
  least 20 pieces (include Pot_A_07, Pot_A_08, Pot_B_08, Pot_G_07) and record both md5 lists. If any
  differs, generate all 163 fresh and say which reuse failed.
- **A2.** Record what changed per piece against the 305 set, if it is still readable
  (`20261105-0420_9c5eec2_t305-axes-corpus/out/axes305`): count of pieces whose line count changed, whose
  best line to a released line moved by more than 5 deg, and the K census against the 220 released lines.

## Stage B — the grid

- **B1.** For every pot that has a GT-bearing lane (all except H), run in ONE job: `OO` (authors' axes +
  our breaklines, the control), `MM` (our axes on the shipped default), and `MMp` (our axes with
  `SFS_AXES_COST_PRUNE=1`, i.e. ticket 305's arm) — so the prune's effect on that pot is measured in the
  same binary, same session, same staged trees. Two repeats each; small pots (A B C F G, ≤9 pieces) may
  take three.
- **B2.** The staged trees must differ only in `Axes/` for the MM vs OO pair and only in the axis FILES
  for MM vs MMp: prove it with `diff -rq` and log the output, as 302/307 did.
- **B3.** Report the assembler's own `1. Acc.txt` (sherds / joins) per repeat, then best-of-N with N
  stated. Do not report a median as the result.
- **B4. Pot A stability.** 5 more seeds of `MM` at the grid `NP` (seeds 3-7), 2 repeats each, plus the 3
  already on record from 307: report **how many of 8 seeds reach 8/8 + 15/15** and, on the seeds that
  miss, which joins fail with angle/offset. This is the only number that says whether the paper's set
  sometimes seats Pot A or seats it rarely.

## Stage C — the Juglet, properly

- **C1. The floor.** Our axes (shipped default) and the authors' `Dataset/Point/Juglet` axes, at floors
  **5, 10, 15, 20, 30** (the authors' default is 20), 2 repeats each, one job. Report seated sherds /
  directed pairs / gauge median / chamfer per cell, best-of-N, and whether any cell seats anything.
- **C2. Why it fails.** At the best floor, report per piece: number of candidate axes written (ours vs
  the authors' file), number of transforms produced, and the largest residuals. Name the mechanism (no
  candidate / wrong candidate / search gives up / gate too tight) rather than leaving a zero.
- **C3.** If a floor seats the Juglet, say so plainly with the floor and the repeats; if nothing does,
  state that the lane fails for both axis sets and therefore that the axis change is not the cause —
  which is a legitimate and useful negative result.

## Stage D — land and record

- **D1.** Corpus integrity: no file under `Dataset/` or the samples tree changed; record the md5 of the
  corpus before and after, as 304/305/307 did.
- **D2.** Renders per pot that moved (before/after the default change) and one Juglet picture at the best
  floor, to `SfSpp_preprocessing/artifacts/pota308/`. This session cannot see images: describe each
  honestly and leave the eye check to the conservator.
- **D3.** Every `sbatch` gets a poll and its `sacct -j <id> --format=State,ExitCode`, appended to the
  ticket Comments; one `index.tsv` row per run with `verdict`/`human_note` empty.
- **D4.** A delta table: pot | 305 `MM` (prune on) | 308 `MM` (paper set) | 308 `MMp` (prune on, same
  job) | 308 `OO` control — so the reader can separate the axis set's effect from run-to-run noise.

## Acceptance

- [ ] **A1** 163-piece axis set at a named commit, provenance proved (fresh-vs-reused md5s for ≥20 pieces incl. the four named).
- [ ] **A2** per-piece change census against the 305 set, and the K census vs 220 released lines.
- [ ] **B1** grid run per pot with `OO`, `MM`, `MMp`, ≥2 repeats each, at a stated `NP`.
- [ ] **B2** axes-only substitution proved by `diff -rq` for every arm.
- [ ] **B3** per-repeat `1. Acc.txt` values and best-of-N with N stated.
- [ ] **B4** Pot A across 8 seeds: how many reach 8/8 + 15/15; failing joins with angle/offset on the rest.
- [ ] **C1** Juglet floor sweep 5/10/15/20/30, both axis sets, 2 repeats, per-cell numbers.
- [ ] **C2** the Juglet failure mechanism named per piece at the best floor.
- [ ] **D1-D4** corpus md5 unchanged, renders described, sacct+index rows, and the delta table.

## Rules and traps (read before the first job)

- `ticket_start.sh` creates the worktree; if `Status` is not `ready-for-agent` on origin when you run it,
  say so and stop rather than improvising a worktree.
- **ssh must be `/c/Windows/System32/OpenSSH/ssh.exe spartan`** — git-bash ssh cannot authenticate. Quote
  the whole remote command in single quotes or `$` expands locally (this has printed a home directory
  listing instead of the run directory twice in this lane).
- Runs: `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_<tag>/` with `run.json`,
  `submit.sbatch`, `logs/`, `out/`, and one `index.tsv` row. Heavy work on compute nodes only; MATLAB only
  on a compute node (the licence is refused on the login node). No recursive `find`/`du` over `/data/gpfs`.
- Reuse the instruments rather than rewriting them: `.scratch/pota-repro/305-stage/` (driver, staging,
  scoring, renders, lane builders), `.scratch/pota-repro/306-stage/` (axes-only substitution proof),
  `.scratch/pota-repro/307-stage/` (extraction + the arm runner at `NP=8`). The t66 lane recipe
  (`runs/20261103-1332_fab76f5_t66-admitsign-default/outU_*/geom`) and the assembler SIF path are in them.
- **Do not fit to the released axes.** They and the GT poses are for scoring and for the `OO` control only,
  never inside a selection rule.
- **Do not read `rad_mm` as valid** (302/307 flagged the column); no compare-only radial instrument exists.
  If you want a radial number, build one and say so.
- Edit the ticket Comments only; **commit and push nothing** — the lead commits. Budget: stop after 8
  failed acceptance checks and report what you have.

## Report back

The delta table first, then: the Pot A 8-seed stability count, the per-pot claims classified as (1) method,
(2) measurement, or (3) reference wrong, the Juglet floor sweep and its mechanism, the corpus md5 line, the
run ids with `sacct` State/ExitCode, and anything you had to leave undone with the reason.
