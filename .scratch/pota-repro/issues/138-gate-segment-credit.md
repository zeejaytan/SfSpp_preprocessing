# Gate-form: credit crossings, not just dots

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 137 (floor proof: 8 is the floor on 282 under POINT-gate; licensed C96 segment passes 2.51/2.99mm from O96/O97; forwards: gate-form ticket on crediting crossings) + all gate tickets (5mm cover standard already in use)

**Status:** results-in

**What to deliver:** a gate-form ruling with measurements. Question: the campaign's cover standard is "within 5mm" — the point-gate credits an ORIG point when the nearest walk POINT is within 5mm. A licensed bridge SEGMENT passing 2.51mm from O96 is within the same 5mm by the same standard — is crediting it moving the goalposts, or applying the standard to the walk's actual geometry (segments, not just vertices)? Rule (stated before running): segment-credited cover = min over walk SEGMENTS of segment-to-ORIG distance, same 5mm threshold, licensed segments only (unlicensed jumps never credit). Measure on the M134d walk + R137 licensed bridge: recompute uncovered-8 under segment-credit, state which spans bank (expect C96 at 2.51/2.99; check C36/C46/C165/C173 segments too — M134d already bridges all 8 per 135, so every bridging segment gets measured). Success bar: segment-credit definition stated with its principled grounding (same 5mm, vertices-vs-segments argument for/against) AND recomputed uncovered list with per-span segment distances AND an explicit statement of whether the gate change is honest measurement or goalpost-moving (falsifiable: would segment-credit also bank spans on the 279/270 walks? check at least one earlier walk — if it banks everywhere, it's inflation; if it banks only genuinely-crossed spans, it's measurement).

**Starting position:** .scratch/pota137_repro/ (licensed bridge, segment distances), pota134_repro/ (M134d walk), pota128_repro/ (279 walk for the falsifiability check). Login-node numpy only — no Slurm, no E2E. New scratch pota138_repro/; render under laptop artifacts/pota138/ (per-span segment distances, recomputed coverage, falsifiability check).

**Rules:** reproduce 137's segment distances first (2.51/2.99) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; gate-form honesty first (report inflation if found).

- [x] Segment distances reproduced + credit rule stated with grounding
- [x] Recomputed uncovered (M134d + bridge) with per-span numbers
- [x] Falsifiability check on an earlier walk
- [x] Verdict: honest measurement or inflation, with evidence

## Comments (worker, 2026-10-19 -- laptop numpy only; COMMIT NOTHING)

**Verdict: HONEST MEASUREMENT -- segment-credit is selective, not inflationary. Under R138 the 282 walk goes from 8 point-uncovered ORIGs in 5 spans to 1 uncovered ORIG (O37, 5.45mm) in 1 open span (36,37); 4 of 5 spans bank. The same rule on the 279 walk banks 9/15 and leaves 6 open across 2 spans -- it does NOT bank everywhere. Gate medians are untouched (segment-credit changes only the cover accounting, never the walked points). Caveat banked with the verdict: 6 of 7 banks hang on a SINGLE licensed segment each, and O36 (4.40) is marginal -- its best segment's endpoints sit nearest O35/O33 (near-miss, not a clean straddle). Thin but licensed; reported, not hidden.**

**0. Control GREEN (reproduce-or-stop PASSED).** Rebuilt from read-only 137 inputs (.scratch/pota138_repro/p138_step1.py): 261->224 segDO O96=2.51 / O97=2.99 and twin 79->261 identical -- exact match to 137 to 0.01mm. M134d marks re-verified: seqlen 290, unique 278/282, gate med 4.2488, uncovered 8, spans [(36,37),(46,47),(96,97),(165,165),(173,173)], maxstep 25.8. Zero ORIG points copied; ORIG = Bl_0 gate-evidence + seating only; tickets 39-137 read-only; no Slurm, no E2E; COMMIT NOTHING.

**1. Credit rule R138 stated BEFORE running (.scratch/pota138_repro/p138_rule.txt, mirrored artifacts/pota138/).** Segment-credited cover = min over LICENSED walk segments of point-to-segment distance (projection clamped), SAME 5mm threshold as the point-gate. Licensed = every step except unlicensed jumps >= 40mm (campaign jump leg, unchanged); R137's t=12 C96 step is licensed by the named-span license. Grounding for: the walk travels along its segments and the author's input is a continuous arc -- a licensed segment traversing 2.51mm from O96 covers that span more faithfully than a 4.9mm-distant dot earns point-cover elsewhere; threshold untouched, no dot invented. Against (stated honestly): vertices-to-edges changes what the gate measures -- a walk could bank a span it flies over; the license guard answers it (only < 40mm envelope-scale strides credit, never teleports), and the falsifiability check decides empirically.

**2. Recomputed uncovered-8 under segment-credit (p138_step2.py; all 289 M134d segments licensed, maxstep 25.8 < 40, 0 excluded):**

| ORIG | point-DO | seg-DO | best segment (slots, len) | straddle audit |
|------|----------|--------|---------------------------|----------------|
| O36 | 5.65 | 4.40 BANKED | t=51, 65->281, 7.8mm | near-miss (nnORIG 35->33; MARGINAL, 1/289 segs <=5) |
| O37 | 5.45 | 5.45 OPEN | t=49, 64->84, 2.2mm (endpoint = nearest point) | touches (37->37); 0/289 segs <=5 |
| O46 | 5.79 | 2.75 BANKED | t=100, 270->204, 17.0mm | STRADDLES (42->51); 1/289 |
| O47 | 5.80 | 3.11 BANKED | t=100, 270->204, 17.0mm (same stride) | STRADDLES (42->51); 1/289 |
| O96 | 6.30 | 2.51 BANKED | t=12 (R137 licensed bridge), 79->261, 12.2mm | STRADDLES (99->92); 1/289 |
| O97 | 5.61 | 2.99 BANKED | t=12, same stride | STRADDLES (99->92); 1/289 |
| O165 | 5.25 | 1.57 BANKED | t=225, 51->276, 17.0mm | STRADDLES (170->161); 1/289 |
| O173 | 5.56 | 3.41 BANKED | t=224, 178->51, 9.1mm | STRADDLES (175->170); 3/289 |

Span verdicts: (36,37) OPEN (O36 banked but O37 honestly open -- its best segment collapses to its nearest point, projection on endpoint) | (46,47) COVERED | (96,97) COVERED (the licensed C96 crossing) | (165,165) COVERED | (173,173) COVERED. 7/8 ORIGs banked, 4/5 spans covered; 6 of 7 banks are clean straddles, O36 is the declared marginal one.

**3. Falsifiability check on the 279 greedy walk (p128_seq_greedy, 206 final, 15 point-uncovered; p138_step3.py; SAME rule, 3 segments >= 40mm excluded as unlicensed):** banks 9/15 -- spans (32,37) COVERED (6/6, one 22.0mm licensed stride 270->154), (96,97) COVERED (2.51/2.99, same t=12 stride exists on 279), (173,173) COVERED (4.23) -- while (46,50) stays OPEN 0/5 (best 5.68) and (165,165) stays OPEN (5.10). A rule that banked everywhere would have taken (46,50) too; it did not. Selectivity holds on both walks: it banks only spans a licensed stride genuinely crosses within 5mm. Note the asymmetry cuts both ways, as measurement should: O37 banks on 279 (3.70) but stays open on 282 (5.45) -- different walk geometry, honestly reported.

**4. Renders + paths.** artifacts/pota138/p138_segdo.png (eye-checked: 282 point-vs-segment bars, 5mm line, 7 green + O37 red) + p138_falsify.png (eye-checked: 279 bars, 9 green / 6 red, (46-50)+O165 visibly open). Texts mirrored: artifacts/pota138/{p138_rule,p138_control,p138_segments,p138_falsify}.txt. Scratch .scratch/pota138_repro/ (step1/2/3 + render .py + rule/control/segments/falsify txts + G282/seq npy). Tickets 39-137 untouched (read-only); COMMIT NOTHING done.
