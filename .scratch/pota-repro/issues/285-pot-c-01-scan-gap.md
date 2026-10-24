# 285 — Pot C 01 is a known-defective input (scan gap)

Status: recorded (no fix, no code change — the piece is flagged, not repaired)
Answers: none
Working in: none

## What was said

Conservator, 2026-10-24 (session note): **Pot C 01 is not watertight.** The scan left a gap in
the mesh, and the pipeline reads that gap as **a second broken edge the sherd does not have**.

This is a property of the INPUT, not of our code. It is recorded here so that no later ticket
scores Pot C 01 and reports the result as a method finding.

## Why it matters

It is the fourth kind of claim in this workspace, and the three-way list in `../AGENTS.md`
does not cover it:

1. the method genuinely failed;
2. the measurement was broken;
3. the reference answer was wrong;
4. **the input piece is defective** (this one).

Pot C 01 is currently the piece carrying the worst lane in the shipped pipeline — C01 Bl0 25 dots,
median 51.62 mm, coverage 0.0; Bl1 81 dots, 41.06 mm, 0.0 (ticket 284), and 11/82 in the earlier
matrix (ticket 273). Two candidate causes are on record:

- **the walk seed** (ticket 275): the full walk starts at the boundary dot nearest the cloud
  centroid, which on this piece lands in a debris lump 26-54 mm from the rim (bag of 986 =
  716/114/79/77, seed in the 77; Bl1 bag 1090 = 825/265, seed in the 265). Nothing in the debris
  carries an author dot.
- **the scan gap** (this ticket): the surface is not closed, and the gap surfaces to the boundary
  detector as an edge.

These have NOT been separated. Until they are, no lane on Pot C 01 may be cited as evidence that
the method fails or that a fix works: it can neither convict nor exonerate a walk change.

## What must not be concluded

- That the 52.6 mm stub is a walk defect. It may be a correct trace of a hole.
- That any change which "fixes C01" has improved the method, unless it is shown to leave the
  other lanes untouched AND the gap is shown not to be what moved.
- That the fragment-count of C01's bag (4 components) is debris only. The gap is an equally good
  explanation for a split.

## Open measurements (nobody has run these)

- Where the gap is: locate the surface hole, its width, and whether it reaches the break face.
- Which lane it manufactures: does it account for Bl1's extra contour, and for the 259-dot lump?
- Whether the authors' own reference lines cross the gap (if they do, their pipeline had the same
  artefact; if they do not, ours invented it).

## Provenance

Conservator's statement, 2026-10-24, in the SfS++ session that was diagnosing the C01 collapse.
Not yet verified against the mesh; the mesh is on the laptop at
`artifacts/mesh_for_viewing/Pot_C_Piece_01_Mesh_DS.obj` (11,875 vertices).
