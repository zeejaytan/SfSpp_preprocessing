# Appendage handling in SfS++ surface and axis extraction

**Answers:** E3
**Prior work searched:** GitHub "Structure-from-Sherds", "SfSpp_preprocessing", "PotSAC", "archaeological pottery fragment handle spout segmentation"; project page https://sj-yoo.info/sfs/; arXiv 2502.13986. Found: https://github.com/DominicoRyu/SfSpp_preprocessing (upstream preprocessing using curvature/normal region growing), https://github.com/SeongJong-Yoo/structure-from-sherds-pp (SfS++ assembler; paper manually excludes 20 special-part sherds), https://github.com/hjsg1010/pottery (DGCNN shard part classification), and https://github.com/lrncrd/PyPottery (2D pottery profile suite); no off-the-shelf geometric body-vs-appendage crease cutter for SfS++ point clouds found.

## Destination

Explain why `Pot_J_Piece_01` failed surface and axis extraction while `Juglet_Piece_1` and `Pot A..I` survived (covering both **attached appendages** and the `20` author-excluded **standalone special parts**), decide whether a general geometric guard is warranted, and if built validate it across all `10` pots + `def_3x` Juglet (`Pot J >= 16/21` on canonical own surfaces without manual trimming, zero regressions elsewhere).

## Notes

- Domain terms live in [CONTEXT.md](../../CONTEXT.md) (**appendage**, **Surface_0**, **Surface_1**); benchmark caveats live in [AGENTS.md](../../AGENTS.md).
- Every geometric claim must be witnessed in 3D/orthogonal renders with a `20 mm` scale bar before acceptance.
- Zero per-pot, per-piece, or manual-trimming rules; any candidate guard must use general geometry.
- Heavy compute runs only on Spartan compute nodes (`sbatch`); execution tickets run via DeepSeek through DSH Baton with a private hidden acceptance check.

## Decisions so far

<!-- One line per resolved ticket: - [Ticket Title](issues/NN-slug.md): one-line gist of the answer -->

## Not yet specified

- Guard mechanism and home (if census proves a guard is warranted): C++ `MeshPreprocessingHeadless` crease-splitting vs Python `sfs_axes` non-axisymmetric outlier rejection.
- Pipeline policy when fed standalone special parts (broken-off handles, noses, ornaments with negligible body wall).
- Full `10`-pot + `def_3x` Juglet validation spec (`to-spec` / implementation tickets) once the guard design is chosen in [Decide appendage guard location and scope](issues/04-decide-appendage-guard-location-and-scope.md).

## Out of scope

- Axisymmetric vessel features (rims, bases, horizontal cordons/flanges).
- CSC hollow-shell handle modelling tests (handled under CSC intents).
- Hard-coded piece exclusion lists or manual mesh trimming.
