# What is in stage39/instruments, and where each file came from

Ticket 39 asks whether `SFS_REASSIGN_MODE=own` keeps the two exported faces apart.  It reuses
ticket 38's sampler, subdivision and measurements unchanged, so that the only difference between
this ticket's cells and ticket 38's is the admission rule under test.  Nothing here re-derives a
number stage 38 already defined; a re-derivation would make the two tickets' tables incomparable
for reasons that have nothing to do with own mode.

## Copied verbatim from stage38/instruments (byte-identical, `cmp`-verified)

| file | md5 | what it is |
|---|---|---|
| `mesh38.py` | `a5e8ff2523229a592189acd82be02cef` | mesh reader, midpoint subdivision, displacement to the original surface, surface sampler with analytic face normals, nearest-neighbour spacing, PCD writer, sampler validation |
| `measure34.py` | `055090a5577ca1e8066a6e4f5146a3f2` | PLY/PCD/OBJ readers, PCA normal fallback, folded angle, 2 mm coverage, the corrected pair statistic (`pair_pointwise` / `pair_stats`) |
| `grow38.py` | `2935869749eea7ae44341bdfe1d9e17a` | the `surface` and `surfacepair` measurement commands this driver calls |
| `replica37.py` | `e190a7948fdf1d65a9f7195e0450a764` | ticket 37's region growing, unchanged |
| `stage_synth_p38.sh` | `9bb59676bc08157687010955d1d9ebc8` | the stager: symlinks mesh and cloud, copies the axis file, writes `inputs.md5` with every row tagged SYNTHETIC |
| `.gitattributes` | — | `* -text`, so git never rewrites a line ending here |

All are LF-only.  `stage_synth_p38.sh` keeps its stage-38 name on purpose: the md5 in the table
above is the file the job's anti-drift gate compares against the pushed commit, and renaming it
would only make the two tickets' stagers look like different instruments.

## New in stage39

| file | what it adds |
|---|---|
| `nest39.py` | the three derived quantities ticket 39 asks for: distinct point count per surface, the shared-position count and fraction both ways and of the smaller (coordinates rounded to 1e-4 mm, the rounding `check38.py` used), the mean-normal dot, and the median per-point folded angle between the two surfaces' normals at matching positions.  Readers and the folded-angle definition are `measure34`'s, imported, not re-implemented. |
| `run_cell39.sh` | the driver: pass 1 samples one cloud per piece and gates it against ticket 38's own numbers before any cell runs; pass 2 runs arm A (radius) then arm B (own) on that same cloud, per piece, in the same job. |
| `submit39.sbatch.tmpl` | the batch script: one phase, build from the pushed commit, anti-drift instruments gate, corpus and `/opt/sfs-pristine` recorded before and after, geometry counted and deleted, index row with verdict and human_note left empty. |
| `submit39.sh` | the renderer: placeholder check, CRLF gate over every script, `bash -n`, `run.json`, then `sbatch`. |
| `COPIES.md` | this file |

## Deliberate differences from stage 38's driver

- **One cloud per piece, two stages.**  Arm A and arm B stage the *same* synthetic cloud, so the
  arms cannot differ by a sampler draw.  Stage 38's driver sampled inside the cell; here the
  sampling is pass 1 and its result is gated before either arm runs.
- **The cloud gate stops the run.**  If a cloud does not reproduce ticket 38's point count and
  median spacing, the driver exits 9 and no cell runs — a comparison against a different cloud is
  not the comparison the ticket asks for.
- **Arm A is checked against ticket 38's per-surface counts** and the result is written into the
  cell row (`ctrl38_reproduced`), so a void control is visible in the table rather than inferred
  from prose.
- **The admission lines are kept separately.**  `logs/admission39.log` holds `[REASSIGN-22]` and
  every `[WINDOW-26*]` line verbatim, which is what the ticket asks to be quoted.
- **`SFS_REASSIGN_MODE` is unset in the job environment** and set per invocation, so arm A is
  genuinely the shipped default rather than a variable that happened to be inherited.
- **Pot A is not in this job.**  Ticket 39 excludes it deliberately: it is the reference from the
  other density group, not a silent sherd, and run 6 on ticket 38 showed its cell is what the wall
  clock kills.
