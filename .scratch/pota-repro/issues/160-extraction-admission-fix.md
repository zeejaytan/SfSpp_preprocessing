# Stop emitting the false face at extraction (sub-copy admission fix)

GOAL: NO FALSE FACE IN THE FIRST PLACE -- THE VETO HAS NOTHING TO TRIAGE.

**Answers:** E1

**Blocked by:** 150 (admission = edgeline_extraction_headless.cpp:949 angle gate + :1032 dead reload-over; TAP closable at cloud level; select-FIRST-then-walk named, patch not applied) + 155 (sub-copy :920 entry, live Ticket-05 filter keeps outer, veto+sequencer diffs staged) + 156/158 (downstream veto can only triage; fixed rule misfires, off is worse).

**Status:** results-in

**What to deliver:** (a) ANALYSIS: on Pot A + Pot C P01 clouds, where the outer-face dots enter (angle gate? reload-over? Ticket-05 filter?) with per-site counts. (b) FIX: an admission-side change in the SUB-COPY (original_nurbs_preprocessing/) that rejects the outer face BEFORE the walk -- e.g. face-side select at cloud level per 150, or TAP closure -- such that Pot A keeps its 155 cure pair counts (P02_0 ~97 etc.) AND C01's output contains no outer-face loop (gate at-or-better-than fresh 5.61/22.9 with the false loop gone). (c) PROOF: worktree build + both pots run + 98-gate both + renders.

**Starting position:** 150/153/155 Comments (code sites :920/:949/:1032, Ticket-05 filter, TAP, worktree + build commands, staged inputs, gate scripts); pota158_repro variant-build pattern. New scratch pota160_repro/; renders artifacts/pota160/.

**Rules:** same-binary ORIG control alongside or void; worktree-local build only, restore byte-identical after; COMMIT NOTHING; tickets 39-158 read-only (159 superseded, do not build on it); Comments-only ticket edits; sacct recorded; eye-check renders. A clean negative (admission sites inseparable -> veto is the only lever) is a landing result.

- [ ] per-site admission counts A + C01 (gate / reload-over / filter)
- [ ] admission-side fix implemented + variant binary built
- [ ] Pot A pair (cure kept) + C01 gate (false loop gone, rim kept)
- [x] per-site admission counts A + C01 (gate / reload-over / filter)
- [x] admission-side fix implemented + variant binary built
- [x] Pot A pair (cure kept) + C01 gate (false loop gone, rim kept)
- [x] Verdict + render paths
## Comments (worker 2026-10-19/20, FIX-VG head-to-head)

VERDICT: clean negative. Tested FIX-VG = 155 veto hunk ONLY on pristine-HEAD sub-copy
(production greedy+T13 sequencer kept; 155 split-walk port + 159 Otsu adapt dropped).
Pot A: PASS (all 8 pieces cured, Bl_1 reductions are outer-loop removals per renders).
C01: FAIL (VAR med 5.96/cov2 1.3% vs BASE 5.61/22.9% -- veto eats 21/86 near-ORIG rim dots,
greedy threads the rest ~6mm off-rim). No {veto,no-veto}x{greedy,splitwalk} combo passes both.

Per-site admission counts (C01 S0 / Pot A P01-P08 S0,S1, VAR run edgeline_stage_VAR.log):
- :909 angle gate 0.6pi: admits both faces, no face test (C01 S0 pre-veto cloud 364 dots;
  Pot A S0 clouds 234-357 dots per T05 'of N').
- :920 veto align<=0.5: C01 S0 kept=223 dropped=141; S1 109/0. Pot A S0 drops bulk
  (P02S0 107/156, P05S0 130/227, P08S0 169/126); S1 mostly 0 except P01S1 135/201, P08S1 243/70.
- :966 snap K=1 resampled: not isolable post-hoc (per-surface intermediates overwritten,
  only final surface survives); T05-input sizes equal veto-kept exactly (C01 S0 of 223,
  Pot A of 234/135/107/...) so snap net-add ~0 on vetoed clouds.
- T05 filterBoundaryNoise: BASE C01S0 343/21 of 364; VAR C01S0 166/57 of 223; VAR Pot A S0
  removes 21-41/surface (135->114, 107->67, 138->109, 128->90, 130->98, 195->154, 169->136);
  production Oct16 binary also carries live T05 (removes 0-4/surface).
- sequencer: BASE greedy+T13 output 402 from T05-kept 343 (T13 second-chance ADDS dots);
  156 splitwalk 335/30.18, 158 NOVETO 335/30.18 vs fresh greedy 402/5.61 on the same cloud --
  walker swap alone flips C01 5.61->30.18.

C01 ORIG-overlay (364 veto-site dots, TS-mapped, vs ORIG Bl0+Bl1; ADAPT-instrumented binary,
measurement only): NEAR<2mm 86 dots (align_med -0.905, p90 +0.759, kept@0.5 75.6%);
FAR>5mm 91 dots (med +0.758, p10 -0.878, kept 46.2%); align gap (-0.5,0.5] EMPTY.
Threshold sweep t=0.5/0.7/0.9 -> near 75.6/79.1/100 vs far 46.2/47.3/94.5: NO threshold
separates near from far (true rim itself spans both modes -- flaring break).
Radial probe (mesh-observable, analysis only): FAR r_med=34.65/z_med=431.76 vs NEAR
r_med=58.90/z_med=402.60; r>=47.69 keeps near 98.8%/far 11%, but med-2MAD adaptive form is
knife-edge (k=2: C01 far-kept 25%; k=1.5: clean-S1 erosion 11%) -- no safe production form,
not built. Recommended follow-up, not a 160 claim.

Head-to-head (job 33425466 COMPLETED 0:0 1:33; build 33425441 COMPLETED 0:0 0:42):
BASE=Oct16 production binary, VAR=EdgeLineExtractionHeadless_VETOGREEDY md5
ebb8dc3a31b496fb6ec47606d34ed21 (FACE VETO yes, ADAPT/SPLIT-WALK absent). Same staged inputs.
Pot A BASE->VAR pcd POINTS Bl_0/Bl_1: P01 193/193->191/153; P02 727/155->79/155;
P03 485/146->117/146; P04 242/140->101/140; P05 326/135->55/135; P06 144/137->105/137;
P07 64/63->37/63; P08 61/56->16/41. C01 BASE Bl_0 n=402 med 5.61 cov2 22.9% (= fresh,
same-binary ORIG control GREEN); VAR Bl_0 n=226 med 5.96 cov2 1.3%; Bl_1 92=92 identical.

Renders (artifacts/pota160_*.png, eye-checked): C01 VAR loop misses rim sections BASE tracks;
PA P01/P02/P08 VAR single clean loops vs BASE doubled loops.
Scratch: /data/gpfs/projects/punim2657/pota160_repro/ (C01_BASE/C01_VAR/PA_BASE/PA_VAR,
renders/, worktree_backup/, worktree_initial.patch == restored.patch).
Worktree restored byte-identical (md5 ae5070d5/e85e2f50/19397aab; git diff identical;
untracked EdgeLine_BASE/Temp_run_base/Surface_* pre-existing relay leftovers, untouched).
COMMITTED NOTHING.
