# Ticket 256 — Pot G paper-arm-ON preprocessing + author score

Answers: E1
Status: results-in
Working in: C:/PR/SfSpp_preprocessing-256 (detached worktree @ 0650111, clean except untracked artifacts/)

## Goal
First paper-arm-ON look at Pot G: run the standard preprocessing pipe (surface split
with paper arm ON by default, edge lanes legacy defaults) over all 7 Pot G pieces
with sampled inputs, and score every fresh lane against the author breaklines
(median/2mm-coverage/jumps>10mm, lengths, reverse coverage), with overlay PNGs.
Follow the 250/251/252 recipe.

## Boundary (per brief, as run)
- Fresh laptop worktree C:/PR/SfSpp_preprocessing-256 @ 0650111 (== origin/main,
  detached, HEAD verified 0650111edafe7943bcd0b65fc7c7a83c12517b0a).
- Fresh Spartan clone /data/gpfs/projects/punim2657/sfs-potG-256 @ 0650111, tracked
  tree clean. Deviation to record: the live checkout is BEHIND (f4add97, predates
  the target) so a local clone could not yield 0650111; cloned locally then fetched
  the full SHA from GitHub (zeejaytan/SfSpp_preprocessing) and checked out --detach.
  No pull --ff-only was meaningful on a fresh clone (nothing to diverge); live
  checkout untouched (read-only git cat-file/log only). No divergence to report.
- Main worktree (user 204-edit still M, uncommitted) off limits except this file.
- Preprocessing ONLY. Paper arm ON by default, no SFS_PAPER_CHAIN override.
  Edge lanes legacy defaults (vote OFF, KD-filter OFF — 0 VOTE_ORDER/SFS_VOTE/
  SFS_KD markers in 0650111 edgeline source). No assembly/reseat/repair, no commits.
- MSYS2_ARG_CONV_EXCL='*' on laptop ops. Pot colours: author black #222222,
  fresh blue #0072B2 throughout (250/251/252 scheme).

## Inputs
- Meshes: /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Mesh/Pot_G_Piece_0{1..7}_Mesh_DS.obj (7/7)
- Axes: .../SfS_pp/Axes/Pot_G_Piece_0{1..7}_Axis.xyz (7/7)
- Sampled PCDs: /data/gpfs/projects/punim2657/pota39_repro/prep/pota39_G/Dataset/Point/Pot_G/Pot_G_Piece_0{1..7}_Point.pcd
  (7/7, agg md5 e4bdf993d4c8f31fc13bce538324f681; per-file c518d5f2/01, 24da7eb2/02, 7fbf51ec/03, 44d3e938/04, e7af20ef/05, db290004/06, e255a092/07)
- Author lanes: .../SfS_pp/Breaklines/Pot_G_Piece_0{1..7}_Breakline_[01].pcd (14/14)

## Build (gate: binary md5s must match staged record, else STOP)
- No rebuild per brief: staged bm172 binaries read-only from sfs-potD-252/build-252
  (job 33690628, COMPLETED 0:0 bm172) into sfs-potG-256/build-256/.
- mesh a51e7c1c385a2039c7932780a837c19f (MATCHES brief) — in-job md5 gate PASSED
- edge dc472b0e87c934b6c487ff8637209864 (MATCHES brief) — in-job md5 gate PASSED
- Source guard: 'bool paperChain = true' present in mesh_processing_headless.cpp
  (0650111); SFS_PAPER_CHAIN/SFS_VOTE_ORDER/SFS_KD_FILTER unset in job env.

## Pipe
- Job 33691232 (pipe, bm172): FAILED 1:0 on launch — worker's own seq-pad bug
  (seq -w 1 7 yields 1..7, guard rightly refused MISSING-PCD 1). Zero compute, guard
  worked as designed. Fixed to seq -w 01 07, resubmitted.
- Job 33691233 (pipe, bm172): COMPLETED 0:0. .err empty (0 bytes).
- Mesh clusters per piece: 8/6/6/4/3/3/11 (P01..P07).
- Mesh log: 7x paper=PAPER-CHAIN (SPLITTER-234 theta=4/kappa=1/nb=10).
- Census: 14/14 lane PCDs (Pot_G/Dataset/Breaklines, + .ply/.xyz formats).
  Headers: P01 137/126, P02 115/118, P03 105/96, P04 108/100, P05 101/95, P06 88/87, P07 72/73.
- Out: /data/gpfs/projects/punim2657/pota256_pipe ; log: sfs-potG-256/pota256_pipe_33691233.out

## Scores vs author (matched lane; slot = which author lane the fresh file matches)
Bar: med<2mm + cov>=90%. lenO = MATCHED author lane length.

| piece | fresh | matches | med/cov | j>10 (jmax) | lenF/lenO | revCov | verdict |
|---|---|---|---|---|---|---|---|
| P01 | Bl0 | auth Bl1 SWAP | 0.66/90.5 | 1 (14.6, idx4) | 257.6/225.3 | 99.2 | BAR-1J |
| P01 | Bl1 | auth Bl0 SWAP | 0.70/100.0 | 0 | 226.9/226.4 | 100.0 | BAR |
| P02 | Bl0 | auth Bl1 SWAP | 0.74/100.0 | 0 | 204.8/207.2 | 100.0 | BAR |
| P02 | Bl1 | auth Bl0 SWAP | 0.55/95.8 | 1 (11.3, idx18) | 220.1/198.8 | 100.0 | BAR-1J |
| P03 | Bl0 | auth Bl1 SWAP | 0.38/99.0 | 0 | 189.1/182.2 | 100.0 | BAR |
| P03 | Bl1 | auth Bl0 SWAP | 0.69/100.0 | 0 | 172.0/168.5 | 100.0 | BAR |
| P04 | Bl0 | auth Bl1 SWAP | 0.58/97.2 | 1 (10.4, idx25) | 201.2/184.4 | 100.0 | BAR-1J |
| P04 | Bl1 | auth Bl0 SWAP | 0.56/98.0 | 0 | 179.5/171.6 | 100.0 | BAR |
| P05 | Bl0 | auth Bl1 SWAP | 0.71/96.0 | 1 (11.0, idx10) | 189.2/166.9 | 100.0 | BAR-1J |
| P05 | Bl1 | auth Bl0 SWAP | 0.54/100.0 | 0 | 167.8/166.7 | 100.0 | BAR |
| P06 | Bl0 | auth Bl1 SWAP | 0.68/95.5 | 0 | 164.6/147.3 | 100.0 | BAR |
| P06 | Bl1 | auth Bl0 SWAP | 0.28/94.3 | 0 | 161.0/144.3 | 100.0 | BAR |
| P07 | Bl0 | auth Bl0 STRAIGHT | 0.72/87.5 | 0 | 131.0/113.0 | 95.3 | NEAR-MISS |
| P07 | Bl1 | auth Bl1 STRAIGHT | 0.35/76.7 | 0 | 134.5/106.6 | 91.7 | NEAR-MISS |

Tally (14 lanes, matched): med<2mm on 14/14; cov>=90% on 12/14. Clean BAR 8,
BAR with one >10mm jump 4 (P01-Bl0side, P02-Bl1side, P04-Bl0side, P05-Bl0side),
NEAR-MISS 2 (P07 x2, coverage). Reverse coverage 100% except P07 (95.3/91.7).
Scorer: sfs-potG-256/score256.py (login node); full text: score256_out.txt alongside.
- Cross-lane slot check: P01–P06 both lanes decisively SWAPPED (straight med
  2.24–3.29 at cov 11–40% vs cross med 0.28–0.74 at cov 90.5–100%). P07 both
  STRAIGHT (cross 4.86/0.0, 4.12/0.0). Same systematic file↔author naming offset
  seen on 27/29 Pot D pieces in 214+252 — with one caveat (see Guards).
- z/r extremes match author within ~1.6mm on all lanes (e.g. P01-fileBl0
  zF=[431.3,496.7] zO=[431.2,495.1] rF=[17.7,84.0] rO=[17.0,84.2]); no excursions
  (contrast 249 C01 +11/+15mm z, r-min ~1mm; C03-Bl1 +45mm z, r-max 74mm).

## Guards vs prior-pot patterns (drift or no-drift, stated)
- P15/P16-style cures: NOTHING TO COMPARE — first Pot G look, no prior Pot G run,
  no known cure pieces on this pot. No lane shows a pre-cure failure shape.
- P03-style single-lane miss watch: NO INSTANCE. No lane with runaway length +
  big jump + rev collapse (worst length ratio 1.26x P07-Bl1 with rev 91.7 and no
  jump>10 — vs Pot D P03-Bl0-side 1.17x + 47mm jump + rev 55.4). No C01-style tails
  (max 1.26x vs 1.8x with rev 100). No C03-Bl1-style runaway (2.6x, rev 40).
- Naming-swap caveat: unlike Pot D (swap present in BOTH legacy 214 and paper 252,
  proving convention), Pot G has no legacy run — the P01–P06 swap is consistent and
  decisive but unattributed: file it as Pot-D-style convention difference, staged
  for the lead to confirm against any legacy Pot G evidence (e.g. pota39_G Temp trees).
- Fresh-vs-author lengths 0.99–1.16x on P01–P06 (matched), 1.16/1.26x on P07.

## Overlays (author black #222222, fresh blue #0072B2; 3D + X-Y/X-Z/Y-Z equal-aspect; titles carry med/cov/jumps/lengths/match)
- Eye-checked: P01-fileBl0 (blue tracks black all around, one chord shortcut at
  idx4 = the 14.6mm jump), P05-fileBl0 (same flavour, 11.0mm chord at idx10),
  P07-fileBl1 (no runaway; extra end loops + overshoots explain cov 76.7 at jmax 6.7).
  Views match the numbers; no runaways anywhere.
- Laptop: C:/PR/SfSpp_preprocessing-256/artifacts/pota256/overlays256/P01_fileBl0_vs_authorBl1.png ... P07_fileBl1_vs_authorBl1.png (14 files) + score256_used.py (copy of score256.py) + score256_out.txt.
- Spartan masters: /data/gpfs/projects/punim2657/sfs-potG-256/overlays256/ (14 files, overlay256.py) + overlays256.tar.gz (overlays + scorer + out + sbatch + mesh md5s).

## Verdict (staged, judgement stays with lead)
- Preprocessing: all 7 Pot G pieces both lanes extracted on the paper-ON-default
  binary; 12/14 lanes AT BAR on the matched metric (med 0.28–0.74, cov 90.5–100,
  rev ~100, ranges match). 4 lanes carry exactly one marginal jump (10.4–14.6mm,
  all chord shortcuts on eye-check). P07 (smallest piece) near-miss on coverage
  both lanes — extra end loops, not a runaway.
- First-look lead, not a conclusion: one pot (G, 7 pieces), one pipe run (33691233)
  + deterministic rescoring. No fix proposed, nothing committed to main (only this
  ticket file edited in the main worktree; pipe/scorer/overlays live in sfs-potG-256
  + laptop -256 worktree, uncommitted). STAGED FOR LEAD: seat decision, swap-convention
  confirmation, and whether P07 wants a legacy-arm comparison.
