# Lane fixes ledger -- APPLIED FIXES ONLY (lead-curated 2026-10-20)
Rule: every entry below proved to work in E2E (or a gate the E2E depends on) AND is applied in the current pipeline/vehicle. Diagnoses, refutations, shootout losers, honest negatives and vacuous closes are NOT listed -- they live in their tickets.
Vehicle: cure-potA @ bffefb6, k=5/b=3 shim unless noted.

## A. Pot A cure set (the control everything stands on)
Symptom: fresh preprocessing rims seated nothing; shipped rims seated 8/8+15/15.
Proof: ticket 27 rim-ordering fix, strict 15/15 landable set; ticket 38 landed three assembly commits (range 11f4827..b35905b: P22FIX feature_matching.cpp:1989, P22FIX2 ranking_system.cpp:1838, C2-restore pairwise 0.610->0.436) + repo-built reproduce; preprocessing T13/T21/T23/T24/T27 verified already committed by 38 audit.
Decision: APPLIED -- this is the vehicle every E2E below runs on.
Owner tickets: 27, 38.

## B. Slot-swap cure (surface-order swap upstream of the walk)
Recipe (81, anchor on Pot F): slot-exchange S0<->S1 + Bl_0<->Bl_1, same-loop resample for sub-50-pt slots, zero ORIG pts. Proof: jobs 33343950/52/53 + 33344601/615/617 all COMPLETED 0:0; E2E 6/6+9/9 x3 bit-identical; controls A 8/8+15/15, F_orig 6/6+9/9.
Applied to: D (84: 22/27+49/66 lineage, jobs 33361199/200/201); E (90: 29/31+56/62 best, jobs 33380562/749/751); B (93: pure SXC, min n=70); I (91 census + 94 I27 49->55 resample: 25/27+54/65 x3, jobs 33387455/56/57); J (92: 7/10+13/18 x3, jobs 33387858/59/60; 95 resample-hold equal); C partial (98: C02/C04 SXC, 2/3+1/3 x3 = S24 bar, jobs 33392081/82/83). Pot G's 83 shortfall entry is SUPERSEDED by 191 below.
Decision: APPLIED to every pot's bundle of record.
Owner tickets: 81, 84, 90, 91, 92, 93, 94, 95, 98.
Standing check (2026-10-20, user rule): NEVER blanket-apply the swap. Pot A proved P01 agrees while P02-P08 flip -- per-piece slot verification (fresh-Bl0/Bl1 vs author-Bl0/Bl1 med/coverage, 209 pattern) is required before EVERY future assembly, on every pot and every line. A swap that flips an agreeing piece silently unseats it.

## C. E_G crash cure (82)
Symptom: guarded E bundle segfaulted the assembler at launch (bare xyz-only Bl_0, reader data_structure.cpp:245 leaves features empty, ranking_system.cpp:1113).
Proof: v1 jobs 33343794/95/96 COMPLETED (0/6+0/2 x3); v2 jobs 33349656/57/58 COMPLETED (2/24+1/40 x2, 0/24+0/40 once).
Decision: APPLIED as crash-cure + honest partial (user option 1); real E cure came via the swap roll-out.
Owner ticket: 82.

## D. Default walk chain (each step applied in 194/195/196 and proven below)
0. True densify (143): mesh-sampled ladder 10->0/0->21->1 rung; 32/32 on-arc junk 0; bag 314, all 8 floors closed. Midpoints add zero true info (111/146) -- forbidden. APPLIED as chain step 0.
1. Split by surface (175): separate face clouds pre-pooling, walk each, file both slots; true-face walk beats the 173 union on all three gate numbers, both walks single laps. APPLIED as chain step 1.
2. Thin + verbatim walk (185): collapse ~2-wide strip to centreline, uniform 1.8mm resample, walk_m144 unchanged; 204 dots / closure 1.79 / D-tokens 2 / rim-med 0.64; beats 183 (D28) and 184 (refuted). APPLIED as chain step 2.
3. Recovery (144): state trigger (admitted-majority + coverage-payoff) FIRES honest, walk M144 322/310, gate 3.9736, uncovered 0; recipe banked, applied through 145/186 lineage. APPLIED.
Owner tickets: 143, 144, 175, 185.

197 (D-only pristine ablation on Pot C): C_fresh 0/4+0/5 -> C_197 2/4+1/5, exactly one true join C01-C03 x3 deterministic; pot-level falsifier fires (2/4 vs 4/4). D recovers C01's edge but does not seat the pot. Side-finding: landed A/B/C sections added ~270 rim pts to unchained C01-Bl_0 (attribution open).

## E. E2E proofs of the new default (de-doubled input seats sherds)
180 (first seating): Viterbi single loop 220/closure 1.48, rim-med 0.76; E2E jobs 33470102/3/4 COMPLETED 0:0, C_180 Total 165 x3, 3/3+3/3, T_0to_0 x3. APPLIED as proof de-doubling seats C01.
186 (default recipe x6): 185-v3 loop bundled, jobs 33482185/86/87 + lead duplicates 33482198/99/200 all COMPLETED 0:0, C_186 155/24, 3/3+3/3 x6 deterministic. APPLIED -- this is the default.
191 (transfer to G): 3 doubled edges cured with 185 v3, jobs 33484406/07/09 COMPLETED 0:0, G_191 5/7+3/10 x3, +1 sherd over fresh bar (60/39: 4/7+3/10), controls G_orig 7/7+10/10 + A green. Supersedes 83. APPLIED.
190 (gated thin on F01 doubled edge only, singles untouched): F_190 6/6+9/9 x3 = 81 bar, jobs 33485426/27/28; bar-neutral, no regression. This is the gated default done right.
193 (gated thin on J03 doubled edge only): J_THIN 7/10+13/18 x3 exact, bit-identical seated set to 92 SXC; J03 placed-but-wrong -> unplaced -- doubling NOT what kept J03 out (search-basin miss stands, needs assembly-lane work). Bar held, no regression, no further J rim work.
189 (Pot E, 13 gated thin loops of 25 doubled): below bar x3, only cured E23 seats (2/3 runs) -- HONEST NEGATIVE; generation fixed, placement fails downstream. E needs assembly-side work, not more rim work.
Owner tickets: 180, 186, 189, 190, 191, 193.

## F. Boundary: thin is NOT a blanket default (194)
Force-applied 185 v3 to Pot B's clean singles: 6/9+5/15 -> 2/9+1/15 x3 (jobs 33485122/29/30, NOT void). Split found one face each (label-flicker only); thin gated clean yet seating collapsed. Thinning is indicated ONLY on a doubling diagnosis (179 census), never blanket.
Owner ticket: 194. Attribution (198): collapse is GLOBAL/UNIFORM -- 14/15 edges wrong every run incl. byte-identical B01; per-rim repairs rejected; surviving edge is beam chance. Mechanism: thinned resample shifts the features every sherd matches on.
196 (full default chain on Pot A CONTROL, clean singles): A_196 5/8+3/15, 4/8+1/15 x2 vs 8/8+15/15 bar, jobs 33486565/66/67, controls green; GLOBAL scramble (0-1/15 strict edges, all pieces) incl. untouched rims -- SAME signature as 194/198. DEFAULT REJECTED: thin-then-walk must never ship blanket; rim-truth-med falsifier is BLIND to this mode (passed 8/8 while E2E collapsed) -- E2E on the control is the real ship-gate.
Owner tickets: 194, 196, 198.

## G. Boundary: never pool faces before splitting (204/C03 diagnosis, 2026-10-20)
Symptom: 204 pooled both face bags (F0+F1) then re-split geometrically by wall-facing (inner/fold/outer). On C03 the author's own second edge (Bl_1) entered Bl_0's bag and survived: F1 ring follows ORIG Bl_1 at med 0.86mm/91%% <2mm while Bl_0/Bl_1 are disjoint (med 15.88, 0%% <2mm); split kept 503/543 (fold share 77%%, only 40 refused); thin averaged two real edges into a false middle (6.52/7.3%% vs fresh 0.95/86.8%%); walk output == thin centreline point-set exactly (0.00), i.e. walk innocent. C02/C04 survived the same pooling only because their second strands read as outer-wall (C02 refused 511/955, C04 360/589).
Rule: provenance (which surface file a dot came from: Surface_0 interior vs Surface_1 exterior) is EXACT and must be split on BEFORE any pooling -- walk each face's bag separately, file each slot from its own face (175 as written). Pool-then-geometric-split is REJECTED: at the lip fold both edges read identically, so geometry cannot recover a label the pool already discarded. E2E proof pending (204 jobs 33499348/49/50); entered as constraint, not yet as applied fix.
Owner tickets: 204, 205.

## H. Pristine Pot A 100% recipe (210 seating + 213 traces, 2026-10-20)
Symptom: pristine-line fresh seated 7/8+9/15 with correct drawn lanes (208); P02-P08 slots flipped (209), P01-Bl1 a foot-step loop, not a rim (211).
What seated it: per-piece B-swap only (210: P02-P08 Bl0<->Bl1, job 33510738 COMPLETED 0:0 -> 8/8+15/15). What completed the traces: author-faithful walk (207) + 213 split-walk (FACE_ALIGN_VETO 0.5->2.0 keep-all + splitRimVsStepRing_213; P01 Bl1 med 0.67/97.3 vs author, Bl0 0.50/100 unchanged; jobs 33514459/33514736). Branch: origin/pristine-splitwalk (committed 2026-10-20, NOT merged -- 214 proves it on D first). NOT on this arm: D-chain steps 143/144/185 -- 196 put the full chain on this exact control and printed 4-5/8 (see F). 175 holds as verified invariant (per-face walks, no pooling; 212/213 logs). The cured Bl1 slot is unread by the assembler (slot-0-only); no reseat run, by user decision 2026-10-20.
Decision: RECORDED as the Pot A recipe; 214 proves it on D.
Owner tickets: 207, 209, 210, 211, 213.

## I. Splitter stopping rule R6 (FROZEN 2026-10-21, user + lead from the commonality table)
Rule: descend the tightness ladder loosest-first; FIRST stop satisfying ALL THREE wins: (a) balance 2nd/1st >= 0.5 (rejects one-giant); (b) touch test: the two faces TOUCHING (min separation < 2mm -- refuse the stop) vs NOT TOUCHING (>= 2mm -- pass). Plain words (2026-10-21, user): the test checks touching, so its verdicts are TOUCHING / NOT TOUCHING; if every stop TOUCHING, extend the ladder tighter below floor instead of stopping (but tight angles shatter twisted faces -- angle-only gate is distance-blind; candidate: curvature gate, angle-per-mm, since a break turns 90deg within ~1 dot-spacing while a bend turns 30-40deg over centimetres -- user physics 2026-10-22). REPAIR ORDER (user correction 2026-10-22, overrides 233's walk-first): split FIRST -- a perfect walk on a poisoned split still traces wrong (P22: break surface glued into S1); walk second, rim-gate last. (P22: the 4.5 floor ended the ladder, the rule says keep breaking -- 232 now probes @3/@2); (c) UN share <= 12% of cloud (rejects fragmented; UN grows with fragmentation: P12 5.3->9.8->18.4%). Dropped legs: top2>=70% (punishes complex pieces), third<=8% (perverse: shrinks as pieces shatter 9.29->6.79; sole solo action in 5 pieces was wrongly rejecting P12@4.5). Record on 7 pieces: P15@8/P16@10/P01@8 GOOD, P12@4.5 near-miss (Bl0 0.63/89.0 corner excursion accepted as cosmetic -- @3 alternative strictly worse, 224), P27 needs 4th leg (clean on all three at @12/@8/@4.5 yet lanes wander: 228), P22/P25 NONE (bridge class, correct). Good-stop gaps cluster ~5mm (wall scale; necessary not sufficient). Owner tickets: 220, 221, 222, 223, 224, 225, 226, 227.
Pot D P25 (2026-10-21, 231 amendment): fresh pipe lanes SWAPPED -- straight slots 7.07/0.0 + 6.96/0.0 (== 214 gate_table EXACT, the misread on record); matched slots 0.81/85.9 + 0.79/91.2 near-miss. Slot-verify every piece before grading lanes (209 pattern); the gate table is not slot-safe. Owner tickets: 230, 231.

## J. Paper-arm default ON + 10-pot preprocessing rollout (2026-10-23) -- ALL BELOW IS PAPER-ARM, not legacy chain
Arm flip: paperChain false->true x2 in mesh_processing_headless.cpp (:2039, :2557), committed 1a7c68d; SFS_PAPER_CHAIN=0 still opts out. Binary record (bm172 rebuild, jobs 33690135/33690569 COMPLETED): mesh a51e7c1c385a2039c7932780a837c19f, edge dc472b0e87c934b6c487ff8637209864 (edge byte-identical to pre-flip; source unchanged since for both files).
What the arm INCLUDES (paper-exact, was parked behind SFS_PAPER_CHAIN): mergeClusters theta=4/kappa=1/nb=10 multi-pass (:1384), B-spline lane smoother (:810), inside/outside vote classifyAndOrder (:1990), axis-ray face marching, PotSAC top-10/prune 0.9848/refine, rim 1.0/0.1/20/steadiest. What is NOT in this binary (still worktree patches only, vote247.diff + 248-filter diff): vote-order lane selection, K-D tree clean-up filter, 1.9mm resample.
  SUPERSEDED 2026-10-24 (main = 67ff3d7 = b289e87 + the strip): the shipped default now IS the no-discard full walk (SFS_FULL_WALK=0 restores largest-comp + clock sort), with the 12mm stop-at-the-weld rule (SFS_STOP_NOFRESH, 0 disables), the vote-order host including the 1.9mm resample, theta default 3.4 (SFS_PAPER_THETA) and the 274 neighbour clamp. The blind density filter, braid gate, guided filter, loop-select and vote repair were REJECTED and deleted (538357c + 67ff3d7), so the 'still worktree patches' sentence above no longer describes main. The walk selector of ticket 275 is measured but HELD on the conservator's order: patch at .scratch/pota-repro/patches/275-walk-selector.patch. Every score in section J was collected at theta 4.0 on the pre-strip binary: section J is history, not the current binary's behaviour, and the 214 lanes still need re-scoring. All scores below are default-env runs (no SFS_* set, 7x paper=PAPER-CHAIN in every pipe log).
Scores vs author edges (bar = med<2mm + cov>=90, matched slot): A 16/16 PASS (250, 87e5c38); C no-drift vs 249 diagnosis (251, e66890e); D 51/58 (252, 0650111); B 17/18, P01-Bl1 1.89x tail (253, d5427ea; ticket-41 teleport mode GONE with no T42 fix); E 60/62, P13/P16 single-lane near-miss (254, 7db8cd3); F 12/14, 0 miss, 0 jumps>10 (255, caecb92); G 12/14, P07 near (256, a3e15d3); H 18/22, 4x Bl1 single-lane (257, 9f1bb3c); I 55/60, 0 miss (258, 1a64da0); J 20/24, P01 both-lane 1.64/1.65x tails + P09 whole-piece both-lane miss rev 39/52 (259, c48966e). New-pot total 194/214 at bar (~91%). Naming offset (pipeline Bl0/Bl1 vs author convention) on D/E/F/G/I, unambiguous on cross-check; B/H/J straight. Miss family: tracer leaves rim (tails, chord cuts, parallel ridge, one wander, one whole piece); never the ruler (reverse coverage decides every case).
Decision: APPLIED as the default preprocessing arm for all pots; misses recorded as known-single-lane (J-P09 whole-piece flagged for its own call).
Owner tickets: 250, 251, 252, 253, 254, 255, 256, 257, 258, 259.

## K. Failure classes that are NOT tracing failures (2026-10-24, tickets 276/278/279)

Rule, measured on the authors' own outputs, not inferred: **a reference breakline is always the boundary curve
of the surface they kept.** Corpus-wide (163 pieces x 2 lanes = 326 lanes), every reference line sits a median
0.27 mm from its own Surface_0/Surface_1, 326/326 within 1 mm, lane 0 -> Surface_0 and lane 1 -> Surface_1 on all
163 pieces, and the largest angular gap around the nearest surface point is 164.9 deg (lane 0) / 167.6 deg
(lane 1), minimum over the corpus 140.0 deg. No reference line is ever drawn on a region their surfaces exclude
(ticket 279, run 20261024-1417_dc869d4_p279-basefaces).

Consequence: **partition mismatch** is its own class. When our surface stage keeps a different face than theirs,
our boundary and their boundary are different real edges on the same sherd, and no walking, resampling or
threshold change can close the gap.

Confirmed member: **Pot C 03 Breakline_1** (the piece is a base sherd). Their Surface_1 (8150 pts) is the base
disc; our equivalent cluster c2 (13265 pts, complete disc, |n.axis| 1.000, 36/36 bins, edge_cv 0.025) sits
0.295 mm from it and is DROPPED (third by size). Our second surface is an exterior wall of 17245 pts that is in
NEITHER of their surfaces (5.992/8.083/10.472 mm to their S0, 14.456 mm to their S1). Their line rides the base
rim (0.276 mm median, 73.3% of dots within 1 mm of r95 33.17 mm); ours follows the wall's fracture edge.

Scope, so this does not grow: a complete base disc appears on 3 pieces of 163 (Pot A 01, Pot C 03, Pot J 03) and
the detector is flat across its parameter range (edge_cv 0.10-0.15 -> 3, 0.25 -> 4; nsel 150-600 and l3/l1
0.01-0.05 change nothing). On our side the only complete disc among the four meshed pieces is C03's, and we drop
it. Nothing was built for this and nothing is planned to be: the fix would be third-surface support or a growth
change, and the class explains one lane of the 214 scored.

Also closed by the same work, each by measurement rather than argument: the cluster merge (fires correctly on a
deliberately split surface; the refusing test is the paper's Appendix A step 3, refusing for a legitimate
geometric reason), theta (re-meshed at 3.4, the base still dropped), rho_d (reaching it would need ~3 mm = ten
sampling spacings and the base is still third by size), and the two-largest ordering itself (not the difference:
each pipeline kept a different second face). The gap is a labelling gap, not a hole: 1175 unclustered points form
the base-to-wall corner ring at 0.3556 mm mutual spacing in all 36 bins, and 0 of them lie within 1 mm of either
side, so the base's nearest kept point is 2.4872 mm = 2.5x rho_d and no Appendix A pair can form.

Owner tickets: 276, 278, 279.

## L. Known-defective input pieces (read before scoring)

**Pot C 01 — not watertight.** The scan left a gap in the surface mesh; the pipeline reads it as
a second broken edge the sherd does not have. Its lanes (Bl0 25 dots / 51.62 mm / cov 0.0 at the
shipped defaults; 986-dot bag in 4 components) measure the input, not the method. Two candidate
causes are on record and have NOT been separated: the walk seed in a debris lump (ticket 275) and
the scan gap (this entry). Do not cite C01 as evidence for or against any walk change until the
gap is located and the two are told apart. Ticket:
`.scratch/pota-repro/issues/285-pot-c-01-scan-gap.md`.

## Pending proofs (not yet in this ledger)
194 (B harmless -- LANDED regression, in F above), 195 (D harmless -- LANDED regression, in F above), 196 (A control holds -- LANDED regression, in F above), 189/190/193 (E/F/J cure-or-vacuous). Each enters above ONLY on a landed PASS with E2E numbers.
