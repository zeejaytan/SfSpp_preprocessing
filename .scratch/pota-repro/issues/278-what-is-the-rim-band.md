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
