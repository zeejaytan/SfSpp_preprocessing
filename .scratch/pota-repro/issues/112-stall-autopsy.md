# Stall-dot autopsy — why does greedy stop at the same dot every time?

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 111 (stall dot identical in control/row-deleted/densified at [-27.26,1.05,388.81]) + 103 (driver = gap at stall dot, now disproven as density) + 99 (walk checkpoints)

**Status:** results-in

**What to deliver:** a full autopsy of the stall event, MEASURE FIRST: replay the greedy walk on the 103 cleaned bag and freeze the moment it stops. Report (a) the stall dot's K=34 net — how many unvisited, at what distances, and why none is taken (all visited? none within reach? cone/heading rule?); (b) the dot's normals + curvature vs its neighbours (does the surface direction flip here?); (c) the mesh context — fold constriction, face/segmentation label, scan border?; (d) where the TRUE arc (ORIG-seated) goes from here — does the walk stop where the author's line continues, i.e. is the next true dot simply missing from the bag (void), or present-but-refused (rule)? The verdict must name one: VOID (next true dot absent → bag-building failure at this spot) or REFUSAL (next true dot present → walk-rule failure at this spot). If REFUSAL with a one-variable resume rule, test it (walk + gate vs 4.68). If VOID, map the void's extent and say what input step owns it.

**Starting position:** pota103/111_repro/ (cleaned + densified bags, walk replays), C01 fragment mesh, 99 checkpoints. Login-node numpy only — no Slurm, no E2E. New scratch pota112_repro/; render under laptop artifacts/pota112/ (stall close-up: net, normals, void/arc context).

**Rules:** control reproduces 103-cleaned stall first (same dot to 2dp) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; mechanism named before any fix arm.

- [ ] Stall reproduced (same dot 2dp) + K-net frozen
- [ ] VOID vs REFUSAL named with numbers
- [ ] Fix arm if REFUSAL (walk + gate) or void map + owner if VOID
- [ ] Verdict + render
## Comments (worker, 2026-10-19 — COMMIT NOTHING; lead to commit)

**Verdict: REFUSAL — the walk eats its own bridge, then strands. No bag void at the stall; the continuation dots are present in the bag but were consumed 40 steps earlier from the off-arc side, and the K=34 window (r=29.7mm) is 34/34 visited ground at stall time. Nearest fresh dot is 44.7mm away at a 122° reversal — greedy cannot take it, T13 teleports instead. No surface flip, no fold, no scan border at the stall: purely walk dynamics.**

**0. Method (login-node numpy/matplotlib only; zero ORIG points copied; ORIG Bl_0 gate-evidence only; COMMIT NOTHING).** New scratch /data/gpfs/projects/punim2657/pota112_repro/ (p112_autopsy.py = control + K-net + normals, p112_freeze2.py = stall-time visits + K-sweep, p112_arc.py = mesh + ORIG arc + verdict, p112_fixarm.py = first-pass + K68, p112_render.py = K100 + figure; p112_numbers.txt, p112_freeze.npz, p112_arc.npz, p112_loop_K68.npy, p112_loop_K100.npy, p112_stall.png). Laptop mirror artifacts/pota112/ (p112_stall.png eye-checked, p112_numbers.txt). Control = 103 verbatim (visit-[93,132] deletion, greedy K=34 + SFS-T13). 39–111 lanes read-only.

**1. Control GREEN — stall reproduced to 2dp.** Greedy 93/270, final 197, 4 jumps at (92,93)/(126,127)/(164,165)/(183,184); stall dot [-27.26,1.05,388.81] identical (gate med 4.68 per 103).

**2. (a) K-net freeze at the stall.** K=34 window radius 29.708mm; stall-time visited 34/34, unvisited 0 (visits in window: 45–69 first pass + 87–92 return leg; k00 self visit 92, chain steps 2.4/2.4/5.5mm into the stall). Stall-time pool: 120 visited / 150 unvisited. Nearest-8 unvisited: ranks 61–74 globally, 44.7–52.1mm, ALL at 116–122° turn vs incoming heading h=[0.01,0.82,-2.27] — behind-across the gap on the bottom arc (U0 = slot 242 = the T13 E(92,93) landing dot). K-sweep: K=34/50 → same stall 93; K=68 → 127 (stalls bottom arc); K=100 → 184; K=150/270 → 197. Chainable dots exist at wider K — the K=34 rule is blind past its own footprints, not starved of dots.

**3. (b) Normals + curvature (unclustered.ply, 2342 pts, all bag dots d2cloud=0.000).** Stall n=[-0.987,-0.141,0.082], curv 0.09897 (lip-like, above 109 LIP band edge 0.045); SEQ89/90/91 cos-vs-stall 0.991/0.979/0.986 — NO surface-direction flip at the stall. SEQ87/88 (the 18.4mm greedy stride at 88→89) cohere worse (0.808/0.873, curv 0.065/0.036) — the stride lands from a flatter patch. Nearest-8 unvisited normals cos 0.15–0.47 vs stall: different surface patch across the gap.

**4. (c) Mesh context (Mesh.obj 11875 verts/23114 faces, same frame: stall→mesh-nn 0.392mm).** Stall→boundary 40.76mm (636 boundary verts — NOT a scan border); local edges (both ends <10mm, n=760) med 1.782/p90 2.989 (normal density); fold check: nearest T13-phase chain dot 44.69mm (no fold touch here); bbox margins [10,48.1,13.4]mm (interior). Nothing special — no constriction, no face/border anomaly.

**5. (d) True arc (ORIG-seated): the walk stops ON the author's line, facing consumed ground.** Stall seats ORIG[21] d=0.53mm; travel dir +1 (chain seats ORIG 5→6→16→18→20→21 tightening 1.96→0.53mm). Next-3 successors ORIG[22,23,24]: near-bag 1.39/3.18/4.96mm — present within 5mm → REFUSAL by the pre-registered rule. But every near-bag dot is visited-at-stall: ORIG[22–24]→ the stall dot itself; ORIG[25–31]→ k14 dot [-27.78,9.56,379.77] (firstvisit 53), 0.68–5.70mm away. Smoking gun: at step 53 the walk stepped within 2.33mm of ORIG[27] (k14), then walked away down the bottom arc (seats ORIG 23→13→9→3→0→208→1→6 at 5–7mm off-arc, seq 56–84) and re-approached 87–92, striding 18.4mm at 88→89 into a cul-de-sac of its own footprints. First pass ate the bridge from the wrong side; second pass starved.

**6. Fix arms (one variable: K only) + gate vs 4.68.** K=68: greedy 127/270 (T13 suppressed, 47%≥40%), final 127, med 4.83 — FAILS bar, ORIGcov 27.0% (90-run gap) = fragment, RULED OUT. K=100: greedy 184/270 (T13 suppressed), final 184, 0 jumps, med 4.29 PASSES bar, ORIGcov 83/211 (39.3%) IDENTICAL to control with identical uncovered runs [30,26,24,9,5], gaps5 35 vs 39. K=100 removes the 4 teleports and tightens the median without losing arc coverage — but abandons 12 uniques, stays gap-ridden (35 gaps>5mm), and leaves the self-consumption mechanism intact (104/110-class operating point, not a cure). NOT claimed as a landing recipe: needs lead call whether a teleport-free, T13-suppressed 184-loop is acceptable, or whether the real fix is heading-aware walk (99's guard, 75's CONE+presplit+select) so the first pass stops eating the bridge.

**7. Renders + paths.** artifacts/pota112/p112_stall.png eye-checked: (PCA local) bag + greedy 0–92 + K-window ring + stall star + magenta unvisited | (GT-seated) ORIG ring + greedy + ORIG[21–30] continuation + stall seat | step profile (18.4mm stride, stall line, 4 teleports). Spartan pota112_repro/: {p112_autopsy.py, p112_freeze2.py, p112_arc.py, p112_fixarm.py, p112_render.py, p112_numbers.txt, p112_freeze.npz, p112_arc.npz, p112_loop_K68.npy, p112_loop_K100.npy, p112_stall.png}. COMMIT NOTHING done.
