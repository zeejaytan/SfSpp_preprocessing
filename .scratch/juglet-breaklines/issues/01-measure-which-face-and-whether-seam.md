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

**Status:** resolved

**Needs-eye:** none — this ticket produces a table, not a placement
claim. The render requirement lands in ticket 02 with the first real
change.

## Result (2026-09-26): two independent causes, and the bigger one is NOT the face

Scripts and output (assembly repo, where the data already lives):
`../structure-from-sherds-pp/artifacts/juglet_run1/`
`breakline_face_audit.py|.txt`, `breakline_face_crosstab.py|.txt`,
`sameface_gt_geometry.py|.txt`. Inputs: the 18 Juglet `Surface_*.xyz`
and 9 `Axis.xyz` from the bundle on Spartan (fetched to
`artifacts/juglet_surfaces/`, `artifacts/juglet_axes/`).

### 1. The extractor traces ONE wall face per sherd, and which one is arbitrary

| sherd | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| face traced | inner | outer | outer | outer | inner | outer | outer | outer | inner |

Confidence is high (97–100% of points on that face). Over 1800 breakline
points: 43.8% outer, 21.5% inner, **34.7% ambiguous** (within 0.5 mm of
both faces). Ambiguity is concentrated in sherd 8 (96%) and 9 (61%).

### 2. Ten of the eighteen true mates are on opposite faces

Cross-tab against the conservator answer key: **10/18 true mates are
inner-vs-outer**, so the assembler comparing the two traces can never see
them. Critically the assignment is **arbitrary, not informative**: 10/18
non-mate pairs are same-face too, so "same face" predicts nothing about
whether a pair is real.

### 3. …and fixing the face would NOT be enough

Of the 8 same-face true mates, only **1/8** has its traces within 2 mm at
ground truth:

| pair | nearest trace | normal dot | gate inliers @2mm/0.85 |
|---|---|---|---|
| 6-7 | 0.92 mm | 0.99 (6°) | **55** |
| 1-9 | 5.04 mm | 0.95 (18°) | 0 |
| 4-6 | 9.98 mm | 0.78 (39°) | 0 |
| 3-7 | 14.84 mm | 0.92 (23°) | 0 |
| 5-9 | 19.75 mm | 0.99 (8°) | 0 |
| 1-5 | 22.22 mm | 1.00 (3°) | 0 |
| 7-8 | 25.88 mm | 0.99 (7°) | 0 |
| 6-8 | 30.40 mm | 0.65 (49°) | 0 |

**This corrects the working theory.** The normals are *not* the problem:
on same-face pairs they agree at 0.92–1.00 (6–23°), which comfortably
passes the gate's 0.85. The opposed normals seen on 2-9 (70.9°) are the
*signature of the opposite-face assignment*, not a separate defect. The
dominant failure is **coverage**: the extracted segment does not span the
seam, sitting 5–30 mm from contact where truth is 0.02 mm.

So the ranking for ticket 02 is the reverse of what this ticket guessed:
**coverage first, both-faces second.**

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
