# Single-line topology — stop the zigzag, not just cover the points

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 140 (eye verdict: author's single clean loop vs our zigzag that crisscrosses inner/outer wall; coverage 210/211 does NOT imply topology) + 105 (face-hop named: trace hops inner-outer) + 134 (M134d walk) + 138 (segment-credit: banks crossings, never penalizes them)

**Status:** results-in

**What to deliver:** a topology metric + a face-coherent walk. Problem: the gate measures point/segment DISTANCE to the author loop — a walk that zigzags across the wall still scores 4.25 because every zig stays near the loop. Nothing penalizes (a) consecutive-dot face alternation (inner-wall dot -> outer-wall dot -> inner), (b) self-intersections of the walk (chords crossing chords). Measure first on M134d: face-flip count (classify each sequenced dot inner/outer by mesh side, count alternations), self-intersection count of walk segments. State both numbers as the topology baseline. Then test a face-coherent ordering: penalize/refuse steps that alternate mesh side vs the running face (stated rule first, ORIG-free), walk + re-measure (coverage gate must not regress past 4.3107, topology counts must fall). Success bar: face-flips and self-intersections down by majority AND gate at/below 4.3107 AND uncovered at/below 8 (segment-credit). If face classification itself is incoherent (dots unclassifiable), refute with the distribution — owner is dot-level (snap-drag leftovers), not walk-level.

**Starting position:** .scratch/pota134_repro/ (M134d sequence, 282 bag), pota140_repro/ (mesh frame), pota104_repro/ (snap-drag evidence). Login-node numpy only — no Slurm, no E2E. New scratch pota142_repro/; renders under laptop artifacts/pota142/ (face-coloured walk: inner vs outer, flip points marked; before/after).

**Rules:** control reproduces 134's marks first or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; topology numbers first, fix second.

- [ ] M134d topology baseline (flips, self-intersections)
- [ ] Face-coherence rule stated + tested walk
- [ ] Coverage vs topology vs bar
- [ ] Verdict + recipe or dot-level refutation

## Comments (worker, 2026-10-19 -- laptop numpy only; COMMIT NOTHING)

**Verdict: DOT-LEVEL REFUTATION with measured mechanism — walk-level ordering cannot stop the zigzag on the 282 bag. Bar not met by any arm; coverage and face-coherence are in direct tension.**

**0. Control GREEN (reproduce-or-stop PASSED).** Rebuilt M134d from read-only 134 inputs (.scratch/pota142_repro/p142_step1.py): seqlen 290, unique 278/282, gate med 4.2488 / <2mm 29.3% / gaps5 98 / maxstep 25.8 / ORIGcov 99/211 / uncovered 8 / spans [(36,37),(46,47),(96,97),(165,165),(173,173)] — exact match to 134. Zero ORIG points copied; ORIG = Bl_0 gate-evidence + ruler only; tickets 39-141 untouched read-only; no Slurm/E2E.

**1. Topology baseline M134d (ruler = ORIG loop geometry, evidence-only; metric validated: ORIG scores 0/0).**
Lateral side = side of nearest ORIG segment in ORIG-PCA lip plane (var [0.53,0.45,0.02], planeN [-0.07,-0.98,-0.18]); eps 1mm = R133 dedupe band; selfint = proper crossings of non-adjacent segment pairs in lip-plane 2D.
M134d: flips 32 (248 classifiable @1mm; 38 @0.5mm / 18 @2mm — stable across eps) / selfint-2D 33 / turns>90 69.
Controls: ORIG 0 flips / 0 selfint at all eps (metric sane); greedy-279: 29 flips / 8 selfint / 19 turns>90. So recovery bought coverage (116->278) at 4x selfintersections (8->33).
SUPERSEDED reading: an early script copy printed 43 flips for M134d; two independent scorings agree on 32 — 32 is the baseline.
Mesh-side classification itself INCOHERENT (tried first, per brief): (a) signed distance of walked dots to nearest mesh face: ALL 290 within 1mm (std 0.03) — dots sit ON the surface, no side to read; (b) inner/outer region split by face-normal-vs-radial: no bimodal split (walk nearest-face n.r hist flat 1..66 across 10 bins; ORIG clusters ~0 = lip edge). Face-by-mesh-side is unmeasurable; lateral-vs-author-loop is the working topology metric.

**2. Face-coherence rule R142 (stated BEFORE any guarded walk, .scratch/pota142_repro/p142_rule.txt; ORIG-free: bag-PCA plane + walk-state headings only).**
Refuse/deprioritize candidates whose lateral sign (vs running heading, bag-PCA plane, eps 1mm) opposes the running side. One variable vs M134d (verbatim greedy-116 freeze + T134 trigger + 24.67 envelope + index-advance; coherence is the only delta).
- Arm A (deprioritize opposite-side to last): seqlen 293, unique 282/282, retreats 11, med 4.2746 / uncovered 8 / spans identical / big 0 — coverage legs HOLD — but flips 33 / selfint 35 / turns90 78. Topology UNCHANGED (within noise of 32/33/69). Local smoothing cannot remove global crossings.
- Arm B (refuse opposite-side): PATHOLOGICAL — 19979-retreat ping-pong (refuse-all-K34 forces retreat; retreat landing re-faces the same refusal; oscillates to guard cap 20000), seqlen 20116, med 6.04 / uncovered 97. Refuse-form is unusable at replay level. VOID.
- Arm C (strand-referenced static labels, ORIG-free): label distribution degenerate (207/282 within 1mm of strand in bag-plane, only 2 +side; agreement with ORIG-ruler labels 0.44) — strand is not a wall-side reference. Coverage COLLAPSES: unique 215, med 4.68, uncovered 56 / spans [(36,37),(46,47),(96,97),(115,161),(164,165),(173,173)]. Dead.
Greedy-phase filter (coherence from step 1) also dies honestly: beelines to the 282 strand slot 221 in 36 steps (same trap as verbatim-116, K34 window saturated, global nearest unvisited 34.8mm) without visiting all 3 admitted dots — trigger would (correctly) SUPPRESS. Kept verbatim freeze for all arms above.

**3. Mechanism (why walk-level cannot fix it — dot-level owner).**
Nearest-neighbour dots are same-side (0/210 opposite-side NN at d>=1mm): the bag does NOT interleave — greedy is locally coherent by itself (only 8 flips in 116 greedy steps). The crossings are forced by WHAT must be covered: recovery-first-visit dots span BOTH ruler sides (106 vs 31 classifiable). Those 31 minority-side dots each demand a crossing out and (mostly) back; 12 envelope retreats (chords up to 10.3mm back to the road) each re-cross the wall. Flips cluster at recovery onset (seqpos 116-118) and the retreat zone (139-150). Single-side preference (Arm C) proves the tension directly: coherence costs 48 extra uncovered ORIGs (8->56). The zigzag is the price of full-bag coverage on a two-walled bag, not a walk-ordering defect — owner is dot-level (both walls present in the bag; snap-drag leftovers per 104), exactly the brief's refutation branch.

**4. Coverage vs topology vs bar.** Bar needs flips AND selfint down by majority (<=16/<=16) with gate<=4.3107 AND uncovered<=8. Best arm (A): 33/35 with 4.2746/8 — coverage legs hold, topology legs miss by 2x. No arm meets all four. Segment-credit (138) does not change this: it re-accounts spans, it does not uncross the walk.

**5. Renders + paths.** artifacts/pota142/p142_side_m134d.png + p142_side_armA.png (eye-checked: lip-plane, green author loop, red/blue walk sides, black flip dots — zigzag straddling the loop visible in one glance). Scratch .scratch/pota142_repro/ (step1 control, step2-3 mesh surveys, step4/superseded + step6/recon topology, step5/5b/8 arms A/B/C, step7 interleave, step9 pockets+render + rule/pockets/walks txts + npy). Tickets 39-141 read-only; COMMIT NOTHING done.
