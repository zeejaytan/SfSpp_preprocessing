# What is in stage40/instruments, and where each file came from

Ticket 40 asks whether `SFS_REASSIGN_MODE=own` is a general repair or a two-piece coincidence.  It
reuses ticket 39's instruments unchanged wherever a number must stay comparable, and adds the grid:
three groups (g1 synthetic Juglet, g2 released Juglet, g3 released Pot A), both arms of every piece
in the same job on the same cloud.

## Copied verbatim from stage39/instruments (content-identical)

| file | note |
|---|---|
| `mesh38.py`, `measure34.py`, `grow38.py`, `replica37.py`, `nest39.py`, `fig39.py` | byte-identical copies of stage 39's instruments; all measurement and figure semantics come from them |
| `measure35.py` | content-identical copy except line endings: it arrived CRLF and was converted to LF so the submitter's CRLF gate passes (content unchanged otherwise; the thickness machinery `wall40.py` lifts lives here) |
| `stage_synth_p40.sh` | stage 38/39's stager under its ticket-40 name (same script the sbatch template's STAGER points at); symlinks mesh and cloud, copies the axis, writes `inputs.md5` |
| `.gitattributes` | `* -text`, so git never rewrites a line ending here |

## New in stage40

| file | what it adds |
|---|---|
| `run_cell40.sh` | the grid driver: pass 1 stages every cloud of the phase's group and gates the CONTROL cells (g1 pieces 2 and 9) against ticket 39's own numbers before any cell runs (exit 9 otherwise); pass 2 runs arm A (radius) then arm B (own) per piece on that same cloud, measures each surface (grow38 surface + nest39 count), pairs the two surfaces per arm (grow38 surfacepair + nest39 pair), measures the wall (wall40.py on the cell's own SampledWithNormals.ply, against ticket 35's recorded medians), keeps an xyz-vs-ply census, counts and then deletes only the stage (the cell's surfaces are KEPT), and closes with switch_proof.tsv counting the cells whose own log line says mode=radius / mode=own against the planned count. |
| `wall40.py` | the wall-thickness instrument: ticket 20's 800-ray method lifted verbatim from measure35.py's thickness block (read_obj / weld / read_ply_vertices / ray_hits / sheets and the ray loop), one mesh + one arm ply -> one JSON, because ticket 40 measures every cell inside the job that produced it. |
| `fig40.py` | figure F2: reads the nest and cell tables the cells wrote and draws shared_over_smaller and mean_normal_dot, arm A against arm B, every piece on one axis, Pot A pieces flagged against the regression line (shared > 0 or dot > -0.9).  A categorical axis has no mm/px, so its JSON records the pixel size. |
| `run_fig40.sh` | the figure driver lifted from one piece to a whole group: per piece that wrote both surfaces in both arms, fig39 render (F1 views + F3 signed histogram) from the same surface bytes the tables measured; a piece that did not is recorded as missing in figures.tsv, not skipped; then fig40.py f2. |
| `submit40.sbatch.tmpl` | the batch script: three phases (1 = g1, 2 = g2, 3 = g3), build from the pushed commit, anti-drift instruments gate against stage40 paths, corpus and /opt/sfs-pristine recorded before and after (md5s now also cover $DS/Axes/Pot_A), cells then figures per phase, closing delete that KEEPS `*/cells-pipeline/*/surfaces/*.ply` for the lead and records what it kept, index row with verdict and human_note left empty. |
| `submit40.sh` | the renderer: phase validation 1\|2\|3 (one per group), placeholder check, CRLF gate over every script, bash -n plus py_compile of the new instruments, ticket-40 run.json, then sbatch. |
| `COPIES.md` | this file |

## Deliberate differences from stage 39's driver

- **The grid, not two cells.**  CELL_LIST entries are GROUP:POT:PIECE:LEVEL:KIND; g1 pins
  SFS_DOWNSAMPLE_TARGET to its synthetic cloud's size, g2/g3 set nothing so the pipeline downsamples
  itself exactly as shipped.
- **Only the CONTROL cells gate.**  g1 pieces 2 and 9 must reproduce ticket 39 exactly (exit 9
  otherwise); g2/g3 anchor cells are recorded in the tables (anchor_hit) but do not stop the run,
  because there is nothing upstream of them in THIS ticket to be unfaithful to.
- **The wall thickness runs inside the cells**, on the cell's own SampledWithNormals.ply before the
  stage is deleted, against ticket 35's recorded medians within 5%.
- **The cells' surfaces are KEPT** through the job's closing delete (named in the delete record);
  ticket 39 deleted everything.
- **Budget skips are recorded, not silent**: a piece whose arms would not both fit in the phase's
  cell budget gets a SKIPPED row in pipeline_cells.tsv.
