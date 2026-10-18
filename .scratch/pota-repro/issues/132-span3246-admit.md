# Span-licensed (32,37)+(46,50) — ROR's rejects, licensed by the mid they hold

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 130 (hit-list #2: rule-sketch R32/R46 = span-licensed ROR-reject re-admit; candidates rej 332/333->O33, 300->O31, 183->O50; license dmid to O41; mid held by 124 seats 40/41/42) + 128 (span-localized precedent) + 131 (pool-empty precedent: state pool first, calibrate dmid, admit zero if empty)

**Status:** results-in

**What to deliver:** the R32/R46 rule-sketch tested. Rule (ORIG-free, stated before running): ROR-6 rejects (21x SI[~keep6]) + span-licensed: within dmid<=5mm of the O41 mid (the held middle of remnant [32..50]) + r1 empty-sector PASS (123 verbatim) + SURF-C1 disp cap (state value first; 131 found disp non-binding, dmid structural) + dedupe + ROW40-exclusion. Candidate pool stated first (expected: rej 332/333 near O33, rej 300 near O31, rej 183 near O50 — verify, do not assume). Test: admit survivors, walk + gate (greedy AND guarded-with-fresh-re-anchor per 126 rule-form only if greedy lands). Success bar: uncovered below 15 AND junk 0 AND gate at/below 4.3107 AND walk >=206. If pool empty at license (like 131) or survivors strand, refute with sequencing and the spans join the chaining list.

**Starting position:** .scratch/pota130_repro/ (span owners, R32/R46 sketch, candidate seats), pota128_repro/ (R128 precedent, 279 bag), pota124_repro/ (SURF-C1). Login-node numpy only — no Slurm, no E2E. New scratch pota132_repro/; render under laptop artifacts/pota132/ (pool, survivors, walk vs 279, coverage delta).

**Rules:** control reproduces 128-greedy first (206, gate 4.3107, uncovered 15) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; span-licensed.

- [ ] 128-greedy reproduced + R32/R46 stated with pool
- [ ] Admitted bag (accounting, junk)
- [ ] Walk + gate vs 128's marks
- [ ] Verdict + recipe or chaining-list refutation

## Comments (worker, 2026-10-19 -- laptop numpy only; COMMIT NOTHING)

**Verdict: REFUTED as a landing rule -- 0 admitted under the stated license. R32/R46 finds its candidates but the license cannot see them: every near candidate sits 13-17mm outside the O41 dmid<=5 ring. (32,37)+(46,50) join the chaining list (C32/C46 bridge class, alongside C165 per 131 and C96/C173 per 130). No detection-side items remain -- all five uncovered spans are now chaining class.**

**0. Control GREEN (reproduce-or-stop PASSED).** Rebuilt 279 in pota132_repro (p132_step1.py, OUT repointed): C=270 + SN124=8 + SN128=1 = 279; greedy-279 100/279, final 206, 4 jumps at (99,100)/(133,134)/(173,174)/(192,193), gate med 4.3107 / <2mm 32.0% / gaps5 41 / maxstep 67.0 / ORIGcov 94/211 / uncovered 15 spans [(32,37),(46,50),(96,97),(165,165),(173,173)] -- multiset-equals 128. ORIG = Bl_0 gate-evidence + seating-measurement only; zero ORIG points copied. No Slurm, no E2E; tickets 39-131 read-only; COMMIT NOTHING.

**1. R32/R46 stated BEFORE running (p132_rule.txt, ORIG-free) + pool stated first.** Pool: the 21 ROR-6 rejects = SI[~keep6] (pre-snap sources S[reject_idx]). Test: r1 empty-sector PASS (123 verbatim, r1=3.23284mm) + K1 snap disp <= 2.5mm (124's junk-0 cap; 131 found disp non-binding, dmid structural -- the tighter 124 value taken, the license decides) + dmid <= 5.0mm to void mid O41 ONLY (local frame via TF^-1; gate ORIG names the mid) + dedupe >= 1mm (reject-index order) + ROW40-coord exclusion. Expected near-license survivors (stated, then verified): rej 332/333->O33, rej 300->O31, rej 183->O50. Guarded arm choice stated in rule: greedy first; fresh re-anchor per 126 rule-form only if greedy lands.

**2. Pool (p132_admit.txt): 0 survivors -- the license misses its own candidates.** r1 pass on 21 rejects = 20/21 (only rej 81 fails, nnb=0 -- reproduces 127/128). dmid(O41)<=5: 0/21. Nearest: rej 332/333 dmid 13.51, rej 183 dmid 15.64, rej 300 dmid 17.04, rej 139 dmid 21.04, rej 331 dmid 21.55. Seating (measurement only): 332/333->O33 d0.38, 300->O31 d0.52, 183->O50 d1.52 -- all ON-ARC, exactly the sketch's named candidates, each 13-17mm outside its own license. S->S0 map misses 0/364. Admitted after dedupe+ROW40: 0. Disp is NOT the binding constraint (all four <= 2.35 < 2.5); dmid is, and at the stated value no operating point exists -- the 131 pattern repeats.

**3. Why 0 -- license-geometry autopsy (p132_diag.txt, measurement only, no walks).** The remnant [32..50] is ~30mm long in the local frame; its middle cannot see its flanks: |O33-O41|=13.34, |O50-O41|=15.34, |O31-O41|=16.79, |O32-O41|=15.06, |O37-O41|=7.08, |O46-O41|=8.84. The sketch names flank candidates but licenses the middle -- self-inconsistent as stated. Calibration over caps (r1-pass & disp<=2.5, no dedupe yet): 5.0-12.0 -> 0; 14.0 -> 2 (332/333->O33); 16.0 -> 3 (+183->O50); 18.0-20.0 -> 4 (+300->O31), all on-arc, junk 0; 22.0 -> 5 (+139 wall, seats O27 d6.35) -- the 127 wall-exclusion lesson reprised: widening the license past ~20 buys wall. Note 332/333 snap to the SAME U dot (mutual 0.00mm) -- dedupe collapses them to one; max distinct yield under any cap<=20 is 3 dots (332/333->1, 300, 183), all DEDUP-OK vs 279 (dbag 6.45/4.25/5.27) and ROW40-clear. Whether a cap-14..18 re-license is principled or license-shopping is a next-ticket rule decision -- NOT run here (one-variable discipline; the stated rule is what was tested).

**4. Walk + gate vs 128's marks.** Bag unchanged (279+0=279), so greedy is step-1 identity: 206, gate 4.3107, uncovered 15 -- bar 0/4 as a landing (nothing gained, nothing broken). Guarded arm per stated choice: greedy did not land, so no fresh re-anchor spent (a second variable); verbatim GUARD-126 on the unchanged bag is the 128 identity, not evidence. Sequencing (walk-side, from 130): nearest-LEFT 14.8-19.7mm at (32,37) and 6.5-10.1mm at (46,50) -- nothing to eat; both spans VOID+BRIDGED, hopped by the 22.0mm step (seqpos55, ORIG-seats 42->28) + 44.7mm teleport. The road is there; the dot isn't -- and under the stated license no dot is admissible. Detection-side exhausted at these spans under K=1 snap; next yield is bridging (C32/C46: license a T13-class teleport across each named span, or presplit-then-walk per 118+117 with the spans as the licensed gap).

**5. Renders + paths.** artifacts/pota132/p132_pool.png (eye-checked: gate-frame zoom on O25..O55 -- red (32,37)/(46,50) spans, magenta O41 dmid<=5 ring EMPTY, orange stars 332/333->O33 + 183->O50 + 300->O31 outside the ring | DO-vs-ORIG[20..60] with red span bands, candidate seats, wall 139 gray). Texts mirrored: artifacts/pota132/{p132_rule,p132_control,p132_admit,p132_diag}.txt. Scratch .scratch/pota132_repro/ (p132_rule.txt + step1/step2/diag/render .py + txt + npy: p132_seq_ctrl/admit(empty)). Tickets 39-131 untouched (read-only); COMMIT NOTHING done.
