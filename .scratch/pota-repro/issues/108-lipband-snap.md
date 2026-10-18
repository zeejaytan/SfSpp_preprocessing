# Lip-band snap — keep only snapped dots near the boundary they came from

GOAL: MATCH AUTHOR'S INPUT.

**What to deliver:** after the unmodified K=1 snap, drop every snapped dot farther than X from the pre-snap boundary set (test X = 1x and 2x the cloud's median dot spacing 1.07761mm — two sub-arms; state both before running). Rationale: 106 proved distance-from-ORIGIN can't separate row from lip, but distance-from-the-boundary-set might: legit lip snaps stay near the boundary curve while the row sits ~2.1mm off it. Walk + gate each sub-arm vs control.

**Answers:** E1

**Blocked by:** 106 (duel numbers: cap 1.38502mm, ROW40 29 S0/11 S1, typical snap 2.19mm) + 103 (row-deleted bag, gate 4.68mm) + 99 (walk checkpoints)

**Status:** results-in

**Success bar (all must hold):** ROW40 admission ~0/40 AND walk gate at/below 4.68mm med AND no new stall/death (greedy >=93, final pushes >=197, T13 jumps reported). If the bar is not met, refute with numbers — no recipe then.

**Starting position:** /data/gpfs/projects/punim2657/pota106_repro/ (control bags, ROW40 definition, walk replay) + 102/103 replay scripts. Login-node numpy only — no Slurm, no E2E. New scratch pota107_repro/ (108/109 likewise); renders under laptop artifacts/pota10X/ matching the ticket number.

**Rules:** control reproduces 106-control first (green control) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); one variable (the fix under test).

- [ ] Control reproduces 106-control
- [ ] Lip-band sub-arms (kept/dropped counts, ROW40 admission, walk, gate)
- [ ] Verdict + recipe (file + line + rule) or refutation

## Comments (worker, 2026-10-19 — COMMIT NOTHING; lead to commit)

**Verdict: success bar NOT met — refutation, no recipe.** Neither sub-arm meets all three conditions; X1 cures admission but kills the walk and the edge, X2 keeps part of the lip but keeps part of the row and still stalls.

**0. Method (login-node numpy only; zero ORIG points copied; ORIG Bl_0 gate-evidence only; COMMIT NOTHING).** Pipe-faithful replay of the 106 chain: S0-alone boundary (364) -> unmodified K=1 snap onto unclustered.ply (2342 verts) -> lip-band filter (THE variable) -> ROR r_o=8.62091 (dense rule) -> greedy K=34 / SFS-T13 walk -> gate vs ORIG Bl_0 (n=211, GT-seated, fresh->ORIG nearest, gaps = consecutive steps >5mm). Thresholds stated BEFORE any arm ran (phase-1 p108_measure.py -> p108_thresh.txt): X1 = 1.07761mm (1x S0 cleaned-cloud spacing, verified by recomputing the pipe adaptive rule: spacing=1.07761, r_b=6.46568, matches 102/104) and X2 = 2.15522mm (2x). Band-dist[i] = min_j ||snapped[i]-Xb0[j]|| over the pre-snap S0-alone boundary set (self-index included, so band-dist <= snap jump). Phase-1 files reused as-is; new code: pota108_repro/{p108_measure.py, p108_run.py, p108_render.py}. Laptop mirror artifacts/pota108/ (measure/run/render scripts, p108_thresh.txt, p108_numbers.txt, p108_compare.png eye-checked). No Slurm, no E2E; 39-107 lanes read-only; no prep/assembly sources touched.

**1. Control GREEN — reproduces 106-control exactly.** Bag 343 kept/21 removed; ROW40 40/40; greedy 93/343, final 237, jumps at (92,93) (132,133) (170,171) (223,224); loop gate med 5.79, <2mm 24.9, gaps5 45, t45 84, t60 45; bag gate med 5.80, <2mm 22.2 — all to 2dp identical with 106-control.

**2. Verdict table (per arm: kept/dropped, ROW40 admission, walk, gate vs ORIG).**

arm | pre-ROR kept/dropped (/364) | ROW40 pre-ROR | ROR bag | ROW40 final | greedy/final | jumps | loop med | loop <2mm | gaps5 | t45/t60 | bag med/<2mm
control | 364/0 | 40/40 | 343 | 40/40 | 93/237 | 4 | 5.79 | 24.9 | 45 | 84/45 | 5.80/22.2
X1 1x | 102/262 | 3/40 | 60 | 0/40 | 45/45 | 0 (no T13: greedy 45/60=75% >= 40% trigger; 15 dots stranded unvisited) | 4.83 | 0.0 | 8 | 12/5 | 4.30/0.0
X2 2x | 224/140 | 20/40 | 161 | 8/40 | 48/104 | 2 at (47,48) (65,66) | 5.46 | 14.4 | 33 | 46/31 | 5.64/12.4

**3. Bar check (all must hold).** ROW40 ~0/40: X1 0/40 HOLDS, X2 8/40 FAILS. Walk gate <=4.68mm med: X1 loop 4.83 FAILS (bag 4.30 is not the walk gate), X2 5.46 FAILS. No stall (greedy >=93, final >=197): X1 45/45 FAILS twice over, X2 48/104 FAILS twice over. T13 jumps reported: X1 none (walk died before second-chance could trigger), X2 two.

**4. Why-not (measured, not guessed).** Band-dist spans med 1.751 / p90 2.480 / max 6.990 over the 364 snapped dots, i.e. almost entirely ABOVE X1 — only 102/364 survive, and the survivors sit so sparse that ROR (tuned for the dense 364-set) eats a further 42/102 (41% vs 21/364 = 6% control). ROW40 band-dist med 2.098 (p10 1.156 / p90 2.857) overlaps the all-dot distribution (med 1.751) almost completely: only 3/40 row dots fall inside X1 and 20/40 inside X2, while the legit lip is stranded alongside the row — X1's loop <2mm share is 0.0%, the true edge is gone, same failure mode as 106 Arm A. X1's loop med 4.83 < control 5.79 is a stump artifact (45-dot loop, zero true-edge coverage), not a gate win — the bar's three conditions are conjunctive for exactly this reason. X2 (224 kept) preserves some lip (<2mm 14.4 vs 24.9 control) but at 20/40 row admission pre-ROR -> 8/40 post-ROR, and the thinned bag still stalls the walker at greedy 48. Net: distance-from-the-boundary-set does not separate row from lip either — the row sits ~2.1mm off the boundary curve but so does most of the legit snapped lip (typical snap jump med 2.19mm, 106). The snap entry (edgeline_extraction_headless.cpp:951-972, K=1 onto unclustered.ply) stays unlandable by any distance threshold tested in 106/108; the fix, if any, is upstream (mesh/sample density at the lip) or a snap rule with a genuinely separating feature.

**5. Renders + paths.** artifacts/pota108/p108_compare.png eye-checked: (local) control/X1/X2 bags + ROW40 X | three walk loops | (GT-seated) ORIG green + three loops. Spartan: pota108_repro/{p108_measure.py, p108_run.py, p108_render.py, p108_thresh.txt, p108_bag_control.npy, p108_bag_X1.npy, p108_bag_X2.npy, p108_loop_control.npy, p108_loop_X1.npy, p108_loop_X2.npy, p108_numbers.txt, p108_compare.png}. Login-node only, no job IDs (nothing submitted).
