# Pipe exclusion: a boundary loop with surface inside it is a pipe, not an edge

GOAL: THE FINDER STOPS REPORTING PIPES AS FRACTURE EDGES.

**Answers:** E1

**Blocked by:** 166 (loop1 = 247e hole in MAIN sheet, flake hovering beside it; FAR rings it; user agrees it is a pipe -- surface goes down along it) + 155 (code sites).

**Status:** ready-for-agent

**User's rule (verbatim):** it is a hole in the sense of a pipe -- there is still surface going down along that hole. Exclude the pipe as edge.

I.e. a true fracture edge is a boundary with AIR beyond it; a pipe rim is a boundary with SURFACE beyond it (the pipe walls descending inside the loop). The test for each boundary loop: does the loop enclose further surface (pipe -- exclude from edge candidacy) or open onto air (true edge -- keep)? Operationalize on the sheet cloud (depth of points inside the loop footprint below the rim plane, interior-point count, or equivalent) -- worker's choice with justification.

**What to deliver:** (a) CONFIRM pipe geometry: depth profile inside loop1 (surface descending how far? pipe walls present?). (b) RULE: pipe-exclusion in the worktree variant (BoundaryEstimation output filtered, or sheet pre-masked); run both pots; 98-gate both. Bar: Pot A cure kept (pairs ~= 155) AND C01 false loop gone with rim kept (at-or-better-than fresh 5.61/22.9). (c) If the loop interior holds no surface (not a pipe), negative with the depth numbers.

**Starting position:** 166 Comments (loops, flake, distances, scripts); 155 Comments (worktree + build); 160/162 Comments (labels, gate scripts). New scratch pota167_repro/; renders artifacts/pota167/.

**Rules:** same-binary ORIG control alongside or void; worktree-local build only, restore byte-identical after; COMMIT NOTHING; tickets 39-166 read-only; Comments-only ticket edits; sacct recorded; eye-check renders.

- [ ] pipe depth profile inside loop1 (surface descending?)
- [ ] pipe-exclusion rule built + both pots run + gated
- [ ] Verdict + render paths
