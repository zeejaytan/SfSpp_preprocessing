# 69: Walk-level re-extraction — trace one loop, not two

**What to deliver:** regenerated C Bl_0 content sitting ~1-2mm off shipped — gate + E2E recovery.

**Answers:** E1

**Blocked by:** 68 (split-select NULL both arms: no in-file loop on shipped contour; in-file options exhausted; jobs 33279876/33279902/33279903 COMPLETED) + 67 (guilty stage getPointsInSequence greedy K=50 no heading guard; enabler PCL BoundaryEstimation r=4mm admitting both lip faces; repair direction: split-then-select before sequencing + forward-cone guard + inner-loop select) + 21 (RegionGrowing split precedent).

**Status:** ready-for-agent

**Starting position:** the true lip was never traced, so no re-sorting recovers it. Re-extract at the walk level: forward-cone guard in getPointsInSequence (heading/component guard), one-loop-per-component emission, BoundaryEstimation radius that admits one lip face. Fresh-only scratch prep copies; bundle references pota68/pota67/pota39 C bundles (read-only). Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only. C02 axle still finder-side (orthogonal). C03 is the green control (rotation-only piece — must stay seated).

**Rules:** land ONLY with fresh-vs-shipped ~1-2mm AND jumps→0 AND gate recovery toward ORIG per-edge AND E2E above 0 ×3 same-binary + controls green (C ORIG 4/4+5/5, A 8/8+15/15, C03 seated) in same runs; renders (eye-check); prep-side scratch copies; assembler E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition; no gate relaxation without a mechanism.

- [ ] Walk-level arms, one variable each
- [ ] Gate + E2E rerun ×3 or measured why-not
- [ ] Job IDs + sacct states

**Successor steer (from 68):** E/I/J — check GT-seated fresh-vs-shipped distance first; if ~5mm + doubled counts, skip to re-extraction.
