# 316: E2E sweep — every sample pot and the Juglet on the 315 axes, and the table the default decision needs

**What to build:** Run the full end-to-end chain (our axes -> our breaklines -> the authors' assembler) on **all ten sample pots and the Juglet** with the 315 axes, and produce one table that says, per pot, how many sherds and joins seat. The point is not a scoreboard for its own sake: 313-315 changed how an axis is generated for **every** piece of **every** pot, yet only three pots (A, B, G) and one pot's axes (E) have been run since. D, C, F, I, J and the Juglet are still standing on the 310 numbers, and the 315 thresholds were set on seven Pot E shoulder pieces. The sweep is what turns "the rule works on E" into "the rule works", or shows where it does not.

Answers: E1
Blocked by: none (315 landed on `main`, `005eb38`)
Status: ready-for-agent
Worker: unassigned
Budget: large 16 (two nights; the corpus axes job alone is ~3 h on 20 workers)
Hand-over: worker with Spartan access; needs `sfs_axes`, the pristine SIF assembler (`/data/gpfs/projects/punim2657/sfs_main/sfs_pristine_assembly.sif`) and ~48-CPU Sapphire jobs. Judgement stays with the lead.

## Why now, and the three things missing

1. **Only three pots have been run on 315.** A 8/8 + 15/15 and B 9/9 + 15/15 (two repeats each), G 4/7 + 1/10 at K<=3 with 7/7 + 10/10 reported at K=6. D (24/28 + 49/69 at 310), I (26/26 + 62/62 at 310), C, F, J and the whole Juglet have **not** been run since the axis generator changed.
2. **Determinism is not established and the E repeats disagree.** Four E arms at K=2/K=3 gave 29, 30, 31, 30 sherds but 57, 58, 62, 51 joins — the same inputs twice, different results. A sweep whose repeats disagree cannot rank arms, so Stage 0 settles this first.
3. **The 315 thresholds were tuned on 7 pieces of one pot.** Wall-slope band `0.50 < mean|a.n| <= 0.925`, clearance `25-105 mm`, `cw <= 0.0095`, promotion at `c_cone < 0.80 * c_cyl` or basin support `>= 50` with `c_cone < 0.95 * c_cyl`. Seven examples is enough to fix one pot and too few to claim a rule; only the sweep says whether other pots' shoulder pieces pass or are damaged.

## The evidence the sweep starts from (lead-verified)

- Pot E, axes315, 31 scored pieces: **every piece carries a line within 10.0 deg of the authors' axis**; 20 at rank 0, all 31 within the top 3; worst 9.99 deg (piece 31), then 24 at 9.59, 23 at 9.27. The 10-deg bar is being met with almost no margin on those three — report the per-piece angle, do not hide behind the pass count.
- Pot E assembly, run `20261108-0430_c1fed82_t315b-kladder-E` (job 34481205): `E_MOR1/2` 31/31 + 62/62; `E_K1R1` 21/31 + 36/62; `E_K1R2` 24/31 + 39/62; `E_K2R1` 30/31 + 58/62; `E_K2R2` 29/31 + 57/62; `E_K3R1` **31/31 + 62/62**; `E_K3R2` 30/31 + 51/62.
- Pot A `20261108-0608_c1fed82_t315c-pota-mm` (job 34482837, 36 min): `MMR1/2` 8/8 + 15/15.
- Pot B `20261108-0430_c1fed82_t315c-potb` (job 34481231, 58 min): 9/9 + 15/15 in all four arms.
- Pot G `20261108-0430_c1fed82_t315c-potg` (job 34481232, 47 min): `MOR1/2` 7/7 + 10/10; `MMR1/2` 4/7 + 1/10 at K<=3. **G is the warning**: truncating to 3 lines costs it, so the sweep must keep a K=6 arm.
- Corpus unchanged in every 315 job (`corpus.diff` empty). The corpus is 163 pieces: A 8, B 9, C 6, D 32, E 34 (31 scored), F 7, G 7, H 11, I 30, J 19. H has no GT-bearing pipe and must **refuse**, not seat.

## Stage 0 — determinism (do this first; it is cheap and it gates everything)

Run one arm twice with byte-identical inputs (`E_K3`, same axes, same lane, same tree recipe) and diff the two runs' per-join results, not just the counts.

- If they differ: find the random source. The obvious suspect is `class/axis_estimation.cpp:139-140` (`std::random_device rd; std::mt19937 gen(rd());`) — confirm it is on the assembly path before changing anything, and if it is, make the seed settable and record the seed in `run.json`.
- If it cannot be made deterministic inside the harness patch guard, run **3** repeats per arm for the whole sweep and report **median and spread** plus the union of seated sherds across repeats. Never quote the best repeat alone.

## Stage 1 — regenerate the corpus axes with the current code

Run the axes stage on all 163 pieces from `main` (`005eb38` or later) with the union path and the 315 code, writing to a fresh `out/axes316`. Two requirements:

- Pot E files must reproduce `axes315` (`/data/gpfs/projects/punim2657/SfSpp/runs/20261108-0415_58594b5_t315a-axes/out/axes315`) — same lines, same order, within 1e-6, or the difference explained line by line.
- Record wall time and worker count (the 310 corpus run was 11 516 s on 20 workers; a large change means something regressed).

## Stage 2 — the axis table (cheap, run it before any assembly)

For every piece of every pot: the smallest angle from our lines to the authors' released axes, **its rank in the file**, and the line count. Then per pot: how many pieces have a <=10 deg line at K<=3 and at rank 0. Write the per-piece TSV to `artifacts/pota316/axes/`, one file per pot.

This is where a generalisation failure will show first and cheapest. If a pot's count drops below the 310 number, say which pieces and how far before spending node hours on assembly.

## Stage 3 — the assembly table, all ten pots

Reuse `20261108-0430_c1fed82_t315b-kladder-E/submit.sbatch` unchanged except `POT`, `NAMED`, `NP`, `ARMS` and `AX_315`. Arms per pot: `MO` (authors' axes, control), `K3`, `K6`; two repeats each (three if Stage 0 could not be fixed). One job per pot, `--cpus-per-task=48`, `--time=04:00:00`, lanes from `20261105-0445_9c5eec2_t305-lane-e2/out/geom`, `AX_BASE` from `20261105-0532_d330469_t308a-axes/out/axes_paper` for the paper-chain control row.

Record per arm: `CountResult` counts, the **per-piece seated list**, the **connected components** (E's failure mode was a 2-piece island passing the lenient per-sherd bar — `17` and `18` counted as seated while 55 deg off the pot), and every failing join with its angle and distance. H gets `MO` only, and the recorded outcome is whether the pipeline refuses it.

## Stage 4 — the Juglet

The Juglet has no released axes, so it is scored against the ticket 68 hybrid baseline, not against a reference. Run the same arms through `308-stage/jug308.sbatch` and report mutual-consistency median **and tail**, naming pieces 3, 8 and 9 (baseline 68: median 12.31 deg, pieces 8 = 16.4, 9 = 23.8, 3 = 10.8; our 302-era port: 12.35, 34.4, 55.6, 20.1). Best-of-N, with N stated.

## Stage 5 — renders and the verdict

- One seating render per pot into `artifacts/pota316/renders/`, plus a side-by-side for the pot that changed most and the pot that changed worst. Renders are for the conservator's eye; the tickets still owe that check.
- Verdict, in this order: the table; which pots are seated and at what K; which pots broke and at which stage (axes vs assembly); whether the 315 rule should become the default or stay behind `--union`; and the claim type for each failure — (1) the method, (2) the measurement, (3) the reference.

## Acceptance

- [ ] A1: the determinism answer — two identical runs diffed per-join; if they differ, the RNG source named at `file:line` and either a seeded fix that reproduces, or 3 repeats per arm with median and spread used everywhere.
- [ ] A2: `axes316` regenerated from `main` for all 163 pieces; Pot E reproduces `axes315` within 1e-6 (or the diff explained); wall time and worker count recorded.
- [ ] A3: the per-pot axis table — per-piece TSV in `artifacts/pota316/axes/`, with the pot-level count of pieces having a <=10 deg line at K<=3 and at rank 0.
- [ ] A4: the assembly table for A-J: `MO`, `K3`, `K6`, repeats, `CountResult`, per-piece seated lists and connected components; every failed piece named. H is a refusal check.
- [ ] A5: no-regression proof on A and B (8/8 + 15/15 and 9/9 + 15/15 in every rule repeat), and the G K=6 row, since G is the pot that needs the extra lines.
- [ ] A6: the Juglet run against the ticket 68 hybrid baseline, best-of-N stated, pieces 3, 8, 9 reported with their angles.
- [ ] A7: job IDs with `sacct` State/ExitCode in Comments; renders in `artifacts/pota316/renders/`; corpus `0 diff`; nothing committed by the worker.

## Instruments that already exist (reuse, do not rewrite)

- Per-pot assembly job: `20261108-0430_c1fed82_t315b-kladder-E/submit.sbatch` — it already parameterises `POT`, `ARMS`, `NREP`, and reads `AX_MO`, `AX_BASE`, `AX_315`.
- Corpus axes: `310-stage/corpus310.py` and `20261105-1215_1a6f16e_t310b3-timing` for the shape and the timing.
- Juglet: `308-stage/jug308.sbatch`; the 68 baseline write-up is in the juglet lane.
- Scoring: the assembler writes `1. Acc.txt`; per-join truth comes from `T_<i>to_<i>.txt` against `original_samples/SfS_pp/Ground Truth`, bar 0.35 rad / 50 mm (`class/data_structure.cpp:977`).

## Rules that apply to this ticket

- **One variable.** The axes change; nothing else. Do not tune a threshold per pot and do not "fix" a failing pot inside this ticket — report it, and the next ticket acts on it.
- Compute nodes only; every `sbatch` gets a poll and its `sacct` State/ExitCode recorded; comments-only edits to this ticket; no commits by the worker.
- A number that cannot be put physically (degrees, millimetres, sherds seated) is a warning about the measurement.