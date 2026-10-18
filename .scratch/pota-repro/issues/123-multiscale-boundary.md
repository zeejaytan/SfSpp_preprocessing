# Span-localized multi-scale boundary — un-blind the test where it goes flat

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 122 (mesh fine everywhere; empty-sector boundary test goes FLAT on-arc at 4 void spans: [9..13], mid-[32..50], [160..161], [173]; ROR owns [25],[96..97]; snap-drag owns [164..165]) + 104 (numpy port of the boundary test exists) + 103 (cleaned bag, gate 4.68)

**Status:** results-in

**What to deliver:** the boundary test is blind at 4 spans because its single radius (6.47mm) and 0.6pi sector rule see no empty sector where the fold crowds the neighbourhood. Re-run the test MULTI-SCALE but CONFINED to void-span neighbourhoods: port-exact first at the pipe radius (reproduce which mesh verts pass/fail there), then smaller radii (state the scale ladder before running, e.g. r, r/2, r/4) applied ONLY inside the 4 blind spans' neighbourhoods, admitting dots that pass at finer scale. Snap surface-constrained (keep 122's lesson: no off-face drag; state the constraint). Seeds come from the span-localized re-run, never from filter rejects (121 stands). Walk + gate the resulting bag (plain greedy K34+T13, pre-registered, same both arms). Success bar (all must hold): uncovered ORIG count below 119's 32 AND admitted junk ~0 (majority within 5mm of ORIG) AND gate at/below 4.68mm AND walk >=197 pushes. If finer scales admit the same flat response (blind at every scale), refute with the response-vs-scale curves — that says the neighbourhood itself carries no edge signal and the span must be bridged by chaining, not detected.

**Starting position:** pota103/104/119/122_repro/ (cleaned bag, boundary-test numpy port, void spans + blind-span list, mesh verts), mesh_processing_headless.cpp:1580-1709 + caller :2040-2068. Login-node numpy only — no Slurm, no E2E. New scratch pota123_repro/; render under laptop artifacts/pota123/ (blind spans: response-vs-scale curves, newly admitted dots, walk vs control).

**Rules:** control reproduces 103-cleaned bag first (270, gate 4.68) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; port-exact-then-ladder-stated.

- [ ] Boundary port-exact at pipe radius (pass/fail reproduced in blind spans)
- [ ] Scale ladder stated, span-localized re-run (response curves, admission accounting)
- [ ] Walk + gate vs full bar
- [ ] Verdict + recipe or all-scale-blind refutation
## Comments (worker, 2026-10-19 — laptop numpy only; COMMIT NOTHING; lead owns checkboxes)

**Verdict: recipe CONFIRMED — bar 4/4, on a single-dot gain. The neighbourhoods DO carry edge signal at r/2 (all-scale-blind REFUTED for 3 of 4 spans); the snap is now the binding constraint, not the sector test.**

**0. Method + control GREEN.** Rebuilt 103 verbatim (p123_control.py = p121/p122 recipe, OUT repointed): cleaned 270, greedy K=34 + SFS-T13 93/270, final 197, 4 jumps at (92,93)/(126,127)/(164,165)/(183,184), stall [-27.26,1.05,388.81], gate med 4.68 / <2mm 29.9% / gaps5 39 / maxstep 67.0 / ORIGcov 83/211. ORIG = Bl_0 gate-evidence only; zero ORIG points copied. Inputs read-only: Pot_C S0 cloud (11165 verts + normals) downloaded from Spartan pota39_repro/prep/pota39_C (md5-verified, mirror in pota123_repro/, source untouched); local Temp/Data/Pot_A is the wrong pot/frame (7018 verts, confirmed NOT used). No Slurm, no E2E; tickets 39-122 read-only; COMMIT NOTHING.

**1. Port-exact at pipe radius: 364/364 to the dot.** PCL-1.9.1 BoundaryEstimation faithfully ported (float32, FLT_MIN init, wrap gap, strict > 0.6*pi; fetched impl/boundary.hpp to settle two details the local lore missed: exact-float-zero delta skip (NOT index skip — S0 has 3496 duplicate coords) and singleton-neighbour wrap -> true). SOR (MeanK=50, std=9) identity verified both self-handlings: 0 removed. Adaptive radius recomputed from S0 bbox = 6.46568mm. Output multiset-equals p104_bnd_S0.npy (port-only=0, pipe-only=0, 338 uniques both). First miss (352/364, pure subset) diagnosed to the delta-skip; second nuance (cp==1 -> wrap=true) verified in.

**2. Scale ladder stated BEFORE running (p123_ladder.txt): r0=6.46568, r1=r0/2=3.23284, r2=r0/4=1.61642**, queries confined to S0 verts within 10mm of the 4 blind mids (310 verts). Snap constraint SURF-C1 stated before running (keeps 122: no off-face drag): K=1 snap kept iff displacement <= 2.0mm AND snapped point within 5mm of the licensing mid. Seeds span-localized only, never filter rejects (121 stands).

**3. Response-vs-scale (pre-snap n5|n10|min per blind mid): [9..13] 0|8|5.52 -> 4|27|2.69 -> 0|54|5.02; mid-[32..50] 0|12|5.79 -> 4|26|3.09 -> 0|54|5.89; [160..161] 0|11|5.80 -> 3|24|2.97 -> 0|60|5.44; [173] 0|14|5.04 -> 0|16|5.04 -> 0|35|5.04.** r1 un-blinds 3/4 centers; r2 re-blinds everywhere (finer is NOT better — neighbourhood fragments). [173] blind at ALL scales: flanked, min frozen at 5.04mm. All-scale-blind refutation REJECTED for 3 spans, HOLDS for [173] (bridge-by-chaining there).

**4. Admission accounting (ORIG-seated, gate frame): r1 93 cand -> SURF-C1 2 survivors (disp-ok=42, mid-ok=22, both=2); r2 203 cand -> 0 survivors. Dedupe + ROW40-exclusion: 1 admitted (r1, disp 1.67, dmid 1.53, seats O160 at 1.53mm).** Cost of SURF-C1: 46/93 r1 snapped dots are on-arc (<=5mm ORIG) but 44 fail the caps — ~17 seat INSIDE blind spans ([11]x2,[13]x4,[40]x4,[41],[42]x2,[45]x2,[161]x2 seats) with disp 2.06-3.76 or dmid 5-6.3, just outside the stated caps; the rest seat at span edges/already-covered arc the confinement correctly excludes. r2: 55 on-arc, all fail (disp med 3.34, drift to 8mm). So the sector test finds the edge at r1 and the K=1 snap displaces it — snap placement (K>1 vote / normal-gated, cf. 122c) or disp-cap calibration is the named next variable for yield.

**5. Walk + gate vs full bar (need uncovered<32 AND junk~0 AND gate<=4.68 AND walk>=197): grown 271, greedy 93/271, final 198, 4 jumps at (92,93)/(126,127)/(165,166)/(184,185). Gate med 4.60 (<2mm 30.3%, gaps5 40, maxstep 67.0, ORIGcov 84/211). Uncovered 30 < 32 PASS ([160..161] span gone — admitted dot covers O160+O161). Junk 1/1 within 5mm PASS. Gate 4.60 <= 4.68 PASS. Walk 198 >= 197 PASS. Fragility note: single-dot dependence — the bar holds mechanically but yield is 1 dot; the recipe below is confirmed, not yet high-yield.**

**6. Recipe (landing): (a) port-exact empty-sector test at adaptive r0 (delta-zero skip + singleton-wrap, SOR identity check); (b) re-run at r0/2 confined to 10mm blind-span neighbourhoods; (c) K=1 snap under SURF-C1 (disp<=2mm, dmid<=5mm); (d) dedupe >=1mm, ROW40-coord exclusion; (e) plain greedy K34+T13 walk. [173]-class spans (flat at every scale) skip to chaining.**

**7. Renders + paths.** artifacts/pota123/p123_curves.png + p123_walk.png (both eye-checked: V-curve at r1 with [173] flat; grown red loop tracks control blue, lime star at admitted dot, stall X). Scratch .scratch/pota123_repro/ (control/port/scale/admit/acct/walk/render scripts + txt + ladder + npy: p123_bnd_r0/nh_r1/nh_r2/admit/qidx/seqs; Pot_C S0 .xyz/.ply read-only mirrors md5 1c88db1e…416881e7). Tickets 39-122 untouched (read-only); COMMIT NOTHING done.
