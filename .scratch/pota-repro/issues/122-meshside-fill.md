# Mesh-side fill — grow the rim's dots where the filter cannot tell them apart

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 121 (filter level exhausted: arc fully inside junk on every measured feature; 5 unique arc seats banked: 26/31/33/50/94) + 120 (ROR-6 load-bearing) + 119 (7 void spans with mesh context) + 111 (lip mesh edges 1.70 vs 1.51 — slight coarseness signal) + 104 (snap refines boundary dots onto full-res verts)

**Status:** results-in

**What to deliver:** the dots must be GROWN at the mesh, not filtered. For each of 119's void spans (and 121's 5 banked seats as ground truth of where dots SHOULD be), read the mesh-side context: local face sizes vs the 1.70/1.51 numbers, segmentation labels at the span, boundary-test response values there, scan coverage (mesh present and fine, or coarse/holey?). Then state ONE mesh-side ORIG-free rule before running — e.g. subdivide coarse lip faces inside void spans and re-run boundary+snap there, or re-run the boundary test at finer radius/decimation confined to void-span neighbourhoods — and test it: void-span coverage, junk accounting, walk + gate (plain greedy K34+T13, pre-registered, same both arms). The rule must be implementable from mesh data alone (no ORIG positions as inputs; ORIG Bl_0 gate-evidence only). Success bar: uncovered ORIG count below 119's 32 AND admitted junk ~0 AND gate at/below 4.68mm AND walk >=197 pushes. If the mesh at void spans is already fine and fully covered by the boundary test's blindness (response values flat there), refute with those numbers — that says the boundary test itself is blind at these spans and names its radius/threshold as the next variable.

**Starting position:** pota103/111/119/120/121_repro/ (cleaned bag, void spans, 5 banked seats, mesh numbers), C01 fragment mesh + segmentation outputs, boundary test code (mesh_processing_headless.cpp:1580-1709). Login-node numpy only — no Slurm, no E2E. New scratch pota122_repro/; render under laptop artifacts/pota122/ (void spans: mesh fineness + boundary response + grown dots, walk vs control).

**Rules:** control reproduces 103-cleaned bag first (270, gate 4.68) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; context-read-then-rule-stated.

- [ ] Mesh context read per void span (fineness, labels, boundary response, coverage)
- [ ] Mesh-side rule stated, grown bag (coverage, junk accounting)
- [ ] Walk + gate vs full bar
- [ ] Verdict + recipe or blindness refutation with next variable named
## Comments (worker, 2026-10-19 — laptop numpy only; COMMIT NOTHING; lead owns checkboxes)

**Verdict: REFUTED as a landing recipe — 2/4 bar. GROWTH-R1 buys 6 on-arc dots at the price of 8 wall-junk dots and a +0.08 gate regression. The mesh at void spans is fine and the boundary test's response goes flat on-arc: the boundary stage (r=6.46568mm / angle 0.6*pi) is blind at 4 of 7 span centers, ROR owns 2 on-arc kills, snap-drag owns 1. Next variables named below.**

**0. Method + control GREEN.** Rebuilt 103 verbatim (p122_control.py = p121_control.py recipe, OUT repointed): cleaned 270, greedy K=34 + SFS-T13 93/270, final 197, 4 jumps at (92,93)/(126,127)/(164,165)/(183,184), stall [-27.26,1.05,388.81], gate med 4.68 / <2mm 29.9% / gaps5 39 / maxstep 67.0 / ORIGcov 83/211. ORIG = Bl_0 gate-evidence only; zero ORIG points copied. New scratch .scratch/pota122_repro/ (control/context/rule/grow/attrib/render scripts + txt + npy). Laptop mirror artifacts/pota122/ (p122_compare.png eye-checked, control/context/rule/numbers/attrib txt). No Slurm, no E2E; tickets 39-121 read-only; COMMIT NOTHING.

**1. Mesh context per void span (fineness / labels / boundary response / coverage).** Fineness + labels cite 119's Spartan probe (correct-frame Pot_C mesh; laptop Temp/Data/Pot_A is the wrong pot/frame): local edges med 1.47-1.85 (vs 111 lip 1.70 / row 1.51 — normal), dMesh <= 0.66, S0 surface <= 5.04mm at all 7 mids, interiors (dBorder 36-80mm). Coverage FINE everywhere: unclustered surface samples n5 = 17-29, n10 = 59-91 per mid (p122_context.txt, gate frame via TF). Boundary response (pre-snap S 364, snapped SI 343 kept / 21 rejected, ROR r=8.62091/k=6) per mid:
- [9..13] pre-snap n5=0, kept min 5.52 -> BOUNDARY-BLIND (flanked, nothing on-arc)
- [25] pre-snap n5=2 -> 1 ROR-kill at 2.17 (banked seat-26 class) -> ROR owns the on-arc dot
- [32..50] pre-snap n5=0 at mid O41 (flanked 5.79+; banked 31/33/50 at span edges are ROR kills) -> BLIND at center
- [96..97] pre-snap n5=1 -> 1 ROR-kill at 4.94 (banked seat-94) -> ROR owns the on-arc dot
- [160..161] pre-snap n5=0 (flanked 5.82+) -> BOUNDARY-BLIND
- [164..165] pre-snap n5=6 -> ZERO kept within 5 (kept min 5.27), ZERO rejects within 18mm -> SNAP-DRAG (K=1 onto unclustered slid all 6 off-arc although U n5=29)
- [173] pre-snap n5=0 (flanked 5.56+) -> BOUNDARY-BLIND
Global: 70/364 pre-snap dots within 10mm of a void mid but only 9/364 within 5mm — the response flanks every void and goes flat on-arc. ROR counts near voids are keep-dense (med 6-15). Ultra-sparse veto (cnt<3, 4 dots): seats O17/O107/O0, 37-50mm off-arc — wall junk, correctly excluded from seeds.

**2. Rule GROWTH-R1 stated before running (p122_rule.txt, ORIG-free):** seeds = 17 ROR-6 rejects with cnt_self>=3 (filter's own sparse-zone flags; no ORIG); per seed: nearest kept dot -> midpoint -> nearest unclustered surface point (on-mesh projection); accept iff >=1.0mm from bag/dedupe and >=1.0mm from ROW40 coords (licensed-deletion semantic). One pass. Result: 13 growers accepted (4 dedupe-collisions), bag 270->283.

**3. Grown-bag numbers vs full bar (need: uncovered<32 AND junk~0 AND gate<=4.68 AND walk>=197).** Full-bag Dob>5 uncovered 32->26 (pass; all 6 newly covered O25/O32/O33/O49/O50/O96 are grower-seated per p122_attrib.txt — banked-seat neighborhoods, no blind-center reached). Growers junk 8/13 (seats 17x2/27/84x3/107/180; only 5/13 within 5mm: seats 28/29/31/51/94) — FAILS the ~0 leg. Gate med 4.76 vs 4.68 (+0.08), gaps5 39->41, maxstep 67.0->86.4 — FAILS. Walk greedy 98/283, final 210/283, 5 jumps relocated — passes >=197. Loop-based "0 uncovered" at [9..13]/[160..161]/[164..165] in the first numbers pass was walk-reroute artifact; full-bag truth keeps them uncovered (attribution file). Same trade class as 120: arc gain priced in wall junk + worse loop.

**4. Blindness refutation with next variables.** Nothing in mesh data marks the blind centers ([9..13], mid-[32..50] O34-48, [160..161], [164..165]-post-snap, [173]): surface uniformly sampled (no density cue), boundary response flat, nearby ROR counts keep-dense (no sparsity cue) — so no ORIG-free construction rooted at filter outputs can localize them; GROWTH-R1's growers land exactly on 121's banked dots plus wall scatter. Named next variables: (a) boundary-test radius/threshold — adaptive r=6.46568mm (spacing*6, clamp[1,15], edgeline_extraction_headless.cpp:891) with angle 0.6*pi (:909): multi-scale re-run (e.g. r 3-4mm) confined to void-span neighborhoods, or angle-threshold sweep, measuring pre-snap n5 per span mid; (b) snap rule at [164..165]: K=1 nearest-U drags on-arc boundary dots off-arc — surface-constrained snap (K>1 vote / normal-gated) as its own ticket; (c) ROR-killed on-arc dots at [25]/[96..97]/span-edges stay unrecoverable by filter (121 stands) — mesh-side growth is the right family, but seeds must come from a span-localized boundary re-run (a), not from filter rejects.

**5. Renders + paths.** artifacts/pota122/p122_compare.png (eye-checked: gate-frame ORIG covered-green vs still-void red X with 5 cyan on-arc + 8 magenta junk grower rings | bag-frame XY grown-210 blue vs control-197 red, shared stall star). Scratch .scratch/pota122_repro/ (p122_control/context/grow/attrib/render.py + txt + rule + npy: p122_G/Bgrown/seqs). Tickets 39-121 untouched (read-only); COMMIT NOTHING done.

