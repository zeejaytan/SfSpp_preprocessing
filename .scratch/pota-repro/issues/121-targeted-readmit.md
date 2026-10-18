# Targeted re-admission — keep the 8 arc dots, none of the wall

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 120 (ROR-3 trade: +9 arc for 9 wall junk, gate 4.85; 8 on-arc newly-kept in p120_newX.npy, seats 26/31/33/50/94) + 109 (curvature separates inverted: lip curved vs flat — candidate rule) + 119 (7 void spans) + 103 (cleaned bag, gate 4.68)

**Status:** results-in

**What to deliver:** ROR-6 stays (load-bearing), plus targeted re-admission of the arc dots it wrongly deletes. MEASURE FIRST: do the 8 on-arc dots separate from the 9 wall-junk dots on a stated feature — pipe curvature (109's split: arc curved vs wall flat?) or seated-distance-to-local-arc or neighbour-count band — rule stated before running. Then build the re-admitted bag (ROR-6 + rule-kept dots) and walk + gate it (plain greedy K34+T13, pre-registered, same both arms). Success bar (all must hold): uncovered ORIG count below 119's 32 AND newly admitted junk ~0 (admitted dots majority within 5mm of ORIG) AND gate at/below 4.68mm AND walk >=197 pushes. If no clean separating feature measures (overlap like 106/108), refute fast with the overlap numbers — that says the 8 must be grown mesh-side, not filtered.

**Starting position:** .scratch/pota120_repro/ (p120_newX.npy: 8 on-arc seats; junk seats; ROR-6 port), pota103/109/119_repro/ (cleaned bag, curvature values, void spans). Login-node numpy only — no Slurm, no E2E. New scratch pota121_repro/; render under laptop artifacts/pota121/ (admitted dots coloured by feature value, voids before/after, walk vs control).

**Rules:** control reproduces ROR-6 bag first (270, gate 4.68) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; feature-measured-then-rule-stated.

- [ ] Feature measured (8 arc vs 9 wall separation or overlap)
- [ ] Rule stated, re-admitted bag (admission accounting, junk count)
- [ ] Walk + gate vs full bar
- [ ] Verdict + recipe or overlap refutation

## Comments (worker, 2026-10-18 — OVERLAP REFUTATION; laptop numpy only; COMMIT NOTHING; lead owns checkboxes)

**Verdict: REFUTED as a landing recipe — no clean separating feature measures (overlap like 106/108). ROR-6 stays; the on-arc dots must be grown mesh-side (densification at void-span arc positions), not filtered.**

**0. Control GREEN (all four checks, read-only inputs, zero ORIG points, Bl_0 gate-evidence only).** ROR-6 port (self-inclusive keep>=6, p120 recipe verbatim): kept 343, ORDERED-EXACT vs pipe bagP (atol=1e-4). Coord-minus-ROW40 == staging 270 (0/0 diff, licensed). Walk (plain greedy K=34 + SFS-T13, pre-registered): 93/197, 4 jumps at (92,93)/(126,127)/(164,165)/(183,184), stall [-27.26,1.05,388.81]. Gate med 4.68, <2mm 29.9%, gaps5 39, maxstep 67.0, ORIGcov 83/211. Matches p120_numbers.txt CONTROL270 line exactly.

**1. Accounting correction to 120's prose.** Recomputed from p120_newX.npy + Bl_0 seating (TF/TO recipe verbatim): sorted seat dists [0.38,0.38,0.52,0.57,1.52,4.12,6.35,8.37,8.37,11.57,31.44,33.89,42.70,45.04,46.66,47.07,47.96] — **6/17 slots (5 unique seats 26/31/33/50/94; seat-33 dup) within 5mm**, agreeing with p120_numbers.txt "6/17". 120's Comments prose "8/17 slots (6 unique)" is a counting slip; the numbers file stands. Junk = 11 slots: 5 high-wall 42-48mm off-arc (near seats 84/106/107), 2 seat-17 (31-34mm, one 2.24mm from a ROW40 coord), 4 fringe (seats 27/170/180x2, 6.4-11.6mm).

**2. Feature separation (ORIG-free features; ORIG-seat used as accounting label only).**
- F1 cnt_self (ROR self-inclusive count): arc {3,4,4,4,5,5} vs junk {3,3,3,4,4,4,4,4,5,5,5} — COMPLETE overlap.
- F2 d_arc (dist to nearest ROR-6-kept dot, local-arc seating): arc [3.55,4.25,5.27,5.27,6.45,6.45] vs junk [2.24,2.51,2.51,2.81,5.16,5.84,6.49,6.70,9.87,13.02,13.84] — arc range FULLY INSIDE junk range.
- d_ROW40 (bag-internal): arc all >=37.9 vs junk [2.24..68.24] — overlap both ends.
- Pipe curvature (109's split): NOT measurable on laptop — SampledWithNormals.ply lives on Spartan (/data/gpfs/.../pota39_C, outside login-node scope and the listed starting position), and 109's own evidence argues against a clean rule: 10/40 ROW40 unique coords fall INSIDE the LIP curvature band [0.04521,0.16057] (5 ROW40 survivors kept by the band rule) — wall dots near the lip already pass the band, so fringe/second-row junk would plausibly survive it too. No clean rule statable.
Per-slot table (slot|cnt|d_arc|d_ORIG|seat|d_ROW40): 0|3|5.27|4.12|94|51.81; 1|4|9.87|47.07|84|9.87; 2|4|13.02|46.66|106|13.02; 3|5|6.49|45.04|84|6.49; 4|4|13.84|47.96|107|13.84; 5|3|5.16|42.70|84|5.16; 6|3|6.70|33.89|17|6.70; 7|5|2.24|31.44|17|2.24; 8|5|2.81|6.35|27|40.46; 9|4|5.27|1.52|50|38.93; 10|4|2.51|8.37|180|68.24; 11|4|2.51|8.37|180|68.24; 12|3|5.84|11.57|170|67.52; 13|5|4.25|0.52|31|43.00; 14|5|3.55|0.57|26|37.92; 15|4|6.45|0.38|33|41.10; 16|4|6.45|0.38|33|41.10.

**3. Rule candidates evaluated in-silico (every statable rule fails the ~0-junk leg):** cnt>=4 keeps arc 5/6 + admits junk 8/11; d_arc<=5 keeps 2/6 + admits 4/11; d_arc in [3.5,6.5] keeps 6/6 + admits 3/11; d_ROW40>35 keeps 6/6 + admits 4/11 (seats 27/170/180x2); best 2-feature box (d_arc in [3.5,6.5] AND d_ROW40>35) still admits 1 junk (slot 12, seat-170) — and is an overfit box on 17 points with no mechanism. No rule meets "newly admitted junk ~0", so no test-arm walk was run (refutation per brief: overlap numbers are the deliverable; a junk-carrying bag cannot meet the all-must-hold bar).

**4. Walk + gate vs full bar.** Control only: 197 pushes / 4.68mm (green above). Test arm: NONE — no rule qualified. Uncovered ORIG stays at control's 32 (119's count, recomputed identical); no re-admitted bag built.

**5. Recipe: NONE at filter level.** Direction stays mesh-side: densify sampling at the 7 void-span arc positions (119 extents) so chainable lip dots exist there at ROR-6 — same landing direction as 120's verdict. Next ticket should own void-span-targeted densification, not another filter.

**6. Paths.** Scratch .scratch/pota121_repro/ (p121_measure.py/txt, p121_feat.npy, p121_control.py/txt, p121_render.py). Render artifacts/pota121/p121_overlap.png (eye-checked: PCA-2D coverage + newX coloured by d_arc with on-arc rings | F1xF2 overlap scatter). Tickets 39-120 untouched (read-only); COMMIT NOTHING done.

