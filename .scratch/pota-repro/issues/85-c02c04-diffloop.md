# 85: C02/C04 different-loop rim-shape (not a re-walk)

**What to build:** a NEW C02/C04 lip loop that rides the true lip face — the 17mm slide shrinks because the overlap hill moves back to truth, not because the search changed.

**Answers:** E1

**Blocked by:** 79 (NULL: guard re-walk reproduces the same off-lip loop — re-walking cannot correct this shape; render eye-checked) + 74 (slide BOUND as content-shifted overlap valley: fresh 24.3% at GT vs 45.2% at the 17.37mm seat; frame exonerated, search sound, C01-independent) + 77/76 (reweighting EXHAUSTED over 21+12 runs — search stays untouched) + 72 (clean lip walks on the S1 branch: C02 Bl_1 0.78mm/98.5%, C04 0.73mm/93% — the true lip exists in OUR data, just not in the loaded slot) + 73 (S24 base: Bl_1 into loaded slot seats 2/3+1/3 x3) + 80 (C02 fused surface — swap alone will not cure it; C04 marginally swapped+doubled).

**Status:** landed-NULL (lead 2026-10-18 — crest family closed raw + smoothed; renders eye-checked by lead; sacct-verified)

**Starting position:** Base = S24base bundles (73/74, read-only). The defect is rim SHAPE: our C02/C04 loops run ~5-6mm off-lip, so the beam's overlap hill peaks at the 17mm slide. Candidate arms, one variable each: (a) lip-face-constrained loop build anchored on the S1-branch lip content (72's clean Bl_1 as the face witness — witness distances only, zero ORIG-style copying: the loop must be built from OUR points); (b) S24base + lip-face-constrained densification toward ORIG spacing (1.8mm uniform, zero teleports — 46 H1 recipe, no ORIG points); (c) your own shape correction that emits a different loop. What is EXCLUDED: re-walking the same walk (79 NULL), search-gate/threshold changes (76/77 exhausted), ORIG points anywhere in a fix. C02's axle is finder-caused and orthogonal (66) — note it, do not chase it unless it blocks seating. Prep-side scratch copies only.

**Rules:** land with fresh-vs-ORIG overlap share at GT at/above ORIG-at-GT 42.7% AND 02-04 relative translation toward <=10mm at same rotation + E2E at/above 2/3+1/3 x3 same-binary + controls green (C ORIG 4/4+5/5, A 8/8+15/15) in same runs; renders (eye-check) before landing; E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK asserts per job; no commits; sacct-direct polling (never scripts/slurm_poll.sh); Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); repeats >=3 per condition; SingleOverlapTest@100/RP/CheckGraph-150 stay unless the shape mechanism names them.

- [ ] Different-loop shape arms, one variable each
- [ ] Gate (overlap share at GT) + E2E rerun x3 or measured why-not
- [ ] Job IDs + sacct states

## Comments (lead landing, 2026-10-18)

Lead review: renders eye-checked (both panels: green 85B loop smooth, no teleports, tracking between red witness and gray ORIG — loop geometry is fine on the ruler, matcher explodes anyway). sacct lead-verified 33363530/531/532 COMPLETED 0:0. Verdict NULL stands with mechanism: prune counts 17->23/27, identical discrete failure across 4-7x jitter difference — branch-flip set by mean face-shift, not curvature noise; ruler gain (43.7%) does not transfer. No third loop geometry without the matcher-side diagnosis. C parked pending user decision on the prune-flip diagnosis.

## Comments worker-2026-10-18 (85B NULL closes the crest family)

BUILT two crest geometries, one variable each, both on the true lip face (two-plane intersect: local normal k-means k=2 + station-Perp plane, dih>=15deg mv<=2.0mm guards, build85.py; per-station correspondence to S24 witness Bl_1 by construction):
- 85A raw crest (pota85_bundle_C_85A): accepted C02 201/203 + C04 115/115; ruler C02-vs-ORIG 0.699/100%, C04 0.811/92.4%; pair share CREST4->CREST2 43.5% raw / BUNDLE 43.0% (uniform-1.8 resample, zero teleports, fin85.py).
- 85B sigma-4 smoothed correction (pota85_bundle_C_85B): loop = witness + Gauss-smooth(crest-witness, sig=4) (sm85b.py/fin85b.py); share 43.7% (bar 42.7 met); ORIG-meandist 0.554/0.744 (beats raw crest 0.699/0.811); jitter |dturn| med 0.74/0.79 deg vs 85A 5.38/4.45 (jit85.py) — curvature noise removed, ruler gain kept.
- Renders artifacts/pota85/C85B_overlay_C02|C04.png eye-checked: smooth, no teleports, green tracks between witness (red) and ORIG (gray).

E2E x3 same-binary (jobs 33363530/33363531/33363532 COMPLETED, vehicle run_pota85_stage_AC85B.sbatch = 85-vehicle + C_85B 6th arm, cure-potA @ bffefb6 k=5/b=3, LINK-SHIM-OK/LINK-FORKMAIN-ABSENT-OK/DRIVER-SHIM-OK per arm per job, score85.py):
- Controls GREEN all 3: A_orig + A_fresh 8/8+15/15; C_orig 4/4+5/5 (02-04 dtrans 2.81mm dang 0.4deg); C_S24base 2/3+1/3 @17.37mm/2.52deg (slide reproduced bit-identical).
- C_85A: sherd 0/3 edge 0/3, 02-04 dtrans 1017.52mm dang 168.45deg x3. C_85B: sherd 0/3 edge 0/3, dtrans 1021.78mm dang 167.5deg x3 (bit-identical).
- Mechanism trace (job 33363530 binary.log): Total-pruned C_S24base 17 vs C_85A 23 vs C_85B 27 — crest loops prune the TRUE branch early; both crest geometries fail in the IDENTICAL discrete mode despite 4-7x jitter difference => branch-flip set by the mean face-shift, not tunable by loop smoothing. Ruler gain (43.7%) does not transfer: matcher keys on whole-loop coincidence count (74 slide-wins), not seam overlap.

VERDICT: NULL for the crest family (raw + smoothed). Exclusions honored throughout: no re-walk, no search-gate changes, zero ORIG points, S24base read-only (md5-guarded per job), scratch bundles only, no commits. Next-of-kin hypothesis for whoever picks this up: diagnose matcher-side (why a ~0.5mm same-face shift flips the branch at prune time) before building a third loop geometry.
Paths: /data/gpfs/projects/punim2657/pota85_repro/{pota85_bundle_C_85A,pota85_bundle_C_85B,pota85_C_85A_bun_md5.txt,pota85_C_85B_bun_md5.txt,run_pota85_stage_AC85B.sbatch,score85.py,C85B_overlay_C02.png,C85B_overlay_C04.png}; runs /data/gpfs/projects/punim2657/sfs_main/pota85_run_3336353{0,1,2}.
