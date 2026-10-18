# Swap cure roll-out (Pot J) — own census, slot exchange, gate + E2E

GOAL: MATCH AUTHOR'S INPUT.

**What to deliver:** Pot J slot-exchange cure following the landed F (81) / D (84) recipe, with J's own measured census (verify each rim fresh-S0 vs ORIG-S0/S1 within 2mm before exchanging — 89 re-census moved pieces, trust nothing listed).

**Answers:** E1

**Blocked by:** 89 (R-SWAP CONFIRMED; regime table) + 84 (D LAND: full recipe — census, byte-proofs, manifests, densify check, why-not) + 83 (census-correction precedent) + 63 (J fresh bar — read from the ticket-63 table before running).

**Status:** results-in (worker 2026-10-18 — LANDS; renders eye-checked; sacct-verified)

**Starting position:** Read 84 Comments (recipe) then the ticket-63 table for J's bar + ORIG denominators. Work from the t39-pipe fresh J bundle + ORIG; new scratch /data/gpfs/projects/punim2657/pota9X_repro/prep/ (X = your ticket's last digit — see Boundary); renders under laptop artifacts/pota9X/.

**Rules:** land with own census table + gate (SXC Bl_0 medians <2mm, jumps called out) + E2E x3 same-binary vs 63 bar + controls (J ORIG + A 8/8+15/15) in same runs; E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK asserts per job; min new-Bl_0 n > 50 else STOP and report (densify is a separate ticket); no commits; sacct-direct polling (never scripts/slurm_poll.sh); Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); repeats >=3.

- [ ] Own J census (measure, don't assume)
- [ ] Slot exchange + byte-proofs + gate
- [ ] E2E x3 vs bar + controls green
- [ ] Job IDs + sacct states

## Comments (worker, 2026-10-18 — COMMIT NOTHING)

**Verdict: LANDS. Pure slot-exchange (SXC) on 8 pieces, 4 controls byte-identical, no densify needed, E2E 7/10+13/18 x3 bit-identical — far above the 63 bar (R1/R2 2/10+1/18, R3 0/10+0/18), at same-vehicle ORIG level. Controls green, asserts green, renders eye-checked. Baselines cited: 63 J ORIG 8/11+16/21 x3 exact (731; pruned 196-200); 63 split-flag fresh J R1/R2 2/10+1/18, R3 0/10+0/18 (1873; pruned 45/54/36); 80 J census (9/12 swapped surfaces: J04-J07,J10-J12 + J02/J09 family).**

**0. Own census (login node, ORIG evidence-only distances; surfaces AND breaklines both levels, @GT where GT exists).** Fresh S0 vs ORIG S0/S1: J01 0.30/5.62, J03 0.31/5.63, J08 0.31/10.18 (controls, match S0); J02 5.51/0.30, J04 5.63/0.30, J05 5.25/0.30, J06 5.35/0.30, J07 5.33/0.30, J10 5.03/0.31, J11 5.11/0.31, J12 5.34/0.32 (swapped, match S1); J09 4.12/2.78 no-GT-either-side (ambiguous, left untouched). Fresh Bl table (vs ORIG Bl0/Bl1 med/cov/jumps>5): J01 Bl0 1.15/70/j1 Bl1 0.85v1/99 (control, doubled content noted below); J02 Bl0 5.95/15+2.55/47 j24 FOREST-Bl0, Bl1 0.72/98/j1 clean-interior (D12/D14 pattern: surface-swapped w/ clean interior loop in Bl1 slot — same slot-exchange cures it, forest content moves to runtime-inert Bl1 slot); J03 Bl0 0.89/76/j11 Bl1 0.70v1/100 (control); J04 Bl0 0.73v1/96/j10 Bl1 0.65v0/100; J05 Bl0 1.14v1/70/j4 Bl1 0.68v0/100; J06 Bl0 0.85v1/90/j5 Bl1 0.59v0/100; J07 Bl0 0.72v1/100/j12 Bl1 0.57v0/100; J08 Bl0 0.59/98/j0 Bl1 0.70v1/91 (control); J09 Bl0 3.16/9+3.87/42 j5, Bl1 n=22 3.08/41 (no GT, un-gateable, untouched); J10 Bl0 0.63v1/100/j0 Bl1 0.75v0/100; J11 Bl0 0.68v1/92/j0 Bl1 0.55v0/100; J12 Bl0 0.63v1/100/j0 Bl1 0.56v0/100. Exchange set = 8 (J02,J04-J07,J10-J12); controls J01/J03/J08/J09 byte-identical. No piece handed to 78 as uncurable — J02 forest-Bl0 content documented here (pre-exchange r5.95/j24 tracking neither); J01 interior curl + J03 droop (pre-existing fresh content, controls) noted for 78's record.

**1. Fix (one variable: file-level slot swap, F/G/D recipe).** cp -a pota39_bundle_J -> /data/gpfs/projects/punim2657/pota92/prep/pota92_bundle_J_SXC (moved under prep/ to match the stage layout after the void-batch path lesson below); 8 pieces Bl_0<->Bl_1 + S0<->S1 (mv, Axes/Mesh/GT untouched). Byte-proofs: 8 x (SXC Bl_0 md5 == fresh Bl_1, SXC S0 md5 == fresh S1); 4 controls fully byte-identical. Manifests: prep/pota92_J_SXC_bun_md5.txt (48: Bl+S) + pota92_J_SXC_BL_md5.txt (24, in-job guard). Densify check: min new-Bl_0 n = 53 (J11/J12) > 50-pt loader gate — pure SXC, no second variable. Zero ORIG points (distances only). Vehicle preflight: asm @ bffefb6 tree-clean, P22FIX/P22FIX2/C2-0.436, shim k=5/b=3, POT_J overlay 2-line-flip verified pre-submit (4-line diff + POT_J active).

**2. Gate (SXC Bl_0 @GT vs ORIG Bl_0, jumps>5mm): medians 8/8 <2mm.** J02 0.72/98.4/1j(14.6), J04 0.65/100/0j, J05 0.68/100/0j, J06 0.59/100/0j, J07 0.57/100/1j(6.0), J10 0.75/100/0j, J11 0.55/100/0j, J12 0.56/100/0j. Controls untouched: J01 1.15/69.7/1j, J03 0.89/75.7/4j, J08 0.59/98.5/0j. Jumps are pre-existing fresh-Bl1-slot content (byte-identical move, swap created nothing); both jumping pieces (J02, J07) seat in all 3 E2E runs, so benign. Cross-check: post-exchange Bl_1 (old Bl_0) vs ORIG Bl_0 = 4.9-11.4 confirms swap direction. Renders eye-checked: artifacts/pota92/Jsel_SXC_vs_ORIG.png (11 panels; exchanged red tracks gray ring, no scatter; J01 panel shows the pre-existing interior red curl, J03 the pre-existing droop — both controls, untouched).

**3. E2E (cure-potA @ bffefb6 asserted in-job, k=5/b=3 shim, POT overlays, STEPS 12/8; stage = run_pota92_stage_AJ.sbatch; sacct-direct throughout):**

| job (sacct COMPLETED 0:0, worker-verified) | A_orig | A_fresh | J_orig | J_SXC |
|---|---|---|---|---|
| 33387858 (0:26) | 8/8+15/15 | 8/8+15/15 | 8/11+16/21 (202) | 7/10+13/18 (122) |
| 33387859 (0:19) | 8/8+15/15 | 8/8+15/15 | 7/11+12/21 (199) | 7/10+13/18 (125) |
| 33387860 (0:25) | 8/8+15/15 | 8/8+15/15 | 8/11+16/21 (198) | 7/10+13/18 (122) |

Asserts per job 4x LINK-SHIM-OK + 4x LINK-FORKMAIN-ABSENT-OK + 4x DRIVER-SHIM-OK; all containers exit 0; bundle guards green in job stdout (post-fix layout); forest hypotheses 125/122/122. Rule (b) LANDS x3: sherds 7 vs bar 2, edges 13 vs bar 1 — J_SXC bit-identical tallies AND identities all 3 runs. J_orig on this vehicle (7-8/11 + 12-16/21) reproduces 63's ORIG (8/11+16/21) within run-to-run search wobble — the SXC sits -1/0 sherds, -3/+1 edges under it.

**4. Why-not (recomputed identities = binary EXACTLY all 3 runs, p92_identities.py = p84 logic, 0.35 rad/50 mm).** SXC all 3 runs seats [1,2,4,5,6,7,10] via 13 edges incl. (2,4),(2,5),(2,6),(2,10),(4,10),(5,10) (all <0.15 rad/<30 mm). (a) Piece 3: control J03, placed-but-wrong all 3 runs (ang ~2.3-2.5, trans ~450-990) while J_orig seats it via (1,3),(3,6),(3,7) — same rim file both arms (J03 untouched), so contextual search-basin miss, not rim quality; rim-side note: J03 Bl0 carries 4 pre-existing jumps. (b) Pieces 8/11/12: missed by BOTH J_orig and J_SXC (all runs) — small-rim frontier (n = 66/53/53), not a cure deficit. (c) Piece 9: no GT in either bundle (excluded, both arms) — left byte-identical, documented. Rims exonerated: every seated SXC edge recomputes <0.15 rad / <30 mm. Seating render eye-checked: artifacts/pota92/pota92_seating_J_SXC.png (green P1/2/4/5/6/7/10 on-vessel walls, red dashed P3/P8/P11/P12 off-vessel, no collapse).

**5. Evidence.** Spartan pota92/ (bundle, censusJ92/gate92/render92.py, stage sbatch, 6 slurm outs) + sfs_main/pota92_run_{33387858,33387859,33387860}/ (binaries, snapshots, pota92_fetch.tgz). Laptop artifacts/pota92/ (Jsel_SXC_vs_ORIG.png, pota92_seating_J_SXC.png, 3 fetch tgzs + extracted fetch_*/, p92_identities.py + outputs, p92_render.py). Poll was sacct directly (never slurm_poll.sh); repeats = 3 same-binary (counting only the valid batch below).

**6. Process note (honest sacct record).** First submission batch 33387270/271/272 (sacct COMPLETED 0:0, ~22 min) is VOID and does not count toward x3: the J_SXC arm never ran in any of them — the sbatch inherited D's ${P92}/prep/... DS path but the bundle sat directly under pota92/ (no prep/), so apptainer mount failed (no such file or directory) for exactly the J_SXC arm; A + J_orig arms in that batch were green (A 8/8+15/15 x2, J_orig 8/11+16/21). The in-job md5 guard passed vacuously on the missing dir (cd-fail falls through to the || intact echo — template flaw worth fixing in the next ticket's sbatch: assert [ -d DS ] first). Fix: moved the bundle to prep/ (byte-identical, both manifests re-verified green post-move), resubmitted unchanged otherwise → 33387858/859/860 all 4 arms green. The as-submitted first-batch sbatch + outs stay on disk as the true record.

**7. Recommendation.** Next roll-out: B (8/9 swapped, small, clean) per census order — E stays queued behind 82's segfault-cure, C stays with 79 (shape), I waits on 78/82. J needs no rim re-roll (gate medians green, forest 125/122-scale, E2E at ORIG level). Piece-3 contextual miss + small-rim 8/11/12 frontier are search-basin data for the assembly lane; J01-curl/J03-droop pre-existing control content is 78's record, not a reopen.

