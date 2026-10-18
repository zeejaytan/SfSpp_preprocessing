# Interior-row ablation — delete the inboard dots, retrace, compare

GOAL: MATCH AUTHOR'S INPUT.

**What to deliver:** A deletion test of the user's circled row in artifacts/pota102/p102_dots_overlay.png (left panel, blue circle): the upper teal row (walk seq ~100-140) running inboard of the purple lip row. Remove exactly those inboard dots from the 343-bag, replay the pipe-exact walk (102's p102_replay.py: greedy K=34 + SFS-T13), and compare against the unedited baseline: greedy coverage, jump count/positions, final ordered loop, gate vs ORIG Bl_0 (median/<2mm/jumps).

**Answers:** E1

**Blocked by:** 102 (replay script + bag with seq positions) + 99 (walk checkpoints)

**Status:** results-in

**Prediction (registered before running):** with the inboard row gone, the walker keeps to the lip row through the circled region: no second-chance jump bounding that region, greedy coverage rises above 93/343, gate median drops below 5.6mm. If instead the walk still jumps there, the cause is the gap (missing lip dots), not the inboard row — report which with numbers.

**Starting position:** /data/gpfs/projects/punim2657/pota102_repro/p102_walk.npz + p102_replay.py. Identify the row objectively: dots inside the circled screen region whose nearest-mesh face is interior wall OR whose offset from the lip band exceeds the bag's 0.68mm median standoff by 3x — state the rule and the removed count before replaying. Login-node numpy only — no Slurm, no E2E. New scratch pota103_repro/; renders under laptop artifacts/pota103/.

**Rules:** read-only on all inputs (zero ORIG points, bundles md5-guarded; deletion happens on an in-memory/session copy only — never overwrite bundle files); COMMIT NOTHING; Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); one variable (the row deletion).

- [ ] Removal rule + count (stated before replay)
- [ ] Walk replay on edited bag vs baseline (coverage, jumps, loop)
- [ ] Gate vs ORIG both arms + verdict on prediction
## Comments (worker, 2026-10-19 — COMMIT NOTHING; lead to commit)

**Verdict: MIXED — row was the landing pad, not the cause. The walk still jumps at the identical stall point with the row gone, so per the brief's decision rule the driver is the gap (missing chainable lip dots), not the inboard row's pull. Gate improves (5.79→4.68mm med) because the 62.9mm row excursion is gone; greedy stall is untouched (93, same dot).**

**0. Method (login-node numpy/matplotlib only; zero ORIG points copied; session-copy deletion; COMMIT NOTHING).** Reused /data/gpfs/projects/punim2657/p102_repro/p102_walk.npz read-only. New scratch /data/gpfs/projects/punim2657/pota103_repro/ (p103_run.py walk = p102_replay.py walk section verbatim, p103_render.py, p103_walk_edited.npz, p103_numbers.txt, p103_compare.png). Laptop mirror artifacts/pota103/ (p103_compare.png eye-checked, p103_numbers.txt). Renders + numbers are the deliverable; no Slurm, no E2E.

**1. Removal rule (stated before replay) + count.** Rule: delete every bag slot whose walk-visit position lies in **[93,132]** — the complete inter-jump chain segment forming the upper teal strand (jump (92,93) lands on it, jump (132,133) leaves it). Identification: exact-geometry replica of the 102 render (byte-identical md5 9cb4ef…, then proj3d+transData screen projection) puts visits 21–132 + 197–220 + 230–236 inside the user's circle; visit-colour readout of the annotated pixels (viridis inversion, bias-calibrated: true 100–110 inverts 101–170, so high readings are blur) confirms the upper strand is the post-(92,93) chain. [93,132] takes the whole strand and nothing off-strand (133+ is the jumped-away chain, 197+ is projection-coincident bottom arc). Count: **73 slots / 40 unique coords, bag 343→270**; every removed coord vanishes entirely (dup slots share visit by coord key — asserted in-script). One variable: K fixed at 34 for both arms (note: pipe-exact K=W//10 would be 27 for the 270-bag; kept 34 so deletion is the only delta).

**2. Walk replay, edited vs baseline (K=34 both arms).** Baseline control reproduces 102 exactly: greedy 93/343 (27.1%), 237 pushes, 4 jumps at (92,93) (132,133) (170,171) (223,224). Edited: **greedy 93/270 (34.4%) — same absolute 93, same stall dot [-27.26,1.05,388.81], 92/93 greedy coords identical** — the stall is upstream of the row and untouched by its deletion. Final **197 pushes** (196 unique + 1 double-tap, all 196 coords visited), **still 4 second-chance jumps** at (92,93) (126,127) (164,165) (183,184). Jump 3D: E(92,93) takes off from the *identical* stall dot but lands [0.2,-31.5,402.4] (gap 44.7, bottom arc) instead of the row start [-29.4,5.8,419.9] (gap 31.5); E(126,127) [1.2,-38.8]→[42.4,-45.3] (43.9); E(164,165) [65.6,-21.2]→[72.2,4.9] (30.4); E(183,184) [73.6,20.5]→[25.1,66.5] (67.0, same landing as B(223,224)). No edited jump touches the circled rows; baseline had two (enter/leave the row).

**3. Gate vs ORIG Bl_0, both arms (GT-seated, fresh→ORIG nearest, 99 recipe; jumps = consecutive gaps >5mm).** ORIG Bl_0 n=211. Baseline loop (237): **med 5.79mm, <2mm 24.9%, 45 gaps>5mm**. Edited loop (197): **med 4.68mm, <2mm 29.9%, 39 gaps>5mm**. Walk-level second-chance jumps 4→4.

**4. Verdict on the registered prediction.** (a) "no second-chance jump bounding that region" — HOLDS for the row itself (no jump lands on/leaves the deleted strand), but the stall-point jump persists from the identical dot, now landing on the bottom arc: the jumping mechanism is intact. (b) "greedy coverage rises above 93/343" — FAILS absolutely (93, not >93; 34.4% only by denominator shrinkage): the stall never involved the row. (c) "gate median drops below 5.6mm" — HOLDS (4.68). Net: the inboard row was a convenient landing pad for the (92,93) teleport, not its cause; the cause is the gap at the stall dot (K-window saturated by visited ground, nothing chainable on-lip — same stall with the row gone). Next variable is upstream (mesh/sample density at the lip), not the row.

**5. Renders + paths.** artifacts/pota103/p103_compare.png: (local frame) baseline loop + deleted row (black X) | edited loop | (GT-seated) ORIG green + baseline red + edited blue. Spartan: pota103_repro/{p103_run.py, p103_render.py, p103_walk_edited.npz, p103_numbers.txt, p103_compare.png}. 39–102 lanes untouched (read-only); no prep/assembly sources touched; COMMIT NOTHING done.

