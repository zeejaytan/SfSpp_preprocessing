# Span rescan (36,37)+(46,47) — new mids, fresh license

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 135 (hit-list #2: R36/R46 rescan to new void-mids O36/O46; candidates UNKNOWN on file; zero-yield promotes both spans to chaining-class) + 132 (O41 license excludes these by construction; wide-license precedent) + 131 (pool-empty precedent: state pool first)

**Status:** results-in

**What to deliver:** the rescan tested. Rule (ORIG-free, stated before running): ROR-6 rejects + r1 empty-sector PASS (123 verbatim) + disp<=2.5 + dmid<=5 to NEW void-mids O36 and O46 (fresh span license — 133's O41 license excludes these by construction) + dedupe + ROW40-exclusion. Candidate pool stated first (133's reject-seat list seats nothing at 36/37/46/47 — verify on the 282 bag). Test: admit survivors, walk + gate (greedy AND M134d-form recovery only if greedy lands — state choice first). Success bar: uncovered below 8 AND junk 0 AND gate at/below 4.2488 AND unique >=278. If pool empty at license or survivors strand, refute with the sequencing — both spans promote to chaining-class (C36/C46) and detection closes on the remnant.

**Lead note:** hit-list #1 (R165 verbatim) is NOT re-run: 131 already spent that exact rule on this neighbourhood (pool empty, no operating point) and the 282 bag changes nothing near O165. Repeat discarded with reason, not silently.

**Starting position:** .scratch/pota135_repro/ (span owners, new-mid license), pota133_repro/ (reject-seat list, 282 bag), pota134_repro/ (M134d recovery form). Login-node numpy only — no Slurm, no E2E. New scratch pota136_repro/; render under laptop artifacts/pota136/ (pool, survivors, walk vs M134d, coverage delta).

**Rules:** control reproduces 134's marks first (290/278u/gate 4.2488/uncovered 8) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; fresh license only.

## Comments (worker, 2026-10-19 -- laptop numpy only; COMMIT NOTHING)

**Verdict: REFUTED as a landing rule -- 0 admitted under the fresh license. R36/R46 replays the 131/132 pool-empty pattern at the new mids: the nearest r1-passing reject sits 0.68mm outside the O36 ring, and every other near candidate is further out. (36,37)+(46,47) promote to chaining-class (C36/C46 bridge class, alongside C96/C173 per 130 and C165 per 131). Detection closes on the remnant -- no detection-side items remain on any of the 8 uncovered ORIG points.**

**0. Control GREEN (reproduce-or-stop PASSED).** Rebuilt 282 in .scratch/pota136_repro (p136_step1.py): C=270 + SN124=8 + SN128=1 + SN133=3 = 282; M134d seq reloaded from p134_seq_d.npy (NOT re-walked): seqlen 290, unique 278/282, gate med 4.2488 / <2mm 29.3% / gaps5 98 / maxstep 25.8 / ORIGcov 99/211 / uncovered 8 spans [(36,37),(46,47),(96,97),(165,165),(173,173)] -- exact multiset-equals 134. ORIG = Bl_0 gate-evidence + seating-measurement only; zero ORIG points copied. No Slurm, no E2E; tickets 39-135 read-only; COMMIT NOTHING.

**1. R36/R46 stated BEFORE running (p136_rule.txt, ORIG-free) + pool stated first + walker choice stated first.** Pool: the 21 ROR-6 rejects = SI[~keep6], r1-tested on own S0 verts (123 verbatim, r1=3.23284mm). Test: r1-PASS + K1 disp<=2.5 + dmid<=5.0 to void mid O36 OR O46 (union license; local frame via TF^-1; gate ORIG names the mids only) + dedupe>=1mm (reject-index order) + ROW40-exclusion. Fresh-license check: |O36-O46|=16.91mm local -- one ring cannot see both spans, hence the union. R165 repeat DISCARDED per lead note (131 spent it: pool empty, no operating point; 282 changes nothing near O165). Walker choice stated in rule: greedy K34+T13 bar arm FIRST (verbatim 134 step1 walk_plain); M134d-form envelope-retreat recovery SECOND ONLY if greedy lands 4/4 (BAND re-frozen from the NEW walk's own state per T134 rule-form -- never ported; verbatim GUARD-126 or ported M134d on a new bag is stale-latch per 128 s4).

**2. Pool (p136_admit.txt): 0 survivors -- both fresh rings empty.** r1 pass on 21 rejects = 20/21 (only rej81 fails, nnb=0 -- reproduces 127/128/132/133). dmid(O36|O46)<=5 union: 0/21. Nearest: rej 332/333 dmid(O36) 5.68 (0.68 past the line, disp 0.75/2.15); rej 183 dmid(O46) 7.57 (disp 2.35, seats O50 d1.52 -- the 135-noted nearest-miss, still VOID-side); rej 300 dmid(O36) 8.84 (disp 2.31, seats O31 d0.52). 133-seat verify on the 282 bag: rejects seating 36/37/46/47 = [] (confirms 135 s2 -- the candidates near these spans seat O31/O33/O50 flanks, not the spans). S->S0 map misses 0/364. Admitted after dedupe+ROW40: 0. Disp is NOT the binding constraint (all three near-misses <= 2.35 < 2.5); dmid is, and at the stated value no operating point exists -- the 131/132 pattern repeats exactly. Calibration (r1-pass & disp<=2.5, no dedupe): cap 7.0 -> 2 (332/333->O33); cap 10.0 -> 4 (+183->O50, +300->O31); cap 14.0-22.0 -> 5 (+139 wall, seats O27 d6.35 -- the 127/132 wall-exclusion lesson reprised; rej331 disp 3.09 fails disp throughout and is already in-bag). Whether a cap-7..10 re-license is principled or license-shopping is a next-ticket rule decision -- NOT run here (one-variable discipline; the stated rule is what was tested).

**3. Walk + gate vs 134's marks.** Bag unchanged (282+0=282), so greedy is strand-identity: greedy-phase 116/282 = 0.4113, final 116, 0 jumps, gate med 5.4597 / uncovered 97 / spans [(36,37),(46,47),(96,97),(115,205)] -- multiset-equals 134-strand exactly (sorted-seq identity True). Bar: uncovered 97<8 FAIL | junk 0 PASS (vacuous, nothing admitted) | gate 5.4597<=4.2488 FAIL | unique 116>=278 FAIL -- 1/4. M134d-form arm per stated choice: greedy did not land, so no envelope-retreat spent (a second variable; verbatim M134d on the unchanged bag is the control identity, not evidence). Sequencing (walk-side): nearest-LEFT 49.7/50.9mm at (36,37) and 60.7/61.6mm at (46,47) (135 s2, slot 133) -- nothing to eat; both spans VOID+BRIDGED, hopped by 24.7/25.8/11.3mm and 17.0/18.2/11.3mm M134d steps. The road is there; the dot isn't -- and under the fresh license no dot is admissible. Detection-side exhausted at these spans under K=1 snap; next yield is bridging (C36/C46: license a T13-class teleport across each named span, or presplit-then-walk per 118+117 with the spans as the licensed gap).

**4. Renders + paths.** artifacts/pota136/p136_pool.png (eye-checked: gate-frame zoom on O25..O55 -- red (36,37)/(46,47) spans, magenta O36 + cyan O46 dmid<=5 rings EMPTY, near-miss stars 332+333->O33 + 300->O31 + 183->O50 + 139 wall outside the rings | DO-vs-ORIG[20..60] M134d vs pool-empty greedy strand). Texts mirrored: artifacts/pota136/{p136_rule,p136_control,p136_admit,p136_walk}.txt. Scratch .scratch/pota136_repro/ (p136_rule.txt + step1/step2/step3/render .py + txt + npy: p136_G282/seq_greedy/admit(empty)). Tickets 39-135 untouched (read-only); COMMIT NOTHING done.

- [x] M134d reproduced + R36/R46 stated with pool
- [x] Admitted bag (accounting, junk)
- [x] Walk + gate vs 134's marks
- [x] Verdict + recipe or chaining-class promotion
