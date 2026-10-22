# Ticket 254 — Pot E paper-arm-ON preprocessing + author score

Answers: E1
Status: results-in
Working in: C:/PR/SfSpp_preprocessing-254 (laptop detached worktree @ 0650111) + /data/gpfs/projects/punim2657/sfs-potE-254 (Spartan fresh clone @ 0650111)

## Goal
First paper-arm-ON look at Pot E: standard preprocessing pipe (surface split
with paper arm ON by default, edge lanes legacy defaults) over all Pot E pieces
with full inputs, and score every fresh lane against the author breaklines
(median/2mm-coverage/jumps>10mm, lengths, reverse coverage), with overlay PNGs.

## Boundary (per brief)
- Fresh laptop worktree of origin/main 0650111 + fresh Spartan clone at 0650111.
- Live checkout (/data/gpfs/projects/punim2657/sfs_preprocessing @ f4add97, behind)
  left untouched per 250-252 precedent — not a divergence, no pull attempted.
- Main worktree (user 204-edit still M) off limits except this ticket file.
- Preprocessing ONLY. Paper arm ON by default, no SFS_PAPER_CHAIN override.
  Edge lanes legacy defaults (vote OFF, KD-filter OFF — neither exists in edge
  source at 0650111). No assembly/reseat/repair, no commits to main.
- Scope: 31/31 pieces WITH full inputs (01-31). Pieces 32-34 have Mesh_DS, Axes
  and author lanes but NO sampled Point PCD anywhere on Spartan (checked
  pota39_E_pt, tree_E_BASE/CONE/PRE, full find) — same scope as the pota39 E2E
  (E 31/62). Runs 32-34 need fresh CC sampling first; lead decision.

## Constraints (per brief, as run)
- Reused staged bm172 binaries read-only (copied from sfs-potD-252/build-252,
  chmod a-w, no rebuild — sources identical: mesh 46fd2ad2, edge 89ab05b1).
  In-job md5 gate before running: mesh a51e7c1c385a2039c7932780a837c19f,
  edge dc472b0e87c934b6c487ff8637209864 — both MATCH, gate passed, else STOP armed.
- sacct COMPLETED 0:0 for every job. MSYS2_ARG_CONV_EXCL='*' on laptop ops.
- Pot images: author black #222222 vs fresh blue #0072B2 throughout (250-252 scheme).

## Comments (worker, 2026-10-23 — preprocessing + score only, COMMIT NOTHING)

### Setup
- Laptop: fresh detached worktree C:/PR/SfSpp_preprocessing-254 @ 0650111
  (== origin/main, verified; worktree clean). 0650111 vs 1a7c68d = ticket
  250/251/252 comments only (git diff stat: 3 files); mesh/edge .cpp byte-identical,
  so the 1a7c68d-built bm172 binaries remain the valid staged record.
- Spartan: fresh clone /data/gpfs/projects/punim2657/sfs-potE-254 @ 0650111,
  tracked tree clean; origin/main == 0650111 (no divergence to resolve).
- Inputs (read-only): PCDs pota39_E_pt/Point_Pot_E 31/31 (agg md5
  bb99b2bd85c050235cd663f8c3524b1c) + ORIG Mesh_DS (renamed _Mesh.obj) + ORIG Axes.
- Splitter log confirms paper=PAPER-CHAIN (SPLITTER-234 theta=4/kappa=1/nb=10)
  on all 31 pieces; SFS_* env unset in-job (defaults rule).

### Jobs (sacct COMPLETED 0:0)
- Pipe submit 33691261 (pota254-pipe, --nodelist=spartan-bm172): CANCELLED 0:0
  before start — bm172 reserved until 20:20 (ReqNodeNotAvail). No side effects
  (tree staging happens in-job). Recorded so the id is accounted for.
- Pipe 33691270 (pota254-pipe, same script minus the nodelist pin):
  COMPLETED 0:0 on bm174. Node deviation justified: 251 pipe ran on bm149;
  in-job md5 gate guarantees binary identity regardless of node. Binaries
  themselves stay bm172-built, reused read-only. Census 62/62 lane files, zero
  MISSING; .err empty. Log: sfs-potE-254/pota254_pipe_33691270.out.
- Score + overlays ran on the login node (light numpy/matplotlib work, per
  250 precedent). No sbatch needed.

### Scores vs author (matched lane shown; slot = which author lane the fresh file matches)
SWAP = pipeline Bl0/Bl1 vs author Bl0/Bl1 naming differs — stable convention
difference, same as Pot D (27/29 pieces there). Cross-lane med 5.0-14.2 vs
matched med 0.32-0.77 everywhere: slots unambiguous.

| piece | fresh | match | med | cov | jumps | jmax | lenF/lenO | revCov | verdict |
|---|---|---|---|---|---|---|---|---|---|
| P01 | Bl0 | SWAP | 0.58 | 98.3 | 1 (idx10) | 11.1 | 428.7/404.4 | 100.0 | BAR-1J |
| P01 | Bl1 | SWAP | 0.32 | 99.5 | 0 | 4.9 | 377.5/369.3 | 100.0 | BAR |
| P02 | Bl0 | SWAP | 0.45 | 98.1 | 0 | 6.3 | 375.3/356.5 | 100.0 | BAR |
| P02 | Bl1 | SWAP | 0.49 | 98.9 | 0 | 2.6 | 330.2/326.7 | 98.9 | BAR |
| P03 | Bl0 | SWAP | 0.73 | 98.4 | 0 | 8.1 | 342.9/330.3 | 100.0 | BAR |
| P03 | Bl1 | SWAP | 0.56 | 98.3 | 0 | 7.7 | 326.3/313.8 | 100.0 | BAR |
| P04 | Bl0 | SWAP | 0.49 | 98.4 | 0 | 7.0 | 347.2/329.7 | 100.0 | BAR |
| P04 | Bl1 | SWAP | 0.37 | 100.0 | 0 | 3.4 | 311.2/310.1 | 100.0 | BAR |
| P05 | Bl0 | SWAP | 0.49 | 98.9 | 0 | 8.4 | 321.6/307.0 | 100.0 | BAR |
| P05 | Bl1 | SWAP | 0.54 | 100.0 | 0 | 1.8 | 298.3/296.2 | 100.0 | BAR |
| P06 | Bl0 | SWAP | 0.69 | 98.4 | 0 | 7.0 | 341.8/327.8 | 100.0 | BAR |
| P06 | Bl1 | SWAP | 0.67 | 92.7 | 1 (idx8) | 12.3 | 354.3/316.7 | 100.0 | BAR-1J |
| P07 | Bl0 | SAME | 0.37 | 100.0 | 0 | 5.8 | 223.6/219.6 | 99.2 | BAR |
| P07 | Bl1 | SAME | 0.55 | 93.7 | 0 | 4.6 | 285.4/274.4 | 96.7 | BAR |
| P08 | Bl0 | SWAP | 0.69 | 96.7 | 1 (idx9) | 11.2 | 279.4/256.8 | 100.0 | BAR-1J |
| P08 | Bl1 | SWAP | 0.40 | 98.0 | 1 (idx46) | 10.3 | 274.9/256.1 | 100.0 | BAR-1J |
| P09 | Bl0 | SWAP | 0.74 | 97.0 | 0 | 5.8 | 301.0/282.3 | 100.0 | BAR |
| P09 | Bl1 | SWAP | 0.68 | 98.6 | 0 | 3.6 | 264.6/259.4 | 100.0 | BAR |
| P10 | Bl0 | SWAP | 0.70 | 98.8 | 0 | 5.0 | 293.0/275.1 | 100.0 | BAR |
| P10 | Bl1 | SWAP | 0.52 | 96.5 | 0 | 9.8 | 263.6/240.8 | 100.0 | BAR |
| P11 | Bl0 | SWAP | 0.68 | 97.8 | 1 (idx43) | 11.8 | 330.4/310.7 | 100.0 | BAR-1J |
| P11 | Bl1 | SWAP | 0.33 | 100.0 | 0 | 9.9 | 294.3/276.2 | 100.0 | BAR |
| P12 | Bl0 | SWAP | 0.60 | 98.1 | 1 (idx10) | 13.4 | 299.6/270.7 | 100.0 | BAR-1J |
| P12 | Bl1 | SWAP | 0.56 | 99.3 | 1 (idx12) | 14.4 | 277.2/252.9 | 100.0 | BAR-1J |
| P13 | Bl0 | SWAP | 0.50 | 94.8 | 1 (idx8) | 12.9 | 284.7/256.3 | 100.0 | BAR-1J |
| P13 | Bl1 | SWAP | 0.76 | 76.9 | 1 (idx4) | 23.0 | 307.4/248.5 | 86.3 | NEAR-MISS |
| P14 | Bl0 | SWAP | 0.42 | 97.2 | 0 | 9.0 | 262.8/246.5 | 100.0 | BAR |
| P14 | Bl1 | SWAP | 0.36 | 98.5 | 0 | 3.0 | 244.2/233.6 | 98.5 | BAR |
| P15 | Bl0 | SWAP | 0.57 | 98.1 | 0 | 4.5 | 193.5/186.5 | 100.0 | BAR |
| P15 | Bl1 | SWAP | 0.57 | 92.4 | 1 (idx9) | 13.6 | 199.0/181.4 | 94.1 | BAR-1J |
| P16 | Bl0 | SWAP | 0.56 | 96.2 | 0 | 8.5 | 287.5/262.3 | 98.6 | BAR |
| P16 | Bl1 | SWAP | 0.67 | 68.9 | 1 (idx18) | 10.1 | 226.1/199.1 | 75.0 | NEAR-MISS |
| P17 | Bl0 | SWAP | 0.70 | 98.5 | 0 | 5.5 | 235.9/227.3 | 100.0 | BAR |
| P17 | Bl1 | SWAP | 0.60 | 100.0 | 0 | 2.7 | 213.3/210.1 | 100.0 | BAR |
| P18 | Bl0 | SAME | 0.64 | 95.4 | 1 (idx9) | 19.4 | 291.2/243.9 | 100.0 | BAR-1J |
| P18 | Bl1 | SAME | 0.43 | 95.2 | 0 | 6.8 | 264.2/235.2 | 100.0 | BAR |
| P19 | Bl0 | SWAP | 0.62 | 100.0 | 0 | 3.4 | 304.0/304.1 | 100.0 | BAR |
| P19 | Bl1 | SWAP | 0.45 | 96.0 | 1 (idx22) | 12.9 | 320.7/288.7 | 100.0 | BAR-1J |
| P20 | Bl0 | SWAP | 0.68 | 100.0 | 0 | 8.5 | 195.7/182.9 | 100.0 | BAR |
| P20 | Bl1 | SWAP | 0.67 | 96.0 | 0 | 9.7 | 187.9/165.4 | 100.0 | BAR |
| P21 | Bl0 | SWAP | 0.49 | 99.0 | 0 | 6.3 | 191.7/183.0 | 100.0 | BAR |
| P21 | Bl1 | SWAP | 0.61 | 93.7 | 0 | 4.0 | 171.4/164.3 | 95.7 | BAR |
| P22 | Bl0 | SWAP | 0.46 | 100.0 | 0 | 8.5 | 204.7/189.6 | 100.0 | BAR |
| P22 | Bl1 | SWAP | 0.63 | 100.0 | 0 | 3.2 | 194.0/187.7 | 100.0 | BAR |
| P23 | Bl0 | SWAP | 0.54 | 99.1 | 0 | 5.7 | 201.9/193.0 | 100.0 | BAR |
| P23 | Bl1 | SWAP | 0.72 | 100.0 | 0 | 1.8 | 187.2/180.8 | 100.0 | BAR |
| P24 | Bl0 | SWAP | 0.60 | 99.1 | 0 | 8.5 | 204.7/191.2 | 100.0 | BAR |
| P24 | Bl1 | SWAP | 0.77 | 90.1 | 1 (idx8) | 18.2 | 214.4/177.7 | 100.0 | BAR-1J |
| P25 | Bl0 | SWAP | 0.55 | 91.9 | 1 (idx22) | 10.2 | 206.4/177.5 | 100.0 | BAR-1J |
| P25 | Bl1 | SWAP | 0.51 | 91.8 | 0 | 8.5 | 181.3/159.0 | 100.0 | BAR |
| P26 | Bl0 | SWAP | 0.61 | 97.9 | 0 | 4.3 | 173.5/168.6 | 100.0 | BAR |
| P26 | Bl1 | SWAP | 0.46 | 98.9 | 0 | 8.4 | 175.8/163.2 | 100.0 | BAR |
| P27 | Bl0 | SWAP | 0.47 | 100.0 | 0 | 1.8 | 154.5/151.4 | 100.0 | BAR |
| P27 | Bl1 | SWAP | 0.44 | 100.0 | 0 | 1.8 | 146.8/145.5 | 100.0 | BAR |
| P28 | Bl0 | SWAP | 0.58 | 95.1 | 0 | 8.8 | 151.0/137.8 | 100.0 | BAR |
| P28 | Bl1 | SWAP | 0.63 | 97.3 | 0 | 4.7 | 134.3/126.6 | 98.6 | BAR |
| P29 | Bl0 | SWAP | 0.66 | 97.4 | 0 | 3.7 | 140.5/127.8 | 100.0 | BAR |
| P29 | Bl1 | SWAP | 0.75 | 94.9 | 1 (idx1) | 11.2 | 149.8/118.4 | 100.0 | BAR-1J |
| P30 | Bl0 | SWAP | 0.47 | 100.0 | 0 | 1.8 | 141.3/137.0 | 100.0 | BAR |
| P30 | Bl1 | SWAP | 0.68 | 94.8 | 1 (idx22) | 11.7 | 146.7/128.3 | 100.0 | BAR-1J |
| P31 | Bl0 | SWAP | 0.57 | 100.0 | 0 | 2.3 | 126.5/125.3 | 100.0 | BAR |
| P31 | Bl1 | SWAP | 0.75 | 100.0 | 0 | 1.8 | 116.8/116.2 | 100.0 | BAR |

Tally (62 lanes): med<2mm on 62/62; cov>=90 on 60/62. Clean BAR 43,
BAR with one marginal jump 17, NEAR-MISS 2 (P13-Bl1 cov 76.9/rev 86.3,
P16-Bl1 cov 68.9/rev 75.0), full MISS 0. Reverse coverage 100 on 56/62
(98-99 on P02-Bl1, P07 x2, P14-Bl1, P28-Bl1; 90s on P15-Bl1, P16-Bl0, P21-Bl1).
Scorer: sfs-potE-254/score254.py (login node); full text: score254_table.csv.
Method note: first scorer version reported straight-lane numbers with a slot
flag (Pot D cross_med style); rewritten to matched-lane reporting like the 252
table before any read-out — caught because matched med/cov contradicted the
z/r ranges. Final CSV carries both matched and cross columns.

### Guards vs prior pots (drift or no-drift, stated)
- Vs Pot C tracer failures (249): ABSENT on Pot E. No C01-style tails
  (worst lenF/lenO 1.27 on P29-Bl1 with rev 100 — a local loop, not a tail;
  P24-Bl1 1.21 rev 100 likewise) and no C03-Bl1-style runaway (worst med 0.77,
  worst cov 68.9 with rev 75 — partial-lane, not whole-lane loss).
- Vs Pot D P03-style single-lane miss: WATCH CONFIRMED, same flavour.
  P16-Bl1 (cov 68.9/rev 75.0, other lane 0.56/96.2) and P13-Bl1
  (cov 76.9/rev 86.3, other lane 0.50/94.8) are one-lane-of-one-piece partial
  misses; the rest of each piece is clean. No whole-piece failure anywhere
  (every piece has both lanes med<1mm).
- Vs Pot D P15/P16 cures: no Pot E pre-cure baseline exists (first paper-arm
  look), but no lane shows the failure modes those cures fixed — nothing to
  re-cure. Slot naming: 29/31 pieces SWAPPED (both lanes agree), P07 + P18
  STRAIGHT — same stable convention difference as Pot D, not a fresh defect.

### Overlays (author black #222222 vs fresh-paperON blue #0072B2; 3D + X-Y/X-Z/Y-Z equal-aspect; titles carry n/med/cov/jumps/lengths/match)
- Eye-checked: P07-Bl0 (blue tracks black all around — matches 0.37/100.0),
  P13-Bl1 (blue cuts a chord + excursion where black bows out — matches
  76.9/86.3 + 23mm jump), P16-Bl1 (blue misses the lower loop black draws —
  matches 68.9/75.0). Views match the numbers; no runaways.
- Laptop: C:/PR/SfSpp_preprocessing-254/artifacts/pota254/overlays254/
  P01_Bl0..P31_Bl1_vs_author.png (62 files) + score254_table.csv +
  pota254_fresh_breaklines.tgz (fresh lanes) + pota254_lanes_overlays.tgz.
- Spartan masters: /data/gpfs/projects/punim2657/sfs-potE-254/overlays254/
  (62 files, overlay254.py) + pota254_pipe tree + score254_table.csv.

### Verdict (staged, judgement stays with lead)
- Preprocessing: all 31 Pot E pieces both lanes extracted on the paper-ON-default
  binary and score AT BAR on 60/62 lanes (med 0.32-0.77 throughout; 2 single-lane
  partial misses P13-Bl1/P16-Bl1 in the Pot D P03 flavour). No Pot C tracer
  failure anywhere. STAGED FOR LEAD: no fix proposed, nothing committed to main
  (only this ticket file new in the main worktree; scorer/overlay/sbatch live in
  sfs-potE-254 + laptop -254 worktree, uncommitted). Weight: one pot (31 pieces),
  one pipe run (33691270) + deterministic rescoring; single-object lead, not a
  conclusion.
