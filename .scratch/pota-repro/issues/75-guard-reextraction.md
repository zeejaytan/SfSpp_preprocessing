# 75: Walk-level forward-cone guard re-extraction

**What to deliver:** C01 lip walked clean at the source + gate toward ORIG.

**Answers:** E1

**Blocked by:** 74 (C01 ceiling PROVEN — no walkable in-file branch: longest link<5mm chain 39pts vs 211 needed; in-file options EXHAUSTED; walk-level re-extraction scoped as successor; jobs 33288861/62/63 COMPLETED) + 67 (doubled-loop bound: walk chains two parallel lip loops via greedy K=50 no heading guard; conservator eyewitness corroborates face-hop) + 69 (offset upstream in boundary-estimator output; GUARD arm regressed — successor must do better with a principled cone, not a threshold tweak).

**Status:** results-in

**Starting position:** re-walk C01's lip with a forward-cone (heading) guard in the stepper so the trace cannot step sideways onto the parallel loop at touch points — the eyewitness-confirmed face-hop cure. Prep-side scratch copies; per 67's repair direction: split-then-select BEFORE sequencing + forward-cone guard + inner-loop select (lip-face rule via Surface_0/1 standoff test, 44-asterisk-safe, no ORIG). Zero ORIG points in any fix; ORIG evidence-only.

**Rules:** land with C01 Bl_0 gated toward ORIG (median + coverage + jumps→0 with NO reordering) + E2E at or above 2/3+1/3 ×3 same-binary + controls green (C ORIG 4/4+5/5, A 8/8+15/15) in same runs; renders (eye-check) + a `Needs-eye:` staged pair per the visual-evidence lane rule (fresh trace on mesh vs author trace on same mesh); E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition; no gate relaxation without a mechanism.

- [x] Guard re-extraction arms, one variable each
- [x] Gate + E2E rerun ×3 or measured why-not
- [x] Job IDs + sacct states

## Comments (finisher, 2026-10-18)

First worker's jobs all COMPLETED before it died; this finisher collected and reports only — no new Slurm jobs, nothing committed.

**Guard arms (prep, build+edge job 33292185; BASE verified identical to p39 vehicle proof):**
- BASE (CONE=off PRESPLIT=off): C01 Bl_0 n=402 — unchanged legacy trace.
- CONE (forward-cone guard only, no presplit): C01 Bl_0 kept comp=0 n=19 (POT_C piece 01, Surface_0 side; second-chance skipped).
- PRE (cone + presplit): C01 Bl_0 n=20.
- SEL (inner-loop select): C01 Bl_0 n=16 — this fragment is what E2E arm C_G used (md5 fd9da9e2 identical in pota75_bundle_C_G and pota75_bundle_SEL; md5 guard files confirm no other-ticket writes).

**C01 Bl_0 gate vs ORIG (gate75.py, login node, fresh-vs-ORIG nearest-neighbour; Bl_1 untouched in all arms):**
- REF / S24 / BASE: n=402, med=5.61mm, <2mm=22.9%, jumps>5mm=[(10,56.8),(39,65.5),(191,105.0)] — the face-hop signature (two parallel-loop jumps ~60mm plus a 105mm leap).
- CONE: n=18, med=5.74mm, <2mm=0.0%, jumps=[(16,32.8)] — cone alone shortened the walk but did not land it on the lip.
- PRE: n=20, med=1.18mm, <2mm=100.0%, jumps=[(4,35.7)] — on-lip median/coverage but one residual 36mm jump.
- SEL: n=16, med=1.18mm, <2mm=100.0%, jumps=NONE — gate green (median + full coverage + zero jumps, no reordering). C_G E2E re-ran exactly this fragment.
- Neighbouring-piece context: C03 Bl_0 also lands in every fresh arm (CONE 100.0%, PRE 100.0%, SEL 100.0% zero jumps); C02 Bl_0 and C04 Bl_0 stay off-lip in all arms (med ~5–6mm), Bl_1 arms untouched throughout.

**E2E tallies (cure-potA @ bffefb6, ×3 repeats, identical in all three jobs):**
- A_orig: 8/8 + 15/15 (all three jobs)
- A_fresh: 8/8 + 15/15 (all three jobs)
- C_orig: 4/4 + 5/5 (all three jobs)
- C_G (S24 + C01-Bl_0:=SEL16 guarded fragment): 2/2 + 1/1 (all three jobs)
- C_S24 (T74 S24 carryover): 2/3 + 1/3 (all three jobs)
- Controls green in same runs: C ORIG 4/4+5/5, A 8/8+15/15 every job. Guarded C01 fragment lifts C_G to 2/2+1/1 vs S24's 2/3+1/3 but does not reach C ORIG 4/4+5/5 — remaining miss is outside C01 Bl_0 (C02/C04 Bl_0 still off-lip, see gate).

**Control states:** all green — bundle md5 guards intact (A-fresh, C-G, C-S24copy) in every stage log; BASE Bl_0 byte-identical to p39 vehicle proof.

**Asserts:** per-arm outer logs carry LINK-SHIM-OK ×1, LINK-FORKMAIN-ABSENT-OK ×1, DRIVER-SHIM-OK ×1 in all 5 arms × all 3 jobs (stage log of 33292678: 5/5/5).

**Render Spartan paths (NOT fetched; lead to pull to C:\PR\SfSpp_preprocessing\artifacts\pota75\):**
- /data/gpfs/projects/punim2657/pota75_repro/C75_C01_arms_vs_ORIG.png (fresh trace vs author trace on same mesh)
- RUNDIR fetches: /data/gpfs/projects/punim2657/sfs_main/pota75_run_<jobid>/pota75_fetch/ (rims_CG/, rims_CS24copy/, GT_C/, P75_*.txt per arm)
- Work dir: /data/gpfs/projects/punim2657/pota75_repro/ (gate75.py, render75.py, sel75.py, patch75.py, edge_*.log, tree_BASE/CONE/PRE/)

**Job IDs (sacct-verified):** 33292678 p75_AC COMPLETED 0:0 (16:37) · 33292704 p75_AC COMPLETED 0:0 (14:54) · 33292722 p75_AC COMPLETED 0:0 (13:45). Prep build+edge: 33290953 (first codegen) + 33292185 (final segment-emit; staged bundles used by E2E).
