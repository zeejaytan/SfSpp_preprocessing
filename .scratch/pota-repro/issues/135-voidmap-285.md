# Void-map refresh on 285 — eight spans left, name them all

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 134 (LAND: M134d walk 278/282 unique, gate 4.2488, uncovered 8, spans [(36,37),(46,47),(96,97),(165,165),(173,173)]) + 130 (void-map precedent + hit-list discipline)

**Status:** results-in

**What to deliver:** the 130 analysis re-run on the M134d walk over the 285 bag (282 + R133's 3 wide dots). Classify each of the 8 uncovered ORIG spans: VOID vs EATEN vs BRIDGED; owner per span; what the 133 dots + 134 recovery moved. Then PRIORITIZE: ordered hit-list ranked cheapest-first (detection remnant > named-span bridge), one-line rule-sketch per span. No new dots, no new walks — reading ticket ending in an ordered hit-list. Success bar: all 8 classified with owners AND ordered hit-list with rule-sketches, OR explicit unknown-owner statement.

**Starting position:** .scratch/pota134_repro/ (285 bag, M134d walk, uncovered-8 list), pota130_repro/ (void-map precedent). Login-node numpy only — no Slurm, no E2E. New scratch pota135_repro/; render under laptop artifacts/pota135/ (uncovered-8 map with owners, hit-list).

**Rules:** reproduce 134's uncovered-8 list first or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits.

- [x] Uncovered-8 reproduced + 130 taxonomy restated
- [x] Per-span classification with owner
- [x] Ordered hit-list with rule-sketches

## Comments (worker, 2026-10-19 -- laptop numpy only; COMMIT NOTHING)

**Verdict: MAP COMPLETE, no unknown owners. All 8 uncovered ORIG points on M134d/282 are VOID (nearest bag dot 5.45-6.30mm away, all SEQ) + BRIDGED (walk hops over each span); zero EATEN (nearest unsequenced slot 34-65mm away). Cheapest-next-yield order: (165,165) snap re-admit > (36,37)+(46,47) span-licensed ROR-reject rescan > (96,97) bridge > (173,173) bridge-last.**

**0. CONTROL GREEN + BAG NOTE (reproduce-or-stop PASSED; brief arithmetic corrected).** Rebuilt 282 in .scratch/pota135_repro (p135_map.py): C=270 + SN124=8 + SN128=1 + SN133=3 = 282; M134d seq reloaded from p134_seq_d.npy (NOT re-walked): seqlen 290, unique 278/282, steps>5mm 98, maxstep 25.8, ORIGcov 99/211, uncovered 8 spans [(36,37),(46,47),(96,97),(165,165),(173,173)] -- exact multiset-equals 134. BAG NOTE: the brief's "285 bag (282 + R133's 3 wide dots)" double-counts -- 282 already IS 279+R133x3 (270+8+1+3); no 285-bag exists on file anywhere (133/134 both bank 282). This ticket maps M134d over the 282 bag; "285" read as 282 throughout. No new dots, no new walks; ORIG = Bl_0 gate-evidence + seating-measurement only; tickets 39-134 read-only; COMMIT NOTHING.

**1. 130 taxonomy restated (5 span-groups on greedy-279, ORIG coverage 94/211).** (32,37) len6 VOID+BRIDGED owner ROR+boundary-blind, DO/DB 5.20-6.76; (46,50) len5 VOID+BRIDGED owner ROR+boundary-blind, DO/DB 5.79-6.15; (96,97) len2 VOID+BRIDGED owner ROR+chaining (rej81 filter-dead at every scale, 127 s5), DO/DB 6.30/5.61; (165,165) VOID+BRIDGED owner snap-drag (123 s4: r1 found the edge, K=1 snap displaced it, 44 on-arc dots failed SURF-C1 at disp 2.06-3.76), DO/DB 5.25; (173,173) VOID+BRIDGED owner ROR+chaining-last (blind at ALL scales, min frozen 5.04mm), DO/DB 5.56. Zero EATEN on greedy-279 (every nearest-LEFT >5mm); no owner unknown. Parent: 119's 7 ROR-deletion voids on the 270 bag.

**2. Per-span classification on M134d/282 (DB = walk-independent bag-to-ORIG; LEFT = unsequenced slots; only 4 LEFT slots exist: 133/160/197/200, 197+200 dup-twins).**

- (36,37) len2 VOID+BRIDGED, owner ROR+boundary-blind (remnant of 130's (32,37), same 119 parent [32..50]). DO/DB 5.65/5.45, nearest slots SEQ 84/84; nearest LEFT 49.7/50.9mm (slot 133) -- nothing to eat. Hopped by 24.7/25.8/11.3mm steps. No admitted dot seats it; full reject-seat list (133 admit.txt) shows no reject seating 36/37.
- (46,47) len2 VOID+BRIDGED, owner ROR+boundary-blind (remnant of 130's (46,50)). DO/DB 5.79/5.80, nearest slots SEQ 61/279 -- slot 279 IS new dot rej183 (seats O50 d1.52) sitting 5.80mm from O47, nearest-miss of all remnants but still VOID-side of the 5mm gate. Nearest LEFT 60.7/61.6mm -- nothing to eat. Hopped by 17.0/18.2/11.3mm steps.
- (96,97) len2 VOID+BRIDGED, owner ROR+chaining. DO/DB 6.30/5.61 UNCHANGED to the dot (+0.00 both) -- neither dots nor recovery touch it; nearest slots SEQ 261/79; nearest LEFT 64-65mm (slot 160). Hopped by 12.2/11.3mm steps. Filter-dead: no detection rule, chaining class (unchanged from 130).
- (165,165) VOID+BRIDGED, owner snap-drag. DO/DB 5.25 UNCHANGED (+0.00); nearest slot SEQ 56; nearest LEFT 34.4mm (slot 197). Hopped by 5.8/7.4/17.0mm steps. Detection-side (r1 edge exists, snap displaced) -- R165 rule stands verbatim.
- (173,173) VOID+BRIDGED, owner ROR+chaining-last. DO/DB 5.56 UNCHANGED (+0.00); nearest slot SEQ 35; nearest LEFT 47.9mm. Hopped by 7.4/9.1mm steps. Weakest S0 support, pure chaining, hardest -- last (unchanged from 130).

DO==DB on all 8 (walk passes at exactly bag distance -- the walk adds nothing near spans); every nearest-bag slot is SEQ (walk visits the nearest dot, still >5mm out). No span is EATEN; no span owner is unknown.

**3. Moved-analysis vs 130's map (what the 133 dots + 134 recovery moved; p135_moved.txt).** 133 DOTS (detection-side): gained exactly ORIG[32,33,34,35,48,49,50] (DO deltas -1.84..-6.39; seats O33/O31/O50 d0.38/0.52/1.52), lost ZERO -- (32,37) shrinks to (36,37), (46,50) shrinks to (46,47). Knock-on: O30 3.12->1.66, O31 4.01->0.52 newly <2mm (cov 94->99); O35 (3.89)/O48 (4.07) covered but not <2. Still-open deltas all +0.00 except O47 -0.35 (new dot 279 now nearest at 5.80). 134 RECOVERY (walker-side only): strand-282 uncovered 97 spans [(36,37),(46,47),(96,97),(115,205)] (quoted from 134 control, NOT re-run) -> M134d 8; the giant stuck span (115,205) (~91 pts of key-space refusal) eliminated walker-side, the 4 mini-spans byte-identical to the forced probe; detection-side moved nothing. Net 130->135: 15 -> 8 uncovered, 94 -> 99 ORIGcov, zero walk-geometry churn losses (lost-list empty).

**4. Ordered hit-list (cheapest-next-yield first; 130's price ladder kept: single-dot admission > span-localized detection rescan > named-span bridge; detection remnant > named-span bridge per brief).**

1. (165,165) -- R165 (verbatim 130): r1@r0/2 edge dots within 10mm of mid O165 + SURF-C1 with disp cap relaxed 2.0->3.5 (R128-calibrated knee) + dmid<=5 + dedupe>=1mm + ROW40-exclusion. Predict 1 dot, junk ~0. Cost class = 128 (1 variable). First because the rule is fully stated with calibrated caps and known yield.
2. (36,37)+(46,47) -- R36/R46 rescan: ROR-6 reject + r1-PASS + disp<=2.5 + dmid<=5 to new void-mids O36/O46 (fresh span license -- 133's O41 license excludes these by construction) + dedupe + ROW40-exclusion. Candidates UNKNOWN on file (133's reject-seat list seats nothing at 36/37/46/47; rej139 wall at dmid 21.04 correctly excluded) -- the rescan itself is the cheap step (login-node filter pass, no walk); a zero-yield rescan promotes both spans to chaining-class, which is itself the decision this hit-list exists to force.
3. (96,97) -- C96 bridge: filter-dead, so sequence the flanks -- license a T13-class teleport across the named span only (slots [89..95]-side to [98..]-side), or presplit-then-walk with (96,97) as the licensed gap. Walker-side rule, needs sequencing proof; behind detection items.
4. (173,173) -- C173 bridge-last: same bridge class as C96 but zero edge signal at any scale (weakest S0 support, 5.04mm) -- pure chaining, hardest. Last.

**5. Renders + paths.** artifacts/pota135/p135_voidmap.png (eye-checked: gate-frame X-Z ORIG arc + greedy-279/M134d walks, red spans w/ owners, orange 119 voids, cyan 124x8, gold 128x1, magenta 133x3 | DO-vs-ORIG curves showing 133-banked [32..35]+[48..50] + hit-list order). Texts mirrored: artifacts/pota135/p135_spans.txt + p135_moved.txt. Scratch .scratch/pota135_repro/ (p135_map.py + p135_diff.py + p135_render.py + txt). Tickets 39-134 untouched (read-only); COMMIT NOTHING done.
