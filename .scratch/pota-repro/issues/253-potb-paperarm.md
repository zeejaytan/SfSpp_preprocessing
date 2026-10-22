# Ticket 253: paper-arm-ON (default) preprocessing of Pot B + author-score

**What to build:** first paper-arm look at Pot B — re-extract all 9 Pot B pieces both lanes with the paper-arm-ON default binary (no env override) and score vs author; follow the 250/251/252 recipe. Preprocessing ONLY: surface split -> edge lanes (legacy defaults: vote OFF, KD-filter OFF — this binary carries neither). No assembly/reseat/repair. No commits to main.

**Answers:** E1

**Blocked by:** 250 (Pot A paper-arm-ON 16/16 at bar), 251 (Pot C no-drift, 249 diagnosis stands), 252 (Pot D 51/58 at bar, P03 single-lane miss).

**Status:** results-in
**Working in:** C:/PR/SfSpp_preprocessing-253 (detached worktree @ 0650111, clean)

- [x] All 9 Pot B pieces (P01-P09) both lanes extracted with default-ON binary
- [x] Scored vs author (med/cov<2mm, jumps>10mm, lengths, reverse coverage)
- [x] Cross-lane slot check (all 9 STRAIGHT)
- [x] Overlay PNGs (author vs fresh, distinct colours), eye-checked
- [x] Guards vs prior-pot pattern cited (P15/P16-style cures, P03-style single-lane miss watch)

## Boundary (as run)

- Laptop: fresh detached worktree C:/PR/SfSpp_preprocessing-253 @ 0650111 (== origin/main). Main worktree untouched except this ticket file (204-edit still M, uncommitted).
- Spartan: fresh clone /data/gpfs/projects/punim2657/sfs-potB-253 @ 0650111, clean, HEAD verified in-job (WRONG-HEAD guard passed). Live checkout left untouched at f4add97 (behind origin/main, Juglet untracked leftovers — same as the 250 precedent: NOT pulled, not a divergence to resolve since nothing builds from it; no pull --ff-only was possible without touching it, so it was left alone and reported).
- Preprocessing ONLY. Surface split with paper arm default ON: SFS_PAPER_CHAIN deliberately UNSET (in-job guard aborts if set). Edge lanes legacy defaults: vote OFF, KD-filter OFF — verified this binary cannot carry them (0 VOTE_ORDER/SFS_VOTE/SFS_KD markers in 0650111 edgeline source; mesh blob 823b3450a7d6, edge blob 99a99c51cae2, identical to 1a7c68d). No assembly, no commits to main.

## Constraints (as run)

- MSYS2_ARG_CONV_EXCL='*' on laptop ops. sacct COMPLETED 0:0 for the pipe job on bm172.
- Binaries reused staged bm172 build read-only (cp -L from sfs-paper-250/build-250, chmod -w, no rebuild — sources identical 1a7c68d->0650111 except ticket files). Binary md5 check line (in-job gate BEFORE running — else STOP was armed): mesh a51e7c1c385a2039c7932780a837c19f, edge dc472b0e87c934b6c487ff8637209864. Both match the 250 rebuild record.
- Pot images: author black #222222, fresh-paperON blue #0072B2 throughout (250/251/252 scheme, kept for comparability).

## Comments (worker, 2026-10-23 — results-in, COMMIT NOTHING)

### Setup

- Inputs (read-only): sampled PCDs /data/gpfs/projects/punim2657/pota45_repro/pota45_B/Dataset/Point/Pot_B/ (9/9; md5-identical to the pota39_B_pt set used in tickets 39/41) + ORIG plain Mesh/Pot_B_Piece_0N_Mesh.obj (Pot B ships no _DS variant — staged directly, no rename) + ORIG Axes/Pot_B_Piece_0N_Axis.xyz. Env = 251 verbatim (PLANE_RULE=0, RHOD=1.0/RHON=0.95/RHOC=0.1/RHOINN=0.75/RHOINC=0.25, SINGLE_SHOT=1, AXIS_FILE).
- Mesh logs confirm paper=PAPER-CHAIN (SPLITTER-234 theta=4/kappa=1/nb=10) on all 9 pieces; mesh clusters 15/5/5/6/6/4/5/6/7. Outputs: /data/gpfs/projects/punim2657/pota253_paper_Pot_B_01..09 (new trees). Scripts: sfs-potB-253/run253_pipe.sbatch, score253.py, overlay253.py.

### Jobs (all sacct COMPLETED 0:0, all bm172)

- Pipe 33691246 (potB253-pipe, Pot B x9 mesh+edge): COMPLETED 0:0 bm172, Elapsed 00:02:24. All 18 lanes present (counts below). md5 + HEAD + no-override guards passed (see pipe253_33691246.out head). No MESH/EDGE exit lines.
- Score + overlays on the login node (no queue): score253_out.txt, overlays253/ (18 PNGs).

### Scores vs author (fresh walk-order, mm; bar med<2 + cov>=90; cross-lane confirms slot)

- P01 Bl0: nF=214 nO=210 lenF=390.8 lenO=375.6 med=0.45 cov=97.7 jumps=0 rev=100.0 cross=4.23/0.0 STRAIGHT
- P01 Bl1: nF=371 nO=218 lenF=736.8 lenO=390.1 =1.89x tail med=0.87 cov=58.8 jumps=1 (idx9, jmax72.6) rev=100.0 cross=5.18/0.0 STRAIGHT — MISS (C01-class tail)
- P02 Bl0: nF=154 nO=150 lenF=281.1 lenO=267.4 med=0.46 cov=97.4 jumps=0 rev=100.0 cross=2.97/40.3 STRAIGHT
- P02 Bl1: nF=158 nO=152 lenF=294.5 lenO=273.1 med=0.51 cov=99.4 jumps=1 (idx9, jmax13.7) rev=100.0 cross=2.98/38.0 STRAIGHT
- P03 Bl0: nF=146 nO=143 lenF=268.0 lenO=255.9 med=0.67 cov=99.3 jumps=0 rev=100.0 cross=3.32/39.0 STRAIGHT
- P03 Bl1: nF=157 nO=147 lenF=296.8 lenO=261.7 med=0.74 cov=94.3 jumps=1 (idx1, jmax17.8) rev=100.0 cross=3.49/36.3 STRAIGHT
- P04 Bl0: nF=139 nO=136 lenF=250.7 lenO=243.3 med=0.56 cov=99.3 jumps=0 rev=100.0 cross=3.30/33.8 STRAIGHT
- P04 Bl1: nF=145 nO=139 lenF=262.8 lenO=248.9 med=0.44 cov=97.9 jumps=0 rev=100.0 cross=3.31/34.5 STRAIGHT
- P05 Bl0: nF=139 nO=131 lenF=263.6 lenO=232.9 med=0.47 cov=93.5 jumps=1 (idx10, jmax17.0) rev=100.0 cross=3.11/31.7 STRAIGHT
- P05 Bl1: nF=133 nO=132 lenF=240.6 lenO=238.3 med=0.72 cov=99.2 jumps=0 rev=100.0 cross=3.10/34.6 STRAIGHT
- P06 Bl0: nF=104 nO=104 lenF=184.6 lenO=184.6 med=0.69 cov=100.0 jumps=0 rev=100.0 cross=3.35/32.7 STRAIGHT
- P06 Bl1: nF=113 nO=105 lenF=210.8 lenO=187.7 med=0.87 cov=94.7 jumps=1 (idx22, jmax11.0) rev=100.0 cross=3.30/31.0 STRAIGHT
- P07 Bl0: nF=108 nO=104 lenF=195.7 lenO=184.5 med=0.51 cov=97.2 jumps=0 rev=100.0 cross=3.33/38.0 STRAIGHT
- P07 Bl1: nF=110 nO=104 lenF=203.9 lenO=186.1 med=0.47 cov=100.0 jumps=0 rev=100.0 cross=3.29/35.5 STRAIGHT
- P08 Bl0: nF=105 nO=101 lenF=191.2 lenO=179.9 med=0.53 cov=98.1 jumps=0 rev=100.0 cross=2.97/29.5 STRAIGHT
- P08 Bl1: nF=104 nO=101 lenF=187.3 lenO=179.9 med=0.37 cov=100.0 jumps=0 rev=100.0 cross=2.94/30.8 STRAIGHT
- P09 Bl0: nF=76 nO=75 lenF=133.5 lenO=132.2 med=0.66 cov=100.0 jumps=0 rev=100.0 cross=3.57/0.0 STRAIGHT
- P09 Bl1: nF=81 nO=78 lenF=145.7 lenO=139.7 med=0.64 cov=98.8 jumps=0 rev=100.0 cross=3.72/0.0 STRAIGHT
- Tally (18 lanes): med<2mm on all 18; cov>=90 on 17/18. Clean BAR 13, BAR-1J 4 (P02-Bl1, P03-Bl1, P05-Bl0, P06-Bl1 — each exactly one 11-18mm jump), MISS 1 (P01-Bl1, cov 58.8, 1.89x tail). Reverse coverage 100%% on all 18 (no gaps — the rim is fully captured everywhere, the P01-Bl1 tail is extra).
- Ranges: z/r match author within ~1mm on all lanes (e.g. P01-Bl0 zF=[411.3,495.6] zO=[411.2,494.8] rF=[1.7,81.4] rO=[1.6,81.7]; P01-Bl1 tail dips r-min 2.0 vs 3.9). No excursions of the 249 class (C01 +11/+15mm z, r-min ~1mm; C03-Bl1 +45mm z, r-max 74mm). Full text: score253_out.txt (Spartan clone + laptop artifacts copy).
- Slot note: same-label med (0.37-0.87) beats cross-lane med (2.94-5.18) on every lane, so all 9 pieces are STRAIGHT — the ticket-41 Bl_0~=shipped-Bl_1 side-flip pattern does NOT reproduce under this chain; labels match author sides. (Cross_cov 30-40%% on P02-P08 reflects the two author sides running close together on Pot B, not ambiguity — straight cov is 93-100%% throughout.)

### Guards vs prior-pot pattern (drift or no-drift stated)

- Vs ticket 41 (old-chain Pot B diagnosis): CURED beyond recognition on 17/18 lanes. Then: fresh Bl_0 counts 1069/358/230/281/219/138/99/161/173 with mid-run teleports in 8/9 pieces (up to 90mm) + p1 garbage ~12mm off either side. Now: counts 214/154/146/139/139/104/108/105/76, 13/18 zero jumps, worst non-tail jump 17.8mm; p1 Bl_0 med 0.45 cov 97.7 (was garbage). The ordering-teleport failure mode is gone on the paper-arm default chain with NO SFS-T42-style fix applied (no shipped-axes pre-edge, no append skips) — the current main chain produces clean Pot B rims out of the box.
- P03-style single-lane miss watch (252: Pot D P03-Bl0 wanders, rev 55.4): WATCH TRIGGERED — P01-Bl1 is this pot's single-lane miss (1.89x tail, cov 58.8, one 72.6mm jump at idx9, rev 100.0). Same flavour as 249 C01 tails (1.76-1.80x, rev 100 — rim captured, tail extra), NOT the C03-Bl1 runaway class (2.60x, rev 40, med 12.21). One lane of one piece, same as Pot D.
- P15/P16-style cures (252: paper arm holds the 214 rescues): no Pot B equivalent exists (Pot B was never a cure pot), but the parallel result holds — the paper arm neither cures nor breaks anything here beyond the one tail; 8/9 pieces fully at bar on both lanes.
- Vs 250/251/252 (no-drift across the default flip): binary-identical pipe (same md5s, same bm172 node class, same env), so the Pot B result is directly comparable; no Pot A/C/D re-run per boundary.

### Overlays (author black #222222, fresh-paperON blue #0072B2; 3D + X-Y/X-Z/Y-Z equal-aspect; titles carry n)

- Eye-checked: P01-Bl1 (blue tracks black around the whole rim + one extra wandering loop, matches the 72.6mm tail jump) and P01-Bl0 (blue tracks black essentially perfectly, one tiny hook) — views match the numbers; no runaways.
- Laptop: C:/PR/SfSpp_preprocessing-253/artifacts/pota253/P01_Bl0_vs_author.png ... P09_Bl1_vs_author.png (18 files) + score253_out.txt + score253_used.py + pipe253_33691246.out.
- Spartan masters: /data/gpfs/projects/punim2657/sfs-potB-253/overlays253/P01_Bl0_vs_author.png ... (18 files, overlay253.py).

### Verdict (staged, judgement stays with lead)

- Preprocessing: all 9 Pot B pieces both lanes extracted on the paper-ON-default binary; 17/18 lanes AT BAR (med 0.37-0.87, cov 93.5-100, rev 100, ranges match). The ticket-41 teleport/garbage failure mode is gone with no special fix. One known single-lane miss (P01-Bl1 C01-class tail, rev 100) staged for the lead's call — accept as known miss or dig into why the tracer leaves the rim on that side.
- STAGED FOR LEAD: no fix proposed, nothing committed to main (only this ticket file created in the main worktree; pipe/score/overlay scripts + binaries live in sfs-potB-253 + laptop -253 worktree, uncommitted). Weight: one pot (B, 9 pieces), one pipe run (33691246) + deterministic rescoring; single-object lead, not a conclusion.
