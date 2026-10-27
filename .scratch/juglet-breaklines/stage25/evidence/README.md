# Stage 25 — per-step geometry ladder (ticket 25)

Ticket: `.scratch/juglet-breaklines/issues/25-dump-the-geometry-at-every-step.md`.
The instrumentation is in `mesh_processing_headless.cpp` (one block at the top of the file plus
hooks at five steps). This directory holds the harness that ran it and the evidence it produced.

## Run of record

    /data/gpfs/projects/punim2657/SfSpp/runs/20261027-0337_d69f76f_t25-dump-grid2

Slurm job 33858581, State COMPLETED, ExitCode 0:0, Elapsed 00:02:24, 8 cpus.
NEW = d69f76fd7b3645811f35815ab3062c58ff988d1c OLD = d543e18627c02354732bd9e7f33eb21d8dbbbce2 (see `run.json`: the tip of main, a398d8a, was
not on origin when the job was written; `git diff a398d8a d543e18 -- mesh_processing_headless.cpp`
is empty).

32 cells: four Juglet pieces (2, 3, 5, 7) x eight tags — B, D, E with `SFS_DUMP_STAGE` set,
A, A2, OLD, DOLD, EOLD with it unset.
B = defaults (0.6 mm step, paper chain on); D = `SFS_PAPER_CHAIN=0`;
E = `SFS_PAPER_CHAIN=0` and `SFS_DOWNSAMPLE_TARGET=-1` (native density);
A/A2 = new binary twice; OLD/DOLD/EOLD = pre-change binary, DOLD and EOLD with the same env as D and E.

## What is in `evidence/`

| file | what it is |
|---|---|
| `cells25.tsv` | one row per cell: exit, dump-file counts, which rungs exist, whether a dump root appeared, dump write/refuse counts, written surfaces, outcome, cluster count |
| `ladder.tsv`, `ladder_summary.txt` | one row per (arm, piece, rung) with the expectation copied from the ticket's table, the measurement read from that rung's sidecar, and pass/fail. Evidence only — it makes no claim that a segmentation is right or that a merge should have fired |
| `defaults_proof25.json`, `proof.log` | per written surface, the sorted multiset of six-column point lines (x y z nx ny nz) per arm: `pointset_equal`, the counts that differ only in one arm, and the nearest-neighbour displacements. md5 is **not** used: the exported PLY carries an uninitialised curvature column |
| `jsoncheck.log` | every sidecar parses as JSON, every PLY is ASCII with a header count equal to its body rows and carries `cluster_id` and `reason` |
| `GEOMETRY_DELETED.txt` | per cell, per extension: files and bytes deleted when the staged tree went; totals, kept dumps and surfaces, stage trees left, geometry outside `surfaces/` |
| `inputs_before.md5` | the cloud, mesh and boot axis of each piece with md5 and point count; identical before and after (12 rows), as is the corpus tree (1803 rows) |
| `figures25.txt`, `figures.log` | one row per figure: panels, pixel size, span in mm, mm per pixel, scale-bar value, row count, missing rungs |
| `cells.log`, `slurm-33858581.out` | the job's own cell output and the batch log |
| `run.json`, `submit.sbatch` | the run's parameters and the exact script submitted |

The figures themselves are PNGs in the run directory, `out/figs/` (F1–F6), not committed here.

## Instruments

`stage_piece_p25.sh` stages one piece's cloud, mesh and axis by symlink and records md5 and point
counts; `run_cell25.sh` runs one (tag, piece) cell, keeps its dumps and deletes its stage tree with
counts; `submit_25.sbatch.tmpl` is the batch script with `__PLACEHOLDERS__` (instantiate with sed);
`ladder25.py`, `defaults_proof25.py`, `figures25.py` and `json_check25.py` read the run directory
and write `out/ladder.tsv`, `out/defaults_proof25.json`, `out/figs/*.png` and the JSON/PLY summary.

All four Python instruments and both shell scripts were exercised against a synthetic mock tree
before submission (then deleted); the only outputs in this directory came from the job above.

## Not done here

- `/opt/sfs-pristine` does not exist on this host: recorded as ABSENT in `GEOMETRY_DELETED.txt` and
  `corpus_before.txt`, never created.
- The ladder dumps stay in the run directory because they are the deliverable; nothing in
  `out/dump/` was deleted.
