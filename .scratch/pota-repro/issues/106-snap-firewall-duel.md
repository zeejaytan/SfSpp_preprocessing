# Snap firewall duel — distance cap vs stay-on-face

GOAL: MATCH AUTHOR'S INPUT.

**What to deliver:** head-to-head screening of the two snap fixes from the lead's 104 close-out: (A) distance-capped snap — refuse any snap jump beyond the cloud's own dot spacing (state the cap rule before running); (B) stay-on-face snap — each boundary dot snaps only to vertices of the face it was found on (S0 dots to S0 verts, S1 to S1). Control: unmodified K=1 snap (reproduces 104: ROW40 40/40). Replay the pipe-exact walk on each resulting bag and gate vs ORIG Bl_0 (median/<2mm/gaps>5mm/jumps).

**Answers:** E1

**Blocked by:** 104 (snap as admission point, ROW40 measures) + 99 (walk checkpoints)

**Status:** results-in

**Prediction (registered before running):** at least one arm drops ROW40 admission to ~zero AND gates at/below 103's row-deleted 4.68mm with no new stall; the winner is the arm whose failure mode is narrower (cap may strand legit dots on coarse regions; face-rule may fail where faces share verts). If both admit the row or both stall the walk, report which with numbers — no recipe then.

**Starting position:** /data/gpfs/projects/punim2657/pota104_repro/ (per-surface boundary sets + unclustered verts + ROW40 definition) + 102/103 walk replay. Login-node numpy only — no Slurm, no E2E. New scratch pota106_repro/; renders under laptop artifacts/pota106/.

**Rules:** cleaned-bag discipline applies downstream only — here the bags under test ARE the variable, so the control must reproduce 104 exactly first (green control); read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); one variable per arm.

- [ ] Control reproduces 104 (ROW40 40/40, same gate)
- [ ] Arm A vs Arm B (ROW40 admission, walk, gate)
- [ ] Verdict + implementation recipe for the winner (file + line + rule), or refutation

## Comments (worker, 2026-10-19 — COMMIT NOTHING; lead to commit)

**Verdict: prediction REFUTED — neither arm cures both birds; no implementation recipe (refutation, per brief).**

**0. Method (login-node numpy only; zero ORIG points copied; ORIG Bl_0 gate-evidence only; COMMIT NOTHING).** Pipe-faithful replay of 104 arm P: S0-alone boundary (364) -> K=1 improve onto unclustered.ply (2342 verts) -> ROR r_o=8.62091 (dense rule) -> greedy K=34 / SFS-T13 walk -> gate vs ORIG Bl_0 (n=211, 103/104 recipe: GT-seat each, fresh->ORIG nearest, gaps = consecutive steps >5mm). Cap rule stated BEFORE running (phase-1 p106_measure.py + p106_cap.txt): Arm A cap = median NN of S0-alone boundary set = 1.38502mm; refused dots keep pre-snap boundary coords. Arm B face rule (phase-1): each unclustered vert labelled by nearest cleaned surface cloud (S0-cleaned vs S1-cleaned, pct8g versions, same as pipe): S0-side=1529, S1-side=813; each S0 boundary dot snaps to nearest S0-side vert only. Phase-1 files reused as-is (p106_face_isS0.npy, p106_clean_S0/S1.npy, p106_cap.txt); attempt-1 green work verified, nothing redone. New code: pota106_repro/p106_run.py (arms + walk + gate), p106_render.py. Laptop mirror artifacts/pota106/ (p106_measure.py, p106_run.py, p106_render.py, p106_numbers.txt, p106_compare.png eye-checked). No Slurm, no E2E; 39-105 lanes read-only; no prep/assembly sources touched.

**1. Control GREEN — reproduces 104 exactly.** Bag 343 kept/21 removed; ROW40 40/40 in final bag; greedy 93/343, final 237, jumps at (92,93) (132,133) (170,171) (223,224); loop gate med 5.79, <2mm 24.9, gaps5 45; bag gate med 5.80, <2mm 22.2 — all to 2dp identical with 104 arm P. Face-hop proxy (turns>45/>60deg): t45=84 t60=45.

**2. Verdict table (per arm: ROW40 admission, walk, gate vs ORIG, two-birds).**

arm | bag | ROW40 final | greedy/final | jumps | loop med | loop <2mm (true-edge share) | gaps5 | t45/t60 | bag med/<2mm
control | 343 | 40/40 | 93/237 | 4 | 5.79 | 24.9 | 45 | 84/45 | 5.80/22.2
Arm A cap | 333 | 3/40 | 128/304 | 4 | 5.82 | 6.9 | 37 | 122/57 | 5.67/6.3
Arm B face | 342 | 29/40 | 93/228 | 5 | 5.65 | 25.9 | 47 | 80/44 | 5.80/22.2

**3. TWO-BIRDS per arm (admission cure + true-edge share within 2mm ORIG + face-hop proxy).** Arm A cures admission (40->3/40; pre-ROR 10/40, ROR drops 7 more) but DESTROYS the true edge: loop <2mm 24.9->6.9, bag <2mm 22.2->6.3, t45 84->122, t60 45->57 — the cap refuses 263/364 (72.3%) because typical snap jumps (med 2.19, p90 3.14, max 10.64) dwarf the cap (1.39); the inboard row sits med 2.10mm out (104 followup), i.e. in the SAME range as legit lip dots, so no distance threshold separates them. Arm B preserves the edge (25.9/22.2, med 5.65 marginally best) but leaves admission at 29/40 and hops unchanged-or-worse (gaps 47 vs 45, 5 jumps vs 4; t45/t60 only marginally down because the loop is 9 dots shorter). Face rule cannot bite harder: ROW40 verts are already 29 S0-side / 11 S1-side, so most snap on-face anyway. Admission winner A, gate winner B by a hair — no arm wins both, and neither reaches 103 row-deleted 4.68mm (best here 5.65). Winner cures both: NO.

**4. Recipe: NOT confirmed at replay level (refutation).** Neither firewall is landable: a distance cap tight enough to strand the row strands the lip; a face rule the row already mostly satisfies. The entry remains the K=1 improve onto unclustered.ply (edgeline_extraction_headless.cpp:951-972, kdtree.nearestKSearch K=1 loop) and the fix, if any, is upstream of the snap (mesh/sample density at the lip, same standing note as 99/103/105) or a snap rule with a genuinely separating feature — distance and face-label both tested NULL here. T75 presplit+select remains the only landing recipe.

**5. Renders + paths.** artifacts/pota106/p106_compare.png eye-checked: (local) control/cap/face bags + ROW40 X | three walk loops (all show teleport chords) | (GT-seated) ORIG green + three loops — all hug ORIG on the intact arc, none traces the top. Spartan: pota106_repro/{p106_measure.py, p106_run.py, p106_render.py, p106_cap.txt, p106_face_isS0.npy, p106_clean_S0/S1.npy, p106_bag_{control,armA,armB}.npy, p106_loop_{control,armA,armB}.npy, p106_numbers.txt, p106_compare.png}.

