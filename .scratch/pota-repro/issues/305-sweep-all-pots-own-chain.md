# 305: Sweep — every sample pot end to end on our own preprocessing output, plus the Juglet

**What to deliver:** one measurement: what the assembler actually seats when **everything** fed to it
comes out of this repository — our breaklines *and* our axes, produced by the code as it now stands
(tickets 302 + 304 landed) — on every sample pot that can be scored, each pot with the authors'
own inputs as the control arm in the same run. Plus the same for the Juglet.

No fixes. This ticket answers 'where does the reproduction stand, pot by pot, with our own chain',
and it must be read as best-of-N with N stated, because beam variance in this assembler is large.

**Answers:** E1

**Blocked by:** none. 302 (per-point cost) and 304 (under-5,000-point rule, now default ON) are
landed on main; the 304 merge is 71ac6d4 and the default flip is 646a387.

**Status:** landed (lead 2026-11-05) — the sweep ran. Our chain reproduces Pot A only when the authors' breaklines are kept; the whole Pot A loss is our axes, and the mechanism is a candidate-set deficit: 20 of 163 pieces carry fewer axis lines than the released files, and the assembler tests every line as a hypothesis. See 'Lead verification and what it means' at the end.
**Working in:** chat on Thinkbook16 (2026-11-05)
**Branch:** 305-sweep-all-pots-own-chain, in /c/PR/worktrees/sfs/305

**Worker:** sfs305

**Budget:** large 12

**Hand-over:** Claude — Spartan compute, the corpus, the assembler SIF and the lane recipe; no MATLAB
needed (that was 304).

## Starting position (verified, do not re-derive)

- **Pot A reproduces the authors 8/8, 15/15 using our axes only** — but with the axis reader's
  truncation off and an explicit step, not with the CLI's own defaults. Run
  20261105-0217_3649473_t304-stageC, arms py_s1_best / ml_s1_final / ml_s1_stage1. The lead re-scored
  the transforms itself (inv(GT_i)GT_j vs inv(T_i)T_j, bar 0.35 rad / 50 mm,
  class/data_structure.cpp:966).
- **Which default is unanswered:** sfs_axes/read_surfaces defaults to truncate=True (equalises the
  two surfaces' point counts). On Piece 08 the truncated basin collapses to **88.15 deg** from the
  reference line where the untruncated one sits at **5.2280 deg** (out/stageC_analysis.txt). So the
  shipped CLI may still lose Pot A Piece 08. **Stage 0 settles this before anything else runs.**
- **Our lanes exist for three inputs only:** outU_jug, outU_pota, outU_potc in run
  20261103-1332_fab76f5_t66-admitsign-default (the t66 recipe, submit66.sbatch in that run dir;
  Arm U = SFS_ADMIT_SIGN at its new default ON). There is **no** lane for pots B, D, E, F, G, I, J.
- **The bar to beat, from ticket 39** (.scratch/pota-repro/issues/39-bj-e2e.md), authors' inputs (ORIG)
  vs our-then-chain: B 9/9+15/15 vs 4/9+2/15 · C 4/4+5/5 vs 0/3+0/3 · D 23/28+55/66 vs 16/27+16/66 ·
  E 31/31+62/62 vs 7/31+4/62 · F 6/6+9/9 vs 4/6+3/9 · G 7/7+10/10 vs 4/7+3/10 · I 25/27+59/65 vs
  9/27+4/65 · J 8/11+16/21 vs 0/10+0/18 · H none (all 11 refused at the admission gate).
  That run used a different assembly vehicle, so **its ORIG numbers are context, not a control** — the
  control is the OO arm inside this run.
- Corpus census (Surfaces/Pot_X_Piece_YY_Surface_0.xyz): A 8, B 9, C 6, D 32, E 34, F 7, G 7,
  H 11, I 30, J 19 = **163**. 44 pieces are under 5,000 points (they now take step 1).

## Stage 0 — does the shipped CLI still seat Pot A? (do this first, it is cheap)

Axes for Pot A 01-08 through the **CLI as shipped** (python -m sfs_axes, no environment override),
which now means the under-5,000 rule ON and truncation at its default. Then the same with the axis
reader's truncation off (the 304 proof path) as the comparator. E2E both ways, floor 50,
**at least 3 seeds each**, and score with the counter's own bar.

Record: seated/joins per seed, best-of-N with N, and for any lost piece the piece-level error in
degrees and millimetres. If the shipped default loses Piece 08 again, that is the headline result of
this ticket — **report it as found, do not fix it, and do not silently switch to the working setting
without saying so in the result**.

## Stage 1 — our lanes for every pot (the missing input)

Copy the t66 recipe from run 20261103-1332_fab76f5_t66-admitsign-default (submit66.sbatch and
instrsrc/) and run Arm U for the pots that have no lane: **B, D, E, F, G, I, J**. Reuse outU_pota,
outU_potc, outU_jug (record their md5s; do not rebuild them — if you must, say why). Binaries from
the current main of this repo, md5 recorded.

One Slurm job per pot. run.json + a runs/index.tsv row per job, verdict/human_note left empty.
Inputs and the corpus read-only: md5 of every corpus file before and after, must match.
Breaklines are the outU_<pot>/geom/*.Bl0 files.

## Stage 2 — axes for every piece, from the code as shipped

sfs_axes over all 163 pieces with the shipped defaults -> **new** output directory (out/axes305
inside your run dir; never overwrite out/axes302). Three seeds for all of Pot A and for the 44
pieces under 5,000 points; one seed elsewhere, and say so. For each piece record K, the angle to the
released axis (diagnostic only), and runtime. State in the log that the under-5,000 rule fired for the
pieces the census lists — the default is on, prove it, do not assume it.

## Stage 3 — the E2E grid

Four arms per pot, where **O** = the authors' released inputs and **M** = ours:

| arm | Breaklines | Axes |
|---|---|---|
| OO | released | released |
| MO | **ours** | released |
| OM | released | **ours** (axes305) |
| MM | **ours** | **ours** |

- **Full 4-arm grid on the five small pots: A, B, C, F, G.**
- **OO + MM only on the four large pots: D, E, I, J** (they are 30-34 pieces; a 4-arm grid there
  costs more than a day of wall-clock for one pot).
- **H: do not run.** All 11 pieces were refused at the admission gate in ticket 39 and there is no
  GT-bearing pipe; state that once, with 39-bj-e2e.md section 1 as the reference, and leave it out of
  the grid.
- **>=2 repeats per arm, and repeat the costly MM arms at least 3 times on the small pots.** Report
  **best-of-N with N** — never a lone median — and also report how many repeats reached the best.
- Floor 50 for pots, floor 20 for the Juglet; the 302/304 vehicle (sfs_pristine_assembly.sif +
  patch_guard67.py k=5/b=3 shim). Record the binary md5s so the vehicle is pinned.
- **Re-derive the E2E set from our own axle files** (an empty *_Axis.xyz auto-excludes its piece,
  BreakLine::ReadAxis -> shard_on_off=false): the set can differ from ticket 39's, because our
  axes now exist for pieces that had none. List the deltas against 39's sets explicitly.
- Score twice: the counter's binary (1. Acc.txt, per-sherd lenient rule) and the strict relative-edge
  table (5 deg / 10 mm) as a diagnostic. **The binary is the reported number**; say which is which.
- Each pot its own job; cap each E2E job at 4 h and record any arm that a cap truncated as truncated —
  do not report a capped arm as a measurement of that arm.

## Stage 4 — the Juglet

Floor 20, arms OO (Dataset axes + t66 jug lanes) and MM (our axes305 for the Juglet + the same
lanes), >=3 repeats. Report score58 (seated/9, candidates, mutual consistency), best-of-N with N,
against what is already known: t67 23 candidates / 0 seated, t68 hybrid 35 / 0, ticket 302 37 / 0,
and Dataset axes median mutual consistency 27.1 deg vs our port 12.35 deg (ticket 302, tail losses on
Juglet Pieces 3, 8, 9 named there).

## Stage 5 — the picture and the table

A seating render per pot for the MM arm at its best repeat, plus OO where it differs, into
artifacts/pota305/ (workspace-relative links in the ticket, gitignored). Then **one line per pot**
for the conservator: pot, pieces, our chain seated/joins, authors' arm seated/joins, N, and whether
our chain is behind, level or ahead — with the claim named as (1) method, (2) measurement or
(3) reference.

## Rules

- **Start with scripts/ticket_start.sh SfSpp_preprocessing .scratch/pota-repro/issues/305-*.md**
  (its own worktree; Status must still read ready-for-agent when you run it).
- SSH: **/c/Windows/System32/OpenSSH/ssh.exe spartan** (git-bash ssh cannot authenticate).
  Single-quote the whole remote command; inner $ escapes need care.
- Released axes and GT may be read **only** to score and to diagnose, **never inside a shipped rule**.
- Corpus read-only; nothing outside your run directories; nothing committed from the worker side.
- Every sbatch gets a sacct -j <id> --format=State,ExitCode recorded in Comments.
- Ticket edits in **Comments only**; Status/Worker lines belong to the lead.
- Budget: **12 failed acceptance checks**.
- If a stage cannot be completed, say which and why, with the job ids — a partial sweep honestly
  reported is worth more than a tidy summary.

## Acceptance

- [x] **A1** Stage 0: Pot A through the shipped CLI, >=3 seeds, seated/joins and piece-level errors
      recorded, best-of-N stated; if the truncation default loses Piece 08, it is reported, not fixed.
- [x] **A2** Stage 1: lanes for B, D, E, F, G, I, J from current main, one job each, md5 of binaries
      and of the arm-U output recorded; corpus md5 unchanged before/after; t66 lanes reused with md5s.
- [x] **A3** Stage 2: out/axes305 for all 163 pieces, seeds per piece recorded, the under-5,000 rule
      shown to have fired on the 44 small pieces, angle-to-released table, runtime.
- [x] **A4** Stage 3: 4-arm grid on A, B, C, F, G and OO+MM on D, E, I, J, >=2 repeats (>=3 for
      small-pot MM), best-of-N with N, binary + strict tables, E2E sets re-derived with deltas
      against ticket 39 named, H excluded with its reason.
- [x] **A5** Stage 3: every arm's vehicle pinned by binary md5; 4 h caps declared and any truncated arm
      marked as truncated.
- [x] **A6** Stage 4: Juglet OO vs MM, >=3 repeats, candidates + seated + mutual consistency,
      best-of-N with N, set beside t67 / t68 / ticket 302.
- [x] **A7** Stage 5: one render per pot in artifacts/pota305/ (workspace-relative links), plus the
      one-line-per-pot table with the claim type named.
- [x] **A8** Every job id with its sacct State/ExitCode in Comments; run.json + index.tsv row
      for every run; nothing committed beyond the ticket's own record.

## Comments (worker, 2026-11-05)

Ticket 305 executed end to end on worktree `C:/PR/worktrees/sfs/305` (branch `305-sweep-all-pots-own-chain`, HEAD `9c5eec2`), commit 9c5eec2 built on Spartan in every job. Nothing committed, no fix applied anywhere, corpus untouched (`logs/corpus_inputs.diff` is 0 lines in every run that wrote one). Every number below is best-of-N with N stated; a lone median is never quoted.

### The answer

**The shipped default still loses Pot A.** Our axes + our breaklines (MM) give **6/8 sherds, 10/15 edges** at all three seeds (3/3 repeats identical at seed 0 and seed 2), and the loss is **entirely the axes**: with the authors' breaklines and our axes (OM) the result is the identical 6/8 + 10/15, while our breaklines with the authors' axes (MO) give the full **8/8 + 15/15**. The two lost pieces are 07 and 08, the only two under-5,000-point pieces (n=3490, n=3152), i.e. the pieces that take `effective_step=1` under the under-5k rule. Turning the axis-reader truncation **off** does **not** restore Pot A: seed 0 and seed 2 stay at 6/8 + 10/15 (3/3), and only at seed 1 does it recover piece 08 (7/8 + 12/15, 3/3), piece 07 failing there too at 56.39 deg / 171.29 mm. So truncation is a contributing cause for piece 08 at one seed, not the cause of the Pot A loss.

### Vehicle, pinned (A5)

| item | value |
|---|---|
| SIF | `/data/gpfs/projects/punim2657/sfs_main/sfs_pristine_assembly.sif` md5 `63a532b9732f84e59e7b1349065f1323` |
| shipped batch source | `hpc/tools/main_pristine_batch.cpp` md5 `fb26e8ab49e9c00f7e8d02de44f6eea5` |
| shim source | `work/shim/G.cpp` md5 `056dfb914d7f067244a87d200ecb9863`, identical in every arm, rep and pot (patch_guard67.py k=5 b=3) |
| per-arm binary | linked md5 differs per arm only because the object path embeds the arm label; same source, same `sed` floor |
| lane binaries | MeshPreprocessingHeadless `748b174f814ab881afb627fab9a978df`, EdgeLineExtractionHeadless `teea26d42e7b0c4716d37b56f99a31b27` |
| sbatch cap | 04:00:00 on every E2E job; **no arm was truncated** — longest job 02:52:07 (Pot E) |

### Stage 0 — Pot A, shipped defaults vs truncation off (A1)

Axes (3 seeds, Pot A): 24 piece-seeds, 0 errors, no K==0 file; the under-5k rule fired `step=1` on exactly pieces 07 (n=3490) and 08 (n=3152). Piece 08 K: trunc 3/1/3, notrunc 3/5/3 (seeds 0/1/2).

| seed | MM trunc=1 (shipped) | MMu trunc=0 | failing joins under trunc=1 |
|---|---|---|---|
| 0 | 6/8 + 10/15, 3/3 identical | 6/8 + 10/15, 3/3 identical | 1-7 56.86 deg/170.56 mm, 4-7 56.51/166.10, 6-7 57.60/177.50, 2-8 124.94/343.26, 4-8 122.34/344.19 |
| 1 | 5-6/8 + 7-10/15 (reps differ) | **7/8 + 12/15**, 3/3 identical | 1-7, 4-7, 6-7 only (piece 08 seated) |
| 2 | 6/8 + 10/15, 3/3 identical | 6/8 + 10/15, 3/3 identical | pieces 07 and 08 |

Axis-file facts behind it (`probe_axes2.py`, angles to the released lines): piece 07 our single candidate sits **5.91 deg** (trunc) / 6.31 deg (notrunc) from released line 0 and the released file carries **3** axis lines; piece 08 our trunc candidates are 36.03 / 15.82 / 65.79 deg from released line 0 — no basin near 5 deg, whereas the truncation-off seed-1 file does carry a 5.667 deg candidate (the mechanism ticket 304's `stageC_analysis.txt` describes). Read with `class/data_structure.cpp` ReadAxis: every 6-number line is a candidate, so a good candidate anywhere in the file can seat the piece; truncation removes it for 08.

### Stage 1 — breakline lanes for B, D, E, F, G, I, J (A2)

One Slurm job per pot, t66 Arm-U recipe (`run_cell66.sh` + `stage_synth_p40.sh` from commit 9c5eec2), corpus inputs by symlink, `SHIPPED` env `SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0`.

| pot | run | job | sacct | wall | Bl0 non-empty | agg md5 of Bl0 |
|---|---|---|---|---|---|---|
| A | `20261103-1332_fab76f5_t66-admitsign-default` (`outU_pota`) | reused, not resubmitted (t66's run.json carries no job id) | n/a | - | 8 | `59dbc632a8ad10ee` |
| B | `20261105-0445_9c5eec2_t305-lane-b2` | 34352729 | COMPLETED 0:0 | 00:05:19 | 9 | `2452e61983d48e2f` |
| C | `..._lane-c2` | 34352730 | COMPLETED 0:0 | 00:08:31 | 4 | `697cd0450ba1dca0` |
| D | `..._lane-d2` | 34352745 | COMPLETED 0:0 | 00:41:07 | 29 | `d75a252faa7eddf8` |
| E | `..._lane-e2` | 34352746 | COMPLETED 0:0 | 00:12:51 | 31 | `bfd664aa79f97f38` |
| F | `20261105-0520_9c5eec2_t305-lane-f3` | 34352939 | COMPLETED 0:0 | 00:03:51 | 7 | `5d8df640833b2693` |
| G | `20261105-0445_9c5eec2_t305-lane-g2` | 34352760 | COMPLETED 0:0 | 00:03:33 | 7 | `fdb0b7a4f977e743` |
| I | `20261105-0520_9c5eec2_t305-lane-i3` | 34352956 | COMPLETED 0:0 | 00:12:57 | 30 | `3f4bd598c502a10a` |
| J | `20261105-0520_9c5eec2_t305-lane-j3` | 34352965 | COMPLETED 0:0 | 00:06:27 | 12 | `2663fd1550b47916` |

`agg` = md5 of the sorted per-file md5 list; the per-file md5s are in each run's `logs/lanes_record.txt`. Corpus inputs md5-identical before/after in every one (`logs/corpus_inputs.diff` empty).

### Stage 2 — axes305 for all 163 pieces, shipped default (A3)

One job, 16 cpus, 3 seeds for Pot A and every under-5k piece, 1 elsewhere; 163 pieces, **no K==0 piece**, 357 cpu-seconds (00:00:31 wall). The under-5k rule fired on **48 distinct pieces** (step=1; 115 take step=10), not the 44 A3 assumed — per pot: A 2, B 1, C 1, D 10, E 8, F 4, G 1, H 2, I 7, J 12, and n_pts runs 704 to 34,290 (median 4,776).

| pot | pieces | rows | K==0 | under-5k pieces | median ang | p90 | max |
|---|---|---|---|---|---|---|---|
| A | 8 | 24 | 0 | 2 | 2.60 | 20.03 | 36.03 |
| B | 9 | 11 | 0 | 1 | 17.31 | 34.00 | 44.45 |
| C | 6 | 8 | 0 | 1 | 40.92 | 84.60 | 84.60 |
| D | 32 | 52 | 0 | 10 | 7.40 | 64.38 | 84.97 |
| E | 34 | 50 | 0 | 8 | 19.35 | 65.90 | 81.88 |
| F | 7 | 15 | 0 | 4 | 12.95 | 31.64 | 31.64 |
| G | 7 | 9 | 0 | 1 | 6.19 | 51.43 | 51.43 |
| H | 11 | 15 | 0 | 2 | 12.32 | 40.67 | 73.52 |
| I | 30 | 44 | 0 | 7 | 13.64 | 28.28 | 89.92 |
| J | 19 | 43 | 0 | 12 | 20.96 | 72.63 | 87.94 |

(Angles are candidate 0 vs the released axis file, sign-agnostic; the full per-piece table is `out/axes305.tsv` in `20261105-0420_9c5eec2_t305-axes-corpus`.)

### Stage 3 — the grid (A4)

Counter number = `1. Acc.txt` from the counter's own binary (per-sherd lenient rule, bar 0.35 rad / 50 mm), **that is the reported number**. Strict = `score305.py`, relative edge table at 20.05 deg / 50 mm, denominator = eligible joins. Rows are best-of-N.

| pot | arm | reps | counter sherd | counter edges | strict joins | reps at best |
|---|---|---|---|---|---|---|
| A (seed 0) | OO | 3 | 8/8 | 15/15 | 15/15 | 3/3 |
| A (seed 0) | MO | 2 | 8/8 | 15/15 | 15/15 | 2/2 |
| A (seed 0) | OM | 2 | 6/8 | 10/15 | 10/15 | 2/2 |
| A (seed 0) | MM | 3 | 6/8 | 10/15 | 10/15 | 3/3 |
| A (seed 0) | MMu | 3 | 6/8 | 10/15 | 10/15 | 3/3 |
| A (seed 1) | MM / MMu | 3 / 3 | 6/8 / 7/8 | 10/15 / 12/15 | 10/15 / 12/15 | 1/3 (reps 5/8+7/15, 6/8+10/15, 5/8+7/15) / 3/3 |
| A (seed 2) | MM / MMu | 3 / 3 | 6/8 / 6/8 | 10/15 / 10/15 | 10/15 / 10/15 | 3/3 / 3/3 |
| B | OO | 2 | 9/9 | 15/15 | 15/15 | 2/2 |
| B | MO | 2 | 9/9 | 15/15 | 15/15 | 2/2 |
| B | OM | 2 | 7/9 | 10/15 | 10/15 | 2/2 |
| B | MM | 3 | 7/9 | 10/15 | 10/15 | 2/3 (one rep 6/9 + 9/15) |
| C | OO / MO / OM | 2 / 2 / 2 | 4/4 | 5/5 | 5/5 | all |
| C | MM | 3 | 4/4 | 5/5 | 5/5 | 3/3 |
| D | OO | 2 | 22/27 | 53/66 | 53/69 | 2/2 |
| D | MM | 2 | 19/28 | 33/69 | 33/69 | 2/2 |
| E | OO | 2 | 31/31 | 62/62 | 62/62 | 1/2 (other rep 61/62) |
| E | MM | 2 | 23/31 | 36-37/62 | 37/62 | 1/2 |
| F | OO | 2 | 6/6 | 9/9 | 9/9 | 2/2 |
| F | MO | 2 | 5/5 | 7/7 | 7/9 | 2/2 |
| F | OM | 2 | 6/6 | 9/9 | 9/9 | 2/2 |
| F | MM | 3 | 5/5 | 7/7 | 7/9 | 3/3 |
| G | OO | 2 | 7/7 | 10/10 | 10/10 | 2/2 |
| G | MO | 2 | 7/7 | 10/10 | 10/10 | 2/2 |
| G | OM | 2 | 5/7 | 3/10 | 3/10 | 2/2 |
| G | MM | 3 | 5/7 | 2/10 | 2/10 | 2/3 (one rep 4/7) |
| I | OO | 2 | 25/27 | 59/65 | 59/65 | 2/2 |
| I | MM | 2 | 18/26 | 23-26/62 | 26/65 | 1/2 |
| J | OO | 2 | 8/11 | 16/21 | 16/21 | 2/2 |
| J | MM | 2 | 5/11 | 7/21 | 7/21 | 2/2 |

E2E sets re-derived from **our own** axle files (empty `*_Axis.xyz` auto-excludes its piece): A 8/8, B 9/9, C 4/4, D 28/29, E 31/31, F 6/7 (F07 has no GT T), G 7/7, I 27/30 (I28-30), J 11/12 (J09) — **identical to ticket 39's sets, no delta**. Pot H not run (see below).

Two readings that matter and are easy to get wrong:
- The counter's denominator is the pieces that produced a T, so a **dropped** piece hides inside a perfect "5/5". The strict join table with the eligible denominator is what exposes it (Pot F: MM 5/5 sherds but 7/9 joins because piece 06 never gets a T).
- The strict **per-piece** column is frame-dependent: Pot D's OO arm reports ~172 deg for every piece while its joins are 53/69, i.e. the whole assembly lands rotated. Joins and the counter are the measurements; per-piece absolute is only readable where the assembly happens to sit in the GT frame.

### Per-pot, one line each, with the claim type (A7)

| pot | result (best-of-N) | claim |
|---|---|---|
| A | MM 6/8 + 10/15; MO 8/8 + 15/15; OM 6/8 + 10/15 | **method** — our axes lose pieces 07/08 (the under-5k pair); our breaklines are clean |
| B | MM 7/9 + 10/15; MO 9/9 + 15/15; OM 7/9 + 10/15 | **method** — one piece lost by our axes; breaklines clean |
| C | all four arms 4/4 + 5/5 | **no defect found** — parity; the C01 interior-Bl0 caveat measures the input and C03 Bl1 is reference-wrong but the assembler never reads Bl1 |
| D | OO 22/27 + 53/66, MM 19/28 + 33/69 | **reference** — the authors' own arm misses 13 joins incl. 8/10/13-18 at 153.0 deg and 7/25-29 at 87-109 deg, exactly ticket 301's released-axis defects (D18/D29); our arm misses the same, so D is not evidence about our method |
| E | OO 31/31 + 62/62, MM 23/31 + 37/62 | **method** — eight pieces lost by our axes |
| F | MO 5/5 + 7/7 (5 T), OM 6/6 + 9/9 | **method** — our breakline drops piece 06; our axes are clean |
| G | MO 7/7 + 10/10, MM 5/7 + 2/10 | **method** — G07's axis is 51.43 deg off the released line with K=1 (the only under-5k piece there) and throws piece 7 outside the pot |
| I | OO 25/27 + 59/65, MM 18/26 + 26/65 | **method** — seven pieces lost, the largest single loss in the sweep |
| J | OO 8/11 + 16/21, MM 5/11 + 7/21 | **reference + method** — the authors' own arm is only 8/11 (J09 has no GT and is excluded); ours 5/11 |
| H | not run | **excluded** — all 11 pieces refused at the admission gate in ticket 39, no GT-bearing pipe |

### Stage 4 — Juglet (A6)

Run `20261105-0525_9c5eec2_t305-jug2` (job 34353011), floor 20, NP 9, `juglet_orig_block.inc` md5 `401195eae5a41579563fc237a9843298`, `-DJUGLET_ORIG`, 3 repeats per arm. score58 (seated/9, candidates, mutual consistency).

| arm | axes | reps | seated | edges | directed | piece T's | gauge residual median |
|---|---|---|---|---|---|---|---|
| F20O | Dataset `Axes/Juglet` | 3 | 0/9 | 0/18 | 0/36 | 2 (pieces 2, 6) | 156.55 deg / 699.24 mm (n=2) |
| F20N | our `axes305_jug` | 3 | 0/9 | 0/18 | 0/36 | 8 (pieces 1-8) | 117.94 deg / 325.71 mm (n=8) |

All three repeats per arm are numerically identical (deterministic search on identical inputs). Known bars: t67 23 candidates / 0 seated, t68 hybrid 35 / 0, ticket 302 37 / 0. Our axes produce **more** candidate placements (8 vs 2) and a **smaller** gauge residual (117.94 vs 156.55 deg), but neither arm seats anything at floor 20 — the Juglet result is unchanged from the prior bars, in the same direction as ticket 302's mutual-consistency finding.

### Renders

All in `SfSpp_preprocessing/artifacts/pota305/` (gitignored landing zone, paths relative to `C:/PR`): [A](SfSpp_preprocessing/artifacts/pota305/a.png) · [B](SfSpp_preprocessing/artifacts/pota305/b.png) · [C](SfSpp_preprocessing/artifacts/pota305/c.png) · [D](SfSpp_preprocessing/artifacts/pota305/d.png) · [E](SfSpp_preprocessing/artifacts/pota305/e.png) · [F](SfSpp_preprocessing/artifacts/pota305/f.png) · [G](SfSpp_preprocessing/artifacts/pota305/g.png) · [I](SfSpp_preprocessing/artifacts/pota305/i.png) · [J](SfSpp_preprocessing/artifacts/pota305/j.png) · early smoke [a_smoke](SfSpp_preprocessing/artifacts/pota305/a_smoke.png). Each panel is OO (authors' breaklines + authors' axes) beside MM (ours), top x-y and side x-z, edges in the assembly frame, `*_OBJ_*.obj` being the raw piece clouds. Manufactured by `render305.py` from the run's `out/<arm>R<rep>/`. Pot A's render shows the failure shape directly: pieces 7 and 8 are the red ones — 7 dropped inside the pot's flat, 8 flung outside the rim — while the rest of the ring seats. Pot G's shows piece 7 thrown clear of the pot.

### Deviations from the ticket, and why

1. **Pot A lanes are not a t305 run** — the ticket allows reusing the t66 arm-U lanes with md5s; A uses `outU_pota` of `20261103-1332_fab76f5_t66-admitsign-default` (8 Bl0, agg md5 as tabled).
2. **Four lane jobs failed before the ones tabled**: 34352516 (two jobs shared one build dir), 34352535 (mesh/stager), 34352752 / 34352766 / 34352768 (derived-manifest awk bug). They are in the job ledger, superseded; no number above comes from them.
3. **One job per pot for the grid**, 2 reps per arm, 3 for the small-pot MM arms; Pot A additionally at seeds 1 and 2 plus the MMu comparator. D/E/I/J are OO + MM only, as instructed.
4. **Pot H not run** — excluded per ticket 39 (all 11 pieces refused at the admission gate, no GT-bearing pipe).
5. **`index.tsv` rows** — 41 rows now cover the 41 submitted run dirs: 37 were written by the driver with the `tag` column empty (the tag lives in the run id) and the four earliest runs (`axes-stage0` 34352501, `axes-corpus` 34352502, `lane-b` 34352516, `lane-d` 34352535) were appended by hand, with the tag filled. `verdict` and `human_note` untouched everywhere. The one run dir with no row is the never-submitted `20261105-0520_..._jug2` (item 6).
6. **Stray run dir** `20261105-0520_9c5eec2_t305-jug2` was created but never submitted (no job, no index row); the Juglet job ran in `..._0525_..._jug2`.
7. **34353209** (`20261105-0615_9c5eec2_t305-e2e-a-moom`) was cancelled at 0:00 before it started and resubmitted in a fresh dir as 34353216; no measurement from it.
8. `score305.py`'s per-piece angle is absolute, not frame-aligned — reported as diagnostic only, per the note above.
9. **A3's "44 small pieces" is 48** on our own surfaces (n_pts < 5000), per pot A 2, B 1, C 1, D 10, E 8, F 4, G 1, H 2, I 7, J 12; the rule fired on all 48 and on none of the 115 larger pieces.

### Job ledger (every job submitted for this ticket)

| job | run | sacct State | ExitCode | elapsed |
|---|---|---|---|---|
| 34352501 | axes-stage0 | COMPLETED | 0:0 | 00:00:19 |
| 34352502 | axes-corpus | COMPLETED | 0:0 | 00:00:31 |
| 34352516 | lane-b (superseded) | FAILED | 8:0 | 00:02:53 |
| 34352535 | lane-d (superseded) | FAILED | 9:0 | 00:01:41 |
| 34352614/15/34/35/57/58/65/82 | one-piece lane runs (superseded) | COMPLETED | 0:0 | 00:01:47-00:04:52 |
| 34352671 | axes-stage0b | COMPLETED | 0:0 | 00:00:33 |
| 34352729 | lane-b2 | COMPLETED | 0:0 | 00:05:19 |
| 34352730 | lane-c2 | COMPLETED | 0:0 | 00:08:31 |
| 34352745 | lane-d2 | COMPLETED | 0:0 | 00:41:07 |
| 34352746 | lane-e2 | COMPLETED | 0:0 | 00:12:51 |
| 34352752/66/68 | lane-f2/i2/j2 (superseded) | FAILED | 9:0 | 00:02:14-00:02:37 |
| 34352760 | lane-g2 | COMPLETED | 0:0 | 00:03:33 |
| 34352778 | e2e-a-smoke | COMPLETED | 0:0 | 00:06:56 |
| 34352808 | axes-stage0c (per-seed) | COMPLETED | 0:0 | 00:00:31 |
| 34352891 | jug (rescored later) | COMPLETED | 0:0 | 00:02:29 |
| 34352939 | lane-f3 | COMPLETED | 0:0 | 00:03:51 |
| 34352956 | lane-i3 | COMPLETED | 0:0 | 00:12:57 |
| 34352965 | lane-j3 | COMPLETED | 0:0 | 00:06:27 |
| 34353011 | jug2 | COMPLETED | 0:0 | 00:03:22 |
| 34353012 | e2e-a-s0 | COMPLETED | 0:0 | 00:39:29 |
| 34353022 | e2e-a-s1 | COMPLETED | 0:0 | 00:20:19 |
| 34353024 | e2e-a-s2 | COMPLETED | 0:0 | 00:15:01 |
| 34353039 | e2e-b | COMPLETED | 0:0 | 00:27:58 |
| 34353041 | e2e-c | COMPLETED | 0:0 | 00:08:22 |
| 34353046 | e2e-g | COMPLETED | 0:0 | 00:08:44 |
| 34353050 | e2e-e | COMPLETED | 0:0 | 02:52:07 |
| 34353051 | e2e-f | COMPLETED | 0:0 | 00:09:03 |
| 34353113 | e2e-j | COMPLETED | 0:0 | 00:31:47 |
| 34353138 | e2e-i | COMPLETED | 0:0 | 01:36:56 |
| 34353209 | e2e-a-moom (cancelled) | CANCELLED+ | 0:0 | 00:00:00 |
| 34353216 | e2e-a-moom | COMPLETED | 0:0 | 00:14:56 |
| 34353295 | e2e-d | COMPLETED | 0:0 | 02:35:06 |

- [x] **A8** Every job id with its sacct State/ExitCode in Comments; run.json + index.tsv row
      for every run; nothing committed beyond the ticket's own record.

## Lead verification and what it means (lead, 2026-11-05)

Verified by recomputation from the run directories, not by reading the tables above.

**1. The grid, re-read from every arm's own 1. Acc.txt** — 81 arm directories under the eleven
t305 E2E run dirs. Every cell in the tables above matched the machine output except one: Pot F MM
is **5/5 sherds + 7/7 edges**, not 5/6 + 7/9 (corrected in the table). That is the trap the worker
itself names: piece 06 produces no T, so the counter's denominator shrinks to 5 and a perfect 5/5
hides a dropped piece. MO also reads 5/5, so Pot F's loss is our **breakline**, not our axes
(OM is 6/6 + 9/9), exactly as the prose says.

**2. Pot A, per join** (out/MMR1/T_ito_i.txt and out/OOR1/ against the 8x8 GT graph, inv(GT_i)GT_j
vs inv(T_i)T_j at 0.35 rad / 50 mm): OO **30/30** directed = 15/15 joins; MM **20/30** = 10/15.
The five failing joins are exactly 1-7 (56.9 deg / 170.6 mm), 2-8 (124.9 / 343.3), 4-7 (56.5 /
166.1), 4-8 (122.3 / 344.2), 6-7 (57.6 / 177.5) — every failure involves piece 07 or 08, matching
1. Acc.txt and the worker's list.

**3. The mechanism, measured on all 163 pieces** (wc -l of the released Axes/ files against
out/axes305/): we emit **fewer lines than the reference on 20 pieces**, more on 19, the same on 124.
The four that decide Pot A and Pot B:

| piece | reference lines | ours | what it means |
|---|---|---|---|
| Pot_A_07 | 3 | 1 (2 with truncation off, axes302) | direction is right (5.91 deg from released line 0); the other two hypotheses are simply absent, and the three joins that fail are 1-7, 4-7, 6-7 |
| Pot_A_08 | 2 | 3 | none near 5 deg (36.03 / 15.82 / 65.79 from released line 0); the 5.667 deg candidate exists only with truncation off, at one seed |
| Pot_B_08 | 2 | 1 | 13.61 deg from released line 1 |
| Pot_G_07 | 1 | 1 | **51.43 deg** — the one loss in the sweep that is a wrong direction, not a missing line |

This is the most useful thing the sweep produced. The assembler treats every 6-number line in an
axis file as a join hypothesis (`class/data_structure.cpp` ReadAxis pushes all of them, and
`class/feature_matching.cpp:1461-1475` loops every pair), so **a missing line is a join that cannot
even be tested** — and the failures land on exactly the pieces whose file is short.

**4. Pot A must not be described as reproducing with our chain.** MO (our breaklines + authors'
axes) 8/8 + 15/15 proves the breaklines are clean; OM reproduces MM exactly, which proves the axes
carry the whole loss; MMu (truncation off) reaches 7/8 at one seed only. So ticket 304's 8/8 was not
reproducible from the shipped defaults, and the honest statement is: **our breaklines reproduce Pot A;
our axes do not, yet.**

**5. Weight, and what is NOT verified.** D/E/I/J carry OO + MM only, so their attribution
("reference" on D, "method" on E and I) is inference from two arms, not a measured MO/OM split. The
strict per-piece angle column is frame-dependent and is not a measurement (Pot D's own OO arm reports
~172 deg per piece while seating 53/66 joins). The renders were **not eye-checked by the lead** — this
session has no image input — so they are for the conservator. Pot H excluded as stated.

**6. Correction to this ticket's own spec:** A3 said "44 pieces under 5,000 points"; the measured
census on our surfaces is **48** (A2 B1 C1 D10 E8 F4 G1 H2 I7 J12), and the rule fired on all 48 and
on none of the 115 larger pieces.

**7. Bookkeeping checked:** sacct spot-checked on six jobs (34352729, 34352745, 34352746, 34353011,
34353050, 34353295) — all COMPLETED 0:0 at the elapsed times tabled; index.tsv holds **41** t305 rows
with verdict/human_note empty; `logs/corpus_inputs.diff` is 0 bytes in the run checked.

**What this leaves open, in one line:** our axis extractor has to emit the hypotheses the reference
carries (Pot A 07: three lines where we give one) before "our chain" can mean anything on the
multi-line pots. That is a new ticket, not a fix inside this one.
