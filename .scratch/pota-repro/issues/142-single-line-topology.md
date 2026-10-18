# Single-line topology — stop the zigzag, not just cover the points

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 140 (eye verdict: author's single clean loop vs our zigzag that crisscrosses inner/outer wall; coverage 210/211 does NOT imply topology) + 105 (face-hop named: trace hops inner-outer) + 134 (M134d walk) + 138 (segment-credit: banks crossings, never penalizes them)

**Status:** ready-for-agent

**What to deliver:** a topology metric + a face-coherent walk. Problem: the gate measures point/segment DISTANCE to the author loop — a walk that zigzags across the wall still scores 4.25 because every zig stays near the loop. Nothing penalizes (a) consecutive-dot face alternation (inner-wall dot -> outer-wall dot -> inner), (b) self-intersections of the walk (chords crossing chords). Measure first on M134d: face-flip count (classify each sequenced dot inner/outer by mesh side, count alternations), self-intersection count of walk segments. State both numbers as the topology baseline. Then test a face-coherent ordering: penalize/refuse steps that alternate mesh side vs the running face (stated rule first, ORIG-free), walk + re-measure (coverage gate must not regress past 4.3107, topology counts must fall). Success bar: face-flips and self-intersections down by majority AND gate at/below 4.3107 AND uncovered at/below 8 (segment-credit). If face classification itself is incoherent (dots unclassifiable), refute with the distribution — owner is dot-level (snap-drag leftovers), not walk-level.

**Starting position:** .scratch/pota134_repro/ (M134d sequence, 282 bag), pota140_repro/ (mesh frame), pota104_repro/ (snap-drag evidence). Login-node numpy only — no Slurm, no E2E. New scratch pota142_repro/; renders under laptop artifacts/pota142/ (face-coloured walk: inner vs outer, flip points marked; before/after).

**Rules:** control reproduces 134's marks first or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; topology numbers first, fix second.

- [ ] M134d topology baseline (flips, self-intersections)
- [ ] Face-coherence rule stated + tested walk
- [ ] Coverage vs topology vs bar
- [ ] Verdict + recipe or dot-level refutation
