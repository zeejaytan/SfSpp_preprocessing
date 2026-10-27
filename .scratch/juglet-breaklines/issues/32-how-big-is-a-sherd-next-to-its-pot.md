# 32: How big is a sherd next to its pot, and does the angle follow that ratio?

**Status:** ready-for-agent
**Answers:** U19
**Blocked by:** none
**Blocks:** none

## Why this ticket exists

Ticket 30 measured the angle the region growing has to work with, and showed the sherds carry
4-27x the local curvature the pot piece does. Two explanations survived: the points are sparser,
or the sherds are small relative to the vessel they came from. Ticket 30 and the reply after it
killed the first one by measurement — the Juglet at native density has point spacing of
0.211-0.258 mm against Pot A's 0.223 mm, and still carries 7-15 deg. The second explanation has
never been measured.

There is a catch to settling it. The radius the angle follows today is 0.78-5.13 mm, while the
Juglet's own vessel radius is 32.5 mm (65 mm vessel). So the quantity being measured today is
local folding, not the pot's shape. If the angle is to be tuned on "how big is the sherd next to
its pot", the radius has to be measured over a window big enough to see the vessel, and no
measurement we have varies the window in physical units.

## What to measure

**Part A — sizes, from geometry and ground truth.**

For each Juglet sherd (9) and each Pot A piece (8, the ones this project controls against):

- the sherd's own extent: the diagonal of its bounding box, in mm, from its cloud;
- the sherd's surface area, in mm2, from its mesh (sum of face areas);
- **the vessel's own extent**, in mm, computed from the ground truth:
  - Juglet: from `Dataset/Juglet_GT/Juglet_Piece_1..9_T.txt` plus the nine meshes, place every
    piece at its reference pose and take the extent of the union. Report the extent and the method.
    This should land near 65 mm — the number every seating tolerance in this project is quoted
    against — and if it does not, that is a finding, not an error to fix silently.
  - Pot A: the same procedure from `Ground Truth/Pot_A_simple_graph.txt` and the released
    transforms. **This number does not exist anywhere in this workspace or in the paper**
    (checked: no Pot A dimension in `C:/PR/papers/text/sfspp-2502.13986v1.md`), so it is the
    first measurement of it.
- **the ratio: sherd extent / vessel extent**, per piece.

**Part B — the same statistic at a physical window instead of a neighbour count.**

Today the curvature radius is fitted over the 30 nearest neighbours, whose physical size differs
between clouds (about 0.68 mm on the pot, 1.3-2.2 mm on the crushed sherds). Replace "30 nearest"
with "every point within w mm", for w = 1, 2, 3 and 5, and report per piece and per window:

- the median number of neighbours actually in the window;
- the median local curvature radius (same quadric fit as ticket 30's part A: local PCA frame,
  radius = 1 / max(|k1|,|k2|)), with its p25 and p75 and the share at the flat cap;
- the median neighbour-normal angle over pairs inside the window (ticket 29's arithmetic);
- the mesh-normal noise floor at that window (median folded angle to the nearest mesh vertex
  normal), so noise and signal stay separable.

**Part C — the two arms that make the pot like-for-like.**

Measure Pot A twice: at its native density, and subsampled to the Juglet's native spacing
(~0.25 mm), so the window contents are comparable. If the pot's numbers move between those two
arms, that movement is the price of density and belongs in the answer.

## Data and arms

- Juglet clouds: derived from the nine meshes as the pipeline derives them (ObjToPcd), not from
  `Dataset/Axes/Juglet` and not from the swept 2026-09-25 bundle, which is gone.
- Pot A clouds: the released corpus clouds under
  `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp` (read-only).
- Arms: `J` (Juglet, mesh-derived, native), `PA_native` (Pot A released cloud, native),
  `PA_025` (the same subsampled to 0.25 mm). Windows 1/2/3/5 mm on every arm.
- Everything runs on compute nodes. Nothing runs on the laptop or the login node.

## Evidence to produce

1. `out/sizes32.tsv`: piece, arm, n_points, extent_mm, area_mm2, vessel_mm, ratio, method notes.
2. `out/windows32.tsv`: piece, arm, window_mm, n_neighbours_median, rho_median_mm, rho_p25_mm,
   rho_p75_mm, share_at_cap, angle_p50_deg, angle_p10_deg, angle_p90_deg, noise_floor_deg.
3. One figure, 300 dpi, with a scale note: panel 1 the angle against the sherd/vessel ratio at
   each window (pot and sherd points distinguishable), panel 2 the fitted radius against the
   window width, one line per piece, with the vessel radius drawn as a reference line.
4. The vessel extents for both pots, with the command and the method that produced them.
5. Input md5 lists before and after; `/opt/sfs-pristine` recorded ABSENT if absent; corpus
   unchanged, proven by comparing the two md5 lists.
6. Geometry deleted at the end with a counted record (files, bytes, per extension), written
   before the delete; the tables, figure and logs kept.
7. An index row with `verdict` and `human_note` left EMPTY.

## Acceptance

- Both tables exist, one row per piece per arm per window, no row with a missing value silently
  dropped (a value that cannot be computed is written as `na` with the reason in a column).
- The vessel extents are derived, not assumed: the Juglet number is computed from the ground truth
  in this ticket, not copied from a note.
- The figure resolves what it claims to show — legible at the stated scale, with the pot and the
  sherds told apart, and the vessel-radius reference line labelled.
- Every number is traceable to a command in the run directory.
- No tracked source file changes. If the measurement cannot be made without changing tracked
  source, stop and report instead.
- Run directories under `/data/gpfs/projects/punim2657/SfSpp/runs/`, named by the usual
  convention; at most 3 jobs; CRLF checked before every submit.

## What this cannot settle

It will not say which threshold to use. It measures whether the ratio predicts the angle — the
reading is the lead's, and the threshold decision comes after it. It also cannot separate "the
sherd is a big piece of a small pot" from "the sherd is mostly broken edge", because both produce
a tight fitted radius; the ratio and the edge-fraction would have to be measured together for that,
and the edge fraction is not in this ticket.
