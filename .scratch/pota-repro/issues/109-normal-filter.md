# Normal-filtered snap — lip dots face differently than wall dots

GOAL: MATCH AUTHOR'S INPUT.

**What to deliver:** compare dot normals (from getNormalsOnSurface, already in the pipe) between the ROW40 verts and the true-lip boundary dots: if their normal directions separate (lip normals ~along-wall vs interior normals ~wall-facing, or curvature split — measure first, state the rule before running), filter the snapped bag on that rule and walk + gate it. Rationale: the paper's own ordering uses normals; the fold's two passes may share a face but their surface directions differ. If no clean split measures, refute fast with the overlap numbers — do not force it.

**Answers:** E1

**Blocked by:** 106 (duel numbers: cap 1.38502mm, ROW40 29 S0/11 S1, typical snap 2.19mm) + 103 (row-deleted bag, gate 4.68mm) + 99 (walk checkpoints)

**Status:** results-in

**Success bar (all must hold):** ROW40 admission ~0/40 AND walk gate at/below 4.68mm med AND no new stall/death (greedy >=93, final pushes >=197, T13 jumps reported). If the bar is not met, refute with numbers — no recipe then.

**Starting position:** /data/gpfs/projects/punim2657/pota106_repro/ (control bags, ROW40 definition, walk replay) + 102/103 replay scripts. Login-node numpy only — no Slurm, no E2E. New scratch pota107_repro/ (108/109 likewise); renders under laptop artifacts/pota10X/ matching the ticket number.

**Rules:** control reproduces 106-control first (green control) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); one variable (the fix under test).

- [ ] Control reproduces 106-control
- [ ] Normal/curvature split measured (overlap numbers, rule stated)
- [ ] Filtered bag if split exists (ROW40 admission, walk, gate)
- [ ] Verdict + recipe (file + line + rule) or refutation

## Comments (worker, 2026-10-19 — COMMIT NOTHING; lead to commit)

**Verdict: REFUTED as a landing recipe — curvature separates the row from the lip, but the filtered walk strands, so the bar is not met. No implementation recipe (refutation, per brief).**

**0. Method (login-node numpy only; zero ORIG points copied; ORIG Bl_0 gate-evidence only; COMMIT NOTHING).** Pipe's OWN getNormalsOnSurface output for C01 (Pot_C_Piece_01_SampledWithNormals.ply: 10714 pts, MST-oriented signed normals + PCL curvature) — no proxy. Every control-bag dot transfers exactly (med/p90/max transfer distance 0.0000mm: bag verts are cloud points). Control-green first: recomputed 106-control verbatim (K=1 improve -> ROR r_o=8.62091 -> greedy K=34/SFS-T13 -> 103 gate) — matches p106_numbers.txt control line exactly (343, ROW40 40/40, 93/237, 4 jumps, med 5.79/<2mm 24.9/gaps5 45/t45 84/t60 45, bag 5.80/22.2). New scratch /data/gpfs/projects/punim2657/pota109_repro/ (p109_measure.py + p109_measure.txt, p109_run.py + p109_numbers.txt, p109_render.py, p109_compare.png, control + filtered bags/loops). Laptop mirror artifacts/pota109/ (scripts + numbers + PNG, eye-checked). No Slurm, no E2E; 39-108 lanes untouched; no prep/assembly sources touched.

**1. Split measurement (rule PRE-REGISTERED before running: angle>=45° with both Rbar>=0.80, OR >=32/40 ROW40 outside LIP curvature central-90% band).** Sets: ROW40 (40 unique) vs LIP = unique control-bag coords minus ROW40. Signed normals are mutually INCOHERENT — ROW40 Rbar=0.262, LIP Rbar=0.182 — so the 83.7° between-mean angle is noise (criterion (a) FAILS; orientation-free axis check agrees: LIP dev med 42.7/p90 76.9 vs ROW40 med 64.0/p90 88.4, heavy overlap). Curvature DOES separate, inverted from the naive guess: ROW40 wall dots are FLAT (med 0.01979, IQR [0.01169,0.04252]) vs lip-edge dots CURVED (med 0.08682, IQR [0.06344,0.12205]). LIP central-90% band [0.04521,0.16057]: ROW40 outside = 60/73 slots but only 30/40 unique — criterion (b) FAILS at unique level (30 < 32), borderline. Ran the filter arm anyway as the informative next step: RULE (stated before running): drop any snapped dot with pipe-curvature < LIP-p5 = 0.04521; kept dots keep snapped coords.

**2. Filter arm (one variable vs control).** On 364 snapped: drop 73 / keep 291; 73 snapped slots sit on ROW40 coords, 55 dropped, 18 kept. After ROR: bag 258 slots / 186 unique (control 343/236), ROW40 5/40. Walk K=34: greedy 144/258 (55.8% >= 40% so T13 second chance NEVER fires, 0 jumps), final 144 — 114 dots strand, 24 greedy-internal gaps>5mm. Loop gate med 4.25, <2mm 32.6%, t45 46/t60 26; bag med 4.31/<2mm 27.5%. Loop is a 143/144-unique subset of the control path (then strands at [65.6,-21.2,409.1]). 5 ROW40 survivors at (0.26,34.88,445.31), (3.05,9.09,442.57), (4.52,9.24,443.07), (5.36,9.14,449.45), (5.78,11.31,449.92) — high-curvature inliers the band keeps.

**3. Against the success bar (ROW40 ~0/40 AND med<=4.68 AND greedy>=93 AND final>=197): FAIL.** ROW40 5/40 (not ~0), med 4.25 passes, greedy 144 passes, final 144 < 197 FAILS — the walk dies instead of completing. The 4.25 median is the same threshold-artefact class as 105-DENSIFY (greedy over 40% suppresses T13, fragment scores well): not a traced loop. Curvature is a real signal (admission 40->5) but at replay level it strands the walker — the gap at the stall dot still has nothing chainable once the flat dots are gone. No recipe: no file+line change lands this. Next variable stays upstream (mesh/sample density at the lip), same standing note as 99/103/105/106; T75 presplit+select remains the only landing recipe.

**4. Renders + paths.** artifacts/pota109/p109_compare.png eye-checked: (local) control bag 343 vs curv-filt bag 258 + ROW40 X (filtered bag missing most of the row strand) | walk loops (control 237 full vs purple 144 fragment with chords) | GT-seated ORIG green + both loops (purple hugs part of arc, never traces the top). Spartan: pota109_repro/{p109_measure.py,p109_run.py,p109_render.py,p109_measure.txt,p109_numbers.txt,p109_compare.png,p109_bag_control.npy,p109_loop_control.npy,p109_bag_filt.npy,p109_loop_filt.npy}. 39-108 lanes read-only; COMMIT NOTHING done.
