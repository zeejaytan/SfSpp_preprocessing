# stage 36 — adaptive sampling spacing with the scan's own normals

Ticket: `.scratch/juglet-breaklines/issues/36-adaptive-spacing-with-the-honest-normals.md`
Answers: U19, E1. Branch: `36-adaptive-spacing-with-the-honest-normals`.

**No source is changed by this stage.** Every switch it turns was already on main; the ticket's
question is what the pipeline does when three of them are on at once, which no arm before this one
had ever tried.

| arm | switches | what it isolates |
|-----|----------|------------------|
| A   | none | today's shipped default: fixed 0.6 mm step, floor 50, re-estimated normals |
| A2  | none, again | the piece's own run-to-run spread |
| B   | `SFS_SPACING_POLICY=piece SFS_SPACING_SAMPLES=200` | adaptive step `S = min(0.6, max(s0, diag/200))` |
| C   | as B + `SFS_NORMAL_SOURCE=input SFS_NORMAL_CARRY=nearest` | the scan's own normals at that step |
| D   | as C + `SFS_SINGLE_CLUSTER=write` | so a one-region outcome is measurable, not thrown away |

`SFS_COUNT_SCALE` is **unset in every arm**, so the floor stays the literal 50 — that is what makes
this grid different from ticket 22's `C2_*` arms, which scaled the counts as the step changed.

Pieces: Juglet 1, 2, 3, 5, 7, 9 and Pot_A 01–08 = 14 pieces × 5 arms = **70 cells**, one job.

## Why the instruments are not the stage-34 ones

They are, except where the question differs:

| file | provenance |
|------|------------|
| `instruments/measure34.py` | ticket 34, **copied byte-identical** (md5 `e9f3b28be4908b4008b99d8085c8c948`) — the surface row, coverage, folded angle and pair statistics are the same measurements, so the numbers are comparable |
| `instruments/pair_ref30.py` | ticket 34's copy of ticket 30's ruler, **copied byte-identical** (md5 `c6c18b634f5324bee22127975e8cc529`) |
| `instruments/compare36.py` | `compare34.py` with two changes: it reads `logs/lines36.log`, and its `KINDS` also keeps `[SPACING-22]`, `[COUNT-22]`, `[SWITCH-23]` and `[NORMAL-34]`. Nothing in `compare_file` (the byte/sorted-points identity test) is touched |
| `instruments/run_cell36.sh` | the stage-34 cell runner, plus the `[SPACING-22]` and `[COUNT-22]` fields parsed into `cell.tsv` (33 columns) and minus the floor-ceiling ladder, which cannot fire with the counts unscaled |
| `instruments/stage_piece_p36.sh` | the stage-34 stager, unchanged in behaviour: symlinks the mesh and the cloud, copies only the axis, md5s all three |
| `instruments/submit36.sh`, `submit36.sbatch.tmpl` | the stage-34 submission path; one binary instead of two (this ticket changes no source, so there is no "before" binary to build), one arm list of five |
| `instruments/fetch_instruments36.sh` | new: copies the instruments out of the **pushed commit** and proves they are LF before anything is submitted |

### The carriage-return trap, and why `fetch_instruments36.sh` exists

The committed blobs of this project's instruments carry carriage returns (`git show <sha>:
.scratch/juglet-breaklines/stage34/instruments/measure34.py` has 890 of them). Two grids in this
project have already died on `set: pipefail: invalid option name` because a CR reached bash. So the
run directory's instruments are derived from the sha under test with `git archive`, every file is
normalised, and `grep -lU $'\r'` plus `bash -n` must both come back clean before `sbatch`.
`submit36.sh` checks again on the rendered `submit.sbatch` and refuses with exit 4.

## What the run directory keeps

```
out/cells36.tsv      one row per cell, 33 columns: the step actually used, the points entering
                     clustering, the clusters at the last retry, the floor and where it came from,
                     the outcome, and both surface point counts
out/surfaces34.tsv   per-surface points, extent, 2 mm coverage, folded angle to the mesh
out/pairs34.tsv      the pair statistics per cell
out/carried34.tsv    what the carry actually carried (ticket 34's instrument, unchanged)
out/pairs30.tsv      ticket 30's ruler over every cell that wrote two surfaces
out/defaults2.tsv    A against A2: byte identity, then sorted-point identity, per surface file
out/lines36.tsv      every [SPACING-22]/[COUNT-22]/[SWITCH-23]/[NORMAL-3x]/[PAPER-234]/[RETRY-23]/
                     [STATUS-23] line each cell printed, one row per line
out/inputs_before.md5, out/inputs_after.md5, out/corpus_before.txt, out/corpus_after.txt,
out/pristine.txt     the before/after identity of every input and of the frozen corpus
out/GEOMETRY_DELETED.txt  per-extension file and byte counts, written before the delete
out/GEOMETRY_KEPT.txt     cells whose stage and rung dump were kept because the measurement failed
out/cells/<tag>/<pot>/<piece>/  cell.tsv, logs/, surfaces/ (both .ply and .xyz), measure/
```

The stage and the ticket-25 rung dump are deleted per cell, after the measurement has read them,
behind a count written first. Surfaces, logs and every table stay.
