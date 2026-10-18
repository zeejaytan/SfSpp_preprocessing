# Face-guard walk — stop the tracer hopping inner to outer wall

GOAL: MATCH AUTHOR'S INPUT.

**What to deliver:** a screening test of the user's two-fix program, fix 2: replay the C01 walk with a face-discipline rule (e.g. heading/forward-cone guard, or nearest-on-same-face preference using the surface label each dot came from) and compare against the unguarded walk: face-hop count (wall-thickness crossings), jumps, gate vs ORIG Bl_0 (median/<2mm/gaps). Prediction (registered before running): the guarded walk stays on one face through the fold region, face-hops drop to ~zero, gate median drops below 103's 4.68mm. If confirmed, write the exact implementation recipe (which routine, file + line, guard condition).

**Answers:** E1

**Blocked by:** 99 (walk checkpoints) + 103 (edited bag + verdict)

**Status:** results-in

**Starting position:** /data/gpfs/projects/punim2657/pota103_repro/p103_walk_edited.npz + walk code section; run BOTH on the edited (row-deleted) bag and on the full 343-bag to separate the two fixes' contributions. Login-node numpy only — no Slurm, no E2E. New scratch pota105_repro/; renders under laptop artifacts/pota105/.

**Rules:** read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); SFS-T13 and pipe sources untouched (replay-level guard only); COMMIT NOTHING; Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); one variable per arm (guard on/off).

- [ ] Guarded vs unguarded on full bag and on row-deleted bag (hops, jumps, gate)
- [ ] Verdict on prediction + contribution split (dots fix vs guard fix)
- [ ] Implementation recipe if confirmed (file + line + guard condition)

## Lead note (2026-10-19 — method correction)
User ruling: once a deletion is known-good (103's row), all later arms run on the cleaned bag ONLY — testing on the full bag with a known-bad row still in it confounds the comparison. The FULL-bag arms above are therefore struck as evidence; the valid verdict rests on EDITED-UNGUARDED vs EDITED-GUARDED vs DENSIFY (all row-deleted): guard still dies at dot 44, densify still 5.54 behind 4.68. Verdict unchanged, evidence base narrowed. Rule for all future tickets: cleaned bag is the baseline; never re-test on a known-contaminated input.

## Comments (worker, 2026-10-18 — DENSIFY prediction, registered BEFORE running)

**Scope addition from lead: third arm DENSIFY (denser-dots vs guard head-to-head).**

**Method (stated before running):** SFS-T06-style equidistant arc-length linear-interp densify (port of `adaptiveDensifyBreakline`, `original_nurbs_preprocessing/edgeline_extraction_headless.cpp:747-823`: cumulative arc length, uniform intervals, piecewise-linear interpolation, t clamped [0,1]) applied to the EDITED-bag unguarded loop (197 pushes) split at >5mm gaps into chainable runs (no fabricated chord dots across teleport jumps), each run densified proportionally to ~2x, unioned with the 74 unvisited edited-bag dots kept as-is; replay UNGUARDED pipe-exact walk (greedy + SFS-T13) on the densified bag with pipe-exact K=W//10 clamped [5,50], plus a K=34 density-only control. One variable vs EDITED-UNGUARDED is density (K=34 control) / density+pipe-K (K=50 arm).

**Prediction:** DENSIFY smooths local steps (turns>60 drop) and improves gate modestly vs 4.68mm, but the stall-point T13 jump persists — greedy stalls at the same dot because the gap is missing chainable lip, not a density artefact (denser dots saturate the K-window sooner, not later) — so jumps stay >0 and face-hop proxy does not reach ~zero. If so, neither densify nor cone-guard recovers a full loop at replay level and the T75 presplit+select recipe stands.

## Comments (worker, 2026-10-18 — RESULTS; COMMIT NOTHING; lead to commit)

**Verdict: prediction REFUTED for guard-alone; DENSIFY arm MIXED (jumps change mechanism, gate still behind 4.68). Neither replay-level fix lands a full loop — T75 presplit+select remains the only landing recipe.**

**0. Method (login-node numpy only; zero ORIG points copied; session-copy bags; COMMIT NOTHING).** Guard = replay-level port of the T75 cone (patch75.py): trailing-window heading (mean of last <=4 steps), 45-degree cone (cos>=0.7071), terminate-on-empty, SFS-T13 second chance skipped. K=34 fixed all guard arms so guard on/off is the only delta. Densify = adaptiveDensifyBreakline port (edgeline_extraction_headless.cpp:747-823: cumulative arc length, uniform intervals, piecewise-linear interp, t clamped [0,1]) applied to the EDITED-bag unguarded loop (197 pushes) split at >5mm gaps into 40 chainable runs (no chord fabrication), each run ~2x, union unvisited dots (coord-keyed: 0 — all 270 slots share the 196 visited coords). New scratch /data/gpfs/projects/punim2657/pota105_repro/ (p105_run.py, p105_densify.py, p105_render.py, p105_loop_*.npy, p105_densified_bag.npy, p105_numbers.*). Laptop mirror artifacts/pota105/ (p105_compare.png eye-checked, p105_numbers_all.txt, p105_densify.json). 39-104 lanes untouched; no prep/assembly sources touched.

**1. Comparison table (gate vs ORIG Bl_0 n=211, 99 recipe; face-hop proxy = turns>45/>60deg; gaps = consecutive steps >5mm).** FULL-UNGUARDED n=237 greedy=93/343 (27.1%) T13=4 med=5.79 <2mm=24.9% gaps5=45 t45=84 t60=45 | FULL-GUARDED n=44 walked=44/343 skips=36 stop=44 T13=skipped med=6.03 <2mm=0.0% gaps5=7 t45=3 t60=0 | EDITED-UNGUARDED n=197 greedy=93/270 (34.4%) T13=4 med=4.68 <2mm=29.9% gaps5=39 t45=59 t60=33 | EDITED-GUARDED n=44 walked=44/270 skips=36 stop=44 path-identical-to-FULL-GUARDED med=6.03 <2mm=0.0% gaps5=7 t45=3 t60=0 | DENSIFY-K37(pipe)/K34 n=171 greedy=171/379 (45.1%, T13 never fires) T13=0 med=5.54 <2mm=28.7% gaps5=14 t45=19 t60=14. Controls reproduce 102/103 exactly.

**2. Guard verdict (registered: on-face through fold, hops ~zero, med < 4.68).** FAILS on all three: guarded walk terminates at dot 44 (36 cone-skips), never reaching the fold/stall region (stall dot 92) — no on-face fold traversal to score; t60 reads 0 only because the walk is a 44-pt fragment; med 6.03 worse than BOTH unguarded arms with <2mm 0.0%. Contribution split: guard effect identical on both bags (same 44-dot path, stop 44 < 92) — independent of row deletion; dots fix (103: 5.79->4.68) and guard fix do not compose at replay level. Consistent with T75 CONE arm (402->19pts, 5.74/0%/1 jump: cone alone shortens, does not land).

**3. DENSIFY verdict (registered: smoother, gate modestly better than 4.68, stall-point T13 persists).** MIXED with a different mechanism: T13 reads 0 NOT by chaining the gap but by threshold artefact — greedy 171/379 (45.1% >= 40%) means the second chance never fires and 208 dots strand with no jumps; greedy-internal gaps>5mm persist at 14 and med 5.54 is WORSE than EDITED-UNGUARDED 4.68 (though better than guarded 6.03). K37 vs K34 identical — K is not the driver. Head-to-head conjunction (hops ~zero AND gate <= guarded) fails on hops (14 residual), so the guard is not superseded; both non-landing.

**4. Recipe: NOT confirmed at replay level (refutation, per brief).** Landing recipe remains T75's: forward-cone guard + presplit (union-find >5mm components) + inner-loop select in original_nurbs_preprocessing/edge_line_ordering.cpp (POTA75 patch block at the :92-103 stepper + T13 skip): SEL n=16 med 1.18/<2mm 100%/zero jumps, E2E C_G 2/2+1/3 x3. Next variable is upstream (mesh/sample density at the lip), not walk/density — same standing note as 99/103.

**5. Renders + paths.** artifacts/pota105/p105_compare.png (eye-checked: FULL unguarded red + teleport chords vs green 44-fragment + guard-stop star | EDITED blue vs green vs densify orange | GT-seated gate overlay vs ORIG green) + p105_numbers_all.txt. Spartan: pota105_repro/{p105_run.py, p105_densify.py, p105_render.py, p105_loop_*.npy, p105_densified_bag.npy, p105_numbers.txt, p105_densify.json, p105_compare.png}.
