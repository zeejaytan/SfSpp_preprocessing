# 80: Float-cause diagnosis (cross-pot)

**What to deliver:** the upstream mechanism that floats whole rims 5-9mm + a fix recipe per cause.

**Answers:** E1

**Blocked by:** float audit 2026-10-18 (110/129 fresh Bl_0 float >2mm, 19 track; floaters share coverage<50% NOT teleports; D/E/I float nearly whole-pot at uniform 5-9mm systematic offset; B01 masked subset tracks 0.73mm/100% — author position survives inside floaters; full 129-row table in parent session) + 67 (C doubled-loop bound: greedy K=50 no heading guard; enabler PCL BoundaryEstimation r=4mm) + 74 (C01 no walkable branch; frame exonerated, search sound) + 46 (ORIG recipe: uniform 1.8mm resample, zero teleports).

**Status:** results-in (worker 2026-10-18 — SLOT-SWAP bound as the dominant cross-pot cause; FOREST second; see Comments)

**Starting position:** the audit table says WHERE (per-piece float-med/coverage/teleports, bundle paths: fresh /data/gpfs/projects/punim2657/pota39_repro/prep/pota39_bundle_{B,C,D,E,F,G,I,J}/SfS_pp/Breaklines/, ORIG sfs_main/original_samples/SfS_pp/Breaklines/, teleports in artifacts/pota46/p46_fingerprints.csv). Find WHY at the walk level: what picks the wrong loop — boundary-estimator output (69 showed offset upstream of walk)? face assignment (T21 RegionGrowing fused walls)? loop-count-vs-placement (70)? sampling? — one variable each, whole-pot D/E/I shifts first (systematic = one cause), then mixed-pot piece families. Read-only diagnosis on the login node first (no Slurm until a cause names a fix); ORIG evidence-only (distances, never points into fixes).

**Rules:** land with per-family cause bound (which stage emits the off-loop, with the code site) + fix recipe per cause handed to the fix lane (79 owns C02/C04 shape, 78 owns guard roll-out — this ticket diagnoses, fixes land there or in a named successor); renders (eye-check) of the mechanism (r-h or mesh-mapped where the wrong loop is picked); no commits; sacct-direct polling if jobs are cut; Comments-only ticket edits; E1 entry only via lead.

- [ ] Whole-pot-shift cause (D/E/I 5-9mm systematic) bound to a stage + code site
- [ ] Mixed-pot families bound (which pieces float which way, shared trait beyond coverage)
- [ ] Fix recipe per cause (repair ticket or hands to 78/79)
- [x] Whole-pot-shift cause (D/E/I 5-9mm systematic) bound to a stage + code site
- [x] Mixed-pot families bound (which pieces float which way, shared trait beyond coverage)
- [x] Fix recipe per cause (repair ticket or hands to 78/79)

## Comments (worker, 2026-10-18 — COMMIT NOTHING; lead to commit)

**Verdict: the dominant cross-pot float cause is a surface/breakline SLOT SWAP, not the walk. Fresh Surface_0/Bl_0 carry the author's Surface_1/Bl_1 content (exterior wall) on ~94/129 pieces. The rim walk faithfully traced the wrong wall's loop. Second cause: the T67 doubled/forest walk defect (~14 pieces). Combined they explain ~108/129; the 19 tracking pieces are exactly the unswapped ones (plus B01 masked-subset).**

**0. Method (login-node screening only; zero Slurm jobs; no code touched; ORIG evidence-only distances).** Fresh = pota39_bundle_{B,C,D,E,F,G,I,J} (read-only); ORIG = sfs_main/original_samples (evidence-only NN distances). Work dir NEW /data/gpfs/projects/punim2657/pota80_repro/ (2 PNGs); 39/78/79 lanes untouched. Laptop copies artifacts/pota80/F02_swap.png + E10_forest.png (local-only, uncommitted).

**1. Family table (full 129-piece fresh-Bl_0 vs ORIG Bl_0/Bl_1 NN median, r=count ratio, j=jumps>5mm; CLEAN=v0<2, SWAPPED=v1<2, FOREST=r>=1.4+j>=1 tracks neither):** SWAPPED ~94 (B02,B05,B07,B09; C02,C04; D 24/29; E 25/31; F02-F07; G01,G03,G04,G06; I 22/30; J04-J07,J10-J12); CLEAN ~17 (B03,B04,B06,B08; C03; D21,D22,D28,D29; F01; G02,G05,G07; I10,I25,I30; J01,J03,J08); FOREST ~14 (B01; C01; D12,D14; E06,E07,E08,E10,E15,E18; I06,I13,I19,I28; J02,J09). Swap census on surfaces agrees: fresh-S0 matches ORIG-S1 better than ORIG-S0 on B 8/9, C 2/4, D 26/29, E 29/31, F 6/7, G 6/7, I 28/30, J 9/12 — and the pieces that TRACK are exactly the non-swapped ones (D22/D28/D29, F01, G07, I25/I30, J01/J03/J08, C03, B01-masked). Author convention is interior-first (ORIG S0 = smaller-radius inner wall, e.g. F02 19.7 vs 23.28).

**2. Stage bind (SWAPPED family): surface ORDER assignment, upstream of the walk.** Size-desc sort (mesh_processing_headless.cpp:218 comparator, applied :1680, clusters[0]→Surface_0) puts the denser-sampled wall first — on these pots the EXTERIOR wall (faces the scanner). The T04 interior-first exchange guard (original_nurbs_preprocessing/edgeline_extraction_headless.cpp:3692, ticket04_interior_first.cpp) never reconciled them: ZERO SFS-T04 lines in prep/EdgeLineExtraction.log — the t39 pipe ran without it. Walk-level evidence of innocence: SWAPPED pieces are clean single loops (F02-F07, E22/E24/E26/E30/E31, J10-J12, D18/D20/D23-D25/D27 all j=0, r≈1.0) — nothing to chain, so the walk cannot be the defect. Fresh Bl_0 vs ORIG Bl_1: F02 0.69, E22 0.56, J10 0.63, D01 1.20, B07 0.61mm.

**3. Stage bind (FOREST family): the T67 doubled-loop walk defect on a swapped base.** Fresh Bl_0 tracks NEITHER author loop, r 2-6x, j 4-26 (E10 r=5.6/j=18, D12 r=4.53/j=21, J02 r=5.84/j=24). Eye-check E10_forest.png: red fresh cloud spans both gray-inner and blue-outer loops plus scatter — BoundaryEstimation admits both lip faces + getPointsInSequence greedy K=50 no heading guard chains them (edgeline_extraction_headless.cpp:806/:921/:1034, per 67). Sub-case I10/J03/B01: doubled content WITH an on-lip branch (masked-subset tracks) — in-file select may suffice (78 SEL recipe).

**4. Eye-checks:** F02_swap.png — red fresh Bl_0 overlays blue ORIG Bl_1 exactly (top + side views), gray ORIG Bl_0 a distinct smaller loop. E10_forest.png — red fresh spans both author loops + scatter. Both inspected via laptop copies.

**5. Fix recipes (hands to 78/79 or named successor; no E2E from this ticket — diagnosis only):** (a) SWAPPED ~94 pieces: re-run edge WITH the wired T04 guard (or slot-exchange S0↔S1 + Bl_0↔Bl_1 in scratch) on one small pot first (F: 7 pieces, 6 swapped + F01 control); gate = fresh Bl_0 vs ORIG Bl_0 <2mm + jumps→0 with NO reordering (files are already clean loops — expect near-free cure); then E2E ×3. Hand to 78 (guard roll-out) as the swap arm. (b) FOREST ~14 pieces: 78 SEL recipe (split-then-select + inner-loop select + forward-cone guard); I10/J03/B01 try in-file select first. (c) C02/C04 rim-shape stays with 79 (C02 fresh-S0 matches NEITHER author wall at 5.7mm — fused surface, T21 family — swap alone will not cure it; C04 marginally swapped 4.65 + doubled). (d) If T04's vote misfires on any swapped piece (axis/normal input), that names a T04-vote ticket as successor.

**Jobs:** none (screening-only per Rules — no cause named a fix until this report). All numbers above are login-node python (numpy only) over read-only bundles.
