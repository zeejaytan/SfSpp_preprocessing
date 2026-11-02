# 61 — Give the growth stop a sound normal field, then ask whether it stops at the break surface

**What to build:** the same nine pieces, run through the same chain with the same stop rule, but
with the normal field the stop test consumes taken from the corpus cloud instead of the
pipeline's per-rung re-estimate. The question is narrow: **with a sound field, does the
break-surface stop fire where it should, or does the rule still fail?** Either answer closes the
stop-rule line of enquiry for now; a positive one means the rule was right and the field was
broken; a negative one means the rule itself does not work and it should be parked.

**Why now (2026-11-02, conservator):** after ticket 60's diagnosis he chose options 1 and 2 —
"1 and 2 ... do 1 and 2 using cursor_code". This ticket is option 1.

**Answers:** U19 (does the pipeline put the Juglet back together), E1 (do our breaklines let SfS
find joins)

**Blocked by:** none

**Status:** ready-for-agent
**Working in:** chat on Thinkbook16 (2026-11-02)
**Branch:** 61-sound-field-stop-test, in /c/PR/worktrees/sfs/61
**Worker:** unassigned

## Spec

### Given (measured facts this stands on)

1. Ticket 59 implemented the stop as an opt-in switch and ran it: with `SFS_BREAK_STOP=1` on
   J1 the surface collapses from 13850 points to 351 and the piece loses its genuine pair, while
   the other eight barely move. Nothing was merged; the patch lives in
   `.scratch/juglet-breaklines/stage59/stage1/mesh_processing_headless.patched.cpp` beside the
   clean `.lf.cpp` it was made from, and the run of record is
   `/data/gpfs/projects/punim2657/SfSpp/runs/20261102-1416_638504b_t59-breakstop-arm`.
2. Ticket 60 found why, and it is not the clay and not the rule: **the field is scrambled**. Measured
   against the mesh, the per-rung re-estimate is sign-flipped on **41.63 %** of J1's 19312 points,
   against 0.18–1.70 % on the other eight. The stored normals of the corpus cloud
   (`Dataset/Point/Juglet/<piece>_Point.pcd`, FIELDS x y z normal_x normal_y normal_z on all
   nine) are **0.40 %** flipped on J1. Of J1's 17638 break-like points, 96.14 % do find clay
   within 0.45 mm along the march, but with a normal pointing the *same* way — the two facing
   walls carry normals pointing the same direction, so a rule asking for `dot <= -0.4` must
   refuse them. Split by sheet: S0 89.75 % flipped, S1 2.40 % — one whole sheet inverted.
3. The pipeline already has a switch that carries the input normals instead of re-estimating:
   `SFS_NORMAL_SOURCE=input` (tickets 33/34), with `SFS_NORMAL_CARRY=mean|nearest`. It is wired at
   `mesh_processing_headless.cpp:1005`, `:1082` (downsampling) and `:3795` (the growth stage, which
   re-loads the rung PLY and is the call whose output the stop test consumes). In this mode MST is
   deliberately **not** applied, and a point with no usable source normal is counted and reported
   (`[NORMAL-33] ... carried= nearest= missing=`), never silently filled.
4. Nothing in the ticket-59 arms set that variable: `submit-arm.sbatch` unsets it, so the t59
   armed run consumed the re-estimated field throughout.

### The four cells

All nine Juglet pieces, `SFS_WORNESS=0.7`, binaries built from this ticket's commit with the t59
patch applied exactly as ticket 59 applied it (only `computeBreakStopFlags59` and its call site
differ from the clean file — reproduce that diff, do not re-invent the rule).

| cell | `SFS_NORMAL_SOURCE` | `SFS_NORMAL_CARRY` | `SFS_BREAK_STOP` | what it isolates |
|------|----------------------|---------------------|------------------|------------------|
| U    | unset                 | unset               | unset            | the t55 baseline (identity gate) |
| I    | input                 | nearest             | unset            | what a sound field does to the surfaces and breaklines alone |
| UA   | unset                 | unset               | 1                | the t59 armed run (identity gate) |
| IA   | input                 | nearest             | 1                | **the question**: the rule given a sound field |

`nearest` is chosen over `mean` for the carried cells because it keeps every source sign
verbatim with no averaging ball (ticket 34); say in the Results why, and if a cell shows
`missing` above 1 % of points, report it rather than patching around it.

### What is measured, per piece, in every cell

- **The field actually consumed**, not the field intended: with `SFS_NORMAL_DUMP_DIR` set, the
  rung-1 normals PLY, sign-flipped fraction against the nearest mesh face normal, and the folded
  angle. This is the column that says whether the switch did anything on the piece — printed
  `[NORMAL-33] carried=` is the corroboration, not the proof.
- The ticket-57 separation metrics, exactly as `check_separation.py` takes them:
  `nS0`, `foldS0`, `blindDeg`, `farS0`, `dc_ge1`, `bl0`, `genuine`. Invocation flags are
  `--geom --mesh-dir --walls --pieces`; note it is **not** `--geom-dir`, and `--pieces` takes
  comma-joined full names.
- Where the S0 boundary sits against the true break edge, if the existing instrument produces it
  cheaply (ticket 60's nearest-S0-point-to-true-edge distance); otherwise say it was not measured.

### Gates (both must pass before any conclusion is drawn)

1. **Identity, U vs t55.** The default-field, disarmed, `WORNESS=0.7` cell must reproduce the t55
   run of record per piece — S0 md5 where the piece is deterministic, and the printed parameters —
   or the build or the cell is wrong. Use t55's own rule for which pieces are deterministic
   (J1's flip draw is not).
2. **Identity, UA vs t59.** The default-field, armed cell must reproduce t59's armed numbers, in
   particular J1's collapse (S0 351 points) and the nine `wall_like` counts
   (1674/1647/2475/2407/5121/3921/6926/3136/1231). If it does not, the instrument differs from
   ticket 59's and the run is void.
3. **The switch has to be shown working.** On J1, `carried` must equal the rung point count
   (19312 at rung 1), `missing` must be small and reported, and the consumed-field flip rate must
   fall from 41.63 % to **at most 5 %**. A cell where input mode silently fell back to the
   re-estimate is a failed cell, not a negative result.

### The decision this ticket exists to reach

With the sound field (IA) on J1:

- **Positive** — the stop no longer collapses the surface, the S0 boundary stops short of the
  true break edge rather than across it (`farS0` well below the 0.86 of the armed default run),
  and the nine still give 9/9 genuine pairs: the rule is right and the field was the fault; record
  it and hand the field question to ticket 62.
- **Negative** — with a sound field the stop still fails the same way, or now fails differently:
  record it and recommend parking the stop rule.
- **Partial** — say exactly which pieces move and which do not, and do not average over the nine.

Report `farS0`, `blindDeg` and `nS0` per piece, never a mean, and state which of the three
claims is being made (method failed / measurement broken / reference wrong).

### Deliverables

- Run directory `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t61-soundfield`
  with `run.json`, `submit*.sbatch`, `logs/`, `out*/`, and the index row appended.
- Tables: one row per piece per cell, the columns above; a `decision_table.tsv` naming the
  verdict per piece.
- Two or three PNGs a conservator can read: J1 before/after under UA and IA at the same camera,
  and the field colouring (sign vs mesh) for U and I on J1.
- `## Results` in this ticket appended by the worker: jobs with `sacct` State/ExitCode, both
  gates with the command and the value, the tables, the verdict, and the names of what was not
  measured.
- **No commits, no tracked source edits.** The patch and the instrumented file stay in the run
  directory, exactly as in tickets 59 and 60.

### Budget and discipline

Two sbatch jobs, wall time 1 hour total (t59's armed nine-piece arm took 7 m 55 s). Compute nodes
only. Build inside the job from the ticket commit; check the built binary's md5 against the
patched binary the job records. Corpus read-only. Poll every job with
`scripts/slurm_poll.sh <JOBID>` and record `sacct` State/ExitCode in the Results. If a gate
fails, stop and report rather than spending the second job.
