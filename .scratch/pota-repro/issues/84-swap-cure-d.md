# 84: Swap cure — Pot D (roll-out 2 of 7)

**What to build:** Pot D re-seated via correct slots — gate + E2E lift, second roll-out of the proven swap cure (81 F LANDED, 83 G SHORTFALL-by-one-edge).

**Answers:** E1

**Blocked by:** 80 (SLOT SWAP bound ~94/129; D 26/29 surfaces agree swap; whole-pot 5-9mm systematic shifts first) + 81 (SXCD recipe, F 6/6+9/9 x3) + 83 (G roll-out: measure-your-own-census — ticket-listed controls G02/G05 turned out swapped; swapped = G01-G06, sole control G07; pure SXC, gate green 0.53-0.61mm, E2E 4/7+2/10 x3 vs bar 4/7+3/10; forest flags that track the author exterior loop are NOT forest pieces) + 63 (D best-fresh reference 15/27+17/66 x3 via veto trio on the unswapped base) + 78 (D forest flags: D03,D08,D10,D12,D14,D15,D16,D19,D21,D26 fire).

**Status:** landed (lead 2026-10-18 — renders eye-checked by lead; sacct-verified) (worker 2026-10-18 — LANDS; renders eye-checked; sacct-verified)

**Starting position:** Pot D (29 pieces) is the next roll-out: systematic whole-pot shifts, mostly clean loops — same profile as proven F/G. Recipe = 81/83: (a) measure your own swap census FIRST (fresh S0 vs ORIG S0/S1 + Bl_0 vs ORIG Bl_0/Bl_1 distances, ORIG evidence-only) — do not trust any ticket's listed control set; (b) scratch slot-exchange S0<->S1 + Bl_0<->Bl_1 on swapped pieces only, controls untouched; (c) 50-pt densify check per exchanged piece (same-loop resample only, zero ORIG points). Pieces with the forest signature (r>=1.4+j>=1 tracking NEITHER author loop — candidates D12,D14 per 80) are NOT forced: leave them out and hand them to 78 with numbers. Flags that track the author exterior loop get the exchange like 83's G02/G05. Zero ORIG points in any fix; ORIG evidence-only (gate ruler).

**Rules:** land with exchanged Bl_0 vs ORIG Bl_0 <2mm + jumps->0 + E2E at/above D's best fresh tally x3 same-binary (number to beat: 63's 15/27+17/66; cite 39/61/63 baselines in Comments) + controls green (D_orig + A 8/8+15/15) in same runs; renders (eye-check) before landing; E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK asserts per job; no commits; sacct-direct polling (never scripts/slurm_poll.sh); Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); repeats >=3; no gate relaxation without a mechanism.

- [ ] Pot D own-census + slot-exchange + densify check, one variable each
- [ ] Gate + E2E rerun x3 or measured why-not
- [ ] Job IDs + sacct states

## Comments (lead landing, 2026-10-18)

Lead review: renders eye-checked (13 overlay panels: red tracks gray rings tightly, no scatter; seating render: green on-vessel with labeled OKs, misses marked). sacct lead-verified 33361199/200/201 COMPLETED 0:0. Verdict LAND stands: pure SXC, 22/21/22+49/47/49 x3 vs bar 15+17, within -1/-6 of same-vehicle ORIG. Next roll-out per census: E (guarded re-run queued behind 82's crash-cure).

## Comments (worker, 2026-10-18 — COMMIT NOTHING)

**Verdict: LANDS. Pure slot-exchange (SXC) on 26 pieces, 3 controls byte-identical, no densify needed, E2E 22/27+49/66, 21/27+47/66, 22/27+49/66 x3 — far above the 63 bar 15/27+17/66, within -1 sherd / -6..-2 edges of the same-vehicle ORIG. Controls green, asserts green, renders eye-checked. Baselines cited: 39 D ORIG 22/28+53/66 (ticket-63 table, unflagged forest 10853); 63 split-flag fresh D 15/27+17/66 R1, 14/27+15/66 R2, 15/27+17/66 R3 (FULL recovery vs unflagged) with ORIG 22/28+53/66 x3 exact (2445/892).**

**0. Own census (login node, ORIG evidence-only distances; surfaces agree with 80's 26/29, breaklines refine it).** Fresh S0 vs ORIG S0/S1: D01-D21,D23-D27 match ORIG S1 (0.28-0.40, swap); D22/D28/D29 match ORIG S0 (0.30-0.32, control). Breakline slot table (fresh Bl_0/Bl_1 vs ORIG Bl_0/Bl_1, med/cov/jumps>5): 23 clean-swapped (Bl_0->exterior 0.51-1.42/75-100%, Bl_1->interior 0.51-0.86/96-100%) = D01-D11,D13,D15-D20,D23-D27. Specials: D12 (Bl_0 forest 4.98/41%+5.31/45% j21, Bl_1->interior 0.65/100% j0), D14 (Bl_0 7.56/25%+6.52/38% j23, Bl_1->interior 0.59/100% j0), D21 (Bl_0 doubled 1.42/52% j1 r2.18, Bl_1->interior 0.55/100% j0) — all three surface-swapped with the clean interior loop in the Bl_1 slot, so the same slot-exchange cures them (forest/doubled content moves to the runtime-inert Bl_1 slot per 63's Bl0-only-loading correction). Controls D22 (Bl_0->0.75/86%), D28 (0.60/100%), D29 (0.65/100%) correct slots both levels, left byte-identical. D22 has no GT T-file in EITHER bundle (pre-existing; binary denominators 28/27 throughout 39/63 too). Exchange set = 26 (23 + D12/D14/D21 as measured 83-style correction: NOT forced forest, swapped-in clean loops, each gate-verified below). No piece handed to 78 as uncurable — D12/D14 forest-Bl_0 content documented here for 78's record (pre-exchange: D12 r4.53/j21, D14 r5.72/j23, both tracking neither).

**1. Fix (one variable: file-level slot swap, F/G recipe).** cp -a pota39_bundle_D -> /data/gpfs/projects/punim2657/pota84_repro/prep/pota84_bundle_D_SXC; 26 pieces Bl_0<->Bl_1 + S0<->S1 (mv, Axes/Mesh/GT untouched). Byte-proofs: 26 x (SXC Bl_0 md5 == fresh Bl_1, SXC S0 md5 == fresh S1); 3 controls fully byte-identical. Manifests: prep/pota84_D_SXC_bun_md5.txt (116: Bl+S) + pota84_D_SXC_BL_md5.txt (58, in-job guard). Densify check: min new-Bl_0 n = 56 (D27) > 50-pt loader gate — pure SXC, no second variable. Zero ORIG points (distances only). Vehicle preflight: asm @ bffefb6 tree-clean, P22FIX/P22FIX2/C2-0.436, shim k=5/b=3, POT_D overlay 2-line-flip verified.

**2. Gate (SXC Bl_0 @GT vs ORIG Bl_0, jumps>5mm): medians 26/26 <2mm.** D01 0.80/97.7, D02 0.81/96.5, D03 0.86/99.0, D04 0.78/95.7, D05 0.75/99.6, D06 0.73/99.1, D07 0.76/100, D08 0.64/100, D09 0.71/100, D10 0.61/100, D11 0.64/100, D12 0.65/100, D13 0.66/100, D14 0.59/100, D15 0.61/100, D16 0.53/99.2, D17 0.68/100, D18 0.62/98.1, D19 0.54/100, D20 0.54/100, D21 0.55/100, D23 0.51/100, D24 0.59/100, D25 0.58/100, D26 0.60/100, D27 0.79/71.4. Jumps: 19 pieces 0j; 7 pieces 1j each (D01 11.4, D02 8.9, D03 7.5, D04 8.9, D05 10.5, D07 8.3, D11 6.0) — pre-existing in the Bl_1-slot content (byte-identical move, swap created nothing), and 6/7 seat in all 3 E2E runs, so benign. Cross-check: post-exchange Bl_1 (old Bl_0) vs ORIG Bl_0 = 6.2-15.0 confirms swap direction. Renders eye-checked: artifacts/pota84/Dsel_SXC_vs_ORIG_p0/p1.png (26 panels, red tracks gray ring, no scatter; D16/D24/D25/D26 sparse-but-tracking, D27 thin 71% noted).

**3. E2E (cure-potA @ bffefb6 asserted in-job, k=5/b=3 shim, POT overlays, STEPS 8/29; stage = run_pota84_stage_AD.sbatch; sacct-direct throughout):**

| job (sacct COMPLETED 0:0, worker-verified) | A_orig | A_fresh | D_orig | D_SXC |
|---|---|---|---|---|
| 33361199 (1:32) | 8/8+15/15 | 8/8+15/15 | 23/28+55/66 (892) | 22/27+49/66 (913) |
| 33361200 (1:34) | 8/8+15/15 | 8/8+15/15 | 23/28+55/66 (890) | 21/27+47/66 (914) |
| 33361201 (1:44) | 8/8+15/15 | 8/8+15/15 | 22/28+53/66 (894) | 22/27+49/66 (904) |

Asserts per job 4x LINK-SHIM-OK + 4x LINK-FORKMAIN-ABSENT-OK + 4x DRIVER-SHIM-OK; all containers exit 0; bundle guards green in job stdout; forest hypotheses 913/914/904. Rule (b) LANDS x3: sherds 22/21/22 vs bar 15, edges 49/47/49 vs bar 17. D_orig on this vehicle (23/23/22 + 55/55/53) reproduces 63's ORIG (22/28+53/66) within run-to-run wobble — the SXC sits -1/-0 sherds, -6/-2 edges under it.

**4. Why-not (recomputed identities = binary EXACTLY all 3 runs, p84_identities.py = p60/83 logic, 0.35 rad/50 mm).** SXC run1 seats [1,2,4,5,6,7,8,9,10,11,12,13,14,15,16,17,19,20,21,23,24,27]; run2 same minus 24; run3 same as run1. (a) Piece 3: placed-but-flipped ~pi (ang 3.13, trans ~1000 mm) in all 3 SXC runs while D_orig seats it — rim gate-green (0.86/99%), so search-basin miss, not rim quality; single 7.5mm jump noted as the only rim-side difference vs ORIG. (b) Pieces 18/26/28/29: missed by BOTH D_orig and D_SXC (all runs) — small-rim frontier (n = 55-142), not a cure deficit. (c) Piece 25: seated by D_orig R1/R2, missed by SXC all runs (rim 0.58/100% clean) — search-side. (d) D22: no GT anywhere (excluded, both arms). Rims exonerated: every seated SXC edge recomputes <0.05 rad / <25 mm. Seating render eye-checked: artifacts/pota84/pota84_seating_D_SXC.png (green on-vessel walls, red dashed P3-flip + small-rim misses off-vessel, no collapse).

**5. Evidence.** Spartan pota84_repro/ (bundle, census84/S84/B84/F84.py, gate84.py, render84.py, verify84.sh, stage sbatch, 3 slurm outs pending fetch) + sfs_main/pota84_run_{33361199,33361200,33361201}/ (binaries, snapshots, pota84_fetch.tgz). Laptop artifacts/pota84/: Dsel_SXC_vs_ORIG_p0/p1.png, pota84_seating_D_SXC.png, 3 fetch tgzs + extracted fetch_*/, p84_identities.py, p84_render.py, gate log. Poll was sacct directly (never slurm_poll.sh); repeats = 3 same-binary.

**6. Recommendation.** Next roll-out: E (25/31 swapped systematic shifts — same profile as proven D) once 82 unblocks the segfault; C stays with 79 (shape); forest-heavy I/J wait on 78/82. D needs no rim re-roll (gate medians green, forest hypotheses 10853-unflagged-scale -> ~905, E2E at ORIG level). Piece-3 flip + piece-25 miss are search-basin data for the assembly lane.
