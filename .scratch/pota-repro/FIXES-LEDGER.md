# Lane fixes ledger — FIRST DRAFT (worker draft, 2026-10-20, COMMIT NOTHING)
Source: intent E1 + issues 39+ (cure story) / earlier as needed. Format: symptom / proof / decision / owner. Vehicle: cure-potA @ bffefb6, k=5/b=3 shim unless noted.

## 80 float-cause (diagnosis, binds swap+forest)
Symptom: 110/129 fresh Bl_0 float>2mm, D/E/I whole-pot 5-9mm systematic shifts.
Proof: login-node screening only, 0 Slurm jobs; fresh-S0 matches ORIG-S1 on B8/9 C2/4 D26/29 E29/31 F6/7 G6/7 I28/30 J9/12; renders F02_swap.png, E10_forest.png eye-checked.
Decision: SWAPPED ~94 (surface order swap upstream of walk) + FOREST ~14 (T67 doubled-loop on swapped base); 19 tracking = unswapped. Recipes handed to 78/79/successors; no E2E from 80.
Owner ticket: 80 (worker 2026-10-18).

## 81 swap cure Pot F (LANDS, recipe anchor)
Symptom: F 6/7 swapped per 80 census; F06 Bl_0 n=45 trips 50-pt loader gate (main.cpp).
Proof: jobs 33343950/52/53 + 33344601/33344615/33344617 all COMPLETED 0:0; SXC gate F02 0.61-F06d 0.65mm 100%/0j; E2E 6/6+9/9 x3 bit-identical; controls A 8/8+15/15, F_orig 6/6+9/9; renders eye-checked (lead).
Decision: LANDS as SXCD (slot-exchange S0<->S1 + Bl_0<->Bl_1, F06 45->55 same-loop resample, zero ORIG pts). Roll remaining pots per census.
Owner ticket: 81 (lead write-back 2026-10-18).

## 83 swap cure Pot G (landed-SHORTFALL, gate green)
Symptom: G census corrected in-ticket: swapped=G01-G06 (not listed set), G07 sole control.
Proof: jobs 33359827/28/29 COMPLETED 0:0; gate 0.53-0.61mm 6/6 green, no densify (min n=77); E2E 4/7+2/10 x3 bit-identical vs bar 4/7+3/10; edge (2,3) 0.165rad/47.8mm borderline counted wrong.
Decision: SHORTFALL by one borderline edge; rims exonerated (no 78 handoff); miss is search-side (P4/P6 thrown, P7 unplaced).
Owner ticket: 83 (lead 2026-10-18).

## 84 swap cure Pot D (LANDS)
Symptom: D 26/29 surfaces agree swap; D22/D28/D29 controls; D12/D14/D21 swapped-base specials cured by same exchange (clean interior in Bl_1 slot).
Proof: jobs 33361199/200/201 COMPLETED 0:0 (lead-verified); gate 26/26 <2mm (e.g. D10 0.61, D25 0.58; min n=56 D27); E2E 22/27+49/66, 21/27+47/66, 22/27+49/66 vs 63 bar 15/27+17/66; ORIG 22/28+53/66 in-vehicle.
Decision: LANDS pure SXC, no densify; next roll-out E (guarded, behind 82 crash-cure).
Owner ticket: 84 (lead landing 2026-10-18).

## 90 swap cure Pot E (LANDS)
Symptom: own census 30/31 swapped, E18 clean control; E07 excluded (both slots neither, to 78), E18 untouched (forest Bl_0, exterior-correct Bl_1).
Proof: jobs 33380562/33380749/33380751 COMPLETED 0:0; gate 29/29 <2mm (E22 0.51-E16 0.89); E2E 29/31+56/62, 26/31+49/62, 23/31+38/62 vs bar 7/31+4/62; controls E ORIG + A green.
Decision: LANDS pure SXC (min n=63, no second variable); E07/E18 handed to 78.
Owner ticket: 90 (worker 2026-10-19).

## 91 swap cure Pot I (STOPPED honest, sets up 94)
Symptom: own census 28 swapped, I25/I30 controls; I28-I30 no GT either side (E2E-excluded per D22 precedent).
Proof: 0 Slurm jobs (honest stop per brief); gate 27/27 GREEN on exchange set; min GT-scored new-Bl_0 I27 n=49 <= 50-pt gate; manifests pota91_I_SXC_bun/md5 green; renders eye-checked.
Decision: STOPPED at densify check, no E2E forced; densify split to ticket 94.
Owner ticket: 91 (worker 2026-10-18).

## 94 densify I27 + E2E (LANDS, completes 91)
Symptom: I27 n=49 blocks 91 bundle (loader gate).
Proof: I27 49->55 same-loop resample (81/F06 verbatim); re-gate 27/27 GREEN (I27 0.47/100%/0j); jobs 33387455/56/57 COMPLETED 0:0; E2E 25/27+54/65 x3 bit-identical vs bar 8/27+3/65; I_orig 25/27+59/65 exact in-vehicle.
Decision: LANDS; Pot I needs no further rim work (I2/I13 flips = search-basin data).
Owner ticket: 94 (worker 2026-10-18).

## 92 swap cure Pot J (LANDS)
Symptom: own census 8 exchanged (J02,J04-J07,J10-J12), J01/J03/J08/J09 controls byte-identical; J02 forest-Bl_0 cured via exchange (clean interior in Bl_1 slot).
Proof: voids 33387270-272 (mount-path miss, J_SXC never ran); valid jobs 33387858/59/60 COMPLETED 0:0; gate 8/8 <2mm (0.55-0.75); E2E 7/10+13/18 x3 bit-identical vs 63 bar 2/10+1/18; ORIG 8/11+16/21 in-vehicle.
Decision: LANDS pure SXC (min n=53); J needs no rim re-roll.
Owner ticket: 92 (worker 2026-10-18).

## 95 resample J (HOLDS, author-regime step)
Symptom: test 89 R-RESAMPLE (uniform 1.8mm closed loops) without breaking 92 seating.
Proof: jobs 33388692/93/94 COMPLETED 0:0; gate 11/11 <2mm (J07 0.39, J10 0.36), 0 jumps>5; E2E 7/10+13/18 x3 exact = 92 landed; controls green, renders eye-checked.
Decision: HOLDS (regression-or-better: equal); resample moves toward author regime safely.
Owner ticket: 95 (worker 2026-10-19).

## 93 swap cure Pot B (LANDS)
Symptom: own census corrects 80: B02-B09 all SWAPPED (2x2 + surfaces), B01 forest/CLEAN-excluded to 78 (r=5.09/j24, interior loop missing).
Proof: jobs 33387265/66/67 COMPLETED 0:0; gate 8/8 <2mm (B03 0.61-B08 0.49; B02 1.15/68%+1j pre-existing); E2E 5/9+3/15, 6/9+5/15, 6/9+5/15 vs bar 4/9+2/15; B_orig 9/9+15/15 in-vehicle.
Decision: LANDS pure SXC (min n=70); P2 flip + P5/P8 misses = search-basin, rims exonerated.
Owner ticket: 93 (worker 2026-10-19).

## 98 swap cure Pot C (LANDS, partial pot)
Symptom: verifies 97: C02+C04 clean swaps, C03 control, C01 fused both slots (excluded to 78).
Proof: pilot failures 33391755/56/57 FAILED <1min (inner-script quote typo); valid 33392081/82/83 COMPLETED 0:0; gate C02 0.78/98.5, C04 0.73/93, C03 0.95/86.8; E2E 2/3+1/3 x3 bit-identical = S24 bar, above fresh 0/3+0/3, -2/-4 under ORIG 4/4+5/5.
Decision: LANDS SXC on C02/C04 only; C01 regeneration stays with 78.
Owner ticket: 98 (worker 2026-10-18).

## 82 segfault cure E_G (crash-cure + honest partial)
Symptom: guarded E bundle crashed assembler at launch (~0.4s, Hierarchy-Batch-P78) on E_G while E_fresh/E_orig/A ran.
Proof: cause bound NOT rim size: all 31 E_G Bl_0 bare xyz-only, reader data_structure.cpp:245 leaves features empty, segfault ranking_system.cpp:1113; v1 jobs 33343794/95/96 COMPLETED (0/6+0/2 x3, 139 hypotheses); v2 jobs 33349656/57/58 COMPLETED (2/24+1/40, 2/24+1/40, 0/24+0/40; 17k hypotheses) below E_fresh best 7/31.
Decision: LANDED as crash-cure + honest partial per user option 1; E real cure = swap roll-out (83+), then guarded-E on swapped base.
Owner ticket: 82 (lead 2026-10-18).

## 143 true densify (detection LAND, walker BLOCKED)
Symptom: all prior densify interpolated the bag (midpoints add zero true edge info); floor 8 uncovered under point-gate (137) with O37 open.
Proof: laptop numpy only, 0 Slurm; 4-rung ladder r0/rA/r1/rB/r2 + ROR ring; 32 fresh TRUE dots 32/32 on-arc junk 0; forced-T13 probe uncovered 8->2 (292) and 314 forced probe uncovered 0 (ORIGcov 116/211) but 58mm jump unbanked; greedy strands (ratio-gate suppression, 133 family).
Decision: detection LAND (extraction NOT saturated), walker BLOCKED; needs M134d-form envelope-retreat re-derivation (next: 144).
Owner ticket: 143 (worker 2026-10-19).

## 144 recovery on 314 (RECOVERY-GATED LANDING)
Symptom: greedy-314 strands at 140/slot221 (0.4459>=0.40 suppresses T13), gate 3.9851 best on record.
Proof: laptop numpy only, 0 Slurm; latch L144 re-derived (strand slot 221, envelope = own max greedy stride 21.72); trigger (admitted-majority 24v8 + payoff +2) FIRED; walk M144 seqlen 322/unique 310/314, gate 3.9736, uncovered 0, maxstep 22.8 (0 banked >25mm, 0 >=40mm); beats greedy (+69), ties forced-probe gate without its jumps.
Decision: recipe banks (T144+M144, no ported numbers); C01 314-trace staged to 145 E2E.
Owner ticket: 144 (worker 2026-10-19).

## 179 input-side seating (gating feature, no assembler touch)
Symptom: 176 TRUE walk (439 dots, doubled) vs author ORIG (211) field-by-field diff names the assembler-starvation features.
Proof: laptop-side only, 0 Slurm, assembler never entered; author 211/380.0mm/closure 1.80/0 gaps/D-tokens 3 vs 176 439/691.4mm/closure 17.67/3 gaps/34 tokens; rim med 0.95; curvature constant 1.9058e-42 identified.
Decision: gating feature + numeric bar named (single closed ~1.8mm loop); staged to 180/186 builds.
Owner ticket: 179 (worker 2026-10-20).

## 180 single-loop input (input legs COMPLETE, E2E STAGED-READY)
Symptom: de-double 439-dot walk to author-ordered single track without key leak (author order only, xyz stays ours).
Proof: laptop numpy only, 0 Slurm; Viterbi single 220 dots/395.6mm/closure 1.48/0 gaps/D-tokens 4; rim-truth med 0.76 (<2mm 100%); bundle slot-hygiene ONLY C01-Bl_0 differs (d4793a55->8ab5bbf2); staged .scratch/pota180_repro + RELAY.txt, no E2E (no SSH).
Decision: E2E LANDED post-staging (lead relay jobs 33470102/3/4 COMPLETED 0:0): C_180 Total 165 x3, pruned 27/28/27, 3/3+3/3, T_0to_0 x3; 179 falsifier (Total stays ~40) not triggered. Density kept, doubling removed (181 distinction).
Owner ticket: 180 (worker prep + lead relay/E2E 2026-10-20).

## 181 no-densify arm (REFUTED honest negative)
Symptom: falsifier: is pre-densify M134d walk (290 rows) already at ~0.95-med class without densify?
Proof: laptop numpy only; M134d vs author med 4.2488 (+3.30 over 176 0.95), ORIGcov 99/211 (46.9%), 98 gaps>5, arc 1361mm (3.6x author), D-tokens 73; D-proxy validated on author loop first.
Decision: REFUTED; no bundle/E2E staged per falsifier rule.
Owner ticket: 181 (worker 2026-10-20).

## 182 trace double-walk (mechanism, DONE)
Symptom: HOW does the walker double-walk the new single-surface densified edgeline (post-176)?
Proof: laptop replay only; 79/438 retrograde steps, 49 flips, lateral scatter ~0.3/1.3mm; one station-lap costs 434 dots/650mm vs author 211/380mm; 67 face-hop ruled DIFFERENT (disjoint loops + 5.5mm hop vs within-lap weave); renders p182_order_trace + p182_station_sweep eye-checked.
Decision: zigzag across ~2-wide TRUE strip (not lapping twice); closure-check would only trim 5-dot tail; cure = single-track discipline (p180 Viterbi 220/closure 1.48 proves it).
Owner ticket: 182 (lead verdict 2026-10-20).

## 183 single-strand picker (arm 1, mixed, loses shootout)
Symptom: one dot per ring-station (key-free, e.g. polar angle) to force single loop.
Proof: laptop only; 202 dots/closure 0.85 PASS bar but arc +9%, D-alphabet 28 (fragmented spacing); render p183_order_trace eye-checked.
Decision: DONE mixed; LOSES to 185 (spacing evenness decided it).
Owner ticket: 183 (lead verdict 2026-10-20).

## 184 heading-rule walk (arm 2, honest negative)
Symptom: direction preference in greedy walker (penalise sideways) to hold single file alone.
Proof: laptop only; 24 configs x 6 seeds ALL miss bar; closest 327 dots/closure 45.1 vs bar <=240/<=2.0; correct move IS sideways half the time on 2-wide strip (strands rows, recovery leaps 12-38mm); render p184_order_trace.
Decision: premise REFUTED; discipline must come from strand separation (183/185), not direction term.
Owner ticket: 184 (lead verdict 2026-10-20).

## 185 thin-then-walk (arm 3, WINS shootout)
Symptom: collapse ~2-wide strip to centreline first, then verbatim walker (no walker change).
Proof: laptop only; 204 dots/arc 365.0/closure 1.79/0 gaps/D-tokens 2 (run 131)/rim-med 0.64; arc 5% short (smoothing shrink), 8 stations uncovered (kink 24-31); renders artifacts/pota185 eye-checked.
Decision: WINS shootout vs 183 (D28) and 184 (refuted); 186 bundles this loop for E2E.
Owner ticket: 185 (lead verdict 2026-10-20).

## 186 thin-loop E2E (laptop COMPLETE, E2E STAGED-READY)
Symptom: bundle 185-v3 loop for assembler (180 pattern port, NNEW 204).
Proof: laptop only, 0 Slurm; v3 md5 57e7077cec514c5e7511e63547bd, mesh walk md5 32b80e8b; slot-hygiene ONLY C01-Bl_0 differs (1b891676); segs rescaled 402->204, veto-absence asserted; renders p186_01_thin_vs_ref + p186_02_order_trace eye-checked; sbatch AC staged (A arms STEPS 8, C arms STEPS 4).
Decision: E2E LANDED x6 deterministic (worker chain 33482185/86/87 + lead duplicates 33482198/99/200, all COMPLETED 0:0): C_186 155/24, 3/3+3/3, T_0to_0 x3; falsifier not triggered; gate now pruning-side (pruned 24 below 30-40 band). Full-chain-by-worker + Comments-handoff rules banked.
Owner ticket: 186 (worker chain + lead duplicate 2026-10-20).

## 187 thin rollout Pot B (vacuous close, honest negative)
Symptom: does any Pot B Bl_0 in record (93 SXC) show 179 doubling (ratio>=1.2 + closure>2 + tokens>=10)?
Proof: login-node census only, 0 Slurm, md5sum -c read-only; B02-B09 ratios 0.99-1.05, closures <=1.92, tokens 2-4 (daylight on all axes); B01 scatter ratio 0.17 (no strip to thin); vehicle HEAD still bffefb6; re-running would byte-repeat 93.
Decision: vacuous close ACCEPTED (lead 2026-10-20); no bundle rebuilt, no E2E (refusing numbers above); E2E decline accepted.
Owner ticket: 187 (worker 2026-10-20).

## 192 thin rollout Pot I (vacuous close, honest negative)
Symptom: does any Pot I rim Bl_0 in record (94 SXC) show 179 doubling?
Proof: login-node census only, 0 Slurm; 30/30 SXC Bl_0 clean singles (closure 1.43-1.94, tokens 2-5); 17 doubled fresh-Bl_0s refused as non-rim (12 foot + 5 forest per 91, rim-truth 5-11mm vs 0.7 bar); live 60/60 manifest OK; rerun would re-print 94 (25/27+54/65 x3, jobs 33387455/56/57).
Decision: vacuous close ACCEPTED (lead 2026-10-20); lesson banked: run rim-truth before thinning -- foot/forest content refused, not beautified.
Owner ticket: 192 (worker 2026-10-20).

## 188 thin rollout Pot D (vacuous close, honest negative)
Symptom: does any Pot D rim Bl_0 in record (84 SXC) show 179 doubling?
Proof: login-node census only, 0 Slurm; 29/29 clean singles (ratio 0.97-1.14, closure <=1.92, tokens 3-4, rim-truth 0.51-0.86); P22 ratio 0.26 = non-planar-loop ruler artifact (closure 1.67, exonerated); 13 doubled fresh-Bl_0s sit runtime-inert in Bl_1 post-84-exchange; render p188 fresh-vs-SXC eye-checked; rerun would duplicate 84 (22/27+49/66 x3, jobs 33361199/200/201).
Decision: vacuous close ACCEPTED (lead 2026-10-20); 84 stands.
Owner ticket: 188 (worker 2026-10-20).

## Honest negatives that closed a branch (ticket + refusing numbers)
Symptom: each row is a branch killed by numbers, not by opinion; full trials in ticket Comments.
Proof: 65 Arm-S no-op (headers-only, teleports intact, E2E 0/3+0/3 x3); 66 true-reorder NULL (jumps->0 but gate flat, E2E 0/3+0/3 x3); 68 split-select NULL (both arms jumps->0, gate flat, E2E 0/3+0/3 x3); 69 walk guards re-tile only (GUARD ~4mm off, SPLIT n=18, no E2E per Rules); 70 boundary no arm at bar (M4 doubling collapsed but loop ~3.8mm off); 71 face NULL (F-NORM 5.61->14.91mm worse, jumps 3->1); 97 touch-split negative (every C01 component >=3.28mm off, no E2E); 85 crest 85B NULL (share 43.7% met, E2E discrete-identical fail 33363530-32); 87 flip-bound <=0.5mm (third loop ruled out BY CONSTRUCTION, 33366075/092/093); 88 matcher-fix REJECTED by user (mechanism kept as input-side criteria, axis veto 0.436); 96 segflags INERT (all fresh info=0, consumers gated on header, no E2E); 145 C_FIN bar-not-beaten (2/3+1/3 x3 = 98 bar, C01 unseated); 184 heading-rule refuted (24x6 all miss, closest 327/45.1).
Decision: branches closed as stated; Pot C ceiling broken by thin-loop: 180/186 seat C01 3/3+3/3 x6 (2026-10-20); thin rollout to B/D/E/F/G/I/J per 187-193, B and I closed vacuous.
Owner ticket: many (65/66/68/69/70/71/97/85/87/88/96/145/184 as cited).
