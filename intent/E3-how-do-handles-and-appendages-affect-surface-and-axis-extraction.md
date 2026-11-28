# E3 — When do handles and other appendages break surface segmentation and axis extraction?

**Status:** open · **Blocked by:** none · **Effort:** corpus-wide appendage inventory (Pot A..J + Juglet) and crease-separation / axis-robustness tests

## Where it stands

[E2](E2-which-surface-differences-cost-joins.md) proved end-to-end on `Pot_J_Piece_01` ([Surface Parity 14](../.scratch/surface-parity/issues/14-diagnose-j01-s1-lobe-and-voxel-selector-split.md), [Surface Parity 16](../.scratch/surface-parity/issues/16-test-j01-handle-deleted-in-pot-j-assembly.md)) that our `MeshPreprocessingHeadless` outer wall (`Surface_1`) bridged across the body-to-spout crease on `Pot_J_Piece_01` and absorbed `17,795` spout points (`42.2%` of `S1`, extending up to `48.5 mm` off the body wall). That asymmetric spout pulled `J01`'s estimated turning axis `59°–70°` away from true and dropped Pot J from `17/21` joins to `6/21`; deleting the spout alone recovered `17/21` (`5/5` `J01` seams) with the unchanged `SHIP` selector, beating the Authors' `16/21` control.

The open puzzle raised by the conservator on 2026-11-28 is why only `Pot_J_Piece_01` broke end-to-end when Pot J is not the only vessel with appendages (several pots in `Pot A..J` and the `Juglet` neck sherd `Juglet_Piece_1` also carry handles, lugs, or spouts). Initial read-only inspection of `t09` segmentation logs suggests three untested hypotheses:

1. **Benchmark exclusions hide most handle sherds:** The SfS++ authors excluded 20 separate special parts ("handle, nose, or ornament" across Pots C, D, E, F, I, and J; see `SfSpp_preprocessing/AGENTS.md`), leaving only body sherds that retain an attached appendage.
2. **Crease separation vs crease bridging:** Some attached appendages appear to split off as a discarded third cluster (for example `Pot_J_Piece_03` logged an `11,511`-point third cluster alongside `21,003` and `13,893` wall clusters in `t09`), whereas `Pot_J_Piece_01` (`sizes = 21,981, 39,864, 159`) bridged the crease and absorbed the spout into `Surface_1`.
3. **Body-wall support vs appendage share (`Juglet_Piece_1`):** In `t09`, `Juglet_Piece_1` logged `S0 = 54,917` vs `S1 = 73,020` (`~18k` more points on `S1`, with two clusters holding `81.8%` of the cloud), suggesting `S1` may also absorb part of the Juglet handle — yet the `def_3x` Juglet still seated `9/9` (`0.456 mm`), possibly because `Juglet_Piece_1` is a full 360° neck/shoulder collar whose axisymmetric body outweighs the handle, unlike `Pot_J_Piece_01`'s smaller side-wall patch (`42.2%` spout).

Weight: Zero dedicated `E3` runs yet; hypothesis-generating observations come from [E2](E2-which-surface-differences-cost-joins.md) (`Pot_J_Piece_01`, `1` piece proved end-to-end) and read-only `t09` log counts on `Juglet_Piece_1` and `Pot_J_Piece_03` (not yet rendered in 3D).

Next: Census every appendage-bearing sherd across `Pot A..J` (including the 20 excluded pieces if meshes exist on Spartan) and `Juglet` (`Juglet_Piece_1` first), render `Surface_0` / `Surface_1` over each mesh to witness whether `MeshPreprocessingHeadless` kept or dropped each handle, spout, or lug, and measure how much each appendage shifts the estimated axis.

## Why it matters

Real archaeological pottery — including the Juglet and future CSC/Rabati vessels — frequently carries handles, lugs, and spouts attached to body sherds. If our preprocessing only survived `Pot A..I` and `Juglet` because benchmark handles were pre-excluded or sat on a 360° neck collar, side-wall sherds with attached appendages will silently fail axis estimation and break reassembly unless segmentation stops at the crease or axis estimation ignores non-axisymmetric protrusions.

## Done when

- [ ] Inventory and visually render (with 20 mm scale bars) every handle-, lug-, or spout-bearing sherd in `Pot A..J` and `Juglet`, classifying for each whether `MeshPreprocessingHeadless` dropped the appendage as a separate cluster or absorbed it into `Surface_0`/`Surface_1`, and measuring its share of wall points and resulting axis error (degrees and mm).
- [ ] Establish why `Juglet_Piece_1` (and any other appendage-bearing sherd in `Pot A..J`) did or did not fail axis estimation and assembly compared with `Pot_J_Piece_01` (separating crease-splitting, appendage-to-body fraction, and circumferential wrap).
- [ ] Decide — based on the census — whether a general segmentation or axis-estimation guard is needed for appendage-bearing sherds, and if built, validate it across all 10 pots + `def_3x` Juglet with zero regressions and `Pot J >= 16/21` on canonical own surfaces without manual trimming.

## Gate / stop condition

Start with a read-only visual census of `Juglet_Piece_1` and all appendage-bearing sherds in `Pot A..J` before changing any C++ segmentation or Python axis code. If appendages are absorbed only when the body-to-appendage fillet is gentler than the current region-growing angle/curvature threshold, test a single general geometric criterion (no per-pot or per-piece rules) and stop if it hurts smooth body walls or any of the 9 passing pots / Juglet.

## Source

[E2](E2-which-surface-differences-cost-joins.md) ([Surface Parity 14](../.scratch/surface-parity/issues/14-diagnose-j01-s1-lobe-and-voxel-selector-split.md) and [16](../.scratch/surface-parity/issues/16-test-j01-handle-deleted-in-pot-j-assembly.md)), `SfSpp_preprocessing/AGENTS.md` (20 excluded special-part pieces), and the conservator's question on 2026-11-28.
