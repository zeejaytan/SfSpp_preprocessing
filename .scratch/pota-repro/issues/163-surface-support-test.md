# Surface-support test: true edge has surface on one side only, false edge sits amid surface

GOAL: TEST EACH DOT AGAINST ITS SOURCE SURFACE, NOT AGAINST OTHER DOTS.

**Answers:** E1

**Blocked by:** 162 (dot-vs-dot emptiness fails backwards -- wrong substrate) + user correction 2026-10-19 + 155 (extraction code sites).

**Status:** ready-for-agent

**User's correction (verbatim):** the dot comes from a surface; that surface's true edge one side is empty, but the false edge has point cloud or vertices on all sides. So put it back to the surface to test -- not whether a DOT is next to another DOT. (Open: how the surface is represented in the code -- mesh, point cloud, grid -- the worker establishes this first.)

**What to deliver:** (a) SUBSTRATE: identify the surface representation feeding the veto-site dots (mesh triangles? point cloud? from which stage output -- mesh-stage Surface xyz / Point PCD / Dataset). (b) SCORE: for the 364 C01 veto-site dots + Pot A rim dots, a support-asymmetry score measured on the SURFACE (e.g. surface present in a half-ball on one side only vs all around; boundary-distance of the dot's source location). Labels via ORIG overlay as in 160/162. One cutoff separating rim from face on BOTH pots? (c) RULE (if it separates): support-gated veto in the worktree variant, both pots run + 98-gated. Bar: Pot A cure kept AND C01 rim kept (at-or-better-than fresh 5.61/22.9). (d) If it straddles, negative with plots.

**Starting position:** 155 Comments (extraction code + stages); 160/162 Comments (veto-site dots, ORIG labels, gate scripts); staged worktree. New scratch pota163_repro/; renders artifacts/pota163/.

**Rules:** same-binary ORIG control alongside or void; worktree-local build only, restore byte-identical after; COMMIT NOTHING; tickets 39-162 read-only; Comments-only ticket edits; sacct recorded; eye-check renders.

- [ ] substrate identified (representation + stage + paths)
- [ ] support-asymmetry scores A + C01 (rim vs face vs ORIG)
- [ ] (if separates) support-gated veto built + both pots run + gated
- [ ] Verdict + render paths
