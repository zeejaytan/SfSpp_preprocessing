# 68: Split-then-select repair — one loop, the inner one

**What to deliver:** C Bl_0 files holding a single inner-lip loop each — gate + E2E recovery.

**Answers:** E1

**Blocked by:** 67 (doubled-loop bound: C01 run2 152 + run3 211 each ~5.5mm off ORIG + cross-mouth spur run1 29; C04 outer loop 134 + 48-pt fold-back + 9-pt nub; C03 single arc fails via neighbours; C02 same disease + finder axle miss; guilty stage getPointsInSequence greedy K=50 no heading guard; enabler PCL BoundaryEstimation r=4mm; screening-only) + 66 (ordering-null ×3 stands) + 21 (RegionGrowing split precedent: SFS-T21 normal-sign split).

**Status:** ready-for-agent

**Starting position:** split each C Bl_0 at >5mm gaps into one-loop components, drop spurs/fold-backs, select the inner loop via Surface standoff probe (predicted: Bl_0 ≈ ORIG counts already in file as run sizes; jumps→0 with no reorder; fresh-vs-shipped med ~5.6→~1-2mm). Fresh-only scratch copies; bundle references pota67/pota66/pota39 C bundles (read-only). Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only. C02 axle still finder-side (orthogonal, per 66).

**Rules:** land ONLY with Bl_0 ≈ ORIG counts AND jumps→0 AND fresh-vs-shipped ~1-2mm AND E2E above 0 ×3 same-binary + controls green (C ORIG 4/4+5/5, A 8/8+15/15) in same runs; renders (eye-check); prep-side scratch copies; assembler E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition.

- [ ] Split-then-select arms, one variable each
- [ ] Gate + E2E rerun ×3 or measured why-not
- [ ] Job IDs + sacct states

**Successor:** forward-cone guard at the walk level (67's durable fix); roll wherever doubled loops recur.
