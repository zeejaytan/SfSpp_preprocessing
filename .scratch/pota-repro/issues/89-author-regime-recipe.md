# 89: Reverse-engineer the author's preprocessing — same/different table + recipe with prediction→check

**What to deliver:** (1) a same-vs-different table: author's inputs vs ours, per property per pot, with the PATTERN each difference follows; (2) the inferred preprocessing recipe (method family + parameters) that explains the author's side; (3) each recipe claim validated by predicting an UNCHECKED author-input property, then checking it.

**Answers:** E1

**Blocked by:** 46 (ready-for-human 2026-10-17: 620-rim fingerprints, uniform 1.8mm resample, segflags gap, teleports/bloat table, recipes R1–R5 untested) + 88 (mechanism-only: author's regime = axis agreement < 0.436 + low coincidence footprint at true seat; S24base in-regime, crest out) + float audit 2026-10-17 (110/129 fresh outlines FLOAT; the perfect split is coverage <50% vs >=50%) + 80 (swap census) + 74 (coincidence mechanism).

**Status:** landed (lead 2026-10-18 — overlays eye-checked by lead; login-node only, no sacct needed)

**Starting position:** Read 46 Results + artifacts/pota46/ first (do NOT redo the fingerprint tables — extend them). Known same: uniform 1.8mm spacing, zero teleports, segment gaps ≤2mm on author side. Known different: segflags (76 ORIG isrim=1 vs all-zero fresh), fresh teleports/bloat, float-vs-track coverage split, axis/coincidence regime on C02/C04. Missing and wanted: (a) author's TRUE-EDGE regime numbers per pot (axis disagreement + coincidence footprint at GT seats — evidence-only distances, never copy points); (b) MESH-MAPPED comparison (author trace drawn on OUR mesh beside our trace on our mesh — the floating-in-space gap); (c) which of R1–R5 (or what new recipe) predicts the author's rim START/END choices, selection among candidate loops, and flag ranges — each claim must predict an unchecked property BEFORE checking it. pristine mesh_processing.cpp + edgeline_extraction.cpp are reference for method family only.

**Rules:** read-only analysis (ORIG inputs evidence-only distances; NOTHING from ORIG copied into any output bundle — ticket-44 asterisk rule); Spartan login-node + small fetches only (never bulk-copy HPC trees); no prep/assembly code changes; no E2E (regime numbers are ruler-side); renders eye-checked (mesh-mapped overlays staged per look-before-trusting); no commits; sacct-direct polling if jobs cut (never scripts/slurm_poll.sh); Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); every fingerprint carries pot/piece/numbers; every recipe claim carries prediction AND check result.

- [ ] Author true-edge regime table (axis + coincidence at GT, per pot)
- [ ] Same/different table with cross-pot patterns
- [ ] Mesh-mapped author-vs-ours overlays, eye-checked
- [ ] Recipe claims with prediction→check pairs
- [ ] Job IDs + sacct states (if any compute)

## Comments (lead landing, 2026-10-18)

Lead review: overlays eye-checked (F-02: fresh Bl_0 tracks author Bl_0 on-mesh — swap confirmed where it matters; E-10: fresh forest chords vs clean author loops — forest confirmed on-mesh). No Slurm jobs (login-node analysis, nothing to sacct-verify). Verdict stands: R-SWAP / R-RESAMPLE / R-FOREST confirmed with pre-registered prediction→check; R-FLAG emission OPEN; regime table honest with the ruler-vs-assembler caveat (author C ruler-axis ~1 yet ORIG C seats — table is same-ruler ORIG-vs-fresh, not 88's axis_angle). C fused stays parked per 79/87. Missing-with-proof list (flag positional rule, multiline-axis semantics, clean-edge regime) is the next-input-work backlog.

## Comments (worker, 2026-10-18 — COMMIT NOTHING; lead to commit)

Verdict: recipe inferred with prediction-check pairs (4 confirmed, 2 rejected-with-mechanism, 1 open with proof of missing). Author regime tabled per pot (288 ORIG + 253 fresh true edges); fresh geometry is mostly RIGHT WALL / WRONG SLOT — under slot-corrected comparison fresh is near-regime everywhere except C. 4 mesh-mapped overlays eye-checked. Zero Slurm jobs (login-node numpy only) — no job IDs to report.

0. Method (read-only; ORIG evidence-only distances, nothing copied). NEW scratch /data/gpfs/projects/punim2657/pota89_repro/ (predictions.md timestamped BEFORE checks; p89_regime.py, p89_recipe.py, p89_p2b.py, p89_render.py; p89_regime_orig.csv, p89_regime_fresh.csv, p89_recipe.csv, p89_flags.csv, 4 overlay PNGs). Laptop mirror artifacts/pota89/ (+ predictions.md, p89_analyze.py, p89_extra*.py). Small-file downloads only. Predictions P1-P6 were written to predictions.md before any check ran; each predicted an UNCHECKED author-input property (interior-first radii, flag z-position, closure distance, turning angle, regime-by-swap-family, length-count identity). No prep/assembly code touched, no E2E, nothing committed. Conventions: GT T = piece-to-global (fwd coincidence far above inv: 0.12 vs 0.00 on A01-A02 control); assembler ReadAxis consumes axis_norm_[0] (data_structure.cpp:146), so ruler uses first axis line; coincidence = share of rim points within 2mm at GT seat, max over the 4 breakline side-pairs (best-pair recorded).

1. Author true-edge regime table (per pot; axis = GT-placed inter-axis angle mod pi, coinc = best-side share).

pot | ORIG edges | ORIG ax_med (max) rad | ORIG coinc_med | FRESH edges | FRESH ax_med | FRESH coinc_med
A | 15 | 0.045 (1.051) | 0.141 | n/a | n/a | n/a
B | 15 | 0.058 (0.454) | 0.183 | 15 | 0.054 | 0.158
C | 5 | 1.058 (1.269) | 0.253 | 5 | 0.271 | 0.027
D | 69 | 0.066 (1.415) | 0.133 | 69 | 0.059 | 0.097
E | 62 | 0.054 (1.504) | 0.175 | 62 | 0.045 | 0.155
F | 9 | 0.063 (0.090) | 0.160 | 9 | 0.060 | 0.136
G | 10 | 0.041 (0.083) | 0.226 | 10 | 0.040 | 0.225
H | 17 | 0.789 (1.559) | 0.188 | n/a | n/a | n/a
I | 65 | 0.045 (1.133) | 0.125 | 65 | 0.047 | 0.137
J | 21 | 0.706 (1.562) | 0.150 | 21 | 0.617 | 0.129

Full per-edge rows in p89_regime_orig.csv (288) + p89_regime_fresh.csv (253). Assembler-side anchor (ticket 88, C02-C04 only): S24 true axis 0.2862/area 2.0 vs crest 1.17-1.42/area 165-170 — ruler-side proxy is NOT the same metric (author C02-C04 ruler axis 1.06-1.27 rad yet ORIG C seats 4/4+5/5), so the table is ORIG-vs-FRESH same-ruler, calibrated by 88 on C. Fresh Bl_0-vs-Bl_0 uncorrected collapses everywhere (B 0.096, C 0.003, D 0.040, F 0.046, J 0.030); slot-corrected best-side matching recovers near-regime (table above) EXCEPT C (0.027 vs 0.253 — fused/shredded, stays with 79). G fully in-regime (0.225 vs 0.226).

2. Same/different table (extends 46 + 80; pot/piece/numbers throughout).
SAME — S1 closed uniform resample: P3 closure <=2mm 163/163 ORIG Bl_0 (all pots A-J); P6 length = n x 1.8mm within 5pct 163/163; start arbitrary (closure about equals joint gate). S2 contact-side convention: author best-pair 00:174 / 11:108 / mixed:6 of 288 (same-side loops 98pct). S3 interior-first slots: P1 ORIG S0<S1 axis-radius 157/163 (96.3pct; violators C-03 H-04 I-25 J-03 J-08 J-14). S4 axis geometry preserved: fresh-vs-ORIG same-edge axis-delta med 0.01-0.02 rad on single-line pieces. S5 meshes: fresh bundle Mesh OBJs byte-identical to source (F02/E10/C02/B03 size-equal — our mesh IS the shared mesh).
DIFFERENT — D1 slot swap (re-census 94 SWAPPED / 19 CLEAN / 16 FOREST of 129, cf 80: 94/17/14): P1b fresh-S0 approx ORIG-S1 within 2mm on 94/94 swapped; edge-level flip census 159/256 shared edges change best-pair (ORIG 00-heavy to fresh 11-heavy 159 + mixed 39). D2 forest/teleports (46 D1-D2; E10 overlay: 750-pt red spans both loops + chords). D3 flags: 105 author files flagged both sides (s1-side 52/105; topflags 1 / +-2 / -3; 95 isrim=1 segments) vs all-zero fresh; positional z-rule REJECTED (P2 mesh-extreme 28/73; P2b rim-extreme 8/73) — emission rule stays open, side/piece-identity is the lead. D4 step 1.905 vs 1.8 (46). D5 fresh axis gaps: C03 axis file EMPTY (0 bytes, assembler reads 0 axes); fresh C01/C02/C04 multiline axes. D6 author axis quirk: about 40 multiline author axis files; C/H/J pot-level axis medians 0.7-1.1 rad (C02's two lines differ by ~60deg+) — axis-based criteria must be line-aware. D7 Pot C ships 6 pieces of breaklines, graph covers 4 (05/06 extra-fragment data).

3. Recipe (method family + parameters; every claim has prediction + check).
R-SWAP CONFIRMED (P1 96.3pct + P1b 94/94 + 159/256 flips): author Bl_0 = interior-wall loop, Bl_1 = exterior; our chain's size-desc sort puts exterior first without the T04 guard. Fix: T04 guard / slot exchange (hands to 78 swap arm); predicts coincidence recovery with NO reordering. R-RESAMPLE CONFIRMED (P3+P6 163/163): closed uniform 1.8mm resample, arbitrary start. Fix: R3 (1.8 + uniformity gate). R-FOREST CONFIRMED (overlays + D1): unordered decorative appends spanning both lip loops. Fix: R1 order+clip + 78 SEL. R-FLAG mechanism confirmed (46 code sites) but EMISSION RULE OPEN (P2/P2b rejected): fix R2 needs a mouth/base detector, not a z-threshold. R-SMOOTHNESS downgraded to note (P4 138/163 within-segment <90deg): path corners survive resampling while normals stay smooth (46 ndot) — expected, not a defect. MISSING (measured proof): flag positional rule (z rejected both frames); multiline-axis line semantics (assembler uses line 0; author's extra lines uninterpreted); clean-edge regime (only 3 fully-clean fresh edges exist: G02/05 0.76, B04/06 0.74, G05/07 0.12 — underpowered by construction, not by method).

4. Mesh-mapped overlays (eye-checked by worker; author-black / author-blue / fresh-red on shared mesh, TOP+SIDE). artifacts/pota89/p89_F_02_overlay.png — red fresh Bl_0 coincides with blue author Bl_1 exactly, black author Bl_0 a distinct smaller loop (swap, seen on mesh). p89_E_10_overlay.png — 750-pt red spans both author loops plus long straight teleport chords (forest). p89_C_02_overlay.png — red partly follows author loops but cuts interior chords + extra right-side branches (fused/doubled, 79's case). p89_B_03_overlay.png — CLEAN control: red follows black with local spurs (230 vs 143 pts — even clean pieces carry extra content). Spartan twins in pota89_repro/.

5. Jobs: none — login-node python/numpy/matplotlib only, read-only bundles. No sacct states to report. No other tickets' paths touched; 39-88 read-only kept.
