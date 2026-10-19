# Adaptive veto: kill the false face, keep every pot's true rim

GOAL: A VETO RULE THAT ADAPTS TO EACH PIECE INSTEAD OF ONE FIXED ANGLE.

**Answers:** E1

**Blocked by:** 156 (fixed align<=0.5 eats C01 true rim: kept=223 dropped=141, gate 27.68/0) + 158 (no-veto 30.18/0: veto load-bearing, cannot just switch off) + 155 (veto code location, worktree, build).

**Status:** superseded-by-160

**What to deliver:** (a) ANALYSIS: align-value distributions of kept vs dropped dots on Pot A true rims vs C01 (from 155/156/158 logs + pcds) -- show where the two faces sit per piece and why one threshold cannot serve both. (b) RULE: a per-piece adaptive veto (e.g. threshold from the piece's own align distribution, bimodal split; or normal-aware: fracture-normal vs local wall geometry, not global radial). (c) PROOF: implement in relay worktree, build, run Pot A relay pair + Pot C P01, gate both the 98 way. Bar: Pot A keeps its cure (pair counts ~= 155: P02_0 ~97 etc., true rims kept) AND C01 true rim kept (gate at-or-better-than fresh 5.61/22.9, dropped set contains no ORIG-loop dots).

**Starting position:** 155/156/158 Comments (code sites, build commands, staged inputs, gate scripts); pota158_repro NOVETO env-gate pattern for variant builds. New scratch pota159_repro/; renders artifacts/pota159/.

**Rules:** same-binary ORIG control alongside or void; worktree-local build only, restore byte-identical after (158 pattern); COMMIT NOTHING; tickets 39-158 read-only; Comments-only ticket edits; sacct recorded; eye-check renders. If no adaptive rule separates both pieces, report the distributions as a negative (that is a landing result).

- [ ] align distributions A vs C01 (kept/dropped/ORIG-loop overlay)
- [ ] adaptive rule implemented + variant binary built
- [ ] Pot A pair re-run (cure kept) + C01 gate (rim kept)
- [ ] Verdict + render paths
