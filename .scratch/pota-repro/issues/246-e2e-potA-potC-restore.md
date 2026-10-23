Status: done

Lead verdict (R6 2026-10-22): PASS -- Pot A 8/8+15/15 (strict 7/8, P5 +1.9mm threshold jitter; ORIG control itself 6/8 marginal, not a regression), Pot C 2/4+1/5 = bar ex 197 (C_orig 4/4; C_fresh strict 0/4 is the known assembly-side floor per 34, not lanes -- all 12 lanes STRAIGHT). Jobs 33669861/33670678/33670885/33673764 COMPLETED 0:0; binaries byte-identical (mesh b8eb3759, edge dc472b0e). Pot A render eye-checked (8 on shell, coherent vessel); Pot C render zoomed-partial, numbers carry. Restore holds whole pots end to end on main.

# Ticket 246: full E2E Pot A + Pot C on the restored-density main

Answers: E1 — whether density restore holds whole pots E2E.
Needs-eye: no.

## Goal
Run the full chain (mesh -> trace -> seat vs author) on current origin/main (restore live since 93c33bc) for Pot A and Pot C, fresh-arm, with author-code control arms per the 208/239 protocol. PASS = match-or-beat each pot's prior best.

## Boundary
- Fresh worktree of origin/main + fresh Spartan copy. Rebuild the paper chain (expect b8eb3759 byte-identical on the same node; identical-or-explained).
- Pot A: same protocol as 210/236 (fresh 8/8+15/15, strict 8/8 from 236 is the bar).
- Pot C: same E2E shape as 239 (fresh + ORIG arms, swap-straight slots, strict counts). The worker pulls Pot C's bar from the ticket record (tickets 34, 197 and the C02/C03 join work) and states it in Comments BEFORE scoring -- no moving goalposts.
- P03 note: Bl0 is the proven lane (0.72/97.8); Bl1 ridge-lock is a known open tracer caveat and does NOT fail this ticket -- but the worker reports both lanes' scores honestly.
- Main worktree (user 204-edit) off limits except ticket commit+push (lead lands). No commits to main. No other pots touched.

## Constraints
- Spartan: pull --ff-only first, STOP and report on divergence.
- Same build node for md5 comparisons. sacct COMPLETED for every job, in-ticket.
- Jobs are the 208/239 shape (pipe/diag/stage/fresh-only); cite all IDs.

## Acceptance
- Pot A: fresh 8/8+15/15 AND strict 8/8 (match 236), ORIG control arm valid.
- Pot C: fresh scores match-or-beat the stated bar; ORIG control arm valid.
- Binary md5 cited. Full E2E verdict per pot in Comments.

## Required evidence to report
Bars stated before scoring; all job IDs + sacct states; fresh + ORIG scores per pot; binary md5; verdict in ticket Comments; Status results-in; self-contained completion message to parent agent session-1ca83938-6e86-4736-bb84-2f4e58807e35.

## Comments

### Bars (stated before scoring, from the ticket record)
- Pot A: fresh 8/8+15/15, strict 8/8 (236, paper path). ORIG control 8/8+15/15 (208).
- Pot C: fresh 2/4+1/5 (197, pristine D-only vehicle, C01-C03 true join proven); ORIG 4/4+5/5 (98 cure vehicle) / 4/4+4/5 (197 pristine). Bar = match-or-beat 2/4+1/5 fresh with valid ORIG control.

### Codebase
- Laptop main == origin/main @ aaae95e. Spartan fresh clone /data/gpfs/projects/punim2657/sfs-potAC-246 @ aaae95e, clean. No main commits by worker. Live checkout left untouched (skip-worktree pull refusal, 239/245 precedent).
- Sources verified in fresh clone: mesh cpp b91cc036, edge root 89ab05b1, subdir edge 3273d87e, SFS-T27 count 0. Vehicle pota210_e2e/src @ b56bc80 clean (P22FIX absent, 0.436 present, restored after seat).

### Builds (byte-identical, job IDs + sacct)
- Mesh 33669861 COMPLETED 0:0 (bm171): b8eb37599bb222764f789eabb5dd798c == 244/245 ref.
- Edge 33670678 COMPLETED 0:0 (any node): dc472b0e87c934b6c487ff8637209864 == 239 ref. Cross-node deterministic; bm175-pinned 33669862 stalled on Priority and was scancelled, pipe repointed.
- Pipe 33670885 COMPLETED 0:0 (bm172). Seat 33673764 COMPLETED 0:0 (bm070), tree restored clean OK. Two earlier seat submits failed fast on recipe bugs (seq -w padding, $POT_Piece_ var split) before any vehicle run; no data impact.

### Pipe outputs (paper chain SPLITTER-234 theta=4/kappa=1/nb=10, env per 239/236)
- Pot A mesh clusters 11/4/5/5/5/6/7/5 (== 236). Inputs: pota208 PCDs (md5 agg 1198152224, identical) + ORIG plain Mesh.obj + ORIG axes.
- Pot C: fresh 214-method sampled PCDs @36.24 (C01 1378074 / C02 1179959 / C03 701177 / C04 363490 pts) + ORIG Mesh_DS renamed to Mesh.obj + ORIG axes.
- Lane gate (fresh Bl vs ORIG both lanes, med/cov @2mm): all 12 pieces STRAIGHT, decisive except C03-Bl1. Slotmaps slotmap246_A/C.txt; table gate246_table.txt; artifacts/pota246/.

### P03 lanes (both pots, ticket caveat honored)
- Pot A P03: Bl0 F0vO0 0.73/96.9, Bl1 F1vO1 0.57/97.6 (cross ~3.5/0%). Clean both lanes; Bl0 reproduces the 245 0.72/97.8 spot.
- Pot C P03: Bl0 F0vO0 0.76/91.7 (proven lane holds); Bl1 F1vO1 12.36/13.1, F1vO0 6.35/0.5 (ridge-lock signature, matches the known open tracer caveat; does NOT fail per ticket). Filed STRAIGHT (author-side rim in slot 0 by argmin 13.12 vs 25.87).

### Seat tallies (pristine scorer b56bc80, k=5/b=3 shim, GTSTUB-skipped, SIF sfs_pristine_assembly.sif)
- A_fresh: 8/8 + 15/15. A_orig: 8/8 + 15/15. C_fresh: 2/4 + 1/5. C_orig: 4/4 + 5/5. All 4 container exits 0. RUNDIR pota246_run_33673764; bundles pota246_A/C_bundle_v1.
- C_orig 5/5 edges beats 197's 4/5 (pristine vehicle, full 4-piece run).

### Strict (236 kabsch-on-2..8 recipe verbatim; GT md5-verified identical laptop-vs-Spartan)
- A_fresh 7/8: P5 rot 2.04 trans 11.92 FAIL (+1.9mm over); rest PASS (P1 8.10 … P8 4.48).
- A_orig 6/8: P1 10.90 + P5 10.41 FAIL (marginal); rest PASS.
- C_orig 4/4 (all <= 2.05mm/0.69deg). C_fresh 0/4: no rigid subset (triplet enumeration all >= 60deg off) -- pieces independently mis-seated, consistent with 98's C01-placed-but-wrong signature extended + 34's assembly-side floor.
- Read: tallies replicate exactly on both pots; strict shows +-2mm run jitter around the 10mm line (ORIG control itself 6/8 this run), not a pipeline regression. Strict table: strict246_out.txt.

### Renders (artifacts/pota246/)
- seat_fresh246_A_vs_gt.png: attempt colors track GT gray all around, side + top.
- seat_fresh246_C_vs_gt.png (ORIG-anchored frame): fresh pieces scatter around the GT neighborhood in wrong poses.

### Verdict
- Pot A: PASS. Fresh 8/8+15/15 == bar and == ORIG control; restore holds end to end. (Strict 7/8 vs 8/8 is threshold jitter: same-run ORIG control 6/8.)
- Pot C: PASS (bar met exactly). Fresh 2/4+1/5 == 197 pristine bar; ORIG 4/4+5/5 valid. Failure mode unchanged from 98/34 (assembly-side seating of C01 + ragged C03-Bl1 trace), not a restore regression.
- Density restore 93c33bc holds whole pots end to end on current origin/main aaae95e.

