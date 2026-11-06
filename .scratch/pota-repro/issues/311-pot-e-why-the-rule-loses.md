# 311: Pot E — why the rule seats the one pot where the reference seats everything

Answers: E1
Blocked by: none (310 landed; the rule is reachable with `--union` + `SFS_AXES_CONVERGE_BEFORE_RANK=1`)
Status: in-progress
Working in: chat on Thinkbook16 (2026-11-06)
Branch: 311-pot-e-why-the-rule-loses, in /c/PR/worktrees/sfs/311
Worker: unassigned
Budget: large 8
Hand-over: worker with Spartan access; needs the pristine SIF assembler, ~20-worker axes runs and MATLAB only if the basin table is asked for. Judgement stays with the lead.

## What to build

Pot E is the one pot where ticket 310's axis rule loses to both baselines, and it loses by a wide margin:

| arm (same job, same breaklines, same staging) | sherds | joins | run |
|---|---|---|---|
| authors' axes on our breaklines (MO) | **31/31, 31/31** | **62/62, 62/62** | 20261105-1407_1a6f16e_t310c2-E out/MOR1, MOR2 |
| our paper chain, ticket 308 (base) | 21/31 | 36/62 | 308 grid |
| our rule axes (MM) | 17/31, 18/31 | 25/62, 25/62 | same run, out/MMR1, MMR2 |

So on Pot E the breaklines, the staging and the assembler are demonstrably good enough to seat all 31 pieces and all 62 joins. **The axis set is the only variable, and ours is the worst of the three.** 13 of the 31 pieces have no correct join at all in MM (the counter is lenient: a piece counts right if it has one correct join — `class/data_structure.cpp:1026`, bar 0.35 rad / 50 mm set at `class/data_structure.cpp:977`).

The suspicion to test, not to assume: Pot E pieces carry many axis lines. Our files for Pot E hold 1 to 6 lines each (2 files with 1, 6 with 2, 6 with 3, 2 with 4, 6 with 5, 12 with 6; mean 4.18) and the assembler scores **every pair of lines on every pair of pieces** (`class/feature_matching.cpp:1464` and `:1534`, every `axis_x` × `axis_y`), admitting a pair whenever the axis angle is under 0.436 rad = 25 deg (`:1715`). More lines per piece therefore buy more chances for a wrong piece pair to pass the gate. The rule may be writing a correct line and paying for it with five decoys — or the correct line may be absent and the ranking wrong the way Piece 08 was before 310. **Those two have different fixes and this ticket's first job is to tell them apart.**

### Stage A — attribution (cheap, do first)
For all 34 `Pot_E_Piece_*_Axis.xyz` files in the rule's output (20261105-1215_1a6f16e_t310b3-timing out/axes310):

1. Is the authors' line (the one MO uses, from the staged `Axes/` of the Dataset tree) present in our file? Report the smallest angle to it and **its rank in the file**. A line within ~2 deg at rank 1-2 means selection downstream; absent or rank 5-6 means generation/ranking.
2. Which 31 of the 34 does the assembler actually count, and why are 3 dropped? Name them. This matters before any per-piece claim.
3. Which pieces fail in MMR1 and MMR2, and which joins. Build the joins from `out/<arm>/T_<i>to_<i>.txt` against `original_samples/SfS_pp/Ground Truth/Pot_E_Piece_<i>_T.txt` at 0.35 rad / 50 mm, exactly as the lead did for Pot A MMR7 in 310 — do not trust `1. Acc.txt` alone for the per-piece list.

### Stage B — one variable at a time (the K ladder)
Reuse the 310 grid harness. Same staged tree, only `Axes/` substituted, and prove it with a `substitution.tsv` of the kind 310 wrote (count of files differing, count under `Axes/`, 0 elsewhere). Pot E only, two repeats, arms:

- `E_K1` — rule pool, best line only; `E_K2`, `E_K3`, `E_K6` — top 2, 3, 6 (K6 must reproduce MMR1/MMR2).
- `E_MO` — authors' axes, the control that must reproduce 31/31 + 62/62 in the same job.
- `E_BASE` — the ticket 308 paper-chain axes, the other control (21/31 + 36/62).

The question: **does capping K restore E, and at what K does it break?** Report every arm's `1. Acc.txt`, plus the failing pieces per arm. If K=1 seats E, the rule's extra lines are the cause and the rest of this ticket is about a blind cap. If K=1 is also bad, the correct line is not in our file for the failing pieces and Stage C applies.

### Stage C — if the line is missing or badly ranked (only if Stage B says so)
Take the failing pieces and produce the same all-candidates table 310 produced for Piece 08: every 10-deg basin, refined on all points at 1e-9, with its Huber cost per point on both walls, and where the authors' line sits among them. 310 already fixed the same failure for a small sherd; this asks whether Pot E has a second, different one (thin walls, a rim-dominated cost, or a piece whose two surfaces disagree).

### Stage D — the blind cap, if K is the cause (only if Stage B says so)
A cap must be blind: no ground truth, no released axes, no per-pot tuning. Test at least two candidates on the whole corpus and the grid:

- cost-ratio: keep a line only if its worse-wall cost per point is within r × the best;
- separation: keep a line only if it is at least 10 deg from every line already kept.

Sweep r on the 163-piece corpus, then run the grid best of two for A, B, D, I (the pots 310 gained on), G (lost one sherd) and E. **A cap that fixes E and costs A, B, D or I is not a fix** — say so plainly and report the trade.

### Stage E — verdict
Name which claim this is: (1) the method, (2) the measurement, or (3) the reference. State the single blind change, or none, with the numbers, and what it costs in time. Do not change any default; 310's switch stays off by default until this is answered. Do not touch the corpus. The target is the whole sample set, not Pot E alone.

## Acceptance

- [ ] A1: the per-piece provenance table for all 34 Pot E files — smallest angle to the authors' line, its rank, line count — plus the 3 files the assembler drops and why.
- [ ] A2: failing pieces and failing joins named for MMR1 and MMR2, recomputed from the T files against Ground Truth at 0.35 rad / 50 mm (not read off `1. Acc.txt`).
- [ ] A3: the K ladder run — `E_K1`, `E_K2`, `E_K3`, `E_K6`, two repeats each — with `1. Acc.txt` per arm and a `substitution.tsv` proving only `Axes/` differed (`E_K6` reproduces 17-18/31 + 25/62).
- [ ] A4: the two controls in the same job — `E_MO` reproduces 31/31 + 62/62 and `E_BASE` reproduces 21/31 + 36/62.
- [ ] A5: if K is the cause, a blind cap (cost-ratio and/or separation) with the corpus sweep and a best-of-two grid on A, B, D, E, G, I, showing no loss on the pots that gained.
- [ ] A6: if the line is missing or misranked, the all-candidates table for the named pieces at the evidence grade of 310's Piece 08 (refined on all points, both walls' cost per point, the authors' line located in it).
- [ ] A7: job IDs with `sacct` State/ExitCode in Comments; renders before/after for any geometry claim; corpus md5 unchanged; nothing committed by the worker.

## Instruments that already exist (reuse, do not rewrite)

- Grid + substitution harness: `.scratch/pota-repro/310-stage/submit310c.sbatch` and `.sh`, `analyse310c.py`, `corpus310.py` (axes for the corpus), `stage310b2.py`. The 310 runs show the exact pattern: `20261105-1407_1a6f16e_t310c2-E/logs/substitution.tsv`.
- Arm runner: `.scratch/pota-repro/308-stage/e2e308.sbatch`.
- Scoring: the assembler writes `1. Acc.txt` itself; per-join checking from `T_<i>to_<i>.txt` is a small script the worker writes (see 310's MMR7 check for the shape).
- Axes: `python -m sfs_axes.cli --union --step 10` with `SFS_AXES_CONVERGE_BEFORE_RANK=1`; corpus axes at 20261105-1215_1a6f16e_t310b3-timing `out/axes310`.

## Rules that apply to this ticket

- MATLAB is the reference where a basin question is asked; the assembler is the judge of seating. Never change the corpus; compute nodes only; every `sbatch` gets a poll and its `sacct` line recorded.
- Comments-only edits to this ticket. No commits by the worker; the lead lands.
- Mark the claim type in the verdict. A number that cannot be put physically (degrees, millimetres, sherds seated) is a warning about the measurement.
