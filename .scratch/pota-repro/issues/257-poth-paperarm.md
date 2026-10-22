# Ticket 257 — Pot H paper-arm-ON preprocessing + author score

**What to build:** first paper-arm-ON look at Pot H: run the standard preprocessing pipe
(surface split with paper arm ON by default, edge lanes legacy defaults) over all 11 Pot H
pieces with sampled ORIG inputs, and score every fresh lane against the author breaklines
(median/2mm-coverage/jumps>10mm, lengths, reverse coverage), with overlay PNGs.
Follow the 250/251/252 recipe.

**Answers:** E1

**Blocked by:** 250 (Pot A paper-arm-ON), 251 (Pot C paper-arm-ON), 252 (Pot D paper-arm-ON).

**Status:** results-in
**Working in:** subagent session-61c820f6 (2026-10-23)

- [x] All 11 Pot H pieces (H01–H11) both lanes extracted with default-ON binary
- [x] Scored vs author (med/cov<2mm, jumps>10mm, lengths, reverse coverage)
- [x] Cross-lane slot check (all lanes STRAIGHT, no swap)
- [x] Overlay PNGs (author vs fresh, distinct colours, eye-checked)
- [x] Guards vs prior-pot pattern cited (P15/P16-style cures N/A; P03-style single-lane miss watch HIT)

## Boundary (as run)

- Laptop: fresh detached worktree C:/PR/SfSpp_preprocessing-257 @ 0650111 (== origin/main;
  `git pull --ff-only` already up to date). Main worktree untouched except this ticket file
  (204-edit still M, uncommitted).
- Spartan: fresh clone /data/gpfs/projects/punim2657/sfs-potH-257 @ 0650111, tracked tree clean;
  live checkout left untouched (f4add97, behind + untracked Juglet state, per 250/251/252
  precedent — NOT a divergence, left alone, no pull).
- Preprocessing ONLY. Surface split with paper arm default ON: SFS_PAPER_CHAIN deliberately
  UNSET (in-job guard aborts if set). Edge lanes legacy defaults: vote OFF, KD-filter OFF —
  verified this binary carries neither (0 VOTE_ORDER/SFS_VOTE/SFS_KD markers in edge source
  at 0650111). No assembly/reseat/repair, no commits to main.

## Inputs

- Meshes: /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Mesh/Pot_H_Piece_NN_Mesh_DS.obj (11 pcs 01–11)
- Axes: .../SfS_pp/Axes/Pot_H_Piece_NN_Axis.xyz (11/11 present)
- Sampled PCDs: sfs-potH-257/Dataset_Input/Point/Pot_H/ (11/11, 214-rule 36.24 pts/mm2,
  uniform-by-area sampling verbatim from pota214_sample_points.py incl. seed 214;
  agg md5 ad5f411d9864b307bfc105b343748eee)
- Author lanes: .../SfS_pp/Breaklines/Pot_H_Piece_NN_Breakline_[01].pcd (11 pieces x 2)

## Build gate (no rebuild: staged bm172 binaries reused read-only, else STOP)

- Spartan clone: /data/gpfs/projects/punim2657/sfs-potH-257 @ 0650111 (clean)
- Binary md5 check line (in-job gate, PASSED before running):
  mesh a51e7c1c385a2039c7932780a837c19f, edge dc472b0e87c934b6c487ff8637209864 —
  both == 250/251/252 rebuild record (staged path sfs-potD-252/build-252, read-only use).
- Source guards (in-job, PASSED): `bool paperChain = true` x2 in mesh source (default ON);
  no SFS_* env; edge source has no vote/KD code. Pipe logs confirm
  paper=PAPER-CHAIN (SPLITTER-234 theta=4/kappa=1/nb=10) on all 11 pieces.

## Jobs (all sacct COMPLETED 0:0)

- Sample 33691249 (potH257-sample, bm163): COMPLETED 0:0. 11/11 PCDs (172M total;
  e.g. P01 664998 pts from 18349.8 mm2; P11 99823 pts from 2754.5 mm2).
- Pipe 33691252 (potH257-pipe, bm172): COMPLETED 0:0. Mesh clusters
  18/13/16/16/8/10/5/7/8/11/7 (P01–P11). All 22 lanes extracted
  (header census 22/22, counts below). No MESH/EDGE exit lines; .err empty.
- Outputs: /data/gpfs/projects/punim2657/pota257_paper_Pot_H_{01..11}/ (per-piece trees,
  250/251 pattern). Mesh env 246-verbatim (PLANE_RULE=0, AXIS_FILE, RHOD=1.0/RHON=0.95/
  RHOC=0.1/RHOINN=0.75/RHOINC=0.25, SINGLE_SHOT=1); edge bare POT_NAME. No assembly.

## Scores vs author (fresh walk-order, mm; bar med<2 + cov>=90; rev = reverse coverage on matched slot)

| lane | nF/nO | lenF/lenO | med/cov | rev | jumps>10mm | slot | verdict |
|---|---|---|---|---|---|---|---|
| P01 Bl0 | 245/218 | 453.2/391.7 | 0.58/90.2 | 100.0 | 1 (jmax 15.8) | STRAIGHT | BAR-1J |
| P01 Bl1 | 242/235 | 434.4/419.6 | 0.62/64.0 | 66.8 | 0 | STRAIGHT | MISS |
| P02 Bl0 | 158/156 | 282.7/278.5 | 0.48/100.0 | 100.0 | 0 | STRAIGHT | BAR |
| P02 Bl1 | 147/137 | 269.1/245.2 | 0.89/70.1 | 74.5 | 0 | STRAIGHT | MISS |
| P03 Bl0 | 133/133 | 239.9/236.5 | 0.73/98.5 | 100.0 | 0 | STRAIGHT | BAR |
| P03 Bl1 | 122/99 | 218.3/176.4 | 0.73/54.9 | 67.7 | 0 | STRAIGHT | MISS |
| P04 Bl0 | 127/128 | 226.5/227.6 | 0.67/100.0 | 100.0 | 0 | STRAIGHT | BAR |
| P04 Bl1 | 118/116 | 210.7/206.3 | 0.68/100.0 | 100.0 | 0 | STRAIGHT | BAR |
| P05 Bl0 | 141/141 | 252.6/251.5 | 0.52/98.6 | 99.3 | 0 | STRAIGHT | BAR |
| P05 Bl1 | 145/140 | 267.9/252.8 | 0.47/97.2 | 100.0 | 1 (jmax 10.5) | STRAIGHT | BAR-1J |
| P06 Bl0 | 140/130 | 257.1/232.8 | 0.66/92.1 | 100.0 | 0 | STRAIGHT | BAR |
| P06 Bl1 | 144/133 | 265.6/237.0 | 0.46/93.8 | 100.0 | 0 (jmax 10.0) | STRAIGHT | BAR |
| P07 Bl0 | 122/118 | 226.4/211.4 | 0.52/97.5 | 100.0 | 1 (jmax 10.4) | STRAIGHT | BAR-1J |
| P07 Bl1 | 125/120 | 229.5/214.3 | 0.76/96.0 | 100.0 | 0 | STRAIGHT | BAR |
| P08 Bl0 | 102/99 | 182.4/176.2 | 0.82/99.0 | 100.0 | 0 | STRAIGHT | BAR |
| P08 Bl1 | 97/95 | 172.2/170.2 | 0.71/100.0 | 100.0 | 0 | STRAIGHT | BAR |
| P09 Bl0 | 95/95 | 169.5/168.3 | 0.57/100.0 | 100.0 | 0 | STRAIGHT | BAR |
| P09 Bl1 | 101/99 | 184.1/175.7 | 0.56/97.0 | 100.0 | 0 | STRAIGHT | BAR |
| P10 Bl0 | 104/101 | 190.5/181.3 | 0.51/100.0 | 100.0 | 0 | STRAIGHT | BAR |
| P10 Bl1 | 101/88 | 180.6/155.5 | 0.70/68.3 | 77.3 | 0 | STRAIGHT | MISS |
| P11 Bl0 | 74/73 | 130.8/131.0 | 0.59/100.0 | 100.0 | 0 | STRAIGHT | BAR |
| P11 Bl1 | 73/73 | 130.7/129.0 | 0.75/100.0 | 100.0 | 0 | STRAIGHT | BAR |

Tally (22 lanes): med<2mm on all 22; cov>=90 on 18/22; rev=100 (or >=99.3) on 18/22.
Clean BAR 15, BAR with one marginal jump 3 (P01Bl0 15.8, P05Bl1 10.5, P07Bl0 10.4),
MISS 4 (P01Bl1, P02Bl1, P03Bl1, P10Bl1 — all Bl1-side, rev 66.8–77.3).
Ranges match author within ~0.5mm on all BAR lanes (e.g. P04Bl0 zF=[390.0,437.5]
vs zO=[390.1,437.6], rF=[4.1,62.1] vs rO=[4.3,62.3]). Miss-lane excursions:
P01Bl1 r-min 14.8 vs 20.3; P02Bl1 z-max +4.5mm; P03Bl1 z-min -7.5mm / r-min 2.8 vs 7.4;
P10Bl1 z-min -8.1mm. Scorer: sfs-potH-257/score257.py (login node); full text:
artifacts/pota257/score257_out.txt (laptop copy) + sfs-potH-257/score257_out.txt.
Cross-lane slot: all 22 STRAIGHT (cross med >=3.83 vs matched <=0.89) — unlike Pot D's
stable SWAP convention, Pot H author lanes match the pipeline naming directly.

## Guards vs prior-pot pattern (drift or no-drift, stated)

- P15/P16-style cures: N/A — no cure history exists for Pot H; nothing to carry. Pot H pieces
  are smaller than Pot D (largest P01 18350 mm2 vs Pot D pieces up to ~2x) and 7 of 11
  pieces score BAR on both lanes out of the box.
- P03-style single-lane miss watch: HIT — 4 Bl1-side lanes miss (P01, P02, P03, P10) with
  rev<80 while their Bl0 sisters sit at BAR (rev 99.3–100). Same flavour as Pot D P03
  (one lane wanders, 17pct extra length, rev 55.4) and Pot C C01-tails/C03-runaway:
  the tracer leaves the rim on one side only. Worst here is milder than Pot C (no 1.8x
  tails, no 2.6x runaway; longest miss lane only 1.24x author length vs C03-Bl1 2.60x).
- No full-piece failure: every piece has at least one BAR lane (rev 100). No swap introduced
  by the paper arm (all slots STRAIGHT, same as the author naming).

## Overlays (author black #222222, fresh-paperON blue #0072B2; 3D + x-z side equal-aspect; titles carry n/med/cov/lengths)

- Laptop: C:/PR/SfSpp_preprocessing-257/artifacts/pota257/H01_Bl0_vs_author.png ...
  H11_Bl1_vs_author.png (22 files) + score257_out.txt, pipe257_33691252.out, sample257_33691249.out.
- Spartan masters: /data/gpfs/projects/punim2657/sfs-potH-257/overlays257/H01_Bl0_vs_author.png ... (22 files, overlay257.py).
- Eye-checked: H01Bl1 (blue tracks black arch then leaves on a big extra loop — matches
  cov 64.0/rev 66.8), H03Bl1 (blue takes a higher parallel branch then rejoins — matches
  cov 54.9), H10Bl1 (blue dips ~8mm below black at the bottom — matches z-min excursion),
  H04Bl0 (blue sits on black point-for-point — clean BAR). Views match the numbers; colours
  distinct (black vs blue) throughout.

## Verdict (staged, judgement stays with lead)

- Preprocessing: all 11 Pot H pieces both lanes extracted on the paper-ON-default binary;
  18/22 lanes AT BAR (med 0.46–0.89, cov 90.2–100, rev >=99.3 on BAR lanes), 4 Bl1-side
  single-lane misses (P01/P02/P03/P10-Bl1, rev 66.8–77.3) in the known Pot C/Pot D-P03
  tracer-leaves-rim flavour but milder (max 1.24x length vs C03-Bl1 2.60x).
- STAGED FOR LEAD: no fix proposed, nothing committed to main (only this ticket file edited
  in the main worktree; pipe/sample/score/overlay scripts live in sfs-potH-257 + laptop -257
  worktree, uncommitted). Weight: one pot (H, 11 pieces), one pipe run (33691252) +
  deterministic rescoring; single-object lead, not a conclusion. Open question for the lead:
  accept the 4 Bl1 misses as known single-lane misses (Pot C/D precedent) or dig into why
  Bl1-side only on this pot.
