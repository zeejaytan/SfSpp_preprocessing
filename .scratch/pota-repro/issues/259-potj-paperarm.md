# Ticket 259 — Pot J paper-arm-ON preprocessing + author score

Answers: E1
Status: results-in
Working in: C:/PR/SfSpp_preprocessing-259 (detached worktree @ 0650111, clean)

## Goal
First paper-arm look at Pot J: standard preprocessing pipe (surface split with paper arm ON by default, edge lanes legacy defaults) over all available Pot J pieces (01-12 with sampled PCDs; 13-19 have Mesh/BL/Axes but no sampled PCD and no POT block per 39, not run) with sampled ORIG inputs, and score every fresh lane against the author breaklines (median/2mm-coverage/jumps>10mm, lengths, reverse coverage), with overlay PNGs.

## Boundary (as run)
- Fresh laptop worktree of origin/main 0650111 (C:/PR/SfSpp_preprocessing-259, detached, clean) + fresh Spartan clone at 0650111 (/data/gpfs/projects/punim2657/sfs-potJ-259, clean tracked tree; fresh clone so no pull needed, HEAD verified == 0650111, no divergence).
- Live checkout /data/gpfs/projects/punim2657/sfs_preprocessing left untouched (f4add97, behind, per 246/249/250 precedent — NOT a divergence, left alone).
- Main worktree (user 204-edit still M, uncommitted) off limits except this ticket file.
- Preprocessing ONLY. Paper arm ON by default, NO SFS_PAPER_CHAIN override (in-job guard aborts if set). Edge lanes legacy defaults (vote OFF, KD-filter OFF — this binary carries neither).
- No assembly/reseat/repair, no commits to main.

## Inputs
- Meshes: /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Mesh/Pot_J_Piece_NN_Mesh_DS.obj (19 pcs 01-19 exist; ran 01-12 with PCDs)
- Axes: .../SfS_pp/Axes/Pot_J_Piece_NN_Axis.xyz (19/19 exist)
- Sampled PCDs: /data/gpfs/projects/punim2657/pota39_repro/prep/pota39_J_pt/Point_Pot_J/Pot_J_Piece_NN_Point.pcd (12/12: 01-12 only; 13-19 never sampled, outside upstream vehicle blocks per 39, not run)
- Author lanes: .../SfS_pp/Breaklines/Pot_J_Piece_NN_Breakline_[01].pcd (19/19 exist; scored 01-12)

## Build (gate: binary md5s must match rebuild record, else STOP)
- Spartan clone: /data/gpfs/projects/punim2657/sfs-potJ-259 @ 0650111, tracked tree clean
- Laptop worktree C:/PR/SfSpp_preprocessing-259 @ same hash, clean
- Binaries staged read-only from the 250 bm172 rebuild record into sfs-potJ-259/build-259/ (chmod a-w, no rebuild — no source change: 0650111..1a7c68d diff is ticket files only, mesh blob 823b3450 / edge blob 99a99c51 identical)
- mesh a51e7c1c385a2039c7932780a837c19f (record prefix a51e7c1c3 MATCHES)
- edge dc472b0e87c934b6c487ff8637209864 (record EXACT — same as 238/239/246/249/250/251/252)
- Build gate PASSED via in-pipe md5 gates. Splitter log confirms paper=PAPER-CHAIN and no SFS_* env (defaults rule: paper ON, vote OFF, KDF absent). Mesh sources md5 46fd2ad253fb3bf1468489daf534f9a6, edge 89ab05b178ed6484e60a8a3da587ca13 == 250 guards.

## Comments (worker, 2026-10-23 — preprocessing + score only, COMMIT NOTHING)

### Setup (boundary + gates)
- Laptop: fresh detached worktree C:/PR/SfSpp_preprocessing-259 @ 0650111 (== origin/main). Main worktree untouched except this ticket file (204-edit still M, uncommitted).
- Spartan: fresh clone /data/gpfs/projects/punim2657/sfs-potJ-259 @ 0650111 clean (origin GitHub HEAD == 0650111, no divergence). Live checkout untouched.
- Sources: mesh_processing_headless.cpp md5 46fd2ad253fb3bf1468489daf534f9a6, edgeline_extraction_headless.cpp md5 89ab05b178ed6484e60a8a3da587ca13 (== build250.sbatch guards).
- Binary md5 check line (250 rebuild record, gate passed BEFORE running — else STOP was armed): mesh a51e7c1c385a2039c7932780a837c19f, edge dc472b0e87c934b6c487ff8637209864. Both match staged bm172 binaries (chmod a-w read-only reuse).
- Mesh invocation carries NO SFS_PAPER_CHAIN env (default ON in effect); edge is legacy CTL (this binary carries no vote/KD-filter code). Pipe logs confirm paper=PAPER-CHAIN on all 12 pieces (SPLITTER-234 theta=4/kappa=1/nb=10).
- Inputs (PCDs pota39_J_pt 01-12 + ORIG Mesh_DS renamed + ORIG Axes). Outputs: /data/gpfs/projects/punim2657/pota259_paper_Pot_J_01..12 (new trees). No assembly/reseat/repair anywhere.

### Jobs (all sacct COMPLETED 0:0, all bm172)
- Pipe 33691262 (potJ259-pipe, run259_pipe.sbatch, bm172): COMPLETED 0:0, Elapsed 00:03:40. Mesh clusters 7/19/13/13/11/12/18/13/13/8/5/8 (P01-12). All 24 lanes present (24 .pcd lane files; 96 files with formats). No MESH/EDGE EXIT lines; .err empty.
- Scorer + overlays on login node (no Slurm; deterministic rescore of pipe output). No build job (reuse per boundary; md5-gated in-pipe).

### Scores vs author (fresh walk-order, mm; bar med<2 + cov>=90; cross-lane confirms slot)
- P01 Bl0: nF=249 nO=176 lenF=515.4 lenO=315.0=1.64x med=0.81 cov=70.3 jumps=1 (idx6, jmax70.8) rev=100.0 cross=5.74/0.0 STRAIGHT TAILS
- P01 Bl1: nF=255 nO=188 lenF=555.1 lenO=336.6=1.65x med=0.81 cov=73.3 jumps=1 (idx9, jmax99.7) rev=99.5 cross=5.71/0.0 STRAIGHT TAILS
- P02 Bl0: nF=147 nO=147 lenF=266.8 lenO=261.8 med=0.49 cov=100.0 jumps=0 rev=100.0 cross=5.38/0.0 STRAIGHT BAR
- P02 Bl1: nF=207 nO=197 lenF=384.4 lenO=353.3 med=0.74 cov=94.7 jumps=1 (idx9, jmax15.4) rev=100.0 cross=5.75/0.0 STRAIGHT BAR-1J
- P03 Bl0: nF=198 nO=189 lenF=360.5 lenO=339.6 med=0.55 cov=97.0 jumps=0 rev=100.0 cross=13.99/0.0 STRAIGHT BAR
- P03 Bl1: nF=129 nO=120 lenF=238.5 lenO=288.1 med=0.70 cov=98.4 jumps=0 rev=100.0 cross=10.41/0.0 STRAIGHT BAR
- P04 Bl0: nF=193 nO=186 lenF=351.1 lenO=332.4 med=0.45 cov=96.9 jumps=0 rev=100.0 cross=5.43/0.0 STRAIGHT BAR
- P04 Bl1: nF=212 nO=201 lenF=394.4 lenO=359.4 med=0.51 cov=94.8 jumps=1 (idx28, jmax16.4) rev=100.0 cross=5.42/0.0 STRAIGHT BAR-1J
- P05 Bl0: nF=149 nO=147 lenF=267.9 lenO=261.6 med=0.76 cov=99.3 jumps=0 rev=100.0 cross=5.24/0.0 STRAIGHT BAR
- P05 Bl1: nF=165 nO=159 lenF=303.7 lenO=283.4 med=0.54 cov=97.6 jumps=1 (idx10, jmax10.3) rev=100.0 cross=5.21/0.0 STRAIGHT BAR-1J
- P06 Bl0: nF=135 nO=133 lenF=241.3 lenO=237.1 med=0.43 cov=99.3 jumps=0 rev=98.5 cross=5.41/0.0 STRAIGHT BAR
- P06 Bl1: nF=155 nO=145 lenF=282.7 lenO=259.9 med=0.58 cov=95.5 jumps=0 rev=100.0 cross=5.35/0.0 STRAIGHT BAR
- P07 Bl0: nF=116 nO=114 lenF=211.9 lenO=203.2 med=0.48 cov=100.0 jumps=0 rev=99.1 cross=5.38/0.0 STRAIGHT BAR
- P07 Bl1: nF=131 nO=125 lenF=238.5 lenO=222.3 med=0.40 cov=100.0 jumps=0 rev=100.0 cross=5.27/0.0 STRAIGHT BAR
- P08 Bl0: nF=80 nO=71 lenF=150.8 lenO=127.2 med=0.64 cov=92.5 jumps=1 (idx9, jmax10.4) rev=98.6 cross=12.04/0.0 STRAIGHT BAR-1J
- P08 Bl1: nF=61 nO=60 lenF=106.9 lenO=105.4 med=0.59 cov=90.2 jumps=0 rev=86.7 cross=11.28/0.0 STRAIGHT BAR
- P09 Bl0: nF=95 nO=74 lenF=172.3 lenO=131.9=1.31x med=2.53 cov=32.6 jumps=0 rev=39.2 cross=3.66/23.2 STRAIGHT MISS
- P09 Bl1: nF=95 nO=69 lenF=181.8 lenO=123.5=1.47x med=2.41 cov=40.0 jumps=1 (idx10, jmax14.4) rev=52.2 cross=3.46/9.5 STRAIGHT MISS
- P10 Bl0: nF=73 nO=72 lenF=130.1 lenO=126.7 med=0.48 cov=100.0 jumps=0 rev=100.0 cross=4.94/0.0 STRAIGHT BAR
- P10 Bl1: nF=74 nO=75 lenF=132.6 lenO=132.1 med=0.60 cov=100.0 jumps=0 rev=100.0 cross=4.90/0.0 STRAIGHT BAR
- P11 Bl0: nF=56 nO=53 lenF=99.1 lenO=94.0 med=0.63 cov=100.0 jumps=0 rev=100.0 cross=5.15/0.0 STRAIGHT BAR
- P11 Bl1: nF=65 nO=58 lenF=117.6 lenO=102.4 med=0.54 cov=92.3 jumps=0 rev=98.3 cross=5.08/0.0 STRAIGHT BAR
- P12 Bl0: nF=58 nO=56 lenF=105.6 lenO=98.4 med=0.54 cov=100.0 jumps=0 rev=100.0 cross=5.23/0.0 STRAIGHT BAR
- P12 Bl1: nF=61 nO=59 lenF=108.3 lenO=104.4 med=0.51 cov=100.0 jumps=0 rev=100.0 cross=5.19/0.0 STRAIGHT BAR
- Ranges match author within ~0.5mm on all BAR lanes (e.g. P07-Bl1 zF=[439.2,480.0] zO=[438.4,479.9] rF=[0.5,62.5] rO=[0.6,62.8]). Excursions: P01-Bl1 r-max 94.9 vs 64.5 (+30mm tail over top edge); P09 z/r both ends (zF=[451.2,484.2] vs [454.4,481.6], r-min 11.0 vs 14.9). Scorer: sfs-potJ-259/score259.py; full text: score259_out.txt alongside.
- Tally (24 lanes): med<2 on 22/24 (P09 both fail); cov>=90 on 20/24 (P01 both + P09 both fail). Clean BAR 16, BAR-1J 4, TAILS 2 (P01), MISS 2 (P09). Reverse 100 except P01-Bl1 99.5, P06-Bl0 98.5, P07-Bl0 99.1, P08 98.6/86.7, P11-Bl1 98.3, P09 39.2/52.2.

### Guards vs prior-pot pattern (drift or no-drift stated; first paper-arm look at J so pattern guards, not same-pot numeric drift)
- Vs 249 Pot C diagnosis: P01 tails (1.64-1.65x, rev 100/99.5, single 70-100mm jump, cov 70-73) REPRODUCE the C01-tail failure mode (C01 1.76-1.80x, rev 100, idx126/idx9 ~100mm jumps) on the default-ON binary — same shape, same size class, both lanes. Tracer-tail watch carries over unchanged.
- Vs 249 C03-Bl1 runaway (2.60x, rev 40, med 12.2) + 252 P03 single-lane miss (Bl1-side wander, 47mm jump, rev 55.4): P09 both-lane miss is the Pot J instance — rev 39.2/52.2 (rim NOT fully captured), med 2.4-2.5, 1.3-1.5x lengths. Whole-piece miss (both lanes), not single-lane; cite as P03-style miss watch, one piece.
- Vs 252 P15/P16 cures (rescued under paper arm, hold at bar): small-piece lanes P06/P07/P10/P11/P12 all BAR (med 0.40-0.63, cov 92.3-100, rev 98.3-100) — no small-piece regression under default-ON. P08-Bl1 rev 86.7 noted but still at bar (med/cov pass).
- Slot naming: Pot J pipeline Bl0/Bl1 vs author Bl0/Bl1 AGREE on all 12 pieces (STRAIGHT, cross_med>=3.46 vs straight<=2.53 even on P09 miss) — no swap. Contrast Pot D 27/29 SWAPPED stable convention (214+252). Pot J naming is clean.
- Coverage: 12/12 available pieces run (01-12 sampled PCDs). 13-19 excluded: no sampled PCDs, no POT block per 39 (J13-19 outside upstream vehicle blocks, not piped) — same available-set logic as 252 (29/29 of available, author ships 32). NOT a single-lane miss; unrun for lack of inputs.

### Overlays (author black #222222, fresh-paperON blue #0072B2; 3D + X-Y/X-Z/Y-Z equal-aspect; titles carry n)
- Eye-checked: P01-Bl1 (blue tracks black ring then tail/chord over top edge, matches 99.7mm jump), P09-Bl0 (blue wanders off black ring both sides, matches med 2.53/rev 39.2 miss), P07-Bl1 (blue coincides with black all around, clean BAR).
- Laptop: C:/PR/SfSpp_preprocessing-259/artifacts/pota259/P01_Bl0_vs_author.png ... P12_Bl1_vs_author.png (24 files) + score259_used.py.
- Spartan masters: /data/gpfs/projects/punim2657/sfs-potJ-259/overlays259/P01_Bl0_vs_author.png ... (24 files, overlay259.py).

### Verdict (staged, judgement stays with lead)
- Preprocessing: all 12 available Pot J pieces both lanes extracted on the paper-ON-default binary (24/24 lanes present, clusters + counts logged). 20/24 lanes AT BAR (med 0.40-0.81, cov 90.2-100, rev 86.7-100); P01 tails (2 lanes, C01-style, rev ~100) + P09 whole-piece miss (2 lanes, rev 39/52).
- First paper-arm look at J: paper arm holds 10 of 12 pieces at bar, with one C01-style tail piece and one P03/C03-style miss piece. STAGED FOR LEAD: no fix proposed, nothing committed to main (only this ticket file edited in the main worktree; scorer/overlay/sbatch live in sfs-potJ-259 + laptop -259 worktree, uncommitted). Weight: one pot (J, 12 pieces), one pipe run (33691262) + deterministic rescoring; single-object lead, not a conclusion.

## Evidence
- Clone: /data/gpfs/projects/punim2657/sfs-potJ-259 (rev 0650111, clean)
- Build reuse: sfs-potJ-259/build-259/ (chmod a-w; md5s above); sources md5s above
- Pipe out: /data/gpfs/projects/punim2657/pota259_paper_Pot_J_01..12 ; log: sfs-potJ-259/pipe259_33691262.out (.err empty)
- Scores: sfs-potJ-259/score259.py, score259_out.txt (copy + lanes tarball unpacked at C:/PR/SfSpp_preprocessing-259/artifacts/pota259/)
- sacct: 33691262 COMPLETED 0:0 bm172 Elapsed 00:03:40
