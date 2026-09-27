# 11: The ~1.2 mm outward bias in our rims — the actual cause

**Answers:** E1

**Blocked by:** nothing. This is the front of the queue.

**Status:** ready-for-agent

**Needs-eye:** required before this ticket closes. It is a geometry claim
about where our rim sits, and the conservator's eye is what settles whether
"1.2 mm outward" is the right description of it.

## The finding

Our rims sit **about 1.2 mm further from their own centroid than the
authors'**, on six of eight sherds, with the same sign every time:

| piece | our length / authors' | our mean radius | authors' | **radius difference** |
|---|---|---|---|---|
| 1 | 0.981 | 54.05 | 54.29 | **−0.23** (fine) |
| 2 | **0.456** | 17.46 | 43.02 | **−25.57** (truncated) |
| 3 | 1.015 | 41.07 | 39.91 | **+1.16** |
| 4 | 1.001 | 38.55 | 37.35 | **+1.20** |
| 5 | 1.047 | 38.74 | 37.53 | **+1.21** |
| 6 | 1.024 | 37.34 | 36.22 | **+1.11** |
| 7 | 1.059 | 16.55 | 15.76 | **+0.80** |
| 8 | 1.093 | 15.92 | 14.79 | **+1.13** |

Median **+1.12 mm**, and it is measured as a distance from the *rim's own
centroid*, so both rims on the same wall share that frame. **The wall swap
cannot disguise this number**, which is what makes it trustworthy where the
per-sherd offset comparison was not.

## Why 1.2 mm per sherd costs 8 of 15 joins

At a joint, the two sherds' rims approach from opposite sides, so their
outward biases **add rather than cancel**: 1.2 + 1.2 ≈ 2.4 mm, which straddles
the 2 mm gate. Measured, and it matches:

| pair | our gap | authors' gap |
|---|---|---|
| 1-3 | 4.22 mm | **0.58 mm** |
| 1-5 | 4.79 mm | **0.27 mm** |
| 1-6 | 3.76 mm | **0.86 mm** |
| 3-4 (via 2-4) | 8.81 mm | **0.97 mm** |

The authors' rims are **0.09–1.30 mm apart on all fifteen pairs**. Ours are
3.7–22.9 mm on the eight that fail. We are 4–9× further apart, and a 1.2 mm
per-sherd bias, doubled at every joint, accounts for it.

## This is a correction, and the error is worth recording

I previously concluded that **six of the eight failures were "piece 1's
geometry, not ours."** That was wrong, and the way it was wrong is
instructive.

I had measured our curve against the authors' and found piece 1 matching
(0.69 mm) while pieces 3–8 sat 3.5 mm off. I then ran the wall swap, which
drove every offset to 0.5–0.8 mm — and the gate went **7/15 → 6/15**. I read
that as "the offset is not the cause."

What I had actually shown was **"that particular intervention did not address
the cause."** The swap changed *which wall* the rim came from; it did not
change the *outward bias on each wall*. Those are different quantities, and
the offsets-vs-reference metric is blind to the difference because the
reference sits on the other wall.

The tell I ignored: I never ran the per-pair analysis on the **authors'
bundle**. The moment I did, piece 1 passed all six of its pairs at 0.27–0.92 mm
with normals agreeing at 0.98–1.00, which is flatly incompatible with "piece
1's rim faces outward." The control arm that would have refuted my own
conclusion was one command away, and I built the conclusion without it.

**The rule this earns: when a conclusion says "X is not the cause", run the
measurement on the reference data too. The reference is the control, and
skipping it is how a plausible inference survives a direct test.**

## Where the bias can come from — candidates, in order of likelihood

1. **The boundary-detection parameters.** `setRadiusSearch(4)` with
   `setAngleThreshold(M_PI * 0.6)` = 108°, flagged in E1 as "very permissive".
   A ~1.2 mm bias is the right order for a radius-search effect.
   *Test:* re-extract at radius 1, 2, 3, 4 mm and see whether the bias tracks
   the radius. **If it does, this is the fix and it is a one-line change.**
2. **Pre-detection smoothing or resampling.** If the surface is smoothed
   inward before the boundary is taken, the rim follows it.
   *Test:* measure our rim against a smoothed version of the raw mesh.
3. **The surface's own construction.** *Test:* the radius against the mesh
   rather than against the authors' rim.

**Test 1 first.** It is a parameter sweep on the cluster, it is cheap, and it
either identifies the fix or removes the leading candidate. Do not do the
surface-selection work in ticket 04 first — it is measured to be a different
effect, and it would confound the sweep.

## Acceptance criteria

- [ ] The 1.2 mm bias is attributed to one named cause, with the
      discriminating measurement quoted
- [ ] At least one candidate is **eliminated** by a test that could have gone
      the other way, not merely supported
- [ ] After the change, the radius difference against the authors is reported
      per sherd, and the **pairwise** distances are reported too — the
      per-sherd figure did not predict the gate and must not be trusted alone
- [ ] The Pot_A gate score is re-measured per pair, from 7/15
- [ ] The Juglet is re-measured against its honest denominator of 10
- [ ] A witnessed look of one rim against the authors' on the same sherd, so
      the conservator can judge the residual bias directly
- [ ] **The reference bundle is included in every comparison arm.** That is the
      check whose absence produced the error this ticket corrects

## Note

Ticket 10 recorded the 3.5 mm offset as "explained but not the cause". That
was half right: the offset is a symptom of the bias, not an independent
defect, and it should be closed against this ticket rather than left as a
separate finding.
