# Swap cure roll-out (Pot I) — own census, slot exchange, gate + E2E

GOAL: MATCH AUTHOR'S INPUT.

**What to deliver:** Pot I slot-exchange cure following the landed F (81) / D (84) recipe, with I's own measured census (verify each rim fresh-S0 vs ORIG-S0/S1 within 2mm before exchanging — 89 re-census moved pieces, trust nothing listed).

**Answers:** E1

**Blocked by:** 89 (R-SWAP CONFIRMED; regime table) + 84 (D LAND: full recipe — census, byte-proofs, manifests, densify check, why-not) + 83 (census-correction precedent) + 63 (I fresh bar — read from the ticket-63 table before running).

**Status:** results-in (worker 2026-10-18 — STOPPED at densify check, no E2E; COMMIT NOTHING)

**Starting position:** Read 84 Comments (recipe) then the ticket-63 table for I's bar + ORIG denominators. Work from the t39-pipe fresh I bundle + ORIG; new scratch /data/gpfs/projects/punim2657/pota9X_repro/prep/ (X = your ticket's last digit — see Boundary); renders under laptop artifacts/pota9X/.

**Rules:** land with own census table + gate (SXC Bl_0 medians <2mm, jumps called out) + E2E x3 same-binary vs 63 bar + controls (I ORIG + A 8/8+15/15) in same runs; E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK asserts per job; min new-Bl_0 n > 50 else STOP and report (densify is a separate ticket); no commits; sacct-direct polling (never scripts/slurm_poll.sh); Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); repeats >=3.

- [ ] Own I census (measure, don't assume)
- [ ] Slot exchange + byte-proofs + gate
- [ ] E2E x3 vs bar + controls green
- [ ] Job IDs + sacct states
## Comments (worker, 2026-10-18 — COMMIT NOTHING)

**Verdict: STOPPED at densify check — no E2E run (honest stop per brief, not a forced cure).** Exchange set 28 pieces (26 GT-scored + I28/I29 no-GT), gate 27/27 GREEN, renders eye-checked — but min new-Bl_0 over GT-scored exchanged pieces is I27 n=49 <= 50, and densify is a separate ticket. Zero Slurm jobs cut, nothing to sacct-verify.

**0. Own census (login node, GT-placed, ORIG evidence-only distances).**
- Surfaces (fresh S0/S1 vs ORIG S0/S1 medians, sampled <=2500 pts): I01-I24, I26, I27 all SWAPPED (S0->S1 0.29-0.82 vs S0->S0 5.7-10.5, symmetric S1->S0 0.29-0.78 vs S1->S1 5.6-8.8); I25 CLEAN control (S0->S0 0.30, S1->S1 0.29). I28-I30 have no GT in EITHER bundle (E2E-excluded, same as D22 precedent).
- Breaklines (fresh Bl_0/Bl_1 vs ORIG Bl_0/Bl_1 med/cov, jumps>5mm): CLEAN-swapped 14 (Bl_0->exterior 0.54-1.28/57-100%, Bl_1->interior 0.53-0.83/72-100%): I01,02,03,04,05,07,08,17,22,23,24,26,27,29. FOREST/doubled-Bl_0 on swapped base 13 (Bl_0 tracks neither, r1.5-5.8/j3-23, Bl_1->interior 0.55-0.78/93-100%): I06,09,10,11,12,13,14,15,16,18,19,20,21 (+I28 no-GT: Bl_0 forest r2.41/j3, Bl_1->B0 0.69/100 clean). Controls I25 (Bl_0->B0 0.54/100), I30 (0.66/100) correct both levels, byte-identical. Partial-coverage watch (swap direction unambiguous): I02 (Bl_0->B1 82%, Bl_1->B0 72%), I13 (49/71%), I04 (Bl_0->B1 58%).
- Totals: 28 swapped, 2 controls (I25, I30). Ticket-80's I 22/30 undercounts — 83-style measure-your-own-census correction confirmed again (same class as G02/G05, D12/D14/D21).

**1. Fix (one variable: file-level slot swap, F/D recipe).** cp -a pota39_bundle_I -> /data/gpfs/projects/punim2657/pota91_repro/prep/pota91_bundle_I_SXC; 28x Bl_0<->Bl_1 + S0<->S1 (mv; Axes/Mesh/GT untouched). Byte-proofs: 28x SXC-Bl_0 md5 == fresh-Bl_1 AND SXC-S0 == fresh-S1; I25/I30 fully identical. Manifests: pota91_I_SXC_bun_md5.txt (120: Bl+S), pota91_I_SXC_BL_md5.txt (60, in-job guard format). Zero ORIG points (distances only). Densify check: min new-Bl_0 over GT-scored exchanged = I27 n=49 <= 50 -> STOP (no-GT exchanged I28 43 / I29 40 even sparser; pre-existing controls I25 67 / I30 40 out of scope).

**2. Gate (SXC Bl_0 @GT vs ORIG Bl_0, gate91.py): 27/27 GREEN, medians 0.53-0.83** (I01 0.78 ... I06 0.62/100, I13 0.78/71, I24 0.60/100, I26 0.53/100, I27 0.56/100 j0). Jumps (pre-existing Bl_1-slot content, byte-identical move, swap created nothing): I01 6.2, I02 13.3, I05 5.2, I11 8.3, I13 18.4@idx1, I14 5.2; other 21 pieces 0j. Renders eye-checked by worker: artifacts/pota91/I_SXC_vs_ORIG_p0.png (I01-I14) + p1.png (I15-I27) — red tracks gray rings, no scatter; I13 partial loop (71%) and I16/I17 self-crossing loops agree in both colors.

**3. E2E: NOT RUN.** STOPPED at densify check per brief §2 (no sbatch cut, no job IDs, no sacct states to verify). Bar for the record: 63 split-fresh I best 8/27+3/65 (R1/R2 8512) vs ORIG 25/27+59/65 x3 exact (1424/667); 39 unflagged I 9+4.

**4. Recommendation.** Densify follow-up ticket (same-loop resample only, zero ORIG points; F06 45->55 precedent in 81): I27 (49->=55), plus I28/I29 (43/40 — unscored, no GT, but live in the matching pool); then E2E x3 on this bundle + I27-dense vs bar 8+3 with I_ORIG + A 8/8+15/15 controls on cure-potA @ bffefb6, k=5/b=3. Bundle/manifests/gate/renders are ready at pota91_repro/ for direct reuse. No piece hands to 78 as uncurable (all 28 swapped pieces gate-green; I27 is sparse, not forest).

**Evidence.** Spartan pota91_repro/ (censusI91.py/txt, censusS91b.py/out, gate91.py, render91.py, prep/pota91_bundle_I_SXC/, pota91_I_SXC_{bun,BL}_md5.txt, I_SXC_vs_ORIG_p0/p1.png). Laptop artifacts/pota91/ (both PNGs, eye-checked). Tickets 39-90 and pota90/pota9X scratch untouched; 39/61/63 baselines cited from Comments. COMMIT NOTHING.

