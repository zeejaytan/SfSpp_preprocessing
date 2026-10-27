# 33: Can the normals the scan already carries — and a merge of the fragments — give sherds 2 and 9 a face?

**Status:** ready-for-agent
**Working in:** chat on Thinkbook16 (2026-10-27)
**Branch:** —
**Answers:** U19, E1
**Blocked by:** none
**Blocks:** none

## Why this ticket exists

Two leads, both pointing at the same two sherds, and the conservator asked for them together
(2026-10-27, "1, let's see if sherd 2, 9 can yield a valid surface with cluster merge").

**Lead 1 — the scan already carries good normals, and the pipeline throws them away.** Ticket 32 measured
the normals stored in the point cloud files against each piece's own mesh: **0.414–1.635°** on the Juglet,
**0.455–0.616°** on Pot A. Ticket 30 measured the normals the pipeline computes for itself against the same
meshes: **3.39–8.10°** on the Juglet. The growth admits a neighbour only within **3.4°**
(`mesh_processing_headless.cpp:3026` area, theta 3.4). Why they differ is visible in the code:
`getNormalsOnSurface` (`:604`) writes the sampled points to an XYZ file **positions only** (`:615`), reads
them back (`:622-630`), and re-estimates normals from scratch with CGAL PCA at
`nb_neighbors = std::max(5, std::min(20, (int)points.size() / 1000))` (`:634`, `:659-662`). At Juglet point
counts that is 5 neighbours — a patch about 1–2 mm across on a surface that folds over a few millimetres.

**Lead 2 — the fragments may be mergeable.** Piece 2 and piece 9 grow many small regions and no face:
ticket 28's replica gave 661 and 1562 regions with the largest 36 and 16 points, and ticket 32 forced the
pipeline's own floor down and got single regions of 32 and 21 points. But `mergePaper234` (`:3186`) is
the step that is supposed to join fragments of one surface, and it has **never been asked to merge
fragments**, because the floor normally kills them first. Its test needs **at least 3 boundary pairs**
hardcoded at `:3142`; all six thresholds already have env switches
(`SFS_PAPER_RHOD/RHON/RHOC/RHOINN/RHOINC`, `:4365-4369`).

The conservator's question is the one to answer: with the good normals restored **and** the merge allowed
to work on fragments, does sherd 2 (or 9) yield a surface that is a face rather than a corner patch?

## What to build

Two switches, both defaulting to today's behaviour:

1. `SFS_NORMAL_SOURCE=reestimate|input` (default `reestimate`). In `input` mode the normals of the
   incoming cloud are carried through the sampling step instead of discarded: for each sampled point,
   average the unit normals of the source points within one sampling radius and normalise; if none are in
   range, fall back to the nearest source point's normal. Points with no usable source normal are reported
   and counted, never silently filled. Print one line per call:
   `[NORMAL-33] call=N source=input npts=... carried=... nearest=... missing=... median_dev_to_pca_deg=...`.
   The curvature field still has to be computed as today — this switch changes normals only.
2. `SFS_MERGE_MIN_PAIRS=<int>` (default 3), replacing the literal at `:3142`, printed in the existing
   `[PAPER-234]` line.

Rules:
- With neither switch set, the pipeline must reproduce today's output exactly (the defaults proof below).
- A carried normal must be a **unit** vector whose sign agrees with the source cloud's, not flipped to a
  convenient hemisphere; MST orientation is not applied in `input` mode, and that is a decision to state
  in the log line, not to hide.

## Arms and cells

Pieces: Juglet 2 and 9 (the target), 3, 5, 7 (the ones that already surface, as controls) and
Pot_A 07 (the reference). Four arms:

| arm | normals | floor | merge |
|---|---|---|---|
| A | reestimate (today) | today | today |
| A2 | reestimate | today | today — repeat, to measure the piece's own spread |
| B | input | today | today |
| C | input | forced down so fragments survive (`SFS_SPACING_POLICY=piece SFS_COUNT_SCALE=auto SFS_FLOOR_CEILING` stepped until the reported floor is at most 2 % of the cloud) | today (min pairs 3) |
| D | input | as C | `SFS_MERGE_MIN_PAIRS=2` |

If a C or D cell still returns one region, say so plainly: the fragments did not meet the merge's own
criteria, and the pair counts that refused them are the evidence.

## The measurement that decides it

For every surface the pipeline writes, on the sherd's cloud and mesh:

- point count, extent (bbox diagonal), and **2 mm coverage** — the fraction of the cloud within 2 mm of the
  surface. A face is most of the sherd; piece 3's today is 92.6 % and pieces 2/9's forced-floor patches were
  28.4 % and 42.5 % (ticket 32).
- median folded angle of the surface's points to the nearest mesh vertex normal.
- the corrected pair statistic (nearest-point vector split along/across the Surface_0 normal, coincidence at
  1 micron) where two surfaces are written — the mean-normal dot test is retired (ticket 24).
- every `[NORMAL-33]`, `[PAPER-234]`, `[WINDOW-26]`, `[FLOOR-23]` and `[STATUS-23]` line for the cell.

## Acceptance criteria

1. Both switches exist, are documented in the run's `run.json`, and print their value per cell.
2. **Defaults proof**: with no switch set, every surface is byte-identical to the pre-change binary's, and
   the point set is identical after sorting — the same proof shape tickets 22, 23, 24, 26 and 30 used.
3. The carry is proven to be a carry: report the median angle between the carried normal and the pipeline's
   PCA normal at the same points, and the median angle of the carried normal to the mesh.
4. Every arm × piece cell reports: exit code, region count, region sizes, merge decisions with pair counts
   and which criterion refused a merge, surfaces written with the measurements above.
5. Pot A 07 in arm B and C keeps **8 of 8** two-surface pieces (whole pot, all eight pieces) and its pair
   statistics stay in the band 3.55–7.13 mm along / 0.24–0.27 mm across / coincidence 0.0000.
6. Corpus and staged inputs md5 identical before and after; `/opt/sfs-pristine` recorded ABSENT, never
   created.
7. Geometry outside the written surfaces deleted with a counted record written **before** the delete;
   surfaces, logs and tables kept for the lead.
8. Index rows appended with `verdict` and `human_note` EMPTY.
9. No verdict, no merge, no write to `intent/`, no change to any tracked file except
   `mesh_processing_headless.cpp` and `.scratch/juglet-breaklines/stage33/`.

## Limits

Four jobs maximum (a ticket's usual cap is three; the extra is for the defaults proof), compute nodes only,
never the laptop and never the login node. CRLF-check every script before submitting — two grids have
already died on `set: pipefail: invalid option name`. Report what you measured and what would have to be
true for it to mean something; the reading is the lead's.

## What this cannot settle

It cannot show that restoring the input normals is sufficient anywhere but on these six pieces, and it
cannot make a face out of a sherd that never had one on its mesh. If arm D still returns fragments, the
honest reading is that the merge's criteria are built for surfaces larger than these fragments, not that
the sherds are unprocessable — the next question would be a merge criterion that measures fragment
adjacency rather than surface normals, and that is a different ticket.
