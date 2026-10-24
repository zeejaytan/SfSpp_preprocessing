# 285 — Pot C 01 and Pot J 01 are known-defective inputs (scan gap)

Status: recorded (no fix, no code change — the pieces are flagged, not repaired)
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

## Pot J 01 — the same defect (added 2026-10-24)

Conservator, 2026-10-24: **"same defect for J01"**. The class is not one bad scan, so it is recorded
per piece and any lane on a flagged piece is treated the same way.

What J 01 shows (shipped defaults unless stated):

| measurement | value | source |
|---|---|---|
| Bl0 shipped (theta 4.0 sheets, pre-strip binary) | 25 dots / 32.050 mm / cov 0.0 | ticket 273 matrix, column D |
| Bl0 on a theta-3.4 rebuild | 47 dots / 29.268 mm | ticket 275 Phase 0 |
| Bl1 on the same rebuild | 82 dots / 23.306 mm | ticket 275 Phase 0 |
| bag, shipped tree | 844 dots in 4 components (586 / 130 / 76 / 52), seed in the 130 | ticket 273 |
| bag, theta-3.4 rebuild | 832 dots in 4 components (580 / 127 / 75 / 50), seed in the 127 | ticket 275 census |
| with the held 275 selector | Bl0 170 dots / 0.558 mm / cov 100.00 (author-side 100.00) | ticket 275 Phase 2 |

The same two causes stand here as on Pot C 01 and are likewise **not separated**: the walk seed lands
in a debris lump 36.72 mm from the largest lump, and the surface is not closed. Until they are told
apart, J 01's stub is not evidence for a seed change either — which leaves **Pot B 01** (B01 Bl1
126 dots / 26.351 mm / cov 0.00, the 275 selector reaching 307 / 0.661 / 97.39) as the only sound
piece still carrying that evidence.

## What must not be concluded

- That the C01 52.6 mm stub, or the J01 29.3 mm stub, is a walk defect. Each may be a correct
  trace of a hole.
- That any change which "fixes C01" has improved the method, unless it is shown to leave the
  other lanes untouched AND the gap is shown not to be what moved.
- That the fragment-count of C01's bag (4 components) is debris only. The gap is an equally good
  explanation for a split.

## Open measurements (nobody has run these — they now cover both pieces)

- Where each gap is: locate the surface hole on Pot C 01 and on Pot J 01, its width, and whether it
  reaches the break face.
- Which lane each gap manufactures: does it account for C01's 259-dot lump and J01's 130-dot lump,
  and for the stubs that follow them?
- Whether the authors' own reference lines cross either gap (if they do, their pipeline had the same
  artefact; if they do not, ours invented it).

## Provenance

Conservator's statement, 2026-10-24, in the SfS++ session that was diagnosing the C01 collapse, and
the same statement for Pot J 01 later the same day. Not yet verified against either mesh; both are on
the laptop at `artifacts/mesh_for_viewing/Pot_C_Piece_01_Mesh_DS.obj` (11,875 vertices) and
`artifacts/mesh_for_viewing/Pot_J_Piece_01_Mesh_DS.obj` (5,524 vertices).
