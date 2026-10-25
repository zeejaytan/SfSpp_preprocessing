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
  SUPERSEDED 2026-10-24 (main = 67ff3d7 = b289e87 + the strip): the shipped default now IS the no-discard full walk (SFS_FULL_WALK=0 restores largest-comp + clock sort), with the 12mm stop-at-the-weld rule (SFS_STOP_NOFRESH, 0 disables), the vote-order host including the 1.9mm resample, theta default 3.4 (SFS_PAPER_THETA) and the 274 neighbour clamp. The blind density filter, braid gate, guided filter, loop-select and vote repair were REJECTED and deleted (538357c + 67ff3d7), so the 'still worktree patches' sentence above no longer describes main. The walk selector of ticket 275 is measured but HELD on the conservator's order: patch at .scratch/pota-repro/patches/275-walk-selector.patch. Every score in section J was collected at theta 4.0 on the pre-strip binary: section J is history, not the current binary's behaviour, and the 214 lanes still need re-scoring -- and were re-scored on 2026-10-25 (tickets 284, 292): the corpus baseline is 281 of 292 sound lanes at bar, section P, with the change set and what each change bought in section Q. All scores below are default-env runs (no SFS_* set, 7x paper=PAPER-CHAIN in every pipe log).
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

### K.2 Same face, two different contours (2026-10-24, ticket 289)

Pot J 09, the one whole-piece failure of the seven-pot rollout, turned out not to be a trace failure at
all. On the shipped binary (8e1e514) both lanes are complete closed rings on the correct faces, welded to
1.80 mm (one dot spacing), with no jump: interior 78 dots / 143.2 mm / median 1.20 mm / 75.6 % coverage
(was 2.53 / 32.6 on ticket 259), exterior 84 / 153.3 / 1.98 / 51.2 (was 2.41 / 40.0, and its 14.4 mm jump
is gone). Ours encloses 1010 mm2, the authors' 769 mm2: our line is the outer silhouette of the sherd,
theirs is a contour drawn inside it over 41 mm of arc, up to 10.4 mm away and smooth (no run longer than
10 mm keeps a turning angle under 2 deg per step, so it only looks like a chord). The pre-walk bag already
sat 1.717 mm off with 48.5 % of its dots beyond 2 mm, so the walk inherited the disagreement and moved it
0.24 mm. Every reference dot is on a kept surface, so this is not the dropped-cluster class of K.

Class name: **same face, different contour (S)**. Running hypothesis, shared with Pot H 02 (ticket 286):
the two pipelines kept surfaces of different EXTENT, and each line is the boundary of its own surface.
The settling test is named in the ticket and not yet run: the share of each reference ring that lies
inside our surface's silhouette.

Owner ticket: 289.

## L. Known-defective input pieces (read before scoring)

**Pot C 01 and Pot J 01 — not watertight, in the INTERIOR surface only.** The conservator reports
a scan gap in the interior mesh of both pieces; the exterior is intact. The pipeline reads the gap as
a second broken edge the sherd does not have, so an interior lane can produce a stub or an extra
contour that belongs to the input.

- Interior lanes (Bl0) are compromised and may not be cited either way: Pot C 01 25 dots / 51.62 mm /
  cov 0.0 (986-dot bag in 4 components), Pot J 01 47 / 29.27 on the theta-3.4 rebuild (25 / 32.05
  shipped; 832-dot bag in 4, seed in the 127-dot lump 36.72 mm from the largest).
- Exterior lanes (Bl1) are NOT explained by the gap and remain evidence: Pot C 01 81 dots / 41.06 mm /
  cov 0.0, Pot J 01 82 / 23.31. Both are walk-seed stubs, and the held 275 selector takes them to
  226 / 0.527 / cov 100.00 (author-side 99.57) and 184 / 0.596 / 100.00 / 100.00. With Pot B 01
  (126 / 26.351 / 0.00 -> 307 / 0.661 / 97.39) that is three intact exterior lanes cured on three
  pieces of three different pots.

The gap itself is still unlocated, and no interior lane may be quoted as a cure. Owner ticket:
`.scratch/pota-repro/issues/285-pot-c-01-scan-gap.md`.

## M. Shipped after section J: the walk starts in the largest lump (2026-10-24, ticket 287)

Landed to main with the ticket and its patch (\`.scratch/pota-repro/patches/287-largest-lump-seed.patch\`).
In \`getPointsInSequence_Vote247\` the deterministic start dot is now taken inside the LARGEST 5 mm
component instead of inside the whole bag: the seed and its centroid are both summed over dots with
\`!used[i] && comp[i] == biggest\`. No environment switch, no threshold touched; the stop rule, the
heading guard, the vote-order host and the 1.9 mm resample are untouched.

Where the bag has split (crack, hole, scan gap) the old code began the walk in a debris lump tens of
millimetres from the rim and the 12 mm stop then ended it as a stub. Measured, with the scorer in the
run directory (before -> after, n / median / coverage ours->author, zero jumps in every row):

- Pot C 01 Bl1 **81 / 41.055 / 0.00 -> 226 / 0.572 / 100.00** (author-side 99.57)
- Pot J 01 Bl1 **82 / 23.201 / 0.00 -> 184 / 0.597 / 100.00** (author-side 99.47)
- Pot C 01 Bl0 25 / 51.620 / 0.00 -> 207 / 0.682 / 98.55 (interior lane of a defective input, ticket L)
- Pot J 01 Bl0 47 / 29.268 / 0.00 -> 170 / 0.581 / 100.00 (same caveat)
- Pot H 02 Bl0/Bl1 and Pot H 10 Bl0/Bl1: **bit-identical**, max|dxyz| 0.000000 (single-lump bags)

Record: run \`/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/\` (jobs
33746239, 33746280, 33746344, 33746350, 33746383, all COMPLETED 0:0); binary before
62ddd28f4476e9cdf5b27cf0ee01c2f0, after a28d10afab2b50bbe750d599ee2b7214. Lead recomputed every row
from the exported clouds with an independent scorer.

**What it does not cover.** Pot D 03/22/01 and Pot B 01 are untested: their stage inputs were deleted
on 2026-10-24 (attic manifest class G, 2,468 Surface_*.xyz) and the authors' own surfaces cannot stand
in for them because the edge stage also needs the mesh-stage product. H02/H10 are still below bar
(73.19 / 72.83) for their own reasons (tickets 280/286), P22 Bl0 is still 87.79, and the 296-lane
corpus cannot be re-scored (ticket 284). Ticket 275's walk selector stays HELD and is now redundant in
purpose: this change seeds the single full walk instead of adding a fallback path.


## N. Known-defective reference lines (read before scoring)

**Pot J 09 — the authors' breaklines are not a valid standard on this piece** (conservator's ruling,
2026-10-24, ticket 289). Their interior line runs 1-2 mm inside the sherd's actual edge; their exterior
line leaves the edge altogether for about 41 mm and crosses the flat of the face, up to 10.4 mm from ours.
Our line follows the broken edge on both lanes, read on an on-mesh overlay of both lines against
`Pot_J_Piece_09_Mesh_DS.obj`.

Applied: **both J 09 lanes are excluded from the bar tally**, so the piece is neither pass nor miss. Pot J
is **20 of 22 valid lanes at bar** (was 20 of 24 with P09 counted as two misses; P01's two tail lanes remain
misses) and the corpus is **265 of 294 valid lanes**. The raw numbers stay in ticket 289: they are the
measurement, not an acceptance criterion.

This is one reference that is wrong, not a doubt about the rest: ticket 279 measured that on 163 of 163
pieces a reference line is the boundary of the authors' own kept surface, and 265 lanes sit within 2 mm of
these references. What would overturn the ruling: their surface being trimmed exactly where ours is not, by
an identifiable rule -- then theirs would be consistent and ours the outlier here. Nothing in hand shows it.

- **Pot C 03 Bl1 - the authors' line is a plate rim, not a break edge** (conservator's ruling,
  2026-10-25). Their Bl1 follows the rim of their own small plate-like face (n_ax 0.939), 5.83 mm from
  ours, with 90% of its dots over pottery our growth never labelled and 100% of them beyond 2 mm from our
  material over a 273.7 mm stretch; the band test classes it *different surface*, the only lane of the nine
  adjudicated. Our line runs the sherd's real outer rim - 607.34 mm of edge against their 273.69 mm. The
  lane is **excluded from the bar tally**: Pot C is 4 of 7 valid edgelines and the corpus becomes
  **283 of 291 (97.3%)**. The numbers stay in ticket 295; they are the measurement, not the criterion.
- **And it is a cheap lane either way, because the assembly stage reads only Breakline_0.** Verified
  2026-10-25: the file_path arrays in structure-from-sherds-pp/class/data_path.h name one file per piece,
  the _0 one, and Breakline_1 appears nowhere in class/ or the build (9 repo-wide hits, all in helper
  scripts and docs). Our Breakline_0 is the boundary of Surface_0 = the **interior** face, so a wrong Bl1
  cannot move a seating number. Of the eleven below-bar lanes, **four are interior** (D 22 Bl0, D 27 Bl0,
  E 16 Bl0, I 25 Bl0) and seven are exterior.

- **Pot I 25 -- the authors' surface order is inverted** (ticket 295). On 163 pieces a concavity test names
  Surface_0 the interior on 158; the exceptions are Pot I 25 and Pot J 14, where their Surface_0 is the
  physically exterior face. Both releases' lines still ride the same physical faces (0.249 / 0.242 mm apart),
  so this is a naming inversion, not a lane swap, and the lanes are scored normally.

## O. Pieces outside the authors' evaluation set (read before comparing to the paper)

**Five pieces we score were never evaluated by the authors, so their numbers are ours alone**
(2026-10-24, measured against the released archives): **Pot F 07, Pot I 28, Pot I 29, Pot I 30,
Pot J 12**.

- The paper excludes pieces by rule — "very small fragments comprising fewer than 50 points in the
  respective surface edge lines (with a perimeter of approximately 9cm) and special parts such as the
  handle, nose, or ornament", removing 1 from C, 2 from D, 4 from E, 2 from F, 3 from I, 8 from J = 20
  (`C:/PR/papers/text/sfspp-2502.13986v1.md:329`). The samples tree reproduces that total exactly:
  20 pieces carry the authors' breaklines, axis and both surfaces but no released cloud (a 21st,
  Pot C 07, has no author artefacts at all). The per-pot split in the paper is off by one on C, D, E
  and F against ours; the total is the reliable figure.
- **The release is the evaluation set, not a lost subset.** `Mesh.zip` and `Point.zip` carry exactly
  Table V's counts — A 8, B 9, C 4, D 29, E 31, F 6, G 7, H 11, I 27, J 11 = **143** — and all 143
  meshes are byte-equivalent in vertex and face counts to ours.
- **How to use them**: score them against the authors' breaklines as usual (the reference is a real
  author line), report them with the corpus, and **never set their scores beside the paper's**. Pot J
  and the pot subtotals must state which of their lanes are inside the evaluation set.
- **The derived clouds are not second-class** — measured on Pot C 01, the one piece that has both:
  nearest-neighbour median 0.091 mm derived→released and 0.110 mm released→derived (p99 0.23 / 0.36),
  offset along the released normal median 0.000 mm, normals |dot| 0.999, own spacing 0.084 against
  0.092 mm. Ours carries 16% fewer points because `cc_mesh_to_pcd.sh` applies a statistical outlier
  removal the release does not. The one real difference is that the sampler is unseeded, worth
  0.14-0.16 mm on a lane median (ticket 289).
- Corpus root and manifests: `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Point/`
  (`MANIFEST_released.tsv`, `MANIFEST_derived.tsv`, `README.md`).


## P. The baseline at the shipped defaults (2026-10-25, ticket 292)

**281 of 292 sound lanes at bar (96.2%)** -- 283/294 valid, 283/296 measured. This is the number to
quote. It is not comparable with the 265-of-294 figure that stands elsewhere in this ledger: that one
was measured at theta 4.0 on the pre-strip binary, on point clouds that can no longer be regenerated.

How it was measured (run `20261025-0134_787c149_p292-rescore`, commit `787c149`, 148 array elements,
all COMPLETED 0:0): the 148 frozen corpus clouds (ticket 290), staged by symlink only (ticket 291),
the shipped defaults with no `SFS_*` override, theta 3.4, and `score292.py` -- the fixed scorer in
`.scratch/pota-repro/292/`. Bar = median <= 2.0 mm AND coverage >= 90; jumps reported beside it.

Exclusions, fixed before the count: Pot J 09 both lanes (reference ruled wrong, ticket 289 ->
294 valid); Pot C 01 and Pot J 01 lane 0 (interior surface defective, ticket 285 -> 292 sound);
the five pieces the authors removed (F07, I28, I29, I30, J12) scored, listed, never compared with
the paper (section O).

Per pot, sound lanes at bar: A 16/16, B 18/18, C 6/7, D 55/58, E 61/62, F 14/14, G 14/14,
H 20/22, I 56/60, J 21/21.

The eleven sound misses fall in two groups and neither is blindness:

- **Eight are the one-stretch family** (D22 Bl0, D27 Bl0+Bl1, E16 Bl0, H02 Bl1, H10 Bl1, I06 Bl1,
  I13 Bl1): median 0.67-0.88 mm, total length within 5% of the reference, one stretch beyond 2 mm.
  This is ticket 286's mechanism (our kept region spans a fold the reference turns into) with nine
  members now, and `Pot_D_Piece_27` is the clearest -- 1.2x the reference length at 0.73 mm median.
- **Three lanes are different contours**: `Pot_C_Piece_03` Bl1 (the known base-band partition mismatch of
  tickets 278/279) and `Pot_I_Piece_25` both lanes (new, ticket 293).


**What the eleven look like** (ticket 294, 2026-10-25 -- eleven figures, each with the shaded mesh above
and the extracted surface below, our line green and the authors' black). In **all eleven**, our line is
the boundary of the surface we kept and the reference is the boundary of the surface the authors kept --
section K's rule, now seen rather than inferred. **Eight lanes are the same face with a different reading
of one stretch** (18-65 mm): on `Pot_D_Piece_22` Bl0 **the reference is the one drawing the chord** (18 mm
straight across the notch, mean gap 4.33 mm) while our line follows the material round it, and on
`Pot_H_Piece_10` Bl1 the reference steps 4.42 mm inside our face for 39.6 mm. **Three lanes are a
different partition**: `Pot_C_Piece_03` Bl1 our outer rim (607 mm of edge) against their closed ring on the
flat, 274 mm round and about 11 mm inside; `Pot_I_Piece_25` both lanes our small closed triangle
(105 / 121 mm) against their larger loop (124 / 106 mm), 6.9 mm apart in 3D. Every reference line here was
measured against the authors' own DS mesh by exact point-to-triangle distance: 18 of 18 rows, median
0.007-0.024 mm, p95 <= 0.115 mm, max 1.386 mm, **0.00% beyond 2 mm** -- so no disagreement in this set is
a reference that left its part, and the eight are a **convention difference about where the edge is
taken**, not a tracing error. Reading trap worth keeping: `Pot_I_Piece_25`'s lines cross in X-Y and are
6.9 mm apart in 3D -- a crossing in one projection is not contact.

**Why the eleven differ, and why the walk cannot close them** (ticket 293, 2026-10-25). Phase A:
`Pot_C_Piece_03` Bl1 is the partition mismatch section K.1 predicted, measured here from cluster
membership -- our line the outer rim of the wall we keep (0.700 mm from its p95 rim, 35.1% ring share)
and theirs 10.51 mm inside that rim, on the base band the mesh stage drops. `Pot_I_Piece_25` is **not a
contour difference at all: the two lanes are one curve pair counted twice**, with the two sides' indices
crossed -- our Bl0 sits 0.680 mm from their Bl1 and our Bl1 0.568 mm from their Bl0, coverage 100/100
both ways (max 1.42 / 1.75 mm), while the same-index pairs sit at 6.910 and 6.951 mm at 0/0; the dot
counts (58 against 60, 67 against 69) and the arc lengths (104.79 against 106.28, 120.57 against 124.26)
pair crossed too. **If the conservator accepts those labels as swapped, both Pot I 25 lanes are at bar
and the corpus is 283 of 292 (96.9%).** Phase B, the eight: one mechanism in three causes -- one
reference drawing a chord over a notch mouth (`Pot_D_Piece_22` Bl0, its own dots 8.07 mm from any kept
material), six references running inside continuous material of the face we keep (D 27 Bl0, D 27 Bl1,
E 16 Bl0, H 10 Bl1, I 06 Bl1, I 13 Bl1; 0.208-1.933 mm from it, 0-6% of their dots on a boundary against
94-100% of ours), and one fold our surface spans (`Pot_H_Piece_02` Bl1, ticket 286's 14.13 deg). **Only
the chord is visible in a boundary set, and only negatively** -- in the other seven the turning feature
lies inside continuous material, so no walk rule, seed or stop condition can close this family; it needs
curvature evidence on the kept face, or a merge that refuses to join across a fold. Our own line never
leaves the surface in any of the eleven (median 0.010-0.052 mm, max 0.334 mm to the authors' own mesh).

One jump survives in the shipped code: `Pot_C_Piece_02` Bl1, a single 37.712 mm step at median
0.530 mm -- at bar, recorded, not diagnosed.

Weight: one draw per piece, one binary, one commit, no repeat runs. The mesh stage is
piece-dependently non-deterministic (ticket 291: 0.867 mm on Pot H 02), so a lane within about 1 mm
of the bar must not be quoted as clearing or missing it on this run alone -- the nearest case is
`Pot_D_Piece_22` Bl0 at 86.40% coverage against a 90% bar.

### Why the eleven below-bar lanes differ -- the conservator's six claims, measured (ticket 295, 2026-10-25)

He read the eleven ticket-294 figures and stated six claims. Every one was measured against the run of
record SfSpp/runs/20261025-1824_ca18c8f_p295-lanes/ (job 33761881), after a gate that reproduced **385 of
385** ticket-293 numbers (worst delta 0.0050 mm). Verdict: **C2 holds; C1 and C3 hold with qualification; C4
and C5 do not hold; C6's judgements hold with both stated reasons corrected.** Two of the four partial
results are in our own favour, which is the least comfortable place for them to be.

- **Pot I 25 is a naming inversion, not a lane swap.** On 163 pieces a concavity test names Surface_0 the
  interior on 158 and Surface_1 on 2 -- **Pot I 25 and Pot J 14**, where the *authors* are the outliers against
  their own 161/163 convention. Both releases' Bl0 ride the **same physical face** (0.249 mm apart) and both
  Bl1 the same other one (0.242 mm); every reference dot is inside 2 mm of our material (max 1.475 / 1.690).
  So the surface files carry an inverted order on that piece, and on our side it shows as the
  breakline-to-surface index pairing.
- **Pot C 03 Bl1 holds:** their line is the rim of their own small plate-like face (n_ax 0.939), 5.83 mm from
  ours; the 2 mm band angle test calls it different_surface, the only lane of the nine that does.
- **Pot D 22 Bl0 and D 27 both hold with qualification:** their lines are boundaries of their own faces. On
  D 22 the earlier reading (that THEIR line bridges the notch with an 18 mm chord) is WRONG and was corrected
  by ticket 297: the 19.92 mm is only the end-to-end distance of their two nearest dots, their polyline runs
  43.28 mm round the corner, and OURS is the 18.00 mm cut across it (our dots 39-49). Measured tilt under
  each line's own dots: theirs 66.3 deg median and 100% above 45 deg (broken/rounded material), ours 29.6 deg
  and 0% (the flat of the face). So ours is the shortcut and the conservator's reading was right.

**No welded break facet anywhere, measured:** on all nine matched lanes **0.00%** of the 2 mm band our kept
material contributes under the reference is pitched more than 45 deg off the authors' own normals (median
0.7-5.5 deg, offset 0.004-0.023 mm). "Our surface swallowed part of the break face" is not present in this
sample and is no ground for a growth or classify change.

**The mechanism is PARTITION -- the face-extent rule**, not the walk seed and not a weld test: our edgeline is
the boundary of the *labelled* face, and immediately outside it lies real sherd material that growth left
unlabelled (H 02: a 2311-point unclustered band in the 2 mm corridor, 89 on Bl1; E 16: 68.6 deg; C 03 and
D 22: 90% / 92.3% of the stretch's nearest labels unlabelled; H 10: 100% over a dropped cluster). Where that
material *is* labelled, our face extends **2.4-9.6 mm past the reference** on the same plane.

**And the growth gate cannot be the fix.** The turns do not differ in per-step size: H 02's straddling pairs
step a median **3.23 deg** with 52.7% at or below the 3.4 deg gate (ticket 281), while Pot D P03's severing
bottleneck is **3.45 deg** and P 22's **3.06** (ticket 271). A gate loose enough to cross H 02's base-rim also
crosses P03's flank and re-breaks the lane 271 fixed. What remains is **which faces are kept** -- a third
surface, or base handling, which the paper itself lists as future work (papers/text/sfspp-2502.13986v1.md:460).

**A reading rule, earned twice.** On H 02 Bl1 I wrote that the authors' line "carries on over the turn"; on
Pot D 22 I assumed the chord was ours. Both were backwards. **Which line stops short is not readable from a
plot -- only the per-dot signed position says it.** Quote the sign, not the picture.

## Q. The shipped change set, and what each change bought (2026-10-25)

One place to read what we actually changed in the pipeline and what it bought, so a later session does
not have to reconstruct it from twenty tickets. Every row is applied in the shipped code; every effect
was measured on the frozen corpus or on a gate that the corpus score depends on. Diagnoses, negatives
and shootout losers are NOT rows -- they are in the "removed" list at the end.

| # | change (commit) | what was wrong | what it bought (measured) |
|---|---|---|---|
| 1 | paper chain on by default, `SFS_PAPER_CHAIN` (`1a7c68d`) | the paper-exact code sat behind an env default false, so scoring ran the legacy chain | the default arm is now the paper's: merge theta 4/kappa 1/nb 10, B-spline lane smoother, inside/outside vote, axis-ray marching, PotSAC top-10, rim 1.0/0.1/20/steadiest |
| 2 | neighbour clamp in `detectSeparateLineSegments` (`6194959`, ticket 274) | `nearestKSearch` returns fewer than k on a short chain and the loop still read slots k+1..n -> SIGSEGV | Pot C 01 EXIT 139 -> 0; six guard lanes bit-identical (max&#124;dxyz&#124; 0.000000) |
| 3 | no-discard full walk as the default (`263`, shipped in `b289e87`/strip) | largest-component + clock sort discarded dots and exploded on multi-strand bags | `P22` Bl1 4.43 mm / 15.8% -> 0.57 / 95.1; `P03` Bl0 0.52 / 100 |
| 4 | stop at the weld, 12 mm (`267`, `SFS_STOP_NOFRESH`) | at the end of the rim the walk leapt 124.6 mm to a far leftover dot: one 11.1 mm jump in the export | `P03` Bl1 463 / 3.18 / 41.9 / 1 jump -> 333 / 0.90 / 57.4 / 0 jumps, largest step 5.7 mm; five guard lanes digit-identical |
| 5 | growth gate 4.0 -> 3.4 deg (`271`, `47c7705`, `SFS_PAPER_THETA`) | the exterior surface ran over the crest into the roll-over, so crease and lip came back as two parallel rows 4-5 mm apart | `P03` Bl1 coverage 57.5 -> 99.0 (median 0.85 -> 0.49); `P03` Bl0 holds 100; guards at bar or better |
| 6 | walk seeds in the largest lump (`287`, `8e1e514`) | the seed was the dot nearest the cloud centroid; on four multi-lump bags that landed in a debris lump 32-54 mm from the rim, so the stop rule correctly ended the walk on the wrong structure | `C01` Bl1 81 / 41.06 / 0 -> 226 / 0.575 / 100; `J01` Bl1 82 / 23.3 / 0 -> 184 / 0.601 / 100; `C01` Bl0 25 / 51.62 / 0 -> 207 / 0.682 / 98.55; `J01` Bl0 47 / 29.27 / 0 -> 170 / 0.582 / 100; zero jumps; single-lump guards bit-identical |
| 7 | frozen input corpus (ticket 290) | clouds were derived per run and deleted, so no past score could be recomputed or compared | 148 clouds in `original_samples/SfS_pp/Point/` (143 released + 5 derived), with md5 and point-count manifests; the derived five match their mesh bbox to 0.031 mm |
| 8 | symlink staging (`291`, `acc9943`, `scripts/stage_piece.sh`) | every job copied its cloud and mesh into its stage tree | 108 bytes copied per piece instead of up to 90 MB; the inputs are byte-identical by construction, and identity claims were restated where the pipeline is deterministic |
| 9 | staging header read without a pipe (`292`, `19b78a7`) | `head -20 "$1" \| awk ... exit` under `set -euo pipefail` could SIGPIPE and abort the stage -- 22 of 148 pieces failed once each, hidden by the retry | fixed and verified against three corpus clouds (999810 / 1000026 / 840964 points as their headers say) |
| 10 | build from a commit (`288`) | a build could be of any tree, and `build.sh --target nurbs` silently compiles a pre-247 duplicate (ticket 282) | `git archive 8e1e514` reproduces binary `a28d10af...` bit-identically, and the eight-lane gate reproduces the table pointwise (max&#124;dxyz&#124; 0.000000) |
| 11 | mesh stage refuses to guess (ticket 277, commit 66d4ad9) | with SFS_AXIS_FILE unset or unopenable it printed one line and kept size order: Surface_0 became whichever cluster was larger, Bl0/Bl1 stopped matching the authors' lanes, and the run read downstream as a method failure | all four no-axis paths now exit 42 with the variable named and no surfaces written (unset and missing-path both proved before/after in run 20261025-2356_66d4ad9_p277-axis-loud); a normal run is unchanged -- identical classify line 10/10, worst pre-vs-post 0.6255/0.6094 mm against the stage's own 0.6255 mm draw spread |

**Removed, because they were measured and they did not work** (all deleted from main in `538357c` and
`67ff3d7`, gate: the strip is behaviour-identical, max&#124;dxyz&#124; 0.000000 on four lanes): the vote
repair 2-opt (262), loop-ness selection (263, it picked an 8-point satellite and crashed), the blind
density filter (261/248 -- it ate 433 of 1082 rim dots and was never the paper's rule, which is a
distance-to-line filter), the braid pre-filter gate (261), and the guided distance filter (264 -- it
removed the far arc exactly and moved no score). The paper's actual K-D idea (keep dots near the fitted
edge line, delete scatter) remains UNPORTED and untested.

**The result, in one line**: **281 of 292 sound lanes at bar (96.2%)** -- 283/294 valid, 283/296
measured -- at the shipped defaults, theta 3.4, on inputs that can be staged again (section P has the
method, the per-pot line and the eleven misses). The old 194/214-at-bar (~91%, section J) and the
265-of-294 tally both belong to a different binary, a different growth angle and clouds that no longer
exist; quote only the 292 number.

**What this ledger still cannot say, 2026-10-25**:
- Whether any of it improves **joins**. E1's actual question is whether the extracted edges let SfS++
  find correct reassemblies; the 96.2% is extraction against the authors' own lines, and no run since
  the strip has measured join success.
- The eleven below-bar lanes now have their "why" (ticket 293, and the paragraph above): `C03` Bl1 is a
  partition mismatch, `I25` both lanes are a **label inversion** (one curve pair counted twice), and the
  eight are one mechanism in three causes, of which only the chord is visible in a boundary set. What is
  still missing is not the mechanism but the **fix**: seven of the eight need curvature on the kept face
  or a merge rule that refuses to join across folds, and neither is built.
- The merge's Step 3 is the paper's own rule and refuses on curved faces; it is a limit, not a defect
  (ticket 276), and no threshold fixes it.
- The mesh stage draws from an unseeded `std::random_device`
  (`mesh_processing_headless.cpp:1526-1527`), which puts a piece-dependent 0.1-0.9 mm band on some
  pieces' exported lines.
- `Pot_J_Piece_09` is unscored by the conservator's ruling on its reference (section N).

## R. The 296-lane score adjudicated (2026-10-25, ticket 295) -- one mechanism, two symptoms, four interior misses

**Result in one line: 283 of 291 valid lanes at bar (97.3%)**, after the conservator struck Pot C 03 Bl1 as
an invalid reference. Nothing in the code changed in this round: every number below rests on the change set
in section Q, scored at the shipped defaults (theta 3.4, largest-lump seed, no-discard full walk, 12 mm
terminal stop, the 274 clamp).

**The six claims the conservator made from the ticket-294 figures, each measured** (run of record
SfSpp/runs/20261025-1824_ca18c8f_p295-lanes/, job 33761881; gate reproduced 385 of 385 ticket-293 numbers,
worst delta 0.0050 mm):

| Claim | Verdict |
|---|---|
| Pot I 25's labels are swapped | Holds with qualification -- it is a **naming inversion**: on 158 of 163 pieces their Surface_0 is the inside; I 25 and J 14 invert their own order. Both releases' lines ride the **same physical faces** (0.249 / 0.242 mm apart) |
| Pot C 03 Bl1 traced the base | **Holds** -- see section N; the lane is now struck |
| D 22 / D 27 ours is the better edge | Does NOT hold on D 22 and holds with qualification on D 27. D 27's two are small insets (7.2 / 16.2 mm). On **D 22 OURS is the 18 mm chord** (theirs runs 43.28 mm round the corner; tilt under theirs 66.3 deg median, under ours 29.6 deg) -- ticket 297, and the earlier ledger claim was backwards |
| H 10 is a mismatch, or our surface is bigger | **Does not hold** -- our face is **14% smaller** (633.9 vs 734.9 mm2) and the whole 12.6 mm stretch sits over a 629-point ribbon cluster we dropped |
| I 06 / I 13 -- our mesh is bigger, so our line is bigger | **Does not hold** -- the faces match to 1.4-1.8% in area and the band under their line is coplanar (1.4 / 1.7 deg, 0.006 / 0.007 mm) |
| H 02's lines stop at the base-rim | **Holds, both reasons corrected** -- see below |

**Pot H 02, the corrected reading:** the turn is real and sharp (material just outside our face at 48.4 deg
median on Bl0, 44.2 on Bl1, 54.8% / 48.5% of it beyond 45 deg) and it is **continuous material, not a scan
gap** -- the unlabelled corridor sits 1.525 / 0.667 mm from the kept face with 282 / 36 of its points within
one sample spacing, Pot C 03's corner-ring signature (section K). But the authors' line does not go past
ours: on Bl1's 59.4 mm stretch their dots are **0.221 mm above our wall face and 4.67 mm inside our edge**.
Ours is the outer edge and the better one. Bl0 is clean (0.830 / 1.332 / 2.090 mm, 71.2% on our edge).

**No welded break facet anywhere.** On all nine adjudicated lanes **0.00%** of the 2 mm band our kept
material contributes under the reference is pitched more than 45 deg off the authors' own normals (median
0.7-5.5 deg, offset 0.004-0.023 mm). "Our surface swallowed part of the break face" is not in this sample
and is no ground for a growth or classify change.

**The mechanism is PARTITION -- which faces are kept**, not the walk seed and not a weld test. Our edgeline
is the boundary of the *labelled* face; immediately outside it lies real pottery that growth left unlabelled
(H 02: a 2311-point corridor in the 2 mm band, 89 of them on Bl1; E 16: 68.6 deg; C 03 90% and D 22 92.3% of
the stretch nearest unlabelled; H 10 100% over a dropped cluster). Where that material *is* labelled, our
face extends 2.4-9.6 mm past the reference on the same plane.

**The growth gate cannot be the fix, and this is now arithmetic.** H 02's straddling pairs step a median
**3.23 deg** with 52.7% at or below the 3.4 deg gate (ticket 281), while Pot D P03's severing bottleneck is
**3.45 deg** and P 22's **3.06** (ticket 271). A gate loose enough to cross H 02's base-rim re-breaks the
lane that fix repaired. What remains is a **partition** change (keep a third surface / label the corridor),
or base handling, which the paper itself lists as future work (papers/text/sfspp-2502.13986v1.md:460).

**What this round cost and what it bought.** Cost: one instrument ticket (295) plus its lead probes, no
build. Bought: a valid denominator (283 of 291), a dead hypothesis (welded facet), a named mechanism
(partition), and the distinction that matters for the next phase -- **only 4 of the 11 remaining misses are
on the interior line the assembler reads** (D 22 Bl0, D 27 Bl0, E 16 Bl0, I 25 Bl0), and on two of those the
conservator's own reading is that ours is the better edge.

**The interior slot is guaranteed by construction, and must still be proved per bundle** (corrected by the
conservator, 2026-10-25). Our surface order is interior-first: classifyAndOrderPaper234 sets Surface_0 to the
interior face and the writer names Surface_0 -> Breakline_0, so every piece we produce feeds the assembler an
interior edge without a per-piece swap decision. What section B's B-swap records is a **pre-fix workaround**
from the period when the surfacing order was not interior-first; needing a swap now would be a bug signal,
not a routine step. The one way the slot could still be wrong was mechanical: without SFS_AXIS_FILE the
classify step silently kept size order (ticket 277). **That hole is closed** -- since ticket 277 the mesh stage
exits 42 with a message naming the variable instead of exporting surfaces it cannot name, so a mislabelled
bundle can no longer appear silently; the proof per bundle stays (a) the classify line printed for every
piece, (b) a measured interior test on the two surfaces, (c) Breakline_0 riding the interior one. The
authors' own data is the exception worth watching: on 2 of 163 pieces their Surface_0 is the exterior
(I 25, J 14), so a ceiling arm built from their _0 files is not interior-consistent on those pieces.

## S. Seating after the strip: the interior slot proved, and both arms seat (2026-10-25, ticket 296)

**Pot A, 8 pieces, 15 joins, identical meshes and axes, only the eight Breakline_0 files differing:**

| arm | run | job | sherds | joins |
|---|---|---|---|---|
| CEILING (authors' Breakline_0) | 20261025-2234_3d5d537_p296-ceiling | 33780523 | 8/8 | 15/15 |
| TEST (ours, shipped defaults) | 20261025-2234_3d5d537_p296-test | 33780524 | 8/8 | 15/15 |

Drift 0 sherds, 0 joins. Assembler pinned /opt/sfs-pristine (upstream 9195c016) in sfs_pristine_assembly.sif,
binary md5 0fd8d707ceb3f9cffd08d8951c43ccda identical in both arms; edge cbf747dc3172fe0bbd188822df14092a,
mesh fb3fd055d30fb08ccce48dba7d49a879. The ceiling arm reproduces the 2026-10-20 reference exactly, so the
harness is sound and **the B-swap in section B is not needed any more**.

**The interior slot is proved by measurement, not assumed** (the conservator's point, 2026-10-25): our
Breakline_0 sits **0.17-0.25 mm** off Surface_0 and **2.9-4.8 mm** off Surface_1 on 8 of 8 pieces; Surface_0 is
the negative-concavity face (m = mean(n.r) with r away from the axis) on 8 of 8 with |m| 0.464-1.703 against a
0.10 abstain line, radius agreeing 8/8; the classify step did real work (1 kept, 7 swapped, theta 3.40000 on
all eight, SFS_AXIS_FILE staged so the no-axis guard never fired). The authors' own bundle reads 8/8 the same
way, so the instrument is calibrated on known-good data. Mechanism at 3d5d537: classifyAndOrderPaper234 at
mesh_processing_headless.cpp:1990, called :2178 after the size sort, guard :1995-1996, swap :2027-2031 / keep
:2033 -> Surface_0=interior; rename Surface_0 -> Breakline_0 at edgeline_extraction_headless.cpp:3517-3525,
written :3536.

**What it does not say.** One pot, fifteen joins: a readiness check, not a corpus result, and it does not move
283/291. Both arms saturate, so **drift 0 is a floor, not a ranking**. Our own surfaces appear in neither arm
(both load the corpus Surfaces/), so this tests the line only; Breakline_1 was staged inert and never read; no
part_acc/chamfer was computed from the saved transforms.

**A labelling trap in the output itself:** the assembler prints the string "Sherd accuracy" twice
(data_structure.cpp:1004-1005). The second line is the **joins** count -- quote it as joins, never as a second
sherd score.

Retained on Spartan: prep out/geom 27 MB (surfaces are not byte-reproducible, unseeded ray-cast draw) and both
arms' out/Result (~363 MB) as the evidence behind the two accuracy lines. Deleted: stage/ 582 MB and the two
dataset/ trees, 242 + 121 MB, each recorded in that run's out/GEOMETRY_DELETED.txt.

## Pending proofs (not yet in this ledger)
194 (B harmless -- LANDED regression, in F above), 195 (D harmless -- LANDED regression, in F above), 196 (A control holds -- LANDED regression, in F above), 189/190/193 (E/F/J cure-or-vacuous). Each enters above ONLY on a landed PASS with E2E numbers.