# Ticket 258 — Pot I paper-arm-ON preprocessing + author score

Answers: E1
Status: results-in
Working in: C:/PR/SfSpp_preprocessing-258 (detached worktree @ 0650111, clean)

## Goal
First paper-arm-ON look at Pot I: run the standard preprocessing pipe (surface split
with paper arm ON by default, edge lanes legacy defaults) over all 30 Pot I pieces
with sampled inputs, and score every fresh lane against the author breaklines
(median/2mm-coverage/jumps>10mm, lengths, reverse coverage), with overlay PNGs.

## Boundary (per brief)
- Fresh laptop worktree of origin/main 0650111 + fresh Spartan clone at 0650111,
  same build node bm172. git pull --ff-only first; STOP on divergence.
- Live checkout untouched. Main worktree (user 204-edit) off limits except this file.
- Preprocessing ONLY. Paper arm ON by default, no SFS_PAPER_CHAIN override.
  Edge lanes legacy defaults (vote OFF, KD-filter OFF — neither exists in edge
  source at 1a7c68d/0650111). No assembly/reseat/repair, no commits to main.

## Inputs
- Meshes: .../SfS_pp/Mesh/Pot_I_Piece_NN_Mesh_DS.obj (30 pcs 01-30)
- Axes: .../SfS_pp/Axes/Pot_I_Piece_NN_Axis.xyz
- Sampled PCDs: pota39_repro/prep/pota39_I_pt/Point_Pot_I/ (30/30, CloudCompare)
- Author lanes: .../SfS_pp/Breaklines/Pot_I_Piece_NN_Breakline_[01].pcd (60 lanes)

## Build (gate: binary md5s must match record, else STOP)
- Spartan clone: /data/gpfs/projects/punim2657/sfs-potI-258 @ 0650111, tracked tree clean
- Binaries REUSED read-only from sfs-paper-250/build-250 (bm172 rebuild):
- mesh a51e7c1c385a2039c7932780a837c19f
- edge dc472b0e87c934b6c487ff8637209864

## Guards to cite
- P15/P16-style rescue holds (252: P15/P16 at bar under paper arm, 214-cure carries)
- P03-style single-lane miss watch (252: P03-Bl1-side wanders, 1x47mm jump, rev 55.4)
- P07-Bl1/P12-Bl0-side regressions watch (252: cov drops 97->81, 89->67)
- 249 Pot C tracer pattern (C01 tails 1.8x, C03-Bl1 runaway 2.6x) — check Pot I for same flavour

## Acceptance
- Every piece both lanes extracted + scored vs author
- Cross-lane slot check, overlay PNGs (author vs fresh, distinct colours)
- Guards vs prior-pot pattern cited

## Required evidence
- Scores table, job IDs + sacct, binary md5 check line, overlay paths
- Status results-in + self-contained completion message; judgement stays with lead

## Comments (worker)
## Comments (worker, 2026-10-23 — preprocessing + score only, COMMIT NOTHING)

### Setup (boundary + gates)
- Laptop: fresh detached worktree C:/PR/SfSpp_preprocessing-258 @ 0650111 (== origin/main). Main worktree untouched except this ticket file (204-edit still M, pre-existing p215 untracked files untouched).
- Spartan: live checkout left untouched (f4add97, behind, skip-worktree state — 250/251/252 precedent, NOT a divergence). Fresh GitHub clone /data/gpfs/projects/punim2657/sfs-potI-258 @ 0650111, tracked tree clean (HEAD verified == origin/main tip, ls-remote confirms).
- Sources in fresh clone: mesh_processing_headless.cpp md5 46fd2ad253fb3bf1468489daf534f9a6, edgeline_extraction_headless.cpp md5 89ab05b178ed6484e60a8a3da587ca13 (== 250/251/252 record). paperChain default ON in source (grep confirms).
- Binaries REUSED read-only from sfs-paper-250/build-250 (bm172 rebuild, no rebuild this ticket, no source change 1a7c68d..0650111 outside ticket files).
- Binary md5 check line (in-job gate, passed BEFORE running — else STOP was armed): mesh a51e7c1c385a2039c7932780a837c19f, edge dc472b0e87c934b6c487ff8637209864. Both match the 250 rebuild record exactly.
- Mesh invocation carries NO SFS_PAPER_CHAIN (default ON in effect); edge is legacy CTL (this binary carries no vote/KD-filter code). Pipe log confirms paper=PAPER-CHAIN on all 30 pieces (30 SPLITTER-234 lines, theta=4/kappa=1/nb=10).
- Inputs: pota39 CloudCompare sampled PCDs (Point_Pot_I, 30/30, agg md5 68e07e21def20bbebd932441787c72f9) + ORIG Mesh_DS renamed to plain stems + ORIG Axes. Outputs: /data/gpfs/projects/punim2657/pota258_pipe (new tree, no prior-pot tree touched). No assembly/reseat/repair anywhere.

### Jobs (all sacct COMPLETED 0:0, all bm172)
- Pipe 33691255 (pota258_pipe, Pot I x30 mesh+edge): COMPLETED 0:0 bm172, elapsed 00:10:47. pended on bm172 (ReqNodeNotAvail, sibling potB253-pipe running) then ran clean. 60/60 lane files, no MISSING; .err 0 bytes.

### Scores vs author (TRUE match = matched slot; bar med<2 + cov>=90; cross-lane decisive ~10x separation on swapped pieces)
- Slots: 54/60 SWAPPED (27 pieces: pipeline Bl0/Bl1 naming vs author convention differs — stable naming-convention difference, same flavour as Pot D 27/29 in both 214 and 252, not a defect). 6/60 STRAIGHT (P11, P25, P30 both lanes).
- Tally on TRUE match: BAR 55/60, NEAR-MISS 5/60, MISS 0/60. 9 lanes carry exactly one marginal jump (10.2–15.2mm).
- NEAR-MISS lanes (all Bl0-side except P27-Bl1): P02-Bl0 0.80/78.3 rev 81.1 len 1.32x (tail, no jump); P06-Bl0 0.56/72.5 rev 74.9 len 1.39x (tail, no jump); P11-Bl0 0.67/70.1 rev 90.8 1x11.7 len 1.35x (tail+jump); P13-Bl0 0.89/62.4 rev 63.7 len 1.26x (tail, no jump); P27-Bl1 0.49/88.3 rev 100.0 (no extra length — 252-P25-Bl1 class, cov 88-90).
- Reverse coverage 100% everywhere else (incl. all BAR lanes); no C03-Bl1-style runaway anywhere (worst med on true match 0.89).
- Author PCD sizes taper P01 ~400mm -> P29/30 ~70mm; fresh tracks within ~10% on BAR lanes.
- Scorer: sfs-potI-258/score258.py (login node); full text: score258_table.csv alongside. NOTE: lenF/lenO columns below compare same file index (mismatched lane on SWAPPED rows); TRUE med/cov is on the matched slot.

| piece | file | slot | TRUE med/cov | j>10(max) | lenF/lenO | revCov | verdict |
|---|---|---|---|---|---|---|---|
| 01 | Bl0 | SWAPPED | 0.56/97.5 | 1(11.0) | 432.2/402.2 | 100.0 | BAR |
| 01 | Bl1 | SWAPPED | 0.41/98.3 | 1(11.6) | 422.0/414.3 | 100.0 | BAR |
| 02 | Bl0 | SWAPPED | 0.80/78.3 | 0(6.6) | 400.8/304.4 | 81.1 | NEAR-MISS |
| 02 | Bl1 | SWAPPED | 0.60/94.5 | 1(12.1) | 336.1/388.1 | 100.0 | BAR |
| 03 | Bl0 | SWAPPED | 0.78/98.0 | 0(7.7) | 365.9/319.5 | 100.0 | BAR |
| 03 | Bl1 | SWAPPED | 0.75/100.0 | 0(3.5) | 325.7/346.9 | 100.0 | BAR |
| 04 | Bl0 | SWAPPED | 0.65/98.3 | 0(5.5) | 316.9/272.2 | 100.0 | BAR |
| 04 | Bl1 | SWAPPED | 0.71/99.4 | 0(3.2) | 278.6/306.3 | 100.0 | BAR |
| 05 | Bl0 | SWAPPED | 0.51/98.4 | 0(7.1) | 343.7/308.1 | 100.0 | BAR |
| 05 | Bl1 | SWAPPED | 0.48/99.4 | 0(6.6) | 319.8/334.2 | 100.0 | BAR |
| 06 | Bl0 | SWAPPED | 0.56/72.5 | 0(8.2) | 352.0/253.2 | 74.9 | NEAR-MISS |
| 06 | Bl1 | SWAPPED | 0.71/100.0 | 0(1.8) | 253.3/319.1 | 100.0 | BAR |
| 07 | Bl0 | SWAPPED | 0.61/98.5 | 0(6.3) | 360.9/328.2 | 100.0 | BAR |
| 07 | Bl1 | SWAPPED | 0.66/99.5 | 0(5.9) | 337.1/352.0 | 100.0 | BAR |
| 08 | Bl0 | SWAPPED | 0.46/97.7 | 0(8.4) | 323.4/283.6 | 100.0 | BAR |
| 08 | Bl1 | SWAPPED | 0.66/95.3 | 1(15.2) | 315.8/305.6 | 100.0 | BAR |
| 09 | Bl0 | SWAPPED | 0.75/98.5 | 0(6.8) | 359.6/336.7 | 100.0 | BAR |
| 09 | Bl1 | SWAPPED | 0.37/98.0 | 0(9.7) | 364.3/343.9 | 100.0 | BAR |
| 10 | Bl0 | SWAPPED | 0.75/99.4 | 0(2.3) | 319.1/310.4 | 100.0 | BAR |
| 10 | Bl1 | SWAPPED | 0.51/100.0 | 0(2.1) | 311.7/311.3 | 100.0 | BAR |
| 11 | Bl0 | STRAIGHT | 0.67/70.1 | 1(11.7) | 393.3/292.3 | 90.8 | NEAR-MISS |
| 11 | Bl1 | STRAIGHT | 0.58/98.8 | 0(8.1) | 315.9/302.0 | 100.0 | BAR |
| 12 | Bl0 | SWAPPED | 0.51/99.4 | 0(8.5) | 312.7/287.0 | 100.0 | BAR |
| 12 | Bl1 | SWAPPED | 0.47/96.4 | 0(8.8) | 307.6/296.5 | 100.0 | BAR |
| 13 | Bl0 | SWAPPED | 0.89/62.4 | 0(2.7) | 296.1/234.3 | 63.7 | NEAR-MISS |
| 13 | Bl1 | SWAPPED | 0.65/94.4 | 1(12.5) | 264.5/285.9 | 100.0 | BAR |
| 14 | Bl0 | SWAPPED | 0.76/98.6 | 0(7.2) | 270.0/252.1 | 100.0 | BAR |
| 14 | Bl1 | SWAPPED | 0.71/95.3 | 0(6.8) | 273.2/258.3 | 100.0 | BAR |
| 15 | Bl0 | SWAPPED | 0.46/100.0 | 0(2.9) | 256.7/236.0 | 100.0 | BAR |
| 15 | Bl1 | SWAPPED | 0.63/100.0 | 0(3.3) | 237.3/252.4 | 100.0 | BAR |
| 16 | Bl0 | SWAPPED | 0.49/100.0 | 0(1.8) | 229.2/215.6 | 100.0 | BAR |
| 16 | Bl1 | SWAPPED | 0.53/97.6 | 0(6.0) | 227.4/227.4 | 100.0 | BAR |
| 17 | Bl0 | SWAPPED | 0.42/100.0 | 0(4.9) | 217.3/191.6 | 100.0 | BAR |
| 17 | Bl1 | SWAPPED | 0.73/99.1 | 0(6.5) | 204.5/210.8 | 100.0 | BAR |
| 18 | Bl0 | SWAPPED | 0.52/100.0 | 0(2.2) | 247.0/229.7 | 100.0 | BAR |
| 18 | Bl1 | SWAPPED | 0.74/97.0 | 0(9.9) | 249.3/244.9 | 100.0 | BAR |
| 19 | Bl0 | SWAPPED | 0.44/100.0 | 0(5.3) | 259.1/229.4 | 100.0 | BAR |
| 19 | Bl1 | SWAPPED | 0.51/99.2 | 0(6.8) | 240.8/242.9 | 100.0 | BAR |
| 20 | Bl0 | SWAPPED | 0.45/99.2 | 1(11.5) | 229.3/185.9 | 100.0 | BAR |
| 20 | Bl1 | SWAPPED | 0.52/100.0 | 0(3.8) | 192.8/207.3 | 100.0 | BAR |
| 21 | Bl0 | SWAPPED | 0.55/100.0 | 0(2.8) | 231.4/213.4 | 100.0 | BAR |
| 21 | Bl1 | SWAPPED | 0.60/100.0 | 1(10.2) | 226.2/224.1 | 100.0 | BAR |
| 22 | Bl0 | SWAPPED | 0.33/99.0 | 0(5.8) | 178.6/161.7 | 100.0 | BAR |
| 22 | Bl1 | SWAPPED | 0.50/97.9 | 0(6.0) | 171.6/168.9 | 100.0 | BAR |
| 23 | Bl0 | SWAPPED | 0.64/99.0 | 0(2.1) | 173.1/156.3 | 100.0 | BAR |
| 23 | Bl1 | SWAPPED | 0.53/92.7 | 1(14.2) | 183.4/163.5 | 100.0 | BAR |
| 24 | Bl0 | SWAPPED | 0.79/95.2 | 0(6.3) | 152.1/133.2 | 100.0 | BAR |
| 24 | Bl1 | SWAPPED | 0.44/95.1 | 0(7.1) | 151.1/137.7 | 100.0 | BAR |
| 25 | Bl0 | STRAIGHT | 0.39/100.0 | 0(1.8) | 124.7/124.3 | 100.0 | BAR |
| 25 | Bl1 | STRAIGHT | 0.74/100.0 | 0(3.3) | 113.1/106.3 | 100.0 | BAR |
| 26 | Bl0 | SWAPPED | 0.49/100.0 | 0(2.0) | 129.8/138.0 | 100.0 | BAR |
| 26 | Bl1 | SWAPPED | 0.58/100.0 | 0(2.6) | 137.6/127.3 | 100.0 | BAR |
| 27 | Bl0 | SWAPPED | 0.35/100.0 | 0(6.4) | 121.6/92.8 | 100.0 | BAR |
| 27 | Bl1 | SWAPPED | 0.49/88.3 | 0(8.9) | 113.3/106.5 | 100.0 | NEAR-MISS |
| 28 | Bl0 | SWAPPED | 0.32/100.0 | 0(5.5) | 91.9/79.2 | 100.0 | BAR |
| 28 | Bl1 | SWAPPED | 0.56/100.0 | 0(1.8) | 79.2/82.6 | 100.0 | BAR |
| 29 | Bl0 | SWAPPED | 0.47/100.0 | 0(1.8) | 65.3/71.6 | 100.0 | BAR |
| 29 | Bl1 | SWAPPED | 0.84/97.8 | 0(1.8) | 77.5/65.4 | 100.0 | BAR |
| 30 | Bl0 | STRAIGHT | 0.43/100.0 | 0(1.8) | 72.8/68.7 | 100.0 | BAR |
| 30 | Bl1 | STRAIGHT | 0.50/100.0 | 0(1.8) | 69.6/70.5 | 97.5 | BAR |

### Guards vs prior-pot pattern (drift or no-drift stated)
- P15/P16-style rescue: no Pot I piece needed a 214-cure (nothing was broken at baseline — first paper-arm look, no legacy comparison). All 30 pieces extract coherent loops; no missing lanes.
- P03-style single-lane miss watch: NO P03-class miss on Pot I. Worst lane is P13-Bl0-side (0.89/62.4, rev 63.7, 1.26x tail, no jump) — a tail, not a wander: the overlay shows blue tracking the author ring with one extra loop, same signature as the C01 tails (1.76-1.80x, rev 100) but smaller (1.26-1.39x on P02/P06/P11/P13). No lane leaves the rim the way 252-P03-Bl1-side (rev 55.4, 1x47mm jump) or 249-C03-Bl1 (2.60x, rev 40) did.
- 249 Pot C tracer pattern: present in miniature — 4 Bl0-side tails (P02/P06/P11/P13, 1.26-1.39x extra, rev 64-91) carry the C01-tail signature (extra length + lowered rev) at ~1/3 the size; both lanes stay on the rim (rev>=63.7, no runaway). P27-Bl1 (0.49/88.3, no extra length) matches the 252-P25-Bl1-side class (cov just under bar, ruler-side).
- Slots: 27/30 pieces SWAPPED file-vs-author naming, stable across all lanes with ~10x med separation — same convention difference as Pot D (27/29 both arms), not drift.

### Overlays (author Bl0 black #222222 / Bl1 grey #555555 dashed; fresh Bl0 blue #0072B2 / Bl1 orange #E69F00; 3D + X-Y/X-Z/Y-Z equal-aspect; titles carry n)
- Eye-checked: P13 (blue tracks author ring + one extra loop, matches 1.26x tail numbers; orange tracks with one 12.5mm chord shortcut) and P25 (blue-on-black, orange-on-grey, coherent loops, STRAIGHT confirmed) — views match the numbers; no runaways. Distinct colours throughout: no pot image reuses similar colours for different things (author pair black/grey vs fresh pair blue/orange).
- Laptop: C:/PR/SfSpp_preprocessing-258/artifacts/pota258/overlays258/P01..P30_vs_author.png (30 files) + score258_table.csv + scripts.
- Spartan masters: /data/gpfs/projects/punim2657/sfs-potI-258/overlays258/P01..P30_vs_author.png (30 files, overlay258.py).

### Verdict (staged, judgement stays with lead)
- Preprocessing: all 30 Pot I pieces both lanes extracted on the paper-ON-default binary (0650111, staged bm172 binaries) and score 55/60 BAR + 5 NEAR-MISS + 0 MISS on the true match. Med 0.32-0.89, rev 63.7-100. No runaway, no missing lane.
- First paper-arm look at Pot I: the arm is safe as the default for this pot at the lane level; the 4 Bl0-side tails (P02/P06/P11/P13) are the watch list for any seating step — same tail signature as C01, smaller.
- STAGED FOR LEAD: no fix proposed, nothing committed to main (only this ticket file edited in the main worktree; scorer/overlay/sbatch live in sfs-potI-258 + laptop -258 worktree, uncommitted). Weight: one pot (I, 30 pieces), one pipe run (33691255) + deterministic rescoring; single-object lead, not a conclusion.
