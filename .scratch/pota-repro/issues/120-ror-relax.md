# ROR relaxation — stop deleting the rim's own dots

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 119 (7 true void spans; owner = ROR min_neighbors=6 via boundary_filter.cpp:10-33; fix = 6->3 C01-only) + 103 (cleaned bag baseline) + 111 (ROR-vs-boundary ambiguity stated — keep it: report whether relaxed ROR admits dots the boundary test itself would reject)

**Status:** results-in

**What to deliver:** exact-port the ROR step (boundary_filter.cpp:10-33, min_neighbors rule) in numpy, reproduce the 270-bag deletion at 6 first (same deleted set to the dot — green control), then rerun at 3 (one variable). Report: (a) void-span shrinkage (each of 119's 7 ORIG void ranges: coverage before/after); (b) junk accounting (newly kept dots seated vs ORIG: on-arc share — the 111 ambiguity check); (c) full-bag walk + gate vs 4.68 bar (GUARD-113 or plain greedy+T13 — state which before running, same in both arms). Success bar: void spans shrink (total uncovered ORIG count down) AND junk share small (newly kept dots majority within 5mm of ORIG) AND gate no worse than 4.68 AND walk no shorter than 197. If 3 admits a second inboard row (junk), refute with the trade numbers — that says ROR-6 was load-bearing and the voids must be filled upstream instead.

**Starting position:** pota103/119_repro/ (cleaned bag, void spans with ORIG extents, ROR port from 104/109 work if reusable), boundary_filter.cpp:10-33 + caller edgeline_extraction_headless.cpp:990-992. Login-node numpy only — no Slurm, no E2E. New scratch pota120_repro/; render under laptop artifacts/pota120/ (void spans before/after on the ORIG arc, newly kept dots coloured by seated distance).

**Rules:** control reproduces ROR-6 deletion exactly first or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; port-exact-then-one-variable.

- [ ] ROR-6 ported exact (deleted set matches)
- [ ] ROR-3 rerun (void shrinkage, junk accounting, walk + gate)
- [ ] Verdict + recipe or trade refutation

## Comments (worker, 2026-10-18 — DESIGN PRE-REGISTRATION, before running; Status unchanged)

Walker (stated before running): plain greedy K=34 + SFS-T13 (103 verbatim), same in both arms. GUARD-113 ruled out for this comparison: it strands at 190 on the 270-bag (113: 3/4 bar) and would confound the ROR variable. Bar stays 4.68 med / 197 pushes, both defined by this walker.

Arms (one variable = min_neighbors 6->3, C01 S0 only): ROR input = 364 snapped (p104_bnd_S0.npy), radius 8.62091 (= 6.46568*8/6, clamp [2,20] inactive), PCL self-inclusive count, keep iff count >= k. Control ROR-6 must keep 343 with deleted set == pipe bagP coords or STOP. ROR-3 -> bag B; B-clean = B minus the 40 ROW40 coords (coord-based; verified == visit-[93,132] deletion on control) -> walk + gate vs 4.68/197 (primary); B-raw = full B walk + gate vs 343-baseline 93/237/5.79 (secondary). Void spans: Dob-coverage recompute per span, B-clean vs 270. Junk: newly-kept (in B, not in 343) seated on ORIG, share within 5mm + distance to ROW40; boundary-ambiguity decided by construction (newly-kept subset of admitted-364, so ROR-3 admits zero boundary-rejected dots).

## Comments (worker, 2026-10-18 — RESULTS; laptop numpy only; COMMIT NOTHING; lead owns checkboxes)

**Verdict: REFUTED as a landing recipe — 2/4 bar items. ROR-6 is load-bearing against inboard-wall scatter; the voids must be filled upstream (targeted re-admission), not by a global threshold relax.**

**0. Control GREEN (corrected rule).** ROR input rebuilt pipe-faithfully: K1-snap of p104_bnd_S0.npy (pre-snap 364) onto Pot_C_Piece_01_unclustered.ply (2342 verts; snap med 2.19mm = pipe typical; ROW40 40/40 present; all 343 pipe coords present, 0 missing). Correction to the pre-reg: PCL counts OTHER-neighbours only (self excluded) — keep iff >=6 others within 8.62091mm reproduces the pipe 343/21 ORDERED-EXACT (multiset diff 0/0, atol=1e-4); naive self-inclusive keep>=6 gives 348/16 (5 extra, all with exactly 5 others) and was rejected. 343-baseline walk replayed identical to pipe seqP (93/237/4); coord-minus-ROW40 == staging 270 (0/0 diff, licenses the deletion for arm B); 270 control 93/197, stall [-27.26,1.05,388.81], gate med 4.68. Zero ORIG points copied (Bl_0 gate-evidence only); all inputs read-only.

**1. ROR-3 numbers (one variable, others>=3): kept 360/364, newly-kept 17 slots / 15 unique.**
(a) Void shrinkage HOLDS partially: spans 7->6, uncovered ORIG 32->23 (cov 179/211->188/211). Per span (uncovered before->after): [9..13] 5->5; [25] 1->0; [32..50] 19->12; [96..97] 2->1; [160..161] 2->2; [164..165] 2->2; [173] 1->1. Newly covered ORIG: 25, 32, 33, 34, 35, 48, 49, 50, 96.
(b) Junk accounting FAILS: only 8/17 slots (6 unique, seats 26/31/33/50/94) within 5mm of ORIG — not a majority. 9 junk slots: 5 high-wall dots 42-48mm off-arc near seats 84/106/107 (5-14mm from ROW40 coords, z~447-451: interior-wall scatter); 2 at seat-17 31-34mm off-arc incl. one 2.24mm from a ROW40 coord (second-row-adjacent); 2 fringe 8.4/11.6mm at seats 180/170. All 17 walk-consumed. 111-ambiguity resolved: all 17 passed the boundary test (subset of admitted-364) — ROR-3 admits zero boundary-rejected dots BY CONSTRUCTION; the junk is mid-face admissions the boundary test itself let through (104-class), which ROR-6 was hiding.
(c) Walk + gate (pre-reg walker, same both arms): B-clean (287 = 360 minus same 40 ROW40 coords): greedy 97/287, final 212/287 (HOLDs >=197), 4 T13 jumps relocated to (96,97)/(113,114)/(151,152)/(206,207); gate med 4.85 vs 4.68 FAILS (+0.17), gaps5 39->44, max teleport 67.0->87.7mm, ORIGcov 83->90/211. B-raw (full 360, pipe-at-3): 97/252, med 5.80 ~= 343-baseline 5.79 — no gate gain without the ROW40 deletion.

**2. Trade refutation.** Gain: +9 ORIG covered, [25] gone, [32..50] 19->12, 8 on-arc dots all walked. Price: 9 junk dots (incl. second-row-adjacent), gate +0.17mm, +5 gaps>5mm, worst teleport +20.7mm. A global 6->3 relax buys 9 arc dots at the cost of 9 wall dots and a worse loop. Recipe: NONE at threshold level. Upstream direction: targeted re-admission of dots seating within 5mm of the 7 void spans (the 8 on-arc dots are named in p120_newX.npy with seats 26/31/33/50/94) or mesh-side densification at void-span arc positions — ROR-6 stays.

**3. Paths.** Scratch .scratch/pota120_repro/ (p120_ror.py, p120_run.py, p120_render.py, p120_SI.npy, p120_B_raw.npy, p120_B_clean.npy, p120_newX.npy, keep masks, seqs, p120_numbers.txt, p120_step1.txt). Renders artifacts/pota120/p120_compare.png (eye-checked: void X's shrink on the right arc, cyan on-arc vs magenta junk interior), + numbers/step1 mirrors. Tickets 39-119 untouched (read-only); COMMIT NOTHING done.
