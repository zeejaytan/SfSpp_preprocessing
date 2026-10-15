# 10: Generalise the frozen finder to pots B–J

**What to build:** the proof the finder works beyond the sample — run the frozen (a)-finder over pots B–J and score it where shipped axles exist.

**Answers:** E1

**Blocked by:** 16-sealed-revalidation (frozen finder + Pot A score below). Pot A held-out leg is already spent (05/07/08 scored in 16) — this ticket is cross-pot only.

**Status:** results-in

**Frozen finder:** `.scratch/pota-repro/p15-stage/axle_finder/` (committed; GM-refine (a)-variant — NOT the rejected (b)-variant in p16-stage). Run it exactly as frozen: no tuning, no per-pot adjustments. If a pot needs a tweak, record the miss and move on — adaptation decisions belong to the successor, not this ticket.

**Standing Pot A score (from 12/14/15/16):** 6/8 direction-pass under the position-conditional bar (direction ≤5° strict everywhere; position ≤2mm where the fragment spans enough shape; P01/P05 at the ~2-3mm material floor). Known misses riding along: P07 count (peel/dedup kills 2 of 3 real modes), P08 landscape (GM prefers a spurious pocket for sh1).

**Per-pot inputs (from ticket 01 census; surfaces face the same pipeline as Pot A):**

| pot | meshes | surfaces | shipped axles (test key) |
|---|---|---|---|
| B | 9 | 18 | 9 |
| C | 7 | 12 | 6 |
| D | 32 | 64 | 32 |
| E | 34 | 68 | 34 |
| F | 7 | 14 | 7 |
| G | 7 | 14 | 7 |
| H | 11 | 22 | 11 |
| I | 30 | 60 | 30 |
| J | 19 | 38 | 19 |

**Rules:** shipped axles are the test key, never finder input. Run pot by pot (largest pots D/E/I may need split jobs); keep steps queued back-to-back. Every sbatch gets a laptop-side poll (`sacct` directly — `slurm_poll.sh` exits immediately) with final State/ExitCode in the ticket.

- [ ] Per-pot table: pieces run, direction errors + radial errors vs shipped, nset vs shipped count, pass/fail under the position-conditional bar
- [ ] Per-pot verdict line: which pots look like Pot A (wall-dominated, direction-passing) vs new failure families (new geometry? multi-axis? base-heavy?)
- [ ] Comments section: cross-pot table + the sentence "the finder generalises beyond the sample: yes/no" with numbers
- [ ] E1 `Where it stands` update proposed in Comments for lead to write into intent/ (worker does not edit intent/)
- [ ] Job IDs + sacct states; no commits; Comments-only ticket edits

**Successor:** cut from the verdict — either per-family repair tickets (if new failure families) or the E2E gate proof (if B–J direction-passes).

## Comments (worker, 2026-10-16)

**Frozen provenance.** Finder = p15-stage (a)-variant EXACTLY as frozen: all 16
`axle_finder/*.m` md5-identical laptop `.scratch/pota-repro/p15-stage/` vs
Spartan `potsac-p15-run/`; Spartan `potsac-p10-run/axle_finder` is a `cp` +
`diff -r`-verified identical copy (p16's (b)-variant never touched). No tuning,
no per-pot adjustments. Loader note: the `read_surfaces` shim is Pot-A-only, so
`p10_run.m` reads `Surfaces/Pot_<L>_Piece_<NN>_Surface_0/1.xyz` directly
(first 6 rows, same convention) and `Axes/Pot_<L>_Piece_<NN>_Axis.xyz` as the
test key only. Pot C mesh 07 has no surfaces/axes files — not run (6 pieces).
Staging: laptop `.scratch/pota-repro/p10-stage/` (`p10_run.m` + 12 sbatches)
mirrors Spartan `potsac-p10-run/`.

**Cross-pot table** (bar: direction ≤5° strict everywhere, position reported;
dirpass = all derr ≤5°; strict = all derr ≤5° AND rerr ≤2mm):

| pot | pieces run | dirpass | strict | verdict family |
|---|---|---|---|---|
| B | 9 | 7/9 | 3/9 | Pot-A-like; misses B03 (landscape), B08 (multi) |
| C | 6 | 5/6 | 1/6 | Pot-A-like; miss C02 count (P07-family) |
| D | 32 | 24/32 | 16/32 | split: D01–D16 16/16 Pot-A-like; D17–D32 8/16 small-multi misses |
| E | 34 | 30/34 | 18/34 | Pot-A-like; misses in multi-axis pieces (E17/E21/E31/E34) |
| F | 7 | 6/7 | 6/7 | Pot-A-like; miss F07 count (P07-family) |
| G | 7 | 7/7 | 4/7 | Pot-A-like, clean |
| H | 11 | 1/11 | 0/11 | NEW FAMILY — wholesale miss (see below) |
| I | 30 | 27/30 | 21/30 | Pot-A-like; late misses I25/I29/I30 (small multi) |
| J | 19 | 10/19 | 5/19 | mixed — heaviest multi-axis load (nans up to 5) |
| **all B–J** | **155** | **117/155 (75%)** | **74/155 (48%)** | — |

**Miss detail (every dirpass=FAIL piece; passes carry position-over-2mm notes):**
- B: P03 nset=2/nans=1 derr 9.12 rerr 37.24 (landscape, P08-family); P08
  nset=3/nans=2 derr [31.37 5.41]. Position-over passes: P01 (3.15), P06
  (3.88), P07 (3.15°/11.19), P09 (2.94°/8.20).
- C: P02 nset=1/nans=2 derr [59.17 1.16] (count miss, P07-family).
  Position-over passes: P03 (4.61), P04 (5.89), P05 (7.58), P06 (2.53°/18.86,
  counts ~300).
- D: D21 [82.40 6.74]; D24 nset=3/nans=4 [24.08 4.74 1.33 5.30]; D25
  7.28/38.18; D26 [10.32 4.78]; D27 [4.75 73.04]; D28 [18.34 5.55]; D29
  nset=1/nans=2 [20.64 0.49]; D30 nset=2/nans=5 [43.26 39.94 1.39 58.79
  78.58]. All D2 misses are low-count (300–2300) multi-axis tails.
- E: E17 [5.21 0.06] (near); E21 nset=1/nans=2 [84.65 1.49]; E31 nset=2/nans=3
  [13.88 5.65 16.14]; E34 nset=1/nans=3 [64.98 0.88 23.93].
- F: F07 nset=1/nans=3 [68.16 1.12 12.79] (count miss, P07-family).
- G: no misses (position-over: P02 2.50, P05 2.43, P06 2.81).
- H: H01/H03/H04 nset=0 (finder returns nothing); H02 85.47/426.59; H05
  nset=1/nans=2 [2.24 56.61]; H06 nset=1/nans=3 [49.72 62.16 13.41]; H07
  [29.90 73.75]; H08 nset=2/nans=3 [41.11 69.15 58.50]; H09 nset=2/nans=6
  [2.91 64.97 83.22 78.70 11.42 78.08]; H11 nset=1/nans=3 [13.39 18.45
  1.07]. Only H10 dir-passes (3.03°, rerr 21.97 over). Counts 276–2119
  throughout — small fragments, multi-axis everywhere.
- I: I25 nset=1/nans=2 [33.38 0.91]; I29 [7.69 18.32]; I30 nset=1/nans=2
  [2.54 16.87].
- J: J01 nset=4/nans=3 [31.31 20.14 0.07]; J06 [0.74 10.40]; J08 nset=1/nans=3
  [70.78 73.98 83.55]; J11 nset=1/nans=3 [83.80 1.43 33.89]; J13
  [21.49 40.89 2.32]; J14 nset=1/nans=5 [49.57 23.03 1.05 24.61 37.43]; J16
  8.57/8.93; J17 72.69/315.74; J19 6.34/22.38.

**Per-pot verdict lines.** Pot-A-like (wall-dominated, direction-passing):
B (7/9), C (5/6), D01–D16 (16/16), E (30/34), F (6/7), G (7/7), I (27/30).
New failure families: (1) **Pot H 1/11** — small multi-axis fragments, finder
often returns 0–1 modes against 2–6 shipped axes; (2) **small-count
multi-axis tails** — D17–D32 (8/16) and J (10/19), nans 2–5 at counts
300–2300; (3) Pot-A P07/P08 families recur exactly where expected — count
misses C02/F07/E34/J08/J11/J13/J14, landscape misses B03/D21/D25/J16/J17/J19.

**The finder generalises beyond the sample: partially — 117/155 pieces (75%)
direction-pass across pots B–J with zero tuning; single-axis wall pieces pass
nearly everywhere (G 7/7, D01–D16 16/16, I01–I15 15/15), but Pot H collapses
(1/11) and multi-axis small fragments miss by count and by landscape, so the
E2E gate is not yet earned.**

**Proposed E1 `Where it stands` update (for lead to write into intent/):**
frozen GM-refine axle finder run unmodified over pots B–J (155 pieces, 12
Slurm jobs, all COMPLETED 0:0): 117/155 (75%) direction-pass ≤5° vs shipped
NURBS axles; single-axis wall pieces pass nearly everywhere (G 7/7, D01–D16
16/16, I01–I15 15/15); misses fall in the two known Pot-A families
(count/selection on multi-axle pieces; GM-landscape pockets) plus one new
family — Pot H 1/11 (small multi-axis fragments). Weight: nine pots, 155
pieces, single runs. Next: per-family repair tickets (H-family first), then
the E2E gate proof.

**Jobs (all COMPLETED 0:0):** 33106488 (B, 00:02:17); 33106699 (C, 00:02:18);
33106700 (D1, 00:04:39); 33106701 (D2, 00:02:11); 33106702 (E1, 00:03:45);
33106703 (E2, 00:02:24); 33106704 (F, 00:01:46); 33106705 (G, 00:01:51);
33106706 (H, 00:02:16); 33106707 (I1, 00:03:23); 33106708 (I2, 00:02:44);
33106709 (J, 00:03:24). Full per-piece logs in
`potsac-p10-run/p10<TAG>-<jobid>.out` on Spartan. No commits; Comments-only
ticket edit.
