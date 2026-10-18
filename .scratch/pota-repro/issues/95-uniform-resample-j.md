# Uniform 1.8mm closed-loop resample (Pot J SXC bundle) — test R-RESAMPLE as a fix

GOAL: MATCH AUTHOR'S INPUT.

**What to deliver:** Take the LANDED pota92 SXC bundle (ticket 92: 7/10+13/18 x3) and resample every new-Bl_0 to the author regime — uniform 1.8mm closed loops (ticket 89 R-RESAMPLE) — then re-gate + E2E x3. Pass bar: seating stays at/above 92's landed 7/10+13/18 with controls green (this tests the resample moves toward author without breaking seating, not a fresh cure).

**Answers:** E1

**Blocked by:** 89 (R-RESAMPLE CONFIRMED with prediction-check; regime = closed 1.8mm resample) + 92 (J LANDS: bundle/manifests/gate/renders at pota92_repro/ for direct reuse) + 84 (E2E recipe) + 63 (J bar/ORIG)

**Status:** results-in (worker 2026-10-19 — HOLDS 7/10+13/18 x3 exact; renders eye-checked; sacct-verified)

**Starting position:** Reuse /data/gpfs/projects/punim2657/pota92/prep/pota92_bundle_J_SXC/ directly — resample ONLY the Bl_0 loops in place (same loops, same faces; arc-length uniform 1.8mm, closed; Axes/Mesh/Surfaces/GT untouched; byte-proof each new-Bl_0 == resample output). New scratch only if the bundle must be copied: pota95_repro/.

**Rules:** one variable (resample only — no slot changes, no densify beyond what 1.8mm gives; if any loop drops to n <= 50, STOP and report per densify rule); re-gate all 8 exchanged (median <2mm, jumps called out); E2E x3 same-binary on cure-potA @ bffefb6, k=5/b=3, with LINK-SHIM-OK + DRIVER-SHIM-OK asserts per job; J ORIG + A controls in the same runs; sacct-direct polling (never scripts/slurm_poll.sh); COMMIT NOTHING; Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); repeats >=3. Min new-Bl_0 n > 50 else STOP (densify is a separate ticket).

- [ ] Uniform 1.8mm closed resample of 8 exchanged Bl_0 (byte-proof)
- [ ] Re-gate 8/8 + controls
- [ ] E2E x3 vs 92's 7+13 (regression-or-better) + controls green
- [ ] Job IDs + sacct states

## Comments (worker, 2026-10-19 — COMMIT NOTHING)

**Verdict: HOLDS. Uniform-1.8mm closed resample of the 8 SXC Bl_0 keeps E2E at exactly 92's landed 7/10+13/18 x3 (regression-or-better: equal), controls green, asserts green, renders eye-checked. R-RESAMPLE moves the rims toward the author regime (89 P3/P6: closure<=2mm, L=nx1.8 within 5pct, uniform spacing, jumps subdivided onto chords) without breaking seating.**

**0. Preflight (login node; zero ORIG points).** Bundle md5s matched 92's landed pota92_J_SXC_BL_md5.txt exactly (no drift since landing); asm @ bffefb6a983403acbd5a96ac46952f4fa0a814e tree-clean (P22FIX/P22FIX2/C2-0.436 verified in-job); pre-resample md5 snapshot saved to pota95_repro/pota95_J_BL_pre_md5.txt.

**1. Resample (one variable; in place, Bl_0 of J02,J04-J07,J10-J12 only).** pota95_repro/p95_resample.py: closed periodic arc-length walk from original index 0 (arbitrary start = author-consistent), n_new=round(P/1.8), piecewise-linear interp of all 7 PCD channels with normals renormalized; segment table kept (same nseg/flags/info=0, ranges proportionally rescaled to cover 1..n_new — inert under info=0 since BuildTree inserts all points, verified in data_structure.cpp:118-133); header rewritten with updated WIDTH/POINTS only. Before->after n: J02 125->139, J04 171->181, J05 136->144, J06 123->130, J07 106->113, J10 69->72, J11 53->54, J12 53->55 (min 54 > 50 — no STOP). Author-regime checks on outputs: closure 1.65-1.81mm (<=2 P3), L/(n*1.8) 0.970-0.989 (within 5pct P6), max gap ~=1.8 uniform (old jump chords J02-14.6/J07-6.0 subdivided onto the same chord — geometry preserved). Byte-proofs: pre/post md5 diff shows EXACTLY the 8 Bl_0 changed (e.g. J02 08b62272->7536e17d, J12 37f3e11c->9e043c67); other 16 Bl files byte-identical; loader header math (nseg+12) + zero duplicate-point checks pass; post manifest pota95_repro/pota95_J_RES_BL_md5.txt (in-job guard target).

**2. Gate (RES Bl_0 @GT vs ORIG Bl_0, same evidence-only method as 92).** 11/11 gateable medians <2mm (J09 no GT, untouched): J02 0.76/99.3, J04 0.72/100, J05 0.68/100, J06 0.65/100, J07 0.39/100, J10 0.36/100, J11 0.41/100, J12 0.43/100; controls identical to 92 (J01 1.15/69.7, J03 0.89/75.7, J08 0.59/98.5). No jumps>5 remain (subdivided). Render eye-checked: artifacts/pota95/Jsel_RES_vs_ORIG.png (11 panels; red RES tracks gray ORIG ring; J01-curl + J03-droop pre-existing controls visible as in 92).

**3. E2E (cure-potA @ bffefb6 asserted in-job, k=5/b=3 shim, POT overlays, STEPS 12/8; stage = run_pota95_stage_AJ.sbatch = 92's sbatch with only RUNDIR/fetch/MD5-path renames, diff-verified; sacct-direct throughout):**

| job (sacct COMPLETED 0:0, worker-verified) | A_orig | A_fresh | J_orig | J_RES |
|---|---|---|---|---|
| 33388692 (0:19) | 8/8+15/15 | 8/8+15/15 | 8/11+16/21 | 7/10+13/18 |
| 33388693 (0:25) | 8/8+15/15 | 8/8+15/15 | 8/11+16/21 | 7/10+13/18 |
| 33388694 (0:27) | 8/8+15/15 | 8/8+15/15 | 8/11+16/21 | 7/10+13/18 |

Asserts per job 4x LINK-SHIM-OK + 4x LINK-FORKMAIN-ABSENT-OK + 4x DRIVER-SHIM-OK; all containers exit 0; in-job md5 guards green (A-fresh + RES manifests). Rule: HOLDS x3 — J_RES tallies bit-identical to 92's J_SXC in all 3 runs; J_orig reproduces 63 ORIG (8/11+16/21) in all 3.

**4. Why-not (recomputed identities = p92 logic, 0.35 rad/50 mm; binary EXACT all 3 runs).** J_RES all 3 runs seats [1,2,4,5,6,7,10] via the same 13 edges (incl. (2,4),(2,5),(2,6),(2,10),(4,10),(5,10)), all <0.15 rad/<35mm — identical seated set AND edge family to 92's SXC. Piece 3 (control, untouched): placed-but-wrong all 3 runs as in 92 — contextual search-basin miss, not rim quality. Pieces 8/11/12 missed by both J_orig and J_RES (small-rim frontier n=66/54/55); piece 9 no GT both arms. Rims exonerated. Seating render eye-checked: artifacts/pota95/pota95_seating_J_RES.png (green P1/2/4/5/6/7/10 on-vessel, red dashed P3/P8/P11/P12 off-vessel, no collapse).

**5. Evidence.** Spartan pota95_repro/ (p95_resample.py, gate95.py, render95.py, run_pota95_stage_AJ.sbatch, pre/post md5 manifests, Jsel_RES_vs_ORIG.png, pota95_seating_J_RES.png, p95_submit.log) + in-place bundle at pota92/prep/pota92_bundle_J_SXC/ (8 Bl_0 resampled, everything else byte-identical) + sfs_main/pota95_run_{33388692,33388693,33388694}/ (binaries, snapshots, fetch tgzs named pota92_fetch.tgz inside — sbatch cosmetic leftover, contents are P95). Laptop artifacts/pota95/ (Jsel_RES_vs_ORIG.png, pota95_seating_J_RES.png, 3 fetch tgzs). Poll was sacct directly (never slurm_poll.sh); repeats = 3 same-binary.

**6. Recommendation.** R-RESAMPLE is seating-neutral on J (7+13 before and after): safe to roll forward as the rim-hygiene step wherever the lead wants author-regime rims (e.g. combined with B roll-out or the 78 lane) — it changes nothing about the piece-3 contextual miss or the small-rim frontier. J needs no further rim work; open items stay with the assembly lane.
