# 72: Upstream content — where does the true lip go?

**What to deliver:** on-contour points in the detection input — gate (+ E2E on landing).

**Answers:** E1

**Blocked by:** 71 (F-NORM NULL: C01 402→184, median worsens 5.61→14.91; ceilings C01 39% partial / C02 0% / C04 0% — no face holds a full on-contour loop; premise refuted at walk-input level; jobs 33284494/33284651/33285429/33285580 COMPLETED; 8/8 STABLE; no E2E per Rules) + 70 (radius picks count not placement) + 69 (offset upstream of walk).

**Status:** ready-for-agent

**Starting position:** for C02/C04, ZERO of our sampled points sit on the shipped contour — the true lip is lost before detection runs. Candidates: mesh sampling resolution at the lip, normal estimation flipping faces, the lip falling between sample rows. Fresh-only diagnosis; bundle references pota71/pota70/pota39 C bundles (read-only). ORIG evidence-only (44-asterisk rule). C03 green control must stay seated.

**Rules:** diagnosis with login-node screening first; E2E only when jumps→0 AND gate recovery AND ~1-2mm all hold; controls green (C ORIG 4/4+5/5, A 8/8+15/15) in same runs; renders (eye-check); no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition; no gate relaxation without a mechanism.

- [ ] Sampling/normal arms at the lip, one variable each
- [ ] Gate (+ E2E if bar met) or measured why-not
- [ ] Job IDs + sacct states (or explicit screening-only)
