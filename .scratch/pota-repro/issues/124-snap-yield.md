# Snap yield — place the dots the test found but the snap dropped

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 123 (r1 finds 93 candidates, SURF-C1 keeps 2, 1 admitted; ~17 on-arc dots fail caps narrowly: disp 2.06-3.76 / dmid 5-6.3; next = snap placement or disp-cap calibration) + 122c (normal-gating note) + 104 (K=1 snap flaw) + 103 (cleaned bag, gate 4.68)

**Status:** ready-for-agent

**What to deliver:** turn 123's single-dot gain into yield. The r1 re-run FINDS on-arc dots that SURF-C1's caps then drop for centimetres of snap drift. Test improved snap placement: candidates (state which before running, one variable) — (i) K>1 vote (snap to medoid/mean of K nearest surface verts instead of K=1), (ii) normal-gated snap (candidate verts whose normals disagree with the coarse dot's normal refused), (iii) calibrated disp-cap (raise 2.0mm only as far as the on-arc/junk separation allows, measured first). Bar (all must hold): admitted dots more than 123's 1 AND admitted junk ~0 (majority within 5mm of ORIG) AND gate at/below 4.60mm (123's mark to beat, else 4.68 hard floor) AND walk >=198 pushes. If better placement only moves drift centimetres (admission stays ~1), refute with the drift-vs-K numbers — that says the coarse dots themselves sit off-surface and the fix belongs at detection, not placement.

**Starting position:** .scratch/pota123_repro/ (ladder, 93 r1 candidates, SURF-C1 code, admitted dot, control numbers), C01 fragment mesh + normals. Login-node numpy only — no Slurm, no E2E. New scratch pota124_repro/; render under laptop artifacts/pota124/ (snap drift before/after per candidate, admitted dots on ORIG arc, walk vs 123-grown).

**Rules:** control reproduces 123-grown bag first (271, gate 4.60, walk 198) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; placement-variable-stated-first.

- [ ] 123-grown reproduced + candidate stated
- [ ] Placement arm (drift numbers, admission accounting, junk count)
- [ ] Walk + gate vs 123's marks
- [ ] Verdict + recipe or detection-side refutation
