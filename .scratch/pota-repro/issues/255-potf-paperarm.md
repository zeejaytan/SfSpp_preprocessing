# 255: Pot F paper-arm-ON preprocessing + author score

**What to build:** preprocessing ONLY on all 7 Pot F pieces with the paper arm default ON (0650111, no env override) through legacy edge lanes, then score vs author. First paper-arm look at this pot; follow the 250/251/252 recipe. No assembly/reseat/repair.

**Answers:** E1

**Blocked by:** 252 (Pot D paper-arm-ON 51/58, P03 single-lane miss), 251 (Pot C no drift), 250 (Pot A all 16 lanes at bar).

**Status:** results-in
**Working in:** subagent of session-61c820f6 (2026-10-22/23)

- [x] All 7 Pot F pieces mesh (paper default ON, no env override) + edge (vote OFF, KD-filter OFF) lanes extracted
- [x] Author score per matched lane (med/cov<2mm, jumps>10mm, lengths, reverse coverage) + cross-lane slot check
- [x] Overlay PNGs author vs fresh with distinct colours, eye-checked
- [x] Guards vs prior-pot pattern cited (P15/P16-style cures, P03-style single-lane miss watch)

## Boundary (as run)

- Laptop: fresh detached worktree C:/PR/SfSpp_preprocessing-255 @ 0650111 (== origin/main, verified). Main worktree untouched except this ticket file (204-edit still M, uncommitted).
- Spartan: fresh clone /data/gpfs/projects/punim2657/sfs-potF-255 @ 0650111, clean detached HEAD (fetched from GitHub HTTPS; live checkout left untouched at f4add97 per 250/251 precedent - NOT a divergence). NOTE: plain 'git rev-parse <sha>' does NOT verify existence - use --verify or cat-file -t (lesson: first clone attempt checked out f4add97 because 0650111 objects were not in the live-checkout clone source).
- Binaries reused read-only from staged bm172 record (build-252, no rebuild, no source change): mesh a51e7c1c385a2039c7932780a837c19f, edge dc472b0e87c934b6c487ff8637209864. In-job md5 gates passed.
- Preprocessing ONLY. SFS_PAPER_CHAIN deliberately UNSET (in-job guard aborts if set); edge legacy (vote OFF, KD-filter OFF - this binary carries neither: 0 VOTE_ORDER/SFS_VOTE/SFS_KD markers at 0650111, same sources as 250/251/252).
- Inputs (read-only): sampled PCDs pota39_repro/prep/pota39_F_pt/Point_Pot_F (7/7, identical md5s to pota81 tree_F_BASE PCDs) + ORIG Mesh_DS renamed + ORIG Axes. Env otherwise = 252 verbatim. Outputs: /data/gpfs/projects/punim2657/pota255_pipe (new tree). No assembly, no commits to main.

## Jobs (bm172 throughout)

- 33691251 (potF255-pipe): FAILED 1:0 bm172 - worker sbatch bug (awk "{print $1}" under set -u: $1 unbound). md5/HEAD guards had already passed; no data staged. Lesson: cut -d" " -f1 instead of awk for md5/POINTS parsing under set -u.
- 33691339 (potF255-pipe resubmit): FAILED 1:0 bm172 - worker sbatch bug ('seq -w 1 7' yields 1..7 unpadded, guard correctly stopped on MISSING-PCD 1 before staging). Lesson: 252's 'seq -w 1 29' pads only because the range spans 2 digits; use explicit '01 02 ...' for small pots.
- 33691428 (potF255-pipe): COMPLETED 0:0 bm172. Mesh clusters + all 14 lane files present (counts below). paper=PAPER-CHAIN on all 7 pieces (7 log lines, SPLITTER-234 theta=4/kappa=1/nb=10). .err empty.
- sacct: 33691251 FAILED 1:0 bm172; 33691339 FAILED 1:0 bm172; 33691428 COMPLETED 0:0 bm172 (batch + extern).

## Scores vs author (matched lane shown; mm; bar med<2 + cov>=90; scorer slot-aware: nO/lenO/revCov/zO/rO already matched, med/cov = same-number file)

| piece | fresh | matches | med/cov | j>10(max) | lenF/lenO | revCov | verdict |
|---|---|---|---|---|---|---|---|
| P01 | Bl0 | auth Bl0 STRAIGHT | 0.56/99.3 | 0 (3.7) | 243.1/235.9 | 100.0 | BAR |
| P01 | Bl1 | auth Bl1 STRAIGHT | 0.83/89.9 | 0 (5.4) | 304.2/321.9 | 83.9 | NEAR-MISS |
| P02 | Bl0 | auth Bl1 SWAP | 0.44/99.3 | 0 (2.7) | 243.9/222.0 | 100.0 | BAR |
| P02 | Bl1 | auth Bl0 SWAP | 0.48/99.2 | 0 (9.0) | 239.4/237.9 | 100.0 | BAR |
| P03 | Bl0 | auth Bl1 SWAP | 0.63/85.2 | 0 (5.1) | 159.9/147.9 | 87.1 | NEAR-MISS |
| P03 | Bl1 | auth Bl0 SWAP | 0.61/100.0 | 0 (5.0) | 156.2/150.8 | 100.0 | BAR |
| P04 | Bl0 | auth Bl1 SWAP | 0.84/93.0 | 0 (9.4) | 133.6/104.7 | 100.0 | BAR |
| P04 | Bl1 | auth Bl0 SWAP | 0.37/95.5 | 0 (8.3) | 123.5/115.1 | 100.0 | BAR |
| P05 | Bl0 | auth Bl1 SWAP | 0.71/100.0 | 0 (1.8) | 114.4/101.5 | 100.0 | BAR |
| P05 | Bl1 | auth Bl0 SWAP | 0.70/95.2 | 0 (6.8) | 114.8/114.7 | 100.0 | BAR |
| P06 | Bl0 | auth Bl1 SWAP | 0.61/100.0 | 0 (4.0) | 110.2/87.6 | 100.0 | BAR |
| P06 | Bl1 | auth Bl0 SWAP | 0.74/100.0 | 0 (2.8) | 92.8/103.3 | 100.0 | BAR |
| P07 | Bl0 | auth Bl1 SWAP | 0.82/100.0 | 0 (2.2) | 65.2/48.5 | 100.0 | BAR |
| P07 | Bl1 | auth Bl0 SWAP | 0.75/100.0 | 0 (1.8) | 53.8/59.2 | 100.0 | BAR |

Tally (14 matched lanes): med<2mm on all 14; cov>=90 on 12/14; zero jumps>10mm on all 14 (max jmax 9.4); rev 83.9-100. 12 BAR + 2 NEAR-MISS (P01-Bl1 cov 89.9/rev 83.9, P03-Bl0-side cov 85.2/rev 87.1), 0 MISS.
Cross-lane slot check: P01 STRAIGHT both lanes (straight 0.56/0.83 vs cross 5.35/5.52); P02-P07 SWAPPED both lanes (same-number med ~4-5.2/cov 0-14 vs cross 0.37-0.84/cov 85-100) - stable pipeline-vs-author naming difference, same class as Pot D (27/29 swapped in both 214 and 252), not a fresh defect.
Ranges: matched z/r agree within ~1mm on all lanes (largest: P03-Bl0-side r-min +2.4mm). No excursions (contrast 249 C01 +11/+15mm z, C03-Bl1 +45mm z).
Lengths: longer-fresh lanes (P04-Bl0-side 1.28x, P06-Bl0-side 1.26x, P07-Bl0-side 1.34x) carry cov 100 + rev 100 - denser sampling along the same rim, not tails (tails would break rev or throw jumps; none >10mm).
Scorer: sfs-potF-255/score255.py; full slot-aware table: score255_table.csv alongside.

## Guards vs prior-pot pattern (drift or no-drift stated)

- P15/P16-style cures: N/A - Pot F has no known cure pieces; nothing needed rescue, all lanes at/near bar without repair.
- P03-style single-lane miss watch (252-P03: cov 50.3 + 47mm jump + 17pct extra length): NO MISS on Pot F. Worst lanes are P01-Bl1 (cov 89.9, marginal, localized deviation eye-checked) and P03-Bl0-side (cov 85.2, one shortcut sector eye-checked) - both track the rim with zero jumps, neither wanders off-rim.
- P07-Bl1-side/P12-Bl0-side-style coverage regressions: only the two near-misses above; no lane below 85.
- No C01-tails (length ratios <=1.34 with cov 100 on the long lanes) and no C03-runaway (no z/r excursions, max jmax 9.4mm).

## Overlays (author black #222222, fresh blue #0072B2; 3D + X-Y/X-Z/Y-Z equal-aspect; slot-aware: fresh-Bl vs MATCHED author-Bl, titles carry n + slot)

- Eye-checked: P02-Bl0-vs-Bl1 (blue rides black essentially perfectly, med 0.44) and P03-Bl0-vs-Bl1 (blue tracks black all round; one shortcut sector top-left where black dips, accounts for cov 85.2 - closed loop, no runaway) and P01-Bl1 (blue tracks black; one small hook where black notches + one minor spike, accounts for cov 89.9).
- Lesson: first overlay render compared same-number lanes and made swapped pieces look diverged - re-rendered slot-aware; swapped-pair overlays confirm the numbers.
- Laptop: C:/PR/SfSpp_preprocessing-255/artifacts/pota255/P01..P07 overlays (14 files, matched names P<nn>_Bl<b>_vs_author-Bl<m>.png) + score255_table.csv.
- Spartan masters: /data/gpfs/projects/punim2657/sfs-potF-255/overlays255/ (14 files, overlay255.py).

## Verdict (staged, judgement stays with lead)

- Preprocessing: all 7 Pot F pieces both lanes extracted on the paper-ON-default binary; 12/14 matched lanes AT BAR, 2 NEAR-MISS, 0 MISS, zero jumps>10mm, ranges match. First paper-arm evidence for Pot F: the arm is safe on this pot - no repair proposed.
- STAGED FOR LEAD: nothing committed to main (only this ticket file new in the main worktree; scorer/overlay/sbatch/pipe outputs live in sfs-potF-255 + laptop -255 worktree, uncommitted). Weight: one pot (F, 7 pieces), one pipe run (33691428) + deterministic rescoring; single-object lead, not a conclusion.
