# 21: Recover the piece-2 exterior-wall surface

**What to build:** the actual fix — find where p2's wall collapses in the surface stage and recover it, closing Pot A at strict 8/8 + 15/15.

**Answers:** E1

**Blocked by:** 20-piece2-endgame (diagnosis below).

**Status:** ready-for-agent

**Starting position (ticket 20, jobs 33114754/33114755/33115534, ORIG controls valid):** the input meshes are byte-identical (md5 985e4eb1, 55,814 verts both sides), yet our p2 S1 surface is a 171-point scrap matching neither ORIG wall (median 2.8–3.4mm off, <1% coverage) while our p2 S0 is a full wall sitting on ORIG's S1 slot (labels swapped). Our Bl0 walk runs ~3mm off both true rims; our Bl1 is an 18-point stub covering 9.5% of the true path. The search is exonerated (ORIG p2 rim seats 4/4 strict in our bundle). Forest inflates 584 vs ORIG 124 — use it as the cheap signal.

Existing leads (do not re-derive, verify and pin): the size-rank surface assignment (`mesh_processing_headless.cpp:1755-1769`, ticket 02) and the +Z shift entering at the surface stage (ticket 01 gap G5). The fault is downstream of the mesh and upstream of the rim walk — pin the exact file:line where p2's exterior wall is dropped or mislabelled, fix minimally, one variable at a time.

**Measurement rule (ticket 20 finding):** the binary 15/15 bar is loose — it reports perfect with p2 ~10°/40mm off. Acceptance here is the STRICT bar only (5°/10mm relative-edge via `p19_score.py` rule): strict 15/15 on the fresh bundle, ORIG control 8/8+15/15 in the same job or void.

- [ ] Pin the extraction-stage file:line (surface assignment/labelling for p2's exterior wall), fix, rebuild from committed sources, same-binary ORIG control
- [ ] Fixed arm: gate + E2E k=5/b=3, strict 15/15; forest count back toward ~124 as corroboration
- [ ] Laptop poll per sbatch (`sacct` directly); before/after seating render + measurement pair; no commits; Comments-only edits

**Successor:** B–J E2E on admitted fragments (same protocol per pot), then the Juglet question re-opens with a working chain.
