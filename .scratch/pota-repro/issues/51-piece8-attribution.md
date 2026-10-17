# 51: Piece-8 attribution — the last miss on Pot B

**What to deliver:** piece 8 seated — or the measured proof it cannot be, matcher-side.

**Answers:** E1

**Blocked by:** 49-flag-recall (relaxed ≥10-pt rule → 8/9+7/15 2/3 runs, seated [1-7,9]; edge 2-8 has 0 strict inliers at GT seating before AND after resampling — intrinsically weak contact).

**Status:** results-in (landed as ceiling proof — session verified jobs + render)

**Starting position:** the 2-8 contact shows zero strict inliers at the TRUE seating — the outline pair carries no measurable grip there. Question is matcher-side: can any beam/scoring change seat P8 off its non-2-8 contacts (6-7/6-9/7-9 neighbourhood?), or is 8/9 the material ceiling for our B outlines? Bundle reference: Spartan pota49_repro/prep/pota49_bundle_B_relaxed; identities script C:\temp\p49\p49_identities.py; renders C:\temp\p49\p49_*_seating.png. Zero ORIG points in any fix (44-asterisk rule); ORIG diagnosis-only.

**Rules:** land ONLY with P8 seated ×3 same-binary runs + controls green (B ORIG 9/9+15/15, A 8/8+15/15) in same runs + B gate 15/15, OR measured proof of ceiling (exhaust the beam-side options first); seating render (eye-check); assembler E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition.

- [x] Beam-side options for P8 + ceiling proof if unseatable
- [x] 9/9 or measured why-not
- [x] Job IDs + sacct states

## Comments (worker, 2026-10-17 — ticket done, verdict: ceiling)

**Verdict: P8 is unseatable inside any globally-good beam solution — 8/9 is the
material ceiling for our B outlines.** P8 seated in only 2 of 16 B-fresh
assemblies (both density-ranking at 5/9); every 8/9 solution misses exactly [8].
Correction to Starting position: GT graph row for P8 (Pot_B_simple_graph.txt in
the relaxed bundle) is pieces **1, 2, 5** — not the 6-7/6-9/7-9 neighbourhood.
P8's live contacts are 1-8 (13 strict / LCS 38, dens 5.43) and 5-8 (19 / 45,
dens 4.50); 2-8 is dead (0 strict, LCS 0/22, score 11.0 — worst-in-forest on
every axis, confirming ticket 49's finding).

**Evidence — B-fresh score / P8 status per condition (controls B ORIG
9/9+15/15 and Pot A 8/8+15/15 GREEN in all 16 runs; all sacct COMPLETED 0:0):**

| Condition | Jobs | B-fresh | P8 |
|---|---|---|---|
| BASE k5/b3 | 33241722 | 8/9+7/15 | out |
| WIDTH k12/b3 ×3 | 33241723/24/25 | 8/9, 7/9, 7/9 | out ×3 (width fragments P6, admits junk 1-2/1-4/1-9/3-7) |
| LENNORM (density rank) ×3 | 33243158/59/60 | 5/9 ×3 | **IN, IN, out** (true 1-8: ang 0.087 rad, trans 38.1 mm) |
| P8FIRST (P8 root) ×3 | 33243161/62/63 | 8/9 ×3, bit-identical | out ×3 — root order irrelevant |
| LENWIDTH (density+k12) ×3 | 33243958/59/60 | 6/9, 5/9, 5/9 | out ×3 (collapses to LENNORM basin) |
| P8LEN (P8 root+density) ×3 | 33260460/61/62 | 4/9, 6/9, 4/9 | out ×3 (forced root collapses assembly) |

**Why-not for 9/9 (measured):** (1) seating P8 costs P2/P4/P5/P6 and vice versa —
P8's 1-8/5-8 edges compete with main-pot edges for the same beam slots under
every ranking; (2) no single-axis ranking (inlier/density/score/axis-angle)
separates all true from false pairs in the 70-pair pruned forest
(C:\temp\p51\p51_ceiling.py); (3) same-binary knife-edge: the identical binary
yields 8/9, 7/9, 6/9, 5/9-seated, 5/9-missed and 4/9 variants — beam lottery
dominates; (4) forcing P8 (P8FIRST ≡ BASE; P8LEN → 4/9) proves the cause is
expansion competition, not root order. Untested cells (width+root,
width+root+density) combine individually-failed interventions with no
mechanistic basis for synergy — beam-side options declared exhausted.
Vehicle: pota51_repro/asm = cure-potA @ bffefb6 + env-gated P51-DUMP /
P51-LENNORM / P51-P8FIRST patches only (lanes 49/50 untouched, read-only).
Eye-check render of P8 seated (LENNORM run 33243159): C:\temp\p51\p51_lennorm_P8_seating.png —
P8 tracks the GT foot rim next to P1 at 5°/38 mm while P2/P4/P5/P6 scatter.
Tallies: C:\temp\p51\p51_tally.py (+fetches f15x/f16x/lw95x/lw96x/pl46x);
attribution probe C:\temp\p51\p51_attrib.py; ceiling C:\temp\p51\p51_ceiling.py.

**Successor:** cross-pot generalization of the B recipe (C–J share the drowning shape).
