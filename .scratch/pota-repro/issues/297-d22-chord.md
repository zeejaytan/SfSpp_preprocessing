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

## Results

Measured 2026-10-26 in run `20261026-0005_a21822e_p297-chord` (Slurm job 33781671), commit
`a21822e72cc6855cc68b5faf5dc2f21364772733` on this branch, three repeats of identical staged inputs
at the shipped defaults. Everything below is in that run's `out/`: `measure297.txt`/`.json` (the
pre-registered rule's numbers), `measure297.secondary.txt` (checks run *after* the rule, which cannot
move it), `scores.tsv`, `classify.tsv`, `build.json`, `inputs.*.md5`, `source.md5`, `png/`.
Picture: `artifacts/297/Pot_D_Piece_22_chord.png` (run copy `out/png/p297_D_22_Bl0_chord.png`).

### The gate — 294 reproduced, and this piece is deterministic here

| repeat | n ours | n auth | median mm | cov ours % | cov auth % | len ours mm | max step mm |
|---|---|---|---|---|---|---|---|
| rep1 | 125 | 133 | 0.757 | 86.40 | 78.95 | 223.007 | 1.801 |
| rep2 | 125 | 133 | 0.757 | 86.40 | 78.95 | 223.007 | 1.801 |
| rep3 | 125 | 133 | 0.757 | 86.40 | 78.95 | 223.007 | 1.801 |
| 294's row | 125 | 133 | 0.757 | 86.40 | 78.95 | 223.007 | 1.801 |

Spread over the three repeats: **0.000 mm** on the median, **0.00 pp** on `cov_ours`; 294's row sits
inside it to the digit. **GATE PASS.** `SFS_AXIS_FILE` was set, and on all three repeats:

```
[PAPER-234] classify: face0 n=5642 interior_frac=1.0000 face1 n=5027 interior_frac=0.0000 satA=10669.0000 satB=0.0000
[PAPER-234] classify: kept -> Surface_0=interior
```

theta `3.40000` on all three (`out/classify.tsv`).

The spread is genuinely zero here, not rounding: the three exported Bl0 files are byte-identical in
x, y and z (md5 `4625c4e1576de44a87bce6bf1cc56417` over those three columns of each file) and their dot
sets agree to 0.000000 mm in every pairing. Only the fitted `normal_x/y/z` and `curvature` columns
differ run to run (first dot, rep1 `-0.64774 0.275002 -0.710498 1.2257e-37` against rep3
`-0.645611 0.267572 -0.715256 -2.77415e-09`), and the rule uses dot positions and mesh-triangle normals,
never the file's normals.

### (a) Every authors' dot to the mesh surface — the chord apart from the rest

| their dots | n | median | p95 | max | <= 0.50 mm | > 1.0 mm | > 2.0 mm |
|---|---|---|---|---|---|---|---|
| chord stretch | 23 | 0.025 | 1.040 | 1.386 | 86.96 % | 8.70 % | 0.00 % |
| the rest | 110 | 0.011 | 0.077 | 0.136 | 100.00 % | 0.00 % | 0.00 % |
| whole line | 133 | 0.012 | 0.107 | 1.386 | 97.74 % | 1.50 % | 0.00 % |

(mm; the whole-line row agrees with ticket 294's mesh reference row for this lane, median 0.012 /
p95 0.107 / max 1.386 / 0.00 % beyond 2 mm — the instrument reproduces itself.) Length-weighted on
the chord's own steps: **4.16 %** of it is more than 1.0 mm from the mesh and **79.02 %** is within
0.50 mm.

### (b) Our dots, same instrument — the control

| our dots | n | median | p95 | max | <= 0.50 mm | > 1.0 mm |
|---|---|---|---|---|---|---|
| detour 39-49 | 11 | 0.081 | 0.150 | 0.151 | 100.00 % | 0.00 % |
| the rest | 114 | 0.025 | 0.134 | 0.332 | 100.00 % | 0.00 % |
| whole line | 125 | 0.027 | 0.145 | 0.332 | 100.00 % | 0.00 % |

Our line is on the mesh along its whole length; neither line is floating, so "on the surface" cannot
separate them and (a)'s shortfall is not an instrument artefact.

### (c) The patch enclosed between the chord and our detour

1533 mesh triangles, **411.74 mm2** of 3-D area (232.96 mm2 projected onto the face plane). Tilt
against the interior-face normal, area-weighted, 5-degree bins 00-90:

```
00-05 0.0   05-10 0.5   10-15 1.2   15-20 3.5   20-25 3.6   25-30 4.2
30-35 5.2   35-40 7.5   40-45 9.4   45-50 13.5  50-55 10.1  55-60 7.1
60-65 5.5   65-70 3.9   70-75 5.8   75-80 6.9   80-85 6.2   85-90 5.9
```

**>= 45 deg: 64.89 % of the area** (71.82 % of the triangles); **<= 20 deg: 5.24 %** (3.33 %). Signed
offset from the face plane along its normal: min -36.69, p5 -35.57, median +1.56, p95 +10.67,
max +12.39 mm — radial depth **36.69 mm**, the polygon reaching round to the body's far side.

The face plane is the authors' own labelled interior face (`Surfaces/Pot_D_Piece_22_Surface_0.xyz`,
1122 points within 15 mm of the stretch, least-squares rms 2.995 mm, normal
`[-0.9296, -0.0433, -0.3661]`). Cross-checks, none of which feed the verdict: our own Surface_0 fitted the
same way differs by 45.07 deg; in the same 15 mm disc the local mesh's area is only 6.4 % parallel to
that plane, 12.18 % perpendicular and 55.92 % steeper than 45 deg over 3127 triangles — the corner is
rounded, so a plane is a crude reference there and the 20/45-degree limits sit within about 6 deg of a
plane that itself fits to rms 3.0 mm.

### (d) Share of the patch within 1 mm of the interior-face plane

**13.99 %** of its area (8.28 % of its triangles). Restricted to the strip near the plane
(|offset| <= 15 mm, which drops the wrap round the far side): 1014 triangles, 331.80 mm2, and there
**64.80 % >= 45 deg** against **0.69 % <= 20 deg**.

### (e) Face-like material the chord cuts away

Triangles both <= 20 deg off the face normal *and* within 1 mm of the face plane: **9.66 mm2, 2.35 %
of the patch** (2.18 mm2 of it in the near-plane strip).

### The chord stretch, on its own

Our stretch by 294's own rule (run of our dots further than 2.0 mm from their line, chosen by max of
arc x mean gap, re-derived on each repeat): our dots **39-49** (11 of 125), **18.00 mm** of arc, mean
gap 4.335 mm, threshold 2.00 mm.
Their counterpart, the dots between the ones nearest our two ends: their dots **12-123** (23 of 133),
**43.28 mm** of their line, ends **19.92 mm** apart, straight distance 19.92 mm.

That is the correction to 294's own wording: their route is **not a straight chord**. Over this
stretch their line goes round the corner — 43.28 mm of polyline — where ours cuts across it in
18.00 mm, and their two ends are 19.92 mm apart. Both lines coincide elsewhere: 105 of their 133 dots
lie within 2 mm of ours.

### Verdict: PARTIAL, and which part survives

The pre-registered rule, applied literally and identically on all three repeats:

- CONFIRM needs >= 90 % of the chord's dots within 0.50 mm **and** >= 70 % of the patch >= 45 deg:
  got **86.96 %** and **64.89 %**. Both limbs miss.
- REFUTE needs > 50 % of the chord's length more than 1.0 mm off **or** >= 70 % of the patch within
  20 deg: got **4.16 %** and **5.24 %**. Neither limb is close.

**PARTIAL.** Both CONFIRM limbs point his way and neither clears its bar; nothing on this edgeline
supports our line over theirs.

- The *pitch* limb survives: the material between the two routes is break facet (64.89 % of it
  >= 45 deg, 0.69 % <= 20 deg in the near-plane strip), not interior-face material continuing
  outward, so our detour does not enclose face the chord wrongly cuts away — 9.66 mm2, 2.35 %.
- The *on-surface* limb survives with a qualification: the chord is on the mesh (median 0.025 mm) but
  two of its 23 dots are 1.0-1.4 mm off it, which is the 4.16 % of its length.
- The shortfall is concentrated where the two lines differ: the 20-40 deg band of the histogram holds
  20.5 % of the patch, i.e. a rounded corner rather than a clean break, which is why the patch lands
  at 65 % and not 70 %.

### Secondary checks (run after the rule; they cannot move it)

- The triangle each line's own dots sit on, tilt off the face normal: their chord median **66.3 deg**,
  100 % of its dots >= 45 deg, **0 % <= 20 deg**; their rest median 62.3 deg. Our detour median
  **29.6 deg**, 18.2 % <= 20 deg, **0 % >= 45 deg**; our rest median 60.5 deg. Our detour is the only
  stretch of either loop whose own dots sit on material within 30 deg of the face plane; every other
  part of both loops runs on break facet.
- Distance from each line's dots to the authors' own labelled interior face: their chord median
  0.290 / p95 1.070 / max 1.470 mm; their rest 0.273 / 0.547 / 0.643; our detour 0.451 / 0.785 /
  0.816; our rest 0.381 / 1.748 / 2.730.

### Reproducibility

- Run `/data/gpfs/projects/punim2657/SfSpp/runs/20261026-0005_a21822e_p297-chord`, job 33781671,
  commit `a21822e72cc6855cc68b5faf5dc2f21364772733`, tag `p297-chord`, host spartan-login2, submitted by
  `new_run.sh` (`run.json`). Slurm time 00:06:01-00:08:47, exit 0.
- Binaries, built from `git archive` of that commit inside `pcl_191_nurbs.sif` (Release, -j8):
  `EdgeLineExtractionHeadless` md5 `cbf747dc3172fe0bbd188822df14092a`, `MeshPreprocessingHeadless`
  md5 `fb3fd055d30fb08ccce48dba7d49a879` (`out/build.json`).
  **294's edge binary was `a28d10afab2b50bbe750d599ee2b7214`, so the md5 does not match** — the identity
  of the instrument rests on something better: no build path is embedded (0 hits for the job's build
  directory in `strings`), both headless sources are byte-identical to 294's commit
  (`edgeline_extraction_headless.cpp` `f0dbfe7032d90a04412d15bd1699a703` 3739 lines,
  `mesh_processing_headless.cpp` `459dabe145056489829804292710b382` 2618 lines), and the scored row
  reproduces to the digit.
- Inputs (staged by symlink with `scripts/stage_piece.sh`; the stage's own `inputs.md5` is kept as
  `out/inputs.rep{1,2,3}.md5`): mesh `Pot_D_Piece_22_Mesh_DS.obj` `b9adb29f112c3bfe010a1bf698632fb0` (2074532 B),
  authors' `Breakline_0.pcd` `2bfacbb541c04385c8a1112613d9f637` (11580 B), `Surface_0.xyz`
  `a69d209045291316464610386987a4e2`, `Surface_1.xyz` `b284250b18eb72e9a955cb97e388dd24`, `Axis.xyz`
  `ed6313c8e165c039d7a2d81ffe84eb15`.
- Analysis: `measure297.py` `becf9d5788db70470ffbf3e5e177b5b4`, `render297.py`
  `9150b04b39c0fcf69f07b3841e83c893`, `measure297_extra.py` `669b27f89befbb0594fc55f72c2db155` — the
  committed copies are `.scratch/pota-repro/297/` on this branch. Run copies:
  `scripts/` in the run directory.
- Geometry: the staged trees were deleted by the job and counted in `out/GEOMETRY_DELETED.txt` (58 real
  files / 47.26 MB per repeat, 2 symlinks each into the read-only corpus). Kept: the two line files
  (`out/geom/authors.Bl0.pcd`, `out/geom/rep{1,2,3}/ours.Bl0.pcd`) plus our Bl1 and both surfaces
  per repeat, and the picture.
- `runs/index.tsv` carries both submits of this ticket, verdict and `human_note` left empty:
  `20261026-0004_05ae973_p297-chord` (job 33781656, died in 4 s on an unexpanded shell variable
  before doing anything — kept as the record of that submit) and this run.
- Defect found after the first number and corrected before any corrected number was read: the chord
  resolver sliced their closed loop by index range, which wrapped 200 mm of it instead of answering
  our 18 mm detour. Their loop runs opposite to our order, so the fix takes the shorter arc between
  the two nearest dots, and a segment-projection cross-check picks the same arc independently
  (200.29 mm one way against 42.79 mm the other). No threshold moved; the first analysis is kept as
  `scripts/measure297_firstrun.py` `e70d8b46764d5cf05feb6b031cb9bda7` with
  `out/measure297.firstrun.{json,txt}` and `out/png/p297_D_22_Bl0_chord.firstrun.png`.
