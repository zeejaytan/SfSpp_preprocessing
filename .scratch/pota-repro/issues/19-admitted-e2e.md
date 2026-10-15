# 19: Pot A end-to-end assembly on admitted fragments

**What to build:** the proof the whole arc owes — our rims plus our axles reassembling Pot A through the untouched assembly program, with refusals excluded by rule and the authors' arm alongside.

**Answers:** E1

**Blocked by:** 18-refusal-gate (frozen finder + shipped refusal gate below).

**Status:** ready-for-agent

**Starting position:**
- Rims: fresh Pot A bundle with the SFS-T13 second-chance walk (ticket 13, committed) — gate 15/15 patched arm, 12/15 ablated arm (ticket 13 evidence). Rebuild the bundle from current sources; do not hand-assemble.
- Axles: frozen GM-refine (a)-finder (`.scratch/pota-repro/p15-stage/axle_finder/`, committed) in the shipped `Axes/Pot_A_Piece_0i_Axis.xyz` position-first format the reader parses (`data_structure.cpp:146-187`).
- Refusal gate (ticket 18, shipped): refuse a fragment when vote-best GM cost > 1.40/pt AND round-1 winner share < 0.22. Apply it mechanically; refused pieces are excluded by rule, not by hand — report which pieces (if any) it refuses on Pot A.
- Control: same-binary ORIG arm (authors' bundle + authors' axes) in the same assembly job, must reproduce 8/8 + 15/15 (as in tickets 06/11/13).
- Assembly: pristine program, k=5/b=3 (Table V Pot A). Spartan assembly tree + job recipes from tickets 06/11/13 leftovers.

**Rules:** no source changes to the finder or the pipeline in this ticket — this is a measurement run. If the bundle needs rebuilding, rebuild from committed sources only. One variable at a time if diagnosis is needed (rims vs axles vs search, in that order — the arc's evidence already separates them).

- [ ] Fresh arm: gate score + E2E placed/edges at k=5/b=3, per-piece placement errors (relative-rot scoring vs ORIG, 0.00° method from ticket 11/13)
- [ ] ORIG arm in the same job: 8/8 + 15/15 reproduced (else the run is void, not a failure)
- [ ] Refusal report: gate applied to all 8 Pot A pieces, admitted/refused list, and the E2E scored on admitted pieces with refusals named
- [ ] Laptop poll per sbatch (`sacct` directly); render one representative seating before/after + measurement pair; no commits; Comments-only edits

**Successor:** B–J E2E on admitted fragments (same protocol per pot), then the Juglet question re-opens with a working chain.
