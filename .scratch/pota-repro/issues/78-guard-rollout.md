# 78: Guard roll-out to doubled-contour pots

**What to deliver:** forward-cone guard + split-then-select + inner-loop select applied wherever doubled contours recur (E/I/J forests dwarf ORIG) — per-pot gate recovery toward ORIG scale.

**Answers:** E1

**Blocked by:** 75 (landed, jobs 33292678/33292704/33292722 COMPLETED: SEL arm gate GREEN on C01 — 16pts, med 1.18mm, 100% <2mm, ZERO jumps, no reordering; C_G E2E 2/2+1/1; residual miss outside C01) + 67 (two-loop check: fresh count ~=2x ORIG + parallel-loop r-h marks doubled contours) + 39 (E/I/J forests dwarf ORIG — roll wherever the check fires).

**Status:** results-in (partial: two-loop check complete, Pot E guard edge running)

**Starting position:** run the two-loop check per pot (fresh count ~=2x ORIG + parallel-loop r-h), then apply the 75 recipe (forward-cone guard + split-then-select BEFORE sequencing + inner-loop select via Surface_0/1 standoff, no ORIG) wherever it fires. Prep-side scratch copies. Zero ORIG points in any fix; ORIG evidence-only.

**Rules:** land per pot with re-walked rims gated toward ORIG (median + coverage + jumps->0, NO reordering) + E2E at/above that pot's best fresh tally x3 same-binary + controls green in same runs; renders (eye-check) + a Needs-eye staged pair per the visual-evidence lane rule on the first pot that moves; E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats >=3 per condition; no gate relaxation without a mechanism.

- [ ] Two-loop check per pot (E/I/J + others)
- [ ] Guard recipe wherever the check fires, one pot at a time
- [ ] Gate + E2E rerun x3 per pot or measured why-not
- [x] Two-loop check per pot (counts+jumps+r-h complete, fires widely, see Comments)
- [ ] Guard recipe wherever the check fires, one pot at a time (Pot E edge RUNNING 33299300)
- [ ] Gate + E2E rerun x3 per pot or measured why-not (pending edge completion)

## Comments (lead landing, 2026-10-18 — workers silent post-completion, tallies collected by lead)

Pot E: edge 33299300 COMPLETED; SEL/gate staged; E2E 33300251/52/53 all COMPLETED 0:0. E_G Binary EMPTY — Hierarchy-Batch-P78 segfaults at launch (~0.4s) on the E_G bundle while E_fresh/E_orig/A arms run fine in the same RUNDIRs. Bundle defect: E_G Bl_0 rims down to 15 pts (E10/E18/E27/E11/E01) vs 78-pt minimum in working E_BASE — sub-minimum rim in the loaded slot is the prime suspect. E_fresh 7/31+3/62 (= best fresh, x3 with third run 6/31), E_orig 30/31+59/62, A 8/8+15/15 both. Status: BLOCKED on bundle crash — successor ticket 82 (segfault cure). Two-loop check results (B–J fires) stand and are inherited by 82.
- [ ] Job IDs + sacct states (partial)

## Comments (worker, 2026-10-18 - COMMIT NOTHING; lead to commit)

**Two-loop check per pot (fresh Bl_0 n vs ORIG n + jumps>5mm; ORIG evidence-only; script pota78_repro/check78.py, login node):**
- B: 7/9 fire (B01 1069 vs 210 ratio 5.09/24j; B02 358 vs 150; B03 230 vs 143; B04 281 vs 136; B05 219 vs 131; B08 161 vs 101; B09 173 vs 75). B06 138 vs 104 ratio 1.33 no-flag; B07 99 vs 104 clean.
- C: known (C01 402 vs 211 ratio 1.91/3j FIRES; C04 191 vs 131 FIRES; C02/C03 no-flag by count but C02 same disease per 67).
- D: 10/29 fire (D03, D08, D10 649 vs 180/17j, D12 689 vs 152/21j, D14 681 vs 119/23j, D15 646 vs 121, D16 256 vs 133, D19, D21, D26). Rest ~1.0 clean.
- E: 22/31 FIRE (E04 946 vs 174/26j, E05 704, E06 720, E07 607, E08 616, E09 333, E10 750 vs 134 ratio 5.60/18j, E11-E16 all 4-6x, E17-E19, E20 130 vs 92 marginal, E21, E23, E25, E27, E28, E29; clean: E01-E03, E22, E24, E26, E30, E31).
- F: 1/7 fires (F01 258 vs 131 ratio 1.97/9j; F02-F07 clean ~1.0).
- G: 3/7 fire (G02 174 vs 112/10j; G05 153 vs 94; G06 119 vs 81; G01/G03/G04/G07 clean).
- I: 17/30 fire (I04, I06 821 vs 142/19j, I08-I16 nine pots 3-5x, I18-I21, I28 106 vs 44/3j; clean: I01-I03, I05, I07, I17, I22-I27, I29, I30).
- J: 7/12 fire (J02 858 vs 147 ratio 5.84/24j; J03 371 vs 189; J04 300 vs 186; J05 566 vs 147; J06 374 vs 133; J07 163 vs 114; J09 211 vs 74; clean: J01, J08, J10, J11, J12).
- Second half (parallel-loop r-h): 7 rep plots in /data/gpfs/projects/punim2657/pota78_repro/*_rh78.png (B01, D10, E10, F01, G02, I06, J02), all multi-run + teleports; E10 eye-checked (fresh 750 in 19 runs vs ORIG 134, black teleport chords, scattered r-h) - check FIRES on E. Script pota78_repro/rh78.py.

**Guard rollout (75 recipe, prep-side scratch only, zero ORIG, no other-ticket writes):** Pot E first (biggest forest 25022 vs ORIG 1912). Reuses 75 binary /data/gpfs/projects/punim2657/pota75_repro/build/EdgeLineExtractionHeadless (POTA75-ARM + POTA69-ARM present). Staged from pota39_E Temp+Dataset. Job 33299300 p78_edgeE (BASE/CONE/PRE) submitted from run_pota78_edge_E.sbatch; sacct RUNNING 0:0 at 00:01:08 elapsed (BASE arm on Pot_E piece 04). SEL+gate scripts staged: pota78_repro/sel78E.py (Surface_0/1 standoff inner-loop select, 31 pieces) + gate78E.py (REF/BASE/CONE/PRE/SEL vs ORIG evidence-only). Bundles pending: prep/pota78_bundle_E_{BASE,CONE,PRE,SEL}/SfS_pp.

**Renders:** Spartan /data/gpfs/projects/punim2657/pota78_repro/*_rh78.png (7 files); laptop copy artifacts/pota78/Pot_E_Piece_10_rh78.png (eye-checked). Needs-eye staged pair still pending first pot landing per visual-evidence lane rule.

**Jobs (sacct-direct, never slurm_poll.sh):** 33299300 p78_edgeE RUNNING (sacct-verified). Gate SEL + E2E x3 (cure-potA @ bffefb6, LINK-SHIM-OK + DRIVER-SHIM-OK, controls A 8/8+15/15 + E ORIG) pending edge completion - successor to run SEL, gate78E, then stage E2E x3 vs best fresh E tally (R1 5/31+3/62, R2 7/31+4/62).
