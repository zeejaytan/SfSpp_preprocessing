# Ticket 321 — Verify 320's generalisability claim, and the Juglet E2E on the final axes

**Status:** resolved
**Answers:** E1
**Depends on:** 320
**Blocks:** none
**Worker:** lead (this session, verification + run; no worker dispatched)

## The claim under test

Ticket 320 landed a base-disk exception in `sfs_axes/potsac.py` and recorded in `intent/E1`:
the axis method is now generalisable — Pot A restored to 8/8 + 15/15, and 0 of the other 171
pieces across Pots A–J and the Juglet changed. The question asked here: is that substantiated,
and if so, what does the one object never assembled on the final axes (the Juglet) do?

## Verification of 320 (lead, from source, not from the ticket's own numbers)

1. **Code is on main and is what the ticket says** — `sfs_axes/potsac.py:524-525`
   (`w_ax = sum(mean_axs*sizes)/sum(sizes)`; `max_drift = 25.0 if (diag >= 140.0 and w_ax <= 0.90) else 8.0`)
   and `:575, :590-591` (veto requires `sz < 4000 and cw > 0.0065`). Commits `97dad1e` (code) →
   `41494d0` (main HEAD at the time of this check). Working tree clean.
2. **The axis sets differ in exactly one file** — `diff -rq axes318 axes320`: 181 files each,
   one difference, `Pot_A_Piece_01_Axis.xyz`; all eight Pot A pieces are byte-identical to
   `axes317` (`cmp` on each). So 171 of 172 piece sets are untouched, as claimed.
3. **The Pot A job really used the new axis** — the staged file in
   `runs/20261109-1928_97dad1e_t320-potA/work/axes_k3/Pot_A_Piece_01_Axis.xyz` is byte-identical
   to `axes320`; its rank 0 is **0.10°** from `Axes/Pot_A_Piece_01_Axis.xyz`, where `axes318`'s
   rank 0 is **68.97°** from it (the ticket quotes 65.2°, measured against the two-file reference).
4. **The Pot A end-to-end numbers** — `score/acc.tsv` of job `34577139`:
   `A_MOR1 8/8 15/15`, `A_MOR2 8/8 15/15`, `A_K3R1 8/8 15/15`, `A_K3R2 8/8 15/15`.
5. **The class boundary is measured, not fitted** — the true base disk sits at `cw = 0.00204`,
   `sz = 5076`; the wall-piercing skewers the veto exists for sit at `cw >= 0.0078`, `sz <= 1656`.
   The thresholds (`cw > 0.0065`, `sz < 4000`) sit inside a gap of ~3.8x and ~3x, and 171/172
   pieces fall outside the band the rule touches.

**Verdict on 320:** substantiated for the ten sample pots — one rule, no per-pot tuning, Pot A
repaired, every other pot's axis file identical to the set that produced the ticket 319 numbers
(B 9/9, C 4/4, F 5/5, G 7/7, H 11/11, I 25/26, D 23-25/28, E 29-31/31, J 8/11, A 3/8 → 8/8).

Two honest limits: (a) byte-identity guarantees identical *inputs*, not identical assemblies — the
assembler varies ±1–2 sherds on repeats (Pot E gave 30/31 and 31/31 from the same staged inputs);
(b) "generalisable" is false as a statement about the Juglet, which the same ticket left at 5/9
within 10° at K<=3 and 0/9 at rank 0.

## The Juglet end-to-end run on the final axes

- Run: `/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0320_41494d0_t320b-juglet`
- Job: **34617857**, `sacct` **COMPLETED 0:0**, Elapsed `00:02:07` (node `spartan-bm065`).
- Arms: `F20O` = the released `Dataset/Axes/Juglet` (control), `F20K3` = `axes320` top-3, two
  repeats each; everything else (lanes `20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom`,
  floor 20, NP 9, `juglet_orig_block.inc`, `-DJUGLET_ORIG`) copied unchanged from the 8 Nov run.

| arm | repeat | sherd | edge |
|---|---|---|---|
| F20O | r1 | 0/9 | 0/18 |
| F20O | r2 | 0/9 | 0/18 |
| F20K3 | r1 | 0/9 | 0/18 |
| F20K3 | r2 | 0/9 | 0/18 |

- Per piece (ours, both repeats byte-identical): p1 152.5°/614 mm, p2 18.1°/145, p3 9.0°/68,
  p4 109.9°/503, p5 23.5°/40, p6 15.9°/148, p7 21.2°/55, p8 154.0°/524, p9 105.3°/804.
  Four pieces are within 25° but 40–148 mm out; five are 105–154° out. On a ~100 mm vessel that
  is scatter, not a near miss.
- Control (the authors' own released juglet axes) produced transforms for **2 of 9** pieces
  (p2 136.2°/426 mm, p6 176.9°/973 mm) — the control fails harder than ours.
- The result is **identical to the 8 Nov baseline** (`20261108-1615_ecd5bb8_t318b-juglet`, job
  34534787), piece for piece — expected, because `axes320`'s Juglet files are byte-identical to
  `axes318`'s. The run therefore confirms the null on the final code; it cannot overturn it.

## What the run exposed — the Juglet's reference pair disagrees with itself

Transform the released axes by the Juglet ground-truth transforms and see whether the nine
world-frame axes agree (they must, if both files describe the same object):

| object | pieces | spread of world axes vs mean (median / max) |
|---|---|---|
| Juglet | 9 | **20–81°** (per-piece: 29.8, 44.4, 26.7, 20.8, 81.2, 32.4, 62.0, 79.3, 57.5) |
| Pot G (control) | 7 | 1.59° / 2.98° |
| Pot B (control) | 9 | 5.40° / 20.82° |
| Pot A (control) | 8 | 5.56° / 54.37° (p8, the known broken reference) |
| Pot H (control) | 11 | 33.42° / 75.99° |

Checked under three conventions (`a`, `R·a`, `Rᵀ·a`): the Juglet never comes closer than 20°.
So the Juglet's released axes and the Juglet ground-truth transforms do not describe the same
frame. The control arm on that object was never valid, and the "0/9" that both 318b and this run
report cannot be attributed to our axis method — nor can the 5/9 axis column, whose reference is
the same pair.

## Where this leaves the claim

- Pot corpus: the axis method is now one rule that covers all ten pots, with the 319 end-to-end
  numbers standing and Pot A repaired. Substantiated.
- Juglet: not generalisable on the evidence available, and not measurable either — the object's
  reference answer is internally inconsistent. Fixing the Juglet reference (derive one frame from
  either the axes or the GT transforms, and check which agrees with the meshes) is the prerequisite
  for any further Juglet result.
