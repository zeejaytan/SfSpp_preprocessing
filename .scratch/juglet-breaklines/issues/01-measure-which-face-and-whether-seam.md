# 01: Measure which wall face each breakline segment came from

**What to build:** a per-segment, per-sherd measurement of two things,
for all 9 Juglet sherds, in millimetres:

1. **Which wall face** did the extracted breakline segment come from —
   inner surface, outer surface, or both? The Juglet wall is ~1.8 mm, and
   the gate failure is consistent with the extractor tracing the inner
   face on one sherd and the outer face on its neighbour (1.7 mm apart,
   normals 67–129° opposed).
2. **Does the segment span the seam?** For each true mate, distance from
   the GT contact point to the nearest extracted point, against the
   0.02 mm truth. Segments running 0.2–30 mm from the contact point are
   missing the seam.

**Answers:** E1

**Blocked by:** none

**Status:** ready-for-agent

**Needs-eye:** none — this ticket produces a table, not a placement
claim. The render requirement lands in ticket 02 with the first real
change.

## Why this first

Two candidate causes are currently undistinguished, and they need
different fixes:

- **Opposite faces** → segmentation assigns a fracture rim to one
  surface cluster instead of both (extractor change: emit both faces).
- **Missing seam** → the extracted fragment excludes the contact region
  (extractor change: coverage/sampling).

Changing both at once and seeing the gate number move would tell us
nothing about which mattered. Measure first.

## How

The Juglet bundle is on Spartan at
`/data/gpfs/projects/punim2657/sfs_preprocessing/Juglet_Dataset_20260916/SfS_pp/`.
Meshes and GT are in the assembly repo's
`artifacts/juglet_input/` (meshes, `Ground Truth/`), and GT contact
points can be derived with the same approach as `.scratch/derive_gt.py`
in the assembly repo.

For each sherd the extractor produces `Surfaces/Juglet_Piece_N_Surface_0.xyz`
(inner) and `_Surface_1.xyz` (outer). So:

1. Load the mesh, the two surface point sets, and the extracted
   breakline segments for sherd N.
2. Assign each breakline point to inner or outer by nearest-neighbour
   against the two surface sets — and record **whether both are close
   enough to be ambiguous** (a point that is ~equidistant from both is
   exactly the wall-thickness case, and its assignment is arbitrary).
3. Report as a table: sherd, segment, points, face assignment
   (inner/outer/ambiguous), nearest GT contact point for each true mate,
   distance to it.
4. Write it to `artifacts/breakline_face_audit.md` and commit the script
   (not the output data).

## Acceptance

- A table covering all 9 sherds and all their segments.
- An explicit count of **ambiguous** (equidistant) breakline points. If
  that count is high, the inner/outer assignment is not recoverable from
  the current surfaces and the extractor must change structurally rather
  than by tuning — that is the single most valuable number here.
- No extraction change in this ticket. It measures.

## Guardrail

Nothing here alters the pipeline, so there is no Pot_A regression risk in
this ticket. That exemption ends at ticket 02.
