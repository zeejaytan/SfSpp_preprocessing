# Recovery on the 314 bag — M134d-form envelope-retreat, re-derived

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 143 (314 bag: 292 + X2/X4 admits incl O37; greedy-314 strands @140, gate 3.9851 best on record; forced-314 probe 241/3.9732/uncovered-0 NOT banked — 58mm jump stays probe-class, confirmed) + 134 (M134d rule-form: per-bag latch, state trigger; verbatim latch goes stale per 125) + 133 (greedy strands via T13-suppression — the mechanism to beat)

**Status:** results-in

**What to deliver:** the M134d-form walk on the 314 bag: re-derive (do NOT transplant) the per-bag latch anchor + state-function trigger on 314 per 134's rule-form, then walk. Bar: greedy-314's marks beaten honestly — pushes above 140-strand equivalent, gate at/below 3.9851, uncovered strictly below 15 (143's greedy strand count is control, not bar), zero UNLICENSED jumps >=40mm; forced-chain probes stay probe-class (any banked step >25mm must be licensed per 137/138 segment-credit or it does not bank). If the latch will not arm or the trigger will not fire honestly on 314, refute with the arming/firing record — do not retune constants to force it.

**Starting position:** .scratch/pota143_repro/ (314 bag + greedy/forced controls), pota134_repro/ (M134d RULE-FORM — the form, not the numbers). Login-node numpy only — no Slurm, no E2E. New scratch pota144_repro/; renders under laptop artifacts/pota144/ (walk vs ORIG, latch-arm record, licensed vs unlicensed accounting).

**Rules:** greedy-314 control reproduced first or stop; read-only inputs, zero ORIG points (ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits.

- [ ] Latch re-derived + trigger firing record on 314
- [ ] Walk vs greedy-314 (pushes, gate, uncovered, jump accounting)
- [ ] Verdict + recipe or arming refutation

## Comments (worker, 2026-10-19 -- laptop numpy only; COMMIT NOTHING)

**Verdict: RECOVERY-GATED LANDING on the dense bag -- all bar legs hold on walk M144. Recipe banks (T144 + M144).**

**0. Control GREEN (reproduce-or-stop PASSED).** Rebuilt 314 in .scratch/pota144_repro (p144_step1.py, walk+gate verbatim from p143_step6): 314 = 292 + 22 grids; greedy-314 140/314 = 0.4459, strands 140 at slot 221, 0 jumps, gate med 3.9851 / uncovered 91 / spans [(115,205)] -- exact-equals 143. Admitted-32 (314-282) visits on-road: 24/32 (poolA 10/10 seqpos 13-117, grids 14/22; unvisited 8 = slots 305-312). ORIG = Bl_0 gate-evidence + seating-measurement only; zero ORIG points copied. No Slurm, no E2E; tickets 39-143 read-only; COMMIT NOTHING.

**1. Latch re-derived + trigger firing record (p144_trigger.txt stated BEFORE any recovery run; p144_freeze.txt).** Latch L144 (314's own): strand slot 221 [25.13,66.52,424.99] -- IDENTICAL far-arc dot as 282's strand (same refusal site, different walk: 140 vs 116); T13 suppressed (0.4459>=0.40, 133 mechanism reprised); envelope = walk's own max greedy stride 21.72 (median 2.83, n>40mm=0); key-space at strand: K-net(34) key-fresh 0 (local dead) / global key-fresh 136 @43.24 -- same signature as 282's FIRE case (128 @43.24, twin slot 228 d=0.00 key-stale). Trigger T144 FIRED: (i) admitted on-road majority 24 vs 8 HOLDS (stuck analogue 0 vs 3 SUPPRESS; 282 recheck 3 vs 0 FIRE, consistent with banked T134) AND (ii) newly-covered sign >0 HOLDS (+2 vs 292-greedy O44/O97, +18 vs 279-greedy). Why majority-form not verbatim ==1: the 8 unvisited grids sit beyond-strand in the open span (seats O163-166/O173-175, all on-arc seatDO 0.5-3.3 junk 0, minDistRoad 53-66mm -- unreached, not orphaned vs stuck 101.6mm); ==1 would false-negative a bag whose forced probe banks everything. Majority + payoff-sign keeps 282's verdict, fires on 314, still suppresses mostly-orphaned rungs; zero numeric constants. Slim-payoff note: (ii) vs 292 is +2 only; tail ORIGcov flat (47,47,47) -- stuck-like locally, honest signal whole-walk as in 134.

**2. Walk vs greedy-314 (M144 = M134d form, 314 values; p144_step3.py).** Greedy-verbatim re-strands 140/slot221 (latch re-confirmed); envelope asserted == freeze 21.72; then index-advance (key-stale allowed, d>=1mm twin-skip reused) + 12 retreats (max 21.56, inside envelope by 0.16) + 0 forwards; HALT at 34.27-over-envelope (same pocket as 134's HALT). M144: seqlen 322 / unique 310/314 / gate med 3.9736 / <2mm 31.7% / gaps5 99 / maxstep 22.8 / ORIGcov 116/211 / uncovered 0 / spans []. Bar: pushes 310>140 HOLD | gate 3.9736<=3.9851 HOLD | uncovered 0<15 HOLD | 0 steps>=40mm HOLD | 0 banked steps>25mm HOLD (max 22.8, no license needed). Vs forced-314 probe (241/3.9732/0, jumps 43.2+58.0, NOT banked): walk BEATS (+69 unique), uncovered MATCHES (0=0), gate ties (+0.0004, sub-noise), big jumps 0 vs 2. Left unsequenced: 4 slots (133/160/197/200) -- ALL key-stale dup-twins (d=0.00), the same four 134/137 left; coverage-identical, not hidden. Per-span maxDO: C36/37 2.23, C46/47 1.24, C96/97 0.96, C165 2.07, C173 3.74, O37 2.23, C115-205 4.61 (max point-DO 4.95).

**3. Recipe to bank (T144 + M144).** Freeze strand; evaluate (i)+(ii); if FIRE, greedy-verbatim then index-advance in K34 (key-stale allowed, d>=1mm), retreating at index-stall to mm-nearest road position with index-unvisited K-net inside the walk's own max-greedy-stride envelope else HALT; ratio gate latched-overridden once fired; no forwards teleports (any banked step >25mm needs a 137/138-class license -- none stated, none needed). Envelope, visits, payoff all derive from the frozen 314 walk/bag; no ported numbers (24.67 never appears).

**4. Renders + paths (eye-checked).** artifacts/pota144/p144_walk.png (blue M144 walk tracks green ORIG arc full loop, orange X = latch strand slot221) | p144_steps.png (step profile max 22.8, envelope 21.72 / 25mm / 40mm lines untouched). Texts mirrored: artifacts/pota144/{p144_control,p144_freeze,p144_trigger,p144_walk,p144_verify}.txt. Scratch .scratch/pota144_repro/ (step1..step4 + trigger.txt + npy). Tickets 39-143 untouched (read-only); COMMIT NOTHING done.
