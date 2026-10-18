# Heading-guard replay — stop the walk eating its own bridge

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 112 (REFUSAL: step 53 passes within 2.3mm of ORIG[27], leaves down-arc, returns into own footprints; stall 34/34 visited) + 103 (cleaned bag, gate 4.68) + 99 (T75 forward-cone exists) + 105 (face-guard died at 44 — this is HEADING not face, different variable)

**Status:** results-in

**What to deliver:** replay greedy on the 103 cleaned bag with a heading guard added — prefer dots continuing the current direction, refuse (or strongly de-prefer) steps that reverse heading ~180° / re-approach from the side the walk already covered (the step-53 bridge-eating move). State the exact rule before running (e.g. T75's forward-cone inside greedy rather than after presplit; angle + fallback stated). Success bar: greedy >=197 pushes AND walks THROUGH the 112 stall dot (not stopping there) AND gate at/below 4.68mm AND continuation dots survive (no 44.7mm teleport landing). If the guard strands elsewhere, report where + whether the stall moved on-arc (progress) or the walk still eats bridges (refutation with the new break point).

**Starting position:** pota103/112_repro/ (cleaned bag, walk replay, stall freeze, step-53 evidence), T75 cone rule from 99. Login-node numpy only — no Slurm, no E2E. New scratch pota113_repro/; render under laptop artifacts/pota113/ (stall region: guarded path vs control, step-53 move kept or refused).

**Rules:** control reproduces 103-cleaned stall first (same dot 2dp) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; rule-stated-before-run; one variable (the heading guard).

- [ ] Control reproduces stall + step-53 bridge move
- [ ] Rule stated, guarded walk (pushes, stall behaviour, gate)
- [ ] Verdict + recipe or refutation with break point
## Comments (worker, 2026-10-19 — COMMIT NOTHING; lead to commit)

**Verdict: STALL MOVED ON-ARC (progress) with a new far-arc break point — 3 of 4 bar items pass. The heading guard walks THROUGH the 112 stall dot, kills all 4 teleports, and gates 4.31 ≤ 4.68; it strands 7 pushes short of the 197 bar at a new stall with the same REFUSAL signature. NOT a full landing; the recipe is an honest partial.**

**0. Method (login-node numpy/matplotlib only; zero ORIG points copied; ORIG Bl_0 gate-evidence only; COMMIT NOTHING).** New scratch /data/gpfs/projects/punim2657/pota113_repro/ (p113_run.py control + guarded + gate, p113_analyze.py mechanism + render, p113_control.npz, p113_guarded.npz, p113_numbers.txt, p113_compare.png). Laptop mirror artifacts/pota113/ (p113_compare.png eye-checked, p113_numbers.txt). Control = 103 verbatim (visit-[93,132] deletion, greedy K=34 + SFS-T13). 39–112 lanes read-only.

**1. Control GREEN — stall reproduced to 2dp.** Greedy 93/270, final 197, 4 jumps at (92,93)/(126,127)/(164,165)/(183,184); stall dot [-27.26,1.05,388.81] identical; gate med 4.68, <2mm 29.9%, gaps5 39; ORIGcov 83/211 (39.3%), uncovered runs [30,26,24,9,5].

**2. Rule stated before run (GUARD-113, one variable = heading guard, greedy phase only, T13 verbatim):** h = mean of last ≤4 step vectors (105 recipe); K=34 window in distance order, nearest unvisited with turn ≤60° (T75 angle); cone empty → nearest unvisited with turn ≤120° (REFUSE ~180° reversals / re-approach from the covered side); all refused → nearest unvisited anyway (emergency fallback, counted — greedy never strands on guard account, unlike 105's terminate-on-empty at dot 44).

**3. Guarded numbers vs 4.68 bar.** Greedy 190/270 (70.3% ≥ 40%, T13 never fires), final 190, T13 jumps 0. Guard stats: 24 non-nearest cone fires, 1 cone-empty ≤120° fallback, 1 emergency. First divergence vs control at seqpos 28 (top arc). Gate: med 4.31 ≤ 4.68 PASSES, <2mm 31.1% (vs 29.9), gaps5 42 (vs 39 — three extra greedy-internal strides). ORIGcov 83/211 (39.3%) with uncovered runs IDENTICAL [30,26,24,9,5] and identical uncovered ORIG idx list. Max step 32.3 (vs control 67.0); no 44.7mm teleport landing — continuation dots survive.

**4. Bar scorecard (3/4):** (a) ≥197 pushes — FAILS (190, −7); (b) walks THROUGH the 112 stall dot — HOLDS (passes within 1mm at guarded seq 166, continues 23 pushes to 189); (c) gate ≤4.68 — HOLDS (4.31); (d) no 44.7mm teleport — HOLDS (0 T13 jumps).

**5. Bridge verdict: step-53 move REFUSED-AS-ENCOUNTERED, bridge dot reused on-arc.** Control consumed slot 154 (bridge, [-27.78,9.56,379.77]) at firstvisit 53 from the off-arc side (2.33mm from ORIG[27], then left down-arc). Guarded takes slot 154 at seq 47 seated ON the author's line (ORIG[28] d=0.68) arriving from the top arc (ORIG 37-seated chain), i.e. as a through-point, not an off-arc bite — then strides 26.8mm to ORIG[14]. The walk no longer eats-then-starves: it reaches the stall region late (seq 166) and walks past it.

**6. New break point (refutation of full bar, progress per brief):** guarded greedy strands at seq 189, dot [25.13,66.52,424.99] (== control's E(183,184) landing; seats ORIG[88] d=6.01, far-arc end). Same REFUSAL signature as 112: K-window (r=21.4mm) 34/34 visited; nearest fresh 96.6mm away at 125° reversal (vs control's 44.7mm/122°). Only 8 slots left uneaten (262/270 visited), all ~97mm back across the gap near the OLD stall — the walk strides over dots near the stall at 162 (18.4mm, same stride as control's 88→89) and cannot return. Mechanism restated: strides-over-then-strands-beyond (was: eats-bridge-then-starves).

**7. Renders + paths.** artifacts/pota113/p113_compare.png eye-checked: (PCA local) bag + control red with teleport chords vs guarded blue ring + 112 stall star + guarded stop X | stall zoom (blue passes gold star at 166) | step profile (4 red T13 spikes circled, blue max 32.3, no T13) | gate CDF (guarded med 4.31 left of control 4.68). Spartan pota113_repro/: {p113_run.py, p113_analyze.py, p113_control.npz, p113_guarded.npz, p113_numbers.txt, p113_compare.png}. COMMIT NOTHING done.
