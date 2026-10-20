# 191 - Thin-loop roll-out: Pot G

Status: landed (lead 2026-10-20: 5/7+3/10 x3 verified, controls green, +1 sherd over fresh bar -- first transfer win beyond C)
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
Apply the 185 thin-then-walk cure to every doubled rim edge of Pot G, bundle, and E2E x3 vs this pot's established bar (cite the prior ticket that set it).

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

## Comments (worker, 2026-10-20 -- thin-loop E2E x3 COMPLETE, PASS vs bar; COMMIT NOTHING)

**Verdict: PASS. Thin-then-walk transfers to Pot G: fresh G_191 = 5/7 sherds + 3/10 edges x3 (Total 196, pruned 36-37), beating the fresh bar (60: 4/7+3/10; 39 R1: 4/7+3/10) by +1 sherd, matching it on edges. Falsifier (sherd <=4/7) NOT triggered. Controls green all runs. COMMIT NOTHING held (only this section added to the ticket file; no repo sources touched; dataset read-only).**

**Bar cited:** ticket 60 (Arm C pilot G: fresh 4/7+3/10 x3, jobs 33265362/63/64; ORIG 7/7+10/10 = 51/31) and ticket 39 (G ORIG 7/7+10/10; fresh R1 4/7+3/10 (146/21), R2 3/7+1/10).

**S0. Census (key-free, laptop-rule signals per 179).** Fresh Bl_0 loops vs ORIG loops (same native frame -- raw fresh-vs-ORIG NN med 1.5-2.1mm, so no T needed for reference): G02-Bl_0 n=174 arc 435.5 clo 63.09 gaps10 Dtok31 ratio 2.55; G05-Bl_0 n=153 arc 363.1 clo 34.53 gaps8 Dtok31 ratio 2.44; G06-Bl_0 n=119 arc 272.0 clo 43.88 gaps5 Dtok21 ratio 2.14 -- all three DOUBLED. Other 11 slots single (ratio 1.1-1.4, clo<=2, Dtok 3-5). ORIG loops are clean single rings (G02 112/198.8/1.80, G05 94/166.7/1.80, G06 81/144.3/1.80). Decision: cure ONLY G02/05/06-Bl_0.

**S1. Cure (185 v3 verbatim: 360-bin angular means, 8 smoothing iters, N1=poly/1.8 cap 240, uniform resample, 6-seed walk_m144, key-free min-arc pick).** One documented input substitution: no TRUE strip exists for G, so the fresh doubled walk itself is the band input (doubling is in-walk, same geometry the v3 thinner is built for); author key used CHECK-ONLY for rim-truth, never as input. Loops (mesh frame = bundle frame, no T): G02 108pts arc 192.9 clo 1.79 Dtok2 back0; G05 91pts arc 161.2 clo 1.78 Dtok2 back0; G06 79pts arc 140.7 clo 1.79 Dtok2 back0. All pass closure<=2.0, zero gaps>5, single wrap. Walk md5s: G02 896638a8, G05 a7203d82, G06 5d65a541. Qualification (honest): rim-truth med ~2.15 all three (vs C 0.64) with +1mm systematic radial offset outward (thin med radius 28.0/24.1/21.3 vs ORIG 26.9/23.4/20.6); cov2 ~43% (48/112, 42/94, 33/81) but cov5 ~100% (91/112, 94/94, 81/81); arcs match ORIG within 3%. Eye-checked (artifacts/pota191/): thin loop rides author ring full circuit, small kink sector same class as 180/186. Normals donor = nearest ORIG row (same frame); curvature = author constant 1.905766e-42 (uniq 1, same as C); seg tables rescaled (5:174->108, 4:153->91, 4:119->79).

**S2. Bundle (p191_build.py, port of p186_build.py, BUILD DONE exit 0).** Base = pota39_bundle_G. ONLY G02/05/06-Bl_0 differ (3fc7fe35/e55cd51a/ffd251ee); other 11 slots bit-identical (recursive diff). Veto-absence recorded; vehicle HEAD bffefb6a983403ac45b96aa84a5c52f4fa0a814e + 2-file delta + asserts in-job (LINK-SHIM-OK / LINK-FORKMAIN-ABSENT-OK / DRIVER-SHIM-OK x4 each run). Manifests: pota191_G_191_bun_md5.txt (42 files) + pota191_G_191_BL_md5.txt.

**S3. E2E x3 (run_pota191_stage_G.sbatch, port of p186 AC: 4 arms A_orig/A_fresh/G_orig/G_191, STEPS 8/8/7/7).** Jobs 33484406/07/09, all sacct COMPLETED 0:0 (~14-16 min). Tallies identical (deterministic; pruned 36 vs 37 once):

| job | A_orig | A_fresh | G_orig | G_191 Total/pruned | G_191 sherd | G_191 edge |
|---|---|---|---|---|---|---|
| 33484407 | 124/70 8/8+15/15 | 420/119 8/8+15/15 | 51/31 7/7+10/10 | 196/37 | 5/7 | 3/10 |
| 33484409 | same | same | same | 196/37 | 5/7 | 3/10 |
| 33484406 | same | same | same | 196/36 | 5/7 | 3/10 |

**S4. Verdict vs bar (honest PASS with one note).** PASS: controls green (G_orig 7/7+10/10 = 39 baseline exactly; A arms unchanged); fresh sherds 4/7 -> 5/7 (+1, beats bar); edges 3/10 meets bar; falsifier not triggered; Total 196 > bar 117-146 (more hypotheses generated), pruned 36-37 (vs 15-21). Note: rim-truth gate was weaker than C's (med 2.15, cov2 43%) yet seating still improved -- the gate that mattered was doubling removal (Dtoks 21-31 -> 2), not sub-mm centering. Per-piece identities: binary-level scoring only (5/7 + 3/10); no identity recompute done (cross-arm T comparison is frame-meaningless; each arm reconstructs in its own frame). No further input-side iteration proposed.

**S5. Evidence.** Spartan pota191_repro/ (p191_thin.py/log, p191_build.py/txt, 3 thin npys, run_pota191_stage_G.sbatch, 9 renders, BL/bun manifests); sfs_main/pota191_run_<JOBID>/ (binary logs, snapshots, pota191_fetch.tgz per run). Laptop artifacts/pota191/ (3 fetch tgzs, vs_orig x3, G02 order+sweep, thin+build logs). Parent session: c80e3b10-781d-47e5-bca9-46adfe746564.
