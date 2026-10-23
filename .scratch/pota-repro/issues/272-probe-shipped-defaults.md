# 272 — Probe the shipped defaults on the lanes that failed last round

Answers: E1
Status: results-in (probe ran 2026-10-24 on 67ff3d7; verdict DO NOT ROLL OUT — 2/10 off-bar; Pot_C_01 segfaults, Pot_J_01 Bl0 collapses)
Working in: C:/PR/SfSpp_preprocessing-248 + Spartan run trees (read-only source; NO rebuild, NO main commits)
Needs-eye: yes (one overlay PNG per probed pot, for the lead)

## Why

Main now ships different defaults than the ones every rollout number was measured on.
At 1a7c68d -> 0650111 the seven pot tickets (250-259, 214 lanes) were scored with
**theta_theta = 4.0 and the greedy edge walk**. Main at 538357c runs
**SFS_PAPER_THETA = 3.4** (mesh stage) plus, at the edge stage, **full walk** (no discard)
and the **stop-at-the-weld rule at 12 mm**, with the five rejected arms physically removed.

Two variables moved at once, so the 214-lane table no longer describes the shipped code.
Rather than re-roll all seven pots blind, score the four pots that carried the failures
first: if the shipped package moves the failure families and leaves the at-bar lanes alone,
the full rollout in ticket 273 is justified; if it does not, we learn that cheaply.

Already measured, not re-run here (ticket 271, three draws): Pot D P03 Bl0 216/0.47/100.0/0
(was 1.81/50.3/1 jump) and Pot D P03 Bl1 339/0.49/99.1/0 (was 3.18/41.9/1 jump 11.1). Both
at bar at 3.4 + full walk + stop; the pot-D half of the crease family is settled.

## Probe set (10 off-bar lanes, 4 pots) and the theta=4 numbers they must be compared against

| Pot | Lane | theta=4 (old) med/cov | len ratio | old verdict | source ticket |
|---|---|---|---|---|---|
| B | P01 Bl1 | 0.87 / 58.8 | 1.89x | MISS (C01-class tail, 1 jump 72.6) | 253 line 45 |
| C | C01 Bl0 | 0.76 / 67.2 | 1.76x | MISS (tail, 1 jump 99.6) | 251 line 40 |
| C | C01 Bl1 | 0.71 / 64.3 | 1.80x | MISS (tail, 1 jump 101.4) | 251 line 41 |
| C | C03 Bl1 | 12.21 / 13.6 | 2.60x | MISS (runaway, rev 40.0) | 251 line 45 |
| H | P01 Bl1 | 0.62 / 64.0 | — | MISS (rev 66.8) | 257 line 70 |
| H | P02 Bl1 | 0.89 / 70.1 | — | MISS (rev 74.5) | 257 line 72 |
| H | P03 Bl1 | 0.73 / 54.9 | — | MISS (rev 67.7) | 257 line 74 |
| H | P10 Bl1 | 0.70 / 68.3 | — | MISS (rev 77.3) | 257 line 88 |
| J | P01 Bl0 | — / — | 1.64x | TAIL (both lanes) | 259 line 62 area |
| J | P01 Bl1 | — / — | 1.65x | TAIL | 259 line 62 area |

Expected mechanism per family (write the expectation down so the result can refute it):
- **Pot H four Bl1 lanes** — ticket 268/270 hypothesis says these are the same past-crest lip
  as Pot D P03 (line rides a few mm out on the roll-over), which theta=3.4 severs. If they do
  NOT move, the hypothesis is dead and Pot H needs its own mechanism ticket.
- **Tails (B P01 Bl1, C C01 both, J P01 both)** — the 267 stop rule + full walk are supposed to
  keep the tracer on the rim instead of appending a long return tail. A tail that survives is a
  different defect from the one 267 fixed.
- **C C03 Bl1 (2.60x, rev 40)** — the runaway class; no mechanism claims it yet. Include it to
  see whether it moves at all.

## Controls (must not leave bar)

One at-bar lane per probed pot, same run, no extra cost: B P02 Bl1, C C02 Bl0, H P01 Bl0,
J P06 Bl0. A control leaves bar if med >= 2.0 mm or cov < 90 where the old table had it at bar.

## Pre-registered go/no-go (written before the run)

ROLL OUT (ticket 273) if **both** hold:
1. at least 6 of the 10 off-bar lanes reach bar (med <= 2.0 mm and cov >= 90, jumps not counted
   against a lane that has no jump > 10 mm), and
2. no control lane leaves bar.

HOLD and re-diagnose if either fails — and report which family refused to move, because that is
the next ticket, not a reason to tune theta further (271 closed that window).

## Goal

1. Take the binaries built from 538357c by the build worker (md5s recorded below when known);
   do not rebuild, do not patch source.
2. Re-extract Pots B, C, H, J with those binaries, env **verbatim** as in tickets 253 / 251 /
   257 / 259 (no theta override, no SFS_* override: defaults only — that is the point).
3. Score every probed lane with **pota266_score.py** against the same author files the pot
   tickets used, and report the delta table: old med/cov -> new med/cov, n, jumps, len ratio,
   per-lane verdict (IMPROVED / HELD / REGRESSED) against the pre-registered rule.
4. One overlay PNG per pot (author black, our lane coloured, 3D + X-Y), so the lead can see
   whether a recovered lane recovered for the right reason.

## Boundary

- Read-only on C:/PR/SfSpp_preprocessing (the laptop checkout). Work in the 248 worktree and on
  Spartan under /data/gpfs/projects/punim2657/sfs-vote-248/.
- No C++ edits, no rebuild, no commits. Report; the lead lands.
- Do not touch the other pods' run trees.

## Acceptance criteria

- All 10 probe lanes + 4 control lanes scored and tabulated against the numbers above.
- Binary md5 + job ids recorded; the log line `[PAPER-234] paper grow: thetaDeg=3.40000` and
  `[STOP-267] ... R=12 rule=ON` quoted from each pot's log (proves the shipped defaults ran).
- The go/no-go verdict computed from the pre-registered rule, not from impression.

## Evidence to report

Delta table, per-pot job ids and sacct State, binary md5s, PNG paths, Spartan tar paths, and one
sentence per family saying whether the written expectation survived.

---

## Results — probe run 2026-10-24 (worker)

**Short version.** The shipped package does not rescue the failing lanes: **2 of the 10
off-bar lanes reached the bar and no control lane slipped**, so the rule written before the
run says **DO NOT ROLL OUT**. The more useful finding is not that count. Two of the four pots
did not sit still — they went somewhere much worse, and one of them now **crashes the
breakline stage**. Those two regressions are not the mesh draw and not the reference: the
same shipped binary, run on the very sheets that produced the old numbers, reproduces the
collapse without a mesh stage in the loop.

### Four corrections to how this ticket was set up

1. **The shipped default is vote-order ON, not OFF.** `edgeline_extraction_headless.cpp:1320`
   reads `bool voteOrder247 = true;`, with `SFS_VOTE_ORDER=0` as the opt-out. An earlier
   `[VOTE-247] OFF` line came from `a8e1f715`, built from the 248 worktree where that arm was
   still opt-in; it is not evidence about the shipped binary. Do not describe the binary as
   greedy.
2. **The binaries are `67ff3d7`, not `538357c`.** `538357c` does not compile: a dangling write
   to the stripped braid-gate statics at `edgeline_extraction_headless.cpp:827`
   (`gateDiag_turnSum`, `gateDiag_L`, `gateDiag_corners`). `67ff3d7` deletes exactly that line.
   Build job 33731268, COMPLETED 0:0, 1:45, six warnings, both targets.
   - `EdgeLineExtractionHeadless` md5 `db7cebb78ed9fc1d69d3622a7fc1ce17`
   - `MeshPreprocessingHeadless` md5 `fb3fd055d30fb08ccce48dba7d49a879`
3. **The earlier six-lane gate (33731308) is not evidence about the strip.** Its mesh lanes ran
   with the default `maxIterations = 30` instead of `SFS_SINGLE_SHOT=1`'s single iteration
   (`mesh_processing_headless.cpp:2049-2051`), so the edge stage was fed a 7.3x denser sheet
   (P01 tree Surface_0 120,907 points against the 271 run's 16,650). Keep its two FAIL rows as
   history; do not carry them forward as regression signal. Run on the 271 sheets, the new
   binary reproduces the accepted 271 table exactly — P03 216/0.35/100.0 and 339/0.52/99.1,
   P01 334/0.62/99.4 and 346/1.01/95.7 — with positions identical to the accepted breaklines.
4. **Which binary made the accepted numbers.** Every rollout number still quoted in this
   ticket was produced by the 271-era binary with an explicit env, not by defaults. The
   defaults are what this ticket measures; the 271 table is the yardstick, not the result.

### What ran

Mesh env pinned verbatim (the pota234/271 pattern), edge stage with **no behaviour env at all**
(none of SFS_VOTE_ORDER / SFS_FULL_WALK / SFS_STOP_NOFRESH / SFS_COMP_*):

```
SFS_PLANE_RULE=0 SFS_PAPER_CHAIN=1 SFS_PAPER_RHOD=1.0 SFS_PAPER_RHON=0.95 SFS_PAPER_RHOC=0.1
SFS_PAPER_RHOINN=0.75 SFS_PAPER_RHOINC=0.25 SFS_SINGLE_SHOT=1        (no SFS_PAPER_THETA)
```

Defaults confirmed in every lane's log:
`[VOTE-247] ON (paper CCW vote-order)`, `[FULL-263] no-discard kept ...`,
`[STOP-267] CHAIN-END ... R=12mm`; mesh side `[PAPER-234] paper grow: thetaDeg=3.40000
kappa=1.00000` and `[PAPER-234] appendix-A merge: rhoD=1.0000 rhoN=0.9500 rhoC=0.1000
rhoInN=0.7500 rhoInC=0.2500`.

Jobs: 33731894 probe (12 tasks, all COMPLETED 0:0), 33731949 four more draws (COMPLETED),
33731967 + 33732044 the attribution control run twice (COMPLETED), 33732035 scoring.
Nothing was rebuilt, patched or tuned.

### Delta table — old theta=4 -> shipped defaults

| pot | lane | old (theta=4) | new n / med / cov / jumps | reading |
|---|---|---|---|---|
| B | P01 Bl1 | 0.87 / 58.8 | 365 / 0.89 / 58.4 / 0 | unchanged — the tail is still there |
| C | C01 Bl0 | 0.76 / 67.2 | 25 / 51.62 / 0.0 / 0 | **collapsed** (317 dots -> 25) |
| C | C01 Bl1 | 0.71 / 64.3 | 81 / 41.04 / 0.0 / 0 | **collapsed** (359 -> 81) |
| C | C03 Bl1 | 12.21 / 13.6 | 124 / 2.01 / 48.4 / 0 | improved, still below bar |
| H | P01 Bl1 | 0.62 / 64.0 | 231 / 0.53 / 100.0 / 0 | **REACHED** |
| H | P02 Bl1 | 0.89 / 70.1 | 137 / 0.74 / 73.0 / 0 | better position, coverage stalls |
| H | P03 Bl1 | 0.73 / 54.9 | 98 / 0.79 / 91.8 / 0 | **REACHED** (just over 90) |
| H | P10 Bl1 | 0.70 / 68.3 | 92 / 0.64 / 72.8 / 0 | better position, coverage stalls |
| J | P01 Bl0 | tail 1.64x | 47 / 29.27 / 0.0 / 0 | **collapsed** |
| J | P01 Bl1 | tail 1.65x | 82 / 23.33 / 0.0 / 0 | **collapsed** |
| B | P02 Bl1 | control | 148 / 0.61 / 100.0 / 0 | at bar |
| C | C02 Bl0 | control | 218 / 0.50 / 100.0 / 0 | at bar |
| H | P01 Bl0 | control | 213 / 0.54 / 100.0 / 0 | at bar |
| J | P06 Bl0 | control | 128 / 0.41 / 99.2 / 0 | at bar |

**Verdict from the pre-registered rule: DO NOT ROLL OUT — off-bar 2/10, controls 0/4 left bar.**
No lane in this run produced a jump longer than 10 mm.

(Goal 3's "len ratio" column was not recomputed; the dot counts carry the same information.
Goal 4's overlay PNGs were **not** produced — this ticket still carries `Needs-eye: yes`.)

### The mesh stage is not reproducible, so a fixed-tolerance gate cannot be trusted yet

Two independent runs, same piece, same pinned env, same input cloud:

| piece | run A sheets | run B sheets | agree? |
|---|---|---|---|
| Pot_H_01 (cloud `c1fb6fe0`) | `ca80a057` / `ef1fb50b` | `80fdb938` / `cdeeee61` | **no** |
| Pot_J_01 (cloud `b75fb455`) | `de143bc6` / `7914d566` | `de143bc6` / `7914d566` | yes |
| Pot_C_01 (cloud `844035fe`) | `6d83a25f` / `414e44c4` | `dbb68382` / `a358e7aa` | **no** |

The mesh stage sometimes reproduces bit-for-bit and sometimes does not. On Pot_H_01 the score
impact was small (Bl0 0.54 -> 0.58, Bl1 0.53 -> 0.65, both still at bar), but the sheets
themselves differ, which is enough to make a fixed-tolerance gate measure draw noise. Seed the
RNG or freeze the sheets before the next gate.

### Why the two catastrophic pieces broke: the edge stage, not the draw and not the reference

Four checks, on Pot_C piece 01 and Pot_J piece 01:

1. **The reference is sound.** The author breaklines lie on this piece's own point cloud:
   Pot_C_01 med 0.61 mm / p95 1.12 / max 1.50; Pot_J_01 0.45 / 0.84 / 1.02;
   Pot_H_01 0.42 / 0.82 / 1.06. Not a wrong-reference case, and not a Bl0/Bl1 swap
   (own Bl0 scores 51.62 mm against author Bl0 and 55.01 mm against author Bl1).
2. **The old binary is still fine on the same sheets.** Old binary + old env on the source
   trees' own sheets reproduces this ticket's rows exactly: C01 Bl0 317 dots 0.76/67.2 (one
   jump 99.6), C01 Bl1 359 dots 0.71/64.3 (jump 101.4), J01 Bl0 249 dots 0.81/70.3,
   J01 Bl1 255 dots 0.81/73.3.
3. **The shipped binary on those same sheets fails, with no mesh stage in the loop.**
   Source tree's own sheets, breaklines deleted, shipped edge defaults:
   - **Pot_C_01: exit 139 (SIGSEGV), zero breakline files — reproduced twice**
     (33731967_0 and 33732044_2, identical logs). Stop-the-line defect, not a scoring question.
   - **Pot_J_01:** Bl0 -> 25 dots, 32.05 mm, 0.0% coverage (was 249 dots, 0.81, 70.3);
     Bl1 -> 184 dots, 0.65, 100.0 (**better** than the old 255 dots, 0.81, 73.3).
4. **The collapse ignores the draw.** Three different sheet sets for Pot_C_01 (`6d83a25f`,
   `7c9e67c3`, `dbb68382`) all give 25 and 81 dots at 51.62 mm and 41.04-41.13 mm, coverage
   0.0%; two of them agree to two decimals. Pot_J_01's two draws are bit-identical and collapse
   identically (47 and 82 dots).

The mechanism is visible in the log, and it is the stop rule firing almost immediately:

```
[FULL-263] no-discard kept 1000/1000 (4 comps @ 5mm)
[STOP-267] CHAIN-END step=88 of 1000: nearest fresh dot 12.6104mm > R=12mm ; refusing it ; left=911 dots unvisited
[FULL-263] chain=89 maxjump=10.4107mm
[VOTE-247] chain=89 turnSum=-1.57241 CW-reversed-to-CCW
[VOTE-247] resampled=14 (L=25.7448mm) corners=0 thr=11.1077 med=3.70257 idx=[]
```

Pot_J_01 Bl0 has the same shape: `CHAIN-END step=129 of 844 ... left=714 dots unvisited`, then
`resampled=29 (L=55.4897mm)`. The tracer stops after roughly a tenth of the rim and the
resample hands back a 14-29 dot stub; the author's lane is many times longer, so coverage is
0% and the nearest-author-dot distance is tens of millimetres. On Pot_J_01 Bl1 the same rule
stopped in a good place and the lane improved — the rule is not simply wrong, it fires on the
wrong frames.

### What each written expectation now says

- **Pot H four Bl1 lanes:** half confirmed. Two reached bar (P01 coverage 64.0 -> 100.0,
  P03 54.9 -> 91.8); two improved in position but stall around 73% coverage (P02 0.74/73.0,
  P10 0.64/72.8). The past-crest-lip mechanism holds where the lanes moved; for P02 and P10 the
  remaining defect is **extent** — the lane covers about three quarters of the author arc — not
  position. Those two need their own mechanism, not more theta.
- **Tails (B P01, C C01, J P01):** not fixed. B is unchanged to the hundredth; C C01 and J P01
  collapsed. Nothing in the shipped package removes a tail.
- **C C03 runaway:** moved a long way (12.21 -> 2.01 mm) but coverage 48.4%, so still below bar.
  No mechanism in this ticket claims it, and nothing here refutes it either.

### Open, not started

1. The Pot_C_01 segfault needs a stack trace before any rollout decision; it reproduces in 13 s.
2. Seed the mesh RNG (or freeze the sheets), otherwise ticket 273's numbers cannot be compared
   to anything.
3. The overlay PNGs (goal 4) are still owed.

### Evidence

All under `/data/gpfs/projects/punim2657/sfs-vote-248/build-67ff3d7/runs272/`:
`results272.txt` (12 probe lanes: input-cloud md5, fresh sheet pair, source sheet pair),
`results272b.txt` (four extra draws), `results272c.txt` (prior-sheet control),
`PRIORBL_C01_PRIORSHEETS/` and `PRIORBL_J01_PRIORSHEETS/` (the old binary's breaklines on those
exact sheets), `probe272_33731894_*.out` and `p272edge_*.out` (per-lane logs, including the two
segfault runs). Scorers: `/data/gpfs/projects/punim2657/sfs-vote-248/score272b.py` and
`probe272_score.py`; scored tables in `/data/gpfs/projects/punim2657/sfs-vote-248/s272b_*.out`.

## Lead verdict (2026-10-24)

**DO NOT ROLL OUT — accepted, and the pre-registered rule was honoured exactly (2/10, 0/4 controls).** No retuning, no cherry-picking a family. The 214-lane table stays the only rollout evidence, and it describes theta=4 + greedy, not the shipped code.

**Stop the line on Pot_C_01.** The shipped defaults segfault the edge stage on a real piece, reproducibly, on the source tree's own sheets and on three independent sheet draws. A default that crashes on a piece in the benchmark cannot ship, whatever its scores are. This outranks every score in this ticket.

**The stop rule is the prime suspect for the four collapses, not yet convicted.** Its own log names the mechanism: `[STOP-267] CHAIN-END step=88 of 1000 ... left=911 dots unvisited` -> `resampled=14 (L=25.7448mm)`. A rule built to refuse one 124 mm final-closure jump is refusing a mid-rim step where the local dot spacing happens to exceed 12 mm. It was tuned on six lanes from three pots (P03/P22/P01) whose worst guard step was 4.69 mm; Pot C and Pot J were never in that set. That is a sampling error in the rule's evidence base, and it is mine — the margin was measured on lanes that could not have shown the failure.

**It may not need fixing at all.** The rule was written for the P03-Bl1 bag that carried a 76-dot satellite at 47 mm. Ticket 271's theta=3.4 removed that lip from the surface; the bag the rule was built for may no longer exist. If theta=3.4 + full walk + stop OFF still puts P03-Bl1 at bar, the rule is a cure for a symptom that no longer occurs, and retiring it is better than guarding it.

**Mesh non-reproducibility is confirmed and now blocks gates.** Same piece, same env, same input cloud: Pot_H_01 and Pot_C_01 give different sheets run to run; Pot_J_01 reproduces bit-for-bit. So `mesh_processing_headless.cpp:1526-1527` (unseeded `std::random_device`) makes a fixed-tolerance gate partly a measurement of draw noise. Every lane in the next ticket reuses ONE frozen sheet pair per piece, and the md5 goes in the row.

**Corrections accepted and recorded:** (a) shipped default is vote-order ON at `edgeline_extraction_headless.cpp:1320`; the OFF line came from `a8e1f715` on the 248 worktree, where the arm was still opt-in. (b) Job 33731308 is not strip evidence — its mesh lanes ran `maxIterations=30` instead of `SFS_SINGLE_SHOT=1`'s 1 (P01 Surface_0 120,907 vs 16,650 points). On the 271 sheets the new binary reproduces the accepted 271 table exactly, so the strip itself remains behaviour-neutral.

**Family read-out, kept as written:** Pot H half cured (P01 100.0, P03 91.8); P02/P10 stall at ~73 % = extent, needs its own mechanism. C C03 moved 12.21 -> 2.01 mm but cov 48.4 %. Tails not fixed anywhere. Nothing here supports a rollout.

**Next: ticket 273** — crash trace first, then the stop rule's attribution and the retire-or-guard decision, all on frozen sheets. Overlay PNGs remain owed (Needs-eye stays open).
