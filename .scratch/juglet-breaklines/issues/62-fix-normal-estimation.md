# 62 — Fix the per-rung normal estimation so a full-round shell stops flipping

**What to build:** a diagnosis of **why** the pipeline's own normal re-estimate inverts one whole
sheet on a round piece, and a measured candidate fix that a person can then decide to adopt. The
fix must be opt-in: no shipped default changes in this ticket.

**Answers:** U19, E1

**Blocked by:** 61 (same source file; run 61 first, its run directory is this ticket's baseline)

**Status:** ready-for-agent
**Working in:** chat on Thinkbook16 (2026-11-02)
**Branch:** 62-fix-normal-estimation, in /c/PR/worktrees/sfs/62
**Worker:** unassigned

## Spec

### Given (measured facts this stands on)

1. On J1 the per-rung re-estimate is sign-flipped on **41.63 %** of 19312 points against the mesh;
   the other eight sit at 0.18–1.70 % (ticket 60, `out/analysis2/B_normals.tsv`). The corpus
   cloud's own stored normals on J1 are 0.40 % flipped — the pipeline's field is worse than the
   one it was handed.
2. The split is **per sheet, not per point**: S0 89.75 % flipped, S1 2.40 %, and the wall-like
   rate differs the same way (0.020 vs 0.141). That is the signature of an orientation pass that
   decided a hemisphere once and propagated it, not of per-point noise.
3. The default path is CGAL `pca_estimate_normals` with `nb_neighbors = max(5, min(20, n/1000))`
   (`mesh_processing_headless.cpp:680`), then `CGAL::mst_orient_normals` at `n24orientK`
   (`:806-809`). For J1's 19312 points that is **k = 19**, and the printed line for the run of
   record reads `[NORMAL-24] ... n=19312 k=19`.
4. The wall is ~2.1 mm (ticket 60's per-piece thickness, J1 1.876 mm) and the rung spacing is
   0.45 mm-ish, so a 19-neighbour ball has a radius of several millimetres — **wider than the
   wall**. On a full-round shell the kNN graph therefore bridges the two faces, and MST orientation
   over a bridged graph can only give the two faces one consistent direction: exactly what is
   observed. This is the prime suspect, not yet measured.
5. A radius path exists (ticket 24): `SFS_NORMAL_MODE=radius` with `SFS_NORMAL_RADIUS_MM` or
   `SFS_NORMAL_RADIUS_AUTO=1` and `SFS_NORMAL_RADIUS_MULT` (multiple of the cloud's own spacing).
   It is untested against this failure.

### Stage 1 — measure the bridging (read-only, no pipeline change)

On J1 and, as controls, J2 (the nearest-resolution piece) and J7 (the other wrapping piece):

- the distribution of the 19th-neighbour distance, against the piece's wall thickness;
- the fraction of kNN-graph edges that cross the wall (an edge crosses when its two endpoints' mesh
  normals are opposed, `dot < -0.4`, and their separation is below twice the wall);
- which MST component the flipped sheet belongs to: is S0's flipped region one connected component
  of the bridged graph, or many small ones?
- the same three numbers at k = 6, 8, 10, 12, 19 and at radius 0.6 / 0.8 / 1.0 / 1.4 mm, so the
  threshold where bridging stops is bracketed by measurement rather than guessed.

Deliverable: a table and one figure (crossing fraction against neighbour scale, with the wall
thickness drawn as a vertical line).

### Stage 2 — the candidate fix, judged end to end

Take the smallest neighbour scale at which J1's bridging collapses (the knee). Run the nine pieces
at `SFS_WORNESS=0.7` with the t59 patch applied, in two cells:

- **F** — that normal setting, stop **disarmed**: does the field fix itself, and do the surfaces
  stay as t55's?
- **FA** — that normal setting, `SFS_BREAK_STOP=1`: does the stop then work (this duplicates
  ticket 61's IA cell on a different field; report both, they are different fields and must not be
  conflated).

Per piece: the consumed-field flip fraction and folded angle (against the mesh, as ticket 60 did),
`nS0`, `blindDeg`, `farS0`, `dc_ge1`, `bl0`, `genuine` from `check_separation.py`
(`--geom --mesh-dir --walls --pieces`, full names, comma-joined).

### Gates

1. `[NORMAL-24]`/equivalent line shows the intended neighbour scale took effect on every piece
   (radius mode and count mode print different fields — quote the line).
2. The fix must **not** move the other eight: each of J2–J9 within 2 percentage points of its
   current flip rate and its `nS0` within 10 % of t55's, or the fix is a regression and the
   ticket says so.
3. Nothing is adopted on the strength of J1 alone; a fix that only works on the wrapping piece is
   recorded as such.

### The outcome this ticket exists to reach

- **A usable setting** — J1's flip rate falls to at most 5 %, folded median stays at or below 5°,
  the eight do not regress, and the armed stop behaves better than in ticket 59: propose the
  setting as opt-in (a named switch with its measured numbers), give the exact call line, and put
  the proposal in the ticket for the conservator — **do not change a default**.
- **No usable setting** — say so with the bracketing numbers, and recommend either carrying the
  corpus normals as a documented pre-step or leaving the field alone.

### Deliverables

- Run directory `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t62-normalfix`,
  `run.json`, `submit*.sbatch`, `logs/`, `out*/`, index row appended.
- `stage1_bridging.tsv`, `stage2_pieces.tsv`, `decision_table.tsv`, and the bridging figure.
- `## Results` in this ticket: jobs with `sacct`, the gates with command and value, the tables,
  the verdict, what was not measured.
- **No commits, no tracked source edits, no default changed.** Any patch stays in the run
  directory.

### Budget and discipline

Three sbatch jobs, wall time 2 hours total. Compute nodes only; corpus read-only; poll each job
with `scripts/slurm_poll.sh <JOBID>` and record `sacct` State/ExitCode. If Stage 1 shows no
bridging at all, the hypothesis is dead — stop, report that, and do not spend Stage 2's jobs.
