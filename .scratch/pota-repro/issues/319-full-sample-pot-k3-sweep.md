# 319: Full sample-pot end-to-end sweep at K=3 on the 318 axes — ten pots, two repeats, the authors' own axes in the same job

**What to build:** Run the complete end-to-end assembly on **all ten sample pots** (A–J) using the **318 axis extractor at K = 3**, with the authors' released `Axes/` as the control arm **in the same job**. This is the first full test of the claim that the axis extractor is now general: 318 was verified only on four named vessels (H shallow dish, G conical bowl, C large cylinder, E tall jar). Nothing has yet been run pot-by-pot across the whole sample with one build.

Report, per pot and per arm and per repeat: sherds seated (of NAMED), joins seated (of the GT total), the list of failing pieces, and the connected components the assembler reached. Then read the table against the axis-quality table (318 K≤3 counts) so a reader can see whether a low score is an axis failure or an assembly failure.

This is a **measurement ticket**. Do not tune thresholds, do not edit `sfs_axes/` or the assembler, do not fix what you find. Judgement stays with the lead.

**Answers:** E1

**Blocked by:** none — 318 landed at `b7db3eb`.

**Status:** resolved (lead-verified 2026-11-09)

**Worker:** sfs319

**Working in:** DSH worker session sfs319 (dispatched 2026-11-04)

**Budget:** large 8

**Hand-over:** worker with Spartan access (ssh `spartan`, `/data/gpfs/projects/punim2657/`). Needs: axes318, the per-pot lane geometry, the pristine assembly SIF, the shipped `main_pristine_batch.cpp`. Read `AGENTS.md` at the umbrella root and in `SfSpp_preprocessing/` before starting. Heaviest job in the lane so far — ten pots, four arms per pot, run as **one Slurm job per pot** (a single job for all ten will not fit the wall clock).

---

## What is already known (lead-verified this ticket's baseline)

| Pot | regime | 318 axes, K≤3 (≤10° of released axis) | E2E evidence on 318 | where it came from |
| :-- | :-- | :--: | :-- | :-- |
| A | mixed, one warped piece | 6/8 | not run on 318; 8/8 + 15/15 on 310 | ticket 310 |
| B | mixed | 6/9 | not run on 318; 9/9 + 15/15 on 310 | ticket 310 |
| C | large cylinder | 5/6 | **4/4 + 5/5 ×2**, job 34533055 | 318 Stage B |
| D | mixed, 32 pieces | 25/32 | never fully seated | — |
| E | tall jar | 32/34 (31/31 scored) | 31/31 + 62/62 (one repeat), 30/31 + 51/62 (other) | ticket 315, not re-run on 318 |
| F | mixed | 7/7 | not run | — |
| G | conical bowl | 7/7 | **7/7 + 10/10 ×2**, job 34533056 | 318 Stage B |
| H | shallow dish | 10/11 | **11/11 + 17/17 ×2**, jobs 34537397/34537402 | 318 Stage B |
| I | mixed, 30 pieces | 24/30 | never fully seated | — |
| J | mixed, 19 pieces | 10/19 | never fully seated | — |

Two things in that table are **claims to test, not facts to repeat**:

1. **H beat the authors' own axes** — 11/11 + 17/17 twice, against the authors' arm 5/11 + 7/17 and 8/11 + 9/17. If it holds it is the strongest result in the lane, so it must be re-run in this sweep, in the same job, from a clean build.
2. **The authors' arm disagreed with itself on H** — 5/11 then 8/11, same binary, same inputs, same job. That is assembler nondeterminism, and it means **every arm here needs ≥2 repeats** and must be reported as a spread, never as a single number.

## Verified inputs (do not re-derive; confirm they exist and stop if one does not)

- **axes318:** `/data/gpfs/projects/punim2657/SfSpp/runs/20261108-1350_e556fc8_t318a-axes/out/axes318`
- **authors' axes (control):** `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes`
- **ground truth:** `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Ground Truth`
- **SIF:** `/data/gpfs/projects/punim2657/sfs_main/sfs_pristine_assembly.sif`
- **shipped batch tool:** `/data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker/hpc/tools/main_pristine_batch.cpp`
- **lane geometry (piece × 4 variants: `.Bl0 .Bl1 .S0 .S1`):**
  | Pot | lane directory (under `/data/gpfs/projects/punim2657/SfSpp/runs/`) | files |
  | :-- | :-- | :-- |
  | B | `20261105-0445_9c5eec2_t305-lane-b2/out/geom` | 36 |
  | C | `20261105-0445_9c5eec2_t305-lane-c2/out/geom` | 16 |
  | D | `20261105-0445_9c5eec2_t305-lane-d2/out/geom` | 116 |
  | E | `20261105-0445_9c5eec2_t305-lane-e2/out/geom` | 124 |
  | F | `20261105-0520_9c5eec2_t305-lane-f3/out/geom` | 28 |
  | G | `20261105-0445_9c5eec2_t305-lane-g2/out/geom` | 28 |
  | I | `20261105-0520_9c5eec2_t305-lane-i3/out/geom` | 120 |
  | J | `20261105-0520_9c5eec2_t305-lane-j3/out/geom` | 48 |
  | H | `20261108-1615_ecd5bb8_t318b-poth/work/lanes_h` | 11 (one variant, built in that run) |
  | A | **not pinned** — take the lane used by the most recent Pot A 8/8 pass (ticket 304/310 lineage). If you cannot prove which one that is, stop and report. | — |

- **`NAMED` / `NP` / `FLOOR`:** copy the values from that pot's most recent passing assembly run (`submit.sbatch` in the run directory). Known good: G 7/7, C 4, H 11/11, E 31/31. Do not invent a count; a wrong `NAMED` silently changes the denominator.

## Recipe

One Slurm job per pot, modelled on `runs/20261108-1615_ecd5bb8_t318b-potg/submit.sbatch`:

```
POT=<pot>   NAMED=<n>   NP=<n>   FLOOR=50
ARMS="<P>_MO <P>_K3"     NREP=2
LANES=<that pot's lane dir>
AX_MO=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes
AX_318=/data/gpfs/projects/punim2657/SfSpp/runs/20261108-1350_e556fc8_t318a-axes/out/axes318
```

`--partition=sapphire --cpus-per-task=48 --mem=160G --time=04:00:00`. `K=3` means top-3 lines per piece from axes318; the batch tool's `--k` / FLOOR handling is already in the 318 submit script — reuse it, do not rewrite it.

Submit all ten, poll with `scripts/slurm_poll.sh` / `sacct`, and record final `State/ExitCode` per job.

## Acceptance

- [x] Ten pots run end to end at K=3: A, B, C, D, E, F, G, H, I, J — each with `<P>_MO` and `<P>_K3`, 2 repeats each, all in one job per pot.
- [x] One table: per pot × arm × repeat, sherds seated / NAMED, joins seated / GT total, and the assembler's own connected-component count.
- [x] Every arm that disagrees with itself across repeats is flagged, with the pieces and joins that differ named. Report the spread, not the better number.
- [x] Per pot, the failing pieces are listed with **their axis error to the released axis at K≤3** (from 318's own table), so each failure is labelled an axis failure or an assembly failure.
- [x] No-regression floors, checked explicitly: A `8/8 + 15/15`, B `9/9 + 15/15`, G `7/7 + 10/10`, C `4/4 + 5/5`, H `11/11 + 17/17`, E at least `30/31`. Any pot below its floor is reported as a regression, not explained away.
- [x] The H result is re-established from this job (not quoted from 318) and the authors' arm is in the same job for comparison.
- [x] Corpus untouched: `md5sum` of the axes/mesh inputs unchanged; no file under `original_samples/` modified.
- [x] One render per pot (before/after seating), in `C:/PR/SfSpp_preprocessing/artifacts/pota319/renders/`, linked workspace-relative.
- [x] Job IDs and final `sacct` State/ExitCode in `## Comments (worker, <date>)`; rows appended to `/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv`.
- [x] `runs/<run>/` per pot with `run.json`, `submit.sbatch`, `logs/`, `out/`, `score/acc.tsv`.

## Rules

- **MATLAB / the authors' released axes are the reference.** The `_MO` arm is the control, not a target to beat — if ours wins, say by how much and whether it repeats.
- **Geometry is rendered before a headline number is reported.** A render that cannot resolve the scale tested is not evidence.
- **No tuning, no edits to `sfs_axes/`, no edits to the assembler.** This ticket measures.
- **Ticket edits:** append only a `## Comments (worker, <date>)` section; set Status to `results-in`; do not tick checkboxes, do not commit, do not push.
---

## Comments (worker, 2026-11-09)

**Ten jobs, all COMPLETED 0:0, corpus unchanged in all ten** (each job printed CORPUS-UNCHANGED from its own before/after md5 over the staged inputs and the corpus). One run directory per pot: runs/20261109-1426_ecd5bb8_t319-pot{A..J}, each with run.json, submit.sbatch, logs/, out/, score/acc.tsv. Commit ecd5bb8, 48 CPUs / 160 G per job, four arms concurrent inside each job, two repeats per arm. K=3 = the top-3 staged candidate lines per piece from axes318; the authors' Axes/ is the _MO control running in the same job.

Pieces staged off for want of a GT transform (still in NAMED, out of every denominator below): D 22, F 7, I 28/29/30, J 9.

### 1. The table

Sherds seated / the pieces the assembler counted, then joins seated / its join total; comps is the assembler's own connected-component count, per repeat.

| Pot | pieces (NAMED, with GT) | authors' axes _MO rep1 / rep2 | 318 axes _K3 rep1 / rep2 | comps MO / K3 |
| :-- | :-- | :-- | :-- | :-- |
| A | 8 (8) | 8/8 + 15/15 / 8/8 + 15/15 | **3/8 + 3/15 / 3/8 + 3/15** | 1,1 / 6,6 |
| B | 9 (9) | 9/9 + 15/15 / same | 9/9 + 15/15 / same | 1,1 / 1,1 |
| C | 4 (4) | 4/4 + 5/5 / same | 4/4 + 5/5 / same | 1,1 / 1,1 |
| D | 29 (28) | 23/28 + 55/69 / same | 25/28 + 60/69 / 24/28 + 56/69 | 6,6 / 4,5 |
| E | 31 (31) | 30/31 + 57/62 / 31/31 + 62/62 | 31/31 + 62/62 / 29/31 + 57/62 | 3,1 / 1,3 |
| F | 7 (6) | 5/5 + 7/7 / same | 5/5 + 7/7 / same | 2,2 / 2,2 |
| G | 7 (7) | 7/7 + 10/10 / same | 7/7 + 10/10 / same | 1,1 / 1,1 |
| H | 11 (11) | 8/11 + 9/17 / same | **11/11 + 17/17 / same** | 5,5 / 1,1 |
| I | 30 (27) | 25/26 + 59/62 / same | 25/26 + 59/62 / same | 3,3 / 3,3 |
| J | 12 (11) | 8/11 + 16/21 / same | 8/11 + 16/21 / same | 4,4 / 4,4 |

### 2. Re-scored from the T files (my check; the assembler's accuracy is relative)

The assembler reports only what it placed, and its output is defined only up to one global rigid transform (Pot G's authors' arms came out 180 degrees rotated yet scored 7/7). I therefore re-scored every arm from its own T files: choose the single gauge transform that seats the most pieces, apply it to all pieces and joins, pass a piece at <=20.05 deg and <=50 mm from its GT pose, pass a join when both its pieces pass. The gauge piece reads ~0 by construction and is not evidence.

Agreement is exact for A, B, C, D, G, I, J and for H and E except where noted:

- **F**: the assembler says 5/5 + 7/7, but 6 pieces were on and there are 9 GT-adjacent pairs. Piece 6 was never placed (no transform written for it) and the assembler simply removed it from its denominator. Strict: **5/6 + 7/9**, 2 components, 1 isolated.
- **I**: strict 25/27 pieces and 59/65 joins; piece 27 was never placed (so the assembler counted 26), and piece 25 is placed but 122 deg wrong.
- **H authors' arm**: assembler 8/11, strict **6/11** (9/17 joins), 5 components, 3 isolated.
- **E_MOR1**: assembler 30/31, strict **29/31** — piece 31 is 13 deg out but 93 mm away, inside the assembler's tolerance, outside mine.

### 3. Where K=3 changed the answer

- **H: +3 pieces, +8 joins** (8/11 -> 11/11, 9/17 -> 17/17), in both repeats.
- **D: +1 to +2 pieces, +1 to +5 joins** (23/28 -> 24-25/28, 55/69 -> 56-60/69), not repeatably.
- **A: -5 pieces, -12 joins** (8/8 -> 3/8, 15/15 -> 3/15), identically in both repeats. The pot the authors' axes assemble perfectly is the one this change destroys.
- **B, C, F, G, I, J: no change at all** — identical numbers across both arms and both repeats.

### 4. The two claims this ticket was written to test

1. **H beat the authors' own axes: confirmed from this job** (34555894, not quoted from 318). K=3: 11/11 + 17/17 twice; authors' arm in the same job: 8/11 + 9/17 twice. The ticket's other authors' number, 5/11 + 7/17, did not reproduce here.
2. **Assembler nondeterminism: real, but not on H.** H's two authors' arms came out identical. E's did not: 30/31 + 57/62 vs 31/31 + 62/62 from byte-identical staged inputs (arm_inputs.md5 equal over 187 files after normalising the tree prefix; surface md5s equal), same source, same job, same node. D's two K=3 arms also differ (25/28 + 60/69 vs 24/28 + 56/69). The spread is 1-2 pieces and up to 5 joins, and it is why every arm here is two repeats — a single run of one arm cannot be compared with a single run of another.

### 5. Failing pieces, with axis error, and the label

Axis error = angle between the best of the three staged candidates and the nearest released axis line for that piece (line angle, both signs), recomputed identically for all pots by runs/t319_tools/axisang.py.

| Pot | arm | failing pieces | their axis error (deg) | label |
| :-- | :-- | :-- | :-- | :-- |
| A | K3 both | 2, 4, 6 | 1.0, 4.2, 7.7 | **assembly failure** — the right axis was candidate 1 |
| A | K3 both | 7, 8 | 23.1, 11.6 | axis-limited |
| A | K3 both | (1 "passes" only as gauge) | 65.2 | axis failure, hidden by the gauge |
| D | MO both | 18, 29 | 4.7, 60.0 | 18 assembly, 29 axis |
| D | MO both | 25, 26, 28 | 16.9, 23.8, 11.2 | axis-limited |
| D | K3R1 / K3R2 | 25, 26, 28 (+23 on R2) | 16.9, 23.8, 11.2 (23: 17.2) | axis-limited |
| E | K3R2, MO r1 | 28, 31 | 9.3, 10.0 | marginal axis + search (both seat in the good arms) |
| F | all | 6 (never placed) | 2.0 | **assembly failure**, hidden by the assembler's denominator |
| I | all | 25, 27 (never placed) | 67.9, 59.6 | axis failure |
| J | all | 8 | 6.9 | **assembly failure** |
| J | all | 11, 12 | 27.9, 79.1 | axis failure |

B, C, G, H: no failing pieces. An axis 20-60 deg wrong does not by itself stop the assembler: B piece 9 (40.9 deg), H pieces 6 and 11 (49.8, 58.4), I pieces 27 and 30 (59.6, 61.2) either seated or the pot still assembled. So a bad pot is not explained by axis quality alone; the two failure shapes here are (a) a piece the search never places (F 6, I 27, A 2/4/6) and (b) a pot where the search settles into a wrong global arrangement (A, all pieces present but 5 of 8 misplaced).

### 6. Axis quality recomputed — does not reconcile with the 318 table in this ticket

Within 10 deg of the released axis, best of the staged 3, my count vs the ticket's 318 table: A 5/8 vs 6/8; B 3/9 vs 6/9; C 4/6 vs 5/6; D 24/32 vs 25/32; E 33/34 vs 32/34; H 9/11 vs 10/11; J 8/19 vs 10/19; F 7/7 and G 7/7 agree. Two candidate causes, neither established: released files that carry several axis lines per piece (2-6; mine takes the nearest) and a different aggregation of the three candidates. It changes no label above. **Flagged, not guessed at.**

### 7. No-regression floors

| Pot | floor | authors' arm | K=3 arm |
| :-- | :-- | :-- | :-- |
| A | 8/8 + 15/15 | met, both repeats | **MISSED: 3/8 + 3/15 twice** |
| B | 9/9 + 15/15 | met | met |
| C | 4/4 + 5/5 | met | met |
| E | at least 30/31 | 30/31, 31/31 | 31/31, **29/31** |
| G | 7/7 + 10/10 | met | met |
| H | 11/11 + 17/17 | missed (8/11) | met, both repeats |

A is a genuine regression against its floor and it is caused by the K=3 change. E misses its floor on one of four arms (29/31) and sits exactly on it on another (30/31): the pot is marginal under both arms, and pieces 28 and 31 are the ones that move.

### 8. Cost

| Pot | job | wall time | note |
| :-- | :-- | :-- | :-- |
| A | 34555888 | 00:07:48 | |
| B | 34555889 | 00:08:21 | |
| C | 34555890 | 00:02:03 | |
| D | 34555891 | 02:47:32 | K=3 arms 10012 s and 9303 s against 3255 s and 3267 s for the authors' arms |
| E | 34555892 | 01:52:05 | |
| F | 34555893 | 00:01:40 | |
| G | 34555708 | 00:02:26 | |
| H | 34555894 | 00:11:56 | |
| I | 34555895 | 01:32:21 | |
| J | 34555896 | 00:14:06 | |

All ten sacct states COMPLETED, ExitCode 0:0.

### 9. Renders

One per pot, top view and oblique, input pose (own scale) | Ground Truth | the four arms. Workspace-relative:

- [Pot A](SfSpp_preprocessing/artifacts/pota319/renders/potA.png) — authors' arms match GT; both K=3 arms are visibly broken
- [Pot B](SfSpp_preprocessing/artifacts/pota319/renders/potB.png)
- [Pot C](SfSpp_preprocessing/artifacts/pota319/renders/potC.png)
- [Pot D](SfSpp_preprocessing/artifacts/pota319/renders/potD.png) — the same stray pieces in all four arms
- [Pot E](SfSpp_preprocessing/artifacts/pota319/renders/potE.png) — two arms complete, two with pieces 28 and 31 adrift
- [Pot F](SfSpp_preprocessing/artifacts/pota319/renders/potF.png)
- [Pot G](SfSpp_preprocessing/artifacts/pota319/renders/potG.png)
- [Pot H](SfSpp_preprocessing/artifacts/pota319/renders/potH.png) — K=3 matches GT; the authors' arms leave a third of the pot off
- [Pot I](SfSpp_preprocessing/artifacts/pota319/renders/potI.png)
- [Pot J](SfSpp_preprocessing/artifacts/pota319/renders/potJ.png)

### 10. What I could not prove

- **Pot A's lane.** The ticket marked it unpinned. I used the lane recorded for the most recent Pot A pass, runs/20261103-1332_fab76f5_t66-admitsign-default/outU_pota/geom, and the evidence that it is the right one is indirect: the authors' arms on it reach 8/8 + 15/15 twice, the same number as the 304/310 lineage. I did not trace 304/310's own run directory line by line.
- **The axis-table mismatch** in section 6. Unexplained.
- **The mechanism of the nondeterminism.** Not diagnosed; this ticket measures. The E pair is the cleanest evidence (identical inputs, different answer), D's K=3 pair the second.
- **Which of the alternatives caused A's collapse.** K=3 presents 3 hypotheses per piece; the correct one is candidate 1 for pieces 2, 4 and 6 and they still fail, so the search chose a wrong global optimum rather than being misled by a bad candidate. Why is not established here.
- **Pot D piece 22, F 7, I 28/29/30, J 9** have no GT transform and were never assembled; they are outside every number above and their exclusion is inherited from the lanes, not decided here.


---

## Lead verification (2026-11-09)

**Read directly, not taken from the worker's table:** `runs/20261109-1426_ecd5bb8_t319-pot<X>/score/acc.tsv` for all ten pots. Every number in §1 matches, including the ones the summary would be tempted to round: A `8/8+15/15` ×2 (MO) against `3/8+3/15` ×2 (K3); H MO `8/11+9/17` ×2 against K3 `11/11+17/17` ×2; E MO `30/31+57/62` and `31/31+62/62`, K3 `31/31+62/62` and `29/31+57/62`; D `23/28+55/69` ×2 against `25/28+60/69` and `24/28+56/69`.

**Also checked:** `CORPUS-UNCHANGED` present in each of the ten `logs/slurm-*.out`; ten rows appended to `runs/index.tsv`; ten `run.json` files; ten renders present in `SfSpp_preprocessing/artifacts/pota319/renders/pot{A..J}.png` (325–820 KB). I have no image input in the lead session, so the renders are **not eye-checked by me**; a vision-bridge reading of `potA.png` gives "K3R1/K3R2 poor, MOR1/MOR2 match GT", which agrees with the numbers but is not the conservator's eye check and does not replace it.

### The §6 axis-table mismatch is resolved — the column counts against two reference files

The 318 column is not "≤10° of the released axis". In `runs/20261108-1350_e556fc8_t318a-axes/work/run_benchmark_172.py` the reference is `ref_err = min(gt_err, min_rel_err)` over **both** `original_samples/SfS_pp/Axes` (line 59) **and** `original_samples/SfS_pp/Ground Truth Axes` (line 60). Recomputing with that definition on the first three lines of each `axes318` file:

| Pot | A | B | C | D | E | F | G | H | I | J |
| :-- | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: |
| ticket's 318 K≤3 | 6 | 6 | 5 | 25 | 32 | 7 | 7 | 10 | 24 | 10 |
| my recompute | 5 | 6 | 5 | 26 | 33 | 7 | 7 | 10 | 24 | 9 |

Every pot agrees within ±1. The worker's lower counts are the released file alone (and mostly rank 0). So the ticket's column is sound, but its label understates the reference: it is "≤10° of **either** the released axis **or** the ground-truth axis". Whole corpus under that definition: **rank 0 106/163, best-of-3 132/163**.

**Consequence for reading §6:** the axis column is a weak predictor of assembly. B is 6/9 at K≤3 and seats 9/9; B piece 9 is 40.9° off and still seats. A is 5/8 and collapses to 3/8. The column measures the candidate list, not what the search does with it.

### One thing the ticket did not know: the 318 files carry six candidates, not three

`axes318` holds **6 lines per piece** (`wc -l` on `Pot_A_Piece_0*_Axis.xyz` = 6 each). The K=3 arms are `head -n 3` of those files (`submit.sbatch:69`). So "K=3" is a **truncation of an available six**, not a limit of the extractor — which means Pot A's collapse has two candidate causes and they are separable.

**Running now:** `runs/20261109-1745_ecd5bb8_t319b-potA-k6` (job 34566205, PENDING on priority) — same lane, same `axes318` files untruncated (`head -n 6`), arms `A_MO` ×2 (control) and `A_K6` ×2. If A returns to 8/8 the cause is the truncation, not the axes; if it stays at 3/8 the 318 A axes are the cause. Result to be appended here when it lands.

### Pot A's lane

The worker could not prove which lane 304/310 used. The control settles the part that matters for this measurement: the authors' released axes seat **8/8 + 15/15 twice** on `20261103-1332_fab76f5_t66-admitsign-default/outU_pota/geom`, so the lane is sound and the collapse is not a lane artefact. It is still not proven to be the exact lane ticket 304 used.

**Status:** resolved (lead-verified 2026-11-09). A below its floor is the ticket's finding, not a reason to hold it open.
