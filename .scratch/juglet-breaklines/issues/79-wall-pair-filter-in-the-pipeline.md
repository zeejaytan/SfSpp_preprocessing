# Ticket 79 — Wire the wall-pair filter into the pipeline and re-trace the boundary

**What to build:** Put ticket 78's **R1** rule — drop a point only where it is outside the wall band **and** fails the −n ray-pair test — behind one default-off switch in `mesh_processing_headless.cpp`, apply it to the clustered cloud **before** the surface fit and to the refinement add-backs, and then **re-trace** the breakline on the filtered cloud so the result is a pipeline result, not an offline point count. Success is Sherd 7's off-lip flap gone in a real cell, with the controls untouched.

**Answers:** E1
**Blocked by:** none — `structure-from-sherds-pp` ticket 361 landed 2026-11-17 (`f5b924f`: the GMnr lanes close the 6-7 fit; the reading is join-level and seating is unchanged). Originally — **ordering set by the conservator (2026-11-17): the cross-lane assembler check lands before any C++ change here.** Nothing in this ticket may be started before 361 reports.
**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-17)
**Branch:** 79-wall-pair-filter-in-the-pipeline, in /c/PR/worktrees/sfs/79
**Worker:** dsh one-shot subagent w79
**Budget:** medium (one switch with five overrides in one file, one extractor re-run, nine 3× cells plus 1× and Pot A controls, one gate table and one render)
**Hand-over:** DeepSeek: read this ticket and ticket 78 in full, plus the R1 numbers in `C:/PR/artifacts/t78/stage0_78.tsv` and the correction section of ticket 78. Build the switch, re-trace, run the cells, score `C:/PR/artifacts/t79/gate79.tsv`, render `render79_before_after.png`, and append your Comments section with one Reading line.

---

## Why this ticket exists

Ticket 78's offline replay showed the localised rule is **safe**: R1 (wall band **and** ray-pair, `ed = -0.70`) drops 0.04 % of Pot A Piece 05's points (12 of 31,786), 0.02 % of P02, 3.54 % of 1× Juglet Piece 1, and leaves 3 off-lip dots on 3× Sherd 7 spanning at most **1.79 mm** — against a bar of ≤ 3 dots and ≤ 3 mm, and inside the 12.0 mm stop limit. The conservator found the 14.54 mm originally reported was a **measurement defect** (the contour summed `np.diff` across deleted dots: 0.601 + 1.791 + **12.146** mm); ticket 78 now records the correction.

What that replay did **not** do is re-trace the boundary. It deleted S0 points and counted the surviving dots; a pipeline result needs the extractor to run again on the trimmed cloud, because the boundary is fitted from the points and a gap is not the same thing as a re-traced line. R1 has never been in the pipeline. That is this ticket.

## The rule, exactly (do not re-tune)

Per piece, with `units = SFS_TREE_UNITS_PER_MM` (3.0 on the 3× bundle, 1.0 on 1×):

1. **Axis guard** — `axisFit = frac(|n·(D×radial)| < 0.3) ≥ 0.80` **and** `|median(nd)| ≥ 0.40`, sign from `median(nd)`. If either fails, the filter is inert for that piece: `reason=bad_axis` (or `base_skip` for the piece named below), nothing dropped.
2. **Wall band** — a point is wall-oriented iff `sgn·(n·radial) > 0.20`; it is **in band** iff it is wall-oriented or within `W = 0.80 mm × units` of a wall-oriented point.
3. **Ray-pair test** — ray along `−n`, `t ∈ [1.5, 10]` mm × units, perpendicular tolerance `0.45 mm × units`, exit when the ray meets an inlier dot within tolerance; a point is **paired** iff it exits at `ed = -0.70` (the default) or better.
4. **Drop** iff **out of band AND unpaired.** Nothing else changes: no growth, merges, gates or thresholds move.

Known and expected, from ticket 78 — treat as confirmations, not surprises: Pot A Piece 01 is skipped by the guard (`|medRad| 0.3123`, `reason=base_skip`); 1× Juglet Pieces 2, 6 and 9 are likewise inert (`|medRad|` 0.3588, 0.0470, 0.2404); a wrong axis only disables the rule, it never drops points.

## Part A — precondition (offline, no job, no code change)

Reproduce ticket 78's R1 numbers from the same dumps with the corrected contour metric, and record them in the ticket before building: 3× Sherd 7 at `ed = -0.70` → **3 dots, largest patch ≤ 1.79 mm**; Pot A P05 12 dropped of 31,786; P02 10 of 42,398; 1× J1 461–469 of 13,834 (3.33–3.39 %). If they do not reproduce, **stop**: `blocked: precondition` — the gate would otherwise be measuring a different bundle.

## Part B — the switch (one file)

`mesh_processing_headless.cpp` only. One new switch, default **off**:

- `SFS_WALL_PAIR_FILTER` = `pair` (R1) | off (unset or `0`).
- Overrides: `SFS_WALL_PAIR_MM` (0.80), `SFS_WALL_PAIR_ED` (-0.70), `SFS_WALL_PAIR_RADIAL_MIN` (0.20), `SFS_WALL_PAIR_AXISFIT_MIN` (0.80), `SFS_WALL_PAIR_MEDRAD_MIN` (0.40), `SFS_WALL_PAIR_MAXDROP` (0.35 — if the rule would drop more than this fraction of the piece's points it refuses and logs `reason=maxdrop`).
- Applied in **two places**: to the clustered cloud immediately **before** `fitSplineSurfaceToCluster` (`:1462`; call sites `:2695`, `:2925-2926`) and to the refinement **add-backs** before they are appended (the same place tickets 73/76 gate, around `:2422-2565`; read their pattern and follow it rather than inventing a second one).
- One log line per piece, exactly this shape:
  `[SFS-79] WALLPAIR piece=<p> mode=<m> active=<0|1> axisFit=<f> medRad=<f> c0_in=<n> c0_kept=<n> add_refused=<n> reason=<ok|base_skip|bad_axis|maxdrop>`
- Follow the existing `getenv` convention in the file (see `:2290-2291`) and warn on a bad value instead of silently defaulting.
- **Identity is a bar, not a claim to make:** with the switch unset, the binary's outputs on `off_3x` must be byte-identical to the current build's (md5 of the dumped dots and of the S0/S1 clouds). Prove it by running both.

## Part C — re-trace, then the cells

1. **Provenance first.** Find the exact command that produced the `Breaklines/` inputs the cells consume (the `EdgelineExtractionHeadless` target in `build.sh:264`; the drivers under `scripts/`). Record it in the ticket with its arguments and the commit it came from. Do not guess a command and do not invent a new extraction path — if the provenance cannot be established, stop as `blocked: provenance`.
2. **Re-trace.** Run that extractor on the filtered cloud for the 3× bundle and the 1× bundle, with the filter on, producing the Bl0 lanes this ticket will compare.
3. **Cells**, `stage66/run_cell66.sh`, exactly the ticket-78 settings (`WORNESS=0.7`; 3×: `SFS_NORMAL_MODE=radius`, `SFS_NORMAL_RADIUS_MM=1.0`, `SFS_MERGE_CLUSTER_DOT=0.887`, `SFS_GROW_BASE_MM=1.5`, `SFS_GROW_BASE_THETA_DEG=25`, `SFS_TREE_UNITS_PER_MM=3.0`; 1×: `SFS_TREE_UNITS_PER_MM=1.0`; no `SFS_REFINE_*`): `off_3x`, `wp_3x` (filter `pair`), `off_1x`, `wp_1x`, `pota_off`, `pota_wp`. `off_3x`/`off_1x`/`pota_off` are the identity anchor and must reproduce the currently recorded numbers.
4. Score into `C:/PR/artifacts/t79/gate79.tsv`, columns `group metric piece off wp reference verdict`, groups: `primary` (3× Sherd 7 off-lip dots and largest patch), `controls` (Pot A P02–P08 share dropped, 1× J1 share), `coverage` (S0/S1/Bl0/Bl1 present on 9/9 and 8/8), `identity` (switch-off md5 equality), `guard` (`base_skip` on P01, inert on 1× J2/J6/J9).

## Bars

- 3× Sherd 7 (filter on, `ed = -0.70`): **≤ 3 off-lip dots and largest contiguous off-lip patch ≤ 3.0 mm** — measured with the corrected metric (chords **only between adjacent surviving dots in the original trace order**, never across a deleted one). Report the patch length, not the total contour.
- Controls: Pot A P02–P08 each drop **≤ 1 %** of S0 and flip **no more than 1** on-lip Bl0 dot; 1× J1 **≤ 4 %** (R1 measured 3.54 %). Piece 01 skipped, `reason=base_skip`.
- Identity: switch-off outputs byte-identical to the current build.
- Coverage: S0/S1/Bl0/Bl1 on 9/9 3× pieces, 9/9 1× pieces, 8/8 Pot A pieces; no crash.
- Off-lip dots on the other eight 3× sherds must not increase (ticket 78's bundle had them at 0; a filtering rule that resurrects them is a regression even if Sherd 7 improves).

## Part D — render and readings

`C:/PR/artifacts/t79/render79_before_after.png` (≥1800×1200): rows `off_3x` / `wp_3x` over Sherds 5–8 in axis space, off-lip dots coloured green (≤ 0.8 mm off the inner wall) and red (> 0.8 mm), plus the Pot A P01/P02/P04 panels. Look at it and write one sentence before the Reading lines.

Exactly one Reading line, verbatim:

- `wall-pair-filter-cures-sherd-7-in-pipeline` — the bar holds in a real cell, controls inside theirs.
- `wall-pair-filter-offline-only` — the points are removed but the re-traced boundary still carries the flap.
- `wall-pair-filter-hurts-controls` — any control bar fails.
- `blocked: precondition` | `blocked: provenance` — Part A or Part C.1 failed.

## Out of scope

- The assembler, ticket 361, and anything in `structure-from-sherds-pp`.
- Tickets 73's and 76's switches, and the trace-side guard.
- Re-tuning `W`, `ed`, the guard thresholds, growth or merge; the 1× bundle's assembly.
- Editing `class/`, `hpc/`, `stage66/run_cell66.sh`, `Dataset/`, or the px3 tree.

## Acceptance

- [ ] Part A numbers reproduce, written into the ticket before the build.
- [ ] One switch, five overrides, one log line, applied before the fit and to the add-backs.
- [ ] Switch-off identity proved by md5, not asserted.
- [ ] Extractor provenance recorded, re-trace run, both cell sets run.
- [ ] `gate79.tsv` rows with verdicts matching their numbers; 3× Sherd 7 bar read with the corrected patch metric.
- [ ] Render looked at, eye sentence before the Reading.
- [ ] Every job's `sacct` `State`/`ExitCode` and run directory id recorded.
