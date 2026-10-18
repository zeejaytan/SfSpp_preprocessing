# Named-span bridge C96 — cross (96,97) without inventing dots

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 136 (detection CLOSED — all 8 uncovered bridging-class) + 135 (hit-list #3: C96 bridge sketch — sequence the flanks, license a T13-class teleport across the named span only) + 118+117 (presplit-then-walk precedent: honest chaining needs licensed teleports) + 134 (M134d recovery form: envelope retreat <= walk's own max stride)

**Status:** results-in

**What to deliver:** the first bridging ticket. Problem: span (96,97) is filter-dead (rej81 r1-FAIL nnb=0) — no dot will ever be admitted there, so the walk must STEP across it. Rule (ORIG-free, stated before running): license exactly one teleport whose endpoints bracket ORIG[96..97] (flank slots on the [89..95]-side to the [98..]-side — concretize from the M134d freeze: nearest sequenced slots to each flank, stated first); the teleport is licensed ONLY across this named span (no general jump-shortening — all other jumps still gated as in M134d). Test: M134d-form walk + licensed C96 bridge on the 282 bag. Success bar (all must hold): uncovered below 8 AND the C96 span covered (O96/O97 within 5mm) AND gate at/below 4.2488 AND no UNLICENSED jump >=40mm AND the bridge stated as a general rule-form (named-span license derived from the walk's own flank slots — never ported coordinates). If the flanks cannot be sequenced into launch position (walk never reaches a flank), refute with the sequencing — that says bridging needs presplit-then-walk (118+117) and C96 waits for the presplit ticket.

**Starting position:** .scratch/pota134_repro/ (282 bag, M134d form, flank slots), pota135_repro/ (C96 precision: filter-dead rej81, flank geometry), pota118_repro/ (presplit precedent). Login-node numpy only — no Slurm, no E2E. New scratch pota137_repro/; render under laptop artifacts/pota137/ (bridge step on arc, walk vs M134d, gate, jump accounting licensed-vs-unlicensed).

**Rules:** control reproduces 134's marks first (290/278u/gate 4.2488/uncovered 8) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; ONE licensed bridge, everything else gated.

- [x] M134d reproduced + bridge rule stated (flank slots, license bounds)
- [x] Bridged walk vs 134's marks (coverage, gate, jump accounting)
- [x] Verdict + recipe or presplit-ticket refutation

## Comments (worker, 2026-10-19 -- laptop numpy only; COMMIT NOTHING)

**Verdict: REFUTED as a landing ticket -- the licensed C96 bridge adds zero measurable yield. M134d already steps across the span (t=12, 12.2mm); point-coverage is at its floor (8) on the 282 bag by proof, so no teleport between existing slots can cover C96. The bridge is designatable but vacuous under the point-gate.**

**0. Control GREEN (reproduce-or-stop PASSED).** Rebuilt 282 in .scratch/pota137_repro (p137_step1.py): C=270 + SN124=8 + SN128=1 + SN133=3 = 282; M134d seq reloaded from p134_seq_d.npy (NOT re-walked): seqlen 290, unique 278/282, gate med 4.2488 / <2mm 29.3% / gaps5 98 / maxstep 25.8 / ORIGcov 99/211 / uncovered 8 spans [(36,37),(46,47),(96,97),(165,165),(173,173)] -- exact multiset-equals 134. ORIG = Bl_0 gate-evidence + seating-measurement only; zero ORIG points copied. No Slurm, no E2E; tickets 39-136 read-only; COMMIT NOTHING.

**1. Bridge rule R137 stated BEFORE running (p137_rule.txt, ORIG-free, general rule-form + concretization).** General form: A = walk's own sequenced slot nearest ORIG[k_lo] (last covered before the named span), B = walk's own sequenced slot nearest ORIG[k_hi] (first covered after); license exactly ONE A-B step (walk order dictates direction), valid ONLY across that named span; bound |AB| <= the walk's own max greedy stride (24.67mm, frozen pre-trigger); all other steps gated as M134d. Concretized for C96 (p137_flank.txt): k_lo=95, k_hi=98; A=slot 261 (nearest SEQ to O95, 4.55mm; seqpos 13); B=slot 224 (nearest SEQ to O98, 4.19mm; dup-twin of 79, dist 0.000; seqpos 286); |AB|=12.2mm <= 24.67. In walk order the step appears as 79->261 at t=12 (79 is B's twin) -- the licensed bridge IS that step, designated not re-walked. Floor note stated with the rule: all 8 uncovered ORIGs' nearest bag slots are SEQ (DO==DB: O96 6.30 / O97 5.61 / O36 5.65 / O37 5.45 / O46 5.79 / O47 5.80 / O165 5.25 / O173 5.56) and every LEFT slot (133/160/197/200) sits >=34.4mm from any uncovered ORIG (p137_floor.txt) -- uncovered=8 is the coverage FLOOR on the 282 bag under the point-gate; predicted bar miss on the coverage legs before running.

**2. Bridged walk vs 134's marks (p137_step3_bridge.py; same point sequence, license designated).** RULE-CHECK passed (seq[12]=79 -> seq[13]=261). Coverage: uncovered 8, spans byte-identical to M134d, C96 point-DO O96=6.30 / O97=5.61 (still open -- floor proof holds). Gate: med 4.2488, <2mm 29.3%, gaps5 98 -- identical to M134d by construction (same point sequence). Jump accounting: 1 licensed step (t=12, 12.24mm, inside envelope); 0 UNLICENSED steps >=40mm (max unlicensed 25.8). Bar: uncovered<8 MISS (by proof, not by walk defect) | C96-covered MISS (DO>=DB>5 always) | gate at/below 4.2488 MATCH (4.2488 == 134's mark exactly) | unlicensed-big0 HOLD. Gate-form observation (NOT claimed as coverage): the licensed segment passes 2.51/2.99mm from O96/O97 -- under a segment-crediting gate the span would already count as crossed (t=12 plus the t=149 11.3mm hop both straddle it).

**3. Verdict + forward path (no presplit-ticket refutation -- flanks ARE reached).** The brief's sequencing-refutation branch does NOT trigger: the walk reaches both flanks adjacently (79@12 -> 261@13), so C96 does not wait on presplit-then-walk for reach. The blocker is the point-gate plus an empty bag near the span (nearest dot 5.61mm out, rej81 filter-dead at every scale per 127/128/135): walker-side bridging can only relabel a hop the walk already takes, never cover. Two honest forward paths, both outside this ticket: (a) detection-side -- a new dot near O96/O97, which needs upstream re-extraction (same owner as 118's structural refutation: mesh/sample density at the lip gap), since no licensed rescan on file admits anything there; (b) gate-form -- a ticket to decide whether geometric crossings (segment-DO<=5) should count as covered, which would bank C96 (2.51/2.99) without inventing a dot. C36/C46/C165/C173 bridging tickets should read this floor proof first: under the point-gate, bridging can never move uncovered below 8 on this bag.

**4. Renders + paths.** artifacts/pota137/p137_bridge.png (eye-checked: gate-frame zoom on O85..O110 -- red C96 span, flank slots A=261/B=224/B-twin 79, magenta licensed t=12, dashed 5mm DB rings around O96/O97 holding no bag dot | step-length profile with licensed step marked, 40mm line untouched, envelope 24.67). Texts mirrored: artifacts/pota137/{p137_rule,p137_control,p137_flank,p137_floor,p137_walk}.txt. Scratch .scratch/pota137_repro/ (p137_step1 _flank _floor _bridge _render .py + p137_rule.txt + txt + npy: p137_G282/seq_m134d/seq_bridge). Tickets 39-136 untouched (read-only); COMMIT NOTHING done.

- [x] M134d reproduced + bridge rule stated (flank slots, license bounds)
- [x] Bridged walk vs 134's marks (coverage, gate, jump accounting)
- [x] Verdict + recipe or presplit-ticket refutation
