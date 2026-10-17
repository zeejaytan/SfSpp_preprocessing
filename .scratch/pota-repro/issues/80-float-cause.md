# 80: Float-cause diagnosis (cross-pot)

**What to deliver:** the upstream mechanism that floats whole rims 5-9mm + a fix recipe per cause.

**Answers:** E1

**Blocked by:** float audit 2026-10-18 (110/129 fresh Bl_0 float >2mm, 19 track; floaters share coverage<50% NOT teleports; D/E/I float nearly whole-pot at uniform 5-9mm systematic offset; B01 masked subset tracks 0.73mm/100% — author position survives inside floaters; full 129-row table in parent session) + 67 (C doubled-loop bound: greedy K=50 no heading guard; enabler PCL BoundaryEstimation r=4mm) + 74 (C01 no walkable branch; frame exonerated, search sound) + 46 (ORIG recipe: uniform 1.8mm resample, zero teleports).

**Status:** ready-for-agent

**Starting position:** the audit table says WHERE (per-piece float-med/coverage/teleports, bundle paths: fresh /data/gpfs/projects/punim2657/pota39_repro/prep/pota39_bundle_{B,C,D,E,F,G,I,J}/SfS_pp/Breaklines/, ORIG sfs_main/original_samples/SfS_pp/Breaklines/, teleports in artifacts/pota46/p46_fingerprints.csv). Find WHY at the walk level: what picks the wrong loop — boundary-estimator output (69 showed offset upstream of walk)? face assignment (T21 RegionGrowing fused walls)? loop-count-vs-placement (70)? sampling? — one variable each, whole-pot D/E/I shifts first (systematic = one cause), then mixed-pot piece families. Read-only diagnosis on the login node first (no Slurm until a cause names a fix); ORIG evidence-only (distances, never points into fixes).

**Rules:** land with per-family cause bound (which stage emits the off-loop, with the code site) + fix recipe per cause handed to the fix lane (79 owns C02/C04 shape, 78 owns guard roll-out — this ticket diagnoses, fixes land there or in a named successor); renders (eye-check) of the mechanism (r-h or mesh-mapped where the wrong loop is picked); no commits; sacct-direct polling if jobs are cut; Comments-only ticket edits; E1 entry only via lead.

- [ ] Whole-pot-shift cause (D/E/I 5-9mm systematic) bound to a stage + code site
- [ ] Mixed-pot families bound (which pieces float which way, shared trait beyond coverage)
- [ ] Fix recipe per cause (repair ticket or hands to 78/79)
