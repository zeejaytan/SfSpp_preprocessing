# Last point O37 — one dot or an honest single

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 138 (HONEST: segment-credit banks 7/8; O37 alone OPEN at 5.45, best segment collapses to nearest point) + 136 (O37 owner ROR+boundary-blind; rings at O36/O46 empty; nearest 332/333 dmid(O36) 5.68) + 128/133 (span-licensed precedent)

**Status:** results-in

**What to deliver:** the last detection-side shot, licensed to O37 alone. Rule (ORIG-free, stated before running): ROR-6 rejects + r1 empty-sector PASS (123 verbatim) + disp<=2.5 + dmid<=5 to O37 (fresh single-point license) + dedupe + ROW40-exclusion. Candidate pool stated first. Test: admit survivors, walk + gate (greedy AND M134d-form recovery only if greedy lands — state choice). Success bar: O37 within 5mm (point or segment) AND junk 0 AND gate at/below 4.2488 AND unique >=278. If pool empty at license or survivors strand, refute with the sequencing — O37 stands as the single last open point (1/211) and detection closes with an honest single, pending upstream re-extraction (118's owner: lip-gap sample density).

**Starting position:** .scratch/pota136_repro/ (reject set, O36/O46 ring geometry), pota134_repro/ (282 bag, M134d form), pota138_repro/ (segment-credit rule, O37 numbers). Login-node numpy only — no Slurm, no E2E. New scratch pota139_repro/; render under laptop artifacts/pota139/ (pool, survivors, walk vs M134d, O37 close-up).

**Rules:** control reproduces 134's marks first (290/278u/gate 4.2488) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; single-point license.

- [ ] M134d reproduced + O37 rule stated with pool
- [ ] Admitted bag (accounting, junk)
- [ ] Walk + gate vs 134's marks (point + segment cover)
- [ ] Verdict + recipe or honest-single close

## Comments (worker, 2026-10-19 -- laptop numpy only; COMMIT NOTHING)

**Verdict: REFUTED as a landing rule -- 0 admitted under the O37 single-point license. The last detection-side shot spends itself honestly: the nearest r1-passing reject sits 2.35mm outside the O37 ring, and no other near candidate is closer. O37 stands as the single last open point (1/211); detection closes with an honest single, pending upstream re-extraction (118's owner: lip-gap sample density).**

**0. Control GREEN (reproduce-or-stop PASSED).** Rebuilt 282 in .scratch/pota139_repro (p139_step1.py): C=270 + SN124=8 + SN128=1 + SN133=3 = 282; M134d seq reloaded from p134_seq_d.npy (NOT re-walked): seqlen 290, unique 278/282, gate med 4.2488 / <2mm 29.3% / gaps5 98 / maxstep 25.8 / ORIGcov 99/211 / uncovered 8 spans [(36,37),(46,47),(96,97),(165,165),(173,173)] -- exact multiset-equals 134. O37 segment-credit reproduced: pointDO=5.45 segDO=5.45 best t=49 slots 64->84 len 2.2 (exact match to 138); O36 5.65/4.40 likewise. ORIG = Bl_0 gate-evidence + seating-measurement only; zero ORIG points copied. No Slurm, no E2E; tickets 39-138 read-only; COMMIT NOTHING.

**1. O37 rule stated BEFORE running (p139_rule.txt, ORIG-free) + pool stated first + walker choice stated first.** Pool: the 21 ROR-6 rejects = SI[~keep6], r1-tested on own S0 verts (123 verbatim, r1=3.23284mm). Test: r1-PASS + K1 disp<=2.5 + dmid<=5.0 to void mid O37 (SINGLE-point license; local frame via TF^-1; O37 local=[-30.14 23.09 380.70]; gate ORIG names the mid only) + dedupe>=1mm (reject-index order) + ROW40-exclusion. Walker choice stated in rule: greedy K34+T13 bar arm FIRST (verbatim 134 step1 walk_plain); M134d-form envelope-retreat recovery SECOND ONLY if greedy lands 4/4 (BAND re-frozen from the NEW walk's own state per T134 rule-form -- never ported; verbatim GUARD-126 or ported M134d on a new bag is stale-latch per 128 s4).

**2. Pool (p139_admit.txt): 0 survivors -- the O37 ring is empty.** r1 pass on 21 rejects = 20/21 (only rej81 fails, nnb=0 -- reproduces 127/128/132/133/136). dmid(O37)<=5: 0/21. Nearest: rej 332/333 dmid(O37) 7.35 (2.35 past the line, disp 0.75/2.15, seats O33 d0.38); rej 300 dmid 10.61 (disp 2.31, seats O31 d0.52); rej 139 wall d15.41 (disp 0.99, seats O27 d6.35); rej 183 d22.31 (disp 2.35, seats O50 d1.52). O37-seat verify: rejects seating 37 = [] (confirms 135 s2 pattern -- near candidates seat O31/O33/O50 flanks, not the span). S->S0 map misses 0/364. Admitted after dedupe+ROW40: 0. Disp is NOT the binding constraint (nearest two <= 2.15 < 2.5); dmid is, and at the stated value no operating point exists -- the 131/132/136 pattern repeats exactly, one ORIG step along-arc from O36 (whose ring was 0.68-miss empty; O37's is 2.35-miss empty). Calibration (r1-pass & disp<=2.5, no dedupe): cap 7.0 -> 0 | cap 10.0 -> 2 (332/333->O33) | cap 14.0 -> 3 (+300->O31) | cap 18.0/22.0 -> 4 (+139 wall, seats O27 d6.35 -- the 127/132 wall-exclusion lesson reprised; rej331 disp 3.09 fails disp throughout and is already in-bag). Whether a cap-10 re-license is principled or license-shopping is a next-ticket rule decision -- NOT run here (one-variable discipline; the stated rule is what was tested).

**3. Walk + gate vs 134's marks (point + segment cover).** Bag unchanged (282+0=282), so greedy is strand-identity: greedy-phase 116/282 = 0.4113, final 116, 0 jumps, gate med 5.4597 / uncovered 97 / spans [(36,37),(46,47),(96,97),(115,205)] -- multiset-equals 134-strand exactly (sorted-seq identity True). Bar: uncovered 97<8 FAIL | junk 0 PASS (vacuous, nothing admitted) | gate 5.4597<=4.2488 FAIL | unique 116>=278 FAIL -- 1/4. M134d-form arm per stated choice: greedy did not land, so no envelope-retreat spent (a second variable; verbatim M134d on the unchanged bag is the control identity, not evidence). O37 cover on both walks (R138 operator, licensed segs <40mm): M134d pointDO=5.45 segDO=5.45 best t=49 (289/289 licensed) -> OPEN; greedy strand pointDO=5.45 segDO=5.45 best t=49 (115/115 licensed) -> OPEN. The best segment collapses to the nearest point on both -- no straddle exists to credit. Sequencing (walk-side): nearest-LEFT 50.9mm at O37 (135 s2, slot 133) -- nothing to eat; span (36,37) VOID+BRIDGED, hopped by 24.7/25.8/11.3mm M134d steps. The road is there; the dot isn't -- and under the single-point license no dot is admissible. Detection-side exhausted at O37 under K=1 snap; next yield is bridging (C36 spans as licensed gaps per 136) or upstream re-extraction (118).

**4. Renders + paths.** artifacts/pota139/p139_pool.png (eye-checked: gate-frame zoom -- magenta O37 dmid<=5 ring EMPTY with X mark, near-miss stars 332+333->O33 + 300->O31 + 183->O50 + 139 wall outside the ring | DO-vs-ORIG[20..60] M134d vs pool-empty greedy strand). Texts mirrored: artifacts/pota139/{p139_rule,p139_control,p139_admit,p139_walk}.txt. Scratch .scratch/pota139_repro/ (p139_rule.txt + step1/step2/step3/render .py + txt + npy: p139_G282/seq_greedy/admit(empty)). Tickets 39-138 untouched (read-only); COMMIT NOTHING done.

