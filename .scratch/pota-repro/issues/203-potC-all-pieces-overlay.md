# 203 - Pot C all pieces: our trace vs author on mesh (197 follow-up)

Status: landed (lead 2026-10-20: 4 triplets + 4 overlays eye-checked; C04 rides a visibly WIDER ring than ORIG + chord -- genuine rim-level suspect for unseated C04; C01/C02/C03 share the ring)
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
User request (m04738): for ticket 197\u2019s Pot C result, draw ALL pieces -- our trace vs the author\u2019s loop overlaid on each piece\u2019s mesh. One triplet per piece (197-loop vs ORIG loop on same mesh + same camera) plus one overlay panel per piece (both loops, two colours, same axes). Eye-checked, mm units, scale bars.

## Boundary
Laptop-side rendering only. Inputs read-only: 197 bundle loops (C_fresh all Bl_0 + C_197 C01-Bl_0; see 197 Comments for .scratch/pota197_repro/ + Spartan pota197_repro/ paths and md5s), ORIG loops (same source as 197\u2019s C_orig arm), Pot C meshes (temp_download/Mesh/Pot_C/ pattern, as in 199/200). Pot C pieces: every piece in the 197 bundle (C01 + the rest -- enumerate from the bundle manifest, do not assume the count). For C01 draw BOTH our versions (fresh doubled + 197 thin) vs ORIG; for other pieces fresh vs ORIG (they are identical in both 197 arms -- state that on the panel). New PNGs under artifacts/pota203/ (untracked) only. Do NOT touch tracked files except this ticket. COMMIT NOTHING.

## Constraints
Same mesh + same camera within each piece\u2019s panels. Every loop must ride its rim band (mesh-proximity check per loop, reported). If a loop file or mesh is missing, draw the pieces that exist and NAME the missing one in Comments -- no substitution, no faking. Read 197 + 199 + 200 Comments first for exact paths, conventions, and the render scripts to reuse (p199_render.py pattern).

## Acceptance
One triplet + one overlay per Pot C piece, all eye-checked, in artifacts/pota203/, with a per-piece line: loop point counts, mesh-proximity med/max, and (for C01) which version each panel shows.

## Required evidence
Comments: PNG paths + source artifact per loop (md5 where available) + mesh-proximity numbers + eye-check per panel + any piece undrawable and why. Final output: same, self-contained.

## Comments (worker, 2026-10-20 -- laptop matplotlib only; COMMIT NOTHING)

**Done: all 4 bundle pieces drawn (bundle manifest = C01-C04 x Bl_0/Bl_1; ORIG ships C05/C06 too but they are NOT in the 197 bundle, so out of scope). 4 triplets + 4 overlays in artifacts/pota203/ (gitignored/untracked), all eye-checked PASS, script + numbers alongside. No missing piece, nothing faked.**

Conventions (199 Comments + p199_render.py seating rule; 200 triplet/overlay pattern + p200_render.py):
- Mesh frame throughout (p200-style): every bundle/ORIG pcd bbox coincides with its mesh bbox, so no seating needed -- except C01 fresh-doubled, inverse-GT seated exactly as 199 BEFORE (V=(W-t)@R, GT=.scratch/pota197_repro/GT_C01.txt), verified prox med 0.55 max 1.61 = 199's BEFORE numbers exactly.
- Same mesh + same camera + same limits within each piece (C01 elev=15 azim=-60 as 199; C02-C04 elev=20 azim=-60 as p200); 20mm scale bars; mm axes. Rerunnable: artifacts/pota203/p203_render.py; full gates in artifacts/pota203/p203_numbers.txt.

Loop sources + md5 (all 8 verified against Spartan-side truth):
- C01 fresh-doubled 439 = .scratch/pota176_repro/p176_C01_TRUE_walk.npy (md5 5f902355, inv-GT seated; == 199 BEFORE).
- C01 197-thin 204 = fetch-tgz rims_C197/Pot_C_Piece_01_Breakline_0.pcd (md5 9f561280 == Spartan pota197_C_197_BL_md5.txt; xyz == .scratch/pota197_repro/p197_true_walk_mesh.npy to 0.0001mm = pcd rounding).
- C01 ORIG 211 = .scratch/pota162_repro/.../Pot_C_Piece_01_Breakline_0.pcd (md5 bbc28cd0 == Spartan original_samples).
- C02/C03/C04 197-loop = fresh bundle Bl_0, byte-identical in both 197 arms (local md5 == Spartan bundle_C md5 == C_197 manifest: 7d48c6c7 / 9d2d6183 / 1ae68ad1); C02 267 / C03 167 / C04 191 pts, from Spartan pota197_prep/pota197_bundle_C via ssh_download to artifacts/pota203/src/.
- C02/C03/C04 ORIG Bl_0 from Spartan original_samples via ssh_download (md5 d0f2d3a8 / 22c8f0e3 / 4787a2e3); C02 221 / C03 191 / C04 131 pts.

Per-piece lines (mesh-proximity med/max per loop; rim-truth vs ORIG; eye verdict):
- C01 triplet p203_C01_triplet.png (a fresh-doubled red / b 197-thin blue / c ORIG green) + overlay p203_C01_overlay.png (all three). Prox: doubled 0.55/1.61, thin 0.62/2.40, ORIG 0.53/1.28. Rim-truth: doubled 0.95/92.0%, thin 0.64/97.1%. Eye PASS -- (a) doubled zigzag rides rim, (b) clean single + known kink-sector wiggle, (c) clean ORIG ring; overlay shows all three sharing the ring. Panel (b) version = C_197 bundle loop (the E2E-staged D output).
- C02 triplet + overlay (197-loop=fresh 267 red vs ORIG 221 green). Prox: fresh 0.47/1.25, ORIG 0.32/0.78. Rim-truth 6.07/0.0% -- red carries long walk-order interior chords across the bowl (diagonals visible in overlay) while green is a clean rim ring; dots share the rim band (no float). Eye PASS (loops on mesh; chords are walk-order artefacts, same class as 200/B01 note).
- C03 triplet + overlay (fresh 167 red vs ORIG 191 green). Prox: fresh 0.49/2.80, ORIG 0.34/1.12. Rim-truth 0.95/86.8% -- red tracks green around the same ring. Eye PASS. (This is the C01-C03 join partner side.)
- C04 triplet + overlay (fresh 191 red vs ORIG 131 green). Prox: fresh 0.45/1.17, ORIG 0.32/0.76. Rim-truth 5.48/5.8% -- red rides the rim band but on a visibly WIDER/outer ring than green over the lower-right sector, plus one walk-order chord on the right; no float. Eye PASS WITH NOTED FEATURE (different ring, not just reordering).

No piece undrawable. Reference (not drawn): pristine fresh C01-Bl_0 132-pt (md5 dcb078dd, artifacts/pota203/src/C01_fresh_Bl0.pcd) -- the pre-doubling bundle loop; ticket asked for the doubled version, which is drawn.
