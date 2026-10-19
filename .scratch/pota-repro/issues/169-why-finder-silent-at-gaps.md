# Why is BoundaryEstimation silent at the gap stations?

GOAL: NAME THE MECHANISM THAT SUPPRESSES EMISSION AT EACH COVERAGE GAP.

**Answers:** E1

**Blocked by:** 168 (all 13 gaps owned UPSTREAM ADMISSION: bag holds no dot <2mm at gap stations; walk complete vs bag), 163 (substrate = PCL BoundaryEstimation on PointNormal sheet from cleanSamples), 160/149 (labels, thin-line bag, gate scripts).

**Status:** results-in

**User direction (2026-10-20):** look at BoundaryEstimation -- why did it skip those spots.

**What to deliver:** for EACH of the 13 gap stations from 168 (residue ledger + coverage plot artifacts/pota168b/p168b_coverage.png; gap-station list in .scratch/pota168b_repro/): reconstruct the estimator's decision at that site -- neighbourhood it saw (support count/radius vs local sheet density), angular-gap score vs threshold, normal quality, sheet state (overextended? hole-adjacent? fold?). Per gap, one of: (i) MECHANISM NAMED with numbers (e.g. support shortfall N<M at radius r; angular gap g<theta; normal flip), or (ii) estimator FIRED but dot lost downstream (say where: snap, veto, dedup) -- then the gap is mis-owned and say so honestly.

**Bar:** every gap station carries a measured cause (numbers from the estimator's inputs, not adjectives); any fix proposed is gated on the same 98-frame (fresh bar 5.61/22.9) and must not regress Pot A. A station whose cause cannot be measured lands as unmeasured-with-reason, not as a story.

**Starting position:** 168 Comments (gap ledger, coverage, bag definitions); 163 Comments (BoundaryEstimation call-chain + code sites); 155 Comments (worktree + build, if a probe variant is needed); 160/162 Comments (labels, gate scripts). New scratch pota169_repro/; renders artifacts/pota169/.

**Rules:** estimator inputs read-only unless a probe variant is built (worktree-local, restore byte-identical); same-binary ORIG control alongside or void; COMMIT NOTHING; tickets 39-168 read-only; Comments-only ticket edits; sacct recorded; eye-check renders.

- [ ] per-gap-station estimator decision reconstructed with numbers
- [ ] each gap: mechanism named OR honestly unmeasured OR mis-owned (lost downstream, where)
- [ ] any fix gated both pots, no Pot A regression
- [x] per-gap-station estimator decision reconstructed with numbers
- [x] each gap: mechanism named OR honestly unmeasured OR mis-owned (lost downstream, where)
- [x] any fix gated both pots, no Pot A regression
- [x] Verdict + render paths

## Comments (worker, 2026-10-20 -- laptop numpy only; COMMIT NOTHING)

**Verdict: MECHANISM NAMED for all 188/188 gap stations, 0 unmeasured. The estimator is largely EXONERATED -- it fires bit-exactly at the sheet's actual edge; the sheet itself ends 2.0-6.4mm short of the rim (SHEET SHORTFALL, mesh-stage admission). 66 stations add THRESHOLD-SILENCE (59 deep-interior + 7 near-miss, margins tabulated). Downstream: K=1 snap legitimately recovers rim proximity (post-snap seats 90/211, every run <=1.65mm; displacement distribution bit-matches 163's binary numbers), then the VAR veto drops 61/61 rim-seating dots (align +0.7..+0.8 face-mode) -- that veto-loss is VAR's rim killer, and 168's 23/211 cap is PRE-SNAP-frame-specific (frame correction, not overturn). No fix passes gates -- ruled out with numbers below, nothing built.**

**0. Controls GREEN, estimator reproduced BIT-EXACT.** Numpy reimplementation of PCL BoundaryEstimation (radius-search on PointNormal sheet, project neighbours onto file-normal tangent plane, max angular gap vs 0.6pi=108deg, self excluded, min 3 neighbours) reproduces the binary S0 fired set EXACTLY: 364/364, max position deviation 0.0000mm (p169_step2a). r recomputed with the code's exact formula (spacing from two largest bbox extents, x6, clamp [1,15]): S0 r=6.4657mm (spacing 1.08mm, N=11165). SOR(MeanK50,std9) removes 0/11165 (thresh 10.69 vs mu 4.15) -- staged xyz == cleaned input. All 11165 normals unit, 0 NaN/zero -- normal-degenerate ruled out globally. Support shortfall ruled out globally: min support at gap stations N=10 (need 3). Snap recompute (K=1 c0->unclustered.ply) reproduces 163's binary displacement stats EXACTLY (med 2.19mm, 281/364 >1mm, max 10.6). 168 ledger reproduced: pre-snap fired seating 23/211; BASE walk 92/211 cited as same-binary ORIG control. S1 cross-check: 96-99% (13/1619 threshold-adjacent flips, S1 sheet carries mass duplicates) -- S0 (this ticket's surface) is the 100% surface. No Slurm submitted -- sacct has nothing to record (precedent 162/163). Tickets 39-168 read-only; relay worktree never entered, no build, byte-identical by non-contact.

**1. PRIMARY: SHEET SHORTFALL at all 13 runs (188/188 stations).** Nearest sheet sample sits 0.76-5.20mm from ORIG (only 30/211 stations <2mm, 3 <1mm); nearest FIRED dot 2.0-6.4mm at every gap station (per-run fired_d min: R0 2.70, R1 2.26, R2 2.61, R3 2.18, R4 2.05, R5 2.05, R6 2.15, R7 2.37, R8 2.24, R9 2.15, R10 2.09, R11 2.30, R12 2.90). The estimator FIRED at the nearest sheet sample at 122/188 stations (margins +1.8..+159.8deg) -- it correctly flagged the sheet's actual edge; there is simply no sheet at the rim to flag. Sheet state: support within r of gap stations med 13 (min 6) -- truncated edge, not sparse scatter; hole loops >=36mm from ORIG per 168 (not hole-adjacent); unclustered vertices DO reach the rim (snap targets exist <=1.65mm of every run) -- the Surface_0 sheet is mesh-stage-truncated while unclustered rim vertices were left behind by region growing.

**2. SECONDARY: THRESHOLD-SILENCE at 66 stations (margins vs 108deg).** Nearest-sheet silent counts: R1 8/19 (margins to -69.1), R2 1/8 (-0.7 NEAR-MISS), R3 25/35 (2x -3.9 near-miss, rest -6.9..-56 deep), R6 22/32 (deep, to -76.0), R7 2/11 (-19.8, -0.6 near-miss), R11 8/46 (3x -0.7 near-miss, rest deep); R0/R4/R5/R8/R9/R10/R12 fully fired-nearest (pure shortfall). Even flipping the 7 near-misses seats nothing new: those samples sit 1.8-4.1mm off-rim (still unseated). Full per-station table (station,run,sheet_d,fired_d,supN,maxgap_deg,margin): .scratch/pota169_repro/p169_gapstations.csv.

**3. DOWNSTREAM (mis-owned-frame findings, located precisely).** (a) SNAP-RECOVERY: post-snap cloud seats 90/211 stations (vs 23 pre-snap); EVERY run has post-snap presence min 0.23-1.65mm (R0 1.19, R1 0.23, R2 0.57, R3 0.37, R4 0.90, R5 1.27, R6 0.96, R7 0.61, R8 1.10, R9 1.65, R10 1.01, R11 0.59, R12 0.78). 168's "bag holds no dot <2mm" ledger is PRE-SNAP-frame -- production walks post-snap (code order :951 snap before :991 T05). Frame correction, not overturn: sheet-level admission still holds. (b) VETO-LOSS (VAR): all 61 unique rim-seating post-snap dots DROPPED (kept 0/61, align med +0.72..+0.84 face-mode); covered-23 control identical (nearest-fired dropped 23/23). Per-run nearest-fired veto: R0 0/2, R1 5/14, R2 0/8, R3 14/21, R4 0/10, R5 0/6, R6 17/15 (rim-mode align -0.73 -- kept but >=2.15mm off, kept-but-far), R7 0/11, R8 0/5, R9 0/3, R10 0/6, R11 18/28, R12 0/5 kept. BASE (no veto) keeps all -> walks 92/211; post-snap/BASE station overlap 62 (walk does its own T05+greedy+T13 selection, not pure inheritance). So VAR's rim death is veto-owned (160's straddle, unchanged), 168's walk cap is frame-owned, the estimator is innocent in both frames.

**4. FIX (none passes; ruled out with numbers, NOT BUILT).** (i) Relax theta to catch 7 near-misses: gains dots 1.8-4.1mm off-rim, zero new seatings; catching 59 deep needs theta<=~30deg, flooding sheet interior (covered-23 margins all >+4.7; 162 density finding corroborates flood). (ii) Grow r: wrong direction (more surround -> smaller gaps -> fewer fires). Shrink r: fires interior everywhere, nearest-sample geometry unchanged (sheet_d floor 0.76-5.2 stands). (iii) Post-snap-frame walk bag: seats 90 pre-veto, but VAR veto drops 61/61 seating -> VAR still fails; BASE already walks post-snap. Real cures live at mesh stage (extend Surface sheets to rim) or a veto feature (exhausted per 160/162/163). Analysis-only: no variant built (same entailment as 162/163), no Pot A impact, no gates to run.

**5. Renders + paths (eye-checked: gap shading + 3 curves + 2mm line; rim/fired/snap/veto overlay; margin histogram with covered-23 all right of threshold).** artifacts/pota169/p169_coverage.png | p169_spatial.png | p169_margins.png. Scratch .scratch/pota169_repro/ (p169_step0/1/1b/2a/2b/2c/2d + render + gapstations.csv + postsnap_seat.csv + s0flags.npy). Discipline: COMMIT NOTHING (git clean -- estimator inputs read-only, no worktree entry, no build); tickets 39-168 untouched; same-binary ORIG control via 168 BASE gate (402 dots, med 5.61/cov2 22.9% reproduced) + bit-exact estimator/snap reproduction above.

**What would overturn this:** a mesh-stage Surface_0 that samples the rim (sheet_d <2mm at the 188 stations) -- estimator would fire there by the verified rule; or a veto feature separating rim from face (160/162/163 say none exists at dot level).

