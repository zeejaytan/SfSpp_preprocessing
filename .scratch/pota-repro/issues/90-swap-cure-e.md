# 90: Swap cure roll-out 3 (Pot E) — own census, slot exchange, gate + E2E

GOAL: MATCH AUTHOR'S INPUT.

**What to deliver:** Pot E slot-exchange cure following the landed F (81) / D (84) recipe, with E's own measured census (not the ticket-80 listing alone — 89 re-census moved pieces: verify each E rim fresh-S0 vs ORIG-S0/S1 within 2mm before exchanging).

**Answers:** E1

**Blocked by:** 89 (R-SWAP CONFIRMED with prediction→check; E-10 forest exemplar; regime: slot-corrected fresh near-author except fused C) + 84 (D LAND: pure SXC recipe, own-census-first rule, 3 byte-identical controls pattern) + 83 (G SHORTFALL: census-correction precedent — ticket listing corrected by measurement) + 82 (E v2 crash-cure stands; swap roll-out cures E — this ticket IS the guarded E re-run with the fixed bundle) + 63 (E fresh bar — read the bar from the ticket-63 table before running).

**Status:** results-in

**Starting position:** Read 84 Comments (full recipe: census method, byte-proofs, md5 manifests, densify gate, why-not identities) and 89 Comments (E forest behavior, regime table) before acting. E bar and E ORIG denominators come from the ticket-63 table (same-vehicle ORIG control in same runs settles any wobble). Bundles: work from the t39-pipe fresh E bundle + ORIG; new scratch /data/gpfs/projects/punim2657/pota90_repro/prep/; renders under laptop artifacts/pota90/. FOREST pieces (if E's census shows Bl_0 forest like E-10): hand uncurables to 78's record per the 84 precedent (document, don't force).

**Rules:** land with own census table (per-piece fresh-S0 vs ORIG-S0/S1 distances + swap/control verdict) + gate (SXC Bl_0 medians <2mm, jumps called out) + E2E x3 same-binary vs 63 bar + controls (E ORIG + A 8/8+15/15) in same runs; E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK asserts per job; min new-Bl_0 n > 50 else densify becomes a second variable (own ticket if needed — do NOT bundle it here); no commits; sacct-direct polling (never scripts/slurm_poll.sh); Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); repeats >=3; SingleOverlapTest@100/RP/CheckGraph-150 stay unless a mechanism names them.

- [ ] Own E census (measure, don't assume)
- [ ] Slot exchange + byte-proofs + gate
- [ ] E2E x3 vs bar + controls green
- [ ] Job IDs + sacct states

## Comments 2026-10-19 (worker: pota90 E2E x3 COMPLETE — LANDS)

**Verdict: LANDS.** Pure-SXC slot-exchange cure (single variable) seats 22-29/31 pieces, 38-56/62 edges x3, all runs far above the 63 bar (best-fresh 7/31+4/62). Gate 29/29 <2mm. Renders eye-checked.

**Own census (login node, ORIG evidence-only, subsampled NN):** 30/31 swapped (fresh-S0 vs ORIG-S1 0.35-1.21 vs vs ORIG-S0 5-11); E18 CLEAN (S0vOS0 0.60, S1vOS1 0.56). Breaklines: 29-piece exchange set E01-06, E08-17, E19-31 (B0vOB1 0.54-1.90 clean or forest-B0 w/ clean B1vOB0 0.51-0.94). E07 EXCLUDED (B0 607pts 6.28/40% forest + B1 105pts 14.66/1% neither; S1vOS0 7.97 neither) — handed to 78. E18 left untouched (surfaces clean slots; B0 347pts 4.69/43.5% forest documented for 78, B1 exterior-correct). Borderlines kept in: E10 (B1 0.94/66% j1), E15 (0.70/87% j1), E16 (0.89/72% j0) — gate to verify.

**Fix:** `prep/pota90_bundle_E_SXC` (cp -a of t39 fresh E bundle): 29 pieces Bl_0<->Bl_1 + S0<->S1 via mv; Axes/Mesh/GT untouched. Byte-proofs: 29x SXC Bl_0 md5 == fresh Bl_1 AND SXC S0 == fresh S1 (SWAP-BYTE-OK); E07/E18 fully byte-identical both slots (CTRL-BYTE-OK). Manifests: `prep/pota90_E_SXC_bun_md5.txt` (124 lines), `prep/pota90_E_SXC_BL_md5.txt` (62). Densify check: min new-Bl_0 n=63 (E29/E31) > 50 -> pure SXC, no second variable.

**Gate** (SXC Bl_0 @GT vs ORIG Bl_0, medians/<2mm share/jumps>5mm): 29/29 <2mm — E01 0.72/99.0 j0, E02 0.70/100 j0, E03 0.70/98.1 j0, E04 0.63/100 j0, E05 0.62/100 j0, E06 0.63/100 j0, E08 0.63/100 j0, E09 0.58/100 j0, E10 0.94/66.4 j1(5.6), E11 0.56/100 j0, E12 0.60/100 j0, E13 0.66/100 j0, E14 0.66/100 j0, E15 0.70/86.7 j1(32.6), E16 0.89/72.4 j0, E17 0.65/100 j0, E19 0.60/100 j1(6.4), E20 0.58/100 j0, E21 0.61/97.7 j0, E22 0.51/100 j0, E23 0.61/100 j0, E24 0.64/100 j0, E25 0.61/100 j0, E26 0.58/100 j0, E27 0.60/100 j0, E28 0.66/95.5 j0, E29 0.66/100 j0, E30 0.63/100 j0, E31 0.67/100 j0. Post-exchange Bl_1 (old Bl_0) vs ORIG Bl_0 = 2.6-9.4 (swap direction confirmed). E07 3.11/41%, E18 4.69/43.5% untouched as documented. Panels `Esel_SXC_vs_ORIG_p0/p1.png`: full-curve overlap; E10 top-arc split, E15 gray-only dip segment visible (both j1, benign); E16 top-arc slight split (j0).

**E2E x3** (cure-potA @ bffefb6, STEPS=31 E arms, same vehicle as 84; 4 LINK-SHIM-OK + 4 DRIVER-SHIM-OK per job; sacct-direct polling):

| job | E_SXC binary | E_SXC identities 0.35rad/50mm | E_orig binary/ident | A_orig | A_fresh |
|---|---|---|---|---|---|
| 33380751 | 29/31+56/62 | 29+56, miss {E07,E15} | 31+61 / 31+61 | 8/8+15/15 | 8/8+15/15 |
| 33380749 | 26/31+49/62 | 26+49, miss {E07,E15,E23,E24,E31} | 31+62 / 31+62 | 8/8+15/15 | 8/8+15/15 |
| 33380562 | 23/31+38/62 | 22+38, miss {E07,E10,E12,E15,E23,E24,E27,E29,E31} | 30+58 / 30+58 | 8/8+15/15 | 8/8+15/15 |

Bar (63 table, best-fresh 7/31+4/62): every SXC run clears it by 15+ pieces / 34+ edges. ORIG envelope 30-31+58-62 reproduces 39's 31+61/62 (run-3 ORIG dipped to 30+58 — assembly nondeterminism, same inputs). Run-3 SXC binary-vs-identities sherd delta (23 vs 22) is definitional (edge sets identical 38/62). Wrong edges in all SXC runs are confined to incident edges of the missing pieces (E07 forest-excluded + E15 borderline present in all three; run variance in the E23/E24/E31 and E10/E12/E27/E29 clusters is assembly-side, not input-side — gate medians there are clean).

**Seating render** (`artifacts/pota90/pota90_seating_E_SXC_33380751.png`, run-1 29+56): green seated rims track the gray GT ORIG vessel; red dashed = P7/P15 off-pose (titles overlap cosmetic, template-inherited). Eye-check PASS.

**Zero-ORIG-points:** SXC inputs are fresh-side breaklines/surfaces only (byte-proofs above); ORIG used for gate scoring + same-run ORIG arm only. No commits made. Scripts/renders: Spartan `pota90_repro/` (censusB90/S90, gate90, verify90, render90, render_seat90, p90_identities, run_pota90_stage_AE.sbatch, slurm-33380*.out); laptop `artifacts/pota90/`.

**Follow-ups for lead:** (1) E07 + E15(/E18-B0) forest record -> ticket 78; (2) run-to-run variance note (SXC 38-56 edges) is assembly nondeterminism — worth one sentence in the E1 close-out on expected spread.
