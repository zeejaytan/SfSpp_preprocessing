# 05: Apply the noise filter the method specifies

**What to build:** the edge-line noise filter is actually applied, rather
than computed, written to disk, printed, and then thrown away.

The paper (§IV-B1) specifies: "Using a K-D tree-based search, points near
the edge line are identified and filtered to remove noise and outliers."
The code does all of that — and then reloads the **unfiltered** boundary
cloud over the filtered one before sequencing, so the filter's output is
never used. On the Juglet it made no difference anyway (it kept 59 of 59
points), which is why this sat unnoticed; on a noisy scan it would
silently do nothing.

**Answers:** E1

**Blocked by:** 04 (filter the edge line once it is known which surface
it belongs to)

**Status:** resolved 2026-09-30 — the filter runs, is ordered, and is
tested. Gate unmoved on both pots, as the ticket predicted (its own note:
no movement is expected and is not evidence of pointlessness).

**Needs-eye:** none.

- [ ] The filter runs after the improved surface/edge-line selection and
      its result is the cloud that gets ordered — verified by a test that
      fails if the unfiltered cloud is ever reloaded
- [ ] The reload of the unfiltered boundary is gone, and a comment
      records that it was there and why it was wrong
- [ ] The filter radius and neighbour count are derived from the cloud's
      own spacing rather than fixed in millimetres, so the stage behaves
      the same on a 65 mm juglet and a 300 mm pot
- [ ] The number of points removed is logged; a filter that removes
      nothing and a filter that removes almost everything are both
      visible in the log
- [ ] A synthetic boundary with a gross outlier loses that outlier, shown
      by a test

## RESOLVED 2026-09-30

- The filter runs after surface selection and its result is what gets
  ordered — shared seam `boundary_filter.{h,cpp}`, compiled into both
  pipeline and test; the `boundary.pcd` reload is gone with a comment
  recording it was there and why it was wrong.
- Radius/neighbors from the cloud's own spacing (bbox-sheet boundary
  radius; 3/6 split at 100 points) — same on juglet and 300mm pot.
- Kept/removed counts logged per face (`[SFS-T05]`); empty-filter falls
  back to unfiltered LOUDLY, never a silent vanishing trace.
- Unit test green 6/6 (synthetic 15mm rim + gross outlier 100mm off: 60
  kept, outlier gone, empty safe).
- Pot_A `filter_live` 15/15 — per-pair inliers moved (1-2: 2→3, 1-3:
  18→25) with all pairs still passing; vote pattern unchanged.
- Juglet 0/5 scorable, 5 unmeasurable, zero copies — trace bytes moved,
  no pair crossed the gate.

## Note

Small ticket, and easy to judge wrongly: if the acceptance number does
not move, that is expected and is not evidence the change was pointless.
Its value is that the code now does what the method says, and that the
behaviour is covered by a test.
