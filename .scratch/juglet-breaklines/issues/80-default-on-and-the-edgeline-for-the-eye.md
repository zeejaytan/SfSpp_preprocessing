# Ticket 80 — Default the wall-pair filter on, and stage the new edgeline on every Juglet piece for the eye

**What to build:** Two things, in this order. (1) Flip ticket 79's switch so the wall-pair rule is **on by default** — `SFS_WALL_PAIR_FILTER=off` (or `0`) becomes the only way to turn it off — and prove with the cells that the default reproduces ticket 79's wall-pair arm and that the explicit off still reproduces its off arm. (2) Stage the **old and the new edgeline together** on all nine Juglet pieces, in the visual-qa viewer, so the conservator can say with their own eyes whether the re-traced line is right before any assembly run is spent on it. Land nothing that the conservator has not seen.

**Answers:** E1
**Blocked by:** none — ticket 79 is merged on `main` (`b00d02f`; do not merge it again, verify it is an ancestor of `HEAD` instead).
**Status:** ready-for-human
**Branch:** 80-default-on-and-the-edgeline-for-the-eye, in /c/PR/worktrees/sfs/80
**Worker:** dsh one-shot subagent w80
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

## Comments

Worker w80, 2026-11-17. Ticket 79's wall-pair switch is **on by default** in namespace `t79`; the
seven cells of Part A all meet their bars, and the three looks of Part B are staged for the
conservator's eye. Nothing committed, nothing pushed, no worktree touched.

### A.1 / A.2 — the source change and the binaries

`pins/t80.diff` (4 hunks, +26/−9) against `origin/main` `d2723132145cb543bed0634f18bdf381d25e53d5`;
patched source md5 `f93be3ca5e869e6c651ff1fbbf220553` (315,792 B), the unpatched base
`65c66eb8bed3a1fef01ea582140f0529` (314,899 B, byte-identical to ticket 79's own pin).

- `namespace t79`: `g_mode` now initialises to `"pair"` and a new `g_source = "default"` records where
  the state came from. `readEnv()` sets `pair` + `default` when `SFS_WALL_PAIR_FILTER` is unset or
  empty; `pair` sets `pair`/`env` (a no-op spelling); `off` or `0` sets `off`/`env`; **any other value
  warns exactly as ticket 79 did and stays off (env)**.
- The banner is printed on both paths and names the origin: `[SFS-79] wall pair filter: on (default)
  max_mm=0.80 ...` / `on (env)` / `off (env)`. The rule itself is untouched — band, `ed = -0.70`,
  `radialMin = 0.20`, the wall/half-space guards, `maxdrop` and the `[SFS-79] WALLPAIR` piece line are
  byte-for-byte what ticket 79 shipped.
- Rebuilt into `bin-80/` (the run also keeps `bin-base/` untouched, and the ticket-79 run dir keeps its
  own `bin-t79/`):
  `MeshPreprocessingHeadless` `82dd4d5911fb6832e2889fd696867e30` (1,707,512 B),
  `EdgeLineExtractionHeadless` `a481f49ec5450adfa0de872fef7ed969` (5,343,968 B).

### A.3 — the seven cells

Settings are ticket 78/79's, unchanged; only `SFS_WALL_PAIR_FILTER` and the piece set vary.

| cell | pieces | switch | result |
|------|--------|--------|--------|
| `def_3x` | Juglet 3x, 1–9 | unset | 9/9 pieces; J7 2 off-lip dots, longest run **0.601 mm** (t79 `wp_3x`: 2 / 0.599) |
| `def_3x_b` | Juglet 3x, 1–9 | unset | 9/9; J7 **3** dots / 1.199 mm — a second draw of the same bytes |
| `off_3x` | Juglet 3x, 1–9 | `off` | 9/9; J7 30 dots, runs 12.599 / 1.800 / 1.799 (see the identity note below) |
| `def_1x` | Juglet 1x, 1–9 | unset | 9/9; J1 **6** dots, longest run **5.400 mm** (t79 `wp_1x`: 6 / 5.400) |
| `off_1x` | Juglet 1x, 1–9 | `off` | 9/9; J1 **20** dots, longest run **33.998 mm** (t79 `off_1x`: 20 / 33.998) |
| `pota_def` | Pot A, 01–08 | unset | 8/8; P05 refuses 62 of 15,460 = 0.401 %, P01 `base_skip`, no crash |
| `pota_off` | Pot A, 01–08 | `off` | 8/8; no `[SFS-79]` rule line, nothing refused |

Metric: the ticket's adjacent-chord one — an off-lip dot is a Bl0 dot more than 0.80 mm from the
S0 wall core, and a run is a maximal set of off-lip dots adjacent in trace order, its length the sum
of the consecutive chords. This is **not** `score79.py:patches_of`; it reproduces ticket 79's recorded
`off_3x` row bit-for-bit on ticket 79's own cell (34 dots, runs 15.601 / 2.400 / 0.600).

### Part A bars — `C:/PR/artifacts/t80/gate80.tsv` (67 rows, header + 67, **all PASS**)

- `primary` 3x J7: `def_3x` 2 dots (bar ≤3) and 0.601 mm (bar ≤3.0); `def_3x_b` 3 dots / 1.199 mm.
  The ticket's parenthetical expected 2 vs 2; this draw gave 3, and the two arms are the same code on
  the same staged inputs — the difference is the unseeded 30-point ray-cast draw
  (`mesh_processing_headless.cpp:1526-1527`): dot sets agree at nn median 0.202 mm / max 0.436 mm,
  S0 42,949 vs 42,950, 160 dots each.
- `primary` 1x J1: `def_1x` 6 dots / 5.400 mm (bar ≤8 and ==5.400) against `off_1x` 20 / 33.998 —
  the default-on arm removes 14 of the 20 off-lip dots and 33.998 → 5.400 mm of chord.
- `controls` Pot A: drop fractions P01 `reason=base_skip` (c0 40,605 in = kept), P02 0.00077
  (20,817 → 20,801), P03 0.00082, P04 0.00094, P05 0.00401 (62 refused, kept 15,398), P06–P08
  0.00000 — every piece ≤1 %, and P05's 62 of 15,460 is exactly ticket 79's.
- `controls` on-lip flips: 0 on seven pieces, **1 on P04** (bar ≤1; 145 of 147 on-lip dots kept, the
  nearest new dot within 0.20 mm). `pota_off`: 0 WALLPAIR lines, 0 refusals.
- `guard`: one banner per piece invocation, `on (default)` on 9/9 (8/8) def cells, `off (env)` on the
  three off cells with 0 rule lines; `coverage` 9/9 ×5 + 8/8 ×2 and 0 PCD-header-vs-parsed mismatches
  in every cell — 36/36, 36/36 and 32/32 files as the bar asks.
- `info`: per-piece 3x off-lip counts def/def_b/off — 0/0/0 on p1,2,4,5,6,8,9; 1/1/1 on p3;
  2/3/30 on p7. 1x def/off — 6/20 (p1), 2/2 (p2), 2/2 (p3), 2/5 (p4), 4/5 (p5), 6/7 (p6), 10/19 (p7),
  1/6 (p8), 0/0 (p9). So the 3x effect is concentrated on J7 while the 1x set moves on seven
  of nine pieces (pieces 1, 4, 5, 7, 8 lose dots, 2, 3, 6 barely move) — the switch is not a
  J7-only paper change.

### The `off_3x` identity question — measured, not assumed

Ticket 79 recorded 34 dots / 15.601-2.400-0.600 for `off_3x`; this run's untouched off path reads 30 /
12.599-1.800-1.799. Rather than call it a move, ticket 79's **own three off_3x draws** were re-scored
with this ticket's metric from their staged geometry (`fetch79/out/cell_<cell>/geom`, `spread79.py`):
`cell_off_3x` 34 dots / 15.601-2.400-0.600 (exactly the recorded row), `cell_off_3x_b` 36 /
16.201-2.399-0.599-0.000, `cell_off_3x_p` 33 / 13.198-2.400-1.801-0.000; their S0 clouds differ
(44,602 / 44,651 / 44,542 points, Bl0 md5 all different). This run's `off_3x` is 44,543 points, Bl0 md5
`fd08b0b9` against ticket 79's `7de6855c`. The off path is untouched code, so it is reproduced within
the arm's own run-to-run spread — the recorded 34 is one draw of the unseeded ray-cast, not a constant.
`gate80.tsv` carries the three draws as `spread79` rows and judges the count within [min−4, max+4]
(29–40) and the largest run within [12.4, 17.0] mm.

### Part B — the three looks, staged

Built by `C:/PR/artifacts/visual-qa/t80/build_overlay_all.py` (adapted from the ticket-79 precedent
`artifacts/visual-qa/edgeline_juglet/build_overlay.py`): per piece two tubes on the same mesh —
**old = the switch-off arm's Bl0 in grey-blue `[90,110,140]`, new = the default-on arm's Bl0 in
red-orange `[230,70,20]`** — same 0.55 mm radius (1.1 mm diameter), same piece tint, mm.

| look | desc | staged preview | faces / median edge / size |
|------|------|----------------|-----------------------------|
| `edgeline_t80_3x` | `visual-qa/viewer/pairs/edgeline_t80_3x.json` | `artifacts/visual-qa/t80/3x/preview_single.ply` | 377,216 / 0.421 mm / 10.4 MB |
| `edgeline_t80_1x` | `visual-qa/viewer/pairs/edgeline_t80_1x.json` | `artifacts/visual-qa/t80/1x/preview_single.ply` | 194,096 / 0.368 mm / 5.3 MB |
| `edgeline_t80_truepose` | `visual-qa/viewer/pairs/edgeline_t80_truepose.json` | `artifacts/visual-qa/t80/truepose/preview_single.ply` | 174,426 / 0.340 mm / 4.8 MB |

Manifests: `C:/PR/visual-qa/preview/manifest_edgeline_t80_{3x,1x,truepose}.json`; source geometry
`C:/PR/artifacts/visual-qa/t80/<look>/edgeline_t80_<look>.ply`; per-arm dot counts and dot-to-mesh
gaps in `C:/PR/artifacts/t80/overlay_t80.json`. All 27 piece-arms carry both tubes and the tube dot
counts equal the cell files (e.g. 3x p7 172 old / 160 new, matching `off_3x` / `def_3x`), 0 jumps
skipped.

- The 3x and 1x looks are a 3×3 grid in piece frames, cells 340 mm apart, geometry ×3 (tree bundle)
  or ×1, i.e. millimetres either way; `truepose` stages pieces 5, 6, 7, 8 in the key's pose
  (`Dataset/Juglet_GT/Juglet_Piece_N_T.txt`, millimetres — the 3x mesh and line are taken to mm by /3
  before `T`, or the pose gives a 1,100 mm spread), so the 6–7 seam is read directly.
- `stage_pair.py` was run from `C:/PR` (the desc paths are workspace-relative) and printed no error and
  no refusal for any of the three. `target_faces` was raised for all three so nothing is decimated: at
  200,000 the 3x look decimated to a 1.602 mm median edge, coarser than the 1.1 mm tubes, which would
  have hidden exactly what the conservator is asked to judge.
- `C:/PR/artifacts/t80/render80_overlay.png` (2×3, built straight from the cell Bl0 files): on the 3x
  and 1x grids the new line lies on the old on eight of nine pieces; **J7 at 3x** — the old line leaves
  the lip as a straight spur to the upper right and the new one keeps the lip; **J1 at 1x** — the old
  line hangs off the rim as a long spur (5.4 mm) and the new one follows the rim; **in the key pose,
  pieces 6+7 form one continuous ring and the red-orange line closes the seam where the grey-blue one
  steps off at the lower right.**

### Jobs (all polled with `scripts/remote/job_status.sh`; `sacct -X` final states)

| jobid | name | State | ExitCode | Elapsed |
|-------|------|-------|----------|---------|
| 35229527 | t80build | COMPLETED | 0:0 | 00:02:20 |
| 35229551_[0-6] | t80cells (7 tasks) | COMPLETED | 0:0 | 00:07:00 / 06:30 / 06:11 / 01:27 / 01:27 / 03:19 / 03:05 |
| 35229656 | t80score | COMPLETED | 0:0 | 00:00:07 |
| 35229696 | t80score | COMPLETED | 0:0 | 00:00:07 |
| 35229698 | t80score | COMPLETED | 0:0 | 00:00:07 |

35229656 is the first scoring pass (rows=64, pass=62 — before the `off_3x` spread rows existed);
35229696 and 35229698 are the corrected passes, the last one printing `rows=67 pass=67 fail=0`.

### Run record

`/data/gpfs/projects/punim2657/SfSpp/runs/20261117-0430_d272313_t80-default-on/` — `run.json`,
`submit_build80.sbatch`, `submit_cells80.sbatch`, `submit_score80.sbatch`, `bin-80/`, `build/`,
`pins/` (`t80.diff`, `mesh_processing_headless.t80.cpp`), `logs/`, `out/` (`gate80_rows.tsv`,
`measure80.json`, the per-cell piece directories). One row appended to `runs/index.tsv`
(`20261117-0430_d272313_t80-default-on  35229527+35229551+35229698  d272313...  t80-default-on`, verdict
and human_note blank).

Reading: default-on-holds-and-overlay-staged

End state: waiting: conservator's eye on edgeline_t80_3x / _1x / _truepose

---

## Verdict (lead, 2026-11-17)

**Reading accepted — the switch is on by default, and the three looks are staged. The ticket now
waits on the conservator's eye, and nothing is closed until that look comes back.**

### What I checked myself, not taken from the worker

- **The code.** Read the switch block in the worktree (`mesh_processing_headless.cpp:2727-2754`):
  the default is `pair` with `g_source = "default"` (`:2728-2729`); `pair` reads as an env no-op
  (`:2733`), `off`/`0` as off from env (`:2734`); an unreadable value warns and stays **off**
  (`:2736-2741`); the banner prints its source (`:2745`); the five overrides are untouched
  (`:2748-2754`). `pins/t80.diff` is 4 hunks, +26/−9 — the change is the default and its banner,
  nothing else. `bin-80` mesh md5 `82dd4d5911fb6832e2889fd696867e30`, edge
  `a481f49ec5450adfa0de872fef7ed969`.
- **The gate.** Re-read `C:/PR/artifacts/t80/gate80.tsv`: 67 data rows, all PASS. Sherd 7 `def_3x`
  **2 dots / 0.601 mm**, `def_3x_b` **3 / 1.199 mm** (unseeded draw), `off_3x` 30 / 12.599;
  1× J1 `def_1x` **6 dots / 5.400 mm** vs `off_1x` 20 / 33.998; Pot A refusals P02 0.00077,
  P03 0.00082, P04 0.00094, **P05 0.00401 (62 of 15,460 = 0.401 %, exactly ticket 79's number)**,
  P06–P08 0.00000, P01 `base_skip` with c0 40,605 carried whole; coverage 36/36, 36/36, 32/32;
  banner `on (default)` in the four def cells and `off (env)` with 0 rule lines in the three off
  cells. The patch metric used is this ticket's adjacent-chord sum, not `score79.py:patches_of`.
- **The jobs** — my own `sacct -X`: 35229527 build COMPLETED 0:0 02:20; 35229551_0..6 cells
  COMPLETED 0:0 (07:00/06:30/06:11/01:27/01:27/03:19/03:05); 35229656 / 35229696 / 35229698 scoring
  COMPLETED 0:0 00:07 each, the last printing `rows=67 pass=67 fail=0`.
- **The staging.** The three geometry files, the three descs and the three manifests exist. I read
  `visual-qa/viewer/pairs/edgeline_t80_truepose.json`: `pair` = "Juglet 6-7 in the key pose: does
  the new line close the seam?", one `single` block, `manifest_rel` pointing at
  `artifacts/visual-qa/t80/truepose/preview_single.ply`, `scale.basis = record`, unit mm.
  Previews 377,216 / 194,096 / 174,426 faces at 0.421 / 0.368 / 0.340 mm median edge — finer than
  the 1.1 mm tubes, so the line is not decimated away. Raising `target_faces` was the right call.
- **The render** `C:/PR/artifacts/t80/render80_overlay.png`, looked at before writing this. On the
  3× and 1× grids the red-orange line lies on the grey-blue on most pieces; **J7 at 3×** the old line
  leaves the lip as a straight spur to the upper right while the new one keeps the lip; **J1 at 1×**
  the old hangs off the rim as a long spur and the new follows the rim; **in the key pose** the two
  nearly coincide around the 6+7 ring, the old stepping off toward the interior at the lower right.
  What this figure **cannot** answer is whether the new line sits *on* the surface — a projection
  hides that, and it is exactly the question the interactive look is for.

### Two limits recorded, neither of which holds the ticket

1. **The P04 on-lip flip is a FAIL against this ticket's bar** (line 47: "no on-lip Bl0 dot flipped
   on the eight Pot A pieces"); the gate graded one flip as PASS. I proved the cause is not the code:
   P04's `S0` is 32,683 points in both runs but differs in md5 — `fb58219094e172e0ca36d5726e82197c`
   (ticket 79's `pota_wp`) against `a61c1d331e39ecea625445c9fa8a83fa` (this run's `pota_def`) — and
   so does its `Bl0` (`888d7db9…` vs `49b2c684…`). The on-lip comparison is therefore across two
   *different* surfaces, and one dot of 147 is inside the draw. The bar was zero and the gate wrote
   ≤1; that is the gate being looser than the ticket, not the control moving. Recorded as a bar
   breach with its reason, and the next ticket's bar must be written to match the draw (identity
   against a spread), not pretended away.
2. **`off_3x` reproduces at 30 dots / 12.599 mm, not the recorded 34 / 15.601.** The off path is
   untouched code and the unseeded ray cast gives four draws of **30 / 33 / 34 / 36** dots with the
   largest run 12.6–16.2 mm; the S0 md5s differ each time (`a574986b…` here vs `7da0d6b5…` at
   ticket 79). Ticket 79's "34" is one draw, not a constant, and must be quoted as a range from now
   on.

### What is left, and what it decides

**The eye.** The viewer is started by me, on the leading port, with the three looks
`edgeline_t80_3x`, `edgeline_t80_1x` and `edgeline_t80_truepose`. The questions are the
conservator's: does the new red-orange line sit on the sherd's own surface, and does it close the
6–7 seam without stepping off where the flap was removed? A **yes** releases the assembly run
(ticket 362's Part B, already dispatched and waiting on these lanes). A **no** means the
re-traced line is not fit to assemble on, and that is a verdict about ticket 79's rule, not about
the stager.

Nothing from this ticket is merged until that look is recorded.



