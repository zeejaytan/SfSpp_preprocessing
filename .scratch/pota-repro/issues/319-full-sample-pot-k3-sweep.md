# 319: Full sample-pot end-to-end sweep at K=3 on the 318 axes — ten pots, two repeats, the authors' own axes in the same job

**What to build:** Run the complete end-to-end assembly on **all ten sample pots** (A–J) using the **318 axis extractor at K = 3**, with the authors' released `Axes/` as the control arm **in the same job**. This is the first full test of the claim that the axis extractor is now general: 318 was verified only on four named vessels (H shallow dish, G conical bowl, C large cylinder, E tall jar). Nothing has yet been run pot-by-pot across the whole sample with one build.

Report, per pot and per arm and per repeat: sherds seated (of NAMED), joins seated (of the GT total), the list of failing pieces, and the connected components the assembler reached. Then read the table against the axis-quality table (318 K≤3 counts) so a reader can see whether a low score is an axis failure or an assembly failure.

This is a **measurement ticket**. Do not tune thresholds, do not edit `sfs_axes/` or the assembler, do not fix what you find. Judgement stays with the lead.

**Answers:** E1

**Blocked by:** none — 318 landed at `b7db3eb`.

**Status:** in-progress

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

- [ ] Ten pots run end to end at K=3: A, B, C, D, E, F, G, H, I, J — each with `<P>_MO` and `<P>_K3`, 2 repeats each, all in one job per pot.
- [ ] One table: per pot × arm × repeat, sherds seated / NAMED, joins seated / GT total, and the assembler's own connected-component count.
- [ ] Every arm that disagrees with itself across repeats is flagged, with the pieces and joins that differ named. Report the spread, not the better number.
- [ ] Per pot, the failing pieces are listed with **their axis error to the released axis at K≤3** (from 318's own table), so each failure is labelled an axis failure or an assembly failure.
- [ ] No-regression floors, checked explicitly: A `8/8 + 15/15`, B `9/9 + 15/15`, G `7/7 + 10/10`, C `4/4 + 5/5`, H `11/11 + 17/17`, E at least `30/31`. Any pot below its floor is reported as a regression, not explained away.
- [ ] The H result is re-established from this job (not quoted from 318) and the authors' arm is in the same job for comparison.
- [ ] Corpus untouched: `md5sum` of the axes/mesh inputs unchanged; no file under `original_samples/` modified.
- [ ] One render per pot (before/after seating), in `C:/PR/SfSpp_preprocessing/artifacts/pota319/renders/`, linked workspace-relative.
- [ ] Job IDs and final `sacct` State/ExitCode in `## Comments (worker, <date>)`; rows appended to `/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv`.
- [ ] `runs/<run>/` per pot with `run.json`, `submit.sbatch`, `logs/`, `out/`, `score/acc.tsv`.

## Rules

- **MATLAB / the authors' released axes are the reference.** The `_MO` arm is the control, not a target to beat — if ours wins, say by how much and whether it repeats.
- **Geometry is rendered before a headline number is reported.** A render that cannot resolve the scale tested is not evidence.
- **No tuning, no edits to `sfs_axes/`, no edits to the assembler.** This ticket measures.
- **Ticket edits:** append only a `## Comments (worker, <date>)` section; set Status to `results-in`; do not tick checkboxes, do not commit, do not push.
