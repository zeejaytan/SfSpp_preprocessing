# Snap self-consistency — reverted dots must pass the test that admitted them

GOAL: MATCH AUTHOR'S INPUT.

**What to deliver:** after the unmodified K=1 snap, run the PCL empty-sector boundary test ON THE SNAPPED DOTS THEMSELVES (same 0.6pi rule, same radius): any snapped dot that fails — i.e. its new neighbourhood is full all round, proving it sits mid-face — reverts to its pre-snap boundary coordinates. Rationale: a dot the snap drags into the middle of a face cannot pass the boundary test there; the test becomes its own firewall. Walk + gate the resulting bag vs control.

**Answers:** E1

**Blocked by:** 106 (duel numbers: cap 1.38502mm, ROW40 29 S0/11 S1, typical snap 2.19mm) + 103 (row-deleted bag, gate 4.68mm) + 99 (walk checkpoints)

**Status:** results-in

**Success bar (all must hold):** ROW40 admission ~0/40 AND walk gate at/below 4.68mm med AND no new stall/death (greedy >=93, final pushes >=197, T13 jumps reported). If the bar is not met, refute with numbers — no recipe then.

**Starting position:** /data/gpfs/projects/punim2657/pota106_repro/ (control bags, ROW40 definition, walk replay) + 102/103 replay scripts. Login-node numpy only — no Slurm, no E2E. New scratch pota107_repro/ (108/109 likewise); renders under laptop artifacts/pota10X/ matching the ticket number.

**Rules:** control reproduces 106-control first (green control) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); one variable (the fix under test).

- [ ] Control reproduces 106-control
- [ ] Self-consistency bag (revert count, ROW40 admission, walk, gate)
- [ ] Verdict + recipe (file + line + rule) or refutation

## Comments (worker, 2026-10-19 — COMMIT NOTHING; lead to commit)

**Verdict: REFUTED — the self-consistency firewall does not fire on the row; no implementation recipe (refutation, per brief).**

**0. Method (login-node numpy only; zero ORIG points copied; ORIG Bl_0 gate-evidence only; COMMIT NOTHING).** Pipe-faithful replay of 106-control (S0-alone boundary 364 -> K=1 float32 snap onto unclustered.ply 2342 verts -> ROR r_o=8.62091 dense rule -> greedy K=34 / SFS-T13 walk -> gate vs ORIG Bl_0 n=211, 103/104 recipe). New arm: PCL-1.9.1 empty-sector test (104 float32 port verbatim: atan2f, FLT_MIN init, wrap, strict > 0.6pi) run ON THE 364 SNAPPED DOTS THEMSELVES — same radius r_b=6.46568, same threshold, normals carried with their dots (364/364 pre-snap rows matched to SOR-cleaned S0 sources at 8dp; 338 unique sources, near-tie dups share normals); dots failing at snapped positions (incl. <3 neighbours) revert to pre-snap coords, then ROR/walk/gate as control. New scratch pota107_repro/p107_run.py; render p107_render.py; laptop mirror artifacts/pota107/ (run + render + numbers + PNG eye-checked). No Slurm, no E2E; 39-106 lanes read-only; no prep/assembly sources touched.

**1. Control GREEN — exact 106 reproduction.** Recomputed bag AND loop are bit-identical to p106 saved arrays (exact-match True/True): bag 343 kept/21 removed; ROW40 40/40 pre-ROR and in-bag; greedy 93/343; final 237 pushes; 4 jumps at (92,93) (132,133) (170,171) (223,224); loop gate med 5.79, <2mm 24.9, gaps5 45, t45/t60 84/45; bag gate med 5.80, <2mm 22.2.

**2. Self-consistency arm: revert 8/364 (2.2%), ROW40 untouched, walk and gate unchanged.** Reverted indices [83, 111, 112, 123, 202, 214, 331, 347] (scattered; snap-jumps med 2.29 max 7.30 — ordinary, same range as kept). ROW40 in selfc bag 39/40 (one row dot reverted to a non-row pre-snap coord; zero reverts land on pre-snap ROW40 coords). ROR 343 kept/21 removed — same as control. Walk: greedy 94 (+1 vs control), final 238 pushes, 4 jumps at the same geometry (shifted +1 by the extra greedy dot: (93,94) (133,134) (171,172) (224,225)). Loop gate med 5.79, <2mm 24.8, gaps5 44, t45/t60 82/46; bag gate med 5.80, <2mm 22.2 — identical to control to 2dp.

**3. Success bar (all must hold): NOT MET.** ROW40 ~0/40? NO (39/40). Loop gate <=4.68mm med? NO (5.79, vs 103 row-deleted 4.68). No stall/death (greedy 94>=93, final 238>=197, T13 jumps reported)? YES — but the first two fail, so per the brief: refute with numbers, no recipe.

**4. Mechanism (why the firewall cannot bite).** The ROW40 dots at their snapped positions still face an empty inboard sector — nothing beyond them within r_b=6.47 — so their max angular gap stays > 0.6pi and they PASS the very test that admitted them. The test as specified cannot separate the row from the lip because both sit at the snapped cloud's edge; it fires only on 8 scattered dots whose snapped neighbourhood happens to close up, and reverting those moves the walk nowhere (same stall region, same 4 teleports, gate unchanged). A genuinely separating feature would have to look inboard of the dot (e.g. distance-to-lip-band), not at sector emptiness — which is fix-108/109 territory, not this ticket.

**5. Recipe: NOT confirmed (refutation).** The entry remains the K=1 improve snap (edgeline_extraction_headless.cpp:951-972, kdtree.nearestKSearch K=1 loop); like 106 arms A/B, this firewall is not landable. Standing note (99/103/104/105/106): the fix, if any, is upstream of the snap (mesh/sample density at the lip) or a snap rule with a separating feature — sector self-consistency tested NULL here. T75 presplit+select remains the only landing recipe.

**6. Renders + paths.** artifacts/pota107/p107_compare.png eye-checked: (local) control vs selfc bags overlap (identical 343) + ROW40 X + reverted-8 gold diamonds | two walk loops overlap with the same teleport chords | (GT-seated) ORIG green + both loops hug ORIG on the intact arc, neither traces the top. Spartan: pota107_repro/{p107_run.py, p107_render.py, p107_revert_idx.npy, p107_bag_{control,selfc}.npy, p107_loop_{control,selfc}.npy, p107_numbers.txt, p107_compare.png}.
