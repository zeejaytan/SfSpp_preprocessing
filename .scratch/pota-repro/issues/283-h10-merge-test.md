# 283 — Name the test that refuses Pot H 10's ribbon

Answers: E1
Status: results-in (rejected on rho_n: 21.33 deg at the seam against 18.19 deg; every other test passes, so H10 closes as class K and no merge change is proposed)
Working in: C:/PR/worktrees/sfs/283 (one mesh run; no C++, no default changed)
Needs-eye: no

## What ticket 281 established

Pot H 10 Bl1 misses 20 of its 88 reference dots. Fifteen of them sit on **dropped cluster 5** —
629 points, a 21.66 x 3.20 x 1.76 mm ribbon meeting kept cluster 1 at 0.3191 mm — so the edge the
authors drew belongs to a facet we never kept. Step 1 of the Appendix A merge is satisfiable there
(35 c5 points within rho_d = 1.0 mm of c1, 37 the other way), so a pair could have formed and the
refusal came from a later test. Which one is not recoverable from a dump: it needs the merge trace.

## Task

One mesh run, frozen inputs, theta 3.4, with **SFS_MERGE_PAIRS=1** (the ticket 276 Phase 2
instrumentation already prints nrm / curv / inner / icurv and the verdict per candidate pair) and
**SFS_AXIS_FILE set** — confirm the log's classify line shows the axis was used, not "no
SFS_AXIS_FILE, keep size order" (ticket 277). Cluster ids must come out the same as in 281's
dump; if they do not, stop and report, because the run is not the same piece.

Find the c5-c1 pair in the PAIR-276 output and quote its line verbatim: the pair index, the
qualifying-pair count, dmin/dmed, nrm, curv, inner, icurv, and the accept/reject verdict.

## Pre-registered read

- Rejected on **rho_n (0.95)**: the refusal is PRINCIPLED — the ribbon sits ~28 deg from the kept
  face's normal and the paper requires agreement within ~18 deg, so merging it would be against
  the paper's own rule. H10 Bl1 then closes as class K with a paper-consistent reason, and no
  merge change is proposed.
- Rejected on **rho_in,n (0.75)** or rho_c: this is the same Step 3 / curvature defect seen on
  Pot C 03 and Pot C 01 in ticket 276 Phase 2, and it becomes a shared cause rather than a
  one-off.
- **No pair printed at all** (no qualifying pair): then 281's Step-1 numbers were measured on a
  different frame — report it and stop; do not retune rho_d.

## Results

One mesh run on the 276 frozen inputs. No C++ edit, no default changed, no threshold retuned.

| item | value |
|---|---|
| job | 33744525 (`p283h10`), COMPLETED 0:0, 6 s |
| run dir | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1832_ee5f4dc_p283-h10-merge-test/` (`out/H10_pairs/`) |
| binary | `37086971e327bc8996ea591bf66064f5` — the ticket 276 Phase 2 instrumentation (diag + PAIR-276) |
| source | `mesh_processing_headless.cpp` md5 `3cf1fbfd91e87644d13e4bc4bce44b53` (worktree 276, untouched) |
| inputs | the ticket 276 frozen set `inputs/H10_diag/`: Point.pcd `994216ee16122285607efb32e640249a`, Mesh.obj `83bd7ed63bd7945ac980ec6794156d89`, Axis.xyz `723002c8925cc7bb4ce1705946d1429b` |
| env | `POT_NAME=Pot_H SFS_PAPER_THETA=3.4 SFS_AXIS_FILE=<stage axis> SFS_MERGE_DIAG=1 SFS_MERGE_PAIRS=1` |

The angle and the axis were both used — verbatim from `out/H10_pairs/mesh.log`:

```
[PAPER-234] paper grow: thetaDeg=3.40000 kappa=1.00000 nb=10
[PAPER-234] classify: face0 n=4484 interior_frac=0.8410 face1 n=3403 interior_frac=0.0341 satA=7058.0000 satB=829.0000
[PAPER-234] classify: kept -> Surface_0=interior
```

There is no `no SFS_AXIS_FILE, keep size order` line anywhere in the log (grep returns empty), so the axis
file was used and the classification is the real one.

### The cluster census is the same piece — the pair trace just numbers a different list

Post-merge, the dump is identical to 281's, line for line: `# npoints 16387 nclusters 9 thetaDeg 3.4 split 0`,
then 9 clusters of 4484 / 3403 / 1685 / 745 / 744 / 629 / 186 / 151 / 72 with the same surface flags, and
`[MERGE-DIAG-276] labels: npoints=16387 nclusters=9 surface0=4484 surface1=3403 dropped=4212 unclustered=4288`.
`SFS_MERGE_PAIRS=1` therefore changed nothing about the decisions — it only printed.

The **PAIR-276 lines do not use the dump's ids.** They index the pre-merge list (13 clusters, printed by the
tool as `Cluster 1..13 : 4484 3403 777 744 629 603 376 278 254 186 151 142 72`), while the dump re-issues the
survivors in descending size order. Four merges happened — 376 into 777, 278 into 1153, 254 into 1431, 142 into
603 — which gives this mapping:

| pre-merge id (pair trace) | size | fate | 281 dump id |
|---|---|---|---|
| c0 | 4484 | kept, Surface_0 | 0 |
| **c1** | **3403** | **kept, Surface_1** | **1** |
| c2 | 777 | +376 +278 +254 = 1685 | 2 |
| c3 | 744 | survived | 4 |
| **c4** | **629** | **the ribbon, dropped** | **5** |
| c5 | 603 | +142 = 745 | 3 |
| c6 / c7 / c8 | 376 / 278 / 254 | merged into c2 | – |
| c9 | 186 | survived | 6 |
| c10 | 151 | survived | 7 |
| c11 | 142 | merged into c5 | – |
| c12 | 72 | survived | 8 |

So **281's `c5` (629, the ribbon) is printed as `c4` in the pair trace, and 281's `c1` is `c1` in both.** The
ticket's stop condition asks whether the run is the same piece; on the evidence it is — same 16387 points,
same theta, same 9-cluster census in the same order, same classify counts, and the pair's `dmin=0.3191`
reproduces the 0.3191 mm that ticket 281 measured independently by nearest-neighbour search. The id
difference is a numbering space, not a different piece, so the run was not stopped; but every future
PAIR-276 reading on this piece must translate, and that is the reason this table is here.

### The c5-c1 pair, verbatim

```
[PAIR-276] pass=1 c1-c4 nA=3403 nB=629 bnd=462/223 scan=223/223 cut=0 pairs=34 cap=0 dmin=0.3191 dmed=0.6547 nrm=0.9315 curv=0.0002 rhoN=0.9500 rhoC=0.1000 verdict=REJECT:rhoN
```

Pass 2 re-tests it and prints the identical line (same values, same verdict):

```
[PAIR-276] pass=2 c1-c4 nA=3403 nB=629 bnd=462/223 scan=223/223 cut=0 pairs=34 cap=0 dmin=0.3191 dmed=0.6547 nrm=0.9315 curv=0.0002 rhoN=0.9500 rhoC=0.1000 verdict=REJECT:rhoN
```

Reading it field by field: `pairs=34` qualifying boundary pairs, with all 223 of the ribbon's boundary points
scanned and **no 200-pair cap** (`cut=0 cap=0`), so this is not a starved search; `dmin=0.3191 dmed=0.6547` mm,
so it is not a distance refusal either; `nrm=0.9315` against `rhoN=0.9500` → **REJECT:rhoN**; `curv=0.0002`
against `rhoC=0.1000`, which would have passed; and `inner=` / `icurv=` are **absent from the line because Step
3 is never reached** — that absence is the information, not missing data.

`0.9315` is **21.33 deg** between the two sides' normals at the seam. The paper's `rho_n = 0.95` is **18.19 deg**.
The ribbon is therefore refused by 3.1 deg, not by a wide margin.

### The pair census — the ribbon's whole neighbourhood, and the absence of other rejections

87 PAIR-276 pair lines over the two passes: 79 rejected at Step 1 with `pairs=0` (no 3 qualifying boundary
pairs), and 8 that reached the tests, from 6 distinct pairs. **Zero rejections on `rho_c`, `rho_in,n` or
`rho_in,c` anywhere on this piece** — measured, not assumed.

The ribbon (`c4`, 629) is tested against every other cluster in both passes and **only the kept sheet forms
pairs with it**: c0 4484, c3 744, c5 603, c6/c7/c8, c9 186, c10 151, c12 72 all give `pairs=0`. Its single
admissible seam is the one quoted above.

The other pairs that formed and passed:

| pair (trace ids) | sizes | pairs | dmin / dmed | nrm | inner | verdict |
|---|---|---|---|---|---|---|
| c2-c6 | 777 / 376 | 8 | 0.2837 / 0.7225 | 0.9759 | 0.8840 | ACCEPT (merged) |
| c2-c7 | 1153 / 278 | 6 | 0.3430 / 0.7661 | 0.9949 | 0.8879 | ACCEPT (merged) |
| c2-c8 | 1431 / 254 | 20 | 0.2989 / 0.7083 | 0.9948 | 0.9703 | ACCEPT (merged) |
| c5-c11 | 603 / 142 | 19 | 0.4960 / 0.7829 | 0.9855 | 0.9779 | ACCEPT (merged) |
| c2-c10 | 1685 / 151 | 8 | 0.5161 / 0.7155 | 0.9221 | – | REJECT:rhoN |

The one other `rho_n` refusal — 1685 against 151, `nrm=0.9221` = 22.78 deg — is also a genuine facet
disagreement, and it too never reaches Step 3.

### Verdict: the first pre-registered read fires — rejected on `rho_n`

The refusal is **principled**: the ribbon's normals disagree with the kept face's by 21.33 deg at the seam,
the paper's Appendix A step 2 requires agreement within 18.19 deg, and Step 2's curvature test would have
passed. Merging it would be against the paper's own rule, so **Pot H 10 Bl1 closes as class K (partition
mismatch, ledger K) for a paper-consistent reason**, and no merge change is proposed.

The honest caveat, stated because it changes what the number means: the margin is **3.1 deg**, so this is a
near miss rather than an emphatic refusal. The Step 3 defect that ticket 276 Phase 2 found on Pot C 03
(`inner=-0.0142`) and Pot C 01 (`inner=-0.1481`) **does not reach this piece at all** — every pair here either
never forms or is decided at Step 2. H10 is therefore *not* evidence for a shared Step 3 cause; it is a
different, paper-consistent refusal.

**What would overturn this:** `nrm` is the mean over the 34 pair-member normals at the seam. Re-estimating
normals at a different search radius could move it across 0.95, and then the ribbon would enter Step 3 and be
subject to exactly the Pot C defect. That is a measurement nobody has made; it is not proposed here, and
nothing was retuned.

### Evidence

`out/H10_pairs/`: `mesh.log` (full run), `pairs.txt` (all 87 PAIR-276 lines), `census.txt`, `build.txt`
(binary + source md5), `inputs.md5`, `exit.txt`, `mergeDiag276_Pot_H_Piece_10.txt` (post-merge dump, identical
to 281's). `stage/H10_pairs/` holds the working tree the run used. Worktree `C:/PR/worktrees/sfs/283` at
`ee5f4dc`; nothing committed, worktrees 275/276/279/280/281/284 untouched.


## Constraints

- Do not change a default, do not edit C++, do not retune any threshold.
- Run directory under SfSpp/runs/ with run.json, one index.tsv row, tag p283-h10-merge-test.
- Report the pair census as well as the c5-c1 line, so the absence of other pairs is visible.

## Acceptance

- The c5-c1 pair line quoted verbatim, with the rejecting test named.
- The classify line proving the axis file was used, and the cluster census matching 281.
- One of the three pre-registered verdicts, and the follow-up it implies.
