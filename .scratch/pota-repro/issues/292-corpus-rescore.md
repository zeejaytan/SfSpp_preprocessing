# 292 — Re-score the frozen corpus at the shipped defaults

Answers: E1
Status: in-progress (worker: corpus re-score, 148 array tasks)
Working in: C:/PR/worktrees/sfs/292
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
