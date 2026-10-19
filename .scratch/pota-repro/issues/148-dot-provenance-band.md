# Dot provenance — what IS a dot, and why does our edgeline form a thick band?

GOAL: NAME THE BAND.

**Answers:** E1

**Blocked by:** 147 (parity walk clean at author spacing; uncovered 15 = void; same inner wall, radial med -0.29mm) + 67/face-hop finding 2026-10-17 (walk hopping faces leaves a wall-thickness fingerprint) + user observation 2026-10-19 (our edgeline looks UNIFORMLY EXTENDED OUTSIDE author's; if dots were a true edge they should form a thin line, not our thick band — the band width itself may cause the zigzag)

**Status:** ready-for-agent

**What to deliver:** an audit of what our dots are, per pipeline stage. For the 314 bag (and the 453 cum where useful): tag every dot by the stage that emitted it (boundary-test admission incl. span-localized admits, ROR survivor, snap add, densify interpolation) and measure the band's cross-edge width at matched ORIG stations (signed inside/outside spread, median + tails) against the mesh wall thickness at those stations. Answer in this order: (1) is the band's width ~= the wall-face width (dots ARE surface/face samples misfiled as edge) or << wall thickness (a true edge with noisy localization)? (2) which stage emits the out-of-line dots — one stage or all of them? (3) reconcile with 147's radial med -0.29mm: does the band STRADDLE the author line (center right, width wrong) or sit truly outside it (center wrong too)? Bar: a per-stage width table + the straddle-vs-outside verdict with separation numbers + the named next fix (which stage to change, what change, predicted width after). A verdict of thin-line-true-edge-with-noise must explain the 48mm void spans; a verdict of face-samples must name the stage that lets face dots into the bag.

**Starting position:** .scratch/pota147_repro/ (on-arc tags, station frame), pota143_repro/ (bag lineage per stage), ticket 67 + face-hop memory (wall-thickness fingerprint). Login-node numpy only — no Slurm, no E2E. New scratch pota148_repro/; renders under laptop artifacts/pota148/ (cross-section views at 3+ stations showing author line, our band, wall faces; per-stage width plot).

**Rules:** ORIG Bl_0 ruler-only (stations + author line position); control reproduces 147's HALF-1 numbers first or stop; COMMIT NOTHING; Comments-only ticket edits.

- [ ] Per-stage dot tags + cross-edge width vs wall thickness
- [ ] Straddle-vs-outside verdict reconciled with 147 radial numbers
- [ ] Named next fix (stage + change + predicted width)
