# C01 walker instrumentation — name the step-across decision (upstream of file-level repair)

GOAL: MATCH AUTHOR'S INPUT.

**What to deliver:** Instrument the t39-pipe rim-walk stage on C01's lip with the author's ORIG loop as reference: watch where the walker steps across to the neighbouring pass, and name the exact code decision (file:line) that takes the wrong step + what guard (same-pass continuation check) would stop it. A tested guard + gate is the stretch goal; the named decision with blocking evidence is the due deliverable.

**Answers:** E1

**Blocked by:** 97 (branch points idx 10/39/191, constrictions (38,191)/(39,401), both slots miss 5.6/46mm) + 68/69/70/71/79/85 (walk/split/radius/face/smoothing exhausted) + 89 (fused-C regime note)

**Status:** results-in

**Starting position:** t39-pipe rim-walk sources + fresh C01 bundle + ORIG C01 loop. Read 97 Comments (branch points, constriction pairs) and 71 (face ceilings) before instrumenting. New scratch pota99_repro/; renders under laptop artifacts/pota99/.

**Rules:** read-only tracing first (no source edits to the pipe — instrument copies or log, never rewrite the walker blind); one variable for any guard attempt; gate any guard variant (median <2mm vs ORIG C01 Bl_0) before E2E; E2E only if gated, on cure-potA @ bffefb6 with asserts + controls; sacct-direct polling (never scripts/slurm_poll.sh); COMMIT NOTHING; Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); honest negative (decision named but unguardable at file level) is a LANDABLE outcome — say so with the blocking evidence.

- [ ] Walker trace on C01 lip vs ORIG reference (step-across points)
- [ ] Named code decision (file:line) + proposed guard
- [ ] Guard variant + gate (if guardable)
- [ ] E2E x3 only if gated + job IDs + sacct states
## Comments (worker, 2026-10-18 — COMMIT NOTHING; lead to commit)

**Verdict: step-across decision NAMED with walk-level + file-level trace evidence; guard proposed (= T75 cone recipe, already gated green + E2E'd — no new E2E run, would duplicate 75). Landable as the due deliverable; honest negative on full-loop recovery with blocking evidence.**

**0. Method (read-only tracing; ORIG evidence-only distances, nothing copied).** Read 99 brief, then 97 Comments (branch points/constrictions/swap table), 68/71/79/85 Comments (ruled-out paths), 75/74 Comments (guard already built + floor bound). NEW scratch /data/gpfs/projects/punim2657/pota99_repro/ (p99_trace.py, p99_render.py, C99_C01_stepacross_vs_ORIG.png). Laptop mirror artifacts/pota99/ (+ p99_numbers.txt). Login-node numpy/matplotlib only — no Slurm jobs, no sacct states. Zero ORIG points; sources read-only; no commits.

**1. Trace map — walk level (pota39_C/edgeline_stage.log, the t39 pipe's own log).** C01 S0 (lip-bearing): 343-pt boundary, K=34 → greedy covers 93/343 (27.1%) then stalls dead (K-window saturated by visited ground) → SFS-T13 second-chance appends to 237/343 (69.1%) with **4 jumps** (line 23). C01 S1: 109-pt, K=10, 83/109 pass, no second chance (line 1226). 106/343 S0 input points never visited — the true lip was never fully traced, before any resampling.

**2. Trace map — file level (fresh C01 Bl_0, 402 pts, echo of the walk after resample).** Jumps>5mm: 9→10 56.8mm, 38→39 65.5mm, 190→191 105.0mm (= 97 runs [0,10)/[10,39, 29-pt aerial spur]/[39,191, 152]/[191,402, 211)). Constrictions (<2mm, non-consecutive): (261,295) 1.56, (38,191)/(39,401) 1.9 — the two parallel loops touch at fold points adjacent to run boundaries 39 and 191/402. GT-seated vs ORIG C01 Bl_0 (211): FULL 5.61/22.9%; [0,10) 3.58/0%, [10,39) 27.21/0% (aerial spur), [39,191) 5.45/28.9%, [191,402) 5.76/22.7% — neither loop on-contour. Emitted-proxy K-window replay (K=40; caveat: pool is the emitted cloud, true pool is the unordered boundary cloud): at 38→39 the across-pass touch point idx191 sits 1.90mm away at turn 1.3° and the nearest-unvisited rule takes it; at 9→10 / 190→191 the local unvisited void (≥18/31mm) stretches the K-window into 56.8/105mm teleports.

**3. Named code decision.** `original_nurbs_preprocessing/edge_line_ordering.cpp:96-101` (t39 pipe copy /data/gpfs/projects/punim2657/pota39_repro/prep/original_nurbs_preprocessing/edge_line_ordering.cpp carries identical lines, md5 40c344f3): `if (!pointExistsInCLoud(p1, cloud_sequenced)) { push p1; previousPoint = currentPoint; currentPoint = p1; break; }` — first unvisited among K nearest (K from :68; C01 S0 K=34), **no heading/continuation check**. Second: :163-186, the SFS-T13 second-chance global-nearest jump, likewise heading-blind — the 4 walk-level jumps. Structural proof of guardability: `previousPoint` is written at :85/:99/:155/:184 but **never read by any live condition** — the only reader is the commented-out alternative walk (cf. repo-root edgeline_extraction.cpp:598-619, previousPoint check at :602 commented out). The heading signal the guard needs is already in hand, unused.

**4. Guard proposed (one variable).** Forward-cone same-pass continuation check at :92-103: heading h = currentPoint − previousPoint; among unvisited K candidates accept the nearest with turn <60°, count cone-misses. Validation by T75 (same recipe): CONE arm 402→19 pts, 5.74/0%/1 jump — cone alone shortens but does not land (input holds no full on-contour loop); CONE+presplit+select (SEL n=16, 1.18/100%/zero jumps) **gate GREEN**, E2E C_G 2/2+1/1 ×3 (jobs 33292678/33292704/33292722 COMPLETED 0:0, controls green). No new E2E here per Rules (guard already gated under 75; re-running would duplicate evidence with a concurrent-worker risk).

**5. Honest negative on full-loop recovery (blocking evidence).** No walk-level guard can recover a full C01 lip loop: greedy coverage stalls at 27% on S0 (this ticket, walk level); walk-input ceiling ≤39% on-contour partial arc (71); longest chainable on-contour run 39 pts (74). SEL's 16-pt fragment (75) is the recoverable maximum at this level. Next variable is upstream (mesh→sample density at the lip / boundary-detection input per face), not walk/split/radius/face/smoothing (69/70/71/79/85 exhaust those).

**6. Renders + paths.** artifacts/pota99/C99_C01_stepacross_vs_ORIG.png eye-checked (runs vs gray ORIG ring, black teleport chords at 10/39/191, magenta constriction links, log step profile). Spartan: pota99_repro/{p99_trace.py, p99_render.py, C99_C01_stepacross_vs_ORIG.png}. 39/68/71/74/75/97 lanes untouched (read-only). No prep/assembly source touched; SingleOverlapTest@100 / RP / CheckGraph-150 untouched.

