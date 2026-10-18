# Span-localized (165,165) — snap-drag's span, r1's eyes

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 130 (hit-list #1: (165,165) snap-drag owner; rule-sketch R165 = span-localized r1@r0/2 + SURF-C1 disp cap 2.0->3.5) + 123 (r1 un-blinds; snap-drag owns [164..165] per 122) + 128 (span-localized precedent: 1 dot, junk 0, greedy bar)

**Status:** results-in

**What to deliver:** the R165 rule-sketch tested. Rule (ORIG-free, stated before running): span-localized to void mid (165,165) (dmid<=5mm) + r1 empty-sector PASS (123 code verbatim) + SURF-C1 disp cap 3.5 (up from 124's 2.5 — span-localized, so the geography does wall-exclusion per 127) + dedupe + ROW40-exclusion. Candidate pool: snap-dragged rejects near the span + ROR-6 rejects near the span — state pool first. Test: admit survivors, walk + gate (greedy AND GUARD-129-form... no: greedy first, guarded second with FRESH re-anchor per 126 rule-form only if greedy lands — state choice). Success bar (all must hold): uncovered below 15 AND junk 0 AND gate at/below 4.3107 AND walk >=206. If pool is empty or survivors strand unvisited, refute with the sequencing and (165,165) joins the chaining list.

**Starting position:** .scratch/pota130_repro/ (span owners, (165,165) precision), pota123_repro/ (r1 verbatim), pota124_repro/ (snap caps, SURF-C1), pota128_repro/ (R128 precedent, 279 bag). Login-node numpy only — no Slurm, no E2E. New scratch pota131_repro/; render under laptop artifacts/pota131/ (pool, survivors, walk vs 279, coverage delta).

**Rules:** control reproduces 128-greedy first (206, gate 4.3107, uncovered 15) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; span-localized.

- [ ] 128-greedy reproduced + R165 stated with pool
- [ ] Admitted bag (accounting, junk)
- [ ] Walk + gate vs 128's marks
- [ ] Verdict + recipe or chaining-list refutation
## Comments (worker, 2026-10-19 -- laptop numpy only; COMMIT NOTHING)

**Verdict: REFUTED as a landing recipe -- 0 admitted under the stated rule. R165 finds the edge but the snap-shadow is structural: every r1 edge dot near (165,165) K=1-snaps to a coordinate already in the 279 bag or to covered arc, and the nearest ROR-6 reject sits 16.74mm away. (165,165) joins the chaining list (C165 bridge class, alongside C96/C173 per 130).**

**0. Control GREEN (reproduce-or-stop PASSED).** Rebuilt 279 in pota131_repro (p131_step1.py, OUT repointed): C=270 + SN124=8 + SN128=1 = 279; greedy-279 100/279, final 206, 4 jumps at (99,100)/(133,134)/(173,174)/(192,193), gate med 4.3107 / <2mm 32.0% / gaps5 41 / maxstep 67.0 / ORIGcov 94/211 / uncovered 15 spans [(32,37),(46,50),(96,97),(165,165),(173,173)] -- multiset-equals 128 (p131_control.txt, p131_seq_ctrl.npy). ORIG = Bl_0 gate-evidence + seating-measurement only; zero ORIG points copied. No Slurm, no E2E; tickets 39-130 read-only; COMMIT NOTHING.

**1. R165 stated BEFORE running (p131_rule.txt, ORIG-free) + pool stated first.** Pool (a) snap-drag: r1 empty-sector edge dots (123 code verbatim, r1=3.23284mm) from S0 verts within 10mm of void mid O165 (local frame via TF^-1; gate ORIG names the mid only), K=1 snapped to U (2342). Pool (b) ROR-6: the 21 ROR-6 rejects (127/128 verbatim). Test: r1-PASS + disp<=3.5 + dmid(O165)<=5 + dedupe>=1mm (pool-a first, then pool-b by reject index) + ROW40-exclusion. Guarded arm choice stated in rule: greedy first; fresh re-anchor per 126 rule-form only if greedy lands (verbatim GUARD-126 on a changed bag is stale-latch per 128 s4).

**2. Pool (p131_admit.txt): (a) 97 S0 verts within 10mm of O165 -> 25 r1-PASS, K=1 disp med 2.30 / max 2.64; snapped seating 16/25 on-arc (seats 161-169). (b) 21 ROR-6 rejects, dmid(O165)<=5: 0/21 (min over pool (b) = 16.74mm -- reproduces 122's zero-rejects-within-18mm). Survivors (r1-pass & disp<=3.5 & dmid<=5): 0. Admitted after dedupe+ROW40: 0. S->S0 map misses 0/364.**

**3. Why 0 -- snap-shadow autopsy (p131_diag.txt, p131_autopsy.txt).** Nearest pool(a) snap sits at dmid=5.25mm, 0.25 past the stated line; 12 within 6mm, 22 within 7mm. Every snap with dmid<5.5 re-finds the existing frontier: 8 collide in dedupe (dbag=0.00) with C-bag slots 39/55/56 -- all sequenced on-road on greedy-279 (seqpos 147/148/149, seats ORIG[165]@5.43 / [167]@4.31-4.68); the dedupe-OK remainder seats covered arc (163/164/166/167, all covered, covers165=False). Sequencing: greedy-279 already drives through the span's neighbourhood on-road (seqpos 144-151 pass within 5.25-9.00mm of O165, closest 5.25 at seqpos 148 = slot 56); ORIG DO[163..169]=[3.64,4.96,5.25,4.62,4.17,3.72,3.69] -- only index 165 exceeds 5mm. The road is there; the dot isn't. Calibration (measurement only, no walks): dmid 5.5 -> 2 admits (seats 163/164, covered); 6.0 -> 3 (163/164/166); 7.0 -> 4 (163/164/166/167); covers165=False at every step, on-arc share falls (2/4 at 7.0) -- relaxing buys covered-arc/off-arc junk, zero coverage (the 127 lesson repeats). Disp is NOT the binding constraint here (pool max 2.64 < 3.5); dmid is, and no dmid operating point exists.

**4. Walk + gate vs 128's marks.** Bag unchanged (279+0=279), so both arms are step-1 identity: greedy 206, gate 4.3107, uncovered 15 -- bar 0/4 as a landing (nothing gained, nothing broken). Guarded arm per stated choice: greedy did not land, so no fresh re-anchor spent (a second variable); verbatim GUARD-126 on the unchanged bag is the 128 identity, not evidence. Mechanism: snap-drag confirmed real (r1 finds edge at 25 positions, K=1 displaces 2.1-2.6mm) but structurally shadowed -- the displaced positions are occupied or covered. Detection-side exhausted at this span under K=1 snap; 124's D1/D2 already measured K>1-vote and normal-gating as dead-ends for yield globally, so the next yield at (165,165) is bridging (C165: license a T13-class teleport across the named span, or presplit-then-walk per 118+117 with (165,165) as the licensed gap), behind the remaining detection items (32,37)/(46,50) per 130.

**5. Renders + paths.** artifacts/pota131/p131_pool.png (eye-checked: gate-frame zoom on O165 magenta ring + red star, red x = pool snaps already in bag slots 39/55/56, orange = pool snaps seating covered arc | DO-vs-ORIG[150..180] with red (165,165) band, pool seats, greedy-279 curve peaking 5.25 at 165). Texts mirrored: artifacts/pota131/{p131_rule,p131_control,p131_admit,p131_diag,p131_autopsy}.txt. Scratch .scratch/pota131_repro/ (p131_rule.txt + step1/step2/diag/autopsy/render .py + txt + npy: p131_seq_ctrl/admit(empty)). Tickets 39-130 untouched (read-only); COMMIT NOTHING done.

