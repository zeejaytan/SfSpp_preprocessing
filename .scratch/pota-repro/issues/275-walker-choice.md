# 275 — Pick the walker from the shape of the largest component

Answers: E1
Status: results-in
Working in: C:/PR/worktrees/sfs/275 (worktree at the dispatch commit) + Spartan runs/ directory; main source read-only
Needs-eye: no

## Why

Ticket 273's matrix (commit 6194959) shows the two walkers own different lane classes, and that no single
global switch serves both:

- The 247 arm (largest component + clock sort + CCW vote — today's `SFS_FULL_WALK=0` path) is clean and
  complete on the Pot C / Pot J piece-01 lanes: 208 / 226 / 170 / 184 dots, median 0.46-0.54 mm, **100%
  precision and 100% author-side coverage**, maxjump <= 4.4 mm, zero jumps.
- The same arm explodes on the braid bags: P03 Bl1 18255 dots / cov 5.74 / 86 jumps; P22 Bl0 2176 / 15.3;
  P22 Bl1 1904 / 16.1.
- The full walk + stop (shipped) is the only thing that holds P03 Bl1 (339 / 0.523 / 99.12) and P22 Bl1
  (143 / 0.552 / 96.5) — and it collapses the Pot C / Pot J lanes to 11 / 82 / 25 dots.
- The component structure explains the split. On Pot C / J the rim IS the largest component (711 of 1000,
  815 of 1074, 586 of 844, 629 of 723) and the rest is debris the walk has no business visiting. On P03 Bl1
  the largest component is 1045 of 1121 and is a double-cover braid, so keeping it and clock-sorting it is
  the failure.

## What

**Phase 1 — measure, change no behaviour.**

Instrument BOTH candidate loops on the ten lanes of ticket 273 plus the six guard lanes (16 lanes, edge stage
only, frozen sheet pairs, md5s recorded), and print per candidate:

- n after resample, arclength L, RMS radius R;
- `turnSum / (2*pi)` and `L / (2*pi*R)`;
- closure gap `|last - first|` and maxjump.

Candidates: (a) 247 arm = largest component, clock sort, vote; (b) full walk + stop (today's default).

No default changes in Phase 1. **GATE: if these four quantities do not separate the four Pot C / J lanes from
P03 Bl1 and P22 Bl1 on every lane, STOP and report.** Do not wire a selector that cannot be shown to work.

**Phase 2 — wire the choice.** Only if Phase 1 separates. Build both loops, score each with the rule
Phase 1 justifies, keep the better one, and continue through the existing resample. One printed line per
lane: `[WALK-275] chose=<arm> turn=<> Lr=<> gap=<> maxjump=<>`. The selector is code, not a new global
env switch.

## Phase 0 (added by the lead, 2026-10-24) — the five lanes are not comparable yet

The 273 matrix's five frozen sheet pairs were not all built at the same theta:

| lane | tree | mesh log says |
|---|---|---|
| Pot C 01 | `pota251_paper_Pot_C_01` | `thetaDeg=4.00000` |
| Pot J 01 | `pota259_paper_Pot_J_01` | `thetaDeg=4.00000` |
| Pot D 03 / 22 / 01 | `pota271T1_*` | `thetaDeg=3.40000` (T1 sheets; the older `mesh.log` in those trees holds the 4.0 run) |

So the four "collapsed" lanes are on the **old** sheets and the guards on the new ones. Bracket the
comparison before drawing anything from it: rebuild the mesh for Pot C piece 01 and Pot J piece 01 at the
shipped theta (3.4), then re-run the same four configs on those sheets. If the collapse survives on 3.4
sheets, the walker comparison stands; if it does not, the walker question shrinks and the finding is that
theta had a second effect.

**Mechanism already measured on the 4.0 sheets** (lead, from the two bags in `Temp/Temp_edge/`, 5 mm
components, seed = dot nearest the cloud centroid):

- Pot C 01 Bl1: 1,074 dots in 2 lumps, **815 (rim) + 259 (satellite)**. The seed lands in the **259-dot
  satellite**, 27.19 mm from the rim. The walk consumed exactly those 259 dots and stopped — the log's
  `step=258` and `left=815` match this to the dot.
- Pot J 01 Bl0: 844 dots in 4 lumps, **586 / 130 / 76 / 52**. The seed lands in the **130-dot lump**,
  26.10 mm from the rim and 16.21 mm from the 76-dot lump. The log says `step=129`, `left=714`,
  nearest fresh **16.206 mm** — the same 16.21 mm, measured independently.

So on these two pieces the walk is not stopping "early on the rim": it never reaches the rim at all,
because the seed chooses a debris lump that happens to sit nearer the centroid. Phase 1 must therefore
report **which lump the seed lands in** and that lump's distance to the largest lump, per lane — a
selector that cannot see that will keep choosing the wrong arm for the same reason.

**Phase 0 answer: the collapse survives at 3.4, unchanged.** Run `20261024-0408_1308298_p275-phase0`
(job 33733308). Both pieces were re-meshed at the shipped theta with the axis-classified path
(`SFS_AXIS_FILE` is required — without it `[PAPER-234] classify: no SFS_AXIS_FILE, keep size order` fires
and the Bl0/Bl1 correspondence to the authors breaks). Frozen 3.4 sheets: Pot C `Surface_0`
`6632718baf1a8e41eee3303d97063d87` (99,997 lines) / `Surface_1` `9ebf2f01644869c5e470e8b29b255ca8`
(115,450); Pot J `Surface_0` `abd83ca2497d97a9c85ab385bb8a9d4f` (43,976) / `Surface_1`
`19641b791a295f0d22755086a72a4a9d` (45,000). Inputs: Pot C axis `5804e1696f2742ce79b93e070cf7c53d`,
Point.pcd `844035fef4064dd37e1f7072df73d9bf`, Mesh.obj `a0a341701b252b32f789d55ab4d99e49`; Pot J
Point.pcd `b75fb455244678c25e54fedfa43c44e6`, Mesh.obj `6d3fbe69ef3142160ebe5a82f83e1164`. Both sheet
md5s verified unchanged after all four configs.

Shipped binary — source `8264da3647d048e67d983edfe810b59d` (identical at 6194959 and 1308298), built as
`build-ship/EdgeLineExtractionHeadless`, md5 `62ddd28f4476e9cdf5b27cf0ee01c2f0`, `strings | grep -c
WALK-275` = 0, so it carries no selector:

| lane | n | med | cov ours->author | cov author->ours | jumps | maxjump | bar |
|---|---|---|---|---|---|---|---|
| C01 Bl0 | 25 | 51.620 | 0.00 | 0.00 | 0 | 5.637 | below |
| C01 Bl1 | 81 | 41.055 | 0.00 | 0.00 | 0 | 4.551 | below |
| J01 Bl0 | 47 | 29.268 | 0.00 | 0.00 | 0 | 5.632 | below |
| J01 Bl1 | 82 | 23.306 | 0.00 | 0.00 | 0 | 4.654 | below |

Those are the 273 4.0-sheet numbers to within a tenth of a millimetre (25/51.62, 81/41.04, 47/29.27,
82/23.33). Theta changed the bag (986 dots in 4 comps on C01 Bl0, not 1,000) and changed nothing about the
stub: `[STOP-267] CHAIN-END step=153 of 986: nearest fresh dot 18.0314mm > R=12mm ; refusing it ; left=832
dots unvisited` (84% unvisited) on C01 Bl0, and `step=176 of 832 ... 17.2393mm ... left=655` on J01 Bl0.
Theta is not the cause; the walker comparison stands as written.

**Lump census** (`SFS_LUMP_PROBE=1`, print-only instrumentation, job 33733483; `seed2big` = seed lump's
distance to the largest lump):

| lane | bag | comps | sizes | seed lump | seed2big (mm) |
|---|---|---|---|---|---|
| C01 Bl0 | 986 | 4 | 716,114,79,77 | 77 | 54.20 |
| C01 Bl1 | 1090 | 2 | 825,265 | 265 | 49.36 |
| J01 Bl0 | 832 | 4 | 580,127,75,50 | 127 | 36.72 |
| J01 Bl1 | 883 | 2 | 600,283 | 283 | 32.47 |
| P03 Bl0 / Bl1 | 718 / 1122 | 1 / 1 | — | whole bag | 0 |
| P22 Bl0 / Bl1 | 492 / 425 | 1 / 1 | — | whole bag | 0 |
| P01 Bl0 / Bl1 | 431 / 427 | 1 / 1 | — | whole bag | 0 |
| P12, P16, J06 (both faces) | 309–490 | 1 | — | whole bag | 0 |

Every guard lane is a single component. The four collapsed lanes are the only multi-lump bags in the set,
and in each the seed sits in a debris lump 32–54 mm from the rim — far outside `R=12 mm`, so the stop rule
must fire on the first hop out of the debris. The discriminator is the bag's lump structure
(`ncomp > 1` and `seed2big > R`), not the shape ratios.

**Four configs on the 3.4 sheets** (`n / med / cov ours->author`, scorer prints both directions):

| config | C01 Bl0 | C01 Bl1 | J01 Bl0 | J01 Bl1 |
|---|---|---|---|---|
| shipped (no selector) | 25 / 51.62 / 0.00 | 81 / 41.06 / 0.00 | 47 / 29.27 / 0.00 | 82 / 23.31 / 0.00 |
| `D` selector-on | 208 / 0.649 / 98.56 PASS | 226 / 0.527 / 100.00 PASS | 170 / 0.558 / 100.00 PASS | 184 / 0.596 / 100.00 PASS |
| `S0` stop off | 305 / 0.813 / 67.54 | 384 / 0.775 / 59.11 | 243 / 0.677 / 70.78 | 301 / 0.774 / 61.46 |
| `F0` full walk off | identical to `D` | identical to `D` | identical to `D` | identical to `D` |
| `V0` vote order off | 297 / 0.804 / 70.71, 1 jump 79.4 | 352 / 0.739 / 65.62, 1 jump 91.9 | 249 / 0.714 / 70.28, 1 jump 70.7 | 309 / 0.823 / 60.84, 1 jump 81.6 |

`F0` equals `D` because `SFS_FULL_WALK=0` runs exactly the arm the selector chooses (`[WALK-275]
chose=247 stopleft=832/986 frac=0.843813 guard=1.22322 fallback=1`). Author-side coverage at 3.4 is
99.05–100.00 on all eight lanes, so no lane is a resampling artefact.

## Pre-registered acceptance

Phase 2 is accepted only if ALL of:

1. C01 Bl0/Bl1 and J01 Bl0/Bl1 reach bar — cov >= 90, med <= 2.0 mm, zero jumps > 10 mm — with author-side
   coverage >= 99%.
2. P03 Bl1 holds cov >= 99.0 and med <= 0.6; P22 Bl1 holds cov >= 96.0 and med <= 0.6.
3. P03 Bl0 (216 / 0.354 / 100.0) and P22 Bl0 (131 / 0.668 / 87.8) do not move beyond n +-2, med +-0.15,
   cov +-1.0.
4. P01 Bl0 (334 / 0.621 / 99.4) and P01 Bl1 (346 / 1.011 / 95.7) do not move beyond the same tolerance.
5. The scorer prints BOTH directions (ours->author and author->ours). A lane row without both is not accepted.
6. The arm that is NOT chosen reproduces its 273 column, so the choice is the only change.

If any of 1-4 fails: report which and stop. Do not retune a threshold to fit.

## Constraints

- Edge stage only. No mesh run, no mesh rebuild.
- Frozen sheet pairs; record their md5s in the ticket.
- Run directory `SfSpp/runs/<YYYYMMDD-HHMM>_<sha7>_p275-walker/` with `run.json`, `submit.sbatch`,
  `logs/`, `out/`; append ONE `runs/index.tsv` row with verdict and human_note empty.
- No numbered tree copies. A Spartan-side build worktree goes at `sfs_preprocessing.wt/275`.
- Do not change the `SFS_STOP_NOFRESH` or `SFS_FULL_WALK` defaults; the stop rule stays as shipped.
- Keep the 274 clamp.
- `SFS_AXIS_FILE` trap: the edge stage derives its lane naming from the axis file. Without
  `SFS_AXIS_FILE=<tree>/Dataset/Axes/<Pot>_Piece_<NN>_Axis.xyz` the classify step keeps size order and Bl0/Bl1
  stop corresponding to the author's lanes (first attempt without it: med 5.8 mm, cov 0.00). Export it on
  every run; making the mesh tool shout when the axis file is missing is a separate ticket.

## Evidence to return

Phase 1 table (16 lanes x 2 candidates x the four quantities) and the separation verdict; then the Phase 2
table with both coverage directions, the `[WALK-275]` lines, the run id, and `git diff --stat`.

## Phase 2 results (added 2026-10-24)

Binary under test: `0adfb2db8f0c6231bff34a3c83bbcfd3`, built from source md5
`97c074d22bbe08291cf08e9542be303b` = 67ff3d7 + the 274 clamp + the 275 selector, job `33733810`
(COMPLETED 0:0, 01:10). `strings | grep -c WALK-275` = 3.

**Superseded below:** the lead steer of 2026-10-24 turned this default ON and added the `ncomp > 1` guard - see *Guard, default flip, and four more lanes*. The paragraph that follows records the Phase-2 state as it was measured.

**The selector is behind a switch and the switch is off by default.** `SFS_WALK_SEL=1` enables it;
unset or `0` leaves the shipped walk untouched (`bool sel275 = false;` before `bool fell275 = false;`,
gate `if (sel275 && fullWalk263 && stopFired275 && frac275 > 0.30) {`). Shipped defaults are unchanged:
`SFS_STOP_NOFRESH=12`, `SFS_FULL_WALK` on, `SFS_VOTE_ORDER` on, theta untouched, no mesh change, no RNG change.
`git diff --stat`: 1 file changed, 202 insertions(+), 114 deletions(-) (worktree only, uncommitted).

One binary, fifteen runs, one sheet pair per piece (job `33733824` p275final, COMPLETED 0:0, 15:20;
all fifteen `EXIT=0`, sheets unchanged pre->post in every run dir):

| lane | shipped (`sel=0`) | `SFS_WALK_SEL=1` | `SFS_FULL_WALK=0` |
|------|------------------|------------------|-------------------|
| C01 Bl0 | 25 / 51.620 / 0.00 / 0.00, 0 jumps, 5.637 | 208 / 0.649 / 98.56 / 99.05, 0, 3.605 | same as `sel=1` |
| C01 Bl1 | 81 / 41.055 / 0.00 / 0.00, 0, 4.551 | 226 / 0.527 / 100.00 / 99.57, 0, 5.185 | same as `sel=1` |
| J01 Bl0 | 47 / 29.268 / 0.00 / 0.00, 0, 5.632 | 170 / 0.558 / 100.00 / 100.00, 0, 4.203 | same as `sel=1` |
| J01 Bl1 | 82 / 23.306 / 0.00 / 0.00, 0, 4.654 | 184 / 0.596 / 100.00 / 100.00, 0, 4.110 | same as `sel=1` |
| P03 Bl0 | 216 / 0.354 / 100.00 / 100.00, 0, 4.325 | identical | 223 / 0.466 / 100.00 / 99.54, 0, 4.769 |
| P03 Bl1 | 339 / 0.523 / 99.12 / 99.13, 0, 5.187 | identical | 18255 / 13.174 / 5.74 / 42.57, 86, 135.083 |
| P22 Bl0 | 131 / 0.668 / 87.79 / 87.22, 0, 5.304 | identical | 2176 / 4.828 / 15.26 / 88.72, 37, 49.879 |
| P22 Bl1 | 143 / 0.552 / 96.50 / 88.89, 0, 3.975 | identical | 1904 / 4.404 / 16.07 / 79.01, 21, 46.355 |
| P01 Bl0 | 334 / 0.621 / 99.40 / 98.53, 0, 4.580 | identical | 338 / 0.706 / 99.11 / 98.53, 0, 4.970 |
| P01 Bl1 | 346 / 1.011 / 95.66 / 95.45, 0, 4.504 | identical | 349 / 1.066 / 95.99 / 95.74, 0, 5.426 |

Cells are n / med mm / cov ours->author % / cov author->ours % / jumps > 10 mm / max step mm.
Frozen sheets, md5 Surface_0 / Surface_1: Pot_C_01 `6632718baf1a8e41eee3303d97063d87` /
`9ebf2f01644869c5e470e8b29b255ca8` (theta 3.4); Pot_J_01 `abd83ca2497d97a9c85ab385bb8a9d4f` /
`19641b791a295f0d22755086a72a4a9d` (theta 3.4); Pot_D_03 `30b646ab4b2ffdc02e173e38f6a99e79` /
`532fb2765291c00aea8a77db3dfa080b`; Pot_D_22 `8c34c1ee70f52cb1832db566b9f032e9` /
`4bd047d062fbca6f78805d0e878c516e`; Pot_D_01 `ec7d044f6a416623657e611e839c3293` /
`ce44acec2c8c490f0247d75e954e5e9d`.

### The switch is inert when unset, and `SFS_WALK_SEL=1` is the accepted column

All thirty face comparisons (`out2/<tag>` against the column it must reproduce, positions only, row by row)
give `n` identical and `max|dxyz| = 0.000000`; the same holds when both sides are sorted first, so no face is
reordered either. `sel=0` reproduces the pristine shipped binary (25/81/47/82 on C01/J01 and the six guard
faces unchanged); `sel=1` reproduces the accepted selector column from `bf583131` (208/226/170/184);
`SFS_FULL_WALK=0` reproduces ticket 273's `F0` column digit for digit (223/0.466/100.00, 18255/13.174/5.74/86/135.083,
2176/4.828/15.26/37/49.879, 1904/4.404/16.07/21/46.355, 338/0.706/99.11/0/4.970, 349/1.066/95.99/0/5.426) from a
different binary than the one that produced it. PCD bytes differ only in the normal and curvature columns, which
are not reproducible run to run even for one binary (job `33733744`: same-binary reruns agree on positions with
`max|dxyz| = 0` but differ in normals by up to 0.100 and write denormal curvature junk), so the identity gate is
on positions.

### `[WALK-275]` lines, one per face, three configs

```
C01 Bl0 off  [WALK-275] chose=full stopleft=832/986 frac=0.843813 guard=1 fallback=0 sel=0
             [WALK-275] shape arm=full nres=28 L=52.6147 R=7.36219 turn=1 Lr=1.13742 gap=1.8791 maxjump=1.87911 chain=154
C01 Bl0 on   [WALK-275] chose=247 stopleft=832/986 frac=0.843813 guard=1.22322 fallback=1 sel=1
             [WALK-275] shape arm=247 nres=221 L=419.384 R=54.1234 turn=1 Lr=1.23324 gap=1.66499 maxjump=1.89768 chain=716
C01 Bl0 F0   [WALK-275] chose=247 stopleft=0/986 frac=0 guard=1 fallback=0 sel=1
             [WALK-275] shape arm=247 nres=221 L=419.384 R=54.1234 turn=1 Lr=1.23324 gap=1.66499 maxjump=1.89768 chain=716
J01 Bl1 on   [WALK-275] chose=247 stopleft=600/883 frac=0.679502 guard=1.19308 fallback=1 sel=1
             [WALK-275] shape arm=247 nres=197 L=374.966 R=48.383 turn=1 Lr=1.23344 gap=1.68121 maxjump=1.90339 chain=600
P03 Bl0 on   [WALK-275] chose=full stopleft=0/718 frac=0 guard=1 fallback=0 sel=1
P22 Bl1 on   [WALK-275] chose=full stopleft=1/425 frac=0.00235294 guard=1 fallback=0 sel=1
             [WALK-275] shape arm=full nres=151 L=287.768 R=24.1731 turn=1 Lr=1.89465 gap=1.6659 maxjump=1.90576 chain=424
P03 Bl1 F0   [WALK-275] shape arm=247 nres=19159 L=36402.8 R=59.6789 turn=-1 Lr=97.0809 gap=1.90237 maxjump=1.90271 chain=1122
```

`frac=0` on every guard lane: the selector can only fire when the stop rule fires, and on single-component
bags it never fires (P22 Bl1 fires once, `1/425 = 0.0024`, far under the 0.30 gate).

### Acceptance items 1-6

1. **PASS** — C01 Bl0 208 / 0.649 / 98.56, C01 Bl1 226 / 0.527 / 100.00, J01 Bl0 170 / 0.558 / 100.00,
   J01 Bl1 184 / 0.596 / 100.00, zero jumps on all four, author-side coverage 99.05-100.00.
2. **PASS** — P03 Bl1 339 / 0.523 / 99.12 (needs cov >= 99.0, med <= 0.6); P22 Bl1 143 / 0.552 / 96.50
   (needs cov >= 96.0, med <= 0.6).
3. **PASS** — P03 Bl0 and P22 Bl0 are bit-identical to their shipped faces (216 / 0.354 / 100.0 and
   131 / 0.668 / 87.8), i.e. no movement at all, inside the +-2 / +-0.15 / +-1.0 tolerance.
4. **PASS** — P01 Bl0 334 / 0.621 / 99.4 and P01 Bl1 346 / 1.011 / 95.7, also bit-identical to shipped.
5. **PASS** — every row above prints both directions (`cov_o` and `cov_a`).
6. **PASS** — `F0` reproduces the 273 column digit for digit and `sel=0` reproduces the pristine binary.

P22 Bl0 stays below bar (87.79) in every config, exactly as ticket 273 recorded it; the selector neither
helps nor hurts it, because its bag is single-component.

## Mechanism — the census that explains the selector (added 2026-10-24)

Diagnostic-only binary `69ec2e4f2b2b4f94286805f02f3b5042` (job `33733622`) prints the connected-component
census of the bag behind `SFS_LUMP_PROBE=1` and dumps every dot with its component label behind
`SFS_LUMP_DUMP`; jobs `33733654` / `33733655` (both COMPLETED 0:0) produced the dumps, `lumps275.py` turned
them into the table. "author dots" = author dots within 2 mm of any dot of that lump.

| lane | bag | lumps (size -> author dots), seed lump marked * | seed -> largest lump |
|------|-----|---------------------------------------------------|----------------------|
| C01 Bl0 | 986 | 716 -> 208, 114 -> 0, 79 -> 0, 77* -> 0 | 49.69 mm |
| C01 Bl1 | 1090 | 825 -> 230, 265* -> 0 | 27.42 mm |
| J01 Bl0 | 832 | 580 -> 176, 127* -> 0, 75 -> 0, 50 -> 0 | 26.10 mm |
| J01 Bl1 | 883 | 600 -> 188, 283* -> 0 | 12.57 mm |
| B01 Bl1 | 1150 | 752 -> 217, 398* -> 0 | 18.26 mm |

Every other lane in the set is single-component: B01 Bl0 700 -> 210; H02 Bl0 493 -> 156, Bl1 486 -> 102;
H10 Bl0 379 -> 101, Bl1 338 -> 68; C03 Bl0 662 -> 191, Bl1 1126 -> 64 (its author file holds 120 dots);
P03 718 -> 219, 1122 -> 339; P22 492 -> 121, 425 -> 148; P01 431 -> 334, 427 -> 339.

**The four collapsed lanes are the only multi-lump bags in the ten-lane set, and every debris lump carries
exactly zero author dots while the largest lump carries all of them; the seed sits in a debris lump 12.57-49.69 mm
away, i.e. always more than `R = 12 mm` from the rim, so the stop rule fires on the first hop out and the chain
dies at the debris lump.** The selector then rebuilds from the largest lump, which is why its chain length equals
that lump size in every case (716, 825, 580, 600).

Two consequences worth recording. (a) Pot B piece 01 Bl1 has the same debris-seed disease outside Pot C/J
(398-dot seed lump, 0 author dots, 18.26 mm out; its 272 state is 0.89 / 58.4, off bar), so the selector is not
a Pot C/J special case. (b) Pot H P02 Bl1 (0.74 / 73.0), Pot H P10 Bl1 (0.64 / 72.8) and Pot C C03 Bl1
(2.01 / 48.4) are single-component, so their off-bar state is not a debris seed: a "start on the largest lump"
rule could not move them, and the 73% there is a real arc the walk never reaches. The author-dot count is what
separates debris from rim, and on this evidence the selector is a keeper rather than a stopgap for the debris
case only.

## Job ledger

| job | name | state | exit | elapsed | purpose |
|-----|------|-------|------|---------|---------|
| 33733571 | p275acc | COMPLETED | 0:0 | 12:36 | shipped vs selector vs F0 on the six guard faces |
| 33733622 | p275build | COMPLETED | 0:0 | — | census/dump probe binary 69ec2e4f |
| 33733654 | p275lumpA | COMPLETED | 0:0 | 01:19 | census dumps: C01, J01, B01, H02, H10, C03 |
| 33733655 | p275lumpB | COMPLETED | 0:0 | 00:42 | census dumps: P03, P22, P01 |
| 33733744 | p275det | COMPLETED | 0:0 | 02:05 | determinism control, two reruns per binary on P03 |
| 33733810 | p275build3 | COMPLETED | 0:0 | 01:10 | rebuild with the `SFS_WALK_SEL` switch -> 0adfb2db |
| 33733824 | p275final | COMPLETED | 0:0 | 15:20 | the fifteen-run table above |

Run dir: `SfSpp/runs/20261024-0500_1308298_p275-accept/` (`out2/` = the fifteen runs, `final2.txt` = the
scoring + identity output, `lump_table.txt` = the census, `score_acc.txt`, `ident_acc.txt`, `det_acc.txt`).

## Guard, default flip, and four more lanes (added 2026-10-24, lead steer m00773)

### The guard

The gate is now

```
if (sel275 && fullWalk263 && stopFired275 && frac275 > 0.30 && ncomp > 1) {
```

and the `[WALK-275]` line carries `ncomp=` so the guard is auditable from a log alone. Reason: a
SINGLE-lump bag can also stop early, and on one the fallback arm is the explosion we already measured -
Pot_D piece 03 Bl1 with `SFS_FULL_WALK=0` gives 18255 dots, 86 jumps > 10 mm, 135.083 mm max step,
med 13.174 / cov 5.74. `frac > 0.30` is reachable on a sparse one-lump rim: Pot_C piece 03 Bl1 stops at
`706/1126 = 0.6270` with `ncomp=1` today, so before the guard the selector would have fired there.
`ncomp` is the existing 5 mm component count from the `[FULL-263]` line; nothing new is computed.

### Two binaries

- Guard only, selector still opt-in: `89926f792c344464a5832c2a7812985f`, source
  `60982b6c9541f377936bce5eed8ffcdd`, job `33734025` COMPLETED 0:0. Used for the 18-run A/B in
  `runs/20261024-0556_1308298_p275-guard` (job `33734050` COMPLETED 0:0, 04:09, all `EXIT=0`), where
  `SFS_WALK_SEL=1` and `SFS_WALK_SEL=0` were set explicitly so the default could not confound the guard test.
- Final, selector ON by default (`bool sel275 = true;`, `SFS_WALK_SEL=0` the explicit opt-out):
  `bb2e53875afecfb892188ecdd35073e7`, source `9b4a7a239dfe866764b7f69eb8034f54`, job `33734084`
  COMPLETED 0:0. Used for the 19-run table in `runs/20261024-0604_1308298_p275-ship` (job `33734098`
  COMPLETED 0:0, 04:21, all `EXIT=0`). `strings | grep -c WALK-275` = 3 on both.

`git diff --stat`: 1 file changed, 204 insertions(+), 114 deletions(-), uncommitted.

### Ten lanes, final binary (job 33734098)

Cells are n / med mm / cov ours->author % / cov author->ours % / jumps > 10 mm / max step mm, then the
bar verdict.

| lane | shipped default (= selector) | `SFS_WALK_SEL=0` (pristine) |
|------|------------------------------|-----------------------------|
| C01 Bl0 | 208 / 0.649 / 98.56 / 99.05, 0, 3.605 PASS | 25 / 51.620 / 0.00 / 0.00, 0, 5.637 below |
| C01 Bl1 | 226 / 0.527 / 100.00 / 99.57, 0, 5.185 PASS | 81 / 41.055 / 0.00 / 0.00, 0, 4.551 below |
| J01 Bl0 | 170 / 0.558 / 100.00 / 100.00, 0, 4.203 PASS | 47 / 29.268 / 0.00 / 0.00, 0, 5.632 below |
| J01 Bl1 | 184 / 0.596 / 100.00 / 100.00, 0, 4.110 PASS | 82 / 23.306 / 0.00 / 0.00, 0, 4.654 below |
| P03 Bl0 | 216 / 0.354 / 100.00 / 100.00, 0, 4.325 PASS | 216 / 0.354 / 100.00 / 100.00, 0, 4.325 PASS |
| P03 Bl1 | 339 / 0.523 / 99.12 / 99.13, 0, 5.187 PASS | 339 / 0.523 / 99.12 / 99.13, 0, 5.187 PASS |
| P22 Bl0 | 131 / 0.668 / 87.79 / 87.22, 0, 5.304 below | identical to default |
| P22 Bl1 | 143 / 0.552 / 96.50 / 88.89, 0, 3.975 PASS | identical to default |
| P01 Bl0 | 334 / 0.621 / 99.40 / 98.53, 0, 4.580 PASS | identical to default |
| P01 Bl1 | 346 / 1.011 / 95.66 / 95.45, 0, 4.504 PASS | identical to default |

The guard costs nothing that was measured: all ten `default` faces reproduce the accepted `SFS_WALK_SEL=1`
column with `max|dxyz| = 0.000000` and the same n, and all ten `SFS_WALK_SEL=0` faces reproduce the pristine
shipped column with `max|dxyz| = 0.000000` and the same n (checked row by row, positions).
The guard-only binary gives the same identity against the same two columns (18-run batch,
`score_guard.txt`), so the guard and the default flip are both no-ops on the ten lanes.

### Four more lanes, final binary (jobs 33734050 and 33734098)

| lane | bag / ncomp | frac at stop | shipped default (= selector) | `SFS_WALK_SEL=0` |
|------|-------------|--------------|------------------------------|------------------|
| B01 Bl0 | 700 / 1 | 0 | 205 / 0.625 / 100.00 / 100.00, 0, 3.879 PASS | identical |
| B01 Bl1 | 1150 / 2 | 0.6539 | **307 / 0.661 / 97.39 / 99.08, 0, 4.747 PASS** | 126 / 26.351 / 0.00 / 0.00, 0, 6.190 below |
| H02 Bl0 | 493 / 1 | 0.0041 | 153 / 0.680 / 100.00 / 100.00, 0, 3.179 PASS | identical |
| H02 Bl1 | 486 / 1 | 0 | 138 / 0.663 / 73.19 / 74.45, 0, 3.771 below | identical |
| H10 Bl0 | 379 / 1 | 0 | 98 / 0.642 / 100.00 / 100.00, 0, 4.404 PASS | identical |
| H10 Bl1 | 338 / 1 | 0 | 96 / 0.716 / 68.75 / 76.14, 0, 4.384 below | identical |
| C03 Bl0 | 662 / 1 | 0 | 187 / 0.641 / 99.47 / 99.48, 0, 4.159 PASS | identical |
| C03 Bl1 | 1126 / 1 | **0.6270** | 124 / 2.010 / 47.58 / 47.50, 0, 4.087 below | identical |

Readings:

- **B01 Bl1 is the second debris case and it is fixed by the selector**: multi-lump (1150 = 752 -> 217 author
  dots, 398* -> 0, seed 18.26 mm out), it goes from 126 / 26.351 / cov 0.00 to 307 / 0.661 / 97.39 with
  author-side 99.08. `[WALK-275] chose=247 stopleft=752/1150 frac=0.653913 guard=1.32171 fallback=1
  ncomp=2 sel=1` and `shape arm=247 nres=364 L=692.032 R=48.7505 turn=1 Lr=2.25927 ... chain=751`.
  Note chain = 751 against a 752-dot largest lump: one dot short, the only lane where chain and lump size
  disagree (716/716, 825/825, 580/580, 600/600 elsewhere). It does not cost coverage - 99.08 author-side.
- **C03 Bl1 is exactly the hazard the guard exists for**: one lump, `frac = 0.6270`, so without `ncomp > 1`
  the fallback would have fired. With the guard the face is bit-identical to shipped.
- **What the guard prevented on C03 is small, not an explosion** - the counterfactual is on the record:
  `SFS_FULL_WALK=0` on that piece gives Bl1 124 / 2.028 / 45.16 / 43.33, i.e. slightly worse than the
  shipped 47.58, with no jump explosion (14 s run). The explosion evidence stays where it was measured:
  P03 Bl1 `F0` = 18255 dots / 86 jumps / 135.083 mm. The guard is justified by the mechanism, and on the
  lanes available it is a small-degradation preventer rather than an explosion preventer.
- **H02 Bl1 and H10 Bl1 stay off bar in every configuration** (73.19 and 68.75 ours->author), single-lump,
  no fallback possible under the guard. These are the real 27-31% arcs, not debris seeds - a
  start-on-largest rule cannot move them and the selector does not pretend to.
- P22 Bl0 stays 87.79 below bar with the selector on, as in every earlier config (single-lump, `frac = 0`).

All eight faces reproduce bit-identically between the guard-only binary (explicit env) and the final binary
(default and opt-out): `max|dxyz| = 0.000000`, same n, in every comparison.

### Follow-up, not built here

The cleaner long-term shape is to RE-SEED the full walk on the largest lump and keep one code path, instead
of switching arms mid-walk. That would retire both the selector and the `SFS_FULL_WALK` split. It is out of
scope for ticket 275 and must not be built under it.

## Lead verdict (2026-10-24) — accepted, then HELD by decision

**Phase 0 is the finding, and it is accepted.** Theta is disproved: rebuilding Pot C 01 and Pot J 01 at 3.4
reproduces the collapsed lanes to within 0.1 mm (25 / 51.620, 81 / 41.055, 47 / 29.268, 82 / 23.306). The
collapse is a SEED problem — the walk starts at the dot nearest the cloud centroid, which on four lanes sits
inside a debris lump 32-54 mm from the rim, so the stop rule correctly ends the walk on the wrong structure
after 84 % of the dots are left unvisited. The census settles the question the lead asked for: **every debris
lump carries exactly zero author dots within 2 mm, and the largest lump carries all of them** (C01 Bl0 716->208
vs 114/79/77 -> 0; C01 Bl1 825->230 vs 265 -> 0; J01 Bl0 580->176 vs 127/75/50 -> 0; J01 Bl1 600->188 vs
283 -> 0; B01 Bl1 752->217 vs 398 -> 0). So the fallback is not choosing between two legitimate arms on these
lanes; it is choosing the structure the author actually traced.

**Phase 2 acceptance, item by item** (med <= 2.0 and cov >= 90 to reach bar; zero jumps):

| item | requirement | measured | verdict |
|---|---|---|---|
| 1 | C01 Bl0 / C01 Bl1 / J01 Bl0 / J01 Bl1 reach bar, author-side >= 99 | 208 / 0.649 / 98.56 / 99.05 ; 226 / 0.527 / 100.00 / 99.57 ; 170 / 0.558 / 100.00 / 100.00 ; 184 / 0.596 / 100.00 / 100.00 | PASS |
| 2 | P03 Bl1 >= 99.0 / <= 0.6 ; P22 Bl1 >= 96.0 / <= 0.6 | 339 / 0.523 / 99.12 ; 143 / 0.552 / 96.50 | PASS |
| 3 | P03 Bl0 216 / 0.354 / 100 and P22 Bl0 131 / 0.668 / 87.8 unmoved | identical, max abs dxyz 0.000000 | PASS |
| 4 | P01 Bl0 334 / 0.621 / 99.4 and P01 Bl1 346 / 1.011 / 95.7 unmoved | identical | PASS |
| 5 | scorer prints both directions | both columns present on all 18 lanes | PASS |
| 6 | unchosen arm reproduces its 273 column | opt-out reproduces the **Phase 0** columns (25 / 51.620 etc.), not the 273 columns, because 273 ran on the theta = 4.0 sheets | PASS against the corrected reference |

Item 6 needed re-referencing rather than waiving: ticket 273's table was measured on Pot C/J surfaces built at
theta 4.0, and this ticket's lanes use the 3.4 rebuild, so the only valid "did the other arm stay itself"
reference is the Phase 0 table. Recorded so a later reader does not treat the difference as a regression.

**Then the user held it.** Decision (m01572): *"hold the walk selector, it will be not needed if merge cluster
is the missing step."* Correct order — the selector patches a seeding symptom, and if the 22.5 % of the cloud
that never becomes a surface (ticket 276, Phase 0b) is where the missing arcs live, the whole comparison is
being run on a cloud that is missing the rim. Consequence, recorded as the state of this ticket:

- **Nothing lands from this ticket.** `sel275` stays off in main; main's `edgeline_extraction_headless.cpp`
  remains pristine (md5 11c84dee5a4a2dc6a2c91825cc1f87e3).
- The diff is preserved outside the worktree as `.scratch/pota-repro/patches/275-walk-selector.patch` in the
  same commit as this verdict, because a laptop worktree is not durable storage: on 2026-10-24 the sibling
  trees C:/PR/SfSpp_preprocessing-239..-259 disappeared from disk and took every uncommitted artefact with
  them. A held diff that exists in one worktree is a diff waiting to be lost.
- What would turn the hold into a landing: ticket 276 Phase 0b showing the missing arcs are **edge-stage**
  misses on real surface points (merge innocent), which leaves the seeding defect as the thing to fix; or a
  later decision to ship it off by default with `SFS_WALK_SEL=1` per run.
- What would kill it: Phase 0b showing the arcs are inside dropped clusters. Then the arc must be recovered at
  the mesh stage first and this ticket is re-scored on rebuilt surfaces, not on these.

