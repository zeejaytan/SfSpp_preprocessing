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

## E. E2E proofs of the new default (de-doubled input seats sherds)
180 (first seating): Viterbi single loop 220/closure 1.48, rim-med 0.76; E2E jobs 33470102/3/4 COMPLETED 0:0, C_180 Total 165 x3, 3/3+3/3, T_0to_0 x3. APPLIED as proof de-doubling seats C01.
186 (default recipe x6): 185-v3 loop bundled, jobs 33482185/86/87 + lead duplicates 33482198/99/200 all COMPLETED 0:0, C_186 155/24, 3/3+3/3 x6 deterministic. APPLIED -- this is the default.
191 (transfer to G): 3 doubled edges cured with 185 v3, jobs 33484406/07/09 COMPLETED 0:0, G_191 5/7+3/10 x3, +1 sherd over fresh bar (60/39: 4/7+3/10), controls G_orig 7/7+10/10 + A green. Supersedes 83. APPLIED.
Owner tickets: 180, 186, 191.

## Pending proofs (not yet in this ledger)
194 (B harmless), 195 (D harmless), 196 (A control holds), 189/190/193 (E/F/J cure-or-vacuous). Each enters above ONLY on a landed PASS with E2E numbers.
