# ticket 29 - what angle does each vessel's wall need?

Run 20261027-1637_7c3248f_t29-angle-survey, job 33865557, commit 7c3248fbbe5370636210fa7288eb5dc1f328910e.

## What the replica is, and what it is not

instruments/replica29.py is the ticket-28 replica of growPaper234
(mesh_processing_headless.cpp:2972-3030, called at :3470) with the theta ladder and
the angle measurement added. It reproduces the region growing only: it knows nothing
about the merge step, nothing about the 3 mm reassignment, and nothing about the
curvature-driven normal estimation that runs before the growth. A theta that looks
right here is a candidate for a pipeline run on the same pieces, not a result.

Part A is not the replica: it reads the rung-2 cloud and normals the pipeline itself
wrote, so those angles are the angles the growth saw.

A cloud whose rung-2 sidecar says "paper_chain": false was segmented by
pcl::RegionGrowing (:3477-3487), not by growPaper234, so the replica sizes beside it
cannot be a gate. Those rows are marked NOT-GATED-sidecar-is-pcl-region-growing.

## Parameters

- kappa 1.000, nb 10, floor 50 points, thetas 2.00, 3.40, 4.00, 5.00, 6.00, 8.00, 10.00, 12.00.
- curvature recomputed as mesh_processing_headless.cpp:745-747 does: k = max(10, min(50, npts/300)),
  curvature = lambda_min / trace(cov) <= 1/3, so the curvature gate cannot refuse while kappa = 1.
- part A pair set: each point's nb nearest neighbours, self skipped, i.e. the BFS
  candidate set; angles in the getAngle3D arithmetic (float normalise, float dot,
  clamp, double acos). Percentiles are over all n*k directed pairs.
- part D criterion, as applied: a Juglet cloud passes at a theta when it has at least
  2 regions at or above the floor and kgate >= 0.5; Pot A 07 passes when it has at
  least 8 regions at or above the floor and its two largest are still at least 3093
  and 2850 points (the pipeline's own rung-2 sizes, so a larger region counts as intact
  and a split one does not).

## Part C - the calibration gate (run first; the run stops if it fails)

| cloud | npts | paper_chain | pipeline rung-2 sizes | replica >= floor | max delta | verdict |
|---|---|---|---|---|---|---|
| B/Juglet_Piece_2 | 1031 | True | - | - | 0 | MATCH |
| B/Juglet_Piece_3 | 1467 | True | 169,99 | 169,99 | 0 | MATCH |
| B/Juglet_Piece_5 | 3021 | True | 679 | 679 | 0 | MATCH |
| B/Juglet_Piece_7 | 4254 | True | 326,263,77,68,65 | 326,263,77,68,65 | 0 | MATCH |
| D/Juglet_Piece_2 | 1031 | False | 174,65 | - |  | NOT-GATED-sidecar-is-pcl-region-growing |
| D/Juglet_Piece_3 | 1467 | False | 343 | 169,99 |  | NOT-GATED-sidecar-is-pcl-region-growing |
| D/Juglet_Piece_5 | 3021 | False | 828,63 | 679 |  | NOT-GATED-sidecar-is-pcl-region-growing |
| D/Juglet_Piece_7 | 4254 | False | 809,553,84,84,53 | 326,263,77,68,65 |  | NOT-GATED-sidecar-is-pcl-region-growing |
| E/Juglet_Piece_2 | 2565 | False | 94,80,61 | - |  | NOT-GATED-sidecar-is-pcl-region-growing |
| E/Juglet_Piece_3 | 3486 | False | 487 | 284 |  | NOT-GATED-sidecar-is-pcl-region-growing |
| E/Juglet_Piece_5 | 6208 | False | 1000,60,58 | 757,52 |  | NOT-GATED-sidecar-is-pcl-region-growing |
| E/Juglet_Piece_7 | 8421 | False | 1701,453,147,108,100,64,63,63,53,50 | 1162,114,66,55 |  | NOT-GATED-sidecar-is-pcl-region-growing |
| PA/Pot_A_Piece_07 | 8598 | True | 3093,2850,203,170,144,120,73,71 | 3093,2850,203,170,134,120,73,71 | 10 | MATCH |

## Files

- out/calibration.tsv
- out/preflight.tsv
- out/angles.tsv
- out/angles_hist.json
- out/theta_ladder.tsv
- out/partD.tsv
- out/figure.txt
- out/cells/
- out/GEOMETRY_DELETED.txt
- out/dump_inventory_before.tsv
- out/dump_inventory_after.tsv

Figure: /data/gpfs/projects/punim2657/SfSpp/runs/20261027-1637_7c3248f_t29-angle-survey/out/ticket29_angles_vs_theta.png, 18.0 x 11.0 in, 2880 x 1760 px at dpi 160, 0.15875 mm/px.

