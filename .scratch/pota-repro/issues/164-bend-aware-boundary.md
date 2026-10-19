# Bend-aware boundary: sharp turns are not edges

GOAL: THE EDGE-FINDER STOPS FIRING WHERE THE SHERD BENDS.

**Answers:** E1

**Blocked by:** 163 (substrate = PCL BoundaryEstimation on cleanSamples sheets; C01 false loop = sheet edge past the loop) + user diagnosis 2026-10-19 + 155 (code sites).

**Status:** ready-for-agent

**User's diagnosis (verbatim):** the only reason BoundaryEstimation marks that as edge is the mesh takes a sharp turn at that junction; the code assumes a sherd is relatively flat without much bend, but this piece has bend. Fix: BoundaryEstimation must not mark anything that has points in 360-degree space -- only mark the true edge.

I.e. the angular-gap test confuses a sharp bend (neighbours present all round in 3D but folded, piling into half the tangent plane because the normal estimate tilts) with a true sheet end (neighbours genuinely missing on one side). The corrected rule fires only when points are truly absent through a 360-degree check that survives bending -- e.g. gap test in 3D rather than the tilted tangent plane, normal-consistency of neighbours, or a bend-compensated threshold.

**What to deliver:** (a) CONFIRM: measure bend (dihedral/curvature/normal-spread) at the C01 false-loop sites vs true-rim sites vs Pot A sites -- is the false loop at a sharp turn? (b) FIX: bend-aware boundary rule in the worktree variant; run both pots; 98-gate both. Bar: Pot A cure kept AND C01 false loop gone with rim kept (at-or-better-than fresh 5.61/22.9). (c) If bend does not own the false loop, negative with the measurements.

**Starting position:** 163 Comments (substrate, code sites, staged inputs); 155 Comments (worktree + build); 160/162 Comments (labels, gate scripts). New scratch pota164_repro/; renders artifacts/pota164/.

**Rules:** same-binary ORIG control alongside or void; worktree-local build only, restore byte-identical after; COMMIT NOTHING; tickets 39-163 read-only; Comments-only ticket edits; sacct recorded; eye-check renders.

- [ ] bend measurements false vs true vs Pot A
- [ ] bend-aware rule built + both pots run + gated
- [ ] Verdict + render paths
