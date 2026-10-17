# 55: Rim lateral position — walk the sheet edge, not the mid-wall

**What to deliver:** a B-p2 rim path that rides the sheet edge like ORIG — valid thickness, honest strengths, E2E lift.

**Answers:** E1

**Blocked by:** 54 (wall sits ON ORIG sheets NN 0.34mm — innocent; OUR rim runs mid-wall ~1.1mm off ORIG rim at GT seating, bad-thickness flags idx 1-186; smooth/swap/flip/trim measured-dead) + 50 (length settled; position still wrong) + 48 (T48b direction-mirror pipeline).

**Status:** results-in (worker 2026-10-17, COMMIT NOTHING)

**Starting position:** the walk must move LATERALLY (across the wall to its edge), not along length. Candidates: seed the walk at the sheet edge (edge-aware initialization from surface geometry), edge-seeking walk cost (prefer rim points at sheet boundary), post-walk lateral snap (project rim rows onto the sheet edge, honestly — same material, corrected position). Constraint from 50: do NOT resample rim spacing (matcher keys off raw sampling). Render reference: artifacts/t54_anatomy.png (ORIG rides edge, ours cuts mid-sheet + top loop). Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only.

**Rules:** land ONLY with rim-on-edge recovery (per-index GT-seated distance toward ORIG) AND/OR valid-thickness recovery AND/OR honest strength lift AND/OR E2E lift ×3 same-binary runs + controls green (B ORIG 9/9+15/15, A 8/8+15/15) in same runs + gates green; renders (eye-check); prep-side scratch copies; assembler E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition.

- [x] Lateral-position arms, one variable each
- [x] Edge-riding proof or measured why-not
- [x] Job IDs + sacct states

## Comments (worker, 2026-10-17, COMMIT NOTHING)

**Bottom line: measured why-not — no lift. The rim walk is not the binding defect: placing OUR p2 rim at the TRUE ORIG edge positions (native-frame nearest-ORIG cheat, diagnostic-only, zero ORIG points in any fix) still gives 107-119/187 valid thickness med 0.85-1.68 vs ORIG 146/150 med 2.90, because OUR Surface_1 crowds the lip (standoff 0.73 at true positions vs ORIG 2.87). Perfect positions are the upper bound of ANY walk/rewalk/snap arm — all three ticket candidates (edge-aware init, edge-seeking cost, lateral snap) are predicted-dead by this bound, and the four honest snap estimators screened all moved metrics flat-to-worse. The defect is the SURFACE lip shape (T21-class regeneration), not the rim path. No E2E spent where measurement already rejects (T53 precedent); no Slurm jobs (login-node numpy screening only).**

**Edge-riding deficit proven numerically (OUR-only geometry, ORIG as evidence metric):** fractional lateral position of rim within local wall row — ORIG med 0.87, 57% at edge, q10 0.75 (hugs one side); OURS med 0.62, 26% at edge, spread q10-q90 0.13-0.86 (mid-sheet wander). Cross-section renders confirm: last segment (rows 155+) both ride the sheet end; mid-run OUR sits ~1-1.5mm lateral off ORIG; OUR/ORIG walls coincide (T54 composition stands).

**Honest arm screening (all OUR-side only, count/order preserved, no resampling; thickness = numpy GetThickness replication, GT-dist = evidence-only):**
- NORMAL-SHIFT (rim along -normal, δ 0.5-2.0): REFUTED — valid 124→90 at δ=0.5, med falls, GT-dist worsens. Correction is not along normals (moves off-sheet, rays miss).
- BOUNDARY-SNAP (per-point binormal snap to density-boundary, side-vote/flip, α/cap variants): REFUTED — valid 112-120, standoff flat/worse, GTmed 1.08→1.15-1.27. Segment median corrections ≈0: density boundary is holes/noise, no coherent lip edge.
- LIPSNAP (OUR-only lip-side oracles: beyond-window + density-falloff; snap to frac 0.85/1.0): REFUTED — beyond-oracle ties 120/187, density-oracle splits 110/75 (no consensus side); best variant 123/187 med 1.71 standoff 0.67 GTmed 1.16; F=1.0 collapses to 82 valid. Wall is ~10mm wide locally; rim sits deep interior, no 1mm-scale OUR-only edge direction exists.
- CHEAT upper bound (diagnostic, never a fix): a=0.5 → 124 valid med 1.54 standoff 0.86; a=1.0 + old normals → 107 med 0.85; a=1.0 + surface-fit normals → 119 med 1.68, standoff 0.73. ORIG self-check 146/150 med 2.90 on same code path. Even TRUE positions + refit normals recover nothing — the surface lip shape, not rim position, binds.

**Renders (eye-checked):** `SfSpp_preprocessing/artifacts/t55_edge.png` (rim vs S1-edge tube, 3 views — rim threads the band, edge incoherent), `SfSpp_preprocessing/artifacts/t55_xsec.png` (8 cross-sections with ORIG walls/rim overlaid evidence-only — good end segment vs mid-run lateral offset vs loop region).

**E2E/strength:** none — no arm moved offline joint metrics; T54 already showed veto-silence doesn't admit the edge. Controls/gates N/A (no bundles staged).

**Job IDs + sacct:** none — offline screening only, login-node numpy (same basis as T53/T54 gate scripts). No sbatch submitted, nothing to poll.

**Successor:** B-p2 Surface_1 LIP-SHAPE regeneration (the wall interior is registered to 0.34mm; only the lip-end shape is wrong — reshape/extend S1 at its edge so the standoff structure exists, then re-seat the existing T50 rim). Scratch point surgery is exhausted on this piece: sequence/50, sampling/49-R3, column-7/52, normals/52-53, smooth/swap/flip/trim/54, lateral-snap/55 all measured-dead. Work dir `/data/gpfs/projects/punim2657/pota55_repro/` (explore/sweep/edge/snap/lipsnap/cheat/xsec/frac/render scripts + t55_edge/t55_xsec PNGs); tickets 49/50/51/52/53/54 + p47/p49 flaggers untouched (read-only).

**Successor:** cross-pot generalization of the B recipe (C–J share the drowning shape).
