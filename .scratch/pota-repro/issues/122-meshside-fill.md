# Mesh-side fill — grow the rim's dots where the filter cannot tell them apart

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 121 (filter level exhausted: arc fully inside junk on every measured feature; 5 unique arc seats banked: 26/31/33/50/94) + 120 (ROR-6 load-bearing) + 119 (7 void spans with mesh context) + 111 (lip mesh edges 1.70 vs 1.51 — slight coarseness signal) + 104 (snap refines boundary dots onto full-res verts)

**Status:** ready-for-agent

**What to deliver:** the dots must be GROWN at the mesh, not filtered. For each of 119's void spans (and 121's 5 banked seats as ground truth of where dots SHOULD be), read the mesh-side context: local face sizes vs the 1.70/1.51 numbers, segmentation labels at the span, boundary-test response values there, scan coverage (mesh present and fine, or coarse/holey?). Then state ONE mesh-side ORIG-free rule before running — e.g. subdivide coarse lip faces inside void spans and re-run boundary+snap there, or re-run the boundary test at finer radius/decimation confined to void-span neighbourhoods — and test it: void-span coverage, junk accounting, walk + gate (plain greedy K34+T13, pre-registered, same both arms). The rule must be implementable from mesh data alone (no ORIG positions as inputs; ORIG Bl_0 gate-evidence only). Success bar: uncovered ORIG count below 119's 32 AND admitted junk ~0 AND gate at/below 4.68mm AND walk >=197 pushes. If the mesh at void spans is already fine and fully covered by the boundary test's blindness (response values flat there), refute with those numbers — that says the boundary test itself is blind at these spans and names its radius/threshold as the next variable.

**Starting position:** pota103/111/119/120/121_repro/ (cleaned bag, void spans, 5 banked seats, mesh numbers), C01 fragment mesh + segmentation outputs, boundary test code (mesh_processing_headless.cpp:1580-1709). Login-node numpy only — no Slurm, no E2E. New scratch pota122_repro/; render under laptop artifacts/pota122/ (void spans: mesh fineness + boundary response + grown dots, walk vs control).

**Rules:** control reproduces 103-cleaned bag first (270, gate 4.68) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; context-read-then-rule-stated.

- [ ] Mesh context read per void span (fineness, labels, boundary response, coverage)
- [ ] Mesh-side rule stated, grown bag (coverage, junk accounting)
- [ ] Walk + gate vs full bar
- [ ] Verdict + recipe or blindness refutation with next variable named
