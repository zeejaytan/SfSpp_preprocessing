# 297 — Is the authors' chord on Pot D 22 Bl0 the better break edge?

Answers: E1
Status: in-progress
Working in: chat on Thinkbook16 (2026-10-25)
Branch: 297-d22-chord, in /c/PR/worktrees/sfs/297
Needs-eye: yes (the conservator has already looked at this mesh and read it against our record)

## The conservator's reading — recorded first, then tested

He said (2026-10-25, verbatim): **"i have seen the mesh for D22, i think in this case, author's
edgeline might be more accurate than ours."**

D22 Bl0 is an **interior** edgeline, the only kind the assembler reads (class/data_path.h names
Breakline_0 only), so this question is load-bearing for seating.

Today's record currently says the opposite, and it was written from distances, not from the sherd:

- Ticket 294: over an 18.0 mm straight segment the authors' line bridges a notch mouth; mean gap
  4.33 mm, arc 18.0 mm; conclusion at the time, "the chord is the authors'".
- Ticket 295 claim C3: D 22 Bl0 "holds with qualification" — their line is the boundary of their own
  face, over a 45.0 mm stretch (18.65% of the arc) 66.9% of their dots sit >2 mm from our material,
  the material under their line is 0.898 mm above ours, and our edge lies 5.974 mm further out.
- Ticket 295's own closing caveat: a distance to OUR material is not a statement about the real edge.

**This ticket exists because the person who has looked at the sherd disagrees with the ruler
reading, and the ruler was answering the wrong question.**

## What has to be true for his reading to be right

1. The chord lies **on the sherd's surface** across the notch (within ~0.5 mm of the mesh), not
   floating over air.
2. The strip between the chord and our detour is **break facet** — material pitched steeply away
   from the interior face — not interior-face material continuing outward.
3. Our detour is the thing that is wrong: it follows a lip, flange or ragged artefact rather than
   the material boundary.

## Measurements (Phase 1) — mesh-based, not cluster-based

Inputs: `Pot_D_Piece_22_Mesh_DS.obj` (2,074,532 B, already on the laptop at
`artifacts/mesh_for_viewing/`, and in the frozen corpus on Spartan), the authors'
`Breaklines/Pot_D_Piece_22_Breakline_0.pcd` from the corpus, and our `Breakline_0` for the same
piece regenerated at shipped defaults.

- **(a)** distance of every authors' dot to the **mesh surface**, reported separately for the chord
  stretch and for the rest of their line (the rest is the control: it should be on the surface).
- **(b)** the same for our dots (control for the instrument).
- **(c)** the patch enclosed between the chord and our detour: normal tilt against the interior
  face's mean normal (histogram, not a mean alone), its area, its radial depth.
- **(d)** share of that patch within 1 mm of the interior-face plane — face material or not.
- **(e)** whether our detour encloses interior-face-like material the chord would cut away.

## Pre-registered verdict rule (written before any number is computed)

- **CONFIRM** (his reading): >=90% of the chord's dots within 0.50 mm of the mesh **and** >=70% of
  the enclosed patch pitched >=45 deg off the interior face normal.
- **REFUTE**: the chord floats >1.0 mm from the surface over >50% of its length **or** >=70% of the
  enclosed patch lies within 20 deg of the face normal.
- **PARTIAL**: anything else — report both numbers, say which part of his reading survives.

No threshold moves after the first number is seen. If a measurement turns out to be impossible with
the data that exists, say so and stop rather than substituting a proxy silently.

## Definitions fixed before the run (no threshold here moves afterwards)

The rule above is fixed. These are the definitions it is applied with, written down before the run
so that the numbers cannot choose their own geometry. Code: `.scratch/pota-repro/297/measure297.py`
(measurement) and `render297.py` (the picture); both are copied into the run directory as
`scripts/` and their md5s are in the Results block.

- **The stretch** is fixed by ticket 294's own rule, copied verbatim out of
  `.scratch/pota-repro/294/p294_render.py:91-119` `worst_stretch()`: the run of OUR dots further
  than 2.0 mm from their line, chosen by the largest arc x mean gap; if no dot is further than
  2.0 mm the threshold falls back to max(1.0 mm, median + 0.5 mm). It gave dots 39-49 of 125 when
  294 was written; it is re-derived for each repeat here, never assumed.
- **The chord** is their dots from the one nearest our dot i to the one nearest our dot j,
  inclusive. Those dots are the *chord dots*; the rest of their line is the control.
- **The interior-face plane** is the least-squares plane through the authors' own labelled interior
  face (`Surfaces/Pot_D_Piece_22_Surface_0.xyz`, identified as the interior one by its agreement
  with our run's `Surface_0`) within 15 mm of the chord midpoint, grown to 22.5 and then 30 mm if
  fewer than 400 points fall inside; its normal is oriented away from the body, into the interior
  air. Three cross-checks are reported and **none of them feeds the verdict**: our own `Surface_0`
  fitted the same way, and the share of the mesh's local area that is parallel (<=20 deg), steeper
  than 45 deg, and perpendicular (>=70 deg) to that plane.
- **The enclosed patch** is the mesh triangles whose centroid lies inside the closed polygon
  [their chord dots] + [our detour dots, reversed], projected on that plane. Its area is the sum of
  those triangles' 3-D areas (the projected area is reported beside it); each triangle's tilt is
  acos(|n_tri . n_face|). Every share is **area-weighted**, with the count-weighted share printed
  beside it so the two cannot be confused.
- **Radial depth** and the face-plane offset are the signed distance of each patch triangle's
  centroid from the face plane along its normal.
- **Face-like** means tilt <=20 deg **and** within 1 mm of the plane; that is the quantity (e)
  reports, as mm2 and as a share of the patch.
- **"over >50% of its length"** for the REFUTE limb is measured length-weighted on the chord's own
  steps, with the dot-weighted share printed beside it.

### The gate, and what counts as reproducing 294

Ticket 294's row is 125 dots / 0.757 mm / 86.40 % ours / 78.95 % theirs at theta 3.40000. The
tolerance is this piece's own run-to-run spread, because the mesh stage draws 30 random ray-cast
points unseeded (`mesh_processing_headless.cpp:1526-1527`). Three repeats of the identical commit,
identical staged inputs and identical defaults are run; **the gate passes if 294's median 0.757 mm
and its cov_ours 86.40 % both fall inside the range the three repeats span**, and that spread
(max - min) is the piece's run-to-run spread, quoted with every later comparison. If they do not,
this ticket says so and every new number is marked provisional. Dot count is reported as it comes
out: the draw moves the line, so a dot or two either way is not a mismatch.

### Read the same way on each repeat

The rule is applied independently to each of the three repeats. If all three give the same verdict,
that is the verdict. If they differ, the verdict is PARTIAL and both outcomes are shown: the
repeats are not a menu to choose from.

## Constraints

- **No source edits, no parameter sweeps, no new binary.** Build the shipped commit with the recipe
  in `.scratch/pota-repro/294/submit294.sbatch`; **never** `build.sh --target nurbs` (it compiles
  the pre-247 duplicate at `original_nurbs_preprocessing/edgeline_extraction_headless.cpp`).
- Stage by symlink with `scripts/stage_piece.sh`; `SFS_AXIS_FILE` **must** be set and the
  `[PAPER-234] classify` line quoted in the report (ticket 277's trap: without it the stage keeps
  size order silently and Bl0/Bl1 swap).
- One run directory under `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_<tag>/`
  with run.json + submit.sbatch + logs/ + out/, plus a row in `runs/index.tsv` with verdict and
  human_note **left empty**.
- Keep the two line files and one PNG; delete staged geometry and say so in
  `out/GEOMETRY_DELETED.txt`.
- Reproduce ticket 294's D22 Bl0 row first as a gate: 125 dots / 0.757 mm / 86.40 ours / 78.95
  theirs, tolerance = this piece's run-to-run spread (the mesh draw is unseeded), stated in the
  ticket before the run.

## Acceptance

One verdict (CONFIRM / REFUTE / PARTIAL) with the five measurements above, the chord stretch
reported separately from the rest of the line, one picture carrying the mesh + both lines + the
enclosed patch, and the run directory named. Every number reproducible from the run's own outputs by
the lead.
