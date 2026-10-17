# 56: S1 lip-shape regeneration — rebuild the lip so the wall stands off

**What to deliver:** a regenerated B-p2 Surface_1 lip with ORIG-like standoff — valid thickness, honest strengths, E2E lift.

**Answers:** E1

**Blocked by:** 55 (CHEAT upper bound: true ORIG positions + old normals → 107 valid med 0.85; +surface-fit normals → 119 med 1.68; standoff 0.73 vs 2.87 — lip SHAPE binds, all walk/rewalk/snap arms upper-bounded dead; scratch surgery exhausted) + 54 (sheets match at 0.34mm away from lip; smooth/swap/flip/trim dead) + 21 (T21 split precedent — RegionGrowing-level regeneration).

**Status:** ready-for-agent

**Starting position:** the lip REGION of S1 must be regenerated, not adjusted: the wall away from the lip is fine (0.34mm), the lip shape defeats the thickness gauge at any rim position. Candidates: RegionGrowing parameter/seed behaviour at the lip (cf. T21 cluster split — the lip may be a fused/seamed cluster), mesh-region refit of the lip from the scan mesh, lip excision + honest re-walk constrained to regenerated material. Constraint from 50: do NOT resample rim spacing in any fix that reaches E2E. Render references: artifacts/t55_xsec.png (walls around failing gauge), artifacts/t54_anatomy.png. Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only.

**Rules:** land ONLY with standoff recovery toward ORIG (2.87) AND/OR valid-thickness recovery toward 97%/med 2.9 AND/OR honest strength lift AND/OR E2E lift ×3 same-binary runs + controls green (B ORIG 9/9+15/15, A 8/8+15/15) in same runs + gates green; renders (eye-check); prep-side scratch copies; assembler E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition.

- [ ] Lip-shape diagnosis (which lip material is wrong: fused cluster? seam? noise?) + regeneration arms
- [ ] Standoff/thickness/strength/E2E lift or measured why-not
- [ ] Job IDs + sacct states

**Successor:** cross-pot generalization of the B recipe (C–J share the drowning shape).
