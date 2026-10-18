# 83: Swap cure — Pot G (roll-out 1 of 7)

**What to build:** Pot G re-seated via correct slots — gate + E2E lift, first roll-out of the proven Pot F swap cure.

**Answers:** E1

**Blocked by:** 80 (SLOT SWAP bound ~94/129: fresh S0/Bl_0 carry author S1/Bl_1; size-desc sort mesh_processing_headless.cpp:218/:1680 puts denser exterior wall first; author interior-first; T04 guard edgeline_extraction_headless.cpp:3692 never ran in t39 pipe) + 81 (LANDS on Pot F: SXCD slot-exchange S0<->S1 + Bl_0<->Bl_1 plus F06 45->55 densify, E2E 6/6+9/9 x3 bit-identical jobs 33344601/615/617; SXC-without-densify 5/5+7/7 via 50-pt loader gate; renders eye-checked) + 04 (T04 guard exists, unwired).

**Status:** landed-SHORTFALL (lead 2026-10-18 — gate green, E2E one borderline edge short; renders eye-checked by lead; sacct-verified)

**Starting position:** Pot G is the next roll-out per the 80 census (G 6/7 swapped: G01,G03,G04,G06 +2 more per family table; controls G02,G05,G07 unswapped). Same size as proven F (7 pieces), mostly clean loops — isolates the swap cure from forest/merge confounds (E) and shape confounds (C02). Recipe = ticket 81 SXCD: (a) scratch slot-exchange S0<->S1 + Bl_0<->Bl_1, (b) 50-pt densify check per piece (F06 needed 45->55 same-loop resample — check every G Bl_0 under ~50 pts the same way, zero ORIG points). If any G piece shows the forest signature (78: G02/G05/G06 fire; r>=1.4+j>=1 tracking neither author loop), do NOT force it — report it back to 78 instead. C02-style fused pieces stay out (none expected on G). Zero ORIG points in any fix; ORIG evidence-only (gate ruler).

**Rules:** land with Bl_0 vs ORIG Bl_0 <2mm + jumps->0 (no reorder expected — swapped pieces are clean loops) + E2E at/above G's best fresh tally 4/7+3/10 (ticket 60, x3 identical) x3 same-binary + controls green (G_orig + A 8/8+15/15) in same runs; renders (eye-check) before landing; E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK asserts per job; no commits; sacct-direct polling (never scripts/slurm_poll.sh); Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); repeats >=3; no gate relaxation without a mechanism.

- [ ] Pot G slot-exchange + densify check, one variable each
- [ ] Gate + E2E rerun x3 or measured why-not
- [ ] Job IDs + sacct states

## Comments (worker, 2026-10-18 — COMMIT NOTHING; lead to commit)

**Verdict: SHORTFALL. Gate GREEN on all 6 swapped pieces (SXC, no densify needed), E2E 4/7+2/10 x3 bit-identical — one borderline edge short of the 4/7+3/10 bar. Controls green, asserts green, renders eye-checked. Rims are cured; the miss is search-side (piece placement), not rim quality. Nothing to hand to 78.**

**0. Census correction (measured, login node, ORIG evidence-only distances).** 6/7 swapped — but NOT the ticket's list: swapped = G01–G06 (fresh Bl_0 vs ORIG Bl_1 0.47–0.72mm; fresh S0 vs ORIG S1 0.29–0.30 on all six). Only G07 is unswapped (Bl_0vG0 0.80, S0vOS0 0.34). Ticket's controls G02/G05 are swapped at both surface and breakline level. G02/G05/G06 carry 78's count+jump flags (r 1.47–1.63, j 5–10) BUT track the author exterior loop (Bl_0vG1 0.57–0.72), so per the brief's definition (r>=1.4+j>=1 tracking NEITHER author loop) they are not forest pieces — slot-exchange applied to all six, G07 untouched. Post-exchange all SXC Bl_0 are clean single loops (n ratios 0.93–0.95, j=0), so no 78 handoff.

**1. Fix (one variable: file-level slot swap, F-recipe).** cp -a pota39_bundle_G -> /data/gpfs/projects/punim2657/pota83_repro/prep/pota83_bundle_G_SXC; pieces 01–06 Bl_0<->Bl_1 + S0<->S1 exchanged (md5-verified swap, Axes/Mesh/GT untouched). Densify check: min exchanged Bl_0 n=77 (G06) > 50-pt loader gate — no densify variable, cure is pure SXC. Zero ORIG points (ORIG distances only). Bundle md5: pota83_repro/prep/pota83_G_SXC_bun_md5.txt.

**2. Gate (SXC Bl_0 vs ORIG Bl_0 @GT; jumps>5mm):** G01 0.56/100%/0j, G02 0.57/98.1%/0j, G03 0.61/98.8%/0j, G04 0.53/100%/0j, G05 0.61/100%/0j, G06 0.53/100%/0j; control G07 0.80/68.6%/0j untouched. Rule (a) LANDS. Render eye-checked: artifacts/pota83/Gsel_SXC_vs_ORIG.png (red SXC tracks gray ORIG ring all round, all 6 panels, coherent, no scatter).

**3. E2E (cure-potA @ bffefb6 asserted in-job, k=5/b=3 shim; stage run_pota83_stage_AG.sbatch = 81 template minus T04 arm):**

| job (sacct COMPLETED 0:0, worker-verified) | A_orig | A_fresh | G_orig | G_SXC |
|---|---|---|---|---|
| 33359827 (13:20) | 8/8+15/15 | 8/8+15/15 | 7/7+10/10 (51/31) | 4/7+2/10 (125/30) |
| 33359828 (17:36) | 8/8+15/15 | 8/8+15/15 | 7/7+10/10 (51/31) | 4/7+2/10 (125/30) |
| 33359829 (16:01) | 8/8+15/15 | 8/8+15/15 | 7/7+10/10 (51/31) | 4/7+2/10 (125/30) |

Asserts per job 4x LINK-SHIM-OK + 4x LINK-FORKMAIN-ABSENT-OK + 4x DRIVER-SHIM-OK; all containers exit 0; bundle guards (asm clean, A-fresh + G-SXC md5 intact) green in job stdout. Forest hypotheses 146 (fresh R1) -> 125. Rule (b): sherds match bar (4/7), edges SHORT 2/10 vs 3/10 — all 3 runs bit-identical tallies AND identical identities.

**4. Why-not (recomputed identities, p83_identities.py = p60 logic, all 3 jobs identical).** SXC seats [1,2,3,5] via (1,3),(2,3),(2,5); fresh seated [1,3,4,6] via (1,3),(1,4),(3,6). Pieces 4/6 placed-wrong (trans errs 147–835mm, no near-misses), piece 7 unplaced both. Edge (2,3) is borderline 0.165rad/47.8mm vs the 50mm gate (binary counts it wrong: recompute 3/10 vs binary 2/10); edges (1,7) 72.8mm and (5,7) 139mm fail translation only (angles pass) — piece-7 placement is the swing vote. Seating render eye-checked: artifacts/pota83/pota83_seating_G_SXC.png (green P1/2/3/5 track gray GT bowl; red dashed P4/6/7 off-vessel). Rims exonerated (all gate-green); no further rim work on G indicated — successor is search-side (unplaced P7, thrown P4/P6), not another rim pass.

**5. Evidence.** Spartan pota83_repro/ (bundle, gate83.py, render83.py, make_stage83.py, stage sbatch, slurm-*.out) + sfs_main/pota83_run_{33359827,33359828,33359829}/ (binaries, snapshots, pota83_fetch.tgz). Laptop artifacts/pota83/: Gsel_SXC_vs_ORIG.png, pota83_seating_G_SXC.png, 3 fetch tgzs + extracted fetch_*/, p83_identities.py, p83_render.py. Poll was sacct directly throughout.

## Comments (lead landing, 2026-10-18)

Lead review: renders eye-checked (rim overlays track on all 6 panels, no scatter; seating shows green P1/2/3/5 on-vessel, red P4/6/7 off). sacct lead-verified 33359827/828/829 COMPLETED 0:0. Census correction accepted (swapped = G01-G06, G07 sole control; G02/G05 78-flags track the author exterior loop, not forest). Verdict SHORTFALL stands on the binary ruler (2/10 vs bar 3/10; worker recompute 3/10 on the 47.8-vs-50mm borderline edge noted as ruler caveat, not a pass). No G rim re-roll (gate green, forest 146->125). Next roll-out: D per worker recommendation.

**6. Recommendation for lead.** Do not re-roll G rims (gate green, forest 146->125). Next roll-out pot: D (24/29 swapped systematic whole-pot shifts, mostly clean loops — same profile as proven F/G) — E stays blocked behind 82's segfault, C stays with 79 (shape), forest-heavy I/J wait on 78/82 outcomes. G E2E shortfall is a search-basin datum for the assembly lane, not a rim-cure failure.
