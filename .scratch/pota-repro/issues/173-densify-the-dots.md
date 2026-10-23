# Densify the dots per the 172 verdict

GOAL: GIVE THE WALKER DOTS THAT ARE DENSE, EVEN, AND ONE LOOP.

**Answers:** E1

**Blocked by:** 172 (SEQUENCE AFTER it lands -- the densify method depends on the verdict: re-sample where MESH-HAS-IT, honest silence where MESH-MISSING).

**Status:** results-in

**User direction (2026-10-20):** run the test, and densify the dot.

**What to deliver:** (a) DENSIFY per 172: where mesh has surface the sheet dropped, re-sample so the sheet reaches the rim (even ~1.5mm spacing target per 147 parity lesson); where mesh is silent, mark honest silence, do not invent dots. (b) Re-run estimator + snap + M144-family walk on the densified bag, gate vs ORIG (coverage stations/211, med, walk-<2mm, flips/selfint) against fresh bar (92/211, 5.61/22.9) and 170 union (90/211, 4.52). (c) Single-loop requirement: one face loop only -- no two-faced weave counted as success (flips/selfint must fall, not just coverage rise).

**Bar:** coverage >= fresh at gate <= fresh with flips/selfint DOWN vs 170, zero invented dots at MESH-MISSING stations. Failing that: honest negative owning dense-vs-even-vs-single-loop with numbers.

**Starting position:** 172 Comments (verdict + method); 169 Comments (estimator repro, snap numbers); 170 Comments (walk recipe, union 90/211); 147 Comments (parity lesson: dense+even+single-loop 206/206). New scratch pota173_repro/; renders artifacts/pota173/.

**Rules:** dataset read-only; relay worktree restore byte-identical if a binary is rebuilt; COMMIT NOTHING; tickets 39-172 read-only; Comments-only ticket edits; sacct recorded; eye-check renders.

- [x] densified bag + method per 172 verdict
- [x] walk + gate vs fresh bar and 170 union
- [x] Verdict + render paths

## Comments (worker, 2026-10-20 -- laptop numpy only; COMMIT NOTHING)

**Verdict: HONEST NEGATIVE on the bar's letter, with the coverage and gate legs smashed. Dense YES, even MOSTLY, single clean loop NO.**

**Bar scorecard (fresh = BASE 92/211, med 5.61, <2mm 22.9%; 170 union = 90/211, med 4.52, <2mm 31.0%; 170 strand1-M topo 126/19/16/25):** densified-bag cap 211/211 (every station has a dot <2mm, per-run max 1.66); strand2-alone 172/211 med 1.2257 <2mm 78.3%; 3-strand union 211/211 med 1.2626 <2mm 76.2% -- coverage and gate legs pass by a mile with zero invented dots (every added dot is a real unclustered mesh vertex; MESH-MISSING count is 0 because all 188 gap stations are MESH-HAS-IT per 172). Single-loop leg FAILS on the letter: s1-M topo 126/21/11/58 (flips 21 vs 19 UP, selfint 11 vs 16 down), s2-M 280/73/88/172 (flips/selfint UP), s3 364/93/151/275. Dense-vs-even-vs-single-loop owned below.

**0. Controls GREEN, no-veto path audited, method per 172.** Mesh 11875v/23114f asserted; loops [274,247,97,18] closed, HOLE = 247-loop; TF==T asserted; S0 staged 11165 with unit normals; unclustered 2343 verts with unit normals; sheet-shortfall control reproduces 172 (sheet->gap min 0.76 med 3.09 max 5.20); BASE control reproduces fresh exactly (402 dots, med 5.61, <2mm 22.9%, ORIGcov 92/211); S0-only estimator replica BIT-EXACT (364/364, maxdev 0.0000); 168 curation re-executed identically on S0 fired (FAR&HOLE drop 73, NEAR-dropped 0, kept 291); full-364 post-snap seating 90/211 reproduced; S0 snap disp med 2.12 (209/291 >1mm). No Slurm submitted -- sacct has nothing to record (precedent 162/163/168/169/170). Tickets 39-172 read-only; relay worktree never entered, no build, byte-identical by non-contact.

**1. DENSIFIED BAG (p173_step0d_bag.py): 753 dots, cap 211/211.** Rim strip = 612 unclustered vertices within 2.5mm of ORIG (real mesh surface per 172: gap station->strip max 1.657, frac<2mm 1.000). ORIG-guided selection is the 147-parity instrument, stated as such; 597/612 overlap the ORIG-free edge-adjacent set (off-sheet>=1mm and <6mm from S0 edge, p173_step0c), so guidance barely matters. Strip curation (168 rule): NEAR 528/MID 84/FAR 0, drop 0, NEAR-dropped 0 -- all rim. Strip snap K=1 to unclustered is identity (med 0.000, max 0.000). Concat 291+612 minus 150 exact-duplicate rows = 753. Per-run cap: all 13 runs fully seated (worst R3 max 1.49). On-arc (<2mm ORIG): 521/753 (vs 147's 101/314); station-ordered gaps med 1.76mm (vs author 1.80), p90 3.11, max 4.49 (vs author's uniform 1.97 max) -- dense at author spacing, even except a 4.5mm tail and 232 off-arc residue dots the no-veto recipe must route around. Estimator legs for the record: merged-sheet re-run (S0 + strip, code-formula r 6.2954) yields 253 fires with only 130/364 S0 fires retained -- naive point-append makes a ragged double edge the estimator correctly stops firing at, so the estimator re-run is reported as a measured NEGATIVE and the production-cure path stays re-segmentation per 172 (not built here).

**2. WALK + GATE (p173_step1_walk.py M144 verbatim; p173_step2b/c strand diagnostics as in 170).** Strand1 (recipe seed row 0): greedy 194/753, T13 ratio 0.258 FIRES, BAND 5.84, 1 retreat then HONEST HALT (road-retreat 6.18 > 5.84); M seqlen 211/unique 210; ORIGcov 59/211, med 1.3127, <2mm 71.6%, maxstep 9.2, 0 steps>25. Strand2 (leftover medoid): greedy 162, BAND 4.86, seqlen 507/unique 506, HALT2 5.95>4.86; ORIGcov 172/211, med 1.2257, <2mm 78.3%, maxstep 10.2. Union s1+s2: 172/211, med 1.2541, <2mm 76.3%, uncovered (DO>5) 35 in one span (19,53). Strand3 (still-unsequenced medoid): seqlen 637/unique 630; union-3: 211/211, med 1.2626, <2mm 76.2%. Remaining span (17-55, R1-R3) is strand-count walk-side residue (bag holds dots <1.66mm there) -- closed by strand3, so every gap is owned walk-side; bag-side admission is ZERO (cap 211/211).

**3. SINGLE-LOOP leg (why the verdict is negative): dense but not one clean line.** Radial-from-loop-axis check (147 HALF1b steer): s1 matched<2mm 151/211 cos-med 1.000 frac>0.9 = 1.000; s2 397/507 cos-med 1.000 -- both strands ride the SAME wall/loop, no two-face split. But the walk oscillates in/out across the ORIG line through scattered residue: s1-M flips 21 (vs 19), s2-M flips 73 selfint 88 turns90 172, s3 93/151/275. Per-step flip rate s2 (73/507 = 0.144) ~= 170 s1 (19/142 = 0.134), while 147 parity scored 2/206 -- the weave is the price of 232 off-arc residue dots (147's parity bag had none off its smooth chord), not a face error. Selfint climbs with lap count (s2 path ~650mm over a ~380mm loop = multi-lap crossings in projection). So: dense YES (1.76mm ~= author 1.80), even MOSTLY (p90 3.11 + residue halo, render), single clean loop NO on the counters despite one wall radially.

**4. Renders + paths (all three eye-checked: gray bag hugs green ORIG full loop with residue halo; purple s2 rides dashed ORIG with small zigzag, green s1 the left/bottom arc, red squares the 17-55 span; coverage shows purple union under 2mm except the 17-55 tent, BASE blue above throughout, green s1 covering only ~110-172).** artifacts/pota173/p173_bag_top.png | p173_walk_top.png | p173_coverage.png. Scratch .scratch/pota173_repro/ (step0d bag, step1 walk, step2b/c strands, step2 gate, step2d union3, step3 render + fm/cand/diag experiments + txts). Discipline: COMMIT NOTHING (git shows only untracked scratch dirs, no tracked modifications); tickets 39-172 untouched; E2E not run (out of scope -- the 211/211 union at med 1.26 is the follow-up's input, not this ticket's).

**What would overturn this:** a walk-side rule that laps the dense loop without in/out oscillation through residue (flips/selfint down at held coverage) -- the dots are proven sufficient (cap 211/211, union-3 walks it at med 1.26); or a re-segmented Surface_0 reaching the rim (172's overturn) that replaces the ragged strip with a clean dense edge, removing the residue the walker weaves through.


**Evidence-path note (2026-10-23):** paths under .scratch/pota1xx_repro/ and .scratch/pota22x/ cited above were removed by the scratch cleanup of this date (untracked intermediates; not recoverable). The numbers, quotes and verdicts in this ticket stand as recorded -- do not chase those paths or re-derive from them.
