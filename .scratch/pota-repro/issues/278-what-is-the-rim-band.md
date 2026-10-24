# 278 — What is the band that holds Pot C 03's whole rim reference?

Answers: E1
Status: ready-for-agent (diagnostic only — no C++ change)
Working in: nothing under version control; reuse the ticket 276 dumps
Needs-eye: no

## Where this comes from

Ticket 276 Phase 3a (run `20261024-1223_0ab0935_p276-phase3a`, job 33737576) established that Pot C 03
Breakline_1's author reference — **119 of 120 dots** — sits on a cluster that the classify step can
never keep:

- the band is the **third** cluster by size (13265 points, against 17245 and 23446 for the two that
  become surfaces), and `classifyAndOrderPaper234` keeps `pclusters[0]`/`pclusters[1]`
  (`mesh_processing_headless.cpp:2105-2118`, the paper's two-largest rule at
  `C:/PR/papers/text/sfspp-2502.13986v1.md:155`);
- the band stands **2.4872 mm** from the kept pair at theta 3.4 (1.9306 mm at 4.0) with **zero point
  pairs within 2 mm** and only 41 within 3 mm, against a 0.3067 mm sampling spacing inside the band.
  So no Appendix A test is ever reached on it: the pair fails on distance long before normals or
  curvature are asked.

The reference breaklines are the authors' own pipeline output, produced under the same two-largest
rule, so in their run a kept surface reached the rim. Ours does not. The merge is not implicated and
theta is not implicated. The open question is what this band physically is.

## Goal

Characterise the band on Pot C 03, and the analogous dropped clusters on Pot H 10, well enough to say
which stage owns the defect.

## Method (reuse the dumps; no new mesh run unless one is genuinely needed)

1. **Orientation.** For the band's points, the median absolute dot product of their normals with the
   kept exterior face's normals. Near 1 = a sheet lying parallel to the face; near 0 = a cross-section.
2. **Shape and extent.** Is it a closed ribbon following the rim, or a patch? Report its extent along
   the rim and across it, and whether its boundary meets the kept face anywhere.
3. **Relation to the author's line.** For the 120 author dots: their distance to the band's own outer
   and inner boundary, and whether they sit on the band's edge nearest the face, its middle, or its
   far edge.
4. **The gap itself.** Is the 2.49 mm separation a hole in the cloud or a real fold? Count the
   unclustered points inside the slab between the band and the face, and report whether the band's
   nearest approach to the face is a point-to-point contact or a gap everywhere along its length.
5. **Pot H 10**, which got worse at 3.4 (96.59% -> 79.55% kept): the same four summaries for the
   dropped clusters carrying its author dots (c2 1.2253 mm, c3 1.3183 mm, c4 1.2868 mm).

## Pre-registered read (written before the measurement)

- **Parallel (`|dot| > 0.8`) and offset by 1-2.5 mm** => the band is a second sheet of the same wall
  (inner surface, or a scan layer behind the outer face). The defect is then upstream — in the cloud
  or in how region growing separates the sheets — and the fix belongs there, not in the merge.
- **Perpendicular (`|dot| < 0.4`)** => the band is the break face (the wall's cross-section at the
  rim). The author's line then sits on the break face while ours stops at the edge — a placement
  difference owned by the edge stage, and the mesh stage is doing its job.
- **In between** => report the distribution rather than forcing a side; that is a real answer too.

## Acceptance

- The four summaries above for Pot C 03, plus item 5 for Pot H 10.
- One line naming which stage owns the defect, drawn only from the pre-registered read.
- Every number traceable to a file in a run directory, with the dump paths and their md5s.

## Evidence to report

- the orientation and shape table, with the band and the face identified by cluster size
- the gap census (unclustered points in the slab; where contact occurs, if anywhere)
- the one-line verdict, plus the single measurement that would overturn it

## Lead verdict (2026-10-24)

**Accepted.** The identification stands on four independent measurements that agree
(orientation vs the two kept faces, disc-shaped PCA, closed near-constant outer radius, and
the author's own dots sitting 0.96 mm inside the outer boundary). The overturning
measurement was named in advance and came back the other way, so this is not a
post-hoc story.

**What it changes.** The Pot C 03 lane is no longer an edge-stage question at all. The edge
stage is never given the face the reference line is drawn on: 119 of 120 reference dots sit
on a cluster that the two-largest rule cannot select (13265 points, third by size), and the
corner ring that would let it join anything is unlabelled (1175 points, all 36 bins,
mutual spacing 0.3556 mm, 0 of them within 1 mm of both sides). The 2.4872 mm distance is
not a hole in the cloud, it is a hole in the labelling.

**Why this is not a parameter.** rho_d would have to triple (1.0 -> ~3.0 mm = ten sampling
spacings) to reach it, and the band is still third by size, so no rho_d value both keeps
Appendix A honest and selects the base. Recorded as closed: merge, classify order, theta,
rho_d and the two-largest ordering are each innocent of *this* lane, and three of them are
innocent by measurement rather than by argument.

**What the paper says that we do not implement.** C:/PR/papers/text/sfspp-2502.13986v1.md:279
(Fig. 11) names base fragments as a distinct class with "a flat surface or a sharp
transition from the base to the side surface"; :313 tabulates base sherds detected per pot
(Pot C 1/1), so their pipeline does identify base sherds; :275 says graph merging exists
precisely because base features used to be relied on. A grep of
C:/PR/SfSpp_preprocessing/mesh_processing_headless.cpp for base returns only the CGAL
Alpha_shape base classes (:90-91), basePath arguments (:1567-1577) and baseName (:2505-2507):
our port has no base-sherd handling of any kind. That gap is now the leading explanation for
why their kept surface reaches the base rim on this piece and ours cannot.

**Pot H 10 kept separate.** Its dropped clusters are genuine break faces (0.07-0.12 against
both kept faces, thin ribbons) and the line is drawn on the fracture instead of at its edge:
an edge-stage placement question. Only c5 (a 0.3191 mm split-off fragment of the exterior
face, fifth by size, 21 of 88 Bl1 dots) is a partition element, and it is small enough to
leave for later.

**Not done here, deliberately:** no third-surface support, no relabelling of the corner
ring, no rho_d tuning, no code change. Each is a design decision larger than this ticket.
