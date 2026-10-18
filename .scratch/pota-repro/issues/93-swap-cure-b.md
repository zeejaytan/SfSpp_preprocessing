# Swap cure roll-out (Pot B) — own census, slot exchange, gate + E2E

GOAL: MATCH AUTHOR'S INPUT.

**What to deliver:** Pot B slot-exchange cure following the landed F (81) / D (84) recipe, with B's own measured census (verify each rim fresh-S0 vs ORIG-S0/S1 within 2mm before exchanging — 89 re-census moved pieces, trust nothing listed).

**Answers:** E1

**Blocked by:** 89 (R-SWAP CONFIRMED; regime table) + 84 (D LAND: full recipe — census, byte-proofs, manifests, densify check, why-not) + 83 (census-correction precedent) + 63 (B fresh bar — read from the ticket-63 table before running).

**Status:** results-in (worker 2026-10-19 — LANDS; renders eye-checked; sacct-verified)

**Starting position:** Read 84 Comments (recipe) then the ticket-63 table for B's bar + ORIG denominators. Work from the t39-pipe fresh B bundle + ORIG; new scratch /data/gpfs/projects/punim2657/pota9X_repro/prep/ (X = your ticket's last digit — see Boundary); renders under laptop artifacts/pota9X/.

**Rules:** land with own census table + gate (SXC Bl_0 medians <2mm, jumps called out) + E2E x3 same-binary vs 63 bar + controls (B ORIG + A 8/8+15/15) in same runs; E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK asserts per job; min new-Bl_0 n > 50 else STOP and report (densify is a separate ticket); no commits; sacct-direct polling (never scripts/slurm_poll.sh); Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); repeats >=3.

- [ ] Own B census (measure, don't assume)
- [ ] Slot exchange + byte-proofs + gate
- [ ] E2E x3 vs bar + controls green
- [ ] Job IDs + sacct states

## Comments (worker, 2026-10-19 — COMMIT NOTHING)

**Verdict: LANDS. Pure slot-exchange (SXC) on B02–B09, B01 byte-identical (forest, handed to 78 with numbers). E2E 5/9+3/15, 6/9+5/15, 6/9+5/15 x3 vs the bar 4/9+2/15 (binaries; strict 4+2/2+5/2+5) — at/above bar all 3 runs, controls green, asserts green, renders eye-checked. Baselines cited: 39 B ORIG 9/9+15/15 (114/76-77) + fresh best 4/9+2/15 R1 (1442/31); 63 split-flag did not run B (no B row — bar is the 39 fresh best).**

**0. Own census (login-node, ORIG evidence-only distances; surfaces agree with 80's 8/9, breaklines correct 80's listed controls).** Fresh S0 vs ORIG S0/S1: B01 0.30/vS0 CLEAN; B02–B09 2.99–3.79/vS0 vs 0.26–0.34/vS1 (all 8 SWAPPED). Breakline 2x2 (fresh Bl_0/Bl_1 vs ORIG Bl_0/Bl_1, med/cov/jumps>5): B02 F0vG1 0.98/66.8 j11 + F1vG0 1.15/68.1 j1; B03 0.79/100 + 0.61/100; B04 0.77/81.9 j7 + 0.56/100; B05 0.68/95.9 j15 + 0.60/100; B06 0.69/86.2 j8 + 0.52/100; B07 0.61/100 + 0.53/100; B08 0.60/100 j3 + 0.49/100; B09 0.82/76.3 j4 + 0.62/100. Correction to 80 (83-style): B03/B04/B06/B08 are SWAPPED, not clean — single-side meds looked ambiguous (loops run close, F0vG0 1.3–1.9) but the 2x2 + surfaces (S0vOS1 ~0.3) are unambiguous. B01 FOREST: F0 4.43/35.8 + 4.93/21.5 j24 r=5.09 tracks neither; F1vG1 0.70/100 j0 is a clean EXTERIOR loop in the Bl_1 slot, so no slot-exchange puts the author-interior loop in Bl_0 — NOT forced, left byte-identical for 78 (float-audit masked-interior note 0.73/100% recorded for 78's SEL lane).

**1. Fix (one variable: file-level slot swap, F/83/D recipe).** cp -a pota39_bundle_B -> /data/gpfs/projects/punim2657/pota93_repro/prep/pota93_bundle_B_SXC; B02–B09 Bl_0<->Bl_1 + S0<->S1 (mv); Axes/Mesh/GT untouched; B01 fully byte-identical. Byte-proofs: 8 x (SXC Bl_0 md5 == fresh Bl_1, SXC S0 md5 == fresh S1); B01 Bl+S byte-identical. Manifests: prep/pota93_B_SXC_bun_md5.txt (36: Bl+S) + pota93_B_SXC_BL_md5.txt (9, in-job guard). Densify check: min new-Bl_0 n = 70 (B09) > 50-pt loader gate — pure SXC, no second variable. Zero ORIG points (distances only). Vehicle preflight: asm @ bffefb6 tree-clean, P22FIX/P22FIX2/C2-0.436, shim k=5/b=3, POT_B overlay 2-line-flip verified.

**2. Gate (SXC Bl_0 @GT vs ORIG Bl_0, jumps>5mm): medians 8/8 <2mm.** B02 1.15/68.1 +1j(43.2, pre-existing Bl_1 content, byte-identical move), B03 0.61/100, B04 0.56/100, B05 0.60/100, B06 0.52/100, B07 0.53/100, B08 0.49/100, B09 0.62/100 — 7 pieces 0j. Cross-check post-exchange Bl_1 (old Bl_0) vs ORIG Bl_0 = 1.33–3.45 confirms swap direction. Renders eye-checked: artifacts/pota93/Bsel_SXC_vs_ORIG_p0.png (8 panels, red tracks gray rings, no scatter; B02 slight top divergence consistent with 68% coverage).

**3. E2E (cure-potA @ bffefb6 asserted in-job, k=5/b=3 shim, POT overlays, STEPS 9/8; stage = run_pota93_stage_AB.sbatch; sacct-direct throughout):**

| job (sacct COMPLETED 0:0, worker-verified) | A_orig | A_fresh | B_orig | B_SXC |
|---|---|---|---|---|
| 33387265 (19:09) | 8/8+15/15 | 8/8+15/15 | 9/9+15/15 (114/76) | 5/9+3/15 (464/62) |
| 33387266 (20:33) | 8/8+15/15 | 8/8+15/15 | 9/9+15/15 (114/77) | 6/9+5/15 (464/61) |
| 33387267 (17:58) | 8/8+15/15 | 8/8+15/15 | 9/9+15/15 (114/76) | 6/9+5/15 (464/62) |

Asserts per job 4x LINK-SHIM-OK + 4x LINK-FORKMAIN-ABSENT-OK + 4x DRIVER-SHIM-OK; all containers exit 0; bundle guards green in job stdout; snapshots non-empty (T-counts 8/8/9/9). Rule LANDS x3: binaries 5/6/6 vs bar 4, edges 3/5/5 vs bar 2. B_orig on this vehicle (9/9+15/15 x3, 114/76-77) reproduces 39's ORIG exactly; A arms reproduce the standing 8/8+15/15 (forests 124/70, 420/119 as in 39). R2/R3 converged to the identical solution (binary + identities decimal-exact — beam determinism, independent RUNDIRs).

**4. Why-not (recomputed identities = strict 0.35 rad / 50 mm; B_orig binary EXACTLY all 3 runs).** SXC strict: R1 4/9+2/15 (binary 5+3 — 5th sherd/3rd edge near-misses), R2/R3 6/9+5/15 binary-exact. Seated: R1 [1,4,7,9], R2/R3 [1,3,4,6,7,9]. (a) Piece 2: missed all 3 SXC runs while B_orig seats it — placed-but-flipped ~pi (ang ~3.1, tr 600–870) in all runs; rim is the weakest gate of the set (1.15/68% + 1 pre-existing jump) but green, so search-basin flip, same family as 84's P3-flip. (b) Pieces 5/8: missed all runs (rims 0.60/100%, 0.49/100% pristine — exonerated); wrong edges (1,5)/(5,8)/(2,8)/(1,8) all flipped ~1.8–3.1 rad — knock-on of the piece-2 linchpin (edges to 1,4,8 unbuildable while 2 is flipped). (c) Pieces 3/6: R1 flipped/near-miss ((1,3) 1.72/634; (6,7) 0.128/56.6 just over the 50mm line), seated R2/R3 — beam variance. (d) B01 seats in ALL 3 SXC runs via (1,4) (0.048–0.093) through its untouched forest Bl_0 — leaving it for 78 cost nothing at E2E. Seating render eye-checked: artifacts/pota93/pota93_seating_B_SXC.png (greens on gray vessel walls, red P2/P5/P8 off-vessel, no collapse).

**5. Evidence.** Spartan pota93_repro/ (census93*.py, gate93.py, render93.py, manifests, stage sbatch, 3 slurm outs) + sfs_main/pota93_run_{33387265,33387266,33387267}/ (binaries, snapshots, pota93_fetch.tgz). Laptop artifacts/pota93/: Bsel_SXC_vs_ORIG_p0.png, pota93_seating_B_SXC.png, 3 fetch tgzs + extracted fetch_*/, p93_render.py, p93_identities.txt. Poll was sacct directly (never slurm_poll.sh); repeats = 3 same-vehicle.

**6. Recommendation.** Next roll-out per census: E (guarded re-run queued behind 82's crash-cure) — same systematic-shift profile as proven D. B needs no rim re-roll (gate green, E2E above bar, within -4/-3 sherds and -12/-10 edges of the same-vehicle ORIG ceiling 9+15). Piece-2 flip + 2/5/8 cluster are search-basin data for the assembly lane; B01 forest numbers above are 78's input.
