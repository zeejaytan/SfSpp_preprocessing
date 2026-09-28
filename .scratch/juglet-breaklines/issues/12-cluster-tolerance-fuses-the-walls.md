# 12: The cluster tolerance may be fusing the two wall faces

**Answers:** E1

**Blocked by:** nothing

**Status:** needs-info — premise wrong, see correction 2026-09-28 below; do NOT run the Euclidean-tolerance sweep as specified

**Needs-eye:** required before closing. A geometry claim about which surface
the rim comes from, so the conservator's eye on the affected sherd.

## The setting, and the correction

`mesh_processing_headless.cpp:658`:

```cpp
ec.setClusterTolerance(2); // 2cm
```

**The value is 2 millimetres and the comment says centimetres — one of the
two is wrong.** The pipeline is in millimetres: the Juglet fix noted at
`edgeline_extraction_headless.cpp:844` exists precisely because this code
previously assumed metres and read 0.015 as 0.015 mm. So the tolerance is
**2 mm, not 20 mm.**

I initially wrote this ticket up on the assumption that it was 20 mm and that
the tolerance therefore exceeded every sherd. **That was wrong, and it is
recorded here because the error pointed the wrong way** — a 2 mm tolerance is
smaller than every sherd (smallest extent 26.2 mm) and about the scale of the
wall, so it cannot merge a whole sherd into one blob by being too large. It
can, however, **bridge the gap between the two wall faces** and fuse them,
which is the opposite failure and the one the evidence actually supports.

`setClusterTolerance(3)` at line 1948 is a second clustering site and is also
inconsistent with the first. Both need looking at.

## Why this is the last candidate standing

Everything else has been measured and excluded:

| candidate | verdict | evidence |
|---|---|---|
| boundary radius | **excluded** | gate flat at 7/15 for every radius 3–9 mm; only collapses below 3 mm (ticket 11) |
| interior/exterior wall choice | **excluded as the cause** | swap gives 6/15, recovering no pair (ticket 10) |
| wall-normal offset | **excluded** | our rim sits 0.02 mm off the mesh, authors' 0.00 mm — not the 1.2 mm once claimed |
| traversal direction | **excluded** | normals are surface normals, \|n·t\| = 0.012 |
| the axis | **excluded** | it only sets a rim/non-rim flag via `getDistFromAxis`; it never transforms a point |

**And the bias in ticket 11 is withdrawn.** Measuring each rim's radius from
its *own centroid* was circular: a rim that traces a slightly different path
has a different centroid, so the radii differ without the curves being far
apart. What actually survives, measured three ways:

- our rim is on the mesh (0.02 mm), the authors' too (0.00 mm);
- the excess is **spread evenly along the whole loop** — 3.83 mm at the ends,
  3.42 mm in the middle, so not truncation and not a localised miss;
- it is a **rigid lateral translation** with **direction agreement 0.91–0.97
  within each sherd, but a different direction on each sherd**.

Per-sherd, constant, lateral. That is the signature of a per-sherd surface
difference — which is what a clustering that fuses or shatters a sherd's two
walls would produce.

## Ticket 10's observation that this explains

Measured there and unexplained until now: on **7 of 8 Pot_A sherds the mesh
stage emits one cluster holding 100% of the points**, so `Surface_0 =
largest cluster` makes no choice at all and both walls pass forward as one
surface. Only piece 1 produced 31 clusters — and **piece 1 is the only sherd
whose rim matches the reference.** A 2 mm tolerance against a wall a few
millimetres thick is exactly the regime where that happens.

## The falsifiable prediction

Raising the tolerance until the walls *must* separate should make the cluster
count per sherd go above 1, **and the gate score must move**. Both halves
matter:

- clusters rise, gate does not → this is eliminated like the others, and the
  fusion is incidental rather than causal;
- clusters rise, gate improves → this is the cause, and the tolerance is the
  fix.

Reporting only the first half is how the previous five candidates each got
eliminated, and only the second half is the finding.

## The constraint that makes this not a one-liner

A tolerance must be **larger than the wall thickness** (so the faces do not
fuse) and **smaller than the sherd's own extent** (so a sherd does not
shatter into fragments). For a 26 mm sherd those bounds are close together,
and a tolerance that separates the walls on the 119 mm sherd may fragment the
small one — after which "largest cluster" picks an arbitrary fragment. That
is the same failure mode ticket 01 recorded when a different parameter was
made too aggressive.

So the tolerance likely has to be **derived per sherd** — from the measured
point spacing, as the boundary radius already is — rather than set once. The
paper does not specify a cluster tolerance, so this is **our judgement, not a
compliance fix**, and must be recorded as such.

## CORRECTION 2026-09-28 — wrong clustering stage, do not run as specified

Read the code before sweeping (`mesh_processing_headless.cpp`):

- `Surface_0` / `Surface_1` come from **RegionGrowing** in `surfaceSegmentation`
  (`:1641-1649`, `:1686`), with defaults `smoothnessAngleThreshold = 4.5`,
  `curvatureThreshold = 1.5` (`:2088`) and existing env overrides
  `SFS_SMOOTHNESS_DEG` / `SFS_CURVATURE_THRESH` (`:2093-2094`). No rebuild
  needed to sweep these.
- `setClusterTolerance(2)` (`:658`) lives in `getClusters_EuclideanDistBased`,
  called only by `getBreakLineForDecorativeParts` (`:1034`) on the
  **unclustered-point** file (`:1906`). It feeds decorative breaklines, not
  `Surface_0`.
- `setClusterTolerance(3)` (`:1948`) lives in `getClusters`, which has **no
  callers** in the file. Dead code.
- The "31 vs 1 cluster" observation in ticket 10 counted
  `*_unclustered.plyCluster_*.pcd` files — the decorative-stage output, not
  the surface split. The association with piece 1 matching is therefore
  **unexplained by this mechanism**, and the falsifiable prediction in this
  ticket (raise Euclidean tolerance → walls separate → gate moves) tests the
  wrong stage.

So the Euclidean-tolerance sweep must NOT run. The surviving upstream
candidate is the **RegionGrowing smoothness/curvature split** that actually
produces `Surface_0` / `Surface_1`, sweepable today via the existing env
vars. The per-sherd, constant, lateral translation signature (ticket 11
withdrawal + direction measurement) is consistent with a per-sherd surface
split difference, which is what that stage controls.

Redirect: sweep `SFS_SMOOTHNESS_DEG` on Pot_A piece 3 first (single-file mode
exists, `:2036-2043`), then all 8. Measure per-sherd cluster behaviour of the
*RegionGrowing* split plus gate score from 7/15. Both halves, per the rule in
ticket 11.

## Acceptance criteria (original, superseded for the Euclidean part)

- [ ] Both clustering sites (lines 658 and 1948) are examined; they currently
      disagree with each other
- [ ] Cluster count per sherd is reported before and after, on all 8
- [ ] The **gate score** is reported before and after, per pair, from 7/15
- [ ] The unit discrepancy in the `// 2cm` comment is resolved — the comment
      or the value is wrong, and saying which is part of this ticket
- [ ] A witnessed look at one affected sherd, since this is a claim about
      which surface the rim comes from
- [ ] If the tolerance is made adaptive, it is derived from a measured
      quantity per sherd, not from a single global constant
- [ ] The authors' arm is included in every comparison, per the rule ticket
      11 records: when a conclusion says X is not the cause, measure the
      reference too
