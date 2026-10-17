# 71: Face selection — keep the inner loop, not the outer

**What to deliver:** surviving loop on the inner lip face ≈ shipped contour — gate (+ E2E on landing).

**Answers:** E1

**Blocked by:** 70 (M4 collapses 4 runs→1 loop, survivor still ~3.8mm off; M8/CLAMP5/NOIMPROVE null; radius selects loop COUNT not PLACEMENT; unclustered snap exonerated; jobs 33283715/33283716/33283920 COMPLETED; 40/40 STABLE; no E2E per Rules) + 67 (two parallel lip loops ~5mm apart; inner via Surface standoff probe) + 68 (S-INNER radius-inner pointed at run2).

**Status:** ready-for-agent

**Starting position:** the detector sees both lip faces; radius picks how many loops survive, not which. Steer survival to the inner face: face-aware selection (normal orientation / Surface standoff side / detection-input density per face). Fresh-only scratch prep copies; bundle references pota70/pota39 C bundles (read-only). C03 green control must stay seated. Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only.

**Rules:** diagnosis with login-node screening first; E2E only when jumps→0 AND gate recovery AND ~1-2mm all hold; controls green (C ORIG 4/4+5/5, A 8/8+15/15) in same runs; renders (eye-check); no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition; no gate relaxation without a mechanism.

- [ ] Face-selection arms, one variable each
- [ ] Gate (+ E2E if bar met) or measured why-not
- [ ] Job IDs + sacct states (or explicit screening-only)
