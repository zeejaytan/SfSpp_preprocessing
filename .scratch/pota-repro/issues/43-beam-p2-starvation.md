# 43: Beam p2-starvation (Pot B) — why fitting candidates never seat

**What to deliver:** p2 seated, or the beam mechanism that stops it, named with numbers.

**Answers:** E1

**Blocked by:** 42-potb-rim-fix (rims fit; blocker is beam-side).

**Status:** ready-for-agent

**Starting position:** B gate 15/15 on real pipe output (SFS-T42, job 33217089); GT-seated p2×p4 overlap ≈ ORIG; p2 candidates 0→93 yet p2 enters the beam last (others 323–795; ORIG p2 has 731); E2E stuck 4/9+2/15 ×2 across 3 different p2 rims (33217561/62). Structural gap: fresh p2 profiles run 9–15 rows vs ORIG 18–34 (~1-in-5 rows out-of-bin breaks every run; smoothing no gain). Controls: B ORIG 9/9+15/15, A both arms 8/8+15/15 — any experiment must keep them green in the same runs.

**Rules:** assembler-lane work happens in scratch copies of the cure vehicle ONLY (cure-potA @ bffefb6; fork main untouched); one variable per arm; beam-width/order changes need ORIG-validity in the same run (a faster wrong answer is failure, not progress); seating render of any claimed improvement (eye-check); no commits; sacct-direct polling; Comments-only ticket edits.

- [ ] Why p2 enters last: scoring decomposition (inlier-sum vs candidate count vs profile length)
- [ ] Width/order/profile-length arms, one variable at a time
- [ ] B fresh improvement + B ORIG 9/9+15/15 + A 8/8+15/15 in the same runs
- [ ] Job IDs + sacct states

**Successor:** cross-pot generalization of whatever seats B (D–J share the drowning shape).
