# Swap cure roll-out (Pot C) — C02/C04 exchange, C03 control, C01 excluded

GOAL: MATCH AUTHOR'S INPUT.

**What to deliver:** Pot C slot-exchange cure per ticket 97's characterization: C02 + C04 are clean swaps (fresh Bl_0 tracks ORIG Bl_1 at 0.95/0.75mm), C03 is the clean control, C01 is fused/shredded in BOTH slots (no on-contour loop — excluded, handed to 78 with 97's numbers). Gate + E2E x3.

**Answers:** E1

**Blocked by:** 97 (Stage 1: C02/C04 swap table, C01 fused both slots, branch points; touch-split NEGATIVE) + 84 (SXC recipe) + 73/74 (S24 routes C02/C04 at 2/3+1/3 with 17mm floor — the bar to beat) + 63 (C bar/ORIG: ORIG 4/4+5/5, fresh 0/3+0/3)

**Status:** results-in (worker 2026-10-18 — COMMIT NOTHING; lead to commit)

**Starting position:** Work from the t39-pipe fresh C bundle + ORIG; new scratch /data/gpfs/projects/punim2657/pota98_repro/prep/; renders under laptop artifacts/pota98/. Own census first (verify 97's swap table: C02/C04 swapped, C03 clean, C01 fused-neither).

**Rules:** land with own census + gate (SXC Bl_0 medians <2mm, jumps called out) + E2E x3 same-binary vs bar (S24 2/3+1/3, fresh 0/3+0/3) + controls (C ORIG + A 8/8+15/15) in same runs; E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK asserts per job; C01 stays byte-identical (78's record, not forced); min new-Bl_0 n > 50 else STOP and report (densify is a separate ticket); no commits; sacct-direct polling (never scripts/slurm_poll.sh); Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); repeats >=3.

- [ ] Own C census (verify 97: C02/C04 swap, C03 clean, C01 fused)
- [ ] Slot exchange C02/C04 + byte-proofs + gate (C01 byte-identical)
- [ ] E2E x3 vs bar + controls green
- [ ] Job IDs + sacct states

## Comments (worker, 2026-10-18 — COMMIT NOTHING; lead to commit)

**Verdict: LANDS. Pure slot-exchange (SXC) on C02+C04, C01/C03 byte-identical, no densify needed, E2E 2/3+1/3 x3 bit-identical — exactly at the 73/S24 bar (2/3+1/3), above fresh (0/3+0/3), -2/-4 under same-vehicle ORIG. Controls green, asserts green, renders eye-checked. Baselines: 39 C ORIG 4/4+5/5; 73 S24 2/3+1/3 x3 (212/16-17 forests); 73 S2 0/3+0/3.**

**0. Own census (login node, ORIG evidence-only distances; each bundle at its own GT T). Surfaces fresh-S vs ORIG-S: C02 S0->O1 0.65/S1->O0 0.64, C04 S0->O1 0.60/S1->O0 0.61, C03 S0->O0 0.65/S1->O1 0.63 (all ~100%), C01 neither (S0->O1 0.86/68% partial, S1 off-lip 14-16mm). Breaklines (med/cov): C01 F0-O0 5.61/22.9 F0-O1 5.96/25.4 F1-O0 46.54/0 F1-O1 47.96/0 (FUSED/SHREDDED both slots — excluded, handed to 78 with 97's numbers, stays byte-identical); C02 F0-O0 6.07/0 F0-O1 0.95/94.4 F1-O0 0.78/98.5 F1-O1 6.00/0 (clean SWAP); C03 F0-O0 0.95/86.8 F1-O1 0.89/90.4 (clean CONTROL); C04 F0-O0 5.48/5.8 F0-O1 0.75/91.1 F1-O0 0.73/93.0 F1-O1 5.64/0 (clean SWAP). Verifies 97's table to the decimal; trust-nothing satisfied.**

**1. Fix (one variable: file-level slot swap, 81/83/84 recipe).** cp -a pota39_bundle_C -> /data/gpfs/projects/punim2657/pota98_repro/prep/pota98_bundle_C_SXC; C02+C04 Bl_0<->Bl_1 + S0<->S1 (mv, Axes/Mesh/GT untouched). Byte-proofs: 4x SXC-Bl/S == fresh opposite-slot (cmp); C01+C03 fully byte-identical (8x cmp -s: Bl_0/Bl_1/S0/S1). Manifests: pota98_C_SXC_bun_md5.txt (26 files) + pota98_C_SXC_BL_md5.txt (8, in-job guard). Source REF md5s re-verified unchanged post-run (16/16 OK, p98_source_guard.md5). Min new-Bl_0 n = 115 (C04) > 50-pt loader gate — pure SXC, no second variable. Zero ORIG points (distances only). Vehicle preflight: asm @ bffefb6 tree-clean, P22FIX/P22FIX2/C2-0.436, shim k=5/b=3, POT_C 2-line-flip verified.**

**2. Gate (SXC Bl_0 @GT vs ORIG Bl_0, jumps>5mm; gate73.py logic repointed).** C02 0.78/98.5% 0j; C04 0.73/93.0% one 6.9mm link @idx5 (pre-existing in the Bl_1-slot content — byte-identical move, swap created nothing); C03 control 0.95/86.8% intact; C01 still shredded (5.61, excluded by design). Renders eye-checked: artifacts/pota98/C98_SXC_vs_ORIG.png (red tracks gray rings tightly on C02/C04; C01 red crisscross vs gray ring; C03 ring intact).**

**3. E2E (cure-potA @ bffefb6 asserted in-job, k=5/b=3 shim, POT overlays, STEPS 8/4; stage = run_pota98_stage_AC.sbatch, 4 arms A_orig/A_fresh/C_orig/C_SXC; sbatch x3; sacct-direct throughout; first-attempt jobs 33391755/56/57 FAILED in <1min on a worker-introduced inner-script quoting typo — byte-identical vehicle otherwise; fixed lines re-validated against 73's template inner+outer bash -n, stale RUNDIRs removed, resubmitted as 33392081/82/83):**

| job (sacct COMPLETED 0:0, worker-verified) | A_orig | A_fresh | C_orig | C_SXC |
|---|---|---|---|---|
| 33392081 | 8/8+15/15 (124/70) | 8/8+15/15 (420/119) | 4/4+5/5 (125/40) | 2/3+1/3 (187/17) |
| 33392082 | 8/8+15/15 (124/70) | 8/8+15/15 (420/119) | 4/4+5/5 (125/40) | 2/3+1/3 (187/18) |
| 33392083 | 8/8+15/15 (124/70) | 8/8+15/15 (420/119) | 4/4+5/5 (125/40) | 2/3+1/3 (187/18) |

Asserts per job 4x LINK-SHIM-OK + 4x LINK-FORKMAIN-ABSENT-OK + 4x DRIVER-SHIM-OK; all containers exit 0; bundle guards green in every job; forests 187/17-18. Rule LANDS x3: sherds 2 vs S24 bar 2, edges 1 vs 1; above fresh 0/3+0/3; -2 sherds / -4 edges under same-vehicle ORIG (bit-identical x3 — deterministic binary).**

**4. Identity (login-node, p98_identity2.py; binary recompute = EXACT all 3 runs).** C_SXC seats pieces {0,1,3} = C01,C02,C04 all 3 runs; binary counts 2/3+1/3 — C01 is placed-but-wrong (shredded content, exonerated by gate), the counted seats are C02+C04 and the seated edge is 02-04 (est frame-pair within ~2deg/~11mm of GT, same pattern as 73 §3 with its 17mm translation-floor caveat — quote binary 1/3 WITH that caveat per 73/74). C_orig seats all 4 (4/4+5/5). Seating render eye-checked: artifacts/pota98/C98_SXC_seating_R1.png (green C02/C04 on gray vessel walls, orange C01 off-vessel, red-x C03 missed at GT pos).**

**5. Evidence.** Spartan pota98_repro/ (p98_census/gate/identity/render x7 scripts, sbatch + 7 slurm outs incl. 3 failed-pilot record, p98_numbers.txt, bundle + 3 md5 manifests, 2 PNGs) + sfs_main/pota98_run_{33392081,33392082,33392083}/ (binaries, snapshots, pota98_fetch.tgz in each). Laptop artifacts/pota98/ (C98_SXC_vs_ORIG.png, C98_SXC_seating_R1.png, p98_numbers.txt, 3 fetch tgzs). 39-97 lanes read-only (REF md5s re-verified post-run). Poll was sacct directly (never slurm_poll.sh); repeats = 3 same-binary. COMMIT NOTHING.**

**6. Recommendation.** C needs no rim re-roll (gate medians green, E2E at the S24 bar with ORIG reproduced exactly in-vehicle). C01 content regeneration stays with 78 (fused both slots; 97's touch-split already NULL). The 02-04 translation floor (~17mm per 73/74) is search-basin-side data for the assembly lane, same family as J's floor in T39.
