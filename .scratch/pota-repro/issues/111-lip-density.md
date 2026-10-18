# Lip density — is the true edge under-sampled, and does feeding it cure the walk?

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 110 (filter removed 5mm-connectivity — no honest walker spans the rim) + 109 (curvature admission 40->5) + 103 (cleaned bag 4.68) + 99 (71/343 never visited)

**Status:** results-in

**What to deliver:** the standing note across six tickets says the next variable is upstream (mesh/sample density at the lip). MEASURE FIRST, then test: (a) compare sampling density along the true lip arc (author-seated regions of the 103 cleaned bag) vs the row region — dot spacing + underlying mesh edge lengths in both regions, numbers stated before any fix; (b) if the lip is under-sampled, densify ONLY the lip sampling (one variable — e.g. finer boundary-test output, midpoint fill on the cleaned bag, or mesh-side densification; state the rule before running) and walk + gate it with greedy+T13. Success bar: greedy >=197 pushes with T13 behaving (not suppressed), gate at/below 4.68mm, ROW40 admission reported (curvature filter may be applied as stated pre-registered step, not a second variable — declare it). If the lip is NOT under-sampled, refute fast with the density numbers — that kills the upstream hypothesis and forces a rethink.

**Starting position:** pota103/109_repro/ (cleaned + filtered bags), C01 fragment mesh, 99 checkpoints. Login-node numpy only — no Slurm, no E2E. New scratch pota111_repro/; render under laptop artifacts/pota111/.

**Rules:** control reproduces 103-cleaned-bag first (green control) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; measure-first, rule-stated-before-run.

- [ ] Density measured (lip arc vs row: dot spacing + mesh edge lengths)
- [ ] Rule stated, densified bag (or fast refutation)
- [ ] Walk + gate vs 4.68 bar
- [ ] Verdict + recipe or refutation

## Comments (worker, 2026-10-19 — COMMIT NOTHING; lead to commit)

**Verdict: REFUTED as a landing recipe — the lip is NOT globally under-sampled (medians match the row), and densifying its gap tail extends the greedy chain one-for-one up to the IDENTICAL stall dot without curing the stall or the teleport mechanism. No implementation recipe (refutation, per brief).**

**0. Method (login-node numpy only; zero ORIG points copied; ORIG Bl_0 gate-evidence only; COMMIT NOTHING).** Control rebuilt 103 verbatim in own scratch (p111_control.py = p103_run.py with OUT repointed): visit-[93,132] deletion (73 slots/40 uniques, bag 343->270), greedy K=34 + SFS-T13, 99/103 gate recipe. Control GREEN, byte-identical to pota103_repro/p103_numbers.txt (diff clean): baseline greedy 93/343 final 237 med 5.79, edited greedy 93/270 final 197 jumps 4 at (92,93)/(126,127)/(164,165)/(183,184), edited med 4.68. New scratch /data/gpfs/projects/punim2657/pota111_repro/ (+ paved-variant bag/loop/numbers kept as ruled-out evidence). Laptop mirror artifacts/pota111/ (p111_measure.py, p111_densify.py, p111_probe.py, p111_render.py, p111_measure.txt, p111_numbers.txt, p111_numbers_paved.txt, p111_compare.png eye-checked). No Slurm, no E2E; 39-110 lanes read-only; no prep/assembly sources touched.

**1. Density measured (phase 1, rule inputs for phase 2).** LIPARC = 59 cleaned-bag uniques with GT-seated ORIG-nn < 2.0mm (30.1% of 196); ROW40 = 40 removed uniques. Dot spacing (unique-level NN, local mm): LIPARC-in-cleaned med 2.411 / mean 2.870 / p90 4.767 / max 12.431; LIPARC-in-baseline med 2.411 / p90 4.323 / max 7.516 (gap pre-exists deletion); ROW40-in-baseline med 2.300 / mean 2.342 / p90 3.483 / max 4.852. Mesh.obj (11875 verts, 34989 edges, same frame by bbox overlap; the 11.27mm med vertex-to-bag figure is whole-fragment coverage, not a frame mismatch): LIPARC-near edges (2387, both ends <5mm) med 1.704 / p90 2.801; ROW40-near (1471) med 1.510 / p90 2.644. Cloud support identical (bag dots ARE cloud points, NN 0.000 both; pts-within-3mm med 8 vs 6). Reading: NO global under-sampling (medians within 5-13%), but the lip carries a gap tail the row lacks (lip max 12.43 vs row max 4.85).

**2. Rule stated before run (rev-A; first attempt paved teleports, kept as negative).** First attempt filled LIPARC-run gaps >3.5mm along full loop order: +59, but 32 of 59 bridged the 44.7/30.4mm T13 teleports (straight chords across non-lip space) — RULED OUT as off-lip fabrication; its numbers kept (p111_numbers_paved.txt: greedy 169/329, T13 suppressed at 51%, final 169, med 3.74, ORIGcov 36.5% — a 109-class fragment scoring well). Rev-A rule: fill ONLY consecutive LIPARC pairs BOTH with control-seqpos < greedy_n=93 (greedy-chained steps; T13-phase pairs skipped and logged), gap > 3.5mm (row p90), floor(g/2.3) midpoints (row median pitch), interpolations of our own dots only. Result: +19 honest lip midpoints, bag 270->289, ROW40 admission 0/40.

**3. Densified walk + gate vs 4.68 bar.** Greedy 93->112 (+19 = every inserted midpoint consumed, then strand), T13 fired per-spec (112/289=38.8%<40%) with the SAME 4 teleports at the SAME lengths (44.7/43.9/30.4/67.0mm), final 216 pushes, loop med 4.22 / <2mm 36.1% / gaps5 35 / t45 59 / t60 33. Fragment guard: ORIGcov 39.3%->47.4% (+17 pts, all midpoints used in-loop), but the three largest uncovered ORIG runs are UNTOUCHED ([30,26,24] both arms). Decisive: the dense stall dot is IDENTICAL to control ([-27.26,1.05,388.81]) — density feeds the chain but the K-window still saturates at the same dot. Against the bar (greedy>=197 AND med<=4.68 AND T13 behaving AND ROW40 reported): greedy 112 FAILS, med 4.22 passes, T13 per-spec, ROW40 0/40. Numbers improve, mechanism intact — same verdict class as 103 (landing pad vs cause): the stall is not a spacing problem.

**4. Renders + paths.** artifacts/pota111/p111_compare.png eye-checked: (local) bag270 grey + LIPARC59 teal + ROW40 red X + MID19 orange | control197 red vs dense216 blue with shared stall star | GT-seated ORIG green + both loops (dense hugs more arc, same teleports). Spartan pota111_repro/: {p111_control.py, p111_measure.py, p111_measure.txt, p111_regions.npz, p111_densify.py, p111_probe.py, p111_render.py, p111_numbers.txt, p111_numbers_paved.txt, p111_bag_dense.npy, p111_loop_dense.npy, p111_bag_paved.npy, p111_loop_paved.npy, p111_compare.png} + control p103_walk_edited.npz/p103_numbers.txt. Next variable is NOT density — the gap at the stall dot has nothing chainable at any tested pitch; rethink points at why the K-window saturates there (direction/curvature gate at the stall) or beam-side, per the standing note. COMMIT NOTHING done.
