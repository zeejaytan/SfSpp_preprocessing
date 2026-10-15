# 19: Pot A end-to-end assembly on admitted fragments

**What to build:** the proof the whole arc owes — our rims plus our axles reassembling Pot A through the untouched assembly program, with refusals excluded by rule and the authors' arm alongside.

**Answers:** E1

**Blocked by:** 18-refusal-gate (frozen finder + shipped refusal gate below).

**Status:** results-in — worker run 2026-10-16: fresh bundle rebuilt from committed sources (SFS-T13, HEAD 84ba640), gate 15/15 patched / 12/15 ablated reproduced; refusal gate admits 8/8 on fresh surfaces (0 refused); E2E at k=5/b=3 with same-binary ORIG control 8/8 + 15/15 (run valid): fresh-ablated 7/8 + 11/15 (only p2 off, 103 deg), fresh-patched 7/8 + 7/15 (p2 unseated, patch poison). No commits; Comments-only edit.

**Starting position:**
- Rims: fresh Pot A bundle with the SFS-T13 second-chance walk (ticket 13, committed) — gate 15/15 patched arm, 12/15 ablated arm (ticket 13 evidence). Rebuild the bundle from current sources; do not hand-assemble.
- Axles: frozen GM-refine (a)-finder (`.scratch/pota-repro/p15-stage/axle_finder/`, committed) in the shipped `Axes/Pot_A_Piece_0i_Axis.xyz` position-first format the reader parses (`data_structure.cpp:146-187`).
- Refusal gate (ticket 18, shipped): refuse a fragment when vote-best GM cost > 1.40/pt AND round-1 winner share < 0.22. Apply it mechanically; refused pieces are excluded by rule, not by hand — report which pieces (if any) it refuses on Pot A.
- Control: same-binary ORIG arm (authors' bundle + authors' axes) in the same assembly job, must reproduce 8/8 + 15/15 (as in tickets 06/11/13).
- Assembly: pristine program, k=5/b=3 (Table V Pot A). Spartan assembly tree + job recipes from tickets 06/11/13 leftovers.

**Rules:** no source changes to the finder or the pipeline in this ticket — this is a measurement run. If the bundle needs rebuilding, rebuild from committed sources only. One variable at a time if diagnosis is needed (rims vs axles vs search, in that order — the arc's evidence already separates them).

- [ ] Fresh arm: gate score + E2E placed/edges at k=5/b=3, per-piece placement errors (relative-rot scoring vs ORIG, 0.00° method from ticket 11/13)
- [ ] ORIG arm in the same job: 8/8 + 15/15 reproduced (else the run is void, not a failure)
- [ ] Refusal report: gate applied to all 8 Pot A pieces, admitted/refused list, and the E2E scored on admitted pieces with refusals named
- [ ] Laptop poll per sbatch (`sacct` directly); render one representative seating before/after + measurement pair; no commits; Comments-only edits

**Successor:** B–J E2E on admitted fragments (same protocol per pot), then the Juglet question re-opens with a working chain.

## Comments (worker, 2026-10-16)

Measurement run — no source changes to finder or pipeline. Spartan pulled
`--ff-only` to 84ba640 (laptop HEAD, SFS-T13 committed); all run scripts are new
untracked files in `potsac-p19-run/` (frozen `axle_finder/` = `cp` + `diff -r`
verified copy of `potsac-p10-run/`); laptop staging under gitignored
`artifacts/pota19/`. Nothing committed or pushed.

**Jobs (all `sacct` State COMPLETED ExitCode 0:0, polled directly):**
33111823 build (SFS-T13-IN-BINARY, BUILD-EXIT=0, from committed source);
33112015 edge rerun; 33112781 matlab (probe + gate/chain); 33113298 assembly
(3 arms, 14:37). `slurm_poll.sh` still exits immediately — all polling via sacct.

**Rebuild fidelity (fresh bundle from committed sources):** SFS-T13 fired exactly
once with the byte-identical ticket-13 log line
(`second-chance: 0.245902 -> 0.721311, 132/183, 4 jumps`); all other 15 surfaces
pass-1 only. Headers reproduce (p02 patched 750 pts / wall 179; p03 146, p04 140,
p05 135). Vs ticket-13 leftovers: all 16 Surfaces byte-identical, 13/16
breaklines identical; the 3 differences (p02-Bl0, p05-Bl1, p06-Bl1) are
normals-only wiggles (~4 deg, positions identical) = pipeline normal-estimation
nondeterminism, proven immaterial below (probe FRESH==REF on every pair).

**Gate score (probe reimplemented: strict d<2mm & |n.n|>0.85, smaller-cloud
Breakline_0 under GT alignment, PASS >= 2 inliers):** REF==FRESH exactly on all
30 pair-runs, summaries reproduce ticket 13 — patched **15/15** (1-2: 4/0.25,
2-4: 8/0.81, 2-5: 18/0.31, 2-8: 6/0.81); ablated **12/15**, fails only on
p2-touching pairs (1-2, 2-4, 2-5 at 0; min_d 2.03/3.07/5.15mm). One definitional
boundary vs ticket 11's probe: mine passes ablated 2-8 (7 strict, min_d 1.15)
where theirs scored 0 (min_d 1.18), and per-pair counts differ slightly (2-5:
18 vs 21, 2-8: 6 vs 8) — summaries and failing sets agree; probe definition above.

**Refusal report (shipped gate cost>1.40 AND share<0.22, mechanical):**
on FRESH surfaces **8/8 admitted, 0 refused** (nearest: P01 1.444/0.251;
rest cost <=1.21, share >=0.338). ORIG-surface diagnostic in the same job:
P01 REFUSED (1.550/0.216), rest admitted — P01 (known curvature outlier) is
borderline either way. E2E below is scored on all 8 = the admitted set, refusals
named: none on the fresh chain.

**Finder chain on fresh surfaces (diagnostic vs shipped, test key only):**
P01 0.08deg/0.30mm nset2; P02 0.12/0.50 nset2; P03 0.81/0.23; P04 0.49/2.13
(direction-pass, material floor); P05 0.16/0.79 nset3; P06 3.08/9.07
(degrades vs 2.00/6.07 on ORIG surfaces); P07 [0.64 5.23 10.59] nset3
(count found, 2 axles off); P08 [13.34 14.71] both miss. ORIG-surface run
reproduces tickets 15/16 to the decimal — harness faithful. All 8 finder axle
files (position-first `[p d]` rows: 2,2,1,1,3,1,3,2) written into both bundles.
No empty outputs; singular-matrix LM warnings only (chains completed sanely).

**E2E at k=5/b=3 (job 33113298, shim TOP_k 5 / BRANCH_b 3):**
- ORIG control: **8/8 + 15/15**, forest 124/pruned 70 (identical to ticket 13 —
  same-binary determinism; run VALID, not void).
- Fresh-ablated (genuine rims + finder axles): **7/8 + 11/15**, forest 584/75.
  Per-piece rel-rot/trans vs ORIG: p1 0.41/1.7, p2 **102.7deg/232mm OFF**,
  p3 0.67/4.5, p4 0.57/2.5, p5 0.21/2.1, p6 1.17/4.3, p7 0.86/6.3, p8 1.30/5.7.
  Wrong edges exactly the 4 p2 edges (1-2, 2-4, 2-5, 2-8, all ~103deg) —
  matches the binary's 11/15 exactly. Extra finder modes inflate the forest
  (584 vs ticket-13's 258 with ORIG axes) without changing the score.
- Fresh-patched (patch rims + finder axles): **7/8 + 7/15**, forest 1207/36.
  p2 UNSEATED (no T file); the seated 7 sit ~107deg off ORIG as a poisoned
  cluster (only ~5 relative edges survive a strict 5deg/10mm bar; binary counts 7
  — two borderline edges 1-5/6-7 sit at 2-4deg but 12-23mm). Patch poison
  confirmed for the third time (forest 1207 vs 584).

**Render:** `artifacts/pota19/pota19_orig_vs_fresh_seating.png` — placed
Breakline_0 rims under each arm's T, ORIG vs fresh-ablated, top + side views, mm
ticks, equal aspect. Eye-check: clean ring in both; fresh p2 (orange) flung out
left/up, all other rims coincide. Measurement pair = per-piece table above.

**Verdict:** the full-fresh chain (our SFS-T13 rims + our frozen-(a) axles,
refusals excluded by rule — of which there are none on Pot A) seats every
admitted piece except p2 (best 7/8 + 11/15 vs authors 8/8 + 15/15 reproduced
same-binary). p2's failure is search + missing wall content (ablated: true pose
unsupported at the gate on 3/4 seams; patched: gate passes yet the beam seats it
103deg off or drops it). Limitation noted: the axle-observable gate cannot see
rim shortness — p2 is axle-admitted but rim-unplaceable. Next suspects in
evidence order: (1) p2's mesh-stage exterior wall (171-pt scrap, ticket 13);
(2) why the beam prefers a 103deg-off p2 pose over leaving it out.

**E1 `Where it stands` proposal for lead:** fresh chain reproduces the authors'
gate (15/15 patched, 12/15 ablated) and seats 7/8 sherds with 11/15 joins
through the untouched program at k=5/b=3 with finder axles throughout and zero
refusals — the reassembly gap is exactly piece 2, blocked behind the missing
exterior wall and search, not behind rims-in-general or axles-in-general.

**Leftovers:** Spartan `potsac-p19-run/` (all scripts, finder axles, job outs),
`pota19_fresh/`, `pota19_bundle/`, `pota19_bundle_patched/`,
`sfs_main/pota19_verify_33113298/` (3 arms: logs + Result snapshots).
Laptop `artifacts/pota19/` (run scripts, scorer, render inputs + PNG).
