# 20: Piece-2 endgame

**What to build:** the last blocker — find why piece 2 cannot seat and fix it, closing Pot A at 8/8 + 15/15.

**Answers:** E1

**Blocked by:** 19-admitted-e2e (measurements below).

**Status:** ready-for-agent

**Starting position (ticket 19, job 33113298, ORIG control valid 8/8+15/15):** everything seats except p2. Fresh-ablated arm: 7/8 + 11/15, p2 ~103°/232mm off, all other pieces within 1.3°/6.3mm of ORIG seatings. Patched arm: 7/8 + 7/15 with p2 unseated — the SFS-T13 second-chance rim poisons the search (3rd confirmation), so the fix is NOT more rim points. Per-piece rims seat cleanly (render `artifacts/pota19/pota19_orig_vs_fresh_seating.png`, lead eye-checked: closed ring both arms, p2 flung). The axle gate admits p2 (fresh 8/8 admitted) — rim shortness is invisible to it, noted as a gate-design observation, not this ticket's fix.

Suspects in order:
1. **p2 exterior wall at the mesh stage** — compare fresh vs ORIG p2 surfaces and rims point by point (the 171-pt scrap vs 11k wall from ticket 04 is the designed exception; check whether the mesh-stage exterior wall for p2 differs from ORIG beyond the rim walk). Swap experiment: ORIG p2 rim + fresh rest — if p2 seats, the fault is in our p2 rim/surface, not the search.
2. **The beam's 103°-off p2 preference** — if the swap still fails, the search prefers a false seating; probe why (p2's 4 gate pairs: which pass, which fail, and what the beam scores the true vs false seating).

**Rules:** no finder or pipeline source changes except the proven-minimal fix for the diagnosed cause (one variable at a time; SFS-T13 stays as-is — its search poison is measured, not debated). Rebuild bundles from committed sources only; same-binary ORIG control in the same job (must reproduce 8/8+15/15 or void).

- [ ] Swap experiment first (ORIG p2 rim into fresh bundle): seats → suspect 1 confirmed, fix our p2 surface/rim; still fails → suspect 2, probe beam scoring
- [ ] Fixed arm: gate + E2E at k=5/b=3, target full 8/8 + 15/15 fresh
- [ ] Laptop poll per sbatch (`sacct` directly); before/after seating render + measurement pair; no commits; Comments-only edits

**Successor:** B–J E2E on admitted fragments (same protocol per pot), then the Juglet question re-opens with a working chain.
