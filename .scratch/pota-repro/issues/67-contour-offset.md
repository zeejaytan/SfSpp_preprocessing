# 67: Prep-stage diagnosis of the contour offset

**What to deliver:** the binding walk defect behind the ~5-6mm doubled-back fresh contours — and the repair direction.

**Answers:** E1

**Blocked by:** 66 (true reorder NULL ×3: jumps→0, gate unmoved, E2E 0/3+0/3 bit-identical; fresh C01 402 pts doubled-back vs ORIG 211 clean loop, ~5-6mm off; content binds, order was co-symptom; jobs 33277750/33278681/33278682 COMPLETED) + 64 (teleports ≤113mm same pieces) + 26/27 (A's teleports were ordering-only and cured; C's are content — different disease, same symptom).

**Status:** results-in — DOUBLED LOOP bound (two parallel lip-edge loops chained; ordering-null explained; screening-only, no new jobs)

**Starting position:** our rim walk emits a contour that folds back on itself (nearly 2× the authors' point count) and sits millimetres off theirs. Suspect the walk steps off the rim onto wall/spur and back (T14 decorative-append family? RegionGrowing fusion family per ticket 21? second-surface pick per Pot B?). Fresh-only diagnosis on the C pieces; ORIG evidence-only (44-asterisk rule). Bundle references: pota66 re-walked bundle + pota39 C bundle (read-only).

**Rules:** diagnosis FIRST with login-node screening; E2E only to confirm a mechanism; no commits; sacct-direct polling; Comments-only ticket edits; renders (eye-check); no gate relaxation without a mechanism.

- [x] Where the walk steps off (which stage, which decision)
- [x] Why A was ordering-only but C is content (what differs)
- [x] Repair direction with a predicted observable
- [x] Job IDs + sacct states (or explicit screening-only)

**Successor:** the repair ticket 67 names; roll wherever doubled contours recur (E/I/J forests dwarf ORIG).

## Comments (worker, 2026-10-17 — COMMIT NOTHING; lead to commit)

**Verdict: walk defect bound — the C rim walk chains TWO parallel lip loops (inner + outer lip edge, ~5mm apart) into one Breakline_0 file. Ordering repairs (65/66) were provably null because no permutation collapses two offset loops into one. Category 1 stands with the mechanism refined: content disease (second loop), not order disease. Screening-only; no new jobs.**

**0. Method (login-node screening, T53/T64 precedent; E2E unneeded — T66's 33277750/33278681/33278682 COMPLETED null stands as the evidence this diagnosis explains).** Fresh = `/data/gpfs/projects/punim2657/pota39_repro/prep/pota39_bundle_C/SfS_pp` (read-only); ORIG = `sfs_main/original_samples/SfS_pp` (evidence-only distances — zero ORIG points in any analysis output that feeds a fix, 44-asterisk rule kept); A control = `sfs_preprocessing_pota27/pota27_bundle` (cured) + T27 records. Work dir NEW `/data/gpfs/projects/punim2657/pota67_repro/` (script `rh_profile.py`); 39/65/66 lanes untouched.

**1. Where the walk steps off (stage + decision, `edgeline_extraction_headless.cpp`).** PCL `BoundaryEstimation` (fixed r=4mm, angle 0.6π) admits BOTH lip faces as boundary → `getPointsInSequence` (:814) greedy K=50 nearest-neighbour chaining with no heading/component guard steps across the ~5mm inter-loop gap at fold-touch points and concatenates disjoint components into one file (`num_components` counted, then ignored) → sphere-march resample preserves both loops → `detectSeparateLineSegments` cuts at curvature peaks but keeps everything → Breakline_0 = doubled contour (flags all 0 → binary reads the full file). Dead-filter note: the `RadiusOutlierRemoval` result is computed, saved to `cloud_Filtered.pcd`, then reloaded-over with raw `boundary.pcd` — the one filter that could have dropped the sparser loop is dead code in effect (same for all pots: enabler, not the A/C difference).

**2. Numbers (fresh-only derivation + evidence-only ORIG distances, ORIG-axis frame).**
- C01 (402 vs ORIG 211): run2 (152) + run3 (211) cover the SAME angular sector as ORIG's arc (bins {0,1,2,11} + {0-4} vs ORIG {0,1,2,3,4,11}), each ~5.5mm off ORIG (run2→ORIG med 5.45, run3→ORIG 5.76), 38mm apart from each other (opposite sides of the doubled ribbon, touching at fold points — hence T66's ≤1.9mm endpoint links). Plus 29-pt cross-mouth spur (run1) + 10-pt frag (run0). Two full-arc parallel loops, not one loop + appends.
- C04 (191 vs ORIG 131): run0 (134) tracks a curve PARALLEL to ORIG at constant ~5.5mm 3D offset (symmetric both directions), +4.5mm radial ≈ one wall thickness (T53: 3–5mm) — the outer-lip-edge loop; run1 (48) folds back ON run0 (run1→run0 med 0.87) — literal doubling-back; run2 (9 pts) sits on ORIG.
- C03 (control): single on-contour arc (run meds 0.7/1.0mm, 100/83% <2mm) — presents one loop; fails via neighbours (T66). C02: all runs ~6mm off (267 vs 221); fresh axis garbage (cos −0.49) — same doubled-loop disease + finder-caused axle miss (T66 stands).
- A-p3 control (cured bundle): 146 pts, ZERO jumps, same 3 angular bins as ORIG, fresh→ORIG med 0.64mm, 100% <2mm. Pre-cure (T27 §1): appends 70–90% <1mm of ORIG — on-curve.

**3. Why A differs from C.** A's extra boundary content (T14 decorative arcs) lay ON the true wall surface — redundant on-curve points; the disease was purely interleaved ORDER, so re-walking cured it. C's extra content is a SECOND, OFFSET full-arc loop (outer lip edge, one wall-thickness out) sharing no points with the true lip — a parallel contour no permutation can merge. What differs physically: C fragments present two lip-edge loops to the fixed-r estimator (small pot, lip-thickness face sampled in Surface_0 — second-surface pick, Pot-B-ticket-44 family); A presented one lip loop + on-surface arcs. Refuted for C: T14-append family (extra content is full-arc, not localized arcs); slipped-down-wall-ring (offset constant/parallel at same heights, not height-dependent); frame shift (centroid alignment worsens it — T66; r-h profiles overlap in h, shift in r).

**4. Repair direction + predicted observable.** Split-then-select BEFORE sequencing: (a) break the boundary cloud into connected components at >5mm gaps and emit ONE loop per component (the counter already exists — stop concatenating); (b) forward-cone guard in the K=50 stepper so the walk can't step sideways onto the parallel loop at touch points; (c) select the inner loop per piece (lip-face rule TBD by successor's first probe: Surface_0/1 standoff test for which loop sits on the sampled face edge — 44-asterisk-safe, no ORIG). Predicted observable: Bl_0 count ≈ ORIG (C01 ~211, C04 ~131 — the counts are already IN the file as run sizes), consecutive jumps → 0 with NO reordering (each loop is internally clean), fresh-vs-shipped median (evidence-only) ~5.6 → ~1–2mm, gate per-edge recovery toward ORIG 34–73 scale, forest/pruned 350/20 back toward 125/40. Successor's first probe: Surface_0 inclusion test (does Surface_0 contain the outer-face strip near the lip? decides outer-edge vs wall-ring provenance) + RegionGrowing-fusion check per T21.

**5. Renders (eye-checked).** `artifacts/pota67/Pot_C_Piece_01_rh.png` (r-h: two offset loops + cross-mouth spur vs gray ORIG; 3D overlay with black teleport chords at the jumps); `artifacts/pota67/Pot_C_Piece_04_rh.png` (r-h: red loop parallel to gray at +4.5mm radial, blue fold-back on red, green on-ORIG nub); `artifacts/pota67/Pot_C_Piece_03_rh.png` (single on-contour arc — staged, corroborates T66's clean-arc render). Script `pota67_repro/rh_profile.py`.

**6. Jobs: screening-only, none cut — no sacct IDs.** T66's 33277750/33278681/33278682 (all COMPLETED 0:0, polled directly) stand as the ordering-null evidence.

**Successor:** the split-then-select repair ticket this diagnosis names; roll the two-loop check (fresh count ≈2× ORIG + parallel-loop r-h) wherever doubled contours recur (E/I/J forests dwarf ORIG).

**Corroboration (conservator eyewitness, 2026-10-18):** independently witnessed a breakline trace jumping across to another break edge after finishing its own — the face-hop mechanism confirmed by eye, classified as a preprocessing bug requiring fixing.
