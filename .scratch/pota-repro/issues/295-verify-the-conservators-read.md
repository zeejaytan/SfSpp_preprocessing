# 295 — Verify the conservator's reading of the eleven below-bar lanes

Status: in-progress
Working in: chat on Thinkbook16 (2026-10-25)
Branch: 295-verify-the-conservators-read, in /c/PR/worktrees/sfs/295
Answers: E1
Created: 2026-10-25
Follows: 293 (the mechanism), 294 (the pictures), 279 (a reference is the boundary of the authors' kept surface)

## Why

The conservator read the eleven figures of ticket 294 and gave a reading of each lane. Every claim below
is a statement about geometry, so every one can be measured. This ticket measures them and says plainly
where the reading holds, where it needs qualifying, and what the answer implies for the pipeline.

**The claims, as stated by the conservator (2026-10-25):**

- **C1 — Pot I 25.** Agreed the lanes are swapped. The open question is *why this single piece got the
  interior/exterior the other way round from the authors*, and *who is correct* — we fixed the
  interior/exterior detection and every other piece agreed with them.
- **C2 — Pot C 03 Bl1.** Our line is much better; the authors' line did not trace the break at all, it
  traced the base.
- **C3 — Pot D 22 Bl0 and D 27 Bl0/Bl1.** Ours is the better match to the mesh/surface; D 27 "clearly
  better".
- **C4 — Pot H 10 Bl1.** Either another mismatched edgeline, or our surface is bigger than the authors'
  line implies.
- **C5 — Pot I 06 Bl1 and I 13 Bl1.** Same category: our mesh is bigger, so our traced line is bigger,
  and it looks as if our surface includes part of the break surface.

## What to measure

Q1 (C1) **Which of the authors' two surfaces is the interior?** For every piece in the corpus with
author artefacts (163 pieces), load the authors' `Surface_0` and `Surface_1`, the piece axis, and decide
each surface's side two independent ways: (a) radial position -- median distance from the axis; (b) normal
direction -- the sign of the mean dot of the surface normals with the outward radial direction. Report the
split as a count ("Surface_0 is the inner face on N of 163 pieces, by radius; by normals on M"), the
definition used, and the pieces that disagree. Then for **Pot I 25** specifically: which of the authors'
surfaces does their `Breakline_0` ride, which does `Breakline_1`, and is that surface the inner or the
outer one. Compare against our own decision line for that piece, printed by the mesh stage as
`[PAPER-234] classify: face0 n=... interior_frac=... face1 n=... interior_frac=... satA=... satB=...`
(ticket 293's log has it: face0 n=3072 interior_frac=0.0000, face1 n=2321 interior_frac=0.9931,
satA=16.0000 satB=5377.0000, then "swapped -> Surface_0=interior"). Say which side is physically the
interior for this sherd, with the evidence, and whether the authors or we are the outlier.

Q2 (C2) **Does the authors' Pot C 03 Bl1 line follow the base?** Measure: the distance of every author
dot to (i) the base band's outer rim, (ii) the band's interior, (iii) our line; the share of their dots
lying on the flat of the band (in-band cross-section); and whether their dots sit on material that the
pipeline dropped. State in one line what edge their line is, and what edge ours is.

Q3 (C3) **Is the reference a break edge at all on D 22 Bl0, D 27 Bl0 and D 27 Bl1?** For each: the share
of reference dots within 2 mm of material; the share whose tangent-plane angular gap marks them as on a
boundary (> 100 deg, the ticket 280 statistic); for D 22 the share of the arc lying over empty space (the
chord); and for D 27 the distance of their line from the face's own boundary. Conclusion per lane: is the
reference a boundary curve, a curve through the interior of the face, or a chord over a void.

Q4 (C4) **Pot H 10 Bl1 — mismatch, or a bigger surface?** Decide between: (a) another interior/exterior
label mismatch; (b) our kept face spans a step/crease and the reference turns at it; (c) our kept face
includes break-surface material. Measure on our kept face: the local surface normal deviation from the
face's dominant plane along the 39.6 mm stretch, histogrammed; the axial/height profile of our surface
across the stretch; the share of the stretch lying over the dropped cluster `c5` (ticket 281: 629 points,
0.3191 mm from kept `c1`, carrying 21 of 88 Bl1 dots); and the distance of the reference dots from our
fitted plane. One conclusion.

Q5 (C5) **Pot I 06 Bl1 and I 13 Bl1 — is our face bigger because it includes the break surface?** Same
instrument as Q4, plus: the local surface tilt at each reference dot (covered vs uncovered) and the share
of our kept face in the stretch whose tilt exceeds, say, 45 deg from the face's dominant plane -- break
facets are steep, a wall face is not. If our face does weld the break facet, say at what share of the
stretch and how far the welded band reaches. Note I 13 additionally swings between two kept faces
(ticket 293: 68.75% nearest `c1`, 31.25% `c0`), so say whether it is one case or two.

## Data you already have

- `..\20261025-0456_3ada802_p293-census/out/` -- ticket 293's tables (`crosspair.tsv`,
  `assign_summary.tsv`, `clusters.tsv`, per-dot `assign.tsv`), the nine piece cluster dumps in `out/diag/`
  (text: mesh points with cluster and surface labels; if normals are missing, derive them by local PCA),
  the eleven figures in `out/png/`, and the logs.
- Authors' artefacts for all 163 pieces: `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/`
  (`Surfaces/`, `Breaklines/`, `Axes/`).
- Meshes (DS for most pieces): `original_samples_backup/SfS_pp/Mesh/`.
- Frozen clouds: `original_samples/SfS_pp/Point/` (manifests beside them, ticket 290).

## Constraints

- **Read-only.** No pipeline run, no rebuild, no default, threshold or C++ change. Analysis code lives on
  the ticket branch. If you must run something on Spartan, a short batch job in a run directory is fine,
  and every job gets `SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_<tag>/` with `run.json`, `submit.sbatch`,
  `logs/`, `out/` and a row in `runs/index.tsv` (verdict and human_note empty -- those are the lead's).
- Stage by symlink (`scripts/stage_piece.sh`) if you need a piece, and delete geometry before you report;
  keep the tables.
- Never `build.sh --target nurbs`: that target compiles the pre-247 duplicate in
  `original_nurbs_preprocessing/` (ticket 282).
- Anything you quote from ticket 293 must reproduce to **0.05 mm and 1 coverage point**, or the
  difference must be stated.

## Acceptance

1. Q1: the 163-piece split as counts, the definition used, the disagreeing pieces named, and the Pot I 25
   verdict with the evidence that decides which side is the interior. A plain answer to "who is correct".
2. Q2-Q5: one row of metrics per lane as specified, plus one plain-language conclusion per lane, marked
   **holds** / **holds with qualification** / **does not hold** against the conservator's claim.
3. A closing paragraph: which of C1-C5 hold, what the exceptions are, and -- if any lane is a welded break
   facet -- what mechanism would have to change (growth, classify, or partition), stated as a hypothesis
   with the number that supports it.
4. Every number traceable to a file in the run or analysis directory; nothing quoted from memory.

## Results

(worker appends)
