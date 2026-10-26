# Ticket 299 - why the authors' own bundle misses the paper on Pot D and Pot H

Status: done (accepted: on Pot D the authors' own bundle is one sherd and two joins short of their own paper at the release we pinned, and the missing sherd is explained by five pieces whose released axis contradicts their released pose -- not by D 22, which is an isolated node and contributes zero to both counts; on Pot H the gap is piece 6 plus three pieces whose pass/fail moves between replays of byte-identical input)
Working in: chat on Thinkbook16 (2026-10-26)
Branch: 299-dh-why, in /c/PR/worktrees/sfs/299
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

## Result (2026-10-26)

### 0. Method, and why the tables below can be trusted

The assembler's own scoring was replicated in Python from the run directories alone
(out/Result/T_ito_i.txt, Ground Truth/Pot_X_Piece_n_T.txt, Ground Truth/Pot_X_simple_graph.txt):
relative pose inv(GT_i)*GT_j against inv(T_i)*T_j, rotation angle arccos((tr(R)-1)/2), a pair passes
iff rotation < 0.35 rad **and** translation < 50 mm (class/data_structure.cpp:927, isSimilarTrans at
:661-680), and a piece counts as seated iff it has **at least one** correct incident GT edge
(:967-983). The replica reproduces **all six** printed pairs to the count: 22/28 + 53/66 (D authb and
rep2), 23/29 + 55/69 (D oursd), 8/11 + 9/17 (H authb and rep2), 8/11 + 11/17 (H oursd). So the
per-piece tables are the same numbers the assembler counted.

Scripts (laptop, .scratch/pota-repro/299-work/): an299.py (the replica), show299.py, edges299.py
(per-edge deg/mm), axis299.py (axis-vs-GT deviation), mk299md.py (regenerates the two tables in
section 3), normaxis299.py (dead end, section 9).

**Absolute poses are not usable and are not used below.** In every run every piece's absolute error
inv(GT_i)*T_i is 172-175 deg with 190-940 mm: the assembled pot sits a global rigid transform away
from the GT frame. That is exactly why the assembler scores relative poses. Every rotation/translation
figure in this ticket is the piece's **best incident GT edge**, i.e. the quantity the rule tests.

### 1. The arithmetic (Phase 0, acceptance 1)

out/Result/1. Acc.txt, verbatim (the label prints twice: sherds, then joins):

| run directory | sherds | joins |
|---|---|---|
| 20261026-0126_d1f1a4c_p298-Pot_D-authb | Sherd accuracy : 22 / 28 (78.5714 %) | Sherd accuracy : 53 / 66 (80.303 %) |
| 20261026-0301_d1f1a4c_p298-Pot_D-authb-rep2 | Sherd accuracy : 22 / 28 (78.5714 %) | Sherd accuracy : 53 / 66 (80.303 %) |
| 20261026-0126_d1f1a4c_p298-Pot_D-oursd | Sherd accuracy : 23 / 29 (79.3103 %) | Sherd accuracy : 55 / 69 (79.7101 %) |
| 20261026-0126_d1f1a4c_p298-Pot_H-authb | Sherd accuracy : 8 / 11 (72.7273 %) | Sherd accuracy : 9 / 17 (52.9412 %) |
| 20261026-0301_d1f1a4c_p298-Pot_H-authb-rep2 | Sherd accuracy : 8 / 11 (72.7273 %) | Sherd accuracy : 9 / 17 (52.9412 %) |
| 20261026-0126_d1f1a4c_p298-Pot_H-oursd | Sherd accuracy : 8 / 11 (72.7273 %) | Sherd accuracy : 11 / 17 (64.7059 %) |

The paper's implied integers, with the lines they come from:

- Pot D SA 82.1 % (C:/PR/papers/text/sfspp-2502.13986v1.md:351) = **23/28** = 82.1429;
  Pot D EA 83.3 % (:356) = **55/66** = 83.3333.
- Pot H SA 90.9 % (:351) = **10/11** = 90.9091; Pot H EA 88.2 % (:356) = **15/17** = 88.2353.
- The denominators are not free: Table III :312 gives 29 D sherds of which one is switched off by the
  50-point floor (section 2) = 28, and :316 gives 69 D GT edges of which piece 27's 3 leave with it
  = 66. Pot H: 11 sherds and 17 edges (:312, :316). No other integer pair on those denominators
  reproduces the percentages (23/29 = 79.31, 55/69 = 79.71).

**Observation 1 in "Why" is confirmed, with one correction.** Our own bundle does reach 23 sherds and
55 joins - but on 29/69, because it also places piece 27. Restricted to the paper's own denominators
the two arms are **identical: 22/28 and 53/66**, and they fail the same edges (section 3). So Pot D is
"the authors' released bundle is one sherd and two joins short of the authors' paper, at the same
staged-piece set and the same denominators", and the shortfall is a property of the assembled result,
not of the counting.

### 2. What is switched off, and by which rule (Phase 2b)

- **Pot D**: the block stages 29 pieces (class/data_path.h:1650-1651, SHARD_NUMBER 29, pieces
  01-29). Exactly one is switched off: **piece 27**, whose released Breakline_0 holds **48 points**,
  below the shim's floor of 50 (hpc/tools/main_pristine_batch.cpp:86, the paper's own datum rule at
  :329 "fewer than 50 points ... perimeter approximately 9cm"). The shim then zeroes that piece's
  row and column in the GT graph (:147-155) and drops it from right_sherd (:236-249), which is where
  the printed denominator 28 and 66 come from. It is the same rule on the same file in both arms, so
  the denominators are reproduced exactly.
- **Pot H**: all 11 staged, **nothing switched off** (every H Breakline_0 has 73-218 points).
- No piece in either pot was switched off for an empty axis file.
- **Piece 22 is on, and is a special case**: it passes both filters, is counted in the 28, and is an
  **isolated node** in Pot_D_simple_graph.txt (degree 0). By the seating rule (:967-983) it can never
  be scored as seated. So the paper's 28 contains one piece that is unscorable by construction, and
  the paper's 23/28 means 23 of the 27 scorable pieces. We reach 22 of those 27.

### 3. Per-piece placement (Phase 1, acceptance 2)

The rule, from the source: data_structure.cpp:927 sets rad_threshold = 0.35 (20.05 deg) and
t_threshold = 50.0 (mm); isSimilarTrans (:661-680) passes a pair iff both hold; and :967-983 sets
right_sherd[i] iff piece i has at least one **correct directed GT edge**. A piece with a good pose but
no passing incident edge is not seated, and a piece with three passing edges still counts once.

"best" below is the minimum-score incident GT edge (rotation deg / translation mm); OK means that edge
passes and the piece is therefore seated. Off = switched off by the 50-point floor. Axis dev is the
angle between the released Axes/ direction (rotated by that piece's released GT pose) and the pot's own
principal axis: section 6 uses it.

#### Pot D (29 staged, 1 off)

| piece | GT deg | axes | axis-GT dev min/max deg | authb best | oursd best | authb-rep2 best |
|---|---|---|---|---|---|---|
| 1 | 7 | 1 | 2.5 / 2.5 | 0.32 / 2.88 OK | 0.47 / 3.47 OK | 0.32 / 2.95 OK |
| 2 | 8 | 1 | 2.6 / 2.6 | 0.30 / 3.12 OK | 0.39 / 2.68 OK | 0.58 / 4.17 OK |
| 3 | 8 | 1 | 3.7 / 3.7 | 1.06 / 4.11 OK | 0.91 / 3.22 OK | 0.96 / 4.24 OK |
| 4 | 4 | 1 | 1.4 / 1.4 | 0.94 / 3.80 OK | 0.57 / 2.22 OK | 0.94 / 4.03 OK |
| 5 | 6 | 1 | 2.1 / 2.1 | 0.64 / 1.21 OK | 0.61 / 1.96 OK | 0.54 / 1.21 OK |
| 6 | 6 | 1 | 1.6 / 1.6 | 0.46 / 2.07 OK | 0.50 / 2.43 OK | 0.40 / 1.49 OK |
| 7 | 6 | 1 | 1.5 / 1.5 | 1.07 / 6.27 OK | 0.40 / 3.17 OK | 0.79 / 4.75 OK |
| 8 | 7 | 1 | 3.2 / 3.2 | 0.92 / 1.95 OK | 0.38 / 2.19 OK | 0.92 / 1.90 OK |
| 9 | 6 | 1 | 2.0 / 2.0 | 0.68 / 3.16 OK | 0.62 / 2.93 OK | 0.66 / 2.90 OK |
| 10 | 7 | 1 | 1.4 / 1.4 | 0.11 / 2.04 OK | 0.30 / 0.81 OK | 0.15 / 2.01 OK |
| 11 | 7 | 1 | 3.2 / 3.2 | 0.81 / 1.65 OK | 0.83 / 1.02 OK | 0.64 / 2.30 OK |
| 12 | 5 | 1 | 2.8 / 2.8 | 0.94 / 5.76 OK | 0.79 / 4.83 OK | 0.95 / 5.89 OK |
| 13 | 7 | 1 | 0.4 / 0.4 | 0.22 / 0.75 OK | 0.31 / 3.10 OK | 0.18 / 0.78 OK |
| 14 | 5 | 1 | 2.4 / 2.4 | 1.10 / 7.29 OK | 0.80 / 4.95 OK | 0.33 / 2.04 OK |
| 15 | 5 | 1 | 3.8 / 3.8 | 1.08 / 6.91 OK | 0.84 / 5.97 OK | 0.92 / 6.12 OK |
| 16 | 4 | 1 | 1.9 / 1.9 | 1.10 / 8.84 OK | 0.80 / 6.09 OK | 0.33 / 2.48 OK |
| 17 | 4 | 2 | 4.6 / 78.8 | 1.23 / 10.08 OK | 1.36 / 10.54 OK | 1.07 / 9.04 OK |
| 18 | 3 | 1 | **36.3 / 36.3** | 153.12 / 895.62 | 153.56 / 896.24 | 76.78 / 273.12 |
| 19 | 3 | 1 | 2.1 / 2.1 | 0.23 / 2.10 OK | 0.62 / 4.37 OK | 0.17 / 1.99 OK |
| 20 | 4 | 1 | 11.3 / 11.3 | 0.30 / 2.74 OK | 1.10 / 2.42 OK | 0.68 / 3.71 OK |
| 21 | 4 | 2 | 24.0 / 71.0 | 1.50 / 5.35 OK | 0.93 / 6.80 OK | 1.39 / 5.36 OK |
| 22 | **0** | 1 | GT transform absent | no GT edge exists | no GT edge exists | no GT edge exists |
| 23 | 4 | 1 | 7.7 / 7.7 | 0.46 / 2.12 OK | 0.50 / 1.52 OK | 0.40 / 1.98 OK |
| 24 | 3 | 4 | 2.7 / 61.7 | 1.58 / 13.25 OK | 0.81 / 5.99 OK | 2.31 / 18.79 OK |
| 25 | 3 | 1 | **37.8 / 37.8** | 107.47 / 519.59 | 110.66 / 565.17 | 175.76 / 802.07 |
| 26 | 3 | 2 | **72.0 / 74.7** | 163.54 / 974.37 | 162.17 / 969.76 | 163.02 / 974.89 |
| 27 | 3 | 2 | 7.9 / 85.8 | off (48-point Breakline_0) | 1.79 / 14.28 OK | off |
| 28 | 3 | 2 | **10.0 / 27.8** | 164.43 / 754.87 | 170.59 / 559.75 | 175.98 / 764.15 |
| 29 | 3 | 2 | **54.6 / 75.3** | 107.47 / 462.95 | 125.77 / 845.57 | 78.49 / 367.88 |

Seated: authb 22/28, oursd 23/29, rep2 22/28. **Not seated in all three arms: 18, 22, 25, 26, 28, 29**
(22 unseat-able by construction; 27 is absent from the authb denominators and seats at 1.79 deg /
14.28 mm when staged, which is the only numerator difference between the arms).

Failed edges, Pot D (of 66 scored): authb and rep2 fail the same **13** - 03-26 163.54/821.32,
03-28 164.42/861.11, 07-29 87.52/426.23, 08-18 153.12/554.76, 10-18 153.26/197.58,
12-28 164.43/659.71, 13-18 153.16/799.83,
13-26 163.42/438.49, 14-28 163.65/596.35, 15-25 108.76/441.74, 16-26 164.68/784.33,
24-25 108.69/375.55, 25-29 107.47/519.59 (66 - 53 = 13). oursd fails those 13 plus
27-29 125.77/337.84, while 02-27 1.79/15.07 and 20-27 1.97/15.97 pass (69 - 55 = 14).
**No D failure is a near miss**: the smallest failed rotation in either D run is 76.78 deg, nearly
four times the 20.05 deg bar, so no threshold slack would seat any of them. Between the two
identical-input authb runs the piece-18 family moves from 153.12-153.26 deg / 554-897 mm to
76.78-77.13 deg / 172-278 mm: the same failed edges, half the rotation error.

One orientation note. The rule tests directed pairs, and the two directions of one edge give the same
rotation angle but not the same translation term, so the per-piece table - which quotes the pair
(piece, its neighbour) - can print a different millimetre figure for an edge than the list above, which
quotes the pair (lower piece, higher piece). Example, Pot D authb, edge 08-18: 554.76 mm in the
orientation listed above, 895.62 mm in the piece-18 orientation used in the table.

#### Pot H (11 staged, none off)

| piece | GT deg | axes | axis-GT dev min/max deg | authb best | oursd best | authb-rep2 best |
|---|---|---|---|---|---|---|
| 1 | 5 | 1 | 1.1 / 1.1 | 1.41 / 2.51 OK | 0.99 / 4.06 OK | 1.37 / 2.72 OK |
| 2 | 4 | 1 | 1.5 / 1.5 | 1.27 / 5.04 OK | 2.19 / 8.68 OK | 1.17 / 3.97 OK |
| 3 | 4 | 1 | 1.4 / 1.4 | 0.88 / 4.06 OK | 1.05 / 2.29 OK | 0.83 / 3.41 OK |
| 4 | 5 | 1 | 6.6 / 6.6 | 1.28 / 4.90 OK | 0.98 / 8.69 OK | 1.17 / 4.97 OK |
| 5 | 2 | 2 | 2.0 / 57.0 | 1.03 / 4.09 OK | 0.99 / 5.85 OK | 1.02 / 3.39 OK |
| 6 | 2 | 3 | **67.3 / 78.1** | 65.73 / 152.35 | 135.14 / 763.60 | 66.26 / 151.70 |
| 7 | 2 | 2 | 7.3 / 45.4 | 0.88 / 5.79 OK | 1.05 / 6.51 OK | 0.83 / 5.17 OK |
| 8 | 2 | 3 | 8.0 / 31.1 | 58.65 / 361.99 | 0.70 / 5.20 OK | 9.68 / 72.88 |
| 9 | 3 | 6 | 9.0 / 88.4 | 5.35 / 2.85 OK | 24.63 / 172.73 | 6.85 / 10.99 OK |
| 10 | 3 | 1 | 4.2 / 4.2 | 10.45 / 73.19 | 0.71 / 3.21 OK | 9.18 / 63.90 |
| 11 | 2 | 3 | **29.7 / 51.7** | 5.35 / 15.25 OK | 24.63 / 185.77 | 6.85 / 14.85 OK |

Seated 8/11 in each arm, but **not on the same pieces**: authb 6, 8, 10; rep2 6, 8, 10 (identical
inputs, identical result); oursd 6, 9, 11. Only piece 6 fails in all three.

Failed edges, Pot H (of 17): authb - 01-06 65.73/201.87, 02-06 67.43/519.58, 02-11 97.19/578.53,
04-09 95.89/555.01, 04-10 104.23/593.79, 07-08 58.65/367.41, 08-10 152.54/776.28, 09-10 10.45/81.20.
rep2 - the same eight, but 07-08 at 9.68/65.82 and 09-10 at 9.18/69.58, i.e. **translation-only near
misses** (1.3-1.5x the 50 mm bar, rotation well inside 20 deg); 08-10 107.15/588.07. oursd - six:
01-06 137.20/607.20, 02-06 135.14/404.37, 02-11 80.93/328.63, 04-09 61.30/326.56,
09-10 61.22/408.72, 09-11 24.63/172.73.

Note that on H the graph does not close: pieces 9 and 11 are each **seated** through the single edge
09-11 (5.35 deg / 15.25 mm) while their other edges 04-09 (95.89 deg) and 02-11 (97.19 deg) fail. The
assembly is a spanning tree, one good edge is enough, and a piece can be seated while two of its three
GT joins are wrong. That is why 8/11 sherds comes with only 9/17 joins.

### 4. Candidate (a): D 22's missing ground-truth transform - REFUTED (acceptance 4)

Ground Truth/Pot_D_Piece_22_T.txt is indeed absent while the other 28 D transforms are present, and
Trans::Read (class/data_structure.cpp:633-659) leaves the identity pose with no error printed. But
**the piece contributes nothing to either count**, for a reason that has nothing to do with the missing
file: piece 22 is an **isolated node** in Ground Truth/Pot_D_simple_graph.txt - its row and column are
all zero, degree 0. Every comparison in CountResult iterates over GT graph entries (:944-965), so no
term involves piece 22; it enters total_sherd (:933-936) because it is on, and it can never satisfy the
seating rule (:967-983, which requires a correct incident edge). Both the numerator effect and the
denominator effect of its transform are therefore **exactly zero**.

Its seeded pose is not degenerate either - it differs from identity by 56.70 deg / 444 mm - but no
choice of transform for it can move 22/28 or 53/66 by one. It is also not the paper's one extra sherd:
a correct pose for an isolated node still is not a correct incident GT edge.

### 5. Candidate (b): which pieces are switched off - ANSWERED in section 2

One piece in two pots, by the paper's own 50-point rule, on the authors' own file, identically in both
arms; the printed denominators are reproduced exactly (28, 66, 11, 17). No discrepancy to explain here.

### 6. Candidate (c): Pot H's shared side, and the axis files (both pots)

Every H piece has a mesh, an axis, both breaklines, a GT transform and a row in the GT graph, and the
GT graph's 17 undirected edges match the 17 the paper's EA denominator implies (:316). Our own H runs
also printed Total number 485 and Total number pruned 232, **equal to the paper's :317 485 and :318
232**, so the pairwise screening stage matches the paper on Pot H exactly.

The one shared input that is measurably inconsistent is the **axes**. Test: rotate each piece's
released Axes/Pot_X_Piece_NN_Axis.xyz direction by that piece's released GT rotation and compare it
with the pot's single principal axis (SVD over single-axis pieces); a wheel-thrown pot has one axis, so
this should be a few degrees. Result per pot (pieces measured / median / max / pieces above 15 deg):

- **B 9 / 3.61 / 11.83 / none**, **E 31 / 2.25 / 13.69 / none**, **G 7 / 1.59 / 2.98 / none** - the
  three pots whose Table V scores reproduce at 100/100 have **no piece above 15 deg in 47 pieces**.
- **D 28 / 3.01 / 71.96**: above the cut are 18 (36.3), 21 (24.0-71.0), 25 (37.8), 26 (72.0-74.7),
  29 (54.6-75.3); 20 is 11.3 and 28 is 10.0-27.8, below the cut but still the largest of the rest.
- **H 11 / 6.61 / 67.29**: 6 (67.3-78.1 on **all three** candidate axes), 11 (29.7-51.7 on all three);
  5, 7, 8, 9 have one good candidate and one bad (5: 2.0/57.0, 7: 7.3/45.4, 8: 8.0/31.1, 9: 9.0/88.4).

Mechanism, from the source: the piece's own axis is the frame it is placed in
(class/reconstruction.cpp:66-123, AxisAlignment, called during matching at class/ranking_system.cpp:781
and for the root piece at :1735), and for a multi-axis piece the matcher tries every axis pair
(class/feature_matching.cpp:1481-1482 and :1551-1552 set axis_index_x_ / axis_index_y_), with ICP
refinement downstream (feature_matching.cpp:1650 into reconstruction.cpp:1113). So an inconsistent axis
need not corrupt a pose directly - D piece 21, minimum deviation 24.0 deg, is placed to 1.50 deg /
5.35 mm - but it biases the initial frames and which pairs the screen keeps. **Which of the two
released files is the wrong one is not determined here** (section 8).

### 7. Candidate (d): does the pin postdate the paper - REFUTED

In sfs_main/archive_2025_sfs_modified_src (the pin 9195c01) the history is ab85ea3 2025-02-06 12:09
"first commit", dd27c09 2025-02-06 13:21 "Remove redundant function at main.cpp", 9a2756c 2025-02-06
13:49, 1a16d8d 2025-02-06 13:50, 99ae705 2025-02-21, **9195c01 2025-03-06 14:18 "Update README.md"**.
git diff --stat 1a16d8d 9195c01 is "README.md | 3 ++-", 1 file changed, and the diff over class/ and
main.cpp is **empty**: the code compiled at the pin is the 2025-02-06 pre-release code, unchanged
through the March README commit. A later fix therefore cannot explain the gap, and 9195c01 is
consistent with the paper's own release (2502.13986v1, February 2025).

Also checked and dismissed as a shim artefact: NO_RIM_INFO / NO_BASE_INFO. Upstream main.cpp:32-33 has
rim information **on** (//#define NO_RIM_INFO) and base information **off** (#define NO_BASE_INFO), and
the INFRA shim hpc/tools/main_pristine_batch.cpp:54-55 is byte-for-byte the same pair, with both ifdef
blocks at :100-110. The shim does not change what the pipeline reads.

### 8. Named cause per pot (acceptance 3)

**Pot D - named cause: one shared pose input is defective, and it is what caps the count at 22 of 28.**
The failure set is not a draw and not a threshold effect: three arms and two byte-identical replays all
fail exactly pieces 18, 25, 26, 28, 29 (and 22 structurally), every one of them by 76-176 deg, i.e.
several times the 20.05 deg bar. Those five are the five pieces whose released axis list contains no
candidate consistent with their released GT pose (minimum deviations 36.3, 37.8, 72.0, 10.0, 54.6 deg),
while every other D piece sits at 0.4-11.3 deg and all 47 pieces of B+E+G - the pots that do
reproduce - sit at or below 13.7 deg. The paper's 23/28 needs **exactly one** of those five to be
placed. Not explained by this: piece 28, whose best candidate is only 10.0 deg off, fails as grossly as
the rest (164 deg), so the axis story is incomplete for that piece alone.
**Still standing, and the one measurement that separates them**: *which* of the two released files is
wrong (axes or GT transforms). The separating measurement is an input-only swap: replace one piece's
Axes/..._Axis.xyz direction with the direction its GT pose implies (R_GT^T * pot axis) in a throwaway
copy of the staged inputs and re-assemble that pot; if the piece seats, the axis file is the defect, if
it still fails, the GT pose is. Five pieces, five short single-pot jobs, no algorithm, threshold or
assembler change - each needs a new run directory and index row.

**Pot H - named cause: one genuine shared defect (piece 6) plus a margin too thin to survive the
pipeline's own run-to-run spread.** Piece 6 fails in all three arms and is the worst axis outlier in
the pot (67-78 deg on all three candidates). Everything else in H is decided within a few millimetres
of the 50 mm bar and does not hold still per piece: between the two byte-identical authb runs
(out/inputs.md5 identical, one unique md5 over 78 lines) piece 8's edge error moved from
58.65 deg / 361.99 mm to 9.68 deg / 72.88 mm - from a gross miss to a 1.46x translation near miss -
while the *count* stayed 8/11. In rep2 two of the three failures are translation-only (piece 8 at
72.88 mm = 1.46x the bar, piece 10 at 63.90 mm = 1.28x; piece 10 also fails as 10.45 deg / 73.19 mm in
rep1). The paper needs 10/11 and 15/17, i.e. two more pieces and six more joins than our best run.
So pot H is not explained by one broken input: it is piece 6 plus two or three pieces whose membership
in the failing set changes between replays of the same bytes. Note also that H's 9/17 joins coexists
with 8/11 sherds because one good edge seats a piece (section 3), so the join count is the sensitive
number here.
**The one measurement that separates "margin" from "structural"**: a third identical run of the same
authb bundle (one job, one new run directory, one index row). If the failing set moves again while the
count stays 8/11, the paper's two pieces are inside our own run-to-run band and no input defect is
needed to explain the gap; if it holds at {6, 8, 10} in three runs, the cause is structural and the next
measurement is the axis swap of the D entry above applied to pieces 6, 8 and 11.

### 9. Dead ends, recorded so they are not repeated

- **Breakline seam distance under the GT poses** cannot arbitrate a GT pose: over all GT edges the
  median of the one-way median nearest-neighbour distance is 57.73 mm on D and 36.46 mm on H (max
  128.41 / 58.68), with a fraction under 2 mm of only 0.05-0.5 even on edges that assemble to 1 deg.
  Dropped.
- **Fitting the revolution axis from the breakline strip's normals** (smallest singular vector of the
  normal scatter matrix) does not work: the estimate scatters 5-90 deg from *both* candidate axes even
  on pieces where the axis file and the GT pose agree within 2 deg. A narrow strip does not constrain a
  surface of revolution. If an independent axis estimate is wanted, it must use the whole surface
  (Point/ cloud or Surface_0 mesh), not the breakline.

### 10. Nondeterminism on identical input (context for any later comparison)

out/inputs.md5 is identical between each pair of replays (203 lines for D, 78 for H, one unique md5),
yet the geometric screen returned 886 pruned pairs in D-rep1 against **888** in D-rep2, and 232 against
**233** on H, and individual poses moved by tens of degrees (D 18: 153.12 vs 76.78 deg; H 8: 58.65 vs
9.68 deg). Only the two printed counts happened to repeat. Any future claim of the form "our change did
not alter the result" must therefore rest on the counts plus a per-piece tolerance measured in the same
session, not on a single re-run agreeing.

### 11. Rebuilding the evidence (nothing large is kept)

Everything above was computed on the laptop from files pulled off Spartan once; the pull is cheap and
reproducible, and no copy of the corpus is committed. From /tmp on Spartan:

- run results: for each of the six run directories, out/Result/1. Acc.txt and out/Result/T_*to_*.txt
  under /data/gpfs/projects/punim2657/SfSpp/runs/<runid>/;
- ground truth: Ground Truth/Pot_D_Piece_*_T.txt, Pot_H_Piece_*_T.txt, Pot_D_simple_graph.txt,
  Pot_H_simple_graph.txt under /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/
  (plus Pot_B/E/G_*_T.txt for the control pots);
- axes: Axes/Pot_{B,E,G,D,H}_Piece_*_Axis.xyz (93 files, ~50 KB);
- breaklines: Breaklines/Pot_{B,E,G,D,H}_Piece_*_Breakline_0.pcd (93 files, ~180 KB);
- input identity: out/inputs.md5 in each run directory (203 lines for D, 78 for H).

Then run an299.py, edges299.py, axis299.py, mk299md.py in this directory with the bundled python
(C:\Users\hermi\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe). The extracted
copy is deleted after use; only the scripts are committed.

## 2026-10-26 — two corrections from ticket 301 (its numbers stand; these two do not)

1. **This ticket's per-piece translation column contradicts its own failed-edge list.** For the four pieces
   that reproduce, section 3 quotes 18 `895.62` mm where the edge list says 554.76, 26 `974.37` vs 821.32,
   28 `754.87` vs 659.71, 29 `462.95` vs 519.59. The degrees agree in every case. Ticket 301 re-ran all five
   and reproduced the **edge list** to 0.12 deg or better (18 153.07 vs 153.12, 26 163.42 identical,
   28 164.43 vs 164.43, 29 87.40 vs 87.52), so the edge list is right and the per-piece column is the typo
   carrier. Cite the edge list.
2. **The axis-deviation correlation is weaker than section 8 reads, and section 10's nondeterminism is worse
   than two replays showed.** Five control arms of byte-identical staged input (same `out/inputs.md5`,
   203 staged entries, `Total number : 2445` in all five) disagreed: pruned 888 / 890 / 892 / 896 / 890,
   sherds 22 or 23 of 28, joins 53 or 55 of 66. **Piece 25 seats (3.14 deg / 19.48 mm) in four of the ten arms
   and fails at 104-157 deg in six, with its own axis untouched** — so for that piece the axis does not decide
   seating at all, which makes it a third counter-example beside 21 and 28. Per-piece verdicts: ticket 301.
