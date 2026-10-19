# Stop emitting the false face at extraction (sub-copy admission fix)

GOAL: NO FALSE FACE IN THE FIRST PLACE -- THE VETO HAS NOTHING TO TRIAGE.

**Answers:** E1

**Blocked by:** 150 (admission = edgeline_extraction_headless.cpp:949 angle gate + :1032 dead reload-over; TAP closable at cloud level; select-FIRST-then-walk named, patch not applied) + 155 (sub-copy :920 entry, live Ticket-05 filter keeps outer, veto+sequencer diffs staged) + 156/158 (downstream veto can only triage; fixed rule misfires, off is worse).

**Status:** ready-for-agent

**What to deliver:** (a) ANALYSIS: on Pot A + Pot C P01 clouds, where the outer-face dots enter (angle gate? reload-over? Ticket-05 filter?) with per-site counts. (b) FIX: an admission-side change in the SUB-COPY (original_nurbs_preprocessing/) that rejects the outer face BEFORE the walk -- e.g. face-side select at cloud level per 150, or TAP closure -- such that Pot A keeps its 155 cure pair counts (P02_0 ~97 etc.) AND C01's output contains no outer-face loop (gate at-or-better-than fresh 5.61/22.9 with the false loop gone). (c) PROOF: worktree build + both pots run + 98-gate both + renders.

**Starting position:** 150/153/155 Comments (code sites :920/:949/:1032, Ticket-05 filter, TAP, worktree + build commands, staged inputs, gate scripts); pota158_repro variant-build pattern. New scratch pota160_repro/; renders artifacts/pota160/.

**Rules:** same-binary ORIG control alongside or void; worktree-local build only, restore byte-identical after; COMMIT NOTHING; tickets 39-158 read-only (159 superseded, do not build on it); Comments-only ticket edits; sacct recorded; eye-check renders. A clean negative (admission sites inseparable -> veto is the only lever) is a landing result.

- [ ] per-site admission counts A + C01 (gate / reload-over / filter)
- [ ] admission-side fix implemented + variant binary built
- [ ] Pot A pair (cure kept) + C01 gate (false loop gone, rim kept)
- [ ] Verdict + render paths
