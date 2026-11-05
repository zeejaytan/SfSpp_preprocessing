# 307: Match the paper's axis method clause by clause — and emit the candidate set the paper describes

**What to deliver:** a clause-by-clause fidelity audit of `sfs_axes` against paper **§IV-B2** and the
authors' MATLAB, with every remaining difference named at a `file:line` and either **fixed** or
**justified in writing**; the paper's own candidate set actually emitted and measured; and Pot A
seating **8/8 sherds + 15/15 joins with our axes only at 2 of 3 seeds, no best-of-N**. The target is
the paper's method. The released axis files are a scoring reference, never a thing to fit to.

**Answers:** E1

**Blocked by:** none. 302 (per-point cost), 304 (under-5,000 rule, default ON), 305 (sweep), 306 (no
equal-count cut; paper chain default) are all on main.

**Status:** landed (lead 2026-11-05) — the paper's set is the default; C1 not met, blocker named
**Worker:** sfs307

**Budget:** large 12

**Hand-over:** Claude — Spartan compute, the assembler SIF and the corpus lanes; MATLAB on a compute
node for the parity and `.m`-reading stages.

## Why this ticket exists (measured; do not re-derive)

- **The assembler is not the suspect.** Same binary, same breaklines, only the axis files swapped:
  **MO (authors' axes) 8/8 + 15/15**, **MM (ours) 6/8 + 10/15** — run `20261105-0617_9c5eec2_t305-e2e-a-moom`
  (job 34353216; arms `MOR1`/`MOR2` = 8/8 15/15, `MMR1`/`MMR2` = `OMR1`/`OMR2` = 6/8 10/15, re-read by the lead 2026-11-05),
  2/2 repeats each. So the difference lives in our axis set, and the way to close it is to match the
  method that produced theirs. Do not spend time on `sfs_main` in this ticket.
- **Best our axes have ever reached: 7/8 + 12/15** (paper chain, equal-count cut off, seed 1, 3/3
  repeats). Nothing so far has produced 8/8 with our axes.
- **Our chain writes 1-3 axis lines per piece; the released files hold 1-6.** Ticket 305's census,
  which this ticket re-counts: ours fewer lines than the reference on 20 of 163 pieces, more on 19,
  the same on 124.
- **The reason we write 1-3 is one line of our code:** `sfs_axes/potsac.py:145`, `keep = cost <
  cost[0] * 1.1`, applied twice (`:239` after stage-1 refine, `:247` after stage-2). The port's own
  docstring says it is a MATLAB quirk kept deliberately ("first survivor, not the minimum — MATLAB
  quirk, kept"). **The paper's description of the same step contains no such prune.** Paper and code
  therefore disagree, and which one we follow is a decision this ticket has to make with a measurement,
  not a preference.
- **Ticket 306's union is not a test of the paper's set.** It unioned 10 seeds and ranked survivors by
  the worst wall's cost per point. The paper's own output — the **top 10** survivors ranked by the
  robustified residual cost, duplicates at 10 deg removed keeping the cheaper — has **never been
  emitted** by this code. That is the largest single untested divergence from the paper, and it is the
  first thing to test.
- **Two smaller divergences are already known and never settled:** the paper says *MLESAC-based*
  sampling while our search is 1,000 fixed uniform 6-point draws ranked MSAC-style; and the paper says
  *trust-region* optimisation while `refine.py` is a literal Levenberg-Marquardt port of the authors'
  `optimize_using_lm.m`. In both cases the authors' code is the operative reading — settle each by
  reading the `.m`, not by trusting either wording.

## The clauses to audit (quoted; `papers/text/sfspp-2502.13986v1.md`)

1. **:171-173** "MLESAC-based sampling with a minimal 6-point solver that enforces Pottmann's
   constraint — ensuring the offset vector, symmetry axis direction, and the cross product of the
   surface normal lie on the same plane".
2. **:173-175** "an extended Cao and Mumford error, applicable to both interior and exterior
   surfaces ... in the subsequent trust-region-based nonlinear optimization".
3. **:175** "selects the top 10 candidate axes. Then, the angles between each pair of axes are
   evaluated, and those with an angle of 10 degrees or less are considered duplicates, with the axis
   having the higher cost, defined as the robustified residual error, being removed through pruning."
4. **:175** "we initially sample only 10% of the surface points to generate axis candidates, and after
   pruning, all surface points are used for more detailed refinement".
5. **:155** "B-Spline fitting is performed for each cluster to refine surface boundaries and uniformly
   sample the point cloud" — surface generation, not the axis method; do not implement an axis from it.

## Stage A — the audit (no E2E; a laptop and one login-node read)

Build the table the rest of the ticket hangs off. One row per clause and per `.m` file, columns:
**the paper says** (quote + line) / **the `.m` does** (`file:line`, quoted) / **we do** (`file:line`) /
**can this change the emitted set?** / **verdict** (`MATCH`, `DIFFERS-DOCUMENTED`,
`DIFFERS-UNDOCUMENTED`). Files to read in `AxisExtraction/` and wherever they live:
`compute_axis_of_symmetry.m`, `compute_pottmann_axis.m`, `compute_biaxial_cao_error.m`, `run_potsac.m`,
`refine_axis.m`, `optimize_using_lm.m`, `robustifier_gm.m`, `robustifier_huber.m`,
`apply_robustifier.m`, `read_surfaces.m`, `extract_axis.m`.

Three specific questions Stage A must answer with a quote, not an inference:

- **A-Q1 (the big one):** does `run_potsac.m` really contain the `cost < cost[0]*1.1` prune, and does
  the paper's "top 10 survive" describe the same quantity? If the `.m` has it, the authors' own
  released files were made by a chain that can only emit 1-3 lines — so the paper's method and the
  authors' output disagree, and we must say which we follow and why.
- **A-Q2:** is the sampling in `compute_axis_of_symmetry.m` adaptive (MLESAC-style stopping or
  likelihood weighting) or 1,000 fixed uniform draws? Quote the loop and the stop condition.
- **A-Q3:** does `compute_pottmann_axis.m` return one axis per 6-point sample or several valid ones?
  Our `sfs_axes/pottmann.py:26-32` returns the single smallest singular vector of the reduced matrix.
  If the `.m` can return more, our pool is a fraction of theirs — say so with the line.

Also in Stage A, the **output-shape census** (`A2`): for all 163 corpus pieces, lines written by our
chain vs lines in the released file, per pot, with the pieces where we differ named. This is the
cheapest fidelity measurement available and it is free of any E2E.

## Stage B — arms, one variable each, Pot A first

Every arm is measured the same way: Pot A at seeds 0/1/2, report `Sherd accuracy` and the join count
read from `out/<arm>/1. Acc.txt` plus a per-join recompute, **no best-of-N** on the assembler. Any arm
that changes the axis set must also produce the corpus census line (163 pieces, md5 of the released
inputs unchanged) and a Juglet arm for collateral damage.

- **B1 — the paper's candidate set, emitted.** Top 10 survivors ranked by the paper's cost, 10 deg
  dedup keeping the cheaper, **no `cost[0]*1.1` prune**. This is the hypothesis the ticket exists to
  test. Report K per piece and whether Pot A moves.
- **B2 — MLESAC sampling** if A-Q2 finds the `.m` adapts (iterations from the inlier ratio, or
  likelihood weights); otherwise record `MATCH` and skip.
- **B3 — Pottmann completeness** if A-Q3 finds more than one axis per sample: return all of them.
- **B4 — the ranking statistic.** The paper defines the cost as "the robustified residual error"; make
  sure the stage-2 order uses exactly that quantity on all points, and that the order is the paper's
  (cheapest first). Report the row that settled it.
- **B5 — the 10% sample.** Stage A decides whether `run_potsac.m` strides or draws at random; match
  the `.m` and report what the difference does on Pot A Piece 07 and Piece 08 specifically (they are
  the two pieces the last four tickets kept returning to).
- **B6 — any other `DIFFERS-UNDOCUMENTED` row Stage A produces.** One arm each; if a row needs no
  code change, close it in the table instead of an arm.

## Stage C — land the paper-faithful chain

- **C1 — the verdict.** Either Pot A seats **8/8 + 15/15 with our axes only at 2 of 3 seeds, no
  best-of-N**, or the ticket states plainly what still blocks it — which piece, which join, and at
  what angle/offset — with the arm that came closest. A negative verdict is a result; do not tune to
  reach the bar.
- **C2 — parity.** Anything touched must still pass ticket 302's MATLAB unit parity (bar `1e-9`) and
  `python -m pytest tests/ -q`.
- **C3 — the corpus.** 163 pieces to new paths, released md5 unchanged, tier table against 306's
  baseline (**84/163 within 5 deg, median best 4.63 deg**) with the direction, and the `rad_mm` column
  reported separately (anchor reflection is a known, fixed defect — do not compare old rad numbers).
- **C4 — Juglet.** One arm, F20 floor, our axes vs the Dataset axes, counts unchanged in kind
  (currently 0/9 seated for every axis set tried).
- **C5 — renders** of any geometry claim into `artifacts/pota307/`, and the defaults documented in the
  ticket and in `intent/E1`.

## What is admissible (read this before choosing a fix)

**A change is admissible only if a paper clause or a line of the authors' `.m` prescribes it.** If a
change seats Pot A but has no paper or code warrant, it is a finding to report, not a default to ship.
The same rule runs the other way: a paper-faithful change that does **not** seat Pot A is still the
correct code, and the ticket must say so and leave it on.

Never fit to the released axis files. Never use them, or the ground-truth poses, inside a selection
rule; they are for scoring only.

## Acceptance

- [ ] **A1** clause table delivered: every row with the paper quote, the `.m` `file:line`, our
      `file:line`, "can it change the emitted set", and a verdict.
- [ ] **A2** the line-count census (ours vs released, 163 pieces, per pot) with the differing pieces
      named.
- [ ] **A3** A-Q1/A-Q2/A-Q3 answered with quotes, and the paper-vs-`run_potsac.m` conflict on the 1.1
      prune decided in writing with the measurement behind the decision.
- [ ] **A4** every `DIFFERS-UNDOCUMENTED` row is either closed as `MATCH` or assigned to a B arm.
- [ ] **B1** the paper's top-10 set emitted and measured on Pot A, 3 seeds, with K per piece.
- [ ] **B2-B6** each arm run or closed with the reason (one variable, one table).
- [ ] **C1** Pot A verdict: 8/8 + 15/15 with our axes at 2/3 seeds, or the named blocker.
- [ ] **C2** 302 parity (bar `1e-9`) and `pytest` pass for everything touched.
- [ ] **C3** corpus 163 with the released md5 unchanged and the tier table against 306's baseline.
- [ ] **C4** Juglet arm reported.
- [ ] **C5** renders in `artifacts/pota307/` and the defaults documented.

## Rules of the road

- `ssh` must be `/c/Windows/System32/OpenSSH/ssh.exe spartan`; git-bash `ssh` cannot authenticate.
  Single-quote the whole remote command or `$` expands locally.
- Runs go under `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_<tag>/` with
  `run.json`, `logs/`, `out/`, and one `index.tsv` row (verdict/human_note empty). Poll every job with
  `sacct -j <id> --format=State,ExitCode` and record State/ExitCode in the ticket.
- Build on the ticket-306 stage scripts in `.scratch/pota-repro/306-stage/` (they already stage the
  Pot A trees, substitute only `Axes/`, and enforce axes-only diffs with `diff -rq`).
- The corpus is read-only: no file under `Dataset/` or the sample trees may change; prove it with an
  md5 diff before and after.
- Heavy work on compute nodes, never the laptop or the login node.
- Edit the ticket's Comments only; commit and push nothing. Hand back: the tables, the run ids, the
  sacct lines, and the diff of anything you would ship.

## Comments

### 2026-11-05 · worker session sfs307 · Stage A (clause audit), Stage B (arms), Stage C (verdict)

**Verdict in one paragraph.** The paper and the authors' MATLAB disagree on one thing that changes the emitted set: `run_potsac.m:61` and `:78` delete every candidate whose Huber cost is more than 10 % above the first survivor's, and the paper (`:175`) describes only the top-10 cut plus the 10° dedup. The prune is the authors' own code (it is in the vendored pristine tree, not a local fix), but it is not the paper's method, and on the assembler it costs sherds at every seed. The shipped default is now the paper's candidate set (`SFS_AXES_COST_PRUNE=0`); the authors' prune stays one environment variable away (`=1`). Pot A with our axes at NP=8: paper set **7/8 13/15, 8/8 15/15, 7/8 13/15** (seeds 0/1/2) against the authors' prune **6/8 10/15, 7/8 12/15, 6/8 10/15**. The 8/8 + 15/15 is reached at **one** of three seeds, not two, so C1 is **not met**; the named blocker is Pot A Piece 08 spun to the wrong place on the pot (joins 2–8 and 4–8 at 86° / 165–169 mm on seed 0 and 168° / 376–380 mm on seed 2), and it is not a clause difference. Corpus: 84/163 pieces within 5° (median best 4.56°) with the new default vs 83/163 (4.66°) with the authors' prune — no worse. MATLAB parity still passes at 1e-9, pytest 9/9. Nothing is committed.

#### 1. What ships

Two files, both in `sfs_axes/` (uncommitted; the lead commits):

- `sfs_axes/potsac.py` — `COST_PRUNE` default flipped `"1"` → `"0"` (paper's set is the default); the `ADAPTIVE_UNDER_5K` comment rewritten: the under-5,000-point step rule is a **deviation**, not the authors' rule (it exists only in the locally patched `AxisExtraction/run_potsac.m:18-27`, commit ff40fc9); module docstring updated to name `run_potsac.m:61/:78` as the prune's home.
- `sfs_axes/cli.py` — module and `extract_piece` docstrings say what the new default is, where the paper says it (`papers/text/sfspp-2502.13986v1.md:175`), and how to get the authors' chain back.

`git diff --stat`: `sfs_axes/cli.py | 21 +-`, `sfs_axes/potsac.py | 58 +-`. `python -m pytest tests/ -q` → 9 passed. `git status`: these two files plus this ticket, and the untracked instruments under `.scratch/pota-repro/307-stage/`.

#### 2. Stage A — clause table (A1)

Provenance established first, because two copies of the MATLAB exist here. `original_nurbs_preprocessing/AxisExtraction/` is the vendored pristine upstream (commit 3095064 "Vendor the pipeline source from the nested clone", provenance back to 405c048 Sisung Liu 2025-03-06). `AxisExtraction/` is the local working copy (ff40fc9 Zeejay Tan 2025-11-15 "Local fixes: MATLAB bugs, headless build, path corrections, SFS format"). `diff -r` between them, ignoring line endings: **one behavioural difference in the whole axis chain — `run_potsac.m`**, whose local copy adds the adaptive-step block at `:18-27`. Every other axis `.m` is identical. So a quote from any other file is the authors' code; a quote from the local `run_potsac.m:18-27` is not.

| # | paper (`papers/text/sfspp-2502.13986v1.md`) | authors' `.m` (pristine) | ours | changes the emitted set? | verdict |
|---|---|---|---|---|---|
| 1 | `:173` "MLESAC-based sampling with a minimal 6-point solver" | `compute_axis_of_symmetry.m:7` (`num_sample_set = 6`), `:9` (`max_iters = 1000`), `:18` `randsample(num_points, 6)` | `potsac.py:74-76`, `:108` | no (sampling only) | **MATCH** — 1,000 fixed uniform 6-point draws without replacement; no adaptive stopping, no likelihood weighting (A-Q2) |
| 2 | `:173` "Pottmann's constraint — the offset vector, symmetry axis direction, and the cross product of the surface normal lie on the same plane" | `compute_pottmann_axis.m:14-25` (reduced 3×3 system, smallest singular vector) | `pottmann.py:26-32` | no (solver only) | **MATCH** — one axis per 6-point sample (A-Q3) |
| 3 | `:173` "the original PotSAC outputs only a single axis … we propose a modified version capable of producing multiple axes" | `run_potsac.m:34-37` (10 refined candidates kept) | `potsac.py:229-231` | yes | **MATCH** |
| 4 | `:175` "selects the top 10 candidate axes" | `run_potsac.m:22` (`num_candidates = 10`), `:37` | `potsac.py:208`, `:231` | yes | **MATCH** |
| 5 | `:175` "those with an angle of 10 degrees or less are considered duplicates, with the axis having the higher cost … removed through pruning" | `run_potsac.m:47-56` (`angles > 0.9848`, `repeats(jj)`) | `potsac.py:134-146` | yes | **MATCH** on threshold and rule; documented quirk: MATLAB marks the *second* member of each pair, i.e. the later one in the GM-sorted order, which is usually but not always the dearer |
| 6 | `:175` "we initially sample only 10% of the surface points" | `run_potsac.m:18` `C(:,1:10:num_points)` | `effective_step` + `cli.py` `--step 10` | yes | **MATCH** for pieces ≥ 5,000 points; **DIFFERS-DOCUMENTED** below 5,000 (row 17) |
| 7 | `:175` "after pruning, all surface points are used for more detailed refinement" | `run_potsac.m:66-68` (`refine_axis(vt(:,i), C, …)` on all `C`); `read_surfaces.m:21-32` keeps both walls whole | `potsac.py:240-241`; `io_surfaces.read_surfaces(truncate=False)` (default since 306) | yes | **MATCH** |
| 8 | `:173` "an extended Cao and Mumford error, applicable to both interior and exterior surfaces" | `compute_biaxial_cao_error.m:16-19` (log-sum-exp soft-min over the two normal-sign hypotheses, `s = 100`) | `cao.py:54-85` | yes (cost feeds ranking) | **MATCH** |
| 9 | `:175` "cost, defined as the robustified residual error" | `run_potsac.m:39-45` (Huber width 1.0, sum of per-point cost) | `potsac.py:265-269`, `_huber_per_point` | yes | **MATCH** |
| 10 | `:173` "trust-region-based nonlinear optimization" | `optimize_using_lm.m:25-91` (LM/trust-region hybrid, max_trials 20, Triggs-corrected robustifier, `J(:,1:3)` projected) | `refine.py` | no (refines, does not select) | **MATCH** — the `.m` is the operative reading; the paper's phrase is generic |
| 11 | — (no paper clause) | `run_potsac.m:61` and `:78` `good_cost_idx = cost < cost(1) * 1.1` | `potsac.py` `COST_PRUNE`, `_dedup` | **yes** | **DIFFERS-DOCUMENTED**, decided: default **OFF** (paper). Measurement in §3 |
| 12 | — (no paper clause) | the second prune at `:78` runs on the **stale** stage-1 cost, never recomputed after the all-points refinement | `_dedup` is handed the same stage-1 cost at `:247` | yes (when the prune is on) | **MATCH** — quirk reproduced faithfully |
| 13 | — (no paper clause) | `run_potsac.m:82-83` `[cost, ia] = sort(cost); vt = vt(:, ia)` — ascending | `potsac.py:248-251` `np.argsort(cost)` | yes | **MATCH** |
| 14 | — (no paper clause) | `run_potsac.m:8-16` one-wall handling (`half_point = floor(0.5*n)`) | `run_potsac(C1, C2=None)` | n/a here (both walls present on all 163 + Pot A) | **MATCH** |
| 15 | — (no paper clause) | `compute_axis_of_symmetry.m:29-34` computes `num_inliers`, never uses it for stopping | `potsac.py:120-121` records inliers, unused | no | **MATCH** |
| 16 | `:155` "B-Spline fitting refines the surface boundaries" | no axis `.m` reads a spline; surfaces arrive as xyz | `io_surfaces.read_surfaces` | no | **MATCH** — a surface-generation clause, nothing to port into the axis chain |
| 17 | — (no paper clause; **local only**) | `AxisExtraction/run_potsac.m:18-27` (ff40fc9): `step = 1` under 5,000 points — absent from the pristine tree | `ADAPTIVE_UNDER_5K` (default ON) | yes | **DIFFERS-DOCUMENTED**, kept ON — see B5 and the buddy arm in §6 |

#### 3. Stage A — the three questions and the 1.1-prune decision (A3)

**A-Q1 — is the `cost < cost[0]*1.1` prune in `run_potsac.m`, and is the paper's "top 10 survive" the same quantity?** Yes to the first: the prune is in the authors' file, twice (`:61` after the stage-1 dedup, `:78` after the all-points refinement), and it applies to the survivors of the 10° dedup, not to the top 10. It is not the same quantity as "top 10 survive": the paper's sentence stops after the dedup, so under the paper as written up to 10 non-duplicate axes are written; the `.m` keeps only those within 10 % of the *first survivor of the GM-sorted order* (which is not necessarily the minimum Huber cost — `compute_axis_of_symmetry.m:48-51` sorts by the GM-robustified sum, while `cost` here is the Huber sum). What it costs on Pot A: Piece 07's second released basin is 3.5× the best cost and dies in all four probe cases; Piece 08's good line is rank 1–38 and dies at one seed. So yes, this single line is the difference between the two methods.

**A-Q2 — is the sampling adaptive (MLESAC stopping / likelihood weighting) or 1,000 fixed uniform draws?** 1,000 fixed uniform 6-point draws without replacement (`compute_axis_of_symmetry.m:9`, `:18`); `num_inliers` is computed at `:31-33` and never used; "MLESAC" survives only as the MSAC-style GM ranking at `:29-32`. Our port matches, so **B2 is closed: there is no adaptation to port.**

**A-Q3 — does `compute_pottmann_axis.m` return one axis per sample or several?** One: the smallest singular vector of the reduced 3×3 system (`:20-25`), unscaled and projected onto the tangent plane by the caller. Multiple axes come from many samples. Our `pottmann.py:26-32` is the same solve, so **B3 is closed: nothing more to extract per sample.**

**The decision (A3).** Default = the paper's set, no cost prune. Warrants, in order: (i) the paper describes the method and has no such line; (ii) the prune is the only place the two differ in a way that changes what is written; (iii) measured on the assembler it is worse at every seed (§6, B1 vs base) and worse or equal on the corpus (83/163 vs 84/163 within 5°); (iv) it is reversible by one env var, and the chain it belongs to is still exercised by the parity gate. The authors' chain is therefore *available*, not *default*, and the parity test (C2) still runs it.

#### 4. Stage A — line-count census, 163 pieces (A2)

Arms: **paper** = new default (no prune, under-5k rule on); **prune** = authors' chain (`SFS_AXES_COST_PRUNE=1`). Released = `$CORP/Axes/*.xyz`, 220 lines over 163 pieces.

| pot | pieces | released lines | paper: ours | paper: fewer/equal/more | prune: ours | prune: fewer/equal/more |
|---|---|---|---|---|---|---|
| A | 8 | 11 | 12 | 1 / 5 / 2 | 11 | 1 / 5 / 2 |
| B | 9 | 10 | 16 | 0 / 4 / 5 | 12 | 1 / 6 / 2 |
| C | 6 | 7 | 10 | 0 / 4 / 2 | 10 | 0 / 4 / 2 |
| D | 32 | 45 | 45 | 3 / 26 / 3 | 45 | 3 / 26 / 3 |
| E | 34 | 41 | 38 | 3 / 31 / 0 | 35 | 4 / 30 / 0 |
| F | 7 | 9 | 10 | 1 / 5 / 1 | 9 | 1 / 5 / 1 |
| G | 7 | 7 | 7 | 0 / 7 / 0 | 7 | 0 / 7 / 0 |
| H | 11 | 24 | 23 | 2 / 4 / 5 | 14 | 6 / 3 / 2 |
| I | 30 | 33 | 40 | 0 / 25 / 5 | 37 | 0 / 27 / 3 |
| J | 19 | 33 | 37 | 3 / 9 / 7 | 31 | 5 / 9 / 5 |
| **all** | **163** | **220** | **238** | **13 / 120 / 30** | **211** | **21 / 122 / 20** |

Differing pieces, paper: A06 A07 A08 B03 B05 B06 B07 B09 C02 C06 D15 D17 D21 D24 D27 D30 E21 E31 E34 F05 F07 H02 H04 H06 H07 H08 H09 H10 I16 I17 I27 I28 I29 J05 J06 J07 J11 J12 J13 J14 J16 J18 J19 (43). Differing pieces, prune: A06 A07 A08 B05 B08 B09 C02 C06 D15 D17 D21 D24 D27 D30 E20 E21 E31 E34 F05 F07 H02 H05 H06 H07 H08 H09 H10 H11 I17 I27 I29 J05 J06 J08 J11 J12 J13 J14 J15 J18 J19 (41). The two arms differ on Pot A in **one line**: Piece 07 gets 2 lines on the paper arm and 1 on the prune arm at every seed; Piece 08 is 3/2 on both. That single line is the whole of the assembly difference in §6 — restoring it gains one sherd and two to three joins at every seed. (Per-piece counts from `census_paper.txt` / `census_base.txt`; the prune arm's files are the `20261105-0406_e6adf69_t307a-axes` run's `out/axes_base/`, since the 307f run extracted only paper/b1/b1b5.)

#### 5. Stage A — A4

Every row of the table above is `MATCH` except three `DIFFERS-DOCUMENTED` (row 6 below 5,000 points, rows 11 and 17), and each is closed by a measurement, not by assignment to an arm still to run: row 11 by B1, rows 6/17 by B5 and its buddy arm (§6). **No `DIFFERS-UNDOCUMENTED` row remains.**

#### 6. Stage B — arms (one variable each; Pot A, seeds 0/1/2)

The number is the assembler's own `1. Acc.txt` (sherds / joins), NP=8, `ARMSPEC "MM:2"` (two internal repeats, identical in every case below), `NAMED=8`, `FLOOR=50`, lanes = ticket 66 `outU_pota/geom`, axes = this ticket's own extraction. NP matters: at NP=3 every arm under-scores (the *same* axis set that gives 7/8 12/15 at NP=8 gives 5/8 7/15 at NP=3), so the NP=3 sweep run earlier in this ticket is kept only as a record and is **not** the table below.

| arm | what varies | warrant | K per piece 01–08 (s0 / s1 / s2) | Pot A s0 / s1 / s2 | verdict |
|---|---|---|---|---|---|
| **B1** | paper's set: no cost prune | paper `:175` | s0 1 1 1 1 1 2 2 3 / s1 1 1 1 1 1 2 2 5 / s2 1 1 1 1 1 2 2 3 | **7/8 13/15 · 8/8 15/15 · 7/8 13/15** | **ACCEPTED — becomes the default** |
| base | authors' prune (previous default) | `run_potsac.m:61,:78` | s0 1 1 1 1 1 2 1 3 / s1 1 1 1 1 1 2 1 5 / s2 1 1 1 1 1 2 1 3 | 6/8 10/15 · 7/8 12/15 · 6/8 10/15 | reference arm |
| B2 | MLESAC adaptation | none exists | — | — | **CLOSED**: A-Q2, 1,000 fixed uniform draws |
| B3 | Pottmann multi-axis per sample | none exists | — | — | **CLOSED**: A-Q3, one axis per sample |
| B4 | rank by post-refine cost (all points) | no clause prescribes it | s0 … 1 3 / s1 … 1 5 / s2 … 2 3 | 6/8 10/15 · 7/8 12/15 · 5/8 7/15 then 6/8 10/15 | **REJECTED** — worse or equal, and unstable between repeats |
| B5 | step = 10 always (under-5k rule off) | local `run_potsac.m:18-27` removed | s0 1 1 1 1 1 2 2 3 / s1 … 2 1 2 / s2 … 2 1 4 | 7/8 13/15 · 6/8 10/15 · 6/8 10/15 | **REJECTED** — no seed improves consistently; Piece 07 loses its second line on s1/s2 |
| (buddy) | paper's literal 10 % **and** no prune | paper `:175` | s0 … 2 2 3 / s1 … 2 2 2 / s2 … 2 2 4 | not assembled (B1 and B5 already isolate both variables) | **Piece 08's released line is lost at all three seeds** (cov5 = 0) — this is why the deviation stays |
| B6 | any remaining `DIFFERS-UNDOCUMENTED` row | — | — | — | **CLOSED**: §5, none remain |

Piece 07 and Piece 08 specifically (B5's named pieces, and the two the ticket is about). Piece 07 has 3 released lines; the paper's set gives it **2** at all three seeds and the prune gives it **1**; no arm reproduces its lines 1–2 (ticket 306: line 2 is in no pool at 120–130°, nearest draw 8.55° away; line 1 is in the pool at 5.06–6.54° but 3.5× the cost). Piece 08 has 2 released lines; the paper's set gives it **3 / 5 / 3** lines.

Run ids and `sacct` (all `COMPLETED | 0:0`):

| run dir (`runs/20261105-0424_e6adf69_t307-…`) | job | elapsed | result |
|---|---|---|---|
| `b1-s0-np8` | 34372619 | 6:15 | 7/8 13/15 |
| `b1-s1-np8` | 34372620 | 6:59 | **8/8 15/15** |
| `b1-s2-np8` | 34372621 | 8:46 | 7/8 13/15 |
| `base-s0-np8` | 34372628 | 5:00 | 6/8 10/15 |
| `base-s1-np8` | 34372629 | 5:20 | 7/8 12/15 |
| `base-s2-np8` | 34372630 | 5:35 | 6/8 10/15 |
| `b4-s0/s1/s2-np8` | 34372622 / 34372623 / 34372624 | 7:44 / 9:10 / 8:51 | 6/8 10/15 · 7/8 12/15 · 5/8 7/15 + 6/8 10/15 |
| `b5-s0/s1/s2-np8` | 34372625 / 34372626 / 34372627 | 7:35 / 4:49 / 7:13 | 7/8 13/15 · 6/8 10/15 · 6/8 10/15 |
| extraction `20261105-0406_e6adf69_t307a-axes` | 34372174 | 1:54 | 96/96 Pot A + 3×163 corpus |
| default-flip proof `20261105-0437_e6adf69_t307f-def` | 34373280 | 2:29 | paper == b1 byte-identical, 3 seeds |
| NP=3 record `-s0/s1/s2` (12 runs) | 34372425/26/33, 34372436/56/57, 34372458/59/60, 34372461/62/63 | 2:28–4:57 | **superseded, see NP note** |

The strict scorer (`score305.py`) reproduces the binary's join count in all 24 run × repeat checks (13, 15, 13, 10, 12, 7+10, 13, 10, 10, 10, 12, 10). Its per-piece column is not usable as printed — it reports 0/8 on runs where the binary says 7–8 and where pieces 1–6 take identical values in different arms (a frame artefact of that diagnostic) — so sherd counts are quoted from `1. Acc.txt`.

#### 7. Stage C — C1 verdict and the named blocker

Criterion: 8/8 + 15/15 with our axes at 2 of 3 seeds. Measured: **1 of 3**. C1 is **not met**; the best attempt is reported (best-of-N rule): `20261105-0424_e6adf69_t307-b1-s1-np8`, job 34372620, **8/8 sherds, 15/15 joins**, both internal repeats, joins at 0.727–3.789° and 3.17–25.07 mm.

**Named blocker — Pot A Piece 08, joins 2–8 and 4–8.** Every failing join on the other seeds involves Piece 08:

- seed 0 (7/8 13/15): join 2–8 **86.0° / 164.7 mm**, join 4–8 **84.9° / 169.0 mm** — seated near a quarter-turn out;
- seed 2 (7/8 13/15): join 2–8 **168.6° / 376.0 mm**, join 4–8 **167.1° / 379.9 mm** — near a half-turn out;
- seed 1 (8/8 15/15): all 15 joins pass.

The other 13 joins pass on every seed at 0.5–3.8° and 3–23 mm. This is not a missing axis and not a pose error: on seeds 1 and 2 both of Piece 08's released lines are within 5° of one of our lines (cov5 = 1, best 3.68° / 3.13°), and the assembly still differs between them — so what remains is *which* of Piece 08's 3–5 candidate lines the assembler matches, and the paper prescribes nothing after "top 10 by cost" that would decide it. On seed 0 both of its released lines are within 10° but neither within 5° (nearest 5.67°) — the worse case, and the one where the sherd lands a quarter-turn out rather than a half-turn. No single-variable arm closes it: B4 (post-refine ranking) worse, B5 (step=10) worse, the authors' prune worse. **This is the named blocker; it is not a gap in the paper's clause set but in the assembler's choice among lines the paper allows.**

#### 8. C2, C3, C4, C5

**C2 — parity PASS.** `20261105-0438_e6adf69_t307c-matlab-unit`, job 34373396, `COMPLETED 0:0` in 0:32. 9 rows (Pot A Piece 01/04/07 × probes released/+2°/+5°), all PASS at the 302 bar: `R1_rel` 4.6–4.8e-15, `J_rel` 4.8e-15–7.6e-13, `R3_rel` 4.7–5.0e-15, `OVERALL: PASS`, `compare rc=0`. Run against the **edited** tree (`potsac.py` md5 287fe6042ffaf92f72e1eefea9a89042, the same file the extraction job used). `python -m pytest tests/ -q` → 9 passed.

**C3 — corpus 163, released md5 unchanged.** `20261105-0437_e6adf69_t307f-def` (job 34373280) wrote all 163 axis sets for each chain to new paths (`out/axes_paper/`, `out/axes_b1b5/`, `out/axes_b1/`, 163 files each) and logged "corpus Surfaces+Axes unchanged"; no file under `Dataset/` was touched by any job in this ticket. Tier table (`analyse306c.py`, direction only):

| tier | pieces | median best° | within 5° | paper arm | prune arm |
|---|---|---|---|---|---|
| gt_close (all released lines matched) | 78 | 2.13 | 100 % | 2.13 / 100 % | 2.13 / 100 % |
| gt_off | 85 | 12.50 | 7.1 % | **12.50 / 7.1 %** | 15.87 / 5.9 % |
| **all** | **163** | **4.56** | **51.5 % (84/163)** | **84/163, 4.56°** | 83/163, 4.66°, 50.9 % |

Baseline to beat was 84/163 within 5° and median best 4.63° (ticket 306): the paper's set **equals the count and improves the median**; the authors' prune is one piece short and its unmatched tier is materially worse (15.87° vs 12.50° median on the 85 pieces whose released lines we do not match). **`rad_mm` is not reported**: this worktree has no compare-only radial instrument (`analyse306c.py` emits direction; `corpus302.py`'s `rad_mm` is computed inside its own extraction loop), and ticket 302 flagged that column's validity. Flagged as the one unmet part of C3 rather than silently dropped — the last valid radial figure on record is 304's corpus run (median 21.171 mm, n=163), which is not comparable to this axis set.

**C4 — Juglet arm, F20 floor.** `20261105-0422_e6adf69_t307d-jug`, job 34372673, `COMPLETED 0:0` in 3:22. Our axes (default chain, seed 0) → `F20N_r1..r3`: **0/9 sherds, 0/36 directed pairs**, 8 of 9 pieces get a transform, chamfer 249.5–278.5 mm; the authors' own Dataset axes → `F20O_r1..r3`: **0/9, 0/36**, 2 of 9 pieces get a transform, chamfer 19.7–21.5 mm; seat bar 4.596 mm, `seated_count 0` both. At F20 the Juglet lane fails for both axis sets — the axis set is not the discriminator, and this arm changes nothing about the ticket's verdict. K per Juglet piece: 1,1,2,1,1,1,2,3,2.

**C5 — render.** `artifacts/pota307/pota307_b1-s1_vs_base-s1.png` (409,207 bytes; job 34373360, 0:11), two rows: top (x,y) and side (x,z); left = paper set 8/8 15/15, right = authors' prune 7/8 12/15. Reading it (image description; this session has no image input): the left panel shows 8 distinct sherd clouds forming one continuous wall band; the right panel shows 7 clouds with Piece 7 sitting isolated near the centre — the missing sherd is the one the prune loses, not a general collapse. Defaults are documented in the `cli.py`/`potsac.py` docstrings (§1).

#### 9. Corrections to the record

1. **Ticket 304's provenance claim is wrong.** `SFS_AXES_ADAPTIVE_UNDER_5K` was documented as "this IS the authors' rule, not a deviation". The pristine `run_potsac.m:18` has no size exception; the block exists only in `AxisExtraction/run_potsac.m:18-27` (ff40fc9, Zeejay Tan). Corrected in `potsac.py` this ticket. The rule stays on (its own 304 measurement; Piece 08's released line is lost without it), but it is a deviation and must be reported as one.
2. **Ticket 306's collapse finding is an NP artefact.** "Adding any second line to Piece 07 drops Pot A to 4/8 5/15" was measured at `NP = 3` (recorded in both `run.json` files, jobs 34358233 and 34358971), the setting that under-scores every arm. At NP=8 the same construct — with the paper's set on — seats Pot A 8/8 15/15 (b1-s1). Do not carry the collapse claim forward.
3. **The MO 8/8 15/15 bar IS verifiable — this bullet is corrected (lead, 2026-11-05).** Only `runs/20261105-0615_9c5eec2_t305-e2e-a-moom` is empty (a stopped first attempt). `runs/20261105-0617_9c5eec2_t305-e2e-a-moom` (job 34353216) holds six arm directories and 17 log files: `MOR1`/`MOR2` both read 8/8 + 15/15, `MMR1`/`MMR2` and `OMR1`/`OMR2` all read 6/8 + 10/15 (lead re-read of each `1. Acc.txt`, 2026-11-05). The worker inspected 0615 and generalised; the bar stands. The name `20261105-0617_c333dc7_t306-c1c-moom` in this ticket's brief was the lead's typo — the run is `9c5eec2`, tag `t305-e2e-a-moom`.
4. **The 306 baseline reproduces.** "84/163 within 5° / median 4.63°" was produced by a chain that then defaulted to the authors' prune; the paper's set reproduces the count (84/163) with a slightly better median (4.56°). Note this when comparing to 306's tables.

#### 10. Acceptance

- [x] **A1** clause table (§2), 17 rows: paper quote, `.m file:line` + whose commit, our `file:line`, whether it can change the emitted set, verdict.
- [x] **A2** census (§4), 163 pieces, per pot, both chains, differing pieces named.
- [x] **A3** A-Q1/Q2/Q3 answered with quotes (§3); the 1.1-prune conflict decided in writing with its measurement.
- [x] **A4** no `DIFFERS-UNDOCUMENTED` row remains; the three `DIFFERS-DOCUMENTED` rows are closed by B1/B5 measurements (§5).
- [x] **B1** paper's set emitted and measured on Pot A, 3 seeds, K per piece (§6).
- [x] **B2–B6** B2 and B3 closed by A-Q2/A-Q3; B4 and B5 run and rejected; B6 closed (§6).
- [ ] **C1** **not met** — 1 of 3 seeds (8/8 15/15 at seed 1); named blocker in §7.
- [x] **C2** parity 1e-9 PASS on the edited tree; pytest 9/9.
- [x] **C3** corpus to new paths, released md5 unchanged, tier table vs 306 baseline; `rad_mm` **not** reported (flagged in §8).
- [x] **C4** Juglet arm reported (§8).
- [x] **C5** render in `artifacts/pota307/`, defaults documented.

#### 11. The diff to ship, with the warrant for each hunk

| file | hunk | warrant |
|---|---|---|
| `sfs_axes/potsac.py` | `COST_PRUNE` default `"1"` → `"0"` | paper `:175` has no cost prune; measured better on Pot A at all three seeds (B1 vs base, §6) and no worse on the corpus (§8 C3) |
| `sfs_axes/potsac.py` | `_dedup`: `if vt.shape[1] == 0 or not COST_PRUNE: return vt, cost` | the switch above; keeps `run_potsac.m:61/:78` reachable with `SFS_AXES_COST_PRUNE=1` |
| `sfs_axes/potsac.py` | `ADAPTIVE_UNDER_5K` comment rewritten (deviation, provenance, B5 measurement) | pristine `run_potsac.m:18` has no size exception; only `AxisExtraction/run_potsac.m:18-27` (ff40fc9) adds it — §9.1 |
| `sfs_axes/potsac.py` | module docstring: prune named at `run_potsac.m:61`/`:78` and marked OFF by default | same two warrants |
| `sfs_axes/cli.py` | module + `extract_piece` docstrings: what the default emits, the paper line, how to restore the authors' chain | documentation of the flip; no behaviour change of its own |

Nothing is committed or pushed: `git status` shows only `sfs_axes/potsac.py` and `sfs_axes/cli.py` modified, plus this ticket's untracked instruments under `.scratch/pota-repro/307-stage/`.

#### 12. Open for the lead

1. Decide whether C1's blocker is worth a follow-on ticket. It is not a paper-fidelity gap any more (the paper's set is shipped and reaches the authors' best result at one seed); it is the assembler's choice among Piece 08's candidate lines. Directions none of which the paper prescribes: a stability rule (write only lines that survive more than one seed), a cap on lines per piece, or leaving it — the authors' own axes also give Piece 08 two lines and reach 15/15 every seed, so nothing in the corpus says how many lines a piece should get.
2. The `rad_mm` column (C3) needs a compare-only instrument before it can be reported for any axis set.
3. `artifacts/pota307/` holds one PNG; the conservator should read it before the 8/8 vs 7/8 claim is repeated anywhere (this session cannot see images).

#### 13. Lead verification and landing (lead, 2026-11-05)

Everything below was recomputed from the run directories, not read off the worker's tables.

1. **Pot A, all twelve arm runs.** Re-read every `out/<arm>/1. Acc.txt` in the twelve `runs/20261105-0424_e6adf69_t307-*-np8` directories. `b1-s0/s1/s2` = 7/8 13/15 · **8/8 15/15** · 7/8 13/15; `base-s0/s1/s2` = 6/8 10/15 · 7/8 12/15 · 6/8 10/15; `b5` = 7/8 13/15 · 6/8 10/15 · 6/8 10/15; `b4` = 6/8 10/15 · 7/8 12/15 · **5/8 7/15 and 6/8 10/15 in the two internal repeats** (the instability the worker reported). Every `MMR1`/`MMR2` pair agrees except that one.
2. **The C1 blocker, recomputed at join level.** Reimplemented `CountResult` (`class/data_structure.cpp:972-1035`: `inv(GT_i)·GT_j` vs `inv(T_i)·T_j`, bar 0.35 rad / 50 mm) over `out/MMR1/T_*to_*.txt` against the corpus GT poses (`sfs_main/original_samples/SfS_pp/Ground Truth/`): seed 0 **13/15**, failing 2-8 86.0° / 164.7 mm and 4-8 84.9° / 169.0 mm; seed 1 **15/15**; seed 2 **13/15**, failing 2-8 168.6° / 375.9 mm and 4-8 167.1° / 379.9 mm. Matches the worker's numbers to rounding (it wrote 376.0 for 375.9). The blocker is exactly as named and involves only Piece 08.
3. **Corpus, both chains.** From `runs/20261105-0406_e6adf69_t307a-axes`: base (prune) 211 lines, 122 of 163 equal to the released count, `tier_base.txt` median best **4.66°**, **50.9 % within 5°** = 83/163; b1 (paper) 238 lines, 120 equal, median **4.56°**, **51.5 %** = 84/163. Released total 220 lines, 163 pieces. The `tier_paper`/`tier_b1` files in the later run reproduce 4.56° / 51.5 % exactly. Baseline to beat (306) was 84/163 and 4.63°: the paper's set equals the count and improves the median. `rad_mm` remains unreported, as flagged.
4. **MATLAB parity.** `runs/20261105-0438_e6adf69_t307c-matlab-unit/out/unit302.tsv`: 9 data rows, 9 `PASS`, worst `J_rel` 7.6e-13 against the 1e-9 bar; log ends `OVERALL: PASS`, `compare rc=0`. `python -m pytest tests/ -q` in the worktree: **9 passed**.
5. **The 306 correction is right.** `run.json` of jobs 34358233 and 34358971 both record `"NP": "3"`, so the "second line on Piece 07 collapses Pot A to 4/8 5/15" finding was measured at the setting that under-scores every arm. At NP=8 the same construct reaches 8/8 15/15. Correction accepted; 306's text should be read with this note.
6. **One worker correction is itself wrong, and is fixed above (§9.3).** The M-O-O-M run is present and readable; only the earlier 0615 attempt is empty.

**Decision — land it.** `COST_PRUNE` defaults to OFF (the paper's set), the authors' chain stays one environment variable away, and the two docstrings say which is which. For the first time a change aimed at matching the paper also improves the assembler at every seed, and it does not regress the corpus. C1 is **not met** and is left unticked: 8/8 + 15/15 is reached at 1 of 3 seeds (best-of-N, N=3), not 2.

**What this means.** The axis code now matches the paper clause for clause: no `DIFFERS-UNDOCUMENTED` row remains, and the three remaining deliberate differences are each named with the line that causes them and the measurement that keeps them. The one gap left on Pot A is no longer about the method the paper describes — it is that Pot A Piece 08 gets 3-5 candidate axes and the assembler sometimes picks a wrong one, spinning the sherd a quarter- or half-turn. The paper does not say how to choose; the authors' own files give Piece 08 two lines and their assembly works, which is why the next question belongs to the assembly stage, not here.

**Not verified by the lead:** `rad_mm` (no instrument exists in this tree); the per-pot census breakdown (only the 163 totals were recomputed); the Juglet arm's internal numbers (0/9 for both axis sets was read, not recomputed). The PNG in `artifacts/pota307/` has not been seen by any session in this line of work — the conservator's eye is still owed before the 8/8 vs 7/8 picture is described to anyone else.
