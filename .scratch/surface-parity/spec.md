# Surface parity against the SfS++ sample input

**Answers:** E2

**Prior work searched:** GitHub “Structure-from-Sherds++” and “PotSAC” found the [authors’ assembler](https://github.com/SeongJong-Yoo/structure-from-sherds-pp) and [preprocessing](https://github.com/DominicoRyu/SfSpp_preprocessing). The [project page](https://sj-yoo.info/sfs/), [Hugging Face paper page](https://huggingface.co/papers/2502.13986), and [arXiv v1](https://arxiv.org/html/2502.13986v1#S4.SS2.SSS2) lead to the released benchmark and the two-wall axis method. The archived comparison uses the Ticket 19 executable built from the pinned assembler base `40b3529` with tracing.

## Problem

Our estimator can match the authors’ Pot E sample-input result with axes estimated from their surfaces. On our surfaces it loses three joins with the same breaklines and assembler. The full surface swap changes wall coverage, point sampling, and normals together, so it cannot identify the difference that matters. E31’s reference placement is on the wall. Base handling is outside the initial experiment.

## Approach

1. Use 27–28 as the first test. Compare both saved estimation walls on E27 and E28 in their existing scan frame. Confirm the inner and outer correspondence and record where the clouds agree, where one lacks coverage, how far apart points are, and how much the normals differ on matched patches.
2. Reproduce the full axis-set contrast and swap only E27’s saved axis file in each direction. Use the existing fracture matching hook and the saved-pose scorer. This test identifies which input to vary in a subsequent surface experiment. It also permits the result that the join depends on multiple sherds or the assembly context.
3. Change one wall property at a time. Start with normals on identical point coordinates and order. Test coverage with defined regions and common spatial sampling, and density within shared coverage, in separate comparisons. Report any coupling explicitly. Neighbourhood size affects estimated normals, so keep the physical support fixed when recomputing them. [PCL normal estimation guide](https://pointclouds.org/documentation/tutorials/normal_estimation.html#selecting-the-right-scale)
4. Carry a useful change from surface samples through ranked axes, fracture stretches, and final scored joins. Keep the authors’ released files and the files estimated from their surfaces as separate controls. Confirm the effect in repeated runs before proposing an extraction change.

## Verification

- The comparison uses one byte-identical assembler, unchanged breaklines, assembly walls, mesh and truth, the archived axis-estimator recipe, and the same candidate limit. Each single-file contrast has exactly one differing hash.
- Record matched and unmatched points separately, compare normals on spatially paired points and check both angular direction and line placement. A closer axis by itself is insufficient evidence of recovery.
- Use locked views and a physical scale for surfaces and any changed placement. Use the same reference scorer throughout. If positive and negative controls fail to separate, publish the failed control and stop attribution.

## Scope

First slice: [01 — Isolate E27’s surface-to-axis effect at join 27–28](issues/01-isolate-e27-surface-axis-effect.md). The [next slice](issues/04-test-wall-normals-at-fixed-points.md) tests wall normals directly. Localise the assembly effect further if needed. Changes to the axis estimator, shortlist, assembler, scorer or reference corpus are outside this effort’s initial experiments.
