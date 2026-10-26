# Ticket 299 - why the authors' own bundle misses the paper on Pot D and Pot H

Status: todo
Working in: unassigned
Branch: unassigned
Answers: E1
Created: 2026-10-26 by the coordinating session, on the conservator's instruction
("can you check what caused author's D and H didn't get their result on paper?")

## Why

Ticket 298 assembled all ten pots twice. On eight pots the AUTHORS' released bundle reproduces
Table V exactly. On two it does not, and both were re-run into fresh directories with identical
results, so the gap is a property of the release at the commit we pinned, not of one run:

| pot | paper (Table V, C:/PR/papers/text/sfspp-2502.13986v1.md:351 SA, :356 EA) | authors' bundle, our runs | our bundle, our runs |
|---|---|---|---|
| D | 82.1 / 83.3 | 78.5714 (22/28) / 80.303 (53/66) | 79.3103 (23/29) / 79.7101 (55/69) |
| H | 90.9 / 88.2 | 72.7273 (8/11) / 52.9412 (9/17) | 72.7273 (8/11) / 64.7059 (11/17) |

**Two observations the lead already made, to be confirmed or refuted, not assumed:**

1. **The paper's D numbers are exactly 23/28 and 55/66.** 23/28 = 82.14, 55/66 = 83.33. Our OWN
   bundle reaches 23 sherds and 55 joins (over 29 and 69) - i.e. the paper's raw counts - while the
   authors' bundle reaches 22 and 53 on the same denominator 28. If that arithmetic is right, Pot D
   is not "everyone is short of the paper", it is "the authors' released bundle is one sherd and two
   joins short of their own paper, and ours matches it".
2. **On Pot H the shortfall is arm-independent**: both arms give 8/11 sherds. When two different
   breakline sets give the same sherd count, the cause is far more likely to be in something both
   arms share (meshes, axes, ground-truth graph/transforms, assembler behaviour) than in the lines.

## Facts already established (do not re-derive; verify if you rely on them)

- Pinned assembler `/opt/sfs-pristine` = upstream `9195c0167e2077a564bd7c91156063252feeb506` +
  the INFRA shim `hpc/tools/main_pristine_batch.cpp`; binary md5 `0fd8d707ceb3f9cffd08d8951c43ccda`
  in every 298 arm. Beam k=5, b=3 (paper :344).
- `hpc/tools/main_pristine_batch.cpp:78-82`: a piece whose axis file reads empty is switched off
  silently. `:86`: a piece whose `Breakline_0` has fewer than 50 points is switched off silently
  (this is the paper's own datum rule, :329 "fewer than 50 points ... perimeter approximately 9cm").
- Pot D's block declares SHARD_NUMBER 29 and the corpus holds 32 D meshes; Pot H's block declares
  11 and the corpus holds 11. Pot H has ALL 11 GT transforms; Pot D has 28 of 29 and
  `Ground Truth/Pot_D_Piece_22_T.txt` is MISSING, and `Trans::Read` turns an absent transform into
  an identity pose (`data_structure.cpp:633`) - so D 22's reference pose may be wrong by construction.
- GT transforms are named `Ground Truth/Pot_<X>_Piece_<n>_T.txt` with NO zero padding
  (`Pot_C_Piece_1_T.txt`), while meshes, axes and breaklines ARE zero padded
  (`Pot_D_Piece_22_Mesh_DS.obj`, `Axes/Pot_D_Piece_22_Axis.xyz`). Axes are `.xyz`, not `.txt`.
- Each arm's run directory holds `out/Result/1. Acc.txt` (two "Sherd accuracy" lines: the first is
  sherds, the second is joins) plus `T_0to_0.txt ... T_nto_n.txt`, i.e. ONE transform per staged
  piece. Those transforms are the seated poses and are the evidence this ticket needs.
- Run directories (Spartan): `/data/gpfs/projects/punim2657/SfSpp/runs/`
  `20261026-0126_d1f1a4c_p298-Pot_D-authb`, `...-Pot_D-oursd`, `...-Pot_H-authb`,
  `...-Pot_H-oursd`, and the repeats `20261026-0301_d1f1a4c_p298-Pot_D-authb-rep2`,
  `...-Pot_H-authb-rep2`. Every one has an index row; do not add duplicates.

## What to do

**Phase 0 - reproduce and pin the arithmetic.** Quote both score lines from each of the four run
directories (six with repeats). Confirm or correct the two observations above from the paper text
(C:/PR/papers/text/sfspp-2502.13986v1.md:329, :345-356) and from the numbers. State the paper's
implied integer counts for D and H.

**Phase 1 - per-piece placement, both pots, both arms.** For each arm of D and H, map each staged
index to its piece id (the block's `file_path`/`gt_graph_path` arrays in the shim, and/or
`out/links.tsv` and `out/selector.txt` in the run dir), then compare each piece's seated transform
`T_ito_i.txt` against its GT transform. Report per piece: rotation error (deg) and translation error
(mm), and classify seated / misplaced by the ASSEMBLER'S OWN criterion - read how it counts, cite the
file:line (`data_structure.cpp`), do not invent a threshold. Deliver a table per pot and arm.

**Phase 2 - test the candidate causes, cheapest first.** Each gets a stated test and a verdict:

- (a) **D 22's missing GT transform.** Is D 22 one of the pieces the assembler counted as not
  seated? If its reference pose is an identity, does the seated pose differ from identity, and by
  how much? This is the one-sherd hypothesis for D (22 vs the paper's 23).
- (b) **Which pieces are switched off and why.** For D and H, list every piece switched off, by
  which rule (empty axis, the 50-point floor, the block's own `shard_on_off`, a missing file), with
  the number that triggered it. Compare the resulting active-piece count with the denominator the
  assembler actually printed.
- (c) **Pot H's arm-independence.** Since both arms give 8/11, test the shared side: does every H
  piece have a mesh, an axis, both breaklines, a GT transform and a row in the GT graph? Is the GT
  graph's edge count consistent with the 17 the EA denominator implies? Is any H mesh inconsistent
  with its point cloud or axis (e.g. a piece whose mesh is a different piece's, or an axis that is
  nearly parallel to the plane)? Name what is wrong with the two (or three) H pieces that fail in
  BOTH arms.
- (d) **The commit question.** The paper's own numbers were produced at some upstream commit; the
  pin is `9195c016`. If `git log` in the pinned tree shows fixes after the release used for the
  paper (search for the seating/GT bookkeeping in `data_structure.cpp`, `class/`), say so with the
  commit ids. This is evidence only - do not change the pin.

**Phase 3 - say what would settle it** if the cause is still ambiguous: the one measurement that
would decide between the remaining candidates, and what it would cost.

## Constraints

- **No algorithm, threshold, weight, ordering or assembler change.** This ticket explains a number;
  it does not fix anything. Do not re-run the campaign.
- Re-using the existing run directories is the default. If one extra measurement truly needs a job,
  it goes in a new run directory under `SfSpp/runs/` with `run.json` + `submit.sbatch` + `logs/` +
  `out/` and its own `index.tsv` row (verdict and human_note left EMPTY for the lead).
- Heavy work on Spartan compute nodes only; the laptop reads logs and runs `check_*.py` gates.
- Never `build.sh --target nurbs` (it compiles the pre-247 duplicate at
  `SfSpp_preprocessing/original_nurbs_preprocessing/`). If you must build, use
  `git archive <commit>` + cmake + make inside `pcl_191_nurbs.sif`, as `.scratch/pota-repro/294/submit294.sbatch`
  does.
- Geometry produced by a measurement job is deleted on the way out with a counted record; nothing
  large persists.
- Write results into this ticket; commit on your branch only; leave Status at in-progress for the
  lead.

## Acceptance

1. Both score lines quoted from every D and H run directory, and the paper's implied integer counts
   stated.
2. A per-piece table per pot per arm: piece id, rotation error, translation error, seated or not by
   the assembler's own rule with the file:line that defines it.
3. A named cause per pot, or an explicit "not determined" naming the candidates still standing and
   the measurement that would separate them.
4. D 22's missing transform answered one way or the other, with its effect on the count stated.
5. Any claim about the paper's numbers carries the paper's line number.

## Needs-eye

none - this ticket produces numbers and tables, not geometry.
