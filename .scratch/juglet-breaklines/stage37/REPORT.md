# Ticket 37 — adaptive spacing becomes the default, and the regions under the floor

Branch \`37-adaptive-default-and-the-regions-under-the-floor\`. Answers: U19, E1.
Evidence only in this file: every number below is read from a file the job wrote in one of the two
run directories, or from the instrument's own output over those files. No verdicts.

## 0. What ran

| run dir | job | name | state | elapsed | cells | commit |
|---|---|---|---|---|---|---|
| \`/data/gpfs/projects/punim2657/SfSpp/runs/20261027-1404_c16e274_t37-adaptive-default\` | 33886175 | t37phase1 | COMPLETED, ExitCode 0:0, 8 cpus, spartan-bm081 | 00:04:56 | 55 | c16e274 |
| \`/data/gpfs/projects/punim2657/SfSpp/runs/20261027-1420_c6f6491_t37-prefigure\` | 33886571 | t37phase2 | COMPLETED, ExitCode 0:0, 8 cpus, spartan-bm197 | 00:01:33 | 16 | c6f6491 |

Both jobs ran on compute nodes only (partition \`sapphire\`, \`nodes=1\`, \`ntasks=1\`, \`cpus-per-task=8\`).
Three-job budget: **2 jobs used**, the third is unspent.

\`\`\`
33886175  t37phase1  COMPLETED  00:04:56  0:0  8  spartan-bm081
33886571  t37phase2  COMPLETED  00:01:33  0:0  8  spartan-bm197
\`\`\`

Binaries, both 1582080 bytes:

\`\`\`
orig md5=38b67513a1e1955e86ff015c878f5531  commit 5bdaff656f7aa683d5d2bc66f7c3fc2e6c31986f  (pre-change)
new  md5=180e68467eac391279675fdc3ffedfe1  commit c16e2743965a6b30afe78db63a7dd0b8f420b19f
      the phase-2 job rebuilt it from c6f6491 and got the same md5
\`\`\`

## 1. Part A — the change

\`mesh_processing_headless.cpp:4365\`: \`std::string spacingPolicy = "piece";\` (was \`"fixed"\`), plus the
9-line comment at \`:4356-4364\` beside the defaults. \`SFS_SPACING_SAMPLES\` is untouched (already 200 at
\`:4360\`), \`SFS_COUNT_SCALE\` is untouched (off). \`SFS_SPACING_POLICY=fixed\` still overrides at \`:4366\`.

\`\`\`
$ git diff --stat main...HEAD -- mesh_processing_headless.cpp
 mesh_processing_headless.cpp | 10 +++++++++-
 1 file changed, 10 insertions(+), 1 deletion(-)
\`\`\`

No second default exists: \`grep -n "spacingPolicy\|g_effectiveSpacingMM"\` finds only \`:1234\` (declaration),
\`:1422\` (a comment), \`:3722\` (the status json), \`:4528-4529\` (json fields) and the \`:4355-4385\` block.

## 2. Proof 1 — \`SFS_SPACING_POLICY=fixed\` reproduces the pre-change binary

AFIX = pre-change binary (5bdaff6) + \`SFS_SPACING_POLICY=fixed\`; BFIX = this ticket's binary + the same
switch. md5 of \`<piece>_SampledWithNormals.ply\`, from \`phase1/out/proof1.md5.tsv\`:

| piece | orig md5 | bytes | new md5 | bytes | |
|---|---|---|---|---|---|
| Juglet_Piece_1 | ab38ff7dde0f52b3fc051196b993e8f8 | 1079873 | ab38ff7dde0f52b3fc051196b993e8f8 | 1079873 | IDENTICAL |
| Juglet_Piece_3 | 122b2fbbc7356c8305cff5b0d8699958 | 108396 | 122b2fbbc7356c8305cff5b0d8699958 | 108396 | IDENTICAL |
| Juglet_Piece_7 | cadba02ac15b5b402d48142abcca98d6 | 314641 | cadba02ac15b5b402d48142abcca98d6 | 314641 | IDENTICAL |
| Pot_A_Piece_01 | b58f583996c154243ca6d41d3149f597 | 6056071 | b58f583996c154243ca6d41d3149f597 | 6056071 | IDENTICAL |
| Pot_A_Piece_02 | 14dbb68ed0fe14fba5a419208f4a2cf1 | 3537421 | 14dbb68ed0fe14fba5a419208f4a2cf1 | 3537421 | IDENTICAL |
| Pot_A_Piece_07 | 29536bde341dd14e22f11b5852eb75ee | 611993 | 29536bde341dd14e22f11b5852eb75ee | 611993 | IDENTICAL |
| Pot_A_Piece_08 | d60db59e9fe0d76e8581067da96aa97b | 548385 | d60db59e9fe0d76e8581067da96aa97b | 548385 | IDENTICAL |

7 of 7 pieces identical. Surface PLY are never compared by md5 anywhere in this work: the mesh stage
draws 30 unseeded ray casts (\`mesh_processing_headless.cpp:1526-1527\`), so surfaces are compared by
sorted point set and by count throughout (see \`out/surfaces34.tsv\`).

## 3. Proof 2 — no environment at all reproduces ticket 36 arm B

Arm A = the new shipped default, environment empty. Reference = ticket 36 arm B
(\`runs/20261028-0013_0a53dee_t36-adaptive-spacing-r2/out/cells36.tsv\`), from \`phase1/out/proof2.tsv\`:

| piece | arm A surf0 / surf1 | t36 arm B surf0 / surf1 | |
|---|---|---|---|
| Juglet_Piece_1 | 10800 / 15780 | 10800 / 15780 | IDENTICAL |
| Juglet_Piece_5 | 229 / 2317 | 229 / 2317 | IDENTICAL |
| Juglet_Piece_7 | 1753 / 1997 | 1753 / 1997 | IDENTICAL |
| Pot_A (8 of 8 pieces) | two-surface on 01,02,03,04,05,06,07,08 | 8 of 8 | 8 of 8 |

## 4. Part B — the floor-capped arm, existing switches only

Arms (all on the new binary):
\`A\` = no environment; \`B\` = A + \`SFS_SINGLE_CLUSTER=write\`;
\`C\` = B + \`SFS_COUNT_SCALE=auto SFS_FLOOR_CEILING=0.005\`; \`D\` = \`SFS_SPACING_POLICY=fixed\`.
The pipeline's own counts, as printed (\`[FLOOR-23]\` gives \`floor\` and \`from\`), from
\`phase1/out/cells37_table.tsv\` (55 rows; the 9 pieces the ticket names are repeated here):

| arm | piece | S mm | npts | clusters pre | post | sizes post-floor | floor | from | capped | outcome | surf0/surf1 pts | diag | cov2mm | fold deg |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | Juglet_Piece_1 | 0.338049 | 23077 | 13 | 7 | 4812,9032,752,373,338,205,59 | 50 | 50 | no | two | 10800 / 15780 | 54.410 | 0.6599 | 1.631 |
| B | Juglet_Piece_1 | 0.338049 | 23077 | 13 | 7 | 4812,9032,752,373,338,205,59 | 50 | 50 | no | two | 10800 / 15780 | 54.410 | 0.6599 | 1.631 |
| C | Juglet_Piece_1 | 0.338049 | 23077 | 7 | 7 | 4812,9032,373,338,236,205,160 | 115 | 158 | yes | two | 10800 / 15780 | 54.410 | 0.6599 | 1.631 |
| D | Juglet_Piece_1 | 0.600000 | 14546 | 22 | 18 | 626,3489,429,411,349,284,228,143,106,103,86,84,... | 50 | 50 | no | two | 3580 / 12092 | 39.650 | 0.2742 | 1.775 |
| A | Juglet_Piece_2 | 0.210898 | 2397 | 0 | 0 | none | 50 | 50 | no | none (21 retries) | - | - | - | - |
| B | Juglet_Piece_2 | 0.210898 | 2397 | 0 | 0 | none | 50 | 50 | no | none | - | - | - | - |
| C | Juglet_Piece_2 | 0.210898 | 2397 | 6 | 5 | 32,31,23,14,14 | 12 | 405 | yes | two | 220 / 179 | 11.486 | 0.2838 | 4.156 |
| D | Juglet_Piece_2 | 0.600000 | 1031 | 0 | 0 | none | 50 | 50 | no | none | - | - | - | - |
| A | Juglet_Piece_3 | 0.215277 | 3252 | 1 | 1 | 289 | 50 | 50 | no | none | - | - | - | - |
| B | Juglet_Piece_3 | 0.215277 | 3252 | 1 | 1 | 289 | 50 | 50 | no | one | 1115 / - | 31.407 | 0.9264 | 2.844 |
| C | Juglet_Piece_3 | 0.215277 | 3252 | 1 | 1 | 289 | 16 | 388 | yes | one | 1115 / - | 31.407 | 0.9264 | 2.844 |
| D | Juglet_Piece_3 | 0.600000 | 1467 | 2 | 1 | 268 | 50 | 50 | no | none | - | - | - | - |
| A | Juglet_Piece_5 | 0.238572 | 5668 | 3 | 2 | 51,740 | 50 | 50 | no | two | 229 / 2317 | 15.569 | 0.0871 | 1.183 |
| B | Juglet_Piece_5 | 0.238572 | 5668 | 3 | 2 | 51,740 | 50 | 50 | no | two | 229 / 2317 | 15.569 | 0.0871 | 1.183 |
| C | Juglet_Piece_5 | 0.238572 | 5668 | 4 | 4 | 136,604,51,29 | 28 | 316 | yes | two | 485 / 2050 | 22.921 | 0.1684 | 1.070 |
| D | Juglet_Piece_5 | 0.600000 | 3021 | 1 | 1 | 679 | 50 | 50 | no | none | - | - | - | - |
| A | Juglet_Piece_7 | 0.257988 | 7471 | 5 | 4 | 609,648,93,57 | 50 | 50 | no | two | 1753 / 1997 | 34.949 | 0.2845 | 1.268 |
| B | Juglet_Piece_7 | 0.257988 | 7471 | 5 | 4 | 609,648,93,57 | 50 | 50 | no | two | 1753 / 1997 | 34.949 | 0.2845 | 1.268 |
| C | Juglet_Piece_7 | 0.257988 | 7471 | 7 | 6 | 609,648,93,57,43,43 | 37 | 270 | yes | two | 1753 / 1997 | 34.949 | 0.2845 | 1.268 |
| D | Juglet_Piece_7 | 0.600000 | 4254 | 5 | 4 | 403,263,68,65 | 50 | 50 | no | two | 1012 / 829 | 27.482 | 0.1969 | 1.124 |
| A | Juglet_Piece_9 | 0.203464 | 1971 | 0 | 0 | none | 50 | 50 | no | none (21 retries) | - | - | - | - |
| B | Juglet_Piece_9 | 0.203464 | 1971 | 0 | 0 | none | 50 | 50 | no | none | - | - | - | - |
| C | Juglet_Piece_9 | 0.203464 | 1971 | 4 | 3 | 16,32,11 | 10 | 435 | yes | two | 144 / 269 | 11.565 | 0.3032 | 2.987 |
| D | Juglet_Piece_9 | 0.600000 | 787 | 0 | 0 | none | 50 | 50 | no | none | - | - | - | - |
| A | Pot_A_Piece_01 | 0.600000 | 85136 | 12 | 11 | 32775,27551,3803,3375,900,815,730,570,379,285,256,190 | 170 | 170 | no | two | 66763 / 57286 | 164.648 | 0.4344 | 0.734 |
| B | Pot_A_Piece_01 | 0.600000 | 85136 | 12 | 11 | (same) | 170 | 170 | no | two | 66757 / 57288 | 164.648 | 0.4344 | 0.734 |
| C | Pot_A_Piece_01 | 0.600000 | 85136 | 12 | 11 | (same) | 170 | 170 | no | two | 66761 / 57288 | 164.648 | 0.4344 | 0.734 |
| D | Pot_A_Piece_01 | 0.600000 | 85136 | 12 | 11 | (same) | 170 | 170 | no | two | 66761 / 57288 | 164.648 | 0.4344 | 0.734 |
| A | Pot_A_Piece_07 | 0.292881 | 34608 | 7 | 7 | 11815,12888,2722,1059,1018,234,216 | 69 | 69 | no | two | 24636 / 26739 | 53.605 | 0.4846 | 0.562 |
| B | Pot_A_Piece_07 | 0.292881 | 34608 | 7 | 7 | (same) | 69 | 69 | no | two | 24638 / 26738 | 53.605 | 0.4846 | 0.563 |
| C | Pot_A_Piece_07 | 0.292881 | 34608 | 7 | 6 | 11815,12888,2722,1234,1059,234 | 173 | 210 | yes | two | 24638 / 26739 | 53.605 | 0.4846 | 0.563 |
| D | Pot_A_Piece_07 | 0.600000 | 8598 | 8 | 7 | 2850,3093,203,191,170,144,73 | 50 | 50 | no | two | 6066 / 6437 | 53.981 | 0.4864 | 0.566 |
| A | Pot_A_Piece_08 | 0.270368 | 36097 | 7 | 7 | 12817,14141,1899,1499,222,106,97 | 72 | 72 | no | two | 26774 / 29286 | 49.755 | 0.5132 | 0.590 |
| B | Pot_A_Piece_08 | 0.270368 | 36097 | 7 | 7 | (same) | 72 | 72 | no | two | 26771 / 29280 | 49.666 | 0.5127 | 0.590 |
| C | Pot_A_Piece_08 | 0.270368 | 36097 | 5 | 5 | 12817,14141,1899,1499,222 | 180 | 246 | yes | two | 26774 / 29291 | 49.755 | 0.5131 | 0.590 |
| D | Pot_A_Piece_08 | 0.600000 | 7682 | 5 | 4 | 2611,2832,284,265 | 50 | 50 | no | two | 5528 / 6097 | 48.700 | 0.5023 | 0.699 |

\`floor\` is the number \`[FLOOR-23]\` printed and \`from\` the value before the cap; the cap is
\`0.005 * npts\` (\`mesh_processing_headless.cpp:3625\`, armed only when \`g_floorCeilingOn && g_countScaleAuto\`).
Arm A's floors on the other five Pot A pieces (arm A only, from the same file): 02 99, 03 93, 04 82,
05 76, 06 55, all uncapped, all two-surface.

Per-cell \`cov2mm\` is \`phase-1\`/\`measure34.py\`'s fraction of cloud points within 2 mm of surface 0, and
\`fold deg\` the median folded angle between surface-0 normals and the mesh (\`|dot|\`).

## 5. Part C — the region-size distribution before any floor

The pipeline cannot report the regions it discarded: it passes the floor into \`growPaper234\`
(\`mesh_processing_headless.cpp:3647\`). \`instruments/replica37.py\` grows from the pipeline's own rung-2
dump (its points, its normals, and \`theta\`/\`kappa\`/\`nb\`/\`floor\` read out of the rung-2 sidecar json)
and counts region sizes before the floor applies.

Columns: \`regions\` = number of regions before any floor; \`largest\` = points in the largest; \`>=10/20/30/50\`
= how many regions reach those point counts; \`>=1%/5%/10%\` = how many reach those fractions of the
cloud; \`ang/pt\` = angle refusals per point; \`depth\` = growth depth of the largest region.

Groups: **N** = adaptive spacing + honest nearest-carry normals (arms NA/PDN, the main column and the
configuration part D is dumped from); **F** = fixed 0.6 mm + nearest-carry normals (arm FX, spacing the
only difference); **R** = adaptive spacing + the pipeline's own re-estimated normals (arm RA — literally
the new default configuration).

| piece | grp | npts | regions | largest | >=10 | >=20 | >=30 | >=50 | >=1% | >=5% | >=10% | ang/pt | depth | floor | survivors | replica verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Juglet_Piece_2 | N | 2399 | 1765 | 45 | 9 | 3 | 2 | 0 | 3 | 0 | 0 | 5.032 | 7 | 50 | 0 | MATCH |
| Juglet_Piece_2 | F | 1031 | 708 | 39 | 5 | 2 | 2 | 0 | 4 | 0 | 0 | 4.612 | 8 | 50 | 0 | MATCH |
| Juglet_Piece_3 | N | 3253 | 2212 | 350 | 10 | 2 | 1 | 1 | 1 | 1 | 1 | 4.872 | 33 | 50 | 1 | MATCH |
| Juglet_Piece_3 | F | 1467 | 878 | 316 | 3 | 1 | 1 | 1 | 3 | 1 | 1 | 4.288 | 38 | 50 | 1 | MATCH |
| Juglet_Piece_3 | R | 3252 | 2124 | 289 | 5 | 1 | 1 | 1 | 1 | 1 | 0 | 4.843 | 36 | 50 | 1 | MATCH |
| Juglet_Piece_5 | N | 5668 | 3311 | 716 | 28 | 9 | 5 | 3 | 3 | 1 | 1 | 4.477 | 45 | 50 | 3 | MATCH |
| Juglet_Piece_5 | F | 3021 | 1564 | 652 | 10 | 4 | 4 | 2 | 4 | 1 | 1 | 4.016 | 55 | 50 | 2 | MATCH |
| Juglet_Piece_5 | R | 5668 | 3214 | 604 | 15 | 5 | 3 | 3 | 2 | 1 | 1 | 4.474 | 43 | 50 | 3 | MATCH |
| Juglet_Piece_7 | N | 7471 | 3943 | 1035 | 42 | 13 | 6 | 4 | 4 | 1 | 1 | 4.340 | 68 | 50 | 4 | MISMATCH |
| Juglet_Piece_7 | F | 4254 | 2020 | 258 | 27 | 12 | 10 | 9 | 9 | 2 | 0 | 3.982 | 23 | 50 | 9 | NEAR |
| Juglet_Piece_7 | R | 7471 | 3527 | 609 | 49 | 14 | 8 | 5 | 3 | 2 | 0 | 4.141 | 45 | 50 | 5 | MATCH |
| Juglet_Piece_9 | N | 1972 | 1465 | 16 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 5.148 | 7 | 50 | 0 | MATCH |
| Juglet_Piece_9 | F | 787 | 578 | 33 | 3 | 1 | 1 | 0 | 3 | 0 | 0 | 4.831 | 12 | 50 | 0 | MATCH |
| Pot_A_Piece_07 | N | 34608 | 2494 | 13131 | 20 | 12 | 10 | 10 | 6 | 2 | 2 | 0.799 | 75 | 69 | 10 | MATCH |
| Pot_A_Piece_07 | F | 8598 | 1031 | 3185 | 16 | 10 | 10 | 7 | 6 | 2 | 2 | 1.186 | 37 | 50 | 7 | MATCH |
| Pot_A_Piece_07 | R | 34608 | 2837 | 12888 | 21 | 9 | 7 | 7 | 5 | 3 | 2 | 0.889 | 74 | 69 | 7 | MATCH |

Machine-readable: \`phase2/out/partc37.tsv\` (long) and \`phase2/out/partc37_wide.tsv\` (the three groups
side by side), written by \`instruments/partc37.py\` from the job's \`out/replica37.tsv\`.

### 5b. Re-validation verdict, explicitly

**VALIDATED.** The replica reproduces the pipeline's own cluster sizes in the configuration the ticket
names (adaptive spacing, the pipeline's own re-estimated normals — group R): 4 of 4 gate cells MATCH
exactly, region for region:

\`\`\`
RA/Juglet_Piece_3   pipeline [289]                                  replica [289]
RA/Juglet_Piece_5   pipeline [604, 136, 51]                        replica [604, 136, 51]
RA/Juglet_Piece_7   pipeline [609, 578, 93, 70, 57]                replica [609, 578, 93, 70, 57]
RA/Pot_A_Piece_07   pipeline [12888, 11815, 2722, 1059, 1018, 234, 216]
                    replica  [12888, 11815, 2722, 1059, 1018, 234, 216]
\`\`\`

What does not match, stated with its deltas:

- \`NA/Juglet_Piece_7\` (adaptive + nearest-carry) is **MISMATCH**: pipeline \`[1035, 136, 88, 85, 82]\`
  against replica \`[1035, 113, 112, 88]\` — the largest region is identical to the point, the tail
  differs (3 pipeline survivors against 2 replica ones).
- \`FX/Juglet_Piece_7\` (fixed + nearest-carry) is **NEAR**: pipeline \`[258,214,137,101,88,86,81,73,71]\`
  against replica \`[258,214,137,101,88,86,85,81,73]\` — three pairs differ by 4, 8 and 2 points, all
  inside the instrument's \`max(2 points, 10%)\` tolerance.
- \`Juglet_Piece_2\` and \`Juglet_Piece_9\` MATCH trivially: both sides find **zero** regions at/above the
  floor (21 retries, no cluster grew). Nothing above the floor exists to disagree about.
- The three part-D pieces (Juglet 2, Juglet 9, Pot_A 07) are all in the **MATCH** column on the
  nearest-carry side, so the dumps below are the validated column.
- The dump is only a valid test of the replica where \`paper_chain=true\`; all 16 rung-2 sidecars in this
  run carry \`paper_chain=true\`, \`theta=3.4\`, \`kappa=1.0\`, \`nb=10\`. (A pre-flight against a
  \`paper_chain=false\` rung-2 dump from another run mismatched, as expected — that dump is not a test of
  the paper chain.)

## 6. Part D — the pre-floor regions, dumped and drawn

One PLY per piece, the ticket-25 rung-2 layout — \`property float x/y/z/nx/ny/nz\`,
\`property int cluster_id\`, \`property uchar reason\` — with \`cluster_id\` ordered by region size (\`0\` =
largest, so the eight ids that have a fixed colour are the eight largest regions), plus a \`.json\`
sidecar holding **every** region's id, size, seed index, seed curvature, growth depth, pops, tests,
angle refusals and curvature refusals.

| piece | PLY bytes | json bytes | points | regions | largest | sizes top 8 | reason 1 (seed) / 3 (grown) |
|---|---|---|---|---|---|---|---|
| Juglet_Piece_2 | 159533 | 346214 | 2399 | 1765 | 45 | 45,38,24,19,18,16,11,10 | 1765 / 634 |
| Juglet_Piece_9 | 129912 | 287300 | 1972 | 1465 | 16 | 16,15,13,13,11,11,11,11 | 1465 / 507 |
| Pot_A_Piece_07 | 2190469 | 490818 | 34608 | 2494 | 13131 | 13131,12042,1622,1248,1127,1052,183,165 | 2494 / 32114 |

Figures (\`instruments/fig37.py\`; fixed colour map 0 blue, 1 red, 2 green, 3 violet, 4 orange, 5 brown,
6 pink, 7 cyan, -1 grey — ids above 7 share grey with -1 and the legend says so; three orthographic
views at one cube scale per piece, so all three views of a piece share camera and scale; the measured
mm/px is printed on the figure beside a 5 mm bar):

| piece | figure | pixels | mm/px | px per mm | 5 mm bar | bytes | dpi |
|---|---|---|---|---|---|---|---|
| Juglet_Piece_2 | \`phase2/figures/Juglet_Piece_2/Juglet_Piece_2_regions_3views.png\` | 1907 x 860 | 0.0637 | 15.7 | 5.0 mm | 225069 | 269.5 |
| Juglet_Piece_9 | \`phase2/figures/Juglet_Piece_9/Juglet_Piece_9_regions_3views.png\` | 1902 x 842 | 0.0445 | 22.5 | 5.0 mm | 269478 | 267.6 |
| Pot_A_Piece_07 | \`phase2/figures/Pot_A_Piece_07/Pot_A_Piece_07_regions_3views.png\` | 2061 x 864 | 0.1084 | 9.2 | 5.0 mm | 349315 | 269.8 |

Per-figure metadata: \`phase2/figures/figures37.json\`. The drawn point set is exactly the dumped PLY
(no filtering, no downsampling), so a point that is grey on the figure is a region with id > 7.

## 7. Integrity

- \`phase1/out/inputs_before.md5\` and \`inputs_after.md5\` are identical (29330 bytes each, \`out/inputs.diff\`
  0 bytes); the corpus tree listing is identical (\`corpus_before.txt\` = \`corpus_after.txt\`, 228922 bytes,
  \`out/corpus.diff\` 0 bytes). Phase 2: the same, both diffs 0 bytes.
- \`/opt/sfs-pristine\` recorded **ABSENT** in both runs (\`phase1/out/pristine.txt\` carries the status line
  plus \`ls: cannot access '/opt/sfs-pristine': No such file or directory\` and a \`stat\` line). Nothing was
  created there.
- The 55-cell run's own arm check read every arm's \`[SPACING-22]\`/\`[COUNT-22]\`/\`[SWITCH-23]\` lines and
  passed; the 16-cell run's is \`phase2/out/ARMCHECK.txt\` (NA 3/3 spacing, 3/3 \`normalSource=input\`;
  PDN 3/3 and 3/3; FX 6/6 and 6/6; RA 4/4 spacing, 0/0 normal input because RA is the re-estimated arm).

## 8. Deletion record

Written before the delete, counted, per tree (\`<cell>/logs/geometry_counts.tsv\`), from 55 + 16 cell records:

| run | stage + rung dump | build tree |
|---|---|---|
| phase 1 (55 cells) | 1530 files, 2241503303 bytes — obj 55/333590836, pcd 186/740234283, ply 608/893493901, xyz 251/273983435, json 275/174800, other 155/26048 | 7693 files, 386489959 bytes |
| phase 2 (16 cells) | 405 files, 211394221 bytes — obj 16/13334880, pcd 40/91327724, ply 162/82194872, xyz 66/24485037, json 80/44162, other 41/7546 | 3887 files, 194337036 bytes |

Kept: \`GEOMETRY_KEPT.txt\` count **0** in both runs — no cell kept its stage or rung dump because nothing
failed. What the delete does not touch, by design: every cell's \`surfaces/\`, \`measure/\`, \`logs/\` and
\`cell.tsv\`, the \`out/prefloor/\` dumps and sidecars, the figures, the tables, and both \`run.json\`.
The two tarballs downloaded to the laptop (\`phase2/evidence.tgz\` md5 \`d5970e19a4d5f233703b1879fb1fca06\`,
\`phase2/cells.tgz\` \`3d405a4e9cc947f9e83340a79b5c6d7c\`) are copies, not the record.

## 9. Index rows and branch

\`\`\`
20261027-1404_c16e274_t37-adaptive-default  33886175  c16e2743965a6b30afe78db63a7dd0b8f420b19f  t37-adaptive-default  <empty>  <empty>
20261027-1420_c6f6491_t37-prefigure         33886571  c6f649115100f8e3f725ef2bd68e1b32f1f629b1  t37-prefigure         <empty>  <empty>
\`\`\`

Both rows were appended by the job itself (\`printf "%s\t%s\t%s\t%s\t\t\n"\`), verdict and human_note left
empty.

## 10. What did not work, with the error text

1. \`fetch_instruments37.sh c6f6491 <rundir>\` first refused:
   \`[FETCH] FATAL commit c6f649115100f8e3f725ef2bd68e1b32f1f629b1 not in /data/gpfs/projects/punim2657/sfs_preprocessing -- push the branch and let the checkout fetch first\`.
   Cause: the canonical checkout had not fetched the new commit. Fix: \`git -C <canon> fetch --no-tags origin\`,
   then the same command printed \`[FETCH] all 17 instrument files are LF; bash -n passes on every .sh\`.
2. \`fig37.py\` first printed \`[F37] MISSING phase2/out/prefloor\Juglet_Piece_2.ply\` — it looked for
   \`<piece>.ply\` while the job writes \`<piece>_prefloor_regions.ply\`. Fixed in the instrument (both names
   are accepted); the job side is unchanged.
3. \`fig37.py\` also reported \`largest=1764\` for Juglet 2 on its first pass: it printed \`max()\` over a dict,
   which is the largest **id**, not the largest region. Fixed to \`max(sizes.values())\` (45 for Juglet 2).
4. The first \`partc37.py\` run listed every row twice: it globbed both \`out/replica37.tsv\` and the per-cell
   \`measure/replica.tsv\`. Fixed to prefer the flattened table.
5. Point markers were invisible on the first figure pass (markers sized from the mm/px target instead of
   the dpi), so a 45-point region had no visible colour. Fixed: markers are now a fraction of a millimetre
   converted through the figure's dpi, the grey tail is drawn first and the eight named regions on top.

## 11. Reproduce

\`\`\`bash
# phase 1 (the change, proofs 1 and 2, the arm grid)
bash <phase-1 rundir>/instruments/submit37.sh <rundir> t37-adaptive-default t37phase1 12:00:00 \
     c16e2743965a6b30afe78db63a7dd0b8f420b19f 5bdaff656f7aa683d5d2bc66f7c3fc2e6c31986f \
     <boot dir> 1
# phase 2 (part C distributions, part D dumps)
bash <phase-2 rundir>/instruments/submit37.sh <rundir> t37-prefigure t37phase2 12:00:00 \
     c6f649115100f8e3f725ef2bd68e1b32f1f629b1 5bdaff656f7aa683d5d2bc66f7c3fc2e6c31986f \
     <boot dir> 2
# on the laptop, from the fetched evidence
python instruments/partc37.py --run phase2
python instruments/fig37.py --dumpdir phase2/out/prefloor --outdir phase2/figures/Juglet_Piece_2 \
       --pieces Juglet_Piece_2 --target-mm-px 0.050
\`\`\`
