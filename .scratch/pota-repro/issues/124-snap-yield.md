# Snap yield — place the dots the test found but the snap dropped

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 123 (r1 finds 93 candidates, SURF-C1 keeps 2, 1 admitted; ~17 on-arc dots fail caps narrowly: disp 2.06-3.76 / dmid 5-6.3; next = snap placement or disp-cap calibration) + 122c (normal-gating note) + 104 (K=1 snap flaw) + 103 (cleaned bag, gate 4.68)

**Status:** results-in

**What to deliver:** turn 123's single-dot gain into yield. The r1 re-run FINDS on-arc dots that SURF-C1's caps then drop for centimetres of snap drift. Test improved snap placement: candidates (state which before running, one variable) — (i) K>1 vote (snap to medoid/mean of K nearest surface verts instead of K=1), (ii) normal-gated snap (candidate verts whose normals disagree with the coarse dot's normal refused), (iii) calibrated disp-cap (raise 2.0mm only as far as the on-arc/junk separation allows, measured first). Bar (all must hold): admitted dots more than 123's 1 AND admitted junk ~0 (majority within 5mm of ORIG) AND gate at/below 4.60mm (123's mark to beat, else 4.68 hard floor) AND walk >=198 pushes. If better placement only moves drift centimetres (admission stays ~1), refute with the drift-vs-K numbers — that says the coarse dots themselves sit off-surface and the fix belongs at detection, not placement.

**Starting position:** .scratch/pota123_repro/ (ladder, 93 r1 candidates, SURF-C1 code, admitted dot, control numbers), C01 fragment mesh + normals. Login-node numpy only — no Slurm, no E2E. New scratch pota124_repro/; render under laptop artifacts/pota124/ (snap drift before/after per candidate, admitted dots on ORIG arc, walk vs 123-grown).

**Rules:** control reproduces 123-grown bag first (271, gate 4.60, walk 198) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; placement-variable-stated-first.

- [ ] 123-grown reproduced + candidate stated
- [ ] Placement arm (drift numbers, admission accounting, junk count)
- [ ] Walk + gate vs 123's marks
- [ ] Verdict + recipe or detection-side refutation

## Comments (worker, 2026-10-19 — laptop numpy only; COMMIT NOTHING; lead owns checkboxes)

**Verdict: recipe CONFIRMED — bar 4/4 with margin. Calibrated disp-cap 2.0 -> 2.5mm turns 123's single-dot gain into 8 admitted dots, 0 junk, gate 4.60 -> 4.31, walk 198 -> 205, uncovered 30 -> 16.**

**0. Method + control GREEN (reproduce-or-stop PASSED).** Rebuilt 123-grown verbatim in pota124_repro (p124_control.py, OUT repointed): bag 270+1=271, greedy 93/271, final 198, 4 jumps at (92,93)/(126,127)/(165,166)/(184,185), gate med 4.60 / <2mm 30.3% / gaps5 40 / maxstep 67.0 / ORIGcov 84/211 / uncovered 30 — multiset-equals 123's marks. ORIG = Bl_0 gate-evidence only; zero ORIG points copied. Inputs read-only: Pot_C S0 cloud + normals (pota123_repro mirror), U verts + normals (pota120_repro/unclustered.ply, 2342 verts), C bag (p113_guarded.npz), OG (p119_OG.npy), ROW40 (p104_walk.npz bagP minus C). No Slurm, no E2E; tickets 39-123 read-only; COMMIT NOTHING.

**1. Candidate stated BEFORE running (p124_candidate.txt, one variable): (iii) calibrated disp-cap.** Only the K=1 snap displacement cap moves; dmid<=5.0mm to licensing blind mid, dedupe>=1.0mm, ROW40-coord exclusion, span-localized r1/r2 seeds (never filter rejects), K=1 nearest-U snap semantic — all frozen at SURF-C1. Caps probed 2.5/3.0/3.5/4.0 (measurement first); landed = smallest cap clearing the bar. Diagnostics (not placement): D1 drift-vs-K, D2 normal agreement.

**2. Placement numbers (p124_measure.txt).** r1 93 cand: on-arc 48 (ORIG<=5mm) vs junk 45; K=1 disp on-arc med 2.27 (p25 1.72 / p90 3.32 / max 7.64) vs junk med 0.00 — junk dies on the FIXED dmid cap, not disp, so the separation is clean: pass (disp<=cap & dmid<=5) at 2.0/2.5/3.0/3.5/4.0 = 2/15/16/18/19 survivors with junk 0 at EVERY step. r2 203 cand: 0/4/4/5/5 survivors, junk 0 throughout (r2 on-arc disp med 3.07 — finer scale sits farther off-surface). D1 drift-vs-K (refutes (i) as the lever): K=3-mean / K=5-medoid RAISE on-arc disp 2.27 -> 2.41/2.47 and move ORIG-seats only med 0.43/0.18mm (max 1.8mm) — votes smooth sub-mm, they do not fix 2-4mm drift. D2 normal agreement (refutes (ii) as the lever on r1): cos(coarse S0, snapped U) on-arc med 0.984 min 0.658, junk min 0.894, frac<0.5 = 0/0 — gating changes nothing at r1 (r2: 4-7% disagree, small). So (ii)/(i) are measured dead-ends for yield; the coarse dots sit 2-3mm off-surface and the cap — not the voter — is the binding constraint.

**3. Admission accounting (dedupe>=1mm + ROW40-exclusion, r1-then-r2 order as 123).** cap 2.5: 19 survivors -> 8 admitted (11 dedupe-collisions), seats [8,11,13,40,41,42,160,161], seat dist [0.55..2.62mm], 8/8 within 5mm (junk 0). Covers blind spans [9..13] (8/11/13) and [160..161] (160/161) fully, mid-[32..50] partially (40/41/42). cap 3.0 -> same 8 seats (extra survivor deduped); 3.5 -> same 8 seats with 2 dots swapped to higher-drift variants (3.35/3.05mm, same seats — worse drift, zero new coverage); 4.0 -> same 8 seats (8->9 swap, drift to 3.76). The curve is flat past 2.5: 2.5 is the calibrated knee (minimal drift, full 8-seat yield, junk 0 everywhere). r2 contributes 0 admitted at every cap (all collide in dedupe).

**4. Walk + gate vs 123's marks (need admitted>1 AND junk~0 AND gate<=4.60 AND walk>=198): grown 278, greedy 99/278, final 205, 4 jumps at (98,99)/(132,133)/(172,173)/(191,192). Gate med 4.31 (<2mm 31.7%, gaps5 41, maxstep 67.0, ORIGcov 92/211). Uncovered 16 (spans (25,25),(32,37),(46,50),(96,97),(165,165),(173,173)) — [9..13] and [160..161] spans gone. Admitted 8>1 PASS. Junk 8/8 within-5mm PASS. Gate 4.31<=4.60 PASS (-0.29). Walk 205>=198 PASS. Single-dot fragility note from 123 is retired: the gain is 8 dots over 3 span groups.**

**5. Recipe (landing): (a) port-exact boundary at r0 + span-localized r1 re-run per 123; (b) K=1 snap under disp<=2.5mm & dmid<=5mm (SURF-C1 with calibrated cap); (c) dedupe >=1mm, ROW40-coord exclusion; (d) plain greedy K34+T13 walk. Still open (not this ticket): [165] snap-drag span, [173] flat-at-all-scales (bridge-by-chaining per 123), ROR-owned [25]/[96..97], mid-span remnants (32-37)/(46-50) — next yield lives at detection/chaining, and any cap >2.5 buys drift without seats (measured).**

**6. Renders + paths.** artifacts/pota124/p124_drift.png (disp on-arc/junk separation + drift-vs-K bars) + p124_arc.png (gate-frame ORIG arc, both loops, 8 magenta stars vs 123 cyan +, gate-shift hist) + p124_walk.png (bag-frame walk vs 123-grown, stall X, step spectra) — all eye-checked. Scratch .scratch/pota124_repro/ (p124_control/candidate/measure/admit/walk/render.py + txt + npy: p124_measure_done/admit_c2p5-c4p0/seq_c2p5/loop_c2p5/seq_ctrl). Tickets 39-123 untouched (read-only); COMMIT NOTHING done.

