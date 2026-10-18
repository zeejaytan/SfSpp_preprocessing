# 81: Swap cure (HELD — dispatch after 78/79 home)

**What to deliver:** swapped pieces re-seated via correct slots — gate + E2E lift.

**Answers:** E1

**Blocked by:** 80 (SLOT SWAP bound ~94/129: fresh S0/Bl_0 carry author S1/Bl_1; size-desc sort mesh_processing_headless.cpp:218/:1680 puts denser exterior wall first; author interior-first; T04 guard edgeline_extraction_headless.cpp:3692 never ran in t39 pipe — zero SFS-T04 lines in prep/EdgeLineExtraction.log; render eye-checked F02_swap.png) + 04 (T04 interior-first guard exists, unwired).

**Status:** results-in (worker 2026-10-18, lead write-back; renders eye-checked)

**Starting position:** (a) re-run edge WITH wired T04, or (b) scratch slot-exchange S0<->S1 + Bl_0<->Bl_1 — starting pot F (6 swapped + F01 unswapped control); then roll per 80's swap census (D 26/29, E 29/31, F 6/7, G 6/7, I 28/30, J 9/12, B 8/9, C 2/4). C02 stays with 79 (fused, swap will not cure). If T04's vote misfires on any swapped piece, name a T04-vote successor instead of forcing it. Zero ORIG points in any fix; ORIG evidence-only.

**Rules:** land with Bl_0 vs ORIG Bl_0 <2mm + jumps->0 (no reorder needed — swapped pieces are clean loops) + E2E at/above each pot's best fresh tally x3 same-binary + controls green in same runs; renders (eye-check); E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats >=3; no gate relaxation without a mechanism.

- [ ] Pot F swap cure arms (wired-T04 vs slot-exchange), one variable each
- [ ] Gate + E2E rerun x3 or measured why-not
- [ ] Roll to remaining swapped pots per census
- [ ] Job IDs + sacct states

## Comments (lead write-back, 2026-10-18 — worker had no pota lane in its workspace)

LANDS on Pot F: SXCD (slot-exchange S0<->S1 + Bl_0<->Bl_1, plus F06 Bl_0 densified 45->55pts same-loop resample, zero ORIG points) E2E 6/6+9/9 x3 bit-identical (jobs 33344601/33344615/33344617, all COMPLETED 0:0, lead-verified). Controls green: A_orig/A_fresh 8/8+15/15, F_orig 6/6+9/9. SXC/T04 without densification 5/5+7/7 — F06's 45-pt interior loop trips the binary 50-pt loader gate (main.cpp), which densification clears. Rims gate green (0.56-0.69mm, jumps 0). Vehicle: cure-potA @ bffefb6, k=5/b=3, LINK-SHIM-OK + DRIVER-SHIM-OK. Renders eye-checked by lead: F06_dense_vs_ORIG (red tracks gray ring, med 0.65) + Fsel_SXC_vs_ORIG (F02 red tracks gray all round; F01 panel shows doubled red as caveated — F01 belongs to 78). Gate table: F02 0.61/100%/0j, F03 0.56/100%/0j, F04 0.62/100%/0j, F05 0.69/100%/0j, F06d 0.65/100%/0j; F01 control 1.00/58.5%/4j (78). Cross-check Bl_1 4.3-6.0mm confirms swap direction. Bundle pota81_bundle_F_SXCD; R1 33343950/52/53 + R2 33344601/615/617 all COMPLETED 0:0 (lead-verified). Roll to remaining swapped pots per 80 census: still open.
