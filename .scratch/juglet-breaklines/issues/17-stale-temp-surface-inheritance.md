# 17: Stale temp files let one sherd's surfaces masquerade as another's

**Answers:** E1

**Blocked by:** nothing — small, reviewable, high blast radius

**Status:** ready-for-agent

**Needs-eye:** none for the fix (plumbing + control flow). The resulting
Juglet breaklines get witnessed under ticket 07's eye requirement, not here.

## The finding

Fresh Juglet run, verified by `cmp` and md5 on disk:

- Pieces 2&3: `Surface_0.xyz` byte-identical (`d6325651`), `Surface_1.xyz`
  identical, breaklines identical (`5ed74975`). Pieces 8&9: same pattern
  (`b2462b5c`, `d5aebe0e`).
- Inputs distinct: meshes differ, Point clouds differ (unique md5s,
  136KB vs 184KB), SampledWithNormals differ.
- Divergence collapses inside `surfaceSegmentation`: `SampledWithNormals`
  differs, `Surface_*` identical.
- Piece 3's (and presumably 9's) `unclustered.ply` is MISSING, not empty.

Mechanism, read from the code, not guessed:

1. `tmpSurfaceCluster_Improved_0/1.ply` are FIXED filenames in the shared
   `intermediatePath` (`mesh_processing_headless.cpp:1809-1810`).
2. The `clusters.size() == 1` branch (`:1921-1943`) builds Cluster1 and
   `break`s — writing NO tmp files and skipping the unclustered section —
   which contradicts the retry loop's evident purpose (loosen smoothness
   +2°/iter up to 45°, 30 iterations, to reach ≥2 clusters).
3. The per-piece copy (`:2108-2117`) checks only `fs::exists`, so a piece
   that produced nothing inherits the previous piece's temp files and
   presents them as its own surfaces.
4. Processing order is alphabetical, so piece 3 inherits piece 2's and
   piece 9 inherits piece 8's. Exactly the observed pairs.

So pieces 3 and 9 have NEVER had their surfaces computed in any run that
hit the single-cluster path — and 4 of 9 Juglet breaklines in the just-
scored bundle are copies. **The 0/18 (0/10 honest) Juglet gate was measured
on corrupted data** and must be re-measured after this fix. Ticket 07
records the retraction.

Pot_A never triggers this (min 2 clusters everywhere: [8,2,2,2,3,2,6,4]),
which is why it stayed hidden. Any pot with a single-cluster sherd hits it.

## What to build (three small changes, one ticket because one bug)

1. **Clean stale temps at piece start** (or write outputs unconditionally):
   delete `tmpSurfaceCluster_*.ply` before segmentation per piece, so a
   piece that produces nothing fails LOUDLY (missing output) instead of
   inheriting. This alone converts silent corruption into explicit error
   and is correct independent of (2).
2. **Remove the premature `break`** in the `==1` branch so the retry loop
   loosens thresholds as evidently intended (capped at 30 iterations,
   existing). Pot_A never exercises this path (min 2 clusters), so no
   regression risk there; judge the outcome by Juglet vote margins + gate.
3. **Skip missing Surface files gracefully in both stages** (warn +
   continue with remaining pieces) instead of aborting the pot
   (edgeline `copy_file` throws → `return -1`) or asserting (empty
   unclustered → SIGABRT, already fixed once in the edgeline for the
   missing-file case; same class).

## Open question, recorded not ducked

What SHOULD a genuinely single-cluster sherd produce? If loosening to 45°
shatters piece 3 into garbage, the vote guards (10%/2.0) should catch weak
margins and keep history — but history would then be missing files, and
"keep" is meaningless. If that happens, the ticket's answer is "skip the
sherd loudly," not a fourth mechanism. Say which outcome occurred.

## Acceptance criteria

- [ ] Rerun shows 9 distinct Surface_0 files (md5-unique) OR explicit
      per-piece skips with warnings — never silent copies. Verified by
      `cmp`, not by log lines (ticket 04's exchange bug is why).
- [ ] No two pieces' breaklines byte-identical unless their meshes are
- [ ] Juglet gate re-measured per pair (honest denominator recomputed —
      the old 0/10 rested on copies and is retracted, not compared against)
- [ ] Pot_A re-measured per pair from its baseline (must be unchanged;
      the path is unexercised there, prove it)
- [ ] Authors' arm rides along; guard audit re-run
