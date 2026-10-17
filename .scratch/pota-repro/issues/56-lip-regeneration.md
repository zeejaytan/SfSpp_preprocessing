# 56: S1 lip-shape regeneration — rebuild the lip so the wall stands off

**What to deliver:** a regenerated B-p2 Surface_1 lip with ORIG-like standoff — valid thickness, honest strengths, E2E lift.

**Answers:** E1

**Blocked by:** 55 (CHEAT upper bound: true ORIG positions + old normals → 107 valid med 0.85; +surface-fit normals → 119 med 1.68; standoff 0.73 vs 2.87 — lip SHAPE binds, all walk/rewalk/snap arms upper-bounded dead; scratch surgery exhausted) + 54 (sheets match at 0.34mm away from lip; smooth/swap/flip/trim dead) + 21 (T21 split precedent — RegionGrowing-level regeneration).

**Status:** results-in (worker 2026-10-17, COMMIT NOTHING)

**Starting position:** the lip REGION of S1 must be regenerated, not adjusted: the wall away from the lip is fine (0.34mm), the lip shape defeats the thickness gauge at any rim position. Candidates: RegionGrowing parameter/seed behaviour at the lip (cf. T21 cluster split — the lip may be a fused/seamed cluster), mesh-region refit of the lip from the scan mesh, lip excision + honest re-walk constrained to regenerated material. Constraint from 50: do NOT resample rim spacing in any fix that reaches E2E. Render references: artifacts/t55_xsec.png (walls around failing gauge), artifacts/t54_anatomy.png. Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only.

**Rules:** land ONLY with standoff recovery toward ORIG (2.87) AND/OR valid-thickness recovery toward 97%/med 2.9 AND/OR honest strength lift AND/OR E2E lift ×3 same-binary runs + controls green (B ORIG 9/9+15/15, A 8/8+15/15) in same runs + gates green; renders (eye-check); prep-side scratch copies; assembler E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition.

- [x] Lip-shape diagnosis (which lip material is wrong: fused cluster? seam? noise?) + regeneration arms
- [x] Standoff/thickness/strength/E2E lift or measured why-not
- [x] Job IDs + sacct states

## Comments (worker, 2026-10-17, COMMIT NOTHING)

**Bottom line: measured why-not — no lift. The lip defect is now precisely mechanized, and every regeneration class the ticket lists is upper-bounded dead, including the JOINT bound nobody had tested (perfect positions + band excision together). Scratch surgery on this piece is exhausted; what remains is a genuine NURBS lip-region refit (pipeline work), specified below as successor.**

**Lip diagnosis (OUR-only geometry; ORIG evidence-only, zero ORIG points used):**
- The S1 bulk is innocent: S1 rim-distance quantiles match ORIG from q25 up (5.2 vs 5.2 at q25, 10.6 vs 9.7 med, 22.0 vs 22.2 q90). The defect lives within ~3mm of the rim: OUR holds 12.7% of S1 there vs ORIG 7.7%, and within 1mm 2.6% (~270 pts) vs 0.3% (~30 pts) — an ~8x excess lip-hugging band (~500-pt band at <1.5mm).
- Ray-hit loci: OUR thickness rays land IN the band (hit-locus rim-dist med 0.85, q10 0.13) at shallow depth (med 1.69); ORIG rays pass to the wall (locus med 2.90, depth med 2.87). OUR lip band intercepts rays meant for the wall.
- Sign analysis over pooled OUR S0+S1: 53/187 ray-winners lie IN FRONT of the rim plane (t>0, surface bulges across the rim — ORIG has 0); behind-material depth med is only 1.57 vs ORIG 2.87 (~1.3mm shallow). So the lip band both curls across the rim plane AND sits shallow. Verdict on the ticket's question: neither fused-cluster (walls split cleanly since T21) nor seam — it is a lip-CURL shape error: the NURBS fit followed curled lip scan points instead of ending at the wall like ORIG's chain (ORIG lip band: 216 pts, also curled, but thin enough that rays pass it).
- Renders eye-checked: `SfSpp_preprocessing/artifacts/t56_lip.png` (8 cross-sections: OUR S1 vs ORIG walls evidence-only + true-ray corridor — walls diverge 2–5mm at the lip while coinciding inboard), `SfSpp_preprocessing/artifacts/t56_depth.png` (hit-depth profile along rim: OUR systematically shallow/spiky/escaping vs ORIG's smooth 1–5mm structure; invalids as gaps).

**Regeneration-arm screening (all OUR-side; ORIG diagnostic-only; deterministic numpy, exact repeats identical):**
- JOINT upper bound (TRUE rim positions + lip-band radial excision R=0–3.0 + old/surface-fit normals) — the bound for "excise + re-seat", i.e. lip-region regeneration's ceiling: excise0 66/57 valid → R=1.0: 60/9 → R=1.5: 56/7 → R=2.0: 16/7 → R=2.5: 7/7 (standoff 2.65 ≈ ORIG, but only 7/187 valid) → R=3.0: 0/7. Excision recovers standoff only by deleting the hitters; the wall behind lies outside the 1mm ray corridor (perp-miss), so validity collapses. Position-only (T55: 119) and excision-only (T53: drops to 27) were each dead; the JOINT is dead too — no combination of rim moves + band removal can pass the gauge.
- CURL-CUT simulation (OUR-only curvature-selected exclusion, the offline analogue of a RegionGrowing lip-cut; interior kept): validity FALLS as the cut deepens, 108→45 (OUR rim) and 28→7 (cheat rim) — the curl is load-bearing for the gauge (rays hit curl or nothing). A RegionGrowing variant that cuts the curl is predicted-dead by this bound, so no C++ rebuild/mesh rerun was spent.
- CORRIDOR probe: 85% of true rays DO have OUR material within 1mm perp — but at wrong t (front/shallow). Material exists; its SHAPE/DEPTH is wrong. Only a refit that moves material (not excludes it) could help.

**E2E/strength:** none spent — no arm moved offline joint metrics (validity, median, standoff jointly toward ORIG 146/150 med 2.90 standoff 2.87); T53 precedent applies. Controls/gates N/A (no bundles staged; gate untouched by construction).

**Job IDs + sacct:** none — offline login-node numpy screening only (same basis as T53/T54/T55 gate scripts). No sbatch submitted, nothing to poll. Slurm never touched.

**Successor (pipeline work, not scratch): NURBS lip-region refit of p2 S1** — refit the lip ~12% of S1 from cluster scan points with the curl band excluded (OUR-only curvature selection exists: `pota56_repro/curv_our.npy` + scripts), so the fit ends at the wall like ORIG's chain. Inputs identified: T21 cluster material (`sfs_preprocessing/pota21_fixed/`, `tmpSurfaceCluster*` + `Segments/`), fit stage is the C++ mesh/NURBS path (`original_nurbs_preprocessing/`). Note the refit must move the wall ~1.3mm deeper AND un-cross the rim plane — a cut alone is proven insufficient. Work dir `/data/gpfs/projects/punim2657/pota56_repro/` (diag/joint/corridor/sign/curlcut/render scripts + .npy + t56 PNGs); tickets 49/50/51/52/53/54/55 + p47/p49 flaggers untouched (read-only).

**Successor:** cross-pot generalization of the B recipe (C–J share the drowning shape).
