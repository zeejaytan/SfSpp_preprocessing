# 200 - Draw what the chain broke: failed pieces before/after on mesh

Status: landed (lead 2026-10-20: 5 triplets eye-checked -- B01/B09/B04 UNCHANGED-global, A07 improved-yet-fails, J03 cured-yet-unseated; B01 fresh==thinned pixel-identical)
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
User request (m04604): C01 is the PROVEN case, not the question. Draw the D chain (densify -> split -> thin -> walk) on the OTHER pots\u2019 sherds where it FAILED, to see what changed on each rim and why it failed. Same-mesh + same-camera triplets (fresh input / thinned output / author where available), mm units, scale bars, eye-checked.

Priority cases (in order -- do all that the saved data supports):
1. B01 (194/198): the killer case -- rim BYTE-IDENTICAL fresh vs thinned, yet dropped 3/3. Draw fresh loop + thinned loop + author on the B01 mesh. Expectation: the two loops coincide, proving visually that nothing on THIS rim changed and the failure is global. If they do not coincide, that itself is the finding -- report it.
2. B09 (194/198): rim-truth gate-GREEN (+0.168, cov 74/75) yet dropped 3/3. Draw fresh vs thinned vs author. What does a gate-green loop that seats nothing look like?
3. One B piece the thin actually reshaped and dropped (P3 or P4 -- 198 Comments names survivors per run; pick a piece dropped 3/3 whose rim changed most): fresh vs thinned vs author.
4. Pot A control pieces (196): pick the 1-2 pieces whose strict edges went most wrong (196 Comments attribution); fresh vs thinned vs author on their meshes.
5. J03 (193): fresh doubled (371-pt open) vs 185-v3 thin loop (178-pt closed) vs author ORIG on the J03 mesh. The clean loop that still does not seat.

## Boundary
Laptop-side rendering only. Find loops in existing artifacts (.scratch/pota194_repro/, /data/gpfs/projects/punim2657/pota194_repro/ manifests + laptop artifacts/pota194[pota194_fetch tgzs], .scratch/pota196_repro/, artifacts/pota193/, pota185/ORIG). Do NOT recompute walks or E2E, do NOT touch tracked files except this ticket. New PNGs under artifacts/pota200/ (untracked) only.

## Constraints
Same mesh + same camera within each triplet or the comparison is void. If a loop file for a case cannot be found (e.g. a 194/196 intermediate was not saved), draw the cases that exist and NAME the missing one in Comments -- do not fake it, do not substitute a different piece. COMMIT NOTHING.

## Acceptance
One triplet PNG per case above that the data supports (minimum: cases 1, 2, 5), all eye-checked, in artifacts/pota200/, plus a one-line verdict per case: what visibly changed on the rim (or did not), and what that implies about where the failure lives (this rim vs global).

## Required evidence
Comments: PNG paths + source artifact per loop (md5 where available) + eye-check per panel + per-case verdict line (changed/unchanged, rim vs global) + any case that could not be drawn and why. Final output: same, self-contained.

## Comments (worker, 2026-10-20 -- 5 triplets drawn, laptop matplotlib only; COMMIT NOTHING)

**Done: cases 1, 2, 5 (minimum) + case 4 (A07) + case-3 substitute (B04) drawn. 5 triplet PNGs (acceptance) + 5 overlays (bonus) + p200_render.py + p200_numbers.txt, all in artifacts/pota200/ (untracked). All loops sit ON their rims (mesh-prox med <=0.48mm every panel); same mesh + same camera + same limits within each triplet; 20mm scale bars; mm axes. No recomputation, no tracked-file changes besides this section.**

PNGs (triplets = acceptance panels, all eye-checked PASS -- loop rides the rim band, no float):
- artifacts/pota200/p200_B01_triplet.png (+ p200_B01_overlay.png, eye-checked PASS)
- artifacts/pota200/p200_B09_triplet.png (+ overlay) / p200_B04_triplet.png (+ overlay)
- artifacts/pota200/p200_J03_triplet.png (+ overlay) / p200_A07_triplet.png (+ overlay)

Loop sources + md5 (full bytes in p200_numbers.txt):
- B01 fresh = pota93 SXC base Bl_0 (ssh, bc1b72d8, 1069) == B01 thinned = rims_B194 Bl_0 (fetch_33485122, bc1b72d8, 1069) -- byte-identical reproduced locally; author = pota41_orig_B tgz (d90144d4, 210). Mesh temp_download/Mesh/Pot_B/Pot_B_Piece_01_Mesh.obj.
- B09 fresh SXC (ssh, b54283af, 70); thinned rims_B194 (bbe961ef, 70 -- matches 194 s4 prefix); author pota41 tgz (b4d42cce, 75).
- B04 fresh SXC (ssh, a70662c9, 127); thinned rims_B194 (91a3202f, 129 -- matches 194 s4); author pota41 tgz (91da529d, 136).
- J03 fresh .scratch/pota193_repro/J03_fresh_Bl0.pcd (35d9d41c, 371); thinned p193_J03_thin_walk.npy (95c7a6a7, 178 -- matches 193 Comments walk md5); author J03_ORIG_Bl0.pcd (e05f32c8, 189).
- A07 fresh P40 base Bl_0 (ssh, 3e2c3e8c, 63); thinned p196_A07_thin_walk.npy (ssh, 1cea1188, 61); author sfs_main/original_samples (ssh, 55939132, 65).

Numbers (mesh frame, no seating needed -- loop bboxes coincide with mesh bboxes; mesh-prox med/max + rim-truth vs ORIG + fresh-vs-thin):
- B01: prox 0.15/1.07 all three; fresh-vs-thin med 0.00 max 0.00 n>5mm 0. VERDICT (case 1): loops coincide EXACTLY -- nothing on this rim changed, failure is GLOBAL. Note: both SXC loops carry walk-order interior chords vs author's clean order, but dot sets share the rim band.
- B09: fresh-vs-thin med 0.59 max 2.17; rim-truth fresh 0.62/thin 0.79 (100% <2mm both). VERDICT (case 2): a gate-green loop that seats nothing looks like a visually perfect rim -- thin tracks fresh tracks author; drop is GLOBAL.
- B04: fresh-vs-thin med 0.57 max 2.10; rim-truth fresh 0.56/thin 0.55. VERDICT (case 3 substitute): even the BEST-falsifier rim (-0.013) drops (R3) with barely-visible smoothing -- no per-rim story. Honest gap: ticket asked for a 3/3-dropped reshaped piece; none exists (198: always-dropped = P1 untouched + P9 gate-green; P3/P4/P6/P7 survive >=1 run), so B04 (dropped 1/3, least-damaged rim) is the closest drawable witness.
- J03: fresh doubled 371 (chords, rim-truth 0.89/75.7%) vs thin clean 178 (rim-truth 0.96/90.4%) ~= author 189; fresh-vs-thin med 1.24 max 5.17. VERDICT (case 5): the thin loop IS the author ring visually, yet J03 goes placed-but-wrong -> unplaced -- blocker is search-basin, not rim.
- A07: thin IMPROVED rim-truth (0.45->0.35, 100% <2mm both); fresh-vs-thin med 0.57 max 2.13; all three clean singles. VERDICT (case 4): control piece whose rim got *better* yet A_196 collapses -- failure is GLOBAL (matches 196 s6).

Eye-checks: all 5 triplets PASS (loops on rim, doubling visible in J03-fresh only, B01-fresh==thin panel-identical); B01 overlay PASS (red/blue coincide exactly, green shares rim band).

