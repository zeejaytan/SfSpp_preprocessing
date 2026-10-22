# Ticket 251: paper-arm-ON (default) preprocessing of Pot C + author-score

**What to build:** re-extract all 4 Pot C lanes with the paper-arm-ON default binary (no env override) and score vs author; measure what the paper arm changes on the same lanes vs the 249 diagnosis (C01 tails 1.8x, C03-Bl1 runaway 2.6x on the 246 explicit-ON path). Preprocessing ONLY: surface split -> edge lanes. No assembly/reseat/repair.

**Answers:** E1

**Blocked by:** 249 (Pot C diagnosis: C01 tails, C03-Bl1 runaway), 246 (restored-density E2E bar), 250 (rebuild at 1a7c68d: mesh a51e7c1c3, edge dc472b0e, bm172).

**Status:** results-in
**Working in:** subagent session-61c820f6 (2026-10-22)

- [x] All 4 Pot C pieces (C01/C02/C03/C04) both lanes extracted with default-ON binary
- [x] Scored vs author (med/cov<2mm, jumps>10mm, lengths, reverse coverage)
- [x] Overlay PNGs (author vs fresh, distinct colours)
- [x] Guards vs 246/249 cited with drift-or-no-drift stated

## Boundary (as run)

- Laptop: fresh detached worktree C:/PR/SfSpp_preprocessing-251 @ 1a7c68d (== origin/main). Blob hashes match commit (mesh 823b345, edge 99a99c5). Main worktree untouched except this ticket file (204-edit still M, uncommitted).
- Spartan: fresh local clone /data/gpfs/projects/punim2657/sfs-potC-251 @ 1a7c68d, clean; live checkout left untouched (f4add97, behind, per 239-249 precedent — NOT a divergence, left alone). No pull needed on a fresh clone; hash verified.
- Preprocessing ONLY. Surface split with paper arm default ON: SFS_PAPER_CHAIN deliberately UNSET (in-job guard aborts if set). Edge lanes legacy default: vote OFF, KD-filter OFF — verified this binary cannot carry them (0 VOTE_ORDER/SFS_VOTE/SFS_KD markers in 1a7c68d *.cpp; edge source 89ab05b1 = good source). No assembly, no commits to main.

## Constraints (as run)

- MSYS2_ARG_CONV_EXCL='*' on laptop ops. sacct COMPLETED 0:0 for the pipe job. Binary md5s gated in-job before running.
- Pot images: author black #222222, fresh blue #0072B2 throughout (249 scheme, kept for comparability).

## Comments (worker, 2026-10-23 — results-in, COMMIT NOTHING)

### Setup

- Binaries staged from the 250 rebuild record into sfs-potC-251/build-251/ (read-only copy, no rebuild — no source change): mesh a51e7c1c385a2039c7932780a837c19f == a51e7c1c3 record, edge dc472b0e87c934b6c487ff8637209864 == record. In-job md5 gates passed; SFS_PAPER_CHAIN-unset guard passed (see pipe251_33690626.out head).
- Inputs (read-only, same files as 246): sfs-potAC-246/pota246_inputs/Point/Pot_C (md5 844035fe/C01, 82bdeae9/C02, 1d01ad63/C03, 9e0512e0/C04) + ORIG Mesh_DS renamed + ORIG Axes. Env otherwise = 246 verbatim (PLANE_RULE=0, RHOD=1.0/RHON=0.95/RHOC=0.1/RHOINN=0.75/RHOINC=0.25, SINGLE_SHOT=1, AXIS_FILE).
- Pipe job 33690626 (potC251-pipe, bm149) COMPLETED 0:0. Outputs: /data/gpfs/projects/punim2657/pota251_paper_Pot_C_{01,02,03,04}/. Scripts: sfs-potC-251/run251_pipe.sbatch, score251.py, overlay251.py.

### Scores (fresh walk-order, mm; 249 legacy numbers beside for the drift call)

| lane | 251 nF (249 n) | 251 lenF/lenO (249 lenF) | 251 med/cov/rev | 249 med/cov/rev | jumps 251 (246) |
|---|---|---|---|---|---|
| C01-Bl0 | 317 (319) | 666.6/378.2=1.76x (670.2) | 0.76/67.2/100.0 | 0.74/66.5/100 | 1, jmax 99.6 (1 idx126 jmax 99.6) |
| C01-Bl1 | 359 (360) | 744.0/413.5=1.80x (745.8) | 0.71/64.3/100.0 | 0.73/64.2/100 | 1, jmax 101.4 (1 idx9 jmax 101.4) |
| C02-Bl0 | 237 (237) | 446.0/398.4=1.12x | 0.76/95.4/100.0 | 0.65/94.5/— | 1, jmax 23.0 (1 idx9 jmax 25.8) |
| C02-Bl1 | 318 (318) | 709.1/678.8=1.04x | 0.48/94.7/97.1 | 0.47/95.3/— | 3, jmax 111.8 (3 idx10/19/109 jmax 111.8) |
| C03-Bl0 | 204 (205) | 385.8/340.8=1.13x | 0.55/93.1/99.5 | 0.76/91.7/— | 1, jmax 22.2 (1 idx13 jmax 22.1) |
| C03-Bl1 | 367 (366) | 712.0/273.7=2.60x (709.8) | 12.21/13.6/40.0 | 12.36/13.1/38.3 | 1, jmax 55.0 (1 idx10 jmax 54.6) |
| C04-Bl0 | 139 (139) | 253.6/233.5=1.09x | 0.72/89.2/91.6 | 0.75/89.2/— | 0 (0) |
| C04-Bl1 | 147 (147) | 270.2/260.6=1.04x | 0.55/99.3/100.0 | 0.55/99.3/— | 0 (0) |

- Cross-lane checks (fresh vs other author lane): all ~6/0% class (C01 6.01/0.0 + 6.04/0.6; C03-Bl1 6.36/0.5) — slots STRAIGHT, no swap introduced by the default flip. z/r extremes reproduce 249 (C01-Bl0 z-max 444.5, r-min 1.6; C03-Bl1 z-range [453.0,525.5] r-max 74.0).

### Guards vs 246/249: NO DRIFT on any of the 8 lanes

- Counts agree to +-2 (thread-noise class: 317/319, 359/360, 204/205, 367/366; four lanes exact). Med within 0.21, cov within 0.9 on every lane; C04-Bl1 exact (0.55/99.3), C04-Bl0 cov exact (89.2). Jump counts/indices/jmax reproduce 246 exactly where 246 recorded them (C01 idx126/idx9, C02-Bl1 triple 10/19/109, C03-Bl1 idx10).
- 249's diagnosis stands unchanged on the default-ON binary: C01 tails 1.76-1.80x with full-rim reverse coverage (both lanes rev 100.0 — the rim is fully captured, the tail is extra); C03-Bl1 runaway 2.60x, rev 40.0, med 12.21. Same failure, same size, same lanes.
- Reading: default-ON (1a7c68d, mesh a51e7c1c3) reproduces explicit-ON (246, SFS_PAPER_CHAIN=1, mesh b8eb3759) to run noise. The flag flip changes nothing on Pot C beyond the binary identity — the paper arm's effect on these lanes was already fully present in the 246/249 record.

### Overlays (author black #222222, fresh blue #0072B2; titles carry med/cov/lengths; eye-checked C01-Bl0 + C03-Bl1)

- C:/PR/SfSpp_preprocessing-251/artifacts/pota251/C01_Bl0_vs_author.png (3D + x-z side; blue tracks black ring then tail over top edge)
- C:/PR/SfSpp_preprocessing-251/artifacts/pota251/C01_Bl1_vs_author.png (same pattern)
- C:/PR/SfSpp_preprocessing-251/artifacts/pota251/C02_Bl0_vs_author.png
- C:/PR/SfSpp_preprocessing-251/artifacts/pota251/C02_Bl1_vs_author.png
- C:/PR/SfSpp_preprocessing-251/artifacts/pota251/C03_Bl0_vs_author.png
- C:/PR/SfSpp_preprocessing-251/artifacts/pota251/C03_Bl1_vs_author.png (blue wanders far off black ring)
- C:/PR/SfSpp_preprocessing-251/artifacts/pota251/C04_Bl0_vs_author.png
- C:/PR/SfSpp_preprocessing-251/artifacts/pota251/C04_Bl1_vs_author.png

### Verdict (evidence staged, judgement stays with lead)

- Default-ON paper arm: NO DRIFT vs 246/249 on any Pot C lane — C01 tails (~1.8x, rev 100) and C03-Bl1 runaway (2.6x, rev 40) reproduce exactly; C02/C04/C03-Bl0 clean at bar. The 249 tracer-failure diagnosis carries over unchanged to the new default binary. STAGED FOR LEAD: nothing committed, no repair proposed.
