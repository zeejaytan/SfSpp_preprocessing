# Re-anchor the trigger on the grown bag — direction with a live latch

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 125 (verbatim latch stale on grown-278: closest 6.05mm, never arms; trigger must be re-derived per bag; bounding voids named) + 116 (GUARD-116 recipe: heading + post-stall recovery) + 124 (grown-278 bag: 205, gate 4.31) + 112 (freeze method: K-net + ORIG-seating per stall)

**Status:** ready-for-agent

**What to deliver:** re-derive the recovery trigger FOR the grown bag instead of porting the stale anchor. Run GUARD-113-equivalent (heading, no recovery) on the grown-278 bag, freeze its strand (K-net + ORIG-seating, 112-style), and state a new ARM rule from the grown bag's own geometry (no absolute-coordinate anchors from the 270-bag; the rule must be bag-relative — e.g. strand-region proximity on the grown route, or coverage-stall signature). Then test the re-anchored guard. Success bar (all must hold): pushes >=205 AND walks through BOTH stall dots AND gate at/below 4.31mm AND zero jumps >=40mm AND leftover below 125's 80. If the re-anchored walk strands at the same far-arc dot with the same REFUSAL signature, report coverage delta vs 125 (progress = road extended; same-dot = the stall is void-bounded and the ticket names the bounding spans as the next detection targets).

**Starting position:** .scratch/pota124_repro/ (grown-278 bag), pota112/116/125_repro/ (freeze method, GUARD recipe, stale-latch evidence). Login-node numpy only — no Slurm, no E2E. New scratch pota126_repro/; render under laptop artifacts/pota126/ (grown-bag freeze, new anchor, path vs 125, latch-arm plot).

**Rules:** control reproduces 124-grown greedy first (99/278, 205, gate 4.31) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; anchor-derived-not-ported.

- [ ] Grown-bag freeze (strand seated, K-net, new anchor stated)
- [ ] Re-anchored guard walk (pushes, stalls, gate, leftovers)
- [ ] Verdict + recipe or void-bounded verdict with spans named
