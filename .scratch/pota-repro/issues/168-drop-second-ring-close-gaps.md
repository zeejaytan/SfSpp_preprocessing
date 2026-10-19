# Drop the hole-ring, close the true-edge gaps

GOAL: THE CURATED EDGE IS THE TRUE BREAKING EDGE ONLY, AND THE WALK TRACES ALL OF IT.

**Answers:** E1

**Blocked by:** 166 (hole + flake + crumb in source data as received), 167 (through-hole not pipe),
168-cut (lead-run planar section: wall stops at rim both sides, air between),
149 (thin-line walk + honest uncovered spans), 144 (M144 recovery), 161 (mesh overlay).

**Status:** results-in

**User ruling (verbatim, 2026-10-20):** the mesh is not watertight -- it is an imperfect scan with unseen areas left open (not solid clay). Call the hole a special case: the mesh itself is defective. Remove the second ring (the false loop around the hole) and use what is left. Remaining problem: the walker still cannot trace the whole real breaking edge -- gaps are left. Solve that.

**What to deliver:** (a) CURATION: drop the hole-ring dots from the edge bag (dots attributed to loop1 -- nearest-loop == loop1 per 166, ~73 FAR; verify none sits on ORIG first: ORIG stays >=35mm from every loop per 166, so the cut cannot eat true rim). Re-gate the curated bag vs ORIG: every kept dot within tolerance, every dropped dot justified by loop attribution. (b) COVERAGE: walk the curated bag (thin-line + M144 recovery as starting recipe, NO retune without evidence) and score ORIG-rim coverage: which ORIG stations are visited, which gaps remain, each gap named (span / veto-eaten / admission-missing). (c) Close -- or honestly bound -- every remaining gap: admission, trigger, or upstream cause per gap. A gap that cannot close lands with its owner, not silence.

**Bar:** curated edge contains no hole-ring dots (count 0 within loop1 footprint + rim band) AND walk covers the full ORIG rim at gate at-or-better-than fresh (5.61/22.9) with zero unowned gaps. Failing that: honest negative with per-gap owners.

**Starting position:** 166 Comments (loops, flake, distances, scripts), 167 Comments (depth numbers), 149/144 Comments (thin walk + recovery recipe), 160/162 Comments (labels, gate scripts). Lead-run cut scripts in .scratch/pota168_repro (p168_cut.py, p168_cut2.py -- MINE, read-only, do not overwrite; use own scratch pota168b_repro/). Renders artifacts/pota168b/.

**Rules:** dataset read-only (the DS mesh IS the source -- no full-res exists, verified byte-identical both sides); same-binary ORIG control alongside or void; COMMIT NOTHING; tickets 39-167 read-only; Comments-only ticket edits; sacct recorded; eye-check renders.

- [ ] hole-ring dots dropped, curation gated (0 in footprint, ORIG untouched)
- [ ] curated-bag walk + ORIG coverage score
- [ ] every gap closed or owned with cause
- [x] hole-ring dots dropped, curation gated (0 in footprint, ORIG untouched)
- [x] curated-bag walk + ORIG coverage score
- [x] every gap closed or owned with cause
- [x] Verdict + render paths

## Comments (worker, 2026-10-20 -- laptop numpy only; COMMIT NOTHING)

**Verdict: HONEST NEGATIVE. Curation leg HOLDS (hole-ring gone, ORIG untouched); coverage bar MISSED -- the curated walk visits 23/211 ORIG stations vs fresh 92/211, and every one of the 13 remaining gaps is admission-side (the bag holds no dot <2mm there). No trigger or retune can close them: the walker visited 23/23 bag-covered stations, so the walk is complete relative to its bag and the bag itself is rim-sparse.**

**0. Controls GREEN (reproduce-or-stop PASSED).** Loop trace verbatim from p166_filecheck: 34989 edges, 636 boundary, loops [274,247,97,18], all closed -- exact-equals 166. Labels exact: NEAR 86 / MID 187 / FAR 91; FAR nearest-loop==HOLE(247e) 73. ORIG(combined Bl_0+Bl_1) min-dist to every loop >=36.1mm (loop1 36.23, loop0 40.22, loop2 70.78, loop3 36.12) -- cut cannot eat true rim. Same-binary ORIG control recomputed from staged BASE pcd (Oct16 production binary output, .scratch/pota161_repro/C01_BASE_..._Breakline_0.pcd): n=402 med 5.61 walk-<2mm 22.9% ORIGcov 92/211 -- reproduces fresh exactly (note: fresh cov2 22.9% is walk-dot <2mm%, ORIGcov is 92/211=43.6%). Tickets 39-167 read-only; lead scripts .scratch/pota168_repro/ read-only, never overwritten; no Slurm submitted -- sacct has nothing to record (analysis laptop-side on staged CSVs/pcds, TO==TF verified md5-equal path per 166).

**1. CURATION (p168b_step0_curate.py).** Drop set = FAR & nearest-loop==HOLE: 73 dots. (Nearest-loop alone would eat the rim: 63 NEAR + 121 MID dots also attribute to loop1 by nearest-loop -- they are 35-82mm away and stay. The ticket's ~73 FAR pins the drop set; verified NEAR-dropped=0.) Dropped dots sit 7.8mm min from Bl_0, 5.1mm min from Bl_1 -- none on either rim. Curated bag 291 = 86 NEAR + 187 MID + 18 FAR-residue (combined-vs-Bl_0+Bl_1). Bar leg 1: kept dots inside HOLE footprint 0, kept within 2mm seg-dist of HOLE 0 (min kept-to-HOLE 35.10mm) -- HOLD. Residue ledger: 18 combined-FAR kept (far from BOTH rims, min 5.1mm; attributed 14 loop3-crumb + 4 loop0-flake; nearest Bl_0 stations 0,2,6,7,170,182,183,188); 65 kept dots Bl_1-near<2mm (slot-1 exterior-face content mixed in the bag -- identity unresolved per 161-revisit, next curation step, not this ticket); c1 cloud (109 dots) all >31mm from ORIG, hole-segdist min 5.7mm -- no hole-ring content, correctly untouched. Curated-bag (unordered) gate: med 4.54, ORIGcov 23/211 -- the bag cap the walk inherits.

**2. WALK (p168b_step1_walk.py, M144 machinery VERBATIM: K34, twin-skip d>=1mm, envelope=own max greedy stride, T13 0.40, HALT rule; gate frame throughout, strides rigid-invariant).** Greedy strands 117/291 at slot 116, T13 ratio 0.4021 SUPPRESSED (by 0.0021 -- noted, not retuned). Envelope BAND 19.13; strand key-space twin-stale 0/33; leftover 174 with 0% within BAND. Recovery: 3 retreats (8.70/12.69/1.88) + index-advance to seqlen 279 / unique 276/291, then HONEST HALT (nearest road-retreat 81.92 > envelope 19.13), 0 forwards. Gate: med 4.4303 (< fresh 5.61, better) / walk-<2mm 7.5% (vs 22.9%, worse) / gaps5 50 / maxstep 26.7 (1 unlicensed step >25mm: 26.68, honestly reported) / ORIGcov 23/211 (vs fresh 92/211) / uncovered(DO>5) 27 stations in 7 spans; uncovered(DO>=2) 188 stations in 13 runs. Payoff: greedy 13/211 -> M 23/211 (sign +, recovery bought +10 but bag caps at 23). Topology (147-verbatim): greedy 116/8/1/3, M 277/24/25/49 (cls/flips/selfint/turns90) -- weaves worse than thin-bag (74/13/15) because the bag forces long strides, not face content. Bar leg 2 MISSED on coverage (23 vs 92); med leg better, walk-percent leg worse.

**3. PER-GAP OWNERS (p168b_step2_gaps.py; all 13 DO>=2 runs).** Bag-covered-but-walk-missed = 0/23 -- the walk is COMPLETE, no trigger gap exists. Every run has bag-covers-in-span = 0 with nearest-curated-dot 2.0-6.4mm: (0,1) (3,21) (23,30) (34,68) (72,81) (83,88) (93,124) (126,136) (139,143) (145,147) (151,156) (158,203) len 46, (206,210). Owner for ALL: UPSTREAM ADMISSION -- the S0 veto-stage cloud holds no dot within 2mm at 188/211 stations (nearest 2.0-6.4mm, med ~3-4mm); the extractor emits candidates 2-6mm off the true rim (same mechanism as 160's threading finding), and curation cannot conjure rim dots. Corroboration: 74 stations BASE covers but cur-walk does not have nearest-curated-dot med 3.1mm (bag-covers 0); BASE dots seating them sit med 2.3mm from any curated dot -- BASE's coverage comes from downstream stages (T05-kept 343 cloud + T13 second-chance adds), not from dots the veto-stage bag holds. Unsequenced 15: 9 duplicates at covered stations + 6 FAR dots (ORIGdist 7.7-36mm, stations 0,2,6,7,79) unreachable past the HALT envelope -- owner HALT-envelope, coverage-neutral (all >5mm from ORIG). The 18 combined-FAR residue dots do not seat any gap (nearest stations listed in step3) -- owner recorded, no gap falsely closed.

**4. Renders + paths (eye-checked: ring circles the blue loop with no red on either rim; walk loops the full rim but rides visibly off the black ORIG line; coverage plot shows bag and walk curves coincident with red gap shading).** artifacts/pota168b/p168b_curation_top.png | p168b_walk_top.png | p168b_coverage.png; texts mirrored artifacts/pota168b/p168b_step{0,1,2,3}.txt. Scratch .scratch/pota168b_repro/ (step0..step4 + curated.npz + seq npy). Discipline: COMMIT NOTHING (no commits); tickets 39-167 untouched; relay worktree never entered, no build, still byte-identical by non-contact.

**What would overturn this:** an S0-stage cloud that actually samples the rim (extraction admitting dots <2mm at the 188 gap stations) -- i.e. the admission-side fix 160 ruled out for angle features, retried with a position/loop-level feature (160 radial r>=47.69 hit 98.8%/11% but knife-edged; 162 dot-emptiness exhausted). Walking cannot fix admission; curation is done and holding.
