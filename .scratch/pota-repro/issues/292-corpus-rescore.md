# 292 — Re-score the frozen corpus at the shipped defaults

Answers: E1
Status: done (baseline taken: 281/292 sound lanes at bar at the shipped defaults)
Working in: main (worktree closed 2026-10-25) (branch 292-corpus-rescore)
Branch: 292-corpus-rescore
Needs-eye: yes -- a per-pot summary picture, and a picture for every lane that misses

## Why

Every lane score in this project was measured on point clouds that no longer exist. The mesh stage
samples its cloud from the OBJ with CloudCompare's unseeded sampler, so a cloud is one draw and
cannot be regenerated; ticket 284 had to close as a no-go having found 2 of 148. The authors'
release closed that gap (ticket 290: 148 frozen clouds, 143 released + 5 derived) and staging is now
symlink-only (ticket 291: 108 bytes copied per piece, inputs byte-identical run to run). The
shipped binary has also changed since the 4.0-era tally: the five rejected arms are gone (538357c,
67ff3d7), the full walk and the 12 mm stop rule are the default, the walk now seeds in the largest
lump (8e1e514, ticket 287), and the growth angle is 3.4 (tickets 269-271).

So there is no current measurement of how many lanes are at bar. This ticket takes one: the whole
corpus, the shipped defaults, the frozen corpus, geometry deleted per piece.

## What is being measured

For every piece in the frozen corpus: stage it by symlink, run the mesh stage at the shipped
defaults (theta 3.4, `SFS_AXIS_FILE` set to the corpus axis), run the edge stage at the shipped
defaults (no `SFS_*` override of any kind), then score BOTH exported lanes (Breakline_0 against
`Breakline_0`, Breakline_1 against `Breakline_1` -- never cross-lane).

The scorer is fixed and committed: `.scratch/pota-repro/292/score292.py`. Its semantics are the ones
tickets 266/287/289/290 used, and they are not to be changed:

- for each of OUR dots, the distance to the nearest AUTHOR dot; `median` = 50th percentile of those
  distances in millimetres;
- `cov_ours` = percentage of OUR dots under 2.0 mm; `cov_auth` = percentage of AUTHOR dots with one
  of ours under 2.0 mm (author-side coverage exists because one-way coverage lets a short stub
  sitting on the line score 100);
- `jumps` = count of consecutive exported steps over 10 mm; `max_step` = the largest of those steps;
- `len_ours` / `len_auth` = polyline length of each lane, in millimetres.

**At bar** = `median <= 2.0` AND `cov_ours >= 90`. Jumps are reported beside the bar, never folded
into it (a lane can be at bar and still jump; that is what the jump column is for).

## Design

One Slurm **job array**, one element per piece, because the geometry rule forbids accumulating:

```
#SBATCH --array=0-147%10
#SBATCH --cpus-per-task=8 --mem=24G --time=00:40:00
```

Each element, in its own node-local tree under the run directory:

1. `scripts/stage_piece.sh <stage> <Pot> <Piece>` -- mesh and cloud by symlink, axis copied.
2. Mesh stage: `apptainer exec --bind /data:/data $SIF env POT_NAME=<Pot> SFS_AXIS_FILE=<staged axis> <bin>/MeshPreprocessingHeadless`
   run with the stage as the working directory. Quote the `[PAPER-234] classify` line and the
   `paper grow` line into the task log (the axis trap, ticket 277: without the axis file the stage
   silently keeps size order and every lane number downstream is nonsense).
3. Edge stage: `apptainer exec --bind /data:/data $SIF env POT_NAME=<Pot> <bin>/EdgeLineExtractionHeadless`.
   No `SFS_*` variable may be set. Quote `[FULL-263]`, `[SEED-287]`, `[STOP-267]` and
   `[VOTE-247]` lines into the log.
4. Score both lanes with `score292.py`; append the two rows to `out/lanes.tsv`.
5. If a lane is **not** at bar, write a small two-panel picture (X-Y and X-Z, author black, ours
   green, dpi 90) to `out/png/<Piece>_Bl<k>.png`. Nothing else is pictured per lane.
6. Delete the whole stage tree, then assert no file over 1 MiB is left under the task's tree except
   the binaries; append what was deleted to `out/GEOMETRY_DELETED.txt`.

After the array: one collect job writes `out/summary.md` and the index row.

## Exclusions the summary must carry (read before quoting any count)

- **Pot J 09, both lanes: excluded from the tally.** The conservator ruled its reference line wrong
  (ticket 289); it is measured and reported, never counted.
- **Pot C 01 and Pot J 01, lane 0 (interior) only: reported, excluded from the headline.** Both
  pieces are not watertight in the interior surface (ticket 285), so an interior-lane number is
  evidence about the input, not the method. Their lane 1 (exterior) counts normally.
- **Five pieces are outside the authors' evaluation set** (F07, I28, I29, I30, J12): they were
  removed by the authors' own rule (paper `:329`), so their lanes are scored and listed, and never
  compared with the paper's numbers (ledger section O).

## Pre-registered headline to produce (write these five numbers before interpreting anything)

1. lanes measured (expect 296);
2. lanes valid (measured minus J09's 2; expect 294);
3. lanes sound (valid minus C01/J01 interior; expect 292);
4. lanes at bar in each of the three sets;
5. lanes with one or more jumps, and the largest jump.

Plus a per-pot table (at bar / measured / valid), and the full list of lanes below bar with
n, median, cov_ours, cov_auth, jumps.

## What this ticket does NOT claim

That any difference from the 4.0-era tally (265 of 294 valid lanes) is an improvement or a
regression. The binary, the growth angle and the sampled cloud all changed; the old number is
history. This run is a **new baseline at the shipped defaults**, and its value is that it can be
re-staged and re-run byte-for-byte from the same commit (tickets 290, 291).

## Constraints

- No code change, no default change, no threshold change, no `SFS_*` override. If the shipped
  defaults crash on a piece, record it and move on; do not patch.
- Build from `git archive` of **this ticket's commit** in the canonical checkout; record the commit,
  the node, and both binary md5s in `run.json`. Never `build.sh --target nurbs` (ticket 282: it
  compiles the pre-247 duplicate at `original_nurbs_preprocessing/edgeline_extraction_headless.cpp`).
- The corpus is INPUT: nothing under `original_samples/SfS_pp` may be written. Re-check the
  manifest md5s after the run and report.
- Run directory `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_p292-rescore/` with
  `run.json`, `submit.sbatch`, `logs/`, `out/`; one row appended to `runs/index.tsv` with
  `verdict` and `human_note` left empty for the lead.
- A piece that fails to stage or to mesh gets an `error` row and keeps its log; the array must not
  abort on it, and the failure count goes in the headline.

## Acceptance (evidence to report back)

- `out/lanes.tsv`: one row per lane with the columns above; every row traceable to a task log.
- The five headline numbers, the per-pot table, the below-bar list, the error list.
- Four lanes recomputed by hand from the exported pcds **before deletion** and shown to match their
  rows (n, median, both coverages, jumps).
- `out/GEOMETRY_DELETED.txt` and the assertion that no file over 1 MiB is left outside `bin/`.
- Corpus manifest re-check: 148/148 md5s unchanged.
- `out/png/` pictures for the misses and one summary picture per pot.
- Run directory path, job ids, binary md5s, commit.

## Results (2026-10-25)

Run directory `/data/gpfs/projects/punim2657/SfSpp/runs/20261025-0134_787c149_p292-rescore`,
commit `787c149a3e5b8e4b23093746677b7842452e9316`. Everything below is at the shipped defaults on the
frozen corpus: no `SFS_*` variable set in either stage, no code, default or threshold change.

### The five pre-registered numbers

| # | number | expected | measured |
|---|---|---|---|
| 1 | lanes measured | 296 | **296** (148 of 148 pieces produced both lanes) |
| 2 | lanes valid (measured minus Pot J 09) | 294 | **294** |
| 3 | lanes sound (valid minus C01 / J01 lane 0) | 292 | **292** |
| 4 | lanes at bar | — | measured **283 / 296** (95.6%), valid **283 / 294** (96.3%), sound **281 / 292** (96.2%) |
| 5 | lanes with at least one jump | — | **1 of 292 sound lanes**; largest single step **37.712 mm** on `Pot_C_Piece_02` lane 1 (that lane median 0.530 mm, so it is at bar) |

In plain terms: on 281 of the 292 sound lanes our line sits within **2 mm of the authors’ line at the
median, with at least 90% of our dots inside 2 mm**. Eleven sound lanes miss that bar; 13 lanes miss
it in total, counting the two excluded Pot J 09 lanes.

### Per-pot table (at bar counted on sound lanes)

| pot | pieces | lanes measured | valid | sound | at bar (sound) |
|---|---|---|---|---|---|
| Pot_A | 8 | 16 | 16 | 16 | 16 |
| Pot_B | 9 | 18 | 18 | 18 | 18 |
| Pot_C | 4 | 8 | 8 | 7 | 6 |
| Pot_D | 29 | 58 | 58 | 58 | 55 |
| Pot_E | 31 | 62 | 62 | 62 | 61 |
| Pot_F | 7 | 14 | 14 | 14 | 14 |
| Pot_G | 7 | 14 | 14 | 14 | 14 |
| Pot_H | 11 | 22 | 22 | 22 | 20 |
| Pot_I | 30 | 60 | 60 | 60 | 56 |
| Pot_J | 12 | 24 | 22 | 21 | 21 |
| **all** | **148** | **296** | **294** | **292** | **281** |

### Every lane below bar (13 measured; 11 of them sound)

| piece | lane | set | n ours | n auth | median mm | cov ours | cov auth | jumps | max step |
|---|---|---|---|---|---|---|---|---|---|
| Pot_C_Piece_03 | 1 | sound | 339 | 120 | 11.281 | 17.99 | 50.00 | 0 | 4.783 |
| Pot_D_Piece_22 | 0 | sound | 125 | 133 | 0.757 | 86.40 | 78.95 | 0 | 1.801 |
| Pot_D_Piece_27 | 0 | sound | 56 | 48 | 0.673 | 73.21 | 83.33 | 0 | 4.698 |
| Pot_D_Piece_27 | 1 | sound | 58 | 49 | 0.798 | 62.07 | 77.55 | 0 | 4.564 |
| Pot_E_Piece_16 | 0 | sound | 111 | 112 | 0.676 | 72.97 | 74.11 | 0 | 4.307 |
| Pot_H_Piece_02 | 1 | sound | 138 | 137 | 0.688 | 72.46 | 74.45 | 0 | 3.410 |
| Pot_H_Piece_10 | 1 | sound | 90 | 88 | 0.728 | 72.22 | 77.27 | 0 | 4.918 |
| Pot_I_Piece_06 | 1 | sound | 178 | 179 | 0.883 | 70.22 | 70.95 | 0 | 4.759 |
| Pot_I_Piece_13 | 1 | sound | 161 | 160 | 0.734 | 82.61 | 85.62 | 0 | 4.458 |
| Pot_I_Piece_25 | 0 | sound | 58 | 69 | 6.910 | 0.00 | 0.00 | 0 | 3.993 |
| Pot_I_Piece_25 | 1 | sound | 67 | 60 | 6.951 | 0.00 | 0.00 | 0 | 3.572 |
| Pot_J_Piece_09 | 0 | excluded (J09) | 79 | 74 | 1.079 | 70.89 | 75.68 | 0 | 4.999 |
| Pot_J_Piece_09 | 1 | excluded (J09) | 91 | 69 | 1.913 | 50.55 | 63.77 | 0 | 4.890 |

Nine of the eleven sound misses are **coverage** misses, not distance misses: the median is at or
under 1 mm while coverage sits at 62–86%, i.e. the line is on the edge but does not span the
authors’ line over part of the loop. Two are distance misses: `Pot_C_Piece_03` lane 1 (11.28 mm)
and both lanes of `Pot_I_Piece_25` (6.9 mm, coverage 0.00 both ways).

### Errors

None. All 148 pieces staged, meshed with their `[PAPER-234] classify` line, ran both lanes and
scored; `out/errors/` is empty.

### Recomputed by hand before the geometry was deleted

`out/recheck/`, an independent parser (own PCD reader, full distance matrix, no code shared with
`score292.py`):

```
[RECOMPUTE] Pot_A_Piece_01 Bl0
  file row   : n=203/208 median=0.613 cov=100.00/99.52 jumps=0 maxstep=4.698
  by hand    : n=203/208 median=0.6133 cov=100.000/99.519 jumps=0 maxstep=4.6977
  agreement  : PASS (n exact, median 0.0003 mm apart, coverage 0.001 pp apart)
[RECOMPUTE] Pot_D_Piece_03 Bl0
  file row   : n=216/219 median=0.511 cov=100.00/99.54 jumps=0 maxstep=4.985
  by hand    : n=216/219 median=0.5114 cov=100.000/99.543 jumps=0 maxstep=4.9850
  agreement  : PASS (n exact, median 0.0004 mm apart, coverage 0.003 pp apart)
[RECOMPUTE] Pot_H_Piece_02 Bl1
  file row   : n=138/137 median=0.688 cov=72.46/74.45 jumps=0 maxstep=3.410
  by hand    : n=138/137 median=0.6877 cov=72.464/74.453 jumps=0 maxstep=3.4104
  agreement  : PASS (n exact, median 0.0003 mm apart, coverage 0.004 pp apart)
[RECOMPUTE] Pot_J_Piece_09 Bl1
  file row   : n=91/69 median=1.913 cov=50.55/63.77 jumps=0 maxstep=4.890
  by hand    : n=91/69 median=1.9128 cov=50.549/63.768 jumps=0 maxstep=4.8896
  agreement  : PASS (n exact, median 0.0002 mm apart, coverage 0.002 pp apart)
```

The four lanes were chosen before the run: one ordinary lane, one Pot D lane, one below-bar lane,
one excluded lane.

### Corpus and geometry

- `out/corpus_check.txt`: before 148 rows, after 148 rows, **corpus_unchanged=YES**, all 148 cloud
  md5s identical. `stage_piece.sh` also checks every staged cloud against
  `Point/MANIFEST_released.tsv` / `MANIFEST_derived.tsv` at staging time.
- `out/geometry_check.txt`: **0 files over 1 MiB under the run directory outside `bin/`**; 597 lines
  in `out/GEOMETRY_DELETED.txt`, **148 of 148** array tasks recorded, run dir 20 M.

### Exclusions carried into this table

- **Pot J 09, both lanes**: excluded from the tally, measured and reported only (reference ruled
  wrong, ticket 289).
- **Pot C 01 and Pot J 01, lane 0 (interior) only**: reported, excluded from the headline. Both are
  not watertight in the interior surface (ticket 285), so an interior-lane number is evidence about
  the input, not the method. Their lane 1 counts normally.
- **Five pieces outside the authors’ evaluation set** (Pot F 07, Pot I 28, Pot I 29, Pot I 30,
  Pot J 12): scored and listed, never compared with the paper (ledger O below).

### Ledger O — pieces the authors excluded, scored for our own record

| piece | lane | n ours | median mm | cov ours | cov auth | jumps | at bar |
|---|---|---|---|---|---|---|---|
| Pot_F_Piece_07 | 0 | 37 | 0.599 | 100.00 | 100.00 | 0 | yes |
| Pot_F_Piece_07 | 1 | 34 | 0.614 | 97.06 | 100.00 | 0 | yes |
| Pot_I_Piece_28 | 0 | 41 | 0.743 | 100.00 | 100.00 | 0 | yes |
| Pot_I_Piece_28 | 1 | 46 | 0.328 | 100.00 | 100.00 | 0 | yes |
| Pot_I_Piece_29 | 0 | 40 | 0.713 | 100.00 | 97.56 | 0 | yes |
| Pot_I_Piece_29 | 1 | 34 | 0.740 | 100.00 | 100.00 | 0 | yes |
| Pot_I_Piece_30 | 0 | 38 | 0.606 | 100.00 | 100.00 | 0 | yes |
| Pot_I_Piece_30 | 1 | 38 | 0.425 | 97.37 | 97.50 | 0 | yes |
| Pot_J_Piece_12 | 0 | 53 | 0.625 | 100.00 | 100.00 | 0 | yes |
| Pot_J_Piece_12 | 1 | 56 | 0.743 | 100.00 | 98.31 | 0 | yes |

All ten are at bar. Their point counts (34–56 per lane) are the small-fragment case the authors’
own rule removed, which is why they are listed apart.

### How it was run

| item | value |
|---|---|
| commit | `787c149a3e5b8e4b23093746677b7842452e9316` |
| edge binary | `a28d10afab2b50bbe750d599ee2b7214` (source `f0dbfe7032d90a04412d15bd1699a703`, 3739 lines) |
| mesh binary | `0171f471d0558d2676df7c4b113c1e9d` (source `459dabe145056489829804292710b382`, 2618 lines) |
| build node | `spartan-bm015.hpc.unimelb.edu.au`, `git archive` of the commit, apptainer `pcl_191_nurbs.sif` |
| build job | **33751053** (p292build), COMPLETED 0:0, 2:01 |
| array job | **33751693** (p292rescore, `--array=0-147%10`, 8 cpus / 24 G / 40 min), **148 of 148 elements COMPLETED 0:0** |
| collect job | **33751725** (p292collect), COMPLETED 0:0, 0:03 |
| staging | `scripts/stage_piece.sh` from the committed tree; two symlinks per piece plus a 108-byte axis copy |
| index row | `20261025-0134_787c149_p292-rescore` / jobid `33751053` / commit as above / tag `p292-rescore`, verdict and human_note left empty |

The edge binary is md5-identical to the one tickets 287/288/289/290 produced and the mesh binary to
ticket 289/290’s, so this run measures the same code the last three tickets did.

### Pictures (this ticket is `Needs-eye: yes`)

`out/png/`, copied to `C:/PR/SfSpp_preprocessing/artifacts/pota292/png/` on the laptop:

- **13 lane pictures**, one per measured lane below bar, 900x378 px, X-Y and X-Z, ours green, authors
  black, the numbers in the title: `Pot_C_Piece_03_Bl1.png`, `Pot_D_Piece_22_Bl0.png`,
  `Pot_D_Piece_27_Bl0.png`, `Pot_D_Piece_27_Bl1.png`, `Pot_E_Piece_16_Bl0.png`,
  `Pot_H_Piece_02_Bl1.png`, `Pot_H_Piece_10_Bl1.png`, `Pot_I_Piece_06_Bl1.png`,
  `Pot_I_Piece_13_Bl1.png`, `Pot_I_Piece_25_Bl0.png`, `Pot_I_Piece_25_Bl1.png`,
  `Pot_J_Piece_09_Bl0.png`, `Pot_J_Piece_09_Bl1.png`.
- **10 pot summary pictures**, one per pot, 1600 px wide, one thumbnail per lane labelled with the
  piece name: `pot_Pot_A.png` (1600x436) through `pot_Pot_J.png` (1600x636); Pot_D and Pot_E are
  1600x1636.

What the two worst look like, read off the pictures (numbers, not a verdict):

- `Pot_C_Piece_03` lane 1: our green line traces the **outer silhouette** of the sherd (339 dots);
  the authors’ black line is a smaller loop inside it plus a straight chord across the bottom
  (120 dots). Two different contours of the same piece, not one line offset from the other — which
  is what 17.99% coverage and an 11.28 mm median look like.
- `Pot_I_Piece_25` both lanes: the green and black curves **cross each other** and neither is a stub;
  coverage is 0.00 both ways. The two lines describe different edges of the piece.
- The nine coverage misses look like the rest of the montage: green and black coincide round most of
  the loop and part company over one stretch.

### What this run is, and what it is not

It is a **new baseline at the shipped defaults on the frozen corpus**: the same commit, the same
frozen clouds and symlink staging reproduce this table, and the pictures record what the misses look
like at this commit.

It is **not** a comparison with the 4.0-era tally of 265 of 294: the binary, the growth angle and the
sampled cloud all changed, so a difference in the count is evidence of neither an improvement nor a
regression. The weight it can bear: **one draw per piece, one binary, one commit, no repeat runs** —
148 pieces from 10 pots, but each lane measured once. The below-bar list is 13 lanes; the ones that
matter for the claim are the 11 sound ones.

### Findings that are not numbers

1. **A race in the committed `scripts/stage_piece.sh` (not fixed here).** It reads a PCD header as
   `head -20 FILE | awk ...`; under the script’s own `set -euo pipefail` the early `awk` exit can
   SIGPIPE `head` and kill the script (exit 141) before it prints anything. It hit 1 element in
   attempt 3 and **22 of 148 elements in the final array**, always on the first try. The array now
   retries staging up to three times and records `stage_tries` (`=1` on 126 pieces, `=2` on 22); all
   148 ended at `stage=0`. The helper itself was **not** modified, because this ticket forbids code
   changes. One-line fix for the lead: drop the `head` and let `awk` read the file (it exits at the
   POINTS line anyway).
2. **A re-run of a lane is not a byte-identical file.** The exported PCDs of one lane differ
   byte-for-byte between two runs on the same inputs, in the curvature column only (ticket 290’s
   finding), while the scored numbers are identical. Any future check of this table must compare
   scores or point sets, never the file md5.
3. **`Pot_H_Piece_02` lane 1 scores 0.688 / 72.46 / 74.45 here against 0.662 / 72.46 / 74.45 in
   ticket 291’s cp-staged arm.** The mesh stage is not deterministic on that piece (two runs of the
   same input differ by up to 0.867 mm on the export, ticket 291), so that difference is inside the
   piece’s own run-to-run spread, not a staging effect.

### Acceptance, item by item

| item | result |
|---|---|
| `out/lanes.tsv` one row per lane, every row traceable to a task log | PASS — 296 rows, 15 columns; `out/logs/<piece>.log` and `out/status/<piece>.tsv` per element |
| the five headline numbers, per-pot table, below-bar list, error list | PASS — above; errors none |
| four lanes recomputed by hand before deletion | PASS — 4 of 4, n exact, medians 0.0002–0.0004 mm apart |
| `GEOMETRY_DELETED.txt` + no file over 1 MiB outside `bin/` | PASS — 597 lines, 148 of 148 tasks, 0 large files |
| corpus manifest re-check 148/148 | PASS — `corpus_unchanged=YES` |
| pictures for the misses and one summary picture per pot | PASS — 13 lane + 10 pot PNGs, copied to `artifacts/pota292/png/` |
| run directory, job ids, binary md5s, commit | PASS — table above |

### Deviations

1. **Staging is retried up to three times** per element. The ticket says a piece that fails to stage
   gets an error row; it does not say to retry. Retrying was chosen because the failure is a race
   inside the committed helper, not bad input, and a retried stage is the same stage. `stage_tries`
   records every retry, the helper is unmodified, and the bug is reported above for the lead.
2. **Three array attempts failed before the run that counts.** 1: the status variables stayed at `-`
   so no stage ran; 2: the scorer was called from the run root instead of `$RUN/scripts`; 3: a stale
   copy of the array script at the run root re-ran the old scorer path, plus the first SIGPIPE
   staging failure. Each attempt’s evidence is kept in `out/attempt1/`, `out/attempt2/`,
   `out/attempt3/` (one README, the relevant logs and status rows) and every output directory was
   cleared before the next attempt, so `out/lanes.tsv` holds one run, not four. No code, default or
   threshold changed in any of them.
3. **The collect job also writes the pot montages.** The ticket asks for a summary picture per pot
   but not which job makes it; they are made in collect from the per-lane thumbnails the array
   already wrote (`out/tiles/`, 296 files), so no geometry survives into the collect job.
4. **The `jobid` column in `runs/index.tsv` holds the build job 33751053**, not the array; the array
   and collect ids are here and in `run.json`. One row per run, as the rule requires.
5. **The run id uses Spartan local time (AEDT, UTC+11)**, as every run in this project does.

## Lead verdict (2026-10-25)

**Accepted.** The five pre-registered numbers are the ticket's, and I recomputed all of them from
\`out/lanes.tsv\` myself (296 rows; the \`at_bar\` field agrees with the median/coverage columns on
every row; per-pot table reproduced lane for lane; 13 below-bar rows, exactly the listed 13).

1. **This is the baseline to quote from now on: 281 of 292 sound lanes at bar (96.2%)** -- 283/294
   valid, 283/296 measured. The old 265-of-294 figure stays history: different binary, different
   growth angle, different sampled cloud.
2. **Replication, and the strongest evidence in the run**: Pot J 09 reproduces ticket 290 exactly --
   Bl0 79 / 1.079 / 70.89 / 75.68 and Bl1 91 / 1.913 / 50.55 / 63.77, digit for digit. Two runs, two
   days, the same frozen cloud: the pipeline is deterministic on that piece and the scorer agrees
   with the one used before.
3. **Ten of the eleven sound misses are not blindness.** Nine sit at median 0.67-0.88 mm with total
   length within 5% of the reference (len ratio 1.01, 1.01, 1.02, 1.05, 1.20, 1.21, 0.92, 1.01,
   1.01; median ratio over all 296 lanes is 0.99). Same route, similar length, one stretch beyond
   2 mm: the extent/contour family already diagnosed on Pot H 02/H 10 in ticket 286, now with nine
   more members across pots D, E, H and I. \`Pot_D_Piece_27\` is the clearest: 1.2x the reference
   length at 0.67-0.80 mm median with 62-73% coverage -- our line runs past the end of theirs.
4. **Two are genuinely different contours.** \`Pot_C_Piece_03\` lane 1 (11.28 mm, 2.23x the reference
   length) is the known base-band partition mismatch of tickets 278/279, unchanged. \`Pot_I_Piece_25\`
   **both lanes** (6.91 / 6.95 mm, zero coverage both ways, our loop crossing outside a smaller
   reference loop in the pictures) is **new and unnamed**; it gets its own ticket, not a line here.
5. **One jump survives in the shipped code**: \`Pot_C_Piece_02\` lane 1, a single 37.712 mm step at
   median 0.530 mm, so at bar. Recorded, not diagnosed; the stop rule does not cover it because the
   step is taken with fresh dots available.
6. **Weight, stated plainly**: one draw per piece, one binary, one commit, no repeat runs. The mesh
   stage is piece-dependently non-deterministic (ticket 291: Pot H 02 moves 0.867 mm between two
   runs of the same bytes), so **a lane within about 1 mm of the bar must not be quoted as clearing
   or missing it on this run alone**. The nearest such case is \`Pot_D_Piece_22\` lane 0 at 86.40%
   coverage against a 90% bar.
7. **A defect found by the run, fixed**: \`scripts/stage_piece.sh\` read the PCD header as
   \`head -20 | awk ... exit\`, which under the script's own \`pipefail\` can kill head with SIGPIPE and
   abort the stage; it hit 22 of 148 pieces, each on its first attempt, and the array's retry hid it.
   Fixed in \`19b78a7\` (awk reads the file directly, no pipeline). The array's 3x retry stays as a
   belt, not as the fix.
8. **Deviations accepted**: three array attempts before the counting run (status variables, scorer
   path, a stale copy) with their output cleared so \`lanes.tsv\` is one run; pot montages built in the
   collect job; \`index.tsv\` jobid is the build job with the array and collect ids in \`run.json\`.
9. **What this does not settle**: why a stretch of a nine-lane family sits beyond 2 mm while the
   route and length agree, and what \`Pot_I_Piece_25\` is. Both are now measurable on inputs that can
   be staged again (tickets 290, 291), which is the difference between this and every earlier tally.