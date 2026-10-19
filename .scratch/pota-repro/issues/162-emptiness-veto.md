# Emptiness test: a true-edge dot has empty space beside it, a false-face dot does not

GOAL: A VETO FEATURE THAT SEES POSITION, NOT ANGLE.

**Answers:** E1

**Blocked by:** 160 (angle features exhausted: align modes straddle true/false on C01) + 158 (veto load-bearing) + user insight 2026-10-19.

**Status:** ready-for-agent

**User's idea (verbatim):** test the edge -- on the edge there would be no dot for miles. I.e. for each veto-candidate dot, examine its local neighbourhood: a dot on the true rim has empty half-space beside it (air beyond the edge), while a dot on the false face sits amid mesh/dots all around. Asymmetry of neighbours (e.g. fraction of an annulus/ball occupied, or largest empty angular sector) should separate rim from face where the normal-angle rule cannot.

**What to deliver:** (a) ANALYSIS: compute a neighbourhood-emptiness score for the 364 C01 veto-site dots + Pot A rim dots; overlay vs ORIG loops -- do true-rim dots score empty and false-face dots score surrounded on BOTH pots with one cutoff? (b) RULE (if it separates): emptiness-gated veto in the worktree variant, both pots run + 98-gated. Bar: Pot A cure kept (P02_0 ~97 etc.) AND C01 rim kept (gate at-or-better-than fresh 5.61/22.9). (c) If emptiness also straddles, report as negative with the plots.

**Starting position:** 155/156/158/160 Comments (code sites, worktree + build, staged inputs, gate scripts); 160 scratch (C01_BASE/C01_VAR, veto-site dots). New scratch pota162_repro/; renders artifacts/pota162/.

**Rules:** same-binary ORIG control alongside or void; worktree-local build only, restore byte-identical after; COMMIT NOTHING; tickets 39-161 read-only; Comments-only ticket edits; sacct recorded; eye-check renders.

- [ ] emptiness scores A + C01 (rim vs face overlay vs ORIG)
- [ ] (if separates) emptiness-gated veto built + both pots run + gated
- [ ] Verdict + render paths
