# Ticket 80 — Default the wall-pair filter on, and stage the new edgeline on every Juglet piece for the eye

**What to build:** Two things, in this order. (1) Flip ticket 79's switch so the wall-pair rule is **on by default** — `SFS_WALL_PAIR_FILTER=off` (or `0`) becomes the only way to turn it off — and prove with the cells that the default reproduces ticket 79's wall-pair arm and that the explicit off still reproduces its off arm. (2) Stage the **old and the new edgeline together** on all nine Juglet pieces, in the visual-qa viewer, so the conservator can say with their own eyes whether the re-traced line is right before any assembly run is spent on it. Land nothing that the conservator has not seen.

**Answers:** E1
**Blocked by:** none — ticket 79 is merged on `main` (`b00d02f`; do not merge it again, verify it is an ancestor of `HEAD` instead).
**Status:** ready-for-agent
**Worker:** unassigned
**Budget:** medium (one default literal plus its banner, one rebuild, the six cells plus two identity re-runs, one overlay builder over 27 piece-arms, three visual-qa descs, one offscreen render)
**Hand-over:** DeepSeek: read ticket 79 in full (the switch, its five overrides, the cells, the identity trap) and `C:/PR/artifacts/t79/gate79.tsv`, plus the overlay precedent `C:/PR/artifacts/visual-qa/edgeline_juglet/build_overlay.py` and its two descs `C:/PR/visual-qa/viewer/pairs/edgeline_juglet_{gallery,truepose}.json`. Do Part A, then Part B, then stop at the eye gate with `End state: waiting:`. Do not run any assembler work; that is ticket 81.

---

## Why this ticket exists

Ticket 79 put the rule in the pipeline but left it **off by default**, because a default-on change to every future run is a decision for the conservator, not the worker. The conservator has now made that decision (2026-11-17): **default on**.

Ticket 79 also verified its result by numbers — off-lip dot counts and chord lengths on Sherd 7 and the controls — and by a small render. Numbers cannot see a **stepped boundary**: where the filter removed the flap, the re-traced line is visibly stepped, and the dot count is blind to it. The conservator's rule here is the workspace's: *look at it before trusting the numbers*. So the same ticket carries the eye gate, and the assembly run that depends on the line waits behind it.

## Part A — default on

A.1 **The edit.** In `mesh_processing_headless.cpp`, `namespace t79`'s `readEnv()` (the switch is parsed at `:2720`, `g_mode` initialised at `:2721`):
- default becomes `pair` with **no** environment variable set;
- `SFS_WALL_PAIR_FILTER=off` or `=0` disables it; `=pair` stays accepted (a no-op spelling);
- any other value must still warn and stay **off** exactly as now (`:2727`), because an unreadable value is not consent to filter;
- the banner at `:2740` must name **where the state came from**: `on (default)`, `on (env)`, `off (env)` — so a log can never be ambiguous about whether the run meant to filter.
Nothing else in the rule moves: same band, same `ed`, same guards, same `maxdrop`, same `[SFS-79] WALLPAIR` line. Do not touch `class/`, `hpc/`, the stagers, or `stage66/run_cell66.sh`.

A.2 **Rebuild** by the route ticket 79 used (`bin-base` untouched; a new `bin-80`), and record the binary's md5 and the source diff.

A.3 **Cells.** `stage66/run_cell66.sh` at exactly ticket 78/79's settings (`WORNESS=0.7`; 3× `SFS_NORMAL_MODE=radius SFS_NORMAL_RADIUS_MM=1.0 SFS_MERGE_CLUSTER_DOT=0.887 SFS_GROW_BASE_MM=1.5 SFS_GROW_BASE_THETA_DEG=25 SFS_TREE_UNITS_PER_MM=3.0`; 1× and Pot A `SFS_TREE_UNITS_PER_MM=1.0`; no `SFS_REFINE_*`). Six cells plus two spread re-runs:

| cell | binary | switch | must reproduce |
|---|---|---|---|
| `def_3x` | new | unset | ticket 79 `wp_3x`: Sherd 7 ≤ 3 dots in a patch ≤ 3.0 mm |
| `def_3x_b` | new | unset | `def_3x` within the ray-cast spread (2 dots vs 2) |
| `off_3x` | new | `off` | ticket 79 `off_3x`: 34 off-lip dots, patches 15.601 / 2.400 / 0.600 mm |
| `def_1x` | new | unset | ticket 79 `wp_1x`: J1 6 dots, longest run 5.400 mm |
| `off_1x` | new | `off` | ticket 79 `off_1x`: J1 20 dots, longest run 33.998 mm |
| `pota_def` | new | unset | ticket 79 `pota_wp`: P05 refuses 62 of 15,460 = 0.401 %, P01 `base_skip`, no crash |
| `pota_off` | new | `off` | ticket 79 `pota_off`: no `[SFS-79]` line, nothing refused |

Use the **ticket's** adjacent-chord metric for patches (sum of chords between consecutive surviving dots in trace order), not ticket 79's `score79.py:patches_of` (3 mm spatial linkage, max-pairwise span) — that was the mislabelled column the lead corrected in ticket 79. Score into `C:/PR/artifacts/t80/gate80.tsv` with columns `group metric piece cell value bar verdict note`.

Bars: every row above met; `def_3x`'s Sherd 7 ≤ 3 dots and ≤ 3.0 mm; Pot A per-piece refusal ≤ 1 % except P01 which must be `base_skip`; 1× J1 ≤ 8 dots; no on-lip Bl0 dot flipped on the eight Pot A pieces; every cell's pieces present (36/36, 36/36, 32/32 files).

A.4 Every `sbatch` polled with `scripts/remote/job_status.sh`; the final `sacct` State/ExitCode of every job recorded in this ticket. A run directory under `/data/gpfs/projects/punim2657/SfSpp/runs/YYYYMMDD-HHMM_<git7>_t80-default-on/` with `run.json` and one `runs/index.tsv` row (verdict and human_note blank).

## Part B — the eye gate: old and new edgeline, side by side, on all nine pieces

Reuse the precedent rather than inventing a new look: `C:/PR/artifacts/visual-qa/edgeline_juglet/build_overlay.py` drew each sherd's `Breakline_0` as a 1.1 mm tube on its own mesh at millimetre scale and staged it through `visual-qa/viewer/pairs/edgeline_juglet_gallery.json`. Do the same, with **two tubes per piece**:

- **old** edgeline (switch `off`, ticket 79's `off_*` cells) in a cool neutral — grey-blue `[90, 110, 140]`;
- **new** edgeline (default on, this ticket's `def_*` cells) in red-orange `[230, 70, 20]`;
- same tube radius on both (0.55 mm as before, so 1.1 mm diameter), same mesh tint, mesh in the **piece frame**, millimetres (`×3` on the 3× tree bundle, `×1` on the 1× set).

Three looks, each its own desc + manifest (geometry stays under `C:/PR/artifacts/`, never copied into the repo):

1. `edgeline_t80_3x` — all **nine** 3× pieces in a 3×3 display grid (cells ~340 mm apart, as the precedent did), piece frame.
2. `edgeline_t80_1x` — all **nine** 1× pieces, same layout.
3. `edgeline_t80_truepose` — pieces **5, 6, 7, 8** carrying the key's own pose (`Dataset/Juglet/Ground Truth/Juglet_Piece_N_T.txt`, tree units ×3) so the conservator can see whether the new line meets across the 6–7 seam where the old one did not.

Write the builder as `C:/PR/artifacts/visual-qa/t80/build_overlay_all.py`, the descs as `C:/PR/visual-qa/viewer/pairs/edgeline_t80_{3x,1x,truepose}.json`, the manifests as `C:/PR/visual-qa/preview/manifest_edgeline_t80_*.json`, and run `python viewer/stage_pair.py viewer/pairs/<name>.json` for each. Follow the desc rules in `C:/PR/visual-qa/AGENTS.md`: `pair` = the question to look for (≤ 70 characters), `method` = what it is, `capture` = the trace; put tints, tube colours, scale and frame into the notes fields. **Do not leave a viewer process running** — the lead starts it for the conservator.

Also render the same three looks offscreen to `C:/PR/artifacts/t80/render80_overlay.png` (a 3-panel figure is enough: 3× grid, 1× grid, true pose) so the staging can be checked without a browser, and say in the ticket what you see in it.

Bars: the three PLYs exist with sane bounds (mm, no NaN); `stage_pair.py` prints no error for any desc; the three descs and three manifests are in the repo tree; every one of the 27 piece-arms has both tubes (nine pieces × three looks) and the dot counts per tube match the cell files it came from.

## Part C — stop at the eye

End with `End state: waiting: conservator's eye on edgeline_t80_3x / _1x / _truepose`. Do not start ticket 81, do not run the assembler, do not merge anything. The lead will start the viewer and hand the conservator the link; the conservator's verdict goes into this ticket's Comments and ticket 81 is dispatched only after it.

## Deliverables

- `C:/PR/artifacts/t80/gate80.tsv` (Part A rows), `C:/PR/artifacts/t80/render80_overlay.png`, `C:/PR/artifacts/t80/overlay_t80.json` (per-piece: dots per arm, median dot-to-mesh gap, longest drawn jump).
- The three visual-qa descs + manifests, staged.
- The source diff and binary md5, the job table with `sacct` State/ExitCode, and the run directory.

## Part D — readings (pick one, verbatim, on a `Reading:` line)

- `default-on-holds-and-overlay-staged` — every Part A bar met **and** the three looks staged.
- `default-on-moves-a-control` — the default does not reproduce ticket 79's wall-pair arm, or a control bar fails.
- `overlay-not-stageable` — Part A passed but a look could not be built or staged (say which and why).

## Out of scope

- Any assembler work (ticket 81), any change to `class/`, `hpc/`, `stage66/run_cell66.sh`, `Dataset/`, the px3 tree.
- Re-tuning the rule (band, `ed`, guards, `maxdrop`) or ticket 73/76's switches.
- The trace-side guard, and the `SfSpp_preprocessing` `original_nurbs_preprocessing/` copy (a stale duplicate; the compiled file is the repository-root one, `CMakeLists.txt:37`).
- Committing, pushing, or opening/removing worktrees.
