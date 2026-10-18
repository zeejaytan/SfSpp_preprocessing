# Pot I densify + E2E (I27 same-loop resample, then run the stopped cure)

GOAL: MATCH AUTHOR'S INPUT.

**What to deliver:** Finish what ticket 91 stopped: densify I27's new-Bl_0 (49 -> >=55, same-loop resample, zero ORIG points — F06 45->55 precedent in 81), re-gate I27, then E2E x3 on the pota91 SXC bundle vs the 63 bar (best split-fresh I 8/27+3/65; ORIG 25/27+59/65 x3 exact) with I_ORIG + A 8/8+15/15 controls.

**Answers:** E1

**Blocked by:** 91 (STOPPED-AT-DENSIFY: bundle/manifests/gate/renders ready at pota91_repro/ for direct reuse) + 84 (D LAND: E2E recipe) + 63 (I bar) + 39 (t39-pipe).

**Status:** results-in (worker 2026-10-18 — LANDS; renders eye-checked; sacct-verified)

**Starting position:** Reuse /data/gpfs/projects/punim2657/pota91_repro/prep/pota91_bundle_I_SXC/ directly — densify ONLY I27 Bl_0 in place (same loop, same face; Axes/Mesh/GT untouched; byte-proof I27 SXC-Bl_0 == resampled fresh-Bl_1 content). I28/I29 stay as-is (no GT in either bundle, E2E-excluded per D22 precedent — densifying unscored rims changes nothing). New scratch only if the bundle must be copied: pota94_repro/.

**Rules:** one variable (I27 density only — no other piece touched); re-gate I27 (median <2mm, jumps called out); E2E x3 same-binary on cure-potA @ bffefb6, k=5/b=3, with LINK-SHIM-OK + DRIVER-SHIM-OK asserts per job; controls in the same runs; sacct-direct polling (never scripts/slurm_poll.sh); COMMIT NOTHING; Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); repeats >=3.

- [ ] I27 densify 49->55+ (same loop, byte-proof)
- [ ] Re-gate I27 + bundle gate green
- [ ] E2E x3 vs bar 8+3 + controls green
- [ ] Job IDs + sacct states

## Comments (worker, 2026-10-18 — COMMIT NOTHING)

**Verdict: LANDS. I27 densified 49->55 (same-loop resample, F06 precedent), re-gate 27/27 GREEN, E2E 25/27+54/65 x3 bit-identical — far above the 63 bar (best split-fresh I 8/27+3/65), at same sherd count and -5 edges vs same-vehicle ORIG. Controls green, asserts green, renders eye-checked. Baselines cited: 63 split-fresh I R1/R2 8/27+3/65, R3 6/27+3/65 (forest 8512) with ORIG 25/27+59/65 x3 exact (1424/667); 39 unflagged I 9+4.**

**0. Densify (one variable: I27 Bl_0 only, login node, zero ORIG points).** pota94_repro/densify_i27.py = 81's densify_f06.py verbatim algorithm (arc-length uniform resample, target max(55, round(L/1.8)), normals lerped+renormalized, curvature 0.01, proportional segment bounds): loop 93.7mm, n=49, spacing 1.91mm -> N=55, max step 1.70mm. Before md5 a984be9871c9daebee7e112a9e095499 (WIDTH 49); resample out pota94_repro/Pot_I_Piece_27_Breakline_0_dense.pcd; installed in place over the SXC Bl_0; after md5 d0a1e7711b2caec1d3a68bde17d5da82 == resample output (byte-proof). One-variable proof: 91's pota91_I_SXC_BL_md5.txt re-checked against the live bundle — 59/60 pass, exactly ONE mismatch: Pot_I_Piece_27_Breakline_0.pcd (the densified file). Axes/Mesh/Surfaces/GT untouched; I28/I29 left as-is per brief (no GT, E2E-excluded).

**1. Re-gate (gate91.py, SXC Bl_0 @GT vs ORIG Bl_0): 27/27 GREEN.** I27 now n=55 med=0.47 <2mm=100.0% jumps=0 GREEN (was n=49 med=0.56 j0). Rest unchanged from 91 (I01 0.78 … I26 0.53; pre-existing jumps I01 6.2, I02 13.3, I05 5.2, I11 8.3, I13 18.4@idx1, I14 5.2 — byte-identical Bl_1-slot content, swap created nothing). New in-job guard manifest pota94_repro/pota94_I_SXC_BL_md5.txt (I27 line updated) verifies MANIFEST94-ALL-OK from the bundle. Render eye-checked: artifacts/pota94/I27_dense_vs_ORIG.png (red dense loop tracks gray ORIG ring tightly, no scatter).

**2. E2E (cure-potA @ bffefb6 asserted in-job, k=5/b=3 shim, POT overlays, STEPS 8/30; stage = run_pota94_stage_AI.sbatch adapted from 84's 4-arm template; sacct-direct throughout):**

| job (sacct COMPLETED 0:0, worker-verified) | A_orig | A_fresh | I_orig | I_SXC |
|---|---|---|---|---|
| 33387455 (0:53) | 8/8+15/15 | 8/8+15/15 | 25/27+59/65 (667) | 25/27+54/65 (612) |
| 33387456 (1:02) | 8/8+15/15 | 8/8+15/15 | 25/27+59/65 (667) | 25/27+54/65 (609) |
| 33387457 (0:47) | 8/8+15/15 | 8/8+15/15 | 25/27+59/65 (667) | 25/27+54/65 (610) |

Asserts per job 4x LINK-SHIM-OK + 4x LINK-FORKMAIN-ABSENT-OK + 4x DRIVER-SHIM-OK; all containers exit 0; bundle guards green in job stdout. Rule LANDS x3: sherds 25 vs bar 8, edges 54 vs bar 3. I_orig on this vehicle reproduces 63's ORIG EXACTLY (forest 1424/pruned 667, 25/27+59/65 x3) — the SXC sits at -0 sherds, -5 edges under it.

**3. Why-not (recomputed identities = binary EXACTLY on I_orig all runs; p84_identities.py logic, 0.35 rad/50 mm).** I_SXC binary 25/27+54/65 x3; strict recompute 25 seated, 53/65 edges — the 1-edge gap is five near-miss edges at 51-70mm ((4,11) 51.8, (5,11) 58.6, (5,25) 70.6, (7,11) 56.8, (20,25) 69.5; binary seats one of them), standard strict-recompute conservatism. Seated (identical all 3 runs): [1,3,4,5,6,7,8,9,10,11,12,14,15,16,17,18,19,20,21,22,23,24,25,26,27]; missing vs ORIG: I2/I13 (placed-but-flipped ~pi, ang ~2.8, trans ~950mm — search-basin misses, rims gate-green 0.83/0.78). Notably I27 (the densified piece) seats in ALL 3 SXC runs while ORIG itself misses I27 (I_orig seated [1-24,26], missing 25/27) — the densified rim seats better than ORIG's own. I28/29/30: no GT anywhere (excluded, both arms). Rims exonerated: every seated SXC edge recomputes <0.09 rad / <50 mm except borderline (11,25) 0.188/49.7. Seating render eye-checked: artifacts/pota94/pota94_seating_I_SXC.png (green on-vessel walls, red dashed P2/P13 misses off-vessel, no collapse).

**4. Evidence.** Spartan pota94_repro/ (densify_i27.py, dense pcd, pota94_I_SXC_BL_md5.txt, run_pota94_stage_AI.sbatch, render94.py, render94seat.py, I27_dense_vs_ORIG.png, pota94_seating_I_SXC.png) + sfs_main/pota94_run_{33387455,33387456,33387457}/ (binaries, snapshots, pota94_fetch.tgz). Laptop artifacts/pota94/: I27_dense_vs_ORIG.png, pota94_seating_I_SXC.png, 3 fetch tgzs + extracted fetch_*/, p94_identities_summary.txt, densify_i27.py, run_pota94_stage_AI.sbatch, pota94_I_SXC_BL_md5.txt. Tickets 39-93 and pota90/pota92/pota93 scratch untouched (their jobs ran concurrently on other nodes). COMMIT NOTHING.

**5. Recommendation.** Pot I cure LANDED — no further rim work needed (gate medians green, E2E at ORIG sherd level, -5 edges). I2/I13 flips are search-basin data for the assembly lane, not rim deficits. The 91 bundle (now I27-dense) is the landed Pot I cure input.
