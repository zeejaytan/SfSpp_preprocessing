# E3 — When do handles and other appendages break surface segmentation and axis extraction?

**Status:** open · **Blocked by:** none · **Effort:** corpus-wide appendage inventory (Pot A..J + Juglet) and crease-separation / axis-robustness tests

## Where it stands

[E2](E2-which-surface-differences-cost-joins.md) proved end-to-end on `Pot_J_Piece_01` ([Surface Parity 14](../.scratch/surface-parity/issues/14-diagnose-j01-s1-lobe-and-voxel-selector-split.md), [Surface Parity 16](../.scratch/surface-parity/issues/16-test-j01-handle-deleted-in-pot-j-assembly.md)) that our `MeshPreprocessingHeadless` outer wall (`Surface_1`) bridged across the body-to-spout crease on `Pot_J_Piece_01` and absorbed `17,795` spout points (`42.2%` of `S1`, extending up to `48.5 mm` off the body wall). That asymmetric spout pulled `J01`'s estimated turning axis `59°–70°` away from true and dropped Pot J from `17/21` joins to `6/21`; deleting the spout alone recovered `17/21` (`5/5` `J01` seams) with the unchanged `SHIP` selector, beating the Authors' `16/21` control.

The open puzzle raised by the conservator on 2026-11-28 is why only `Pot_J_Piece_01` broke end-to-end when Pot J is not the only vessel with appendages (several pots in `Pot A..J` and the `Juglet` neck sherd `Juglet_Piece_1` also carry handles, lugs, or spouts). Initial read-only inspection of `t09` segmentation logs suggests three untested hypotheses:

1. **Authors' benchmark exclusions vs our pipeline:** The SfS++ authors manually excluded 20 separate special parts ("handle, nose, or ornament" across Pots C, D, E, F, I, and J; see `SfSpp_preprocessing/AGENTS.md`) from their released `Point/` benchmark input. **Our own surface pipeline did NOT drop those 20 pieces** — it simply never saw them because `t09` ran on the `143` released + `5` derived clouds (`148` pieces). On real pottery or on the full mesh set, our pipeline receives every handle, spout, nose, and ornament sherd without pre-filtering.
2. **Crease separation vs crease bridging (`Pot_J_Piece_03` clarified):** Across the `157` processed `Pot A..J` (`148`) + `Juglet` (`9`) pieces in `t09` ([Census attached appendages in t09 and Juglet](../.scratch/appendage-handling/issues/17-census-attached-appendages-in-t09-and-juglet.md), job `35956230`), `89` pieces carry a substantial 3rd cluster (`>=5%` or `>=2,000` pts), including `Pot_J_Piece_03` (`11,511` pts, `18.8%`). Visual 3D inspection showed `Pot_J_Piece_03`'s dropped 3rd cluster is a flat-base-to-wall/rim crease cut (`3,773` uncovered vertices; `1.87°` best GT axis), not a handle, while `Pot_J_Piece_02` shattered its small lug across `16` small clusters (`18` clusters total; `0.0%` off-author on `S1`; `6.82°` GT).
3. **Body-wall support vs appendage share (`Juglet_Piece_1` proved):** On `Juglet_Piece_1` (`S0 = 54,917`, `S1 = 73,020`), `Surface_1` *did* absorb the loop handle (`7,658` pts, `10.5%` of `S1` sitting `> 4.0 mm` from `S0`, verified visually in 3D/XZ/YZ). Yet removing the handle shifted the estimated axis by only `0.023°` (`1.2480° -> 1.2248°` GT) and `0.17 mm` (`8.9376 -> 8.7665 mm`) because `Surface_0` wraps **`359.00°`** around the circular neck/shoulder collar — whereas failing `Pot_J_Piece_01` has only `135.00°` angular wrap alongside a `36.8%–42.2%` absorbed spout (`88.56°` rank-0 / `69.97°` best GT error).

Weight: `1` dedicated `E3` diagnostic census covering all `157` processed `t09` + `Juglet` pieces ([Census attached appendages in t09 and Juglet](../.scratch/appendage-handling/issues/17-census-attached-appendages-in-t09-and-juglet.md), job `35956230`, `COMPLETED 0:0`, `3` renders verified) plus [E2](E2-which-surface-differences-cost-joins.md) end-to-end causality on `Pot_J_Piece_01` (`Pot J` `6/21 -> 17/21`). The `20` author-excluded special-part meshes and quantitative crease/wrap thresholds remain untested.

Next: Charted under [Appendage handling map](../.scratch/appendage-handling/map.md). [Census attached appendages in t09 and Juglet](../.scratch/appendage-handling/issues/17-census-attached-appendages-in-t09-and-juglet.md) is **resolved**, unblocking [Separate crease bridging from body support on surviving sherds](../.scratch/appendage-handling/issues/20-separate-crease-bridging-from-body-support-on-surviving-sherds.md) (`ready-for-agent`) alongside [Probe the 20 author-excluded special-part meshes](../.scratch/appendage-handling/issues/19-probe-the-20-author-excluded-special-part-meshes.md) (`ready-for-agent`).

## Why it matters

Real archaeological pottery — including the Juglet and future CSC/Rabati vessels — frequently carries handles, lugs, and spouts on body sherds as well as separate handle/ornament pieces. We cannot rely on the authors' manual input exclusion because our own pipeline never drops those 20 special parts; side-wall or appended sherds will silently fail axis estimation and break reassembly unless segmentation stops at the crease or axis estimation ignores non-axisymmetric protrusions.

## Done when

- [ ] Inventory and visually render (with 20 mm scale bars) every handle-, lug-, or spout-bearing sherd in `Pot A..J` (both the `148` processed clouds and the `20` author-excluded special-part meshes where present) and `Juglet`, classifying for each whether `MeshPreprocessingHeadless` dropped the appendage as a separate cluster or absorbed it into `Surface_0`/`Surface_1`, and measuring its share of wall points and resulting axis error (degrees and mm).
- [ ] Establish why `Juglet_Piece_1` (and any other appendage-bearing sherd in `Pot A..J`) did or did not fail axis estimation and assembly compared with `Pot_J_Piece_01` (separating crease-splitting, appendage-to-body fraction, and circumferential wrap).
- [ ] Decide — based on the census — whether a general segmentation or axis-estimation guard is needed for appendage-bearing sherds, and if built, validate it across all 10 pots + `def_3x` Juglet with zero regressions and `Pot J >= 16/21` on canonical own surfaces without manual trimming.

## Gate / stop condition

Start with a read-only visual census of `Juglet_Piece_1` and all appendage-bearing sherds in `Pot A..J` before changing any C++ segmentation or Python axis code. If appendages are absorbed only when the body-to-appendage fillet is gentler than the current region-growing angle/curvature threshold, test a single general geometric criterion (no per-pot or per-piece rules) and stop if it hurts smooth body walls or any of the 9 passing pots / Juglet.

## Source

[E2](E2-which-surface-differences-cost-joins.md) ([Surface Parity 14](../.scratch/surface-parity/issues/14-diagnose-j01-s1-lobe-and-voxel-selector-split.md) and [16](../.scratch/surface-parity/issues/16-test-j01-handle-deleted-in-pot-j-assembly.md)), `SfSpp_preprocessing/AGENTS.md` (20 excluded special-part pieces), and the conservator's question on 2026-11-28.
