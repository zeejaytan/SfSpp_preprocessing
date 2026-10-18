# 87: Offset ladder — bind the prune-flip threshold in rim units (S24base +0.5/+1.0/+1.5mm toward crest face)

**What to build:** S24base loops shifted in the normal direction toward the 85B crest face at +0.5 / +1.0 / +1.5mm (one variable each; uniform resample to factor density out; zero teleports; 46 H1 recipe discipline, no ORIG points — the target face is OUR crest, built from OUR points), then E2E x3 per rung on the 85 vehicle with controls in the same runs.

**Answers:** E1

**Blocked by:** 86 (PARTIAL: kill bound to PairwisePruning pre-graph; leading hypothesis = true edge crosses area-50 overlap kill as coincidence rises 24.3→43.7%; sub-gate open; successor §4(i) = this ladder) + 85 (crest NULL: jitter exonerated, flip set by mean face-shift med 0.7-1.0mm) + 73 (S24base seats 2/3+1/3 — the passing reference) + 74 (coincidence mechanism).

**Status:** landed-FLIP-BOUND (lead 2026-10-18 — renders eye-checked by lead; sacct-verified)

**Starting position:** The flip sits somewhere between the S24 face (survives: prune 17, seats 2/3) and the crest face ~0.7-1.0mm away (pruned: 23/27, seats 0/3). Walk the ladder between them. Read 86 Comments §3-§4 for the per-edge table + probe spec before building. Bundles under /data/gpfs/projects/punim2657/pota85_repro/ are READ-ONLY (md5-guarded per job); build ladder bundles as NEW prep-side scratch under /data/gpfs/projects/punim2657/pota87_repro/. Ruler first per rung (face offset achieved, coincidence share), then E2E.

**Rules:** land with the flip rung bound (offset magnitude where prune 17→23+ AND E2E 2/3→0/3 flips, x3 same-binary) + prune-rate table across rungs + verdict whether any HONEST rim variable (sub-tolerance shape noise) can cross it (third loop justified only if the flip sits beyond honest tolerance; else matcher-side fix per 86 §4); controls green (C ORIG 4/4+5/5, A 8/8+15/15) in same runs; renders (eye-check) before landing; E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK asserts per job; no commits; sacct-direct polling (never scripts/slurm_poll.sh); Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); repeats >=3 per rung; SingleOverlapTest@100/RP/CheckGraph-150 stay unless the flip mechanism names them.

- [ ] Ladder bundles +0.5/+1.0/+1.5mm, ruler per rung
- [ ] E2E x3 per rung + prune-rate table + flip rung bound
- [ ] Honest-tolerance verdict (third loop justified or matcher-side fix)
- [ ] Job IDs + sacct states
## Comments (lead landing, 2026-10-18)

Lead review: renders eye-checked (L05 tracks witness near-perfectly, L15 separation clearly larger, no teleports — ladder as designed). sacct lead-verified 33366075/092/093 COMPLETED 0:0. Verdict FLIP-BOUND stands: flip at first rung (<=0.5mm, sub-tolerance), coincidence saturates at L05, failure discrete-identical across all rungs. Third-loop geometry ruled out BY CONSTRUCTION — no honest rim variable can be made robust. C rim work closed; only path is matcher-side (86 §4(ii) instrumented build) per user decision.

## Comments (worker, 2026-10-18 -- COMMIT NOTHING; lead to commit)

VERDICT: FLIP-BOUND at the FIRST rung (+0.5mm). The prune flip AND the E2E flip both sit inside (0, 0.5mm] of normal offset toward the 85B crest face -- i.e. within honest sub-tolerance shape noise. Third loop NOT justified; fix is matcher-side per 86 section 4 (probe ii if the lead wants the sub-gate named).

0. Build (NEW dir /data/gpfs/projects/punim2657/pota87_repro/; tickets 39-86 + pota84 scratch/bundles/artifacts untouched; zero ORIG points; 46 H1 recipe). Per rung m in {0.5,1.0,1.5}: Q = W + m*unit(C85Bsm4 - W) per station (exact normal-magnitude offset toward the crest face; static stations 0/203+0/115 -- every witness station has nonzero crest direction), then closed-loop uniform resample to 1.8mm (n02 = 217/219/220, n04 = 126/127/129; maxjump <= 1.803mm, zero teleports), witness normals/curvature interpolated, witness segment ranges preserved; Bl_0 replaced, Bl_1 witness + C01/C03 untouched; S24base-bundle copies only. build87.py. md5 per bundle (pota87_C_L{05,10,15}_bun_md5.txt); vehicle md5-guards S24base + all three ladder bundles per job (no guard trips).

1. Ruler per rung (GT-seated, login node; S24base/85B values reproduce 86 section 3 exactly):
   rung | n02/n04 | C04->C02 share@2 | med NN | sub-1.5mm | offset-from-S24 med 02/04
   S24base | 203/115 | 24.3% | 8.234 | 13 | -- (survives: prune 17, 2/3+1/3)
   L05 +0.5 | 217/126 | 43.7% | 8.873 | 49 | 0.668/0.709 (offset NN med includes tangential resample shift; normal component exactly 0.5 by construction)
   L10 +1.0 | 219/127 | 44.1% | 8.456 | 51 | 1.074/1.106
   L15 +1.5 | 220/129 | 38.8% | 7.968 | 36 | 1.523/1.556 (share NON-MONOTONIC: pushes past the valley -- recorded, not smoothed over)
   85B crest | 218/126 | 43.7% | 8.565 | 53 | 0.925/0.759
   Coincidence saturates at the first rung: +0.5mm already reaches the full crest coincidence level (43.7%). ruler87.py.
   Renders (eye-checked): artifacts/pota87/C87_L{05,10,15}_overlay_C{02,04}.png -- green offset loop tracks smoothly between red witness and gray ORIG on all 6 panels, no teleports, no spikes, clean closure; L15 separation clearly larger, L05 near-witness as designed.

2. E2E x3 same-binary (jobs 33366075/33366092/33366093, all COMPLETED 0:0; vehicle run_pota87_ladder.sbatch = 85 vehicle + C_L05/L10/L15 7-arm, cure-potA @ bffefb6 k=5/b=3, LINK-SHIM-OK + LINK-FORKMAIN-ABSENT-OK + DRIVER-SHIM-OK 7/7/7 per job; sacct-direct polling):
   arm | prune x3 | sherd x3 | edge x3 | 02-04 dtrans/dang x3
   A_orig | 70 | 8/8 | 15/15 | -- (control green x3)
   A_fresh | 119 | 8/8 | 15/15 | -- (control green x3)
   C_orig | 40 | 4/4 | 5/5 | 2.76-4.06mm / 0.39-0.43deg (control green x3)
   C_S24base | 17/17/17 | 2/3 | 1/3 | 17.37mm / 2.52deg bit-identical x3 (passing reference reproduced)
   C_L05 | 25/24/24 | 0/3 | 0/3 | 1015.12mm / 163.89deg bit-identical x3 -- FLIPPED
   C_L10 | 30/29/30 | 0/3 | 0/3 | 1010.22mm / 165.65deg bit-identical x3 -- flipped
   C_L15 | 22/23/22 | 0/3 | 0/3 | 1025.41mm / 168.04deg bit-identical x3 -- flipped (prune wobbles 22-23 but discrete failure mode identical)
   Prune-rate table (pruned/total): S24base 17/212 = 8.0% x3; L05 24-25/263 = 9.1-9.5%; L10 29-30/275 = 10.5-10.9%; L15 22-23/276 = 8.0-8.3%; (85B 27/267 = 10.1% per 86). Flip criterion (prune 17->23+ AND E2E 2/3->0/3) met at L05 x3 bit-stable; L15 prune dips to 22 but E2E stays discretely failed.
   score87.py; fetch tarballs sfs_main/pota87_run_*/pota87_fetch.tgz.

3. Honest-tolerance verdict: the flip sits at <= 0.5mm normal offset -- a sub-tolerance shape perturbation (INLIER_THRESHOLD = 1.5mm; rim extraction noise is mm-scale; the ladder's own tangential resample shift is ~0.17mm). ANY honest rim variable at this scale crosses the threshold, so no third-loop geometry can be made robust by construction: the ladder proves the matcher kills the true 02-04 edge as soon as the crest loop enters whole-loop coincidence (share 24.3% -> 43.7% at the first rung), consistent with 86's leading hypothesis (area-50 overlap gate). Recommendation: matcher-side fix per 86 section 4 successor (ii) instrumented build to name the sub-gate (overlap-area vs basket-score vs axis-0.436 vs MergeSimPair); keep Pot C parked; E1 entry via lead only.

Paths: bundles /data/gpfs/projects/punim2657/pota87_repro/pota87_bundle_C_L{05,10,15}/ + build87.py/ruler87.py/render87.py/score87.py/run_pota87_ladder.sbatch + C87_L*_overlay_C*.png; runs /data/gpfs/projects/punim2657/sfs_main/pota87_run_3336607{5,92,93}; renders artifacts/pota87/.

