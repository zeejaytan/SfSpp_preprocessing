# 250: Pot A paper-arm-ON preprocessing + author score

**What to build:** preprocessing ONLY on all 8 Pot A pieces with the paper arm default ON (1a7c68d, no env override) through legacy edge lanes, then score vs author. Measure what the paper arm changes against the 246 expectation (Pot A 8/8+15/15). No assembly/reseat/repair.

**Answers:** E1

**Blocked by:** 246 (Pot A 8/8+15/15 + Pot C 2/4+1/5 bar on restored-density main), 249 (Pot C tracer diagnosis + lane/pose guards).

**Status:** results-in
**Working in:** subagent session-61c820f6 (2026-10-22/23)

- [ ] All 8 Pot A pieces mesh (paper default ON, no env override) + edge (vote OFF, KD-filter OFF) lanes extracted
- [ ] Author score per lane (med/cov<2mm, jumps>10mm, lengths, reverse coverage) with guards vs 246/249 cited, drift or no-drift stated
- [ ] Overlay PNGs author vs fresh with distinct colours, eye-checked

## Comments (worker, 2026-10-23 — preprocessing + score only, COMMIT NOTHING)

### Setup (boundary + gates)
- Laptop: fresh detached worktree C:/PR/SfSpp_preprocessing-250 @ 1a7c68d (== origin/main). Main worktree untouched except this ticket file (204-edit still M, uncommitted).
- Spartan: live checkout /data/gpfs/projects/punim2657/sfs_preprocessing is BEHIND (f4add97 vs origin/main 1a7c68d) with skip-worktree/untracked state — left untouched per 246/249 precedent, NO pull (would need conflict resolution). Fresh clone /data/gpfs/projects/punim2657/sfs-paper-250 @ 1a7c68d clean (tracked tree; origin points at the live checkout path, HEAD verified == 1a7c68d so no divergence to resolve).
- Sources: mesh_processing_headless.cpp md5 46fd2ad253fb3bf1468489daf534f9a6, edgeline_extraction_headless.cpp md5 89ab05b178ed6484e60a8a3da587ca13 (== build250.sbatch guards).
- Binary md5 check line (rebuild record match, gate passed BEFORE running — else STOP was armed): mesh a51e7c1c385a2039c7932780a837c19f, edge dc472b0e87c934b6c487ff8637209864. Both == bin250_md5.txt (bm172 rebuild).
- Mesh invocation carries NO SFS_PAPER_CHAIN env (default ON in effect); edge is legacy CTL (this binary carries no vote/KD-filter code). Pipe logs confirm paper=PAPER-CHAIN on all 8 pieces (SPLITTER-234 theta=4/kappa=1/nb=10).
- Inputs (same as 246 Pot A): pota208 PCDs + ORIG plain Mesh.obj + ORIG Axes. Outputs: /data/gpfs/projects/punim2657/pota250_paper_Pot_A_01..08 (new trees, 246 trees untouched). No assembly/reseat/repair anywhere.

### Jobs (all sacct COMPLETED 0:0, all bm172)
- Build 33690135 (potD250-build, pre-staged by lead, worker-verified): COMPLETED 0:0 bm172. Guards OK + BUILD250 DONE.
- Verify 33690569 (potD250-verify md5 gate + default-ON/opt-out smoke): COMPLETED 0:0 bm172. md5sum -c OK; default run paper=PAPER-CHAIN, opt-out (SFS_PAPER_CHAIN=0) paper=off; VERIFY250 DONE.
- Pipe 33690610 (potA250-pipe, Pot A x8 mesh+edge, run250_pipe.sbatch): COMPLETED 0:0 bm172. Mesh clusters 11/4/5/5/5/6/7/5 == 246 (== 236). All 16 lanes present (counts below). No MESH/EDGE exit lines; .err empty.

### Scores vs author (fresh walk-order, mm; bar med<2 + cov>=90; cross-lane confirms slot)
- P01 Bl0: nF=210 nO=208 lenF=379.3 lenO=373.3 med=0.37 cov=99.0 jumps=0 rev=100.0 cross=5.07/0.0 STRAIGHT
- P01 Bl1: nF=223 nO=214 lenF=408.1 lenO=382.6 med=0.34 cov=97.3 jumps=1 (idx9, jmax10.3) rev=100.0 cross=5.03/0.0 STRAIGHT
- P02 Bl0: nF=170 nO=169 lenF=312.8 lenO=301.7 med=0.71 cov=98.2 jumps=1 (idx14, jmax10.4) rev=100.0 cross=3.46/0.0 STRAIGHT
- P02 Bl1: nF=179 nO=170 lenF=323.8 lenO=307.4 med=0.61 cov=99.4 jumps=0 rev=100.0 cross=3.47/0.0 STRAIGHT
- P03 Bl0: nF=161 nO=156 lenF=291.5 lenO=278.4 med=0.72 cov=100.0 jumps=0 rev=100.0 cross=3.51/0.0 STRAIGHT
- P03 Bl1: nF=164 nO=161 lenF=298.4 lenO=286.5 med=0.57 cov=98.2 jumps=0 rev=100.0 cross=3.48/0.0 STRAIGHT
- P04 Bl0: nF=157 nO=151 lenF=289.5 lenO=269.5 med=0.76 cov=99.4 jumps=1 (idx12, jmax10.5) rev=100.0 cross=3.55/0.0 STRAIGHT
- P04 Bl1: nF=156 nO=155 lenF=281.0 lenO=276.1 med=0.49 cov=99.4 jumps=0 rev=100.0 cross=3.58/0.0 STRAIGHT
- P05 Bl0: nF=153 nO=147 lenF=280.7 lenO=262.2 med=0.41 cov=97.4 jumps=0 rev=100.0 cross=3.65/0.0 STRAIGHT
- P05 Bl1: nF=157 nO=151 lenF=284.7 lenO=272.6 med=0.60 cov=97.5 jumps=0 rev=100.0 cross=3.63/0.0 STRAIGHT
- P06 Bl0: nF=163 nO=150 lenF=306.0 lenO=268.0 med=0.70 cov=95.1 jumps=1 (idx34, jmax16.2) rev=99.3 (author gap 132-132) cross=3.33/0.0 STRAIGHT
- P06 Bl1: nF=157 nO=152 lenF=285.1 lenO=271.9 med=0.71 cov=97.5 jumps=0 rev=100.0 cross=2.96/1.3 STRAIGHT
- P07 Bl0: nF=70 nO=65 lenF=128.4 lenO=115.9 med=0.68 cov=97.1 jumps=0 rev=100.0 cross=3.95/0.0 STRAIGHT
- P07 Bl1: nF=68 nO=67 lenF=119.0 lenO=117.9 med=0.56 cov=100.0 jumps=0 rev=100.0 cross=3.79/0.0 STRAIGHT
- P08 Bl0: nF=60 nO=60 lenF=105.0 lenO=106.0 med=0.64 cov=100.0 jumps=0 rev=100.0 cross=3.48/0.0 STRAIGHT
- P08 Bl1: nF=64 nO=63 lenF=113.6 lenO=111.5 med=0.39 cov=100.0 jumps=0 rev=100.0 cross=3.50/0.0 STRAIGHT
- Ranges: z/r match author within ~0.5mm on all lanes (e.g. P01-Bl0 zF=[363.6,419.1] zO=[363.6,419.2] rF=[19.2,83.5] rO=[19.3,83.8]); no excursions (contrast 249 C01 +11/+15mm z, r-min ~1mm; C03-Bl1 +45mm z, r-max 74mm). Scorer: sfs-paper-250/score250.py (login node); full text: score250_out.txt alongside.
- All 16 lanes AT BAR on the forward metric; 12/16 zero jumps, 4 lanes carry exactly one marginal jump (10.3–16.2mm). P06-Bl0's 16.2mm chord (idx34) costs one author point (rev 99.3%).

### Guards vs 246/249 (drift or no-drift stated)
- Vs 246 Pot A gate (gate246_table.txt, same bm172 paper-env path): NO DRIFT. Straight-lane deltas |dmed|<=0.04mm, |dcov|<=3.1pp (largest: P03-Bl0 cov 96.9->100.0 better; P01-Bl1 96.9->97.3; P04-Bl1 0.52->0.49; rest identical to the decimal). Lane counts match within 1pt (P02-F0 171->170, P03-F1 165->164, P06-F0 162->163). Slotmap: all 8 STRAIGHT (cross_med>=2.96 vs straight<=0.76), == slotmap246_A.txt.
- Vs 246 seats: no new assembly per boundary — seat guard carried (A_fresh 8/8+15/15, A_orig 8/8+15/15, job 33673764; strict A_fresh 7/8 P5 +1.9mm jitter, ORIG control 6/8 same run). This ticket changes no seat number; lane parity predicts no seat change, but the claim stays a prediction until the lead seats it.
- Vs 249 Pot C diagnosis: not re-run (Pot A only). Known failure modes (C01 ~1.8x tails, C03-Bl1 2.6x runaway, C02/C04/C03-Bl0 clean) unaffected by this ticket. Pot A guard (8/8+15/15 both arms same run) still carries the pipeline-sound half.
- Read for the lead: flipping the default OFF->ON reproduces the explicit-ON (SFS_PAPER_CHAIN=1) 246 lanes to the decimal — the default change itself moves nothing vs 246. What the paper arm changes vs the true legacy (paper=off) path is NOT measured here (no opt-out Pot A run per boundary); 250 proves default-ON == env-ON, not paper vs legacy.

### Overlays (author black #222222, fresh-paperON blue #0072B2; 3D + X-Y/X-Z/Y-Z equal-aspect; titles carry n)
- Eye-checked: P03-Bl1 (blue tracks black all around, one small hook) and P06-Bl0 (coherent loop + one chord shortcut at idx34, matches the 16.2mm jump) — views match the numbers; no runaways.
- Laptop: C:/PR/SfSpp_preprocessing-250/artifacts/pota250/P01_Bl0_vs_author.png ... P08_Bl1_vs_author.png (16 files) + score250_used.py.
- Spartan masters: /data/gpfs/projects/punim2657/sfs-paper-250/overlays250/P01_Bl0_vs_author.png ... (16 files, overlay250.py).

### Verdict (staged, judgement stays with lead)
- Preprocessing: all 8 Pot A pieces lanes extracted on the paper-ON-default binary and score AT BAR on all 16 lanes (med 0.34–0.76, cov 95.1–100, rev 99.3–100, ranges match). Paper-default reproduces 246 paper-env with NO DRIFT (mesh clusters + lanes identical).
- STAGED FOR LEAD: no fix proposed, nothing committed to main (only this ticket file edited in the main worktree; scorer/overlay/sbatch live in sfs-paper-250 + laptop -250 worktree, uncommitted). Weight: one pot (A, 8 pieces), one pipe run (33690610) + deterministic rescoring; single-object lead, not a conclusion.
