# Ticket 252 — Pot D paper-arm-ON preprocessing + author score

Answers: E1
Status: results-in
Working in: C:/PR/SfSpp_preprocessing-252 (detached worktree @ 1a7c68d, clean)

## Goal
First paper-arm-ON look at Pot D: run the standard preprocessing pipe (surface split
with paper arm ON by default, edge lanes legacy defaults) over all 29 Pot D pieces
with sampled ORIG inputs, and score every fresh lane against the author breaklines
(median/2mm-coverage/jumps>10mm, lengths, reverse coverage), with overlay PNGs.

## Boundary (per brief)
- Fresh laptop worktree of origin/main 1a7c68d + fresh Spartan clone at 1a7c68d,
  same build node bm172. git pull --ff-only first; STOP on divergence.
- Live checkout untouched. Main worktree (user 204-edit) off limits except this file.
- Preprocessing ONLY. Paper arm ON by default, no SFS_PAPER_CHAIN override.
  Edge lanes legacy defaults (vote OFF, KD-filter OFF — neither exists in edge
  source at 1a7c68d). No assembly/reseat/repair, no commits to main.

## Inputs
- Meshes: /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Mesh/Pot_D_Piece_NN_Mesh_DS.obj (29 pcs 01-29)
- Axes: .../SfS_pp/Axes/Pot_D_Piece_NN_Axis.xyz
- Sampled PCDs: /data/gpfs/projects/punim2657/sfs-potD-214/Dataset_Input/Point/Pot_D/ (29/29, agg md5 ad4bdf9076718d96f52cc5f07f69b9a9)
- Author lanes: .../SfS_pp/Breaklines/Pot_D_Piece_NN_Breakline_[01].pcd (author ships
  Pot D pieces 01-32; only 01-29 have Mesh_DS inputs, so 29/29 of available)

## Build (gate: binary md5s must match rebuild record, else STOP)
- Spartan clone: /data/gpfs/projects/punim2657/sfs-potD-252 @ 1a7c68d, tracked tree clean
- Laptop worktree C:/PR/SfSpp_preprocessing-252 @ same hash, clean
- Job 33690628 (build, bm172): COMPLETED 0:0
- mesh a51e7c1c385a2039c7932780a837c19f (record prefix a51e7c1c3 MATCHES)
- edge dc472b0e87c934b6c487ff8637209864 (record EXACT — same as 238/239/246/249)
- Build gate PASSED. Splitter log confirms paper=PAPER-CHAIN and no SFS_* env
  (defaults rule: paper ON, vote OFF, KDF absent).

## Pipe
- Job 33690681 (pipe, bm172): COMPLETED 0:0
- Census: 58/58 lane files (pota252_pipe/Dataset/Breaklines/Pot_D, 58 fresh + formats = 232 files)
- Out: /data/gpfs/projects/punim2657/pota252_pipe ; log: sfs-potD-252/pota252_pipe_33690681.out

## Scores vs author (med mm / cov pct within 2mm / jumps>10mm / lengths mm / revCov pct)
Matched lane shown; slot = which author lane the fresh file matches
(SWAPPED = pipeline Bl0/Bl1 naming vs author convention differs — stable across
214 and 252 for 27/29 pieces; P22 STRAIGHT in both; P29 flipped STRAIGHT under
paper arm while staying at bar).

| piece | fresh | matches | 252 med/cov | 252 j>10(max) | 252 lenF/lenO | revCov | 214 med/cov | verdict |
|---|---|---|---|---|---|---|---|---|
| P01 | Bl0 | auth Bl1 SWAP | 0.55/100.0 | 0 (2.4) | 630.6/631.2 | 100.0 | 0.48/99.7 | BAR |
| P01 | Bl1 | auth Bl0 SWAP | 0.44/97.4 | 0 (9.1) | 635.5/607.9 | 100.0 | 0.66/96.3 | BAR |
| P02 | Bl0 | auth Bl1 SWAP | 0.60/98.0 | 0 (8.6) | 545.0/524.2 | 100.0 | 0.64/97.3 | BAR |
| P02 | Bl1 | auth Bl0 SWAP | 0.48/97.2 | 1 (11.0) | 524.0/502.0 | 100.0 | 0.63/98.3 | BAR-1J |
| P03 | Bl0 | auth Bl1 SWAP | 1.81/50.3 | 1 (47.0) | 720.2/615.0 | 55.4 | 0.70/99.1 | MISS |
| P03 | Bl1 | auth Bl0 SWAP | 0.70/97.8 | 0 (7.8) | 409.2/393.1 | 100.0 | 0.61/95.6 | BAR |
| P04 | Bl0 | auth Bl1 SWAP | 0.55/98.9 | 0 (6.3) | 488.7/481.7 | 99.6 | 0.52/99.6 | BAR |
| P04 | Bl1 | auth Bl0 SWAP | 0.49/98.0 | 0 (9.6) | 466.8/447.9 | 100.0 | 0.55/96.9 | BAR |
| P05 | Bl0 | auth Bl1 SWAP | 0.60/97.2 | 1 (14.4) | 520.2/493.2 | 100.0 | 0.67/98.2 | BAR-1J |
| P05 | Bl1 | auth Bl0 SWAP | 0.49/97.7 | 0 (9.1) | 473.5/458.7 | 100.0 | 0.67/97.8 | BAR |
| P06 | Bl0 | auth Bl1 SWAP | 0.39/100.0 | 0 (7.5) | 489.9/484.2 | 100.0 | 0.42/95.5 | BAR |
| P06 | Bl1 | auth Bl0 SWAP | 0.61/98.1 | 0 (9.4) | 473.8/455.1 | 100.0 | 0.72/96.0 | BAR |
| P07 | Bl0 | auth Bl1 SWAP | 0.35/98.2 | 0 (7.7) | 398.3/383.1 | 100.0 | 0.69/97.8 | BAR |
| P07 | Bl1 | auth Bl0 SWAP | 0.67/80.9 | 1 (10.0) | 382.6/354.3 | 84.8 | 0.52/97.1 | NEAR-MISS |
| P08 | Bl0 | auth Bl1 SWAP | 0.52/97.1 | 1 (13.6) | 440.2/416.0 | 100.0 | 0.57/99.6 | BAR-1J |
| P08 | Bl1 | auth Bl0 SWAP | 0.72/99.1 | 0 (5.7) | 398.1/391.3 | 100.0 | 0.42/98.2 | BAR |
| P09 | Bl0 | auth Bl1 SWAP | 0.51/97.7 | 0 (8.4) | 467.4/446.8 | 100.0 | 0.47/96.1 | BAR |
| P09 | Bl1 | auth Bl0 SWAP | 0.48/95.8 | 1 (17.7) | 444.3/409.9 | 100.0 | 0.51/92.4 | BAR-1J |
| P10 | Bl0 | auth Bl1 SWAP | 0.49/100.0 | 0 (2.1) | 309.9/307.6 | 100.0 | 0.57/98.3 | BAR |
| P10 | Bl1 | auth Bl0 SWAP | 0.71/93.4 | 1 (27.9) | 350.1/337.5 | 91.7 | 0.56/92.8 | BAR-1J |
| P11 | Bl0 | auth Bl1 SWAP | 0.59/97.0 | 0 (6.9) | 359.7/346.6 | 100.0 | 0.59/98.0 | BAR |
| P11 | Bl1 | auth Bl0 SWAP | 0.45/98.9 | 0 (8.6) | 338.0/323.7 | 100.0 | 0.60/98.4 | BAR |
| P12 | Bl0 | auth Bl1 SWAP | 0.73/66.5 | 1 (43.8) | 373.2/278.7 | 78.2 | 0.57/89.1 | NEAR-MISS |
| P12 | Bl1 | auth Bl0 SWAP | 0.51/94.4 | 1 (11.3) | 299.3/271.9 | 100.0 | 0.77/98.8 | BAR-1J |
| P13 | Bl0 | auth Bl1 SWAP | 0.48/98.3 | 0 (3.1) | 315.8/303.0 | 100.0 | 0.63/97.7 | BAR |
| P13 | Bl1 | auth Bl0 SWAP | 0.76/99.4 | 0 (1.8) | 295.0/294.0 | 100.0 | 0.70/95.4 | BAR |
| P14 | Bl0 | auth Bl1 SWAP | 0.49/95.5 | 1 (18.6) | 292.2/256.8 | 100.0 | 0.64/100.0 | BAR-1J |
| P14 | Bl1 | auth Bl0 SWAP | 0.76/96.8 | 0 (7.2) | 226.8/214.1 | 100.0 | 0.62/100.0 | BAR |
| P15 | Bl0 | auth Bl1 SWAP | 0.57/99.3 | 0 (4.7) | 258.5/251.7 | 100.0 | 0.44/82.0 | BAR |
| P15 | Bl1 | auth Bl0 SWAP | 0.77/100.0 | 0 (2.0) | 218.0/215.6 | 100.0 | 0.43/87.5 | BAR |
| P16 | Bl0 | auth Bl1 SWAP | 0.49/98.6 | 0 (6.7) | 262.3/250.0 | 100.0 | 0.80/76.2 | BAR |
| P16 | Bl1 | auth Bl0 SWAP | 0.72/100.0 | 0 (1.8) | 237.4/236.4 | 100.0 | 1.45/51.8 | BAR |
| P17 | Bl0 | auth Bl1 SWAP | 0.63/99.1 | 0 (3.1) | 192.1/187.2 | 100.0 | 0.52/96.4 | BAR |
| P17 | Bl1 | auth Bl0 SWAP | 0.44/96.9 | 0 (6.4) | 179.2/169.0 | 100.0 | 0.72/98.0 | BAR |
| P18 | Bl0 | auth Bl1 SWAP | 0.51/96.3 | 1 (10.5) | 248.1/231.7 | 100.0 | 0.48/96.3 | BAR-1J |
| P18 | Bl1 | auth Bl0 SWAP | 0.52/97.0 | 1 (12.3) | 246.3/215.9 | 100.0 | 0.71/97.5 | BAR-1J |
| P19 | Bl0 | auth Bl1 SWAP | 0.69/100.0 | 0 (1.8) | 229.4/216.8 | 100.0 | 0.50/93.8 | BAR |
| P19 | Bl1 | auth Bl0 SWAP | 0.79/100.0 | 0 (2.7) | 206.1/203.6 | 100.0 | 0.55/99.1 | BAR |
| P20 | Bl0 | auth Bl1 SWAP | 0.60/100.0 | 0 (4.7) | 229.7/220.5 | 100.0 | 0.74/100.0 | BAR |
| P20 | Bl1 | auth Bl0 SWAP | 0.47/100.0 | 0 (1.8) | 214.8/216.1 | 100.0 | 0.62/100.0 | BAR |
| P21 | Bl0 | auth Bl1 SWAP | 0.54/100.0 | 0 (4.3) | 184.3/180.1 | 100.0 | 0.62/100.0 | BAR |
| P21 | Bl1 | auth Bl0 SWAP | 0.46/97.9 | 0 (6.0) | 173.4/160.1 | 100.0 | 0.52/99.0 | BAR |
| P22 | Bl0 | auth Bl0 SAME | 0.82/84.6 | 0 (5.1) | 246.3/241.3 | 86.5 | 0.79/82.6 | NEAR-MISS |
| P22 | Bl1 | auth Bl1 SAME | 0.50/91.1 | 1 (14.6) | 293.6/289.7 | 87.7 | 0.77/89.7 | BAR-1J |
| P23 | Bl0 | auth Bl1 SWAP | 0.71/99.0 | 0 (3.1) | 184.9/179.2 | 100.0 | 0.68/95.2 | BAR |
| P23 | Bl1 | auth Bl0 SWAP | 0.61/100.0 | 0 (1.8) | 160.4/162.0 | 100.0 | 0.73/100.0 | BAR |
| P24 | Bl0 | auth Bl1 SWAP | 0.50/94.4 | 0 (9.5) | 166.1/146.9 | 100.0 | 0.47/93.5 | BAR |
| P24 | Bl1 | auth Bl0 SWAP | 0.51/92.0 | 1 (13.6) | 166.6/141.4 | 98.7 | 0.63/97.6 | BAR-1J |
| P25 | Bl0 | auth Bl1 SWAP | 0.43/98.7 | 0 (4.4) | 143.0/137.7 | 100.0 | 0.81/85.9 | BAR |
| P25 | Bl1 | auth Bl0 SWAP | 0.70/89.8 | 1 (16.2) | 171.0/142.2 | 100.0 | 0.79/91.2 | NEAR-MISS |
| P26 | Bl0 | auth Bl1 SWAP | 0.42/100.0 | 0 (5.1) | 141.9/138.6 | 100.0 | 0.49/93.2 | BAR |
| P26 | Bl1 | auth Bl0 SWAP | 0.49/96.5 | 0 (4.8) | 156.0/141.2 | 100.0 | 0.62/91.8 | BAR |
| P27 | Bl0 | auth Bl1 SWAP | 0.81/64.7 | 0 (5.6) | 124.4/86.9 | 81.6 | 0.89/62.9 | NEAR-MISS |
| P27 | Bl1 | auth Bl0 SWAP | 0.91/73.3 | 0 (2.6) | 107.0/84.9 | 87.5 | 0.65/70.0 | NEAR-MISS |
| P28 | Bl0 | auth Bl1 SWAP | 0.76/100.0 | 0 (2.8) | 103.6/98.9 | 100.0 | 0.39/98.4 | BAR |
| P28 | Bl1 | auth Bl0 SWAP | 0.54/100.0 | 0 (1.8) | 107.8/102.4 | 100.0 | 0.79/100.0 | BAR |
| P29 | Bl0 | auth Bl0 SAME | 0.48/100.0 | 0 (5.9) | 149.9/137.5 | 98.7 | 0.57/98.5 | BAR |
| P29 | Bl1 | auth Bl1 SAME | 0.75/100.0 | 0 (2.2) | 122.8/120.4 | 100.0 | 0.77/92.9 | BAR |

Tally (58 lanes): med<2mm on all 58; cov>=90pct on 51/58. Clean BAR 41,
BAR with one >10mm jump 11, NEAR-MISS 5 (P07-Bl1-side, P12-Bl0-side, P22-Bl0,
P25-Bl1-side cov 89.8, P27 x2), MISS 1 (P03-Bl0-side). Reverse coverage 100pct
except P03-Bl0-side 55.4, P12-Bl0-side 78.2, P07-Bl1-side 84.8, P22 86-88,
P27 82-88. Scorer: sfs-potD-252/score252.py (score252_table.csv, 116 rows).

## Guards vs 246 / 249 (drift or no-drift, stated)
- Pot A / Pot C NOT re-run in this ticket (boundary = Pot D). No-drift case rests
  on binary identity: edge md5 dc472b0e87c934b6c487ff8637209864 EXACT-matches
  the 238/239/246/249 record; mesh md5 a51e7c1c385a2039c7932780a837c19f
  matches the rebuild record of this ticket; the only source change vs the 239
  mesh is the intended paperChain default flip (235 arm).
- In-pot overlap guards (235 paper-arm numbers reproduced from the same pipe):
  P15 0.57/99.3 + 0.77/100 (235: 0.68/98.4 + 0.54/99.3) no drift; P16
  0.49/98.6 + 0.72/100 (235: 0.46/97.1 + 0.45/99.3) no drift — 214-cure holds;
  P01 at bar as in 214/235; P27 same near-miss class as 235 (ruler caveat stands).
- One small drift WITH cause: P25-Bl1-side 0.70/89.8 with one 16.2mm jump vs
  235 0.46/96.2 — single excursion, overlay P25 shows where.

## Overlays (author black #222222 vs fresh blue #0072B2, 3D + x-z side per lane)
- C:/PR/SfSpp_preprocessing-252/artifacts/pota252/overlays/P01_vs_author.png ..
  P29_vs_author.png (29 files, titles carry med/cov/jumps/lengths/match)
- Eye-checked: P03 (Bl1-file lane sits on author rim; Bl0-file lane follows half
  the rim then loops away), P12 (Bl0-file lane V-dives off rim, 43.8mm jump),
  P01 (both lanes coincide).

## Comments (what this means — judgement stays with lead)
- Paper arm ON holds or improves 27 of 29 Pot D pieces vs the 214 old chain, and
  the 214-cure pieces P15/P16 stay rescued. First full-pot evidence that the arm
  is safe as the default for this pot.
- New finding: P03 is the one piece that gets WORSE under the paper arm — its
  two lanes swap file assignment AND the Bl1-side lane wanders (covers about half
  the rim, one 47mm jump, 17pct extra length). Same flavour as the Pot C tracer
  failures in 249 (C01 tails, C03 runaway), but here one lane of one piece, not
  a whole-piece failure. Possible paper-arm edge case: the re-split changes which
  wall face each lane starts from and the tracer leaves the rim on one side.
  Lead decision: accept P03 as a known single-lane miss, or dig into why the
  split flips its assignment.
- P07-Bl1-side and P12-Bl0-side lose coverage vs 214 (97 to 81pct, 89 to 67pct)
  — regressions to weigh against the P15/P16 rescues.
- P27 remains a near-miss under the ruler caveat from 235; P22 unchanged class.
- Slot naming: pipeline Bl0/Bl1 vs author Bl0/Bl1 differs for 27/29 pieces in
  BOTH 214 and 252 — a stable naming-convention difference, not a fresh defect.
  P29 flips to STRAIGHT under the paper arm while staying at bar (second
  assignment-flip instance alongside P03).

## Evidence
- Clone: /data/gpfs/projects/punim2657/sfs-potD-252 (rev 1a7c68d, clean)
- Build log: sfs-potD-252/pota252_build_33690628.out ; md5s: sfs-potD-252/bin252_md5.txt
- Pipe out: /data/gpfs/projects/punim2657/pota252_pipe ; log: sfs-potD-252/pota252_pipe_33690681.out
- Scores: sfs-potD-252/score252.py, score252_table.csv (copy + lanes tarball
  unpacked at C:/PR/SfSpp_preprocessing-252/artifacts/pota252/)
- sacct: 33690628 COMPLETED 0:0 bm172; 33690681 COMPLETED 0:0 bm172
