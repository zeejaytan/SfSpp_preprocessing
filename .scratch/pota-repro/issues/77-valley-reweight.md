# 77: Overlap-valley reweighting

**What to deliver:** 02-04 seated without the 17mm slide.

**Answers:** E1

**Blocked by:** 76 (landed WHY-NOT-MEASURED, 9 jobs COMPLETED: W1 halved inlier gate / W2 halved angle gate / R1 refinement ablated — all null, seat bit-identical 2.52deg/17.37mm; gate-tightening = wrong family, refinement exonerated; E2E holds 2/3+1/3 x9) + 74 (valley bound: fresh overlap 24.3% at GT vs 45.2% at search seat vs ORIG-at-GT 42.7%; pure single-axis slide; C01-independent).

**Status:** ready-for-agent

**Starting position:** reweight the beam score so the valley peak coincides with truth — one variable each: (a) volume-boost removal, (b) MatchingScore exponent, (c) max_overlap_area_ penalty, (d) symmetry-breaking of your own design. Search-side scratch copies; prep content (S24 swaps) taken as given from 73/74 bundles (read-only). Zero ORIG points in any fix; ORIG evidence-only.

**Rules:** land with 02-04 relative translation toward <=10mm at same rotation + E2E at or above 2/3+1/3 x3 same-binary + controls green (C ORIG 4/4+5/5, A 8/8+15/15) in same runs; renders (eye-check); E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats >=3 per condition; SingleOverlapTest@100/RP/CheckGraph-150 stay unless the valley mechanism names them.

- [ ] Reweighting arms, one variable each
- [ ] Gate + E2E rerun x3 or measured why-not
- [ ] Job IDs + sacct states
