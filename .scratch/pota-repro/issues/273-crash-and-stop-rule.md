# 273 — The shipped defaults crash and stub: name the crash, then decide retire-or-guard

Answers: E1
Status: results-in
Working in: C:/PR/worktrees/sfs/273 (worktree at e060f87) + Spartan run trees; main source read-only, NO main commits
Needs-eye: no

## Why

Ticket 272 (e060f87) probed the shipped defaults on 10 off-bar lanes and 4 controls:
2/10 reached bar, 0/4 controls left it, so no rollout. Two things outrank the score:

1. **Pot_C_01 segfaults the edge stage** (`exit 139`, zero breakline files), reproducibly, on
   the source tree's own sheets and on three independent sheet draws.
2. **Four lanes collapse to stubs**: C C01 Bl0 317 -> 25 dots (cov 0.0), C C01 Bl1 359 -> 81
   (cov 0.0), J P01 Bl0 249 -> 25 (cov 0.0), J P01 Bl1 255 -> 184. The log names the mechanism:
   `[STOP-267] CHAIN-END step=88 of 1000 ... left=911 dots unvisited` -> `resampled=14`.

The stop rule was tuned on six lanes from three pots whose worst guard step was 4.69 mm.
Pot C and Pot J were never in that set. It may be firing on legitimately sparse rim.

## Goal

Three questions, answered in this order, with numbers:

**A. Name the crash.** Reproduce Pot_C_01 on a frozen sheet pair with shipped defaults and get a
backtrace (`gdb -batch -ex run -ex bt`, or `catchsegv`, or a core with `ulimit -c unlimited`).
Report the function and line. If the fault is in a path the strip touched, say which line.
**Report A immediately — do not run B before A is reported.**

**B. Attribute the collapse.** Edge stage only, no mesh in the loop, one frozen sheet pair per
piece (record both md5s). Configurations, everything else at shipped defaults:

| id | env |
|---|---|
| D | shipped defaults (no behaviour env) |
| S0 | `SFS_STOP_NOFRESH=0` (stop rule off) |
| F0 | `SFS_FULL_WALK=0` |
| V0 | `SFS_VOTE_ORDER=0` |

Lanes: the four collapsed (C C01 Bl0, C C01 Bl1, J P01 Bl0, J P01 Bl1) plus guards
(P03 Bl0, P03 Bl1, P22 Bl0, P22 Bl1, P01 Bl0, P01 Bl1).
Score every lane the ticket-272 way (n / med / cov / jumps / maxjump vs its own author lane).

**C. Retire or guard, decided by a rule written before you run C.** The stop rule exists to refuse
one 124 mm final-closure jump on a P03-Bl1 bag that carried a 76-dot satellite at 47 mm. Ticket 271's
theta = 3.4 removed that lip from the surface, so the bag may no longer exist.

- **R1 — retire.** If S0 restores all four collapsed lanes to their old dot counts (within 10 %)
  AND P03 Bl1 with S0 still reaches bar (med <= 2.0, cov >= 90), then the rule is a cure for a
  symptom that no longer occurs: recommend **default off** (`stopR267 = 0`), no new mechanism.
- **R2 — guard.** If S0 restores the lanes but P03 Bl1 falls below bar with S0, implement exactly
  ONE guard: the stop may fire only when (i) the chain has already visited >= 90 % of the eligible
  dots, OR (ii) the current point is within R of the chain's seed (loop already welded). Pick one,
  pre-register the threshold, validate on all 10 lanes, and STOP if either guard fails.
- **R3 — exonerate.** If S0 does not restore the lanes, the stop rule is not the cause: report which
  configuration does restore them (F0 or V0) with the table, and stop.

## Boundary

- Any code change lives in the 248 worktree only, behind an env switch, default unchanged.
- Do not change theta, do not change the RNG, do not touch `mesh_processing_headless.cpp`.
- Frozen sheets for the whole ticket: one pair per piece, md5 recorded per row. If a pair must be
  rebuilt, say why and record both.
- Do not commit to main. Ticket text lands in `C:/PR/SfSpp_preprocessing/.scratch/pota-repro/issues/`.

## Acceptance

1. A crash site named to function + line, with the backtrace quoted.
2. A 10-lane x 4-config table (D / S0 / F0 / V0) with n, med, cov, jumps, maxjump and sheet md5s.
3. One of R1 / R2 / R3 stated with the numbers that trigger it.
4. If R2: the guard's diff, its env switch, and the 10-lane validation table.

## Evidence to report

Backtrace text; the per-lane table; the log lines proving which config ran
(`[STOP-267] R=...`, `[FULL-263]`, `[VOTE-247]`); job ids and sacct State/ExitCode; sheet md5s.

## Results (2026-10-24)

Status: results-in. Every number below comes from the **POTA-274 fixed edge binary** (67ff3d7 + the
k-clamp, ticket 274), because the shipped binary cannot produce the D column at all on Pot_C_01 — it
segfaults. The crash itself stays on the record here and in 274.

### A. The crash, named

Reproduced 4/4 on the frozen Pot_C_01 pair with shipped defaults and no debugger (job `33732190`,
COMPLETED 0:0): exit 139, zero breakline files. Readable backtrace from a `-g` rebuild of the same
source (jobs `33732191` COMPLETED 0:0, `33732230`, `33732255`), host gdb attached to the container
process:

```
Program received signal SIGSEGV, Segmentation fault.
#0  detectSeparateLineSegments(...)  edgeline_extraction_headless.cpp:2257
#1  processFragmentData(...)          edgeline_extraction_headless.cpp:3377
#2  main                              edgeline_extraction_headless.cpp:3700
```

The faulting instruction reads a `float3` at `rawBreaklinePts->points[nn_indicesAll[i]].x` with
`rax = 0xfffffffbd36acf40` (garbage), stride 16 = `sizeof(pcl::PointXYZ)`, `i = 12` while the cloud
holds 11 valid indices. Root cause: `:2239` asks `nearestKSearch(pt, 20, ...)`; PCL 1.9
`kdtree_flann.hpp:139-143` clamps `k` to the cloud size and **resizes both result vectors down**, but
the loop at `:2240` still read slots `11..19` unchecked. It is **not** in a path the strip touched —
pre-existing released code, already seen once in ticket 216 and once in 248, made common by the stop
rule (a truncated chain is a short chain). Fixed under ticket 274 (9 insertions / 5 deletions, no env
switch); the six guard lanes are bit-identical under it.

### B. The matrix

Edge stage only, no mesh in the loop, one frozen sheet pair per piece, five pieces, 4 configs.
Scored the ticket-272 way against each lane's own author file
(`/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines/<Pot>_Piece_<NN>_Breakline_<st>.pcd`):
`med` = median nearest author distance (mm), `cov` = % of fresh dots within 2 mm, `jumps` = consecutive
steps > 10 mm, `maxjump` = largest consecutive step (mm); bar = med <= 2.0 AND cov >= 90.

Collapsed lanes (the four under suspicion):

| lane | cfg | n | med | cov% | jumps | maxjump | bar | stop rule (D only) |
|---|---|---|---|---|---|---|---|---|
| C01 Bl0 | D | 11 | 54.922 | 0.00 | 0 | 2.065 | below | fires: step 88 of 1000, nearest fresh 12.6104 mm > R=12, 911 dots left |
| C01 Bl0 | S0 | 309 | 0.785 | 67.64 | 2 | 61.827 | below | — (no stop line: R=0) |
| C01 Bl0 | F0 | 208 | 0.537 | 100.00 | 0 | 3.110 | **PASS** | fires with d = FLT_MAX at step 710 |
| C01 Bl0 | V0 | 317 | 0.764 | 67.19 | 1 | 99.647 | below | — |
| C01 Bl1 | D | 82 | 41.373 | 0.00 | 0 | 2.934 | below | fires: step 258, nearest fresh 54.649 mm, 815 left |
| C01 Bl1 | S0 | 377 | 0.797 | 60.48 | 0 | 7.757 | below | — |
| C01 Bl1 | F0 | 226 | 0.539 | 100.00 | 0 | 4.003 | **PASS** | — |
| C01 Bl1 | V0 | 359 | 0.714 | 64.35 | 1 | 101.386 | below | — |
| J01 Bl0 | D | 25 | 32.050 | 0.00 | 0 | 5.546 | below | fires: step 129, nearest fresh 16.206 mm, 714 left |
| J01 Bl0 | S0 | 243 | 0.738 | 70.78 | 0 | 6.494 | below | — |
| J01 Bl0 | F0 | 170 | 0.460 | 100.00 | 0 | 4.402 | **PASS** | — |
| J01 Bl0 | V0 | 249 | 0.809 | 70.28 | 1 | 70.803 | below | — |
| J01 Bl1 | D | 184 | 0.646 | 100.00 | 0 | 4.041 | PASS | fires: step 628, nearest fresh 44.602 mm, 94 left |
| J01 Bl1 | S0 | 256 | 0.698 | 72.27 | 0 | 6.924 | below | — |
| J01 Bl1 | F0 | 184 | 0.539 | 100.00 | 0 | 4.321 | **PASS** | — |
| J01 Bl1 | V0 | 255 | 0.808 | 73.33 | 1 | 99.739 | below | — |

Guard lanes:

| lane | cfg | n | med | cov% | jumps | maxjump | bar |
|---|---|---|---|---|---|---|---|
| P03 Bl0 | D | 216 | 0.354 | 100.00 | 0 | 4.325 | PASS |
| P03 Bl0 | S0 | 216 | 0.354 | 100.00 | 0 | 4.325 | PASS |
| P03 Bl0 | F0 | 223 | 0.466 | 100.00 | 0 | 4.769 | PASS |
| P03 Bl0 | V0 | 227 | 0.714 | 96.92 | 0 | 9.850 | PASS |
| P03 Bl1 | D | 339 | 0.523 | 99.12 | 0 | 5.187 | PASS |
| P03 Bl1 | S0 | 339 | 0.523 | 99.12 | 0 | 5.187 | PASS |
| P03 Bl1 | F0 | 18255 | 13.174 | 5.74 | 86 | 135.083 | **below** |
| P03 Bl1 | V0 | 350 | 0.521 | 98.00 | 0 | 6.637 | PASS |
| P22 Bl0 | D | 131 | 0.668 | 87.79 | 0 | 5.304 | below |
| P22 Bl0 | S0 | 131 | 0.668 | 87.79 | 0 | 5.304 | below |
| P22 Bl0 | F0 | 2176 | 4.828 | 15.26 | 37 | 49.879 | below |
| P22 Bl0 | V0 | 137 | 0.420 | 87.59 | 0 | 3.540 | below |
| P22 Bl1 | D | 143 | 0.552 | 96.50 | 0 | 3.975 | PASS |
| P22 Bl1 | S0 | 178 | 0.557 | 78.65 | 0 | 6.397 | **below** |
| P22 Bl1 | F0 | 1904 | 4.404 | 16.07 | 21 | 46.355 | below |
| P22 Bl1 | V0 | 150 | 0.586 | 94.67 | 0 | 6.265 | PASS |
| P01 Bl0 | D | 334 | 0.621 | 99.40 | 0 | 4.580 | PASS |
| P01 Bl0 | S0 | 334 | 0.621 | 99.40 | 0 | 4.580 | PASS |
| P01 Bl0 | F0 | 338 | 0.706 | 99.11 | 0 | 4.970 | PASS |
| P01 Bl0 | V0 | 342 | 0.767 | 98.83 | 0 | 1.979 | PASS |
| P01 Bl1 | D | 346 | 1.011 | 95.66 | 0 | 4.504 | PASS |
| P01 Bl1 | S0 | 346 | 1.011 | 95.66 | 0 | 4.504 | PASS |
| P01 Bl1 | F0 | 349 | 1.066 | 95.99 | 0 | 5.426 | PASS |
| P01 Bl1 | V0 | 359 | 1.010 | 94.43 | 0 | 5.707 | PASS |

Frozen sheets (md5 of `Temp/Data/<Pot>/<Pot>_Piece_NN_Surface_{0,1}.xyz`, one pair per piece, no
rebuild):

| piece | tree | Surface_0 | Surface_1 |
|---|---|---|---|
| Pot_C 01 | pota251_paper_Pot_C_01 | 5c012f0bb17bc620fc39ce7525dcd9bb | d50d499de4e6e2a19a4fdc230a471350 |
| Pot_J 01 | pota259_paper_Pot_J_01 | 17674245c0db65d5f81aebb55f38c423 | 046ccf10bfde1b1f17c3718ac2256c06 |
| Pot_D 03 | pota271T1_P03_FULL | 30b646ab4b2ffdc02e173e38f6a99e79 | 532fb2765291c00aea8a77db3dfa080b |
| Pot_D 22 | pota271T1_P22_G10 | 8c34c1ee70f52cb1832db566b9f032e9 | 4bd047d062fbca6f78805d0e878c516e |
| Pot_D 01 | pota271T1_P01_G10 | ec7d044f6a416623657e611e839c3293 | ce44acec2c8c490f0247d75e954e5e9d |

Proof that each config ran what it says (Pot_C_01 logs):

```
D  [VOTE-247] ON (paper CCW vote-order) / [FULL-263] no-discard kept 1000/1000 (4 comps @ 5mm)
   [STOP-267] CHAIN-END step=88 of 1000: nearest fresh dot 12.6104mm > R=12mm ; refusing it ; left=911 dots unvisited
S0 [VOTE-247] ON / [FULL-263] chain=1000 maxjump=43.182mm / [VOTE-247] chain=1000 turnSum=9.40941 CCW-kept
   -> zero [STOP-267] lines in the whole run (SFS_STOP_NOFRESH=0 turns the rule off; no DIAG)
F0 [VOTE-247] comp-filter kept 711/1000 (comp 0 of 4 @ 5mm) / [VOTE-247] resampled=219 (L=416.206mm)
   -> no [FULL-263] lines: FULL_WALK=0 selects the older comp-filter + vote path
V0 [VOTE-247] OFF (greedy split-walk intact)   x2
```

The S0+DIAG confirmation run (`SFS_STOP_NOFRESH=0 SFS_STOP_NOFRESH_DIAG=1`) printed
`[STOP-267] BEGIN bag=1000 seed=... R=0 rule=OFF` and per-step instrument lines, and produced
**the same lanes as plain S0** (309/377 dots, max|dxyz| = 0.000000 against `C01_S0`): the diagnostic
is inert, as intended.

Reproducibility: two separate runs of the same config on the same sheets give identical positions —
`GATE/C01_FIX` vs `MATRIX/C01_D` max|dxyz| 0.000000 (11 and 82 dots), `C01_S0` vs `C01_S0DIAG`
0.000000 (309 and 377 dots). The `.pcd` **md5 differs between such runs only in the normal columns**
(positions identical), so file hashes are not the reproducibility check here; the scorer reads x/y/z.

Jobs: `33732389` p273mat COMPLETED 0:0 (13 min 13 s, 21 edge runs = 5 pieces x 4 configs plus the
S0+DIAG confirmation); gate job `33732363` COMPLETED 0:0; crash and debug jobs `33732190`,
`33732191`, `33732230`, `33732255` all COMPLETED 0:0.

### C. Verdict: **R1 fires**

- R1 condition 1 — S0 restores all four collapsed lanes within 10 % of their old dot counts: **yes**
  C01 Bl0 309 vs 317 (0.97), C01 Bl1 377 vs 359 (1.05), J01 Bl0 243 vs 249 (0.98), J01 Bl1 256 vs 255 (1.00).
- R1 condition 2 — P03 Bl1 with S0 still at bar: **yes**, 339 dots / med 0.523 / cov 99.12.
- Therefore: R1, retire — recommend the stop rule default off (`stopR267 = 0`, i.e. the shipped
  default becomes `SFS_STOP_NOFRESH=0`), no new mechanism. R2 was not reached; R3 does not apply
  because S0 does restore the lanes.

Two facts the pre-registered rule did not cover, recorded rather than acted on:

1. **S0 costs P22 Bl1 its bar.** P22 Bl1: D 143 dots med 0.552 cov 96.50 PASS -> S0 178 dots med 0.557
   cov 78.65 below. The stop rule fires there at step 423 of 425 (left = 1) with nearest fresh
   36.188 mm, and switching it off changes the chain's end enough to move the lane 35 dots. R1's guard
   condition names P03 Bl1 only, so the rule as written still licenses retirement; a decision that
   weighs all six guards would see this as a cost of retiring.
2. **"Restored" means restored to the old, still-below-bar state.** Under S0 the four collapsed lanes
   come back to 243-377 dots but sit at cov 60.5-72.3 — the same state ticket 272 measured as off-bar
   for the pre-strip binary. The only config that lifts all four to bar is F0 (cov 100.00), and F0
   wrecks P03 Bl1 (18255 dots, cov 5.74, 86 jumps) and both P22 lanes. No single switch fixes the
   collapsed lanes and keeps the guards.

Also recorded: **P22 Bl0 is below bar in every configuration** (D 87.79, S0 87.79, V0 87.59, F0 15.26),
so it is not evidence about the stop rule either way — it was already off-bar before this ticket.

### Bookkeeping

Run directory (new convention): `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-0301_67ff3d7_p273-matrix/`
with `run.json`, `submit.sbatch`, `logs/`, `out/<TAG>/` (21 tags; job `33732389`); one row appended to
`runs/index.tsv` (verdict and human_note left empty). Scripts: `runs273/B_matrix.sbatch`,
`runs273/score273.py`, `runs273/stopdump.py`, `runs273/compare273.py`. Nothing committed to main.


## Lead verdict (2026-10-24) — accepted, and the stop rule does not retire

Every cell of the 10 x 4 table was independently reproduced from the run directory's own exports
(`out/<TAG>/*Breakline_*.pcd`, numpy, each lane against its own author file). n, med, cov, jumps and
maxjump reproduce to rounding. One column the table lacked, and it changes the reading: **author-side
coverage** — the share of the AUTHOR's dots that lie within 2 mm of ours, i.e. the reverse direction.
Scorer: `artifacts/pota275/score275.py` (laptop, read-only over the fetched pcds).

| lane | D (shipped) | S0 (stop off) | F0 (full walk off) | V0 (vote off) |
|---|---|---|---|---|
| C01 Bl0 | 11 dots, cov 0.0, auth 0.0 | 309, 67.6, auth 100, maxjump 61.8 | **208, 100.0, auth 100, maxjump 3.1** | 317, 67.2, auth 100, maxjump 99.6 |
| C01 Bl1 | 82, 0.0, 0.0 | 377, 60.5, 100, 7.8 | **226, 100.0, 100, 4.0** | 359, 64.3, 100, 101.4 |
| J01 Bl0 | 25, 0.0, 0.0 | 243, 70.8, 100, 6.5 | **170, 100.0, 100, 4.4** | 249, 70.3, 100, 70.8 |
| J01 Bl1 | 184, 100.0, 99.5 | 256, 72.3, 99.5, 6.9 | **184, 100.0, 99.5, 4.3** | 255, 73.3, 99.5, 99.7 |

Median distance is 0.46-0.81 mm in every cell that has coverage; D's median is 32-55 mm only because its
stub sits 55 mm off the author's line.

**Decision: R1 is not executed — the stop rule stays.** The pre-registered rule fires on its letter; the
matrix it was written against shows the letter is the wrong test. Three reasons, in order of weight:

1. **Retirement does not reach bar.** S0 returns the four lanes at 60.5-72.3 precision with largest steps of
   6.5-61.8 mm; V0 at 64-73 with steps to 101 mm. Their author-side coverage is 100, so they touch the whole
   rim and wander over it. "Restored" means restored to off-bar, and retiring also costs P22 Bl1 its bar
   (96.5 -> 78.7). Retiring buys nothing and spends a guard.
2. **Dot count cannot see a detour.** R1 tested "S0 restores the four lanes" by count alone. A count is blind
   to a 101 mm jump between two dots, which is precisely the failure these four lanes have.
3. **The best cell keeps the rule on.** F0 leaves the stop rule active and produces the cleanest lines these
   four lanes have ever shown — 100 precision, 100 author coverage, maxjump <= 4.4 mm, zero jumps, median
   0.46-0.54 mm. A story in which the stop rule causes the collapse cannot explain its own best cell.

### What the matrix did establish: the two walkers own different lane classes, and the component structure says which

- C01 Bl0's bag is 1000 dots in 4 components; the rim is the largest at **711 (71%)**. C01 Bl1 1074 in 2,
  largest 815. J01 Bl0 844 in 4, largest 586. J01 Bl1 723 in 2, largest 629.
- The full walk ignores that structure. It seeds at the centroid-nearest dot, follows whichever small
  structure it lands in, and after 89 (C01 Bl0), 258 (C01 Bl1) and 129 (J01 Bl0) dots the nearest fresh dot
  is 12.6 / 54.6 / 16.2 mm away — so the stop rule ends the walk, correctly, on the wrong structure. With the
  rule off the same walk leaps that gap and drags the debris field into the line, which is where the
  61-101 mm steps come from.
- On P03 Bl1 the bag is **1122 dots in ONE component** at the shipped theta=3.4 — the 1121-dot
  two-row bag (1045 + a 76-dot satellite) of the theta=4 era is gone, because the 3.4 trim severs the
  roll-over lip (ticket 271). So "keep the largest component" keeps everything there and the damage is
  **the angular sort itself**, not a braid: F0 explodes (18255 dots, cov 5.74, 86 jumps = ~35 m of path
  at 1.9 mm spacing for a ~600 mm rim) while V0, which walks dot to dot, is fine (350 / 0.521 / 98.00).
  The no-discard walk holds (D: 339 / 0.523 / 99.12).
  CORRECTION (2026-10-24, lead): an earlier version of this bullet called that bag a double-cover braid.
  That was measured on the theta=4 sheets and does not describe the shipped bag; the log line that
  settles it is `[FULL-263] no-discard kept 1122/1122 (1 comps @ 5mm)`.
- P22 is a single component (492 and 425 dots): D holds Bl1 at 96.5, F0 wrecks it (2176 / 4.83). The same
  angular-sort defect, not a doubling.

So the answer is neither a global switch nor a retune. It is: **choose the walker per lane from the shape of
the largest component.** Ticket 275 carries that, with a Phase 1 that must show the criterion separates the
lanes before anything is wired into the default path.

### Two records, not actions

1. **The scorer is one-way.** `cov` in every table so far is ours->author only, so a short clean line scores
   100. That is why the author-side column had to be computed before this table could be read at all. Ticket
   275 must print both directions.
2. **P22 Bl0 stays off-bar in all four configs** (87.8 / 87.8 / 87.6 / 15.3). Unchanged by this ticket; it is
   still the separate parallel-ridge / extent item, not evidence about the walker.

## Comments (lead, 2026-10-24) - the worktree behind this ticket is closed

This ticket's worktree was removed. The commit it was opened at is an ancestor of
`origin/main`, so no commit was stranded; what the tree alone held was the **working-tree
text** - the experimental variant that produced this ticket's numbers - and that is archived:

- `C:/PR/.scratch/workspace-restructure/archive/worktrees-273-275-20261024/` (laptop)
- `/data/gpfs/projects/punim2657/SfSpp/attic/worktrees-273-275-20261024.tar.gz` (project attic,
  md5 `2ee9ea91ea48ce11c4dfe8479c94d5cd`, 65 members, with `-INDEX.md` and `-MANIFEST.tsv`)

MANIFEST.tsv records 53 files with sha1; every member was extracted and `cmp`-verified against
the worktree before `git worktree remove --force` ran. The `Working in:` line above no longer
resolves to a directory - the ticket stays open and its findings are unchanged.
