# Ticket 323 — Which lines to hand the assembler: make the candidate set hold every pot

**Status:** resolved
**Answers:** E1
**Depends on:** 322 (the estimator and the Juglet key)
**Blocks:** none
**Worker:** cursor_code (dispatched 2026-11-10, this ticket is the brief)
**Budget:** large

> **Summary (2026-11-10, for the conservator).** Each sherd now hands the reassembly program its best axis
> line, plus any other candidate line that fits the sherd's wall almost as well (wall-thickness cost
> within 1.2 times the best line's), up to three. The ratio is computed per sherd from its own
> measurements, with no millimetre threshold and no per-pot setting. The rule was fixed in writing
> before any test ran.
>
> **Result:** all ten pots reassembled at or above their target on both repeats (20 of 20 runs). The rule
> beat the authors' own axes on Pot D (26 of 28 sherds seated against 23) and Pot H (11 of 11 against 8-10)
> and tied them on the other eight. Pot E reached 31 of 31 sherds and 62 of 62 joins; the three-line set
> had given it 20-29 sherds. Pot G's lost joins came back (10 of 10). The new files differ from the old
> three-line set **only by deleting lines**: every sherd keeps the same first line.
>
> **Why it works:** the program tries every candidate line of every sherd and checks only that the two
> lines used in one join agree, so each extra wrong line is another chance to build a group that fits
> together but is wrong. Extra lines are kept only when they are nearly as good as the best one, which is
> where the right line hides when the first one is wrong.
>
> **Unresolved:** (1) **the Juglet still does not reassemble**: 0 of 9 sherds against the real key, with the
> scoring convention checked, so this is the method failing on a vessel a fifth the size of the pots;
> (2) **the program's own run-to-run variation is untouched**: it can give different answers on identical
> input (earlier tickets), even though every pot here gave the same score on both repeats; (3) the
> renders have not been checked by eye.
> Evidence: `## Comments`, checkpoints 3 (pre-registration), 13 (deletion only) and the final verdict;
> renders in `SfSpp_preprocessing/artifacts/pota323/renders/`.

## The ask

The axis estimator is now better than the one we ship — and it made the *end-to-end* result worse.
That sentence is the whole ticket.

Ticket 322 built a profile-thickness cost for an axis and showed it finds the right axis more often
than the shipped ranker: **135 of 163 pot pieces within 10 deg at its first line, against 107**.
It then handed the assembler the top three of those lines and **broke Pot G**, whose joins fell from
10 to 4-5; one line only and Pot G was fine again but A, E, H and J lost joins instead. Every
combination tried failed a pre-registered rule.

So the open question is no longer "can we find the axis". It is:

> **Given a ranked candidate set for each piece, what decides which lines the assembler gets — so that
> every pot keeps its joins at once, and the same rule works on a vessel we have not tuned for?**

Answer it with one formulation. A per-pot table of line counts is not an answer; it is the thing we
already know how to write and already know does not generalise.

## What is already known (do not re-derive; do check it)

**The estimator (ticket 322, `sfs_axes/profile.py`, landed but imported by nothing):** cost of an axis
on a wall = trimmed mean of the smallest principal std-dev of k=24 nearest neighbours in the (r, z)
plane; piece cost = mean over its two walls; Nelder-Mead on 4 dof about the start. Refined from the
reference axis it moves a median **1.5 deg** (>10 deg on 9/163), against **6.4 deg** (>10 deg on 70/163)
for the distance-invariant normal cost.

**Axis-level table (pieces within 10 deg; rank 0 / best-of-3 / best-of-6):**

| set | pots (163) | Juglet (9) |
|---|---|---|
| `axes320`, shipped today | 107 / 133 / 137 | 4 / 6 / 8 |
| `axes322`, profile ranker | **135 / 146 / 151** | **6 / 8 / 8** |

**End to end, and this is the failure to fix:**

| set | what happened |
|---|---|
| `axes322` top 3 per piece (K=3) | A 8/8 15/15, B, C, F, H, J at floor — **Pot G 7/7 4/10 and 6/7 5/10** (floor 10/10) |
| `axes322` line 1 only (K=1) | G 7/7 10/10, B, C, D, F, I at floor — **A 8/8 9/15, E 26-28/31 44-51/62, H 9/11 11/17, J 6/11 5-8/21** |
| hybrid: profile line 1 + `axes320` lines 2-3, 10 deg dedup | 144/163 pots at best-of-3 against a required 146; A 8->7, H 11->10, I 27->26; Juglet 7 |
| Pot G arms: `axes322` line 1 only, and line 1 + `axes320` lines 2-3 | both **7/7 10/10** |

**The mechanism, measured on Pot G (job 34620128):** the profile ranker's first line is right
(G03 2.0 -> 8.0 deg, others 0.9-10.1 deg, 6 of 7 closer); its **second and third lines sit 16.9-51.8 deg
off** and the assembler latches onto them, failing joins 2-3, 2-6, 4-5, 5-7 at 141-154 deg (repeat 1)
and 79-107 deg (repeat 2). Not a line cap, not a sign flip — a plausible-looking wrong line that the
assembler prefers.

**Why more lines help the others:** A, E, H and J lose joins at K=1, so on those pots the *right* line
is not always ranked first, or the assembler needs an alternative to the one it was given. That is the
tension: alternatives rescue A/E/H/J and destroy G.

## Questions you are being asked (answer them, do not merely report)

1. **What does the assembler actually do with a set of lines?** Read the code, not the docs: how many
   lines does it load per piece, in what order, how does it score a candidate pair, and what makes it
   choose a 141 deg join over a correct one? If a piece's bad line can only be excluded by not shipping
   it, say so; if the assembler's own scoring is the thing that can be fixed, say that too.
2. **Is "how many lines" the right question at all?** Consider that the set could be ordered, could
   carry per-line weights, could be pruned by agreement between lines (two independent methods agreeing
   within N deg), or could be chosen per *piece* by a scale-free confidence rather than per pot. Any of
   these is fair game; a per-pot constant is not.
3. **What kills the bad lines without killing the good ones?** The G failure is a line that is 17-52 deg
   off with a good cost. Find a signal that separates it from the lines A/E/H/J need. Candidate signals
   include (yours to test, not a list to work through): margin between the line's cost and the next
   basin's, basin support size, agreement between the profile cost and the normal cost, agreement
   between independent seeds, and whether the line's implied rim closes.
4. **Does the rule hold on the Juglet?** It is a different regime (33 mm across, near-spherical body) and
   we now have a real key for it — see below. A rule that is right on the ten pots and wrong there is
   not general.
5. **Say what you predict before you run it.** Write the prediction and the pass/fail rule into the
   ticket before submitting the jobs, then report against it. Ticket 322's two pre-registered rules both
   failed and that is the reason its result is trustworthy; keep the same discipline.

## Floors the ten pots must keep (two repeats; a pot counts as held if either repeat reaches it)

| pot | sherds | joins |
|---|---|---|
| A | 8/8 | 15/15 |
| B | 9/9 | 15/15 |
| C | 4/4 | 5/5 |
| D | 23-25/28 | 55-60/69 |
| E | 29-31/31 | 57-62/62 |
| F | 5/5 | 7/7 |
| G | 7/7 | 10/10 |
| H | 11/11 | 17/17 |
| I | 25/26 | 59/62 |
| J | 8/11 | 16/21 |

Juglet: report, do not gate — it has no floor yet. **Score it against
`Dataset/Juglet_GT/Juglet_Piece_N_Axis.xyz`, which now exists** (nine lines fitted to the assembled
vessel, README beside them), and remember that **8 of the 18 pairs in `Juglet_simple_graph.txt` do not
touch in the true pose**, so 18 joins is not attainable: the ten touching pairs are the ceiling.

## Constraints

- **One code path, no per-object constants.** The shipped default (`run_potsac`) and `--union` are one
  path. If a rule needs a threshold, it must be scale-free (a ratio, a quantile) or derived per piece
  from the piece's own numbers — and you must show why it is not a per-pot constant in disguise.
- **Fast loop first.** `t322/dump_basins.py` scores all 172 pieces' basins in 85 s on 8 CPUs and
  `t322/rank_rules.py` scores a ranking rule offline in seconds. Rank offline, prove the axis table, and
  only then spend end-to-end jobs. End-to-end runs are much slower than the axis table and are what
  actually decides.
- **Assembler nondeterminism is real.** The same staged inputs give different scores between repeats
  (Pot E returned 30/31 and 31/31 in one job; H's authors' arm 5/11 then 8/11). Two repeats per arm,
  and never call a one-repeat difference a result.
- **Everything runs on Spartan compute nodes**, never the login node: `ssh spartan`, project root
  `/data/gpfs/projects/punim2657/`, `sbatch` with polling via `sacct` (do not use
  `scripts/slurm_poll.sh`, it exits immediately). Record job IDs and final `sacct` State/ExitCode.
- **The corpus never changes.** Inputs are staged by symlink; compare corpus md5s before/after a run.
- **Renders for any geometry claim**, at a view that resolves the scale, into
  `C:/PR/SfSpp_preprocessing/artifacts/pota323/renders/`. A number about seating without a picture is not
  done.
- **No commits.** Leave the working tree for the lead; write your findings into this ticket.

## Where things are

- Estimator: `C:/PR/SfSpp_preprocessing/sfs_axes/profile.py` (landed, unwired). The ranker that uses it
  is `C:/PR/SfSpp_preprocessing/.scratch/pota-repro/t322/profile_ranker.patch` (`git apply` re-applies it;
  it was reverted after the Pot G diagnosis, deliberately).
- `axes322` (181 files): `/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0415_d628fc0_t322-axes/out/axes322`
- `axes320` (the shipped set) = `.../runs/20261108-1350_e556fc8_t318a-axes/out/axes318` (181 files) with
  **one** file replaced: `Pot_A_Piece_01_Axis.xyz` from
  `.../runs/20261109-1928_97dad1e_t320-potA/work/axes_k3/Pot_A_Piece_01_Axis.xyz` (8 files there; only this
  one differs from `axes318`). Ticket 321 verified that as the whole of the 320 change.
- Ticket 322's end-to-end runs: `.../runs/20261110-0420_d628fc0_t322-pot<A..J>/score/acc.tsv` (K=3) and
  `.../runs/20261110-05*_d628fc0_t322k1-pot<A..J>/score/acc.tsv` (K=1). The Pot G diagnostic:
  `.../runs/20261110-0446_d628fc0_t322-potG-diag`.
- Assembler: `/data/gpfs/projects/punim2657/sfs_main/`, SIF `sfs_pristine_assembly.sif`, batch tool
  `sfspreproc-docker/hpc/tools/main_pristine_batch.cpp`. The paper chain is ticket 308's; the arms are
  built by the `make_e2e_*.sh` scripts in `t322/`.
- Juglet lanes: `.../runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom` (9 pieces x
  Bl0/Bl1/S0/S1); GT: `Dataset/Juglet_GT`.
- Read `C:/PR/AGENTS.md` and `C:/PR/SfSpp_preprocessing/AGENTS.md` first, and ticket 322 in full.

## Definition of done

1. A written answer to the five questions, in this ticket, with the numbers behind it.
2. A stated rule — "for each piece, ship these lines because ..." — in one paragraph, scale-free.
3. End-to-end evidence for the rule: **all ten pots at floor**, two repeats, job IDs and `sacct` states
   recorded; plus the Juglet scored against the real key and reported.
4. If the rule cannot hold all ten, say which pots it cannot hold and why, with the mechanism — a
   measured limit is a result; a table of per-pot exceptions is not.
5. Renders in `artifacts/pota323/renders/` for anything you claim about seating.
6. Working tree left uncommitted, ticket updated with a minimal set of artefacts, and a short
   `## Comments` trail a later reader can resume from cold.

If you conclude the failure is in the assembler's own pair scoring rather than in the axis set, that is
an acceptable answer — but you must show it with the assembler's code and a measured experiment, not
with an argument.

## Comments

### Worker (cursor_code), 2026-11-10 — checkpoint 1: Q1, what the assembler does with a set of lines (code read)

Source read: `C:/PR/structure-from-sherds-pp` at `9a613b5` (the code the pristine SIF is built from —
**to confirm against `/opt/sfs-pristine` in the SIF before quoting as final**).

- **Loading:** every line of a piece's axis file becomes `edge_line_.axis_point_[k]` / `axis_norm_[k]`
  (`class/data_structure.cpp:164`); nothing caps K in the assembler.
- **Features are per line.** The edge-line features (D, H, Theta and thickness; quantised at 0.15 / 0.15 /
  0.15 / 0.2, `feature_matching.cpp:1517-1521`) are computed in the frame of each line separately: for a
  piece with K > 1 lines, `StateManager` aligns the piece to line k and recomputes its features for every k
  (`ranking_system.cpp:776-793`, `AxisAlignment` + `CalculateFeatureAxisless(shard, k)`). **A piece already
  placed in a growing assembly (`state.true_node_[j]`), or one with a single line, gets line 0 only**
  (`ranking_system.cpp:778-779`).
- **Pair scoring:** `FeatureCompGraphBuilding` (`feature_matching.cpp:1497-`) runs the LCS feature match for
  **every piece pair x every line pair** (`axis_x` x `axis_y`), each hit carrying the two line indices
  (`axis_index_x_ / _y_`). Each hit is ICP-aligned; it survives only if (i) after alignment the two lines
  *it used* agree within **0.436 rad = 25 deg** (`feature_matching.cpp:1715`, again `:1853`), (ii) the lowest
  ICP score in its group is <= 1.5 (`:1726`), (iii) no 3-D overlap (`:1729`).
- **Consequence (the mechanism behind Pot G):** a wrong second line on an *unplaced* piece is a second,
  independent description of its edge; it generates its own candidate joins, and the only axis test
  applied to them is that the *two lines used by that one join* agree — not that the piece's line agrees
  with the line the rest of the assembly already sits on. Once such a join seeds or extends a graph, later
  pieces are matched against that graph's frame (placed pieces use line 0 only), so a self-consistent wrong
  group can grow — what ticket 322 saw on G ({2, 5} seated 79-154 deg off the rest).
- **Provisional answer to Q1:** a bad line can be kept out either by not shipping it, or by changing the
  assembler's axis test from "the two lines of this join agree" to "this piece's line agrees with the line
  of the graph it is joining". The second is an assembler change; whether it is in scope, and whether it is
  enough, is not yet measured. Still to read: `GraphAxisRefinement` / `IcpIncGraphAxis` (what happens to a
  placed piece's axis), and how the global search ranks competing graphs.

**Plan for the next turns** (each <= 9 min): (1) finish Q1 in the code above; (2) offline, from
`t322/out/basins_all.json` and `profile_rank.json`: separate Pot G's harmful lines from the lines that A /
E / H / J need, on per-piece scale-free signals (cost margin, basin support, profile-vs-normal agreement,
seed agreement); (3) read the K=1 losses on A / E / H / J from the assembled poses (which joins, which
line would have served) as in 322 checkpoint 9; (4) pre-register a rule and its prediction here; (5) only
then submit end-to-end jobs (ten pots x two repeats, plus the Juglet scored against `Dataset/Juglet_GT`).
### Worker, 2026-11-10 ~07:40 — checkpoint 2: one hypothesis, and the first fast-loop numbers

**SIF source check:** job **34623202** (`runs/20261110-0730_d628fc0_t323-sifsrc`) copies `/opt/sfs-pristine`
out of `sfs_pristine_assembly.sif` on a compute node; the diff against laptop `9a613b5` is next turn.
Checkpoint 1's file:line citations stand only once that diff is clean.

**Hypothesis for this ticket: (a), don't ship the bad line.** Reason: the conservator's standing
instruction is that the axis method generalises, and (a) changes only our output. (b), the assembler's local
25-deg test, is not tested now. It becomes the answer only if (a) cannot separate Pot G's bad lines from the
lines A / E / H / J need.

**Fast loop** (`t323/line_labels.py` on `basins_all.json` + `profile_rank.json`, the refined `ranked` list,
15-deg dedup, K=3). It reproduces 322's rank-0 count: **135/163** pot pieces within 10 deg (A 6/8, B 9/9,
C 5/6, D 27/32, E 32/34, F 6/7, G 7/7, H 9/11, I 25/30, J 9/19; Juglet 6/9). Extra lines (rank 1-2): 29
good, 280 bad.
- **Pot G: rank 0 right on 7/7, all 14 extra lines wrong** (16.9-77.0 deg); its cheapest extra line costs
  **1.32x** its first (G 04). So G needs no extra line, as its K=1 run showed (10/10 twice).
- **Rescue lines** (rank 0 wrong, an extra line right), with error and cost relative to rank 0:
  A06/1 3.9 deg 1.06x, A07/2 8.3 1.50x, C06/2 1.1 1.16x, D18/1 2.9 1.06x, D27/1 2.7 1.03x, E14/1 9.4 1.03x,
  H08/1 1.6 1.13x, H11/1 1.9 1.01x, I27/2 8.4 1.94x, I29/2 9.2 4.27x, J07/1 4.8 1.06x;
  Juglet 7/1 2.6 1.07x, Juglet 3/2 8.6 2.49x.
- **Gate: ship rank k >= 1 only if its cost <= tau x rank 0's cost** (a ratio within one piece, no
  millimetres). Good/bad extra lines kept per pot:

| tau | A | B | C | D | E | F | G | H | I | J | Jug |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.1 | 2/1 | 3/3 | 0/3 | 5/3 | 3/2 | 1/0 | **0/0** | 1/0 | 1/1 | 2/9 | 1/1 |
| 1.2 | 2/1 | 3/3 | 1/4 | 5/11 | 4/7 | 1/3 | **0/0** | 2/2 | 2/4 | 3/17 | 1/3 |
| 1.3 | 2/1 | 3/6 | 2/5 | 5/13 | 4/12 | 1/3 | **0/0** | 2/3 | 2/6 | 3/22 | 1/4 |
| 1.5 | 3/4 | 3/9 | 2/8 | 5/14 | 6/21 | 1/4 | 0/2 | 2/5 | 2/9 | 3/28 | 1/7 |

  At tau 1.2, G gets K=1 and the rescues for A06, E14, H08, H11 and J07 (the K=1 losers' pieces) are kept.
  Lost: A07 (1.50x; its rank 0 is 16.3 deg, inside the assembler's 25 deg), I27, I29 and Juglet 3.
- **Not yet known:** whether the joins lost at K=1 on A / E / H / J are the ones at these rescue pieces.
  Ticket 322 rejected "a cost-ratio gate"; I still have to check what threshold it tested and against what
  before this can be pre-registered. tau must also not be tuned to G's 1.32 (see below).

**Next:** (1) diff the SIF source; (2) read 322's rejected cost gate; (3) map the K=1 joins lost on A / E / H /
J to pieces; (4) pre-register the gate (tau picked from a gap in the good/bad distribution, not from G) and
its per-pot prediction; (5) end-to-end, two repeats.
**SIF job update:** 34623202 FAILED 127:0 after 3 s (`apptainer` not on the compute node's PATH); resubmitted with the full Apptainer 1.3.3 path from 322's scripts as **34623253**, same run directory.

### Worker, 2026-11-10 07:36 — checkpoint 3: PRE-REGISTERED (written before any end-to-end job)

**The rule, one sentence:** each piece gives the assembler its profile-ranked lines (15 deg apart, cheapest
first), keeping the first line and every later line whose profile cost (mean wall thickness) is at most
**1.2x** that piece's own cheapest line, up to three lines.
**One number: tau = 1.2.** The ratio is scale-free: it divides two thicknesses of the same piece, so it has
no millimetres in it, and it is computed per piece from that piece's own costs. The cap of three is
the largest set already run end to end (K=3), not a tuned value.

**Why 1.2, from the fast loop** (`t323/line_labels.py`, K=6 list):
- Rescue lines cluster at 1.01-1.16x; the next one is at 1.50x (A07). Any tau from 1.16 to 1.49 keeps the
  same rescues, so the choice inside that interval only trades away wrong lines.
- **tau 1.15:** loses the C06 rescue (1.16x); pots best-of-3 142 (C 5/5 instead of 5/6). Lines per piece:
  G 1.00 (max 1); A 1.38, H 1.18, J 2.11, E 1.26.
- **tau 1.3:** keeps the same rescues as 1.2 (best-of-3 143) but adds wrong extra lines (B 3 to 6, D 11 to 13,
  E 7 to 12, J 17 to 22). It also sits 0.02 below Pot G's cheapest wrong line (1.32x); that is a margin
  read off one pot, which this ticket must not tune to.
- 1.2 is the lowest round value that keeps every rescue at or below 1.16x. It was chosen from the rescue
  distribution pooled over all pots. G's 1.32 was not used: G gets no extra line at any tau below 1.32.

**Axis level** (within 10 deg; rank 0 / best-of-3 / best-of-6; the Juglet against `Dataset/Juglet_GT` keys):

| pot | n | axes320 | axes322 | **axes323** | axes323 lines/piece mean (max) |
|---|---|---|---|---|---|
| A | 8 | 6/6/6 | 6/8/8 | 6/7/7 | 1.62 (5, capped to 3) |
| B | 9 | 5/6/6 | 9/9/9 | 9/9/9 | 1.78 (4, capped to 3) |
| C | 6 | 4/5/5 | 5/6/6 | 5/6/6 | 2.33 (6, capped to 3) |
| D | 32 | 23/26/28 | 27/29/30 | 27/29/30* | 1.56 (4, capped to 3) |
| E | 34 | 23/33/33 | 32/33/33 | 32/33/33 | 1.35 (4, capped to 3) |
| F | 7 | 4/7/7 | 6/6/6 | 6/6/6 | 1.57 (3) |
| G | 7 | 7/7/7 | 7/7/7 | 7/7/7 | **1.00 (1)** |
| H | 11 | 10/10/10 | 9/11/11 | 9/11/11 | 1.36 (2) |
| I | 30 | 18/24/25 | 25/27/28 | 25/25/25 | 1.20 (3) |
| J | 19 | 7/9/10 | 9/10/13 | 9/10/12* | 2.58 (6, capped to 3) |
| **pots** | 163 | 107/133/137 | 135/146/151 | **135/143/146*** | |
| Juglet | 9 | 4/6/8 | 6/8/8 | 6/7/7 | 1.44 (3) |

The axes323 column is the uncapped rule from the offline loop. With the cap of three, best-of-6 equals
best-of-3 (starred cells: D 29, J 10, pots 143). The means are also uncapped. The built files' counts are
printed by the build job.

**Pass/fail (fixed now):** **PASS** if all ten pots reach their floor on at least one of two K3 repeats
(sherds and joins both: A 8/8 15/15; B 9/9 15/15; C 4/4 5/5; D >= 23/28 >= 55/69; E >= 29/31 >= 57/62;
F 5/5 7/7; G 7/7 10/10; H 11/11 17/17; I >= 25/26 >= 59/62; J >= 8/11 >= 16/21). **FAIL** otherwise. The
MO arms are the control: a pot whose MO arm also misses its floor is reported as
assembler variance, not scored as a pass. The Juglet is reported, not gated: joins against the 10 real
contacts, axes against the key.

**Prediction (before running):** G at floor (its input equals the K=1 input that held 10/10 twice).
B, C, D, F and I at floor (they held at both K=1 and K=3 where measured). H and J at floor, because their
rescues (H08, H11, J07) are kept. A is the weakest call: A06 is kept, but A07's rescue (1.50x) is dropped,
and K=1 lost 6 of A's 15 joins deterministically. E is uncertain, because only E14's rescue applies and E's
K=1 loss (26-28/31) was larger than one piece. Expected: PASS with A or E the likeliest miss.
**Submitted after the block above was written** (`t323/make_e2e_323.sh`, stamp 20261110-0736):

| what | run | job |
|---|---|---|
| axes323 build (compute node) | `20261110-0736_d628fc0_t323-axes` | 34623282 |
| Pot A-J (MOR1, MOR2, K3R1, K3R2; afterok the build) | `20261110-0736_d628fc0_t323-pot<X>` | A 34623283, B 34623284, C 34623285, D 34623286, E 34623287, F 34623288, G 34623289, H 34623290, I 34623291, J 34623292 |
| Juglet (F20O / F20K3 x 2; afterok the build) | `20261110-0736_d628fc0_t323-juglet` | 34623293 |

The pot jobs come from each pot's 319 run, changing only `AX_318` (to axes323) and the job name. The Juglet
job comes from `t320b-juglet`, changing only `AX_320` (to axes323) and the job name.

**SIF source vs laptop `9a613b5`** (job 34623253 COMPLETED 0:0; per-file md5 plus a CR-normalised diff;
SIF md5 in `runs/20261110-0730_d628fc0_t323-sifsrc/out/sif.md5`; the tarball has 921 bytes of `ls` output in
front of the gzip stream):
- Identical: `feature_matching.cpp/.h`, `data_structure.h`, `ranking_system.h`, `reconstruction.cpp/.h`,
  `filter`, `KDTree`, `visualize`, `axis_estimation.h`, `CMakeLists.txt`.
- `ranking_system.cpp`: the laptop adds a 5-line empty-state guard at line 727. The SIF's lines 771-788 are
  the laptop's 776-793, with identical logic.
- `data_structure.cpp`: the laptop adds a PCD fallback after line 245. Line 164 (axis loading) is the same.
- `main.cpp`: the laptop adds an empty-state guard at 225. `data_path.h` differs in dataset selection and
  comments, and the runs replace it anyway (`inc_src`).
- `axis_estimation.cpp:250, 314`: **the SIF runs Ceres with `num_threads` threads; the laptop pins 1**
  ("single-threaded Ceres determinism, Ticket-12"). This is a plausible source of the assembler's
  run-to-run spread on identical inputs. It has not been tested here.
- **Verdict:** checkpoint 1's code reading stands for the SIF build. Its `ranking_system.cpp` line numbers
  are laptop numbers: subtract 5 for the SIF.
**Correction to the submission table above: those IDs never ran.** The first two axes323 builds failed
before writing anything, and Slurm cancelled every dependent job:
- **34623282** FAILED 1:0, `Pot_A_Piece_01: 6 file lines vs 8 ranked`. The axes322 writer keeps 6 of up
  to 8 ranked lines; the check now requires the file to be a prefix of the ranked list.
- **34623336** FAILED 1:0, `KeyError Pot_JUGLET_Piece_01`. axes322 also holds 9 old-name Juglet files with
  no ranking; the build now skips them by name and fails unless all 172 ranked pieces are written.

The dead run directories are `20261110-0736_*_t323-*` and `20261110-0739_*_t323-*` (12 each, index rows
with an empty verdict; nothing ran in them). The rule and tau are unchanged. **The live jobs:**

| what | run | job | state at submission |
|---|---|---|---|
| axes323 build | `20261110-0740_d628fc0_t323-axes` | 34623393 | **COMPLETED 0:0** |
| Pot A-J | `20261110-0740_d628fc0_t323-pot<X>` | A 34623394, B 34623395, C 34623396, D 34623397, E 34623398, F 34623399, G 34623400, H 34623401, I 34623402, J 34623403 | PENDING |
| Juglet | `20261110-0740_d628fc0_t323-juglet` | 34623404 | PENDING |

**Built axes323, lines per piece (mean, max; after the cap of 3):** A 1.38 (3), B 1.67 (3), C 1.83 (3),
D 1.50 (3), E 1.32 (3), F 1.57 (3), **G 1.00 (1)**, H 1.36 (2), I 1.20 (3), J 2.05 (3), Juglet 1.44 (3).
Pot G is exactly its K=1 input (7 lines over 7 files). Every other pot gets extra lines on some pieces:
the rule is not "one line everywhere", which was measured and failed (322 K=1). File md5s are in
`out/axes323.md5`.
### Worker, 2026-11-10 07:43 — checkpoint 4: line counts, SIF one-liner, job states

**axes323 lines per piece** (counted from the built files, `20261110-0740_d628fc0_t323-axes/out/axes323`):

| pot | pieces | lines | mean | max | 1 line | 2 lines | 3 lines |
|---|---|---|---|---|---|---|---|
| A | 8 | 11 | 1.37 | 3 | **6** | 1 | 1 |
| B | 9 | 15 | 1.66 | 3 | 5 | 2 | 2 |
| C | 6 | 11 | 1.83 | 3 | 3 | 1 | 2 |
| D | 32 | 48 | 1.50 | 3 | 22 | 4 | 6 |
| E | 34 | 45 | 1.32 | 3 | **25** | 7 | 2 |
| F | 7 | 11 | 1.57 | 3 | 4 | 2 | 1 |
| G | 7 | 7 | 1.00 | 1 | 7 | 0 | 0 |
| H | 11 | 15 | 1.36 | 2 | 7 | 4 | 0 |
| I | 30 | 36 | 1.20 | 3 | 26 | 2 | 2 |
| J | 19 | 39 | 2.05 | 3 | 7 | 4 | 8 |
| Juglet | 9 | 13 | 1.44 | 3 | 6 | 2 | 1 |

Pot A per piece: 01:1, 02:1, 03:1, 04:1, 05:1, **06:2** (the rescue, line 2 at 3.9 deg), **07:1** (its rank 0 is 16.3
deg; the 8.3-deg rescue at 1.50x is dropped), 08:3. **Risk, stated before the jobs land:** 6 of A's 8 pieces
have the same single line as at K=1, which lost 6 of 15 joins in both repeats. A holds only if those joins
were lost at A06, which now gets its rescue, and not at A07 or through the wrong extra lines that K=3 gave
A01-05. Which joins K=1 lost has not been mapped (checkpoint 2, next step 3). **A at floor is now a coin
flip, not the prediction above.** E is similar: 25 of 34 pieces have one line.

**SIF diff, one line:** the SIF's `/opt/sfs-pristine` does **not** match laptop `9a613b5` byte for byte. It
differs in `class/ranking_system.cpp:727-731` (laptop-only empty-state guard), `class/data_structure.cpp:245-295`
(laptop-only PCD fallback), `main.cpp:225-228` (laptop-only guard), `class/axis_estimation.cpp:250,314`
(SIF `num_threads`, laptop 1) and `class/data_path.h`. `feature_matching.cpp`, where the per-join scoring
and the 25-deg test live, is identical; checkpoint 1's logic holds, with SIF line = laptop line - 5 in
`ranking_system.cpp` after 727.

**Job states** (sacct, 07:43): pots A-J 34623394-34623403 **PENDING** 0:0; Juglet 34623404 **RUNNING**
(1 min). No `score/acc.tsv` exists yet in any `20261110-0740_d628fc0_t323-*` run.
### Worker, 2026-11-10 07:50 — checkpoint 5: the joins K=1 lost on A and E, and a prediction written before the A and E results

**Pot A, K=1** (`20261110-0506_d628fc0_t322k1-potA`, `score/A_K1R{1,2}.tsv`; both repeats identical, 9/15):
lost joins **1-6, 1-7, 3-6, 4-6, 4-7** (155.8-158.2 deg, 581-788 mm) and **6-7** (13.0 deg / 91.8 mm). All six
involve piece 06 or 07, and pieces {06, 07} were seated as their own group, ~157 deg off {01-05, 08}.
These are the only two A pieces whose first line is wrong:

| piece | ranked lines (err / cost ratio) | axes323 keeps | fixes its joins? |
|---|---|---|---|
| A06 | 35.0 / 1.00, **3.9 / 1.06**, 23.4 / 2.19 | 35.0, **3.9** | yes: a 3.9-deg line is shipped (as in K=3, which held 15/15) |
| A07 | 16.3 / 1.00, 69.4 / 1.36, **8.3 / 1.50**, 5.9 / 1.94 | **16.3 only** | no: the 8.3-deg line is dropped at 1.50x |

There is no precedent for A07 seating with only a >10-deg line: axes320 gave A07 51.9 / 69.0 / 23.1 deg,
and 319's K3 arms scored A **3/8 3/15** (`20261109-1426_ecd5bb8_t319-potA/score/acc.tsv`; A's 15/15 floor
comes from the MO arms). 16.3 deg is inside the assembler's 25-deg join test, so 07 is not excluded by it.

**Pot E, K=1** (`..._t322k1-potE`, `score/E_K1R*_cpp.json`): failed pieces R1 {14, 23, 24, 28, 30, 31},
R2 {14, 28, 31}.

| piece | first line err | axes323 keeps | line-caused? |
|---|---|---|---|
| E14 | **50.3** | 50.3, **9.4**, 17.8 | yes; rescue kept. Its joins 1-14, 2-14, 6-14, 14-26, 14-30 should recover |
| E28 | 0.9 | 0.9 | **no**: right line, failed both K=1 repeats and K=3 R1 |
| E31 | 6.8 | 6.8, 39.6 | **no**: right line, failed both K=1 and both K=3 repeats |
| E23 / E24 / E30 | 2.0 / 7.0 / 3.4 | 2.0, 28.7 / 7.0, 4.6, 22.5 / 3.4, 19.0 | no; failed in K=1 R1 only |

**New measurement: axes322 at K=3 is below Pot E's floor too**: `20261110-0420_d628fc0_t322-potE` scored
E_K3R1 **20/31 33/62** and E_K3R2 **29/31 47/62** (floor >= 57 joins). Joins 13-25 (10.2 deg), 24-31,
25-31, 28-31 and 26-30 fail in every K=1 and K=3 repeat. **On Pot E the profile line set misses the floor at
both K=1 and K=3. The rule can only move E between those two, so a line-count rule cannot be what holds E.**

**PREDICTION (written before the A and E results; jobs 34623394 and 34623398 PENDING at 07:50):**
- **Pot A: below floor, 8/8 sherds, 12/15 joins.** 1-6, 3-6 and 4-6 recover through A06's 3.9-deg line.
  **1-7, 4-7 and 6-7 fail**, because A07's only line is 16.3 deg off and its 8.3-deg line was dropped at
  1.50x. Alternative: 15/15, if a 16.3-deg line under the 25-deg test is enough to seat 07. Untested; no
  precedent either way.
- **Pot E: below floor on joins (~47-55/62), sherds 28-30/31.** The E14 joins recover (the rescue is kept).
  **Joins at E28 and E31 (13-28, 27-28, 24-31, 25-31, 28-31) and the persistent 13-25 and 26-30 stay lost:
  these pieces have the right line and fail anyway, so their losses are not caused by the lines**. Mechanism
  not identified; assembler nondeterminism and edge-feature matching are candidates.
- **So the pre-registered rule is expected to FAIL** (A and E below floor), with A caused by a dropped line
  (fixable only with tau >= 1.50, which lets G's 1.32x wrong line in) and E not caused by lines.

**Poll (sacct 07:50):** pots A-J 34623394-34623403 PENDING. Juglet 34623404 **COMPLETED 0:0** (2m32s);
`score/acc.tsv` is 0/9 0/18 on all four arms, control included. **That is a broken measurement, not a
result:** the template run `20261110-0320_41494d0_t320b-juglet` also reads 0/9 0/18 on every arm, and the
C++ `Acc.txt` scorer reads 0 on the Juglet whatever the axes. The Juglet joins must be scored from the
saved T matrices against `Dataset/Juglet_GT` (the 10 real contacts). Not done yet.
### Worker, 2026-11-10 07:55 — checkpoint 6: correction on the Juglet control, and pot status

**Correction to checkpoint 5:** the Juglet **F20O arm is void by construction, not a broken measurement.**
It stages `Dataset/Axes/Juglet`, which is our own 2026-09-16 MATLAB PotSAC output, not an authors'
reference (AGENTS.md, "The Juglet has no authors' reference"). Ticket 322 measured it right on 1 of 9
pieces against the key. F20O is excluded from every Juglet read-out. The F20K3 arm (axes323) is scored
**only against `Dataset/Juglet_GT`**: job **34623526** (`t323/jugscore.sbatch`) runs the unchanged pot scorer
`score311_cpp.py` (0.35 rad / 50 mm) on `out/F20K3_r{1,2}` with the key's `Juglet_Piece_N_T.txt`. It reports
/18 and the touching pairs only. The repo Acc.txt figure (0/9 0/18) is not used. Note: the assembler wrote
T files for 8 of 9 pieces (`T_0` to `T_7`); piece 9 has none. Ticket 322 lists **nine** non-touching pairs
(1-5, 1-6, 3-7, 4-5, 4-6, 5-9, 6-8, 7-8, 8-9) while saying "8 of 18"; both denominators are reported.

**Pot jobs** (sacct 07:55): all ten PENDING since 07:40 (Slurm reason below). No `acc.tsv`, so there are no
scores and no verdicts yet.

| pot | arm | repeat 1 (sherds, joins) | repeat 2 | floor | pass/fail |
|---|---|---|---|---|---|
| A-J | MO, K3 | pending | pending | as checkpoint 3 | — |
| Juglet | F20K3 vs key | job 34623526 PENDING | | reported, not gated | — |
| Juglet | F20O | void (not a reference) | void | — | — |
Slurm reason for all eleven t323 jobs at 07:56: **(Priority)**. The account has 40 pending jobs, including about 30 `mirror2/3_*` jobs (34487716-34487736) that are not this ticket's and were left alone.

### Worker, 2026-11-10 08:00 — checkpoint 7: PREDICTION FOR ALL TEN POTS (written before any t323 pot job started)

Method: `t323/predict_k1.py`, plus the per-join `.tsv` files for D, F, I and J (no `_cpp.json` for those).
Each K=1 failed join (ticket 322, `20261110-0506_d628fc0_t322k1-pot<X>/score/`) is **line-caused** if one of
its pieces has a first line > 10 deg from the reference, and **fixable** if axes323 gives that piece a line
<= 10 deg. Joins are in piece numbers (the off pieces are D22, F07, I28-30 and J09). The axes322 K=3 results
(`..._t322-pot<X>`) are cited where they settle an "other" cause.

| pot | K=1 (R1 / R2; sherds, joins) | wrong first line -> axes323 best | failures: line-caused, fixable | line-caused, not fixable | other cause | **predicted axes323 (K3 arm)** | floor |
|---|---|---|---|---|---|---|---|
| A | 8/8 9/15 / same | 06: 35.0 -> **3.9**; 07: 16.3 -> 16.3 (1 line) | 1-6, 3-6, 4-6 | 1-7, 4-7, 6-7 | none | **8/8 12/15** | **below** |
| B | 9/9 15/15 / same | none | — | — | — | 9/9 15/15 | at |
| C | 4/4 5/5 / same | none | — | — | — | 4/4 5/5 | at |
| D | 24/28 58/69 / same | 18: 15.4 -> **2.9**; 26: 69.1 -> 12.6; 27: 17.2 -> **2.7**; 29: 18.8 -> 11.0 | none | 3-26, 13-26, 16-26, 7-29, 25-29, 27-29 | 3-28, 12-28, 14-28, 15-25, 24-25 | 24/28 ~58/69 | at |
| E | 26/31 44/62 / 28/31 51/62 | 14: 50.3 -> **9.4**; 29: 16.6 -> 10.7 | 1-14, 2-14, 6-14, 14-26, 14-30 | none | R2: 13-28, 18-23, 24-31, 25-31, 27-28, 28-31 (R1 +6) | **28-30/31, 50-56/62** | **below (joins)** |
| F | 5/5 7/7 / same | 06: 14.7 -> 14.7 (1 line, as at K=1) | — | — | — | 5/5 7/7 | at |
| G | 7/7 10/10 / same | none; input identical to K=1 | — | — | — | 7/7 10/10 | at |
| H | 9/11 11/17 / same | 08: 18.5 -> **1.6**; 11: 45.2 -> **1.9** | 2-11, 7-8, 9-11 | none | 4-9, 4-10, 9-10 (all three pieces have right lines; recovered at K=3 R1, when 04 and 10 had 3 lines; axes323 gives 04 and 10 one line, 09 two) | **11/11 14/17** | **below** |
| I | 25/26 59/62 / same | 20: 21.6 -> 21.6; 25: 34.5 -> 16.9; 27: 10.7 -> 10.7 | none | 5-25, 11-25, 20-25 | none | 25/26 59/62 (K=1 and K=3 both gave this) | at |
| J | 6/11 5/21 / 6/11 8/21 | 07: 20.4 -> **4.8**; 08: 12.6 -> 12.6; 11: 11.2 -> 11.2; 12: 21.7 -> 21.7 | 1-7 | 2-8, 5-12, 6-11, 8-11, 8-12 | R1: 1-3, 1-4, 1-5, 1-6, 2-5, 2-6, 3-6, 4-5, 4-6, 5-10 (the J01 cluster; J01's first line is right, 5 deg) | **8/11 16/21**: K=3 lost exactly the five not-fixable joins, and axes323 gives J01 three lines (5/7/25 deg), as K=3 did | at (exactly at floor) |

**Predicted verdict: FAIL**, with **A, E and H below floor** and the other seven at floor. Causes by pot:
- A: a dropped rescue line (A07's 8.3-deg line at 1.50x).
- E: not line-caused (pieces with right lines fail; E also missed its floor at axes322 K=3).
- H: the 4-9 / 4-10 / 9-10 group, which K=3 recovered only when 04 and 10 had their extra (wrong) lines.
Lowest-confidence calls: H (K=3 R2 lost 1-5, 1-6, 2-6, 3-5 on identical input, so the assembler's own
spread is 4 joins) and J (exactly at floor, no margin).

**Poll (sacct 08:00):** pots A-J 34623394-34623403 and jugscore 34623526 all **PENDING (Priority)**.
### Worker, 2026-11-10 08:08 — checkpoint 8: first results against checkpoint 7

sacct 08:08: A 34623394 **COMPLETED 0:0** (4m17s), C 34623396 **COMPLETED 0:0** (1m45s); B, D, E RUNNING;
F-J PENDING; jugscore 34623526 COMPLETED 0:0. The A arm staged axes323 (md5 of `work/axes_k3` = `axes323`
for A01, A02, A06, A07, A08; line counts 1 / 1 / 2 / **1** / 3).

| pot | arm | repeat 1 | repeat 2 | floor | pass/fail | checkpoint 7 predicted | prediction |
|---|---|---|---|---|---|---|---|
| A | MO | 8/8 15/15 | 8/8 15/15 | 8/8 15/15 | control at floor | — | — |
| A | **K3 (axes323)** | **8/8 15/15** | **8/8 15/15** | 8/8 15/15 | **PASS** | 8/8 12/15, below | **WRONG** |
| C | MO | 4/4 5/5 | 4/4 5/5 | 4/4 5/5 | control at floor | — | — |
| C | **K3 (axes323)** | **4/4 5/5** | **4/4 5/5** | 4/4 5/5 | **PASS** | 4/4 5/5, at | right |

**Pot A, what the miss says:** A07 seated on its single 16.3-deg line once A06 had its 3.9-deg line. A
first line 16.3 deg off, inside the assembler's 25-deg join test, was enough. The K=1 loss was A06's
35-deg line pulling A07 into a wrong two-piece group, not A07's own line. Checkpoint 7's
"line-caused, not fixable" class used a 10-deg bar the assembler does not use. **The same reasoning
weakens the D (26 at 12.6, 29 at 11.0), I (20 at 21.6, 25 at 16.9) and J (08 at 12.6, 11 at 11.2, 12 at 21.7)
"not fixable" cells**: they may also seat.

**Juglet, F20K3 (axes323) against `Dataset/Juglet_GT`** (score311_cpp.py; F20O void, as in checkpoint 6):
r1 and r2 identical. **0/9 sherds, 0/18 joins, touching pairs 0/9.** T files for 8 of 9 pieces (9 missing).
Nearest pass: 1-8 at 6.3 deg / 51.4 mm (bar 0.35 rad / 50 mm). The rest are 28-179 deg off. **Not
yet a result:** this applies the pot convention `inv(T_i) T_j` to the key's matrices. Ticket 322 found the
two conventions disagree by 6.8-136.7 deg on this key, and the convention the assembler's `T_<i>to_<i>`
files use against this key has not been verified. Next: score one assembled pair under both conventions,
and render it.
### Worker, 2026-11-10 08:17 — checkpoint 9: B, F, G landed; Juglet convention settled; the Pot A mechanism

sacct 08:17: B 34623395, F 34623399, G 34623400 **COMPLETED 0:0**; D, E, H, I, J RUNNING.

| pot | arm | repeat 1 | repeat 2 | floor | pass/fail | predicted (ckpt 7) | prediction |
|---|---|---|---|---|---|---|---|
| A | K3 (axes323) | 8/8 15/15 | 8/8 15/15 | 8/8 15/15 | PASS | 8/8 12/15 below | wrong |
| B | MO | 9/9 15/15 | 9/9 15/15 | 9/9 15/15 | control at | — | — |
| B | K3 (axes323) | **9/9 15/15** | **9/9 15/15** | 9/9 15/15 | **PASS** | 9/9 15/15 | right |
| C | K3 (axes323) | 4/4 5/5 | 4/4 5/5 | 4/4 5/5 | PASS | 4/4 5/5 | right |
| F | MO | 5/5 7/7 | 5/5 7/7 | 5/5 7/7 | control at | — | — |
| F | K3 (axes323) | **5/5 7/7** | **5/5 7/7** | 5/5 7/7 | **PASS** | 5/5 7/7 | right |
| G | MO | 7/7 10/10 | 7/7 10/10 | 7/7 10/10 | control at | — | — |
| G | K3 (axes323) | **7/7 10/10** | **7/7 10/10** | 7/7 10/10 | **PASS** | 7/7 10/10 | right |

Running tally: 5 of 5 landed pots at floor on both repeats; predictions 4 of 5 right (A wrong, favourably).
**Pot G's regression is undone:** axes322 at K=3 gave 4-5/10, axes323 gives 10/10 twice.

**Juglet convention** (job 34623717, `t323/convention.py`; median / max pairwise angle between the pieces'
axes mapped into the assembled frame):

| poses | axes | R a | R^T a |
|---|---|---|---|
| Pot A GT T | GT axes | **0.06 / 0.09** | 62.56 / 86.09 |
| Pot B GT T | GT axes | **0.04 / 0.08** | 57.86 / 88.08 |
| Pot A assembler T (A_K3R1) | GT axes | **1.50 / 3.39** | 63.09 / 86.96 |
| Juglet key T | key axes | **0.00 / 0.00** (by construction) | 56.36 / 89.13 |
| Juglet key, touching pair 1-8 / 1-2 | key axes | **0.00 / 0.00** | 39.50 / 53.69 |
| Juglet assembler T (F20K3_r1) | key axes | 16.05 / **76.10** | 58.48 / 87.76 |
| Juglet assembler T, pair 1-8 | key axes | 6.24 | 42.81 |

**The pots' GT, the Juglet key and the assembler all map with a' = R a; the key is in the same convention as
the pots' GT.** `score311_cpp.py`'s `inv(T_i) T_j` is therefore the right composition for the key, and no
AGENTS.md change is needed. The key's own 0.00 is circular, since its axes were mapped through its own T.
The independent check is ticket 322's validation of the key T against TORA's assembled hdf5 at
0.0001 mm. **The Juglet F20K3 0/9 0/18 (touching 0/9) is a real assembly failure, not a scoring artefact:**
the assembled pieces' axes are 16 deg apart at the median and 76 deg at worst. That is the method failing,
on the Juglet.

**Pot A, what changed (the ticket's first mechanism claim).** Correction to the brief: the 3/8 3/15 arm is
ticket **319**'s K3 arm on **axes318**. axes322 at K=3 held A at 8/8 15/15 twice. The pair that isolates
the change is **axes322 K=1 (8/8 9/15 twice) against axes323 (8/8 15/15 twice)**. Same profile ranking,
same first line on every piece. axes323 adds lines on two pieces only:
- **A06:** +3.9 deg (cost 1.06x) beside its 35.0-deg first line.
- **A08:** +4.0 deg (1.03x) and +15.7 deg (1.10x) beside its right 2.3-deg first line.

A01-05 and A07 keep one line. Against axes322 K=3, axes323 drops two lines on each of A01-05 and A07
(none of them within 10 deg except A07's 8.3-deg line at 1.50x) and one on A06 (23.4 deg, 2.19x).
At K=1 all six lost joins touched 06 or 07, seated together ~157 deg off the rest. With A06's 3.9-deg line
available, both 06 and 07 seat, **A07 on its single 16.3-deg line**. **Claim: one right extra line on the
one piece whose first line was badly wrong (35 deg) restored all 6 joins.** A07's 16.3-deg error does not
need a fix under the assembler's 25-deg test. Not isolated: A08's two extra lines changed in the same
step. Separating them needs an arm with A06's extra line only (not run). Two repeats, one pot.
### Worker, 2026-11-10 08:13 — checkpoint 10: poll

sacct: A 34623394, B 34623395, C 34623396, F 34623399, G 34623400, Juglet 34623404 and conv 34623717
**COMPLETED 0:0**; D 34623397 (12m38s), E 34623398 (11m23s), H 34623401, I 34623402 and J 34623403 **RUNNING**.

| pot | MO R1 / R2 | K3 (axes323) R1 / R2 | floor | pass/fail | predicted (ckpt 7) |
|---|---|---|---|---|---|
| A | 8/8 15/15 / 8/8 15/15 | 8/8 15/15 / 8/8 15/15 | 8/8 15/15 | PASS | below — wrong |
| B | 9/9 15/15 / 9/9 15/15 | 9/9 15/15 / 9/9 15/15 | 9/9 15/15 | PASS | at — right |
| C | 4/4 5/5 / 4/4 5/5 | 4/4 5/5 / 4/4 5/5 | 4/4 5/5 | PASS | at — right |
| D | not yet | not yet | >=23/28 >=55/69 | — | at |
| E | not yet | not yet | >=29/31 >=57/62 | — | below |
| F | 5/5 7/7 / 5/5 7/7 | 5/5 7/7 / 5/5 7/7 | 5/5 7/7 | PASS | at — right |
| G | 7/7 10/10 / 7/7 10/10 | 7/7 10/10 / 7/7 10/10 | 7/7 10/10 | PASS | at — right |
| H | not yet | not yet | 11/11 17/17 | — | below |
| I | not yet | not yet | >=25/26 >=59/62 | — | at |
| J | not yet | not yet | >=8/11 >=16/21 | — | at |
### Worker, 2026-11-10 08:22 — checkpoint 11: H and J (numbers read by the lead at 08:15), poll

| pot | MO R1 / R2 | K3 (axes323) R1 / R2 | floor | pass/fail | predicted (ckpt 7) |
|---|---|---|---|---|---|
| H | 10/11 10/17 / 8/11 9/17 | **11/11 17/17 / 11/11 17/17** | 11/11 17/17 | **PASS** | 11/11 14/17, below — **wrong** (the good direction) |
| J | 8/11 16/21 / 8/11 16/21 | **8/11 16/21 / 8/11 16/21** | 8/11 16/21 | **PASS** (exactly at floor) | 8/11 16/21, at — **right** |

Source: `runs/20261110-0740_d628fc0_t323-pot{H,J}/score/acc.tsv`, read by the lead. The J authors' control
is also 16/21, not 21/21.

Poll (sacct 08:22): D 34623397 RUNNING (22m24s), E 34623398 RUNNING (21m09s), I 34623402 RUNNING
(13m59s). No `acc.tsv` or `acc_*.row` for D, E or I yet.

Running tally: **7 of 7 landed pots at floor on both K3 repeats** (A, B, C, F, G, H, J). Checkpoint 7's
predictions were right on 5 of 7; both misses (A, H) predicted a failure that did not happen.
### Worker, 2026-11-10 08:35 — checkpoint 12: renders, corpus check, mechanism (A, H)

**Renders** (job 34624179 COMPLETED 0:0; `t323/render323.py`: the 314 `render_assemblies.py` drawing plus a
GT panel. Each arm is moved into the GT frame through its first staged piece; pieces come from the run's
staged list, so J09 is off). Columns: GT | authors' axes MOR1 | axes323 K3R1; top and perspective views:
- [Pot A](SfSpp_preprocessing/artifacts/pota323/renders/potA.png): axes323 and MOR1 both lay out as GT; the
  06/07 pair sits in place.
- [Pot H](SfSpp_preprocessing/artifacts/pota323/renders/potH.png): **MOR1 is visibly broken** (pieces
  scattered, one standing on edge; consistent with 10/17), while axes323 lays out as GT.
- [Pot J](SfSpp_preprocessing/artifacts/pota323/renders/potJ.png): axes323 shows one stray dark-blue piece off
  the left rim (most likely P12, one of J's three unseated pieces 08 / 11 / 12); otherwise as GT.

**Limit:** the view spans ~300 mm, so it shows a piece in the right place or not. It cannot separate a
seated join from one a few mm off; the scorer's 0.35 rad / 50 mm bar is the measurement for that. **Not
eye-checked by the conservator.**

**Corpus check, one line:** `find <dir> -maxdepth 1 -newer runs/20261110-0730_d628fc0_t323-sifsrc/run.json`
(07:30, this ticket's first job) over original_samples/SfS_pp/{Axes, Ground Truth, Ground Truth Axes,
Surfaces, Point, Mesh, Breaklines}, both `Dataset/Juglet_GT` copies and `sfs_preprocessing/Dataset/Axes/Juglet`:
**0 files in all 10**. Each landed pot job printed **CORPUS-UNCHANGED** from its own before/after md5 of the
corpus inputs (7 of 7 so far, 0 CORPUS-CHANGED). D, E and I are still to report theirs.

**Mechanism (A, H): which piece gets which line** (errors vs reference, deg; cost ratio to the piece's first line):
- **Pot A:** one-line 9/15, axes323 15/15. axes323 adds a line to two pieces: **A06 +3.9 (1.06x)** beside a
  35.0-deg first line, and A08 +4.0 (1.03x) and +15.7 (1.10x) beside a right 2.3-deg first line. A01-05 and
  A07 stay at one line; A07 seats on its 16.3-deg first line. Against axes322's three lines (also 15/15),
  axes323 removes 13 lines: 2 each on A01-05 and A07 (all > 10 deg except A07's 8.3 at 1.50x) and A06's
  23.4 (2.19x).
- **Pot H:** one-line 9/11 11/17 (both repeats), axes323 11/11 17/17 (both). axes323 adds a line to four
  pieces: **H08 +1.6 (1.13x)** beside 18.5, **H11 +1.9 (1.01x)** beside 45.2, H06 +34 and H09 +17 (both
  wrong, both <= 1.2x). Against axes322's three lines (11/11 17/17 then 9/11 13/17), axes323 removes 2 lines
  each on H01-05, H07 and H10 and the third line on H06, H08, H09 and H11. The one-line loss of 4-9, 4-10 and
  9-10, which ckpt 7 called "other", was recovered, with H04 and H10 still on one line.
- **Common pattern, two pots and two repeats each:** the joins came back when the two or three pieces
  whose first line was badly wrong (A06 35, H08 18.5, H11 45.2) got their right line at <= 1.13x. Removing
  the wrong extra lines elsewhere cost nothing on A or H, and on G it is what restored 10/10. **Not
  isolated:** each pot changed more than one piece at once (A08; H06, H09).
### Worker, 2026-11-10 08:42 — checkpoint 13: axes323 vs axes322, file by file (is the change only selection?)

Compared each `axes323/<piece>_Axis.xyz` with `head -n 3` of the same axes322 file (what the axes322 K3 arm
staged). Checks: md5 of line 1; every axes323 line is present verbatim among axes322's first three, in the
same order, starting at line 1 (`grep -qxF --`, plus an index-order check).

| pot | pieces | pieces that lost lines | lines dropped | line 1 differs |
|---|---|---|---|---|
| A | 8 | 7 | 13 | 0 |
| B | 9 | 7 | 12 | 0 |
| C | 6 | 4 | 7 | 0 |
| D | 32 | 26 | 46 | 0 |
| E | 34 | 31 | 52 | 0 |
| F | 7 | 5 | 7 | 0 |
| G | 7 | 7 | 14 | 0 |
| H | 11 | 11 | 18 | 0 |
| I | 30 | 27 | 49 | 0 |
| J | 19 | 10 | 16 | 0 |
| Juglet | 9 | 8 | 14 | 0 |

All 172 files: **line 1 identical to axes322 on 172 of 172**. Every axes323 line is in axes322's top three
(0 of 172 files with a foreign line), and every file is an in-order subsequence starting at line 1 (0 out of
order). **axes323 is a pure deletion from axes322's three-line set: no line added, none moved, none
re-estimated.** Against axes322 K=3 the only change is which lines were removed. Against axes322 K=1 the
only change is which lines were added (line 1 is the same everywhere). **No ranking confound.**

Poll (sacct 08:42): D 34623397 RUNNING (40m43s), E 34623398 RUNNING (39m28s), I 34623402 RUNNING (32m18s);
no acc.tsv yet.
### Worker, 2026-11-10 08:58 — checkpoint 14: E and I (numbers read by the lead at 08:52), D partial

| pot | MO R1 / R2 | K3 (axes323) R1 / R2 | floor | pass/fail | predicted (ckpt 7) |
|---|---|---|---|---|---|
| E | 31/31 62/62 / 31/31 62/62 | **31/31 62/62 / 31/31 62/62** | >=29/31 >=57/62 | **PASS** | 28-30/31 50-56/62, below: **wrong** (the good direction) |
| I | 25/26 59/62 / 25/26 59/62 | **25/26 59/62 / 25/26 59/62** | >=25/26 >=59/62 | **PASS** | 25/26 59/62, at: **right** |
| D (partial) | R1 not yet / **23/28 55/69** | **26/28 63/69** / not yet | >=23/28 >=55/69 | **PASS on R1** (the rule needs one of two repeats) | 24/28 ~58/69, at: **right** (exceeded) |

Sources: E job 34623398 COMPLETED 0:0 (45m58s) and I job 34623402 COMPLETED 0:0 (32m21s), `score/acc.tsv`
read by the lead. Both logs print CORPUS-UNCHANGED. D job 34623397 RUNNING (57m39s); its finished rows are
`score/acc_D_K3R1.row` and `score/acc_D_MOR2.row`.

Pot E against the other line sets, same first lines: one line 26/31 44/62 and 28/31 51/62; axes322 three
lines 20/31 33/62 and 29/31 47/62; **axes323 31/31 62/62 twice**. The checkpoint 7 analysis called E's
losses at E28 and E31 "not line-caused", because those pieces' own first lines were right; the extra lines
elsewhere were the cause, and removing them fixed it.

Prediction tally (ckpt 7, written before any pot ran): **7 of 10 right** (B, C, D, F, G, I, J). The 3 misses
(A, E, H) all predicted a failure that did not happen.

## Interim verdict (written 2026-11-10 08:58; final sentence waits for Pot D's second K3 repeat)

**Pre-registered rule (checkpoint 3, written before any end-to-end job):** each piece gives the assembler its
profile-ranked lines (15 deg apart, cheapest first), keeping the first line and every later line whose
profile cost (mean wall thickness) is at most **1.2x** that piece's own cheapest line, up to three. The
ratio is scale-free and computed per piece from its own costs. PASS = all ten pots at floor on at least one
of two K3 repeats.

**Results (K3 arm on axes323; repeat 1 / repeat 2; sherds, joins):**

| pot | axes323 | floor | |
|---|---|---|---|
| A | 8/8 15/15 / 8/8 15/15 | 8/8 15/15 | pass |
| B | 9/9 15/15 / 9/9 15/15 | 9/9 15/15 | pass |
| C | 4/4 5/5 / 4/4 5/5 | 4/4 5/5 | pass |
| D | 26/28 63/69 / 26/28 63/69 | >=23/28 >=55/69 | pass |
| E | 31/31 62/62 / 31/31 62/62 | >=29/31 >=57/62 | pass |
| F | 5/5 7/7 / 5/5 7/7 | 5/5 7/7 | pass |
| G | 7/7 10/10 / 7/7 10/10 | 7/7 10/10 | pass |
| H | 11/11 17/17 / 11/11 17/17 | 11/11 17/17 | pass |
| I | 25/26 59/62 / 25/26 59/62 | >=25/26 >=59/62 | pass |
| J | 8/11 16/21 / 8/11 16/21 | >=8/11 >=16/21 | pass |

Nine pots have passed on both repeats and D on its first. No previous set held all ten: axes322 at three
lines lost G (4-5/10) and E (33-47/62); at one line it lost A, E, H and J (ticket 322).

**Only deletion changed (checkpoint 13):** axes323 is a strict subset of axes322's three-line set. Line 1 is
identical on 172 of 172 pieces, every kept line is verbatim from axes322's top three in the same order,
and 248 lines were removed in total (234 on the pots, 14 on the Juglet). No line was re-estimated or re-ranked, so the gain is attributable to
line selection alone.

**Mechanism:** the assembler scores every pair of pieces over every pair of their lines, and accepts a join
when the two lines it used agree within 25 deg (`feature_matching.cpp:1715`, identical in the SIF). It never
checks that a piece's line agrees with the assembly the piece is joining. So **every extra line is another
chance for the assembler to build a self-consistent wrong group** (G's {2, 5}; E's 28 / 31 group at three
lines). **Ship an extra line only when it is nearly as cheap as the best line (<= 1.2x)**: those are the
lines that rescue a wrong first line (A06 3.9 deg at 1.06x, H08 1.13x, H11 1.01x, E14 1.03x, J07 1.06x).
The wrong alternatives mostly cost more (median 1.83x).

**Juglet (reported, not gated):** F20K3 on axes323 scores 0/9 sherds and 0/18 joins against `Dataset/Juglet_GT`
(touching pairs 0/9). The pose convention was verified (checkpoint 9), so this is the method failing on the
Juglet: the assembled pieces' axes are 16 deg apart at the median, 76 deg at worst. The F20O control is void.

**Pot D, final** (job 34623397 COMPLETED 0:0, 1h02m20s, CORPUS-UNCHANGED; `score/acc.tsv` read by the lead):
D_MOR1 23/28 55/69, D_MOR2 23/28 55/69, **D_K3R1 26/28 63/69, D_K3R2 26/28 63/69**.

**Against the authors'-axes control (MO, same job, same repeats):**

| pot | MO R1 / R2 | axes323 R1 / R2 | axes323 vs MO |
|---|---|---|---|
| A | 8/8 15/15 / 8/8 15/15 | 8/8 15/15 / 8/8 15/15 | tie |
| B | 9/9 15/15 / 9/9 15/15 | 9/9 15/15 / 9/9 15/15 | tie |
| C | 4/4 5/5 / 4/4 5/5 | 4/4 5/5 / 4/4 5/5 | tie |
| D | 23/28 55/69 / 23/28 55/69 | 26/28 63/69 / 26/28 63/69 | **beats** (+3 sherds, +8 joins) |
| E | 31/31 62/62 / 31/31 62/62 | 31/31 62/62 / 31/31 62/62 | tie |
| F | 5/5 7/7 / 5/5 7/7 | 5/5 7/7 / 5/5 7/7 | tie |
| G | 7/7 10/10 / 7/7 10/10 | 7/7 10/10 / 7/7 10/10 | tie |
| H | 10/11 10/17 / 8/11 9/17 | 11/11 17/17 / 11/11 17/17 | **beats** (+1-3 sherds, +7-8 joins) |
| I | 25/26 59/62 / 25/26 59/62 | 25/26 59/62 / 25/26 59/62 | tie |
| J | 8/11 16/21 / 8/11 16/21 | 8/11 16/21 / 8/11 16/21 | tie |

**Final verdict: PASS.** The pre-registered rule holds **all ten pots at or above floor on both repeats**
(20 of 20 K3 runs). The axes323 arm **beats the authors'-axes control on 2 pots (D, H), ties on 8 (A, B, C,
E, F, G, I, J) and loses on none**. (A and E tie the control at full marks; their gain is over this ticket's
own earlier line sets, not over the authors'.) Weight: ten pots, two repeats each. On every pot both
repeats gave identical scores, so this run showed no spread to discount. The assembler's nondeterminism
is documented elsewhere (ticket 322: H 11/11 then 9/11 on identical input) and was not tested here.
Renders for D, E and I: job 34624906 COMPLETED 0:0, the same `t323/render323.py`:
[Pot D](SfSpp_preprocessing/artifacts/pota323/renders/potD.png),
[Pot E](SfSpp_preprocessing/artifacts/pota323/renders/potE.png),
[Pot I](SfSpp_preprocessing/artifacts/pota323/renders/potI.png). In all three, both arms lay out as GT at
this scale (~400 mm view). D's 3-sherd difference from the authors' arm is not resolved in the picture;
the scorer measures it. Not eye-checked by the conservator.