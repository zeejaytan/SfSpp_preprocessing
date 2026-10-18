# Void-map refresh on 279 — name every span's owner, pick the cheapest

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 129 (279-ABSOLUTE: all distinct groups sequenced, leftovers twins, stall refusal identical; honest road = greedy 206) + 119 (7-void taxonomy + per-void owners on the 270 bag) + 127/128 (chaining list [173]/[96..97]; [25] banked)

**Status:** results-in

**What to deliver:** the 119 analysis re-run on the 279 walk. Classify each of the 15 uncovered ORIG spans: VOID (no near-bag dots) vs EATEN (dots exist, walk consumed/ignored) vs BRIDGED (walk jumps over); name the owner per span from the known taxonomy (ROR deletion / boundary-blind / snap-drag / chaining-class / walk-refusal); state which spans the 128 admission + 129 freeze moved vs 119's map. Then PRIORITIZE: rank the spans by cheapest-next-yield (single-dot admission like 128 > span-localized detection like 123 > chaining like [173]) with a one-line rule-sketch per span. No new dots admitted, no walks beyond the 279 greedy/guard already on file — this is a reading ticket that ends with an ordered hit-list. Success bar: every one of the 15 uncovered spans classified with an owner AND an ordered hit-list with rule-sketches, OR an explicit statement that a span's owner is unknown (which itself becomes the next ticket).

**Starting position:** .scratch/pota119_repro/ (void taxonomy + owners), pota128/129_repro/ (279 walk, coverage deltas, uncovered-15 list). Login-node numpy only — no Slurm, no E2E. New scratch pota130_repro/; render under laptop artifacts/pota130/ (uncovered-15 map with per-span owners, hit-list order).

**Rules:** reproduce 128's uncovered-15 list first or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits.

- [x] Uncovered-15 reproduced + 119 taxonomy restated
- [x] Per-span classification with owner
- [x] Ordered hit-list with rule-sketches

## Comments (worker, 2026-10-19 -- laptop numpy only; COMMIT NOTHING)

**Verdict: MAP COMPLETE, no unknown owners. All 15 uncovered ORIG spans on greedy-279 are VOID (nearest bag dot 5.20-6.76mm away, all SEQ) + BRIDGED (walk hops/teleports over each span); zero EATEN spans -- the detection-side shelf is empty, consistent with 129's walk-side absolute. Cheapest-next-yield order: (165,165) snap re-admit > (32,37)/(46,50) span-licensed ROR-reject re-admit > (96,97) bridge > (173,173) bridge-last.**

**0. Control GREEN (reproduce-or-stop PASSED).** Rebuilt 279 in pota130_repro (p130_map.py, OUT repointed): C=270 + SN124=8 + SN128=1 = 279; greedy-279 seq (reloaded p128_seq_greedy, not re-walked) 206, steps>5mm 41, ORIGcov 94/211, uncovered 15 spans [(32,37),(46,50),(96,97),(165,165),(173,173)] -- exact multiset-equals 128. No new walks, no new dots; ORIG = Bl_0 gate-evidence + seating-measurement only; tickets 39-129 read-only; COMMIT NOTHING.

**1. 119 taxonomy restated (7 voids on the 270 bag, ORIG coverage 179/211).** Spans ORIG[9..13](5.3-6.0mm gaps) / [25](5.7) / [32..50](len19,maxgap6.8) / [96..97](6.3) / [160..161](5.8) / [164..165](5.3) / [173](5.6). Mesh ctx per mid (local frame): arc meshed (dMesh<=0.66), edges normal fineness (med 1.47-1.85), voids interior (dBorder 36-80mm, not scan border), S0 surface present <=5mm -- scan/mesh/snap causes ruled OUT; pre-filter cloud holds 17-29 pts within 5mm of every void mid, post-filter bag 0 (nearest 5.3-6.9mm). Owner (all 7, one pattern): ROR deletion -- `original_nurbs_preprocessing/boundary_filter.cpp:10-33` via `edgeline_extraction_headless.cpp:990-992`, `outlier_radius_mm=max(2,min(20,g_boundary_radius_mm*8/6))` (:986-989), `min_neighbors=6` (:991-993). Residual ROR-vs-boundary-radius-test ambiguity noted, not hidden (same filter block; 120/127 separated them downstream). Breaks: 7 VOID + 28 EATEN-BRIDGE (112-REFUSAL pattern at stall break01).

**2. Per-span classification on greedy-279 (DB = walk-independent bag-to-ORIG; LEFT = unsequenced slots).**

- (32,37) len6 VOID+BRIDGED, owner ROR+boundary-blind. DO/DB 5.20-6.76 (nearest slots SEQ 154/65/84); nearest LEFT 14.8-19.7mm (slots 254/60) -- nothing to eat. Hopped by 22.0mm step (seqpos55, ORIG-seats 42->28 bracket the span) + 44.7mm teleport. Remnant of 119 [32..50]; mid covered by 124 seats 40/41/42. 123: blind at pipe radius, edge signal at r0/2 -- detection-side.
- (46,50) len5 VOID+BRIDGED, owner ROR+boundary-blind. DO/DB 5.79-6.15 (SEQ 61/69/135); nearest LEFT 6.5-10.1mm (slots 60/138). Same 119 parent, same 123 standing as (32,37).
- (96,97) len2 VOID+BRIDGED, owner ROR+chaining. DO/DB 6.30/5.61 (SEQ 261/79); nearest LEFT 6.9/5.6mm (slot 224). Hopped by 12.2mm step (seats 99->92) + 67.0mm teleport (seats 130->88). Kill rej81->O94 r1-FAIL nnb=0 (127 s5: filter-dead at every scale) -- no detection rule; chaining class.
- (165,165) VOID+BRIDGED, owner snap-drag. DO/DB 5.25 (SEQ 56); nearest LEFT 5.25mm (slot 181). Remnant of 119 [164..165]; 126 s3 agenda names [165] snap-drag (123 s4: r1 found the edge, K=1 snap displaced it, 44 on-arc dots failed SURF-C1 at disp 2.06-3.76).
- (173,173) VOID+BRIDGED, owner ROR+chaining (last). DO/DB 5.56 (SEQ 35); nearest LEFT 5.56mm (slot 47). Hopped by 7.4mm step (seats 175->171). 123 s3: blind at ALL scales (flanked, min frozen 5.04mm) -- detection exhausted; 127: unconditional chaining list.

No span is EATEN on greedy-279 (every nearest-LEFT >5mm); no span owner is unknown.

**3. Moved-analysis vs 119's map (what 128 admission + 129 freeze moved).** [9..13] GONE via 124 (seats 8/11/13) -- not 128/129. [25] GONE = 128's bank (rej331->O26, DO 5.70->2.17, +2 ORIGcov [25,26]) -- the only span 128 moved. [32..50](len19) SPLIT to (32,37)+(46,50) via 124 (seats 40/41/42 hold the mid on greedy); 129's freeze MERGES them back to (32,50) on the guarded walk -- guarded loses [38..45] to walk-refusal (strand ORIG[88] d=6.01, K-net 34/34, recoverable shelf 0; 129 autopsy), proving walk-side exhaustion, moving nothing detection-side. [160..161] GONE via 124 (seats 160/161); [164..165] shrunk to (165,165) via 124 road extension (164 covered with no admitting dot). [96..97] and [173] UNMOVED across 119->126->128->129. Net: 128 moved one span ([25]); 129 moved zero detection-side and certified the rest as detection-side work.

**4. Ordered hit-list (cheapest-next-yield first; detection before chaining per 127; single-dot span-localized first per 128's proven cost: 1 variable, junk 0, gate holds).**

1. (165,165) -- R165: r1@r0/2 edge dots within 10mm of mid O164/O165 + SURF-C1 with disp cap relaxed 2.0->3.5 (R128-calibrated knee; 123 s4 seats inside blind spans at disp 2.06-3.76) + dmid<=5 + dedupe>=1mm + ROW40-exclusion. Predict 1 dot, junk ~0. Cost class = 128.
2. (32,37)+(46,50) -- R32/R46: ROR-6 reject + r1-PASS + disp<=2.5 + dmid<=5 to void-mid O41 (local frame, new span license -- 128's O25 license excludes these by construction) + dedupe + ROW40-exclusion. Candidates on file: rej 332/333->O33 (d=0.38), rej 300->O31 (d=0.52), rej 183->O50 (d=1.52). Keep the dmid license tight -- 127 s4: dmid does all wall-exclusion work.
3. (96,97) -- C96 bridge: filter-dead, so sequence the flanks -- license a T13-class teleport across the named span only (slots [89..95]-side 261/145-147 to [98..]-side comp0), or presplit-then-walk (118+117 staged triggers) with (96,97) as the licensed gap. Walker-side rule, needs sequencing proof; behind detection items.
4. (173,173) -- C173 bridge-last: same bridge class as C96 but zero edge signal at any scale (weakest S0 support of all voids, 5.04mm) -- pure chaining, hardest. Last.

**5. Renders + paths.** `artifacts/pota130/p130_voidmap.png` (eye-checked: gate-frame X-Z ORIG arc + greedy/guard walks, red spans w/ owners, orange 119 voids, cyan 124x8, gold 128x1 | DO-vs-ORIG curves showing [25] banked + guarded [38..45] loss). Text mirrored: `artifacts/pota130/p130_spans.txt`. Scratch `.scratch/pota130_repro/` (p130_map.py + p130_spans.txt + p130_render.py). Tickets 39-129 untouched (read-only); COMMIT NOTHING done.
