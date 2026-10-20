# 189 - Thin-loop roll-out: Pot E

Status: landed (lead 2026-10-20: HONEST NEGATIVE verified -- 13 gated loops ship, E2E below bar x3, only E23 converts; generation fixed, placement fails downstream)
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
Apply the 185 thin-then-walk cure to every doubled rim edge of Pot E, bundle, and E2E x3 vs this pot's established bar (cite the prior ticket that set it).

## Method (worker runs FULL chain, SSH works -- Host spartan)
1. Census: for each rim piece, test for doubling with key-free signals (closure distance, arc vs plan perimeter, D-token count per the 179 recipe). Name which edges are doubled.
2. Cure: apply the 185 v3 recipe (thin TRUE strip to centreline, uniform 1.8mm resample, verbatim walk_m144) to each doubled edge. Gate each loop: closure <=2.0, single wrap, rim-truth med where an author key exists (check-only).
3. Bundle: rebuild this pot's bundle with ONLY the cured Bl_0 slots changed (byte-proofs, only-changed-diff, veto-absence record, same guards as 180/186).
4. E2E: upload, login-node build (expect BUILD DONE), sbatch x3 + laptop-side poll per AGENTS.md, sacct tallies. Own a falsifier in advance.

## Constraints
Laptop + Spartan both allowed. COMMIT NOTHING (worker). No repo sources touched, dataset read-only. Finish by writing the self-contained result to this ticket's Comments + final output -- never via send_message (child-to-parent messaging does not exist).

## Acceptance
Per-piece doubling census + per-loop gates + bundle byte-proofs + E2E tallies x3 (Total/pruned/sherd/edge) vs the pot's bar + honest verdict (pass / honest negative with the refusing numbers).

## Required evidence
Ticket Comments + final output: census numbers, loop gates, md5s, job IDs, per-run tallies, verdict.

## Comments (worker, 2026-10-20 -- full chain COMPLETE, HONEST NEGATIVE; COMMIT NOTHING)

**Verdict: HONEST NEGATIVE.** 13 gated thin loops installed as E Bl_0 generate
abundantly (Total 15579 x3, 8x the ORIG control) but seat at/below the fresh
bar on all three runs. Only one cured piece (E23, edge 23-24, 2/3 runs) converts.
The gate for Pot E is downstream of generation (placement/pruning-side, or
fresh-channel/segment-side) -- NOT the doubled input. No further input-side
iteration without new evidence. Falsifier (pre-registered, 179-style): E_189
sherd total stays at fresh level (~7) -- CONFIRMED (2-6/31 vs bar 7/31).

**Bar (prior ticket that set it): t90 s5 -- best-fresh 7/31+4/62; ORIG envelope
30-31+58-62 (same-run ORIG arms here reproduce 31/31+61-62/62, so the vehicle
is consistent with t90's).**

**S1. Census (key-free, login node, fresh pota39_bundle_E; closure/arc/gaps5/
D-tokens per the 179 recipe).** Slot 1: all 31 single (closure ~1.9, gaps 0-1,
ntok 3-5) -- no cure. Slot 0: 6 single (E01 203pts/392mm/1.62/1/3tok;
E22,E24,E26,E30,E31 similar) -- no cure; **25 doubled** (E02-21,E23,E25,E27-29:
n 109-946, closure 14-122 or gappy, ntok 14-53, e.g. E04 946pts/1923mm/26gaps).
Doubled = every slot-0 edge except the 6 singles.

**S2. Cure (185-v3 port, one documented deviation: thin input is the fresh
doubled walk xyz, not the TRUE strip -- no per-piece TRUE bags exist for E;
angle-binning averages strands identically; walk_m144 verbatim p176_lib via
the p184 copy; 6 seeds, key-free pick).** 24/25 pass key-free gates first try
(closure <=2.0, gaps5 0, n<=240, D-tokens collapsed to 2-7, runs 25-142).
E19 centreline had one 5.57mm coverage jump (gate FAIL) -> documented fallback:
linear-subdivided the jump (172->174pts), re-walked, now closure 1.86/gaps 0.
Rim-truth re-gate (185 acceptance; ORIG key CHECK-ONLY, never built from;
frameless -- fresh and ORIG rims are already co-framed, med-none ~1mm, the
gate_fetch T maps elsewhere): **13 shipped** (cured-vs-ORIG1 med <=2.0mm lab
standard): E02 0.90, E03 0.98, E09 0.91, E11 1.30, E14 1.04, E17 0.90, E20 0.56,
E21 0.88, E23 0.60, E25 0.76, E27 0.69, E28 0.82, E29 0.53. **12 refused**
(truth drifted vs fresh): E04 2.53/1.77, E05 3.32/1.33, E06 3.32/4.38,
E07 6.81/6.28 (forest, cf. t90), E08 4.00/6.04, E10 5.18/2.33, E12 2.88/1.32,
E13 4.21/1.58, E15 3.07/2.83, E16 5.71/1.49, E18 3.43/2.13, E19 3.70/1.20 --
left fresh. Render eye-check caught what gates passed: E16's loop skips a whole
top sector (wrong-strand pick, angle-mean fragile under 4-5x strands); E10
bulges past truth (+50mm arc). Channels fully fresh-side (fresh-normal NN
donor meds 0.6-0.9, n>5mm 0; normals unit-exact everywhere).

**S3. Bundle (base = t39 fresh E, cp-a).** ONLY the 13 cured Bl_0 differ (62
files: 13 DIFFERS, 49 bit-identical -- asserted, sets match exactly).
Veto-absence (all flag 0) asserted per piece; segs rescaled fresh->newN (p186
mechanics). Manifest: Spartan pota189_repro/pota189_E_189_BL_md5.txt.
BUILD DONE exit 0, in-job bundle guard green in all 3 jobs.

**S4. E2E x3** (cure-potA @ bffefb6 asserted in-job, k5-b3 shim, STEPS 8 A /
31 E arms, 4x LINK-SHIM-OK + DRIVER-SHIM-OK per job; sbatch ported from t90's;
run dirs sfs_main/pota90_run_3348438{8,9,0} -- RUNDIR kept t90's name, cosmetic).
Jobs 33484388/89/90 all COMPLETED 0:0.

| job | E_189 Total/pruned | sherd | edge | E_orig | A_orig | A_fresh |
|---|---|---|---|---|---|---|
| 33484388 | 15579/258 | 6/31 | 2/62 | 1912/822 31+61 | 124/70 8/8+15/15 | 420/119 8/8+15/15 |
| 33484389 | 15579/248 | 2/31 | 1/62 | 1912/827 31+61 | same | same |
| 33484390 | 15579/261 | 4/31 | 1/62* | 1912/824 31+62 | same | same |

*390 binary prints 4/31+1/62; strict identities (p90 recipe, 0.35rad/50mm)
recompute 4 pieces [23,24,26,30], 2 edges (23,24),(26,30) -- same class of
binary-vs-identity delta t90 noted. Run-388 identities: pieces [1,6,23,24],
edges (1,6),(23,24). Run-389: [26,30], edge (26,30). Cured pieces seating:
E23 only (2/3 runs, with single E24); the other 12 cured never seat anywhere.

**Why-not (measured).** Generation is fixed (15579 hypotheses) but placement
fails: 60/62 true edges place-but-wrong (ang 0.6-3.1, tr 150-1400). Prime
suspects for lead: (1) channels -- Pot C's landing cure used G0 AUTHOR normals;
this run used fresh NN normals (zero-ORIG rule kept; truth-near loops still
don't seat, so the loop shape is not sufficient); (2) segment windows --
rescaled-fresh segs vs ORIG seg structure uncompared. E23 (the one converter)
is evidence the vehicle CAN seat a thin loop -- the other 12 lack something E23
has (E23 truth med 0.60, among the best).

**Evidence.** Spartan pota189_repro/ (thin189.py, fix19_189.py, build189.py,
rimtruth189.py, coverage189.py, census/norm scripts, run_pota189_stage_AE.sbatch,
E*_thin_walk.npy x25 + E19b, renders/, prep/pota189_bundle_E_189/,
pota189_E_189_BL_md5.txt, logs); laptop artifacts/pota189/ (3 fetch tgz,
thin/build logs, E02/E10/E16 order-traces). Tickets 39-188 read-only;
no repo sources touched; dataset read-only; COMMIT NOTHING (tracked diff =
this section only).

**Follow-ups for lead (no action taken):** (a) median-per-bin re-thin for the
12 refused (angle-mean is strand-fragile -- E16 sector skip is the exhibit);
(b) channel/segment ablation (G0-normal variant vs rescaled-seg variant) to
isolate why truth-near loops don't seat; (c) E07 forest stays with t78.
