# 194 - Thin-then-walk as default: non-regression on clean Pot B

Status: landed (lead 2026-10-20: REGRESSION verified -- 2/9+1/15 x3, controls reproduce, NOT void; blanket default REFUTED)
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
Prove the thin-then-walk default is HARMLESS on clean rims: force-apply the 185 v3 recipe to Pot B's already-single SXC Bl_0 loops, bundle, E2E x3 vs 93's bar. If tallies match 93, the default is safe everywhere (cures doubled, keeps clean).

## Method (worker runs FULL chain, SSH works -- Host spartan)
0. Densify (143 pre-step): measure dot spacing on each B02-B09 SXC Bl_0 loop first. If coarser than the ~1.8mm regime, true mesh-sampled densify per 143 (ladder to saturation); midpoint interpolation is FORBIDDEN (111/146 refutation -- it adds zero true edge info). If already at ~1.8mm, record spacing numbers and close this step vacuous per loop.
1. Split (175 pre-step, read 175-two-walks-two-slots.md first): apply the 175 split-by-parent-surface rule to each B02-B09 SXC Bl_0 loop BEFORE thinning -- mesh-observable features only, no ORIG in the rule. Expectation on clean singles: each loop yields ONE face cloud (no second cloud); if the split finds two faces inside a 'clean' loop, that is new evidence -- report it, do not silently pool. Then thin+walk the face cloud(s) per step 2.
2. Thin: apply 185 v3 (thin TRUE strip to centreline, uniform 1.8mm resample, verbatim walk_m144) to each face cloud from step 1 (B01 forest excluded, with 78 per 93/187). Gate each loop: closure <=2.0, single wrap, rim-truth med (check-only, expect ~0.5-1.15 per 187).
3. Falsifier (own in advance): any loop whose rim-truth med worsens by >0.5mm vs its unthinned SXC input is REFUSED (not bundled) -- thinning must not move clean dots off the rim.
4. Bundle: rebuild with ONLY the thinned Bl_0 slots changed (byte-proofs, only-changed diff, veto-absence, 180/186 pattern).
5. E2E: same vehicle cure-potA @ bffefb6 (this carries every Pot A-diagnosis change: preprocessing T13/T21/T23/T24/T27 + assembler P22FIX/P22FIX2 + C2-restore per ticket 38 -- verify HEAD before building); same-binary ORIG control must reproduce its bar (93's ORIG arm) or the run is VOID. Upload, login-node build (expect BUILD DONE), sbatch x3 + laptop-side poll per AGENTS.md.

## Constraints
Laptop + Spartan both allowed. COMMIT NOTHING (worker). No repo sources touched, dataset read-only. Finish by writing the self-contained result to this ticket's Comments + final output -- never via send_message.

## Acceptance
Per-loop gates + falsifier check + bundle byte-proofs + E2E tallies x3 vs 93 + verdict (safe-default / regression with refusing numbers).

## Required evidence
Ticket Comments + final output: loop gates, refused loops if any, md5s, job IDs, per-run tallies, verdict.

## Comments (worker, 2026-10-20 -- REGRESSION, thin-then-walk is NOT a safe default; COMMIT NOTHING)

**Verdict: REGRESSION -- force-applying the 185 v3 thin-then-walk to clean single Pot B rims collapses E2E seating from the 93 bar (R2/R3 6/9+5/15, R1 5/9+3/15) to 2/9+1/15 in all 3 runs.** Valid executions (guards green, ORIG controls reproduce, same vehicle) -- the runs are NOT void. The default cures doubled rims (C01) but damages clean singles: do NOT roll out as a blanket default; gate any thinning on a doubling diagnosis (179 census recipe) instead.

**0. Densify (143 pre-step) -- vacuous close, numbers recorded, no midpoint interpolation anywhere.** Mean on-arc dot spacing (arc/n from the 187 census arcs): B02 259.1/116 = 2.23 raw, 1.88 excluding its documented pre-existing 43mm jump; B03 250.8/133 = 1.89; B04 239.0/127 = 1.88; B05 229.3/121 = 1.90; B06 184.2/99 = 1.86; B07 180.8/97 = 1.86; B08 176.8/95 = 1.86; B09 132.8/70 = 1.90. All loops at the ~1.8mm regime (within 6%); input gaps>5mm: only B02's known jump (187 table), rest 0. Nothing coarser than regime, so no mesh-sampled densify; v3's uniform 1.8mm resample fixes output density by construction.

**1. Split (175 rule: tri wall by fn.rhat thresholds -0.5/+0.5 about mesh centroid, dots inherit nearest-tri label, fold joins inner; bundle Mesh/*.obj, same frame -- nearest-tri med ~0.01 except B02 0.11/max 3.3).** Outer-labeled dots: B02 9 (longest run 4), B03 1, B04 0, B05 0, B06 13 (run 3), B07 4, B08 7 (run 4), B09 4 -- scattered singles/pairs, longest run 4, no contiguous second cloud. Expectation holds: ONE face cloud per loop; no two-faces evidence. Reading: label flicker at the lip (fold zone), not a second loop -- several excluded red-x dots sit visibly ON the rim arc (render below). Face clouds: B02 107/116, B03 132/133, B04 127/127, B05 121/121, B06 86/99, B07 93/97, B08 88/95, B09 66/70.

**2. Thin (185 v3 verbatim on face clouds: 360-bin angle centreline + 8x Laplacian smooth + poly/1.8 resample + verbatim walk_m144 6-seed pick).** All 8 gated (closure<=2.0, gaps5=0, D-tokens 2, single-wrap +/-0.98..0.99 backfrac 0):

| loop | N1 | arc | closure | med/max | rim-truth med/cov | falsifier delta vs unthinned SXC |
|---|---|---|---|---|---|---|
| B02 | 124 | 221.2 | 1.79 | 1.79/3.08 | 1.60, 72/150 | +0.457 keep (marginal -- cov 83->72, excluded rim dots 6-12 likely mislabeled) |
| B03 | 136 | 242.6 | 1.78 | 1.78/3.67 | 0.84, 139/143 | +0.224 keep |
| B04 | 129 | 230.9 | 1.79 | 1.79/3.68 | 0.55, 132/136 | -0.013 keep |
| B05 | 122 | 217.7 | 1.79 | 1.79/3.36 | 0.49, 127/131 | -0.111 keep |
| B06 | 98 | 174.9 | 1.79 | 1.79/3.63 | 0.59, 103/104 | +0.068 keep |
| B07 | 97 | 172.2 | 1.78 | 1.78/3.64 | 0.62, 101/104 | +0.089 keep |
| B08 | 94 | 166.8 | 1.78 | 1.78/2.91 | 0.70, 97/101 | +0.206 keep |
| B09 | 70 | 124.9 | 1.79 | 1.79/3.36 | 0.79, 74/75 | +0.168 keep |

**3. Falsifier: none refused** (worst delta +0.457 < 0.5; B02 kept but flagged marginal above).

**4. Bundle (93-SXC base + ONLY 8 thinned Bl_0 installed).** NNEW 124/136/129/122/98/97/94/70; self-donor (unthinned SXC loop) NN channels, med donor-dist 0.55-0.71 (B02 max 18.05 at the jump, n>5mm=17 -- jump region only); seg headers OLD->NNEW proportionally rescaled (continuity enforced); WIDTH/POINTS=NNEW verified per file. Proofs: Bl diff = ONLY B02-B09 Bl_0 differ; recursive diff = same 8 files; 93-SXC md5sum -c ALL-OK (base untouched); B01 md5-identical to 93 SXC (bc1b72d8...); bun manifest 54 files; veto grep ABSENT; vehicle asm HEAD bffefb6a983403ac45b96aa84a5c52f4fa0a814e tree-clean, ancestry holds P22FIX2 9f432bc + P22FIX 89f771c + C2-restore b35905b; prep ancestry holds T13 b0083ae + T21 f39b1b0 + T23 f08d960 + T24+T27 48ca2c0 (all read-only verified). New-Bl_0 md5 prefixes: B02 36792003, B03 5d5f1e2f, B04 91a3202f, B05 8ec5d6f6, B06 4530c5b7, B07 9c83f43a, B08 4251d284, B09 bbe961ef (full in pota194_B_194_BL_md5.txt).

**5. E2E (run_pota194_stage_AB.sbatch = 93's sbatch with B_194 path swaps + D_SXC-unbound-var fix; cure-potA @ bffefb6 asserted in-job; k=5/b=3; STEPS 8/8/9/9; sacct-direct polling throughout):**

| job (sacct COMPLETED 0:0) | A_orig | A_fresh | B_orig | B_194 |
|---|---|---|---|---|
| 33485122 (20:22) | 124/70 8/8+15/15 | 420/120 8/8+15/15 | 114/77 9/9+15/15 | 554/44 2/9+1/15 |
| 33485129 (16:28) | 124/70 8/8+15/15 | 420/120 8/8+15/15 | 114/77 9/9+15/15 | 554/45 2/9+1/15 |
| 33485130 (22:11) | 124/70 8/8+15/15 | 420/119 8/8+15/15 | 114/77 9/9+15/15 | 554/44 2/9+1/15 |

Asserts 4x LINK-SHIM-OK + 4x LINK-FORKMAIN-ABSENT-OK + 4x DRIVER-SHIM-OK per job; all containers exit 0; snapshots non-empty (T-counts 8/8/9/9); fetch tgzs pota194_fetch.tgz (111150/111208/111178 B) per RUNDIR. Same-binary ORIG controls reproduce 93 exactly (A_orig 124/70 8/8+15/15; B_orig 9/9+15/15, pruned 77 vs 76-77) -- runs NOT void. Total hypotheses shift 464->554 proves the thinned bundle (not the 93 bundle) reached the binary.

**Regression numbers:** bar R2/R3 seated [1,3,4,6,7,9] 6/9+5/15 (R1 5/9+3/15); B_194 seats 2/9 with 1/15 edges, binary-identical all 3 runs (deterministic, not beam variance -- cf. 38's 7-8/8 class). At least 4 of 93's seated pieces drop; which 2 still seat (and the exact dropping set) needs GT-scoring of the T-files -- new analysis code, NOT run under this ticket's script freeze; requesting re-approval as follow-up.

**Mechanism notes (hypotheses, not conclusions).** (a) The resample replaces measured author dots with centreline interpolations -- per 111/146 that adds zero true edge info while moving every station the matcher keys on; clean rims pay the cost with no doubling to cure. (b) B02's exclusion-driven drift (rimmed 1.60, cov 72/150) may seed a bad linchpin (93: piece-2 flip already the SXC weak point), but one weak rim cannot alone explain 7 unseated -- the 464->554 hypothesis-space shift points to a global feature change. (c) Step-1 exclusion of on-arc dots as "outer" (B06 13, B02 9 incl. run 6-12) thins real rim content the walk then bridges by smoothing.

**Evidence.** Spartan pota194_repro/ (p194_split/thinface/build2/wrap2 .py + .txt logs, parentface/facecloud/thinface_walk .npy, p194_face_thin.png, run_pota194_stage_AB.sbatch, pota194_B_194_BL_md5.txt, pota194_B_194_bun_md5.txt, prep/pota194_bundle_B_194/) + sfs_main/pota194_run_{33485122,33485129,33485130}/ (per-arm logs, snapshots, pota194_fetch.tgz). Laptop artifacts/pota194/p194_face_thin_TMP.png (step-0/1 render, eye-checked: 8 single closed rims, blue walks track green clouds, red-x exclusions scattered/on-arc, B02 chord bridges the known jump). No commits; dataset read-only (ORIG = distance-evidence only, zero ORIG points in bundle).

