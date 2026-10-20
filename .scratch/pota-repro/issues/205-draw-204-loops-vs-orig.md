# 205 - Draw 204's D-loops: per-piece triplets vs ORIG

Status: landed (lead 2026-10-20: 4 triplets + 4 overlays + C03 strip eye-checked, verdicts confirmed -- C01 HOLDS, C02 CURED, C03 REGRESSED with mechanism visible, C04 CURED)
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
Render what the 204 D chain did to every Pot C piece BEFORE the E2E lands, so the eye can judge the repair against the author's answer key while the jobs run. Same panel pattern as 199/200/203.

## Method (laptop-only render leg; COMMIT NOTHING)
1. Inputs: the four 204 D-loops (staged under .scratch/pota204_repro/ + the 204 bundle -- ask the 204 ticket/worker paths; C01 filed md5 matches 197's exactly), the four fresh loops, the four ORIG loops (answer key, draw-only). Mesh: C01 mesh as in 199/203 for the overlay.
2. Per piece (C01, C02, C03, C04): triplet (a) BEFORE = fresh loop on mesh, (b) AFTER = 204 D-loop on mesh, (c) AUTHOR = ORIG loop on mesh. Same viewpoint/scales as 203's triplets so they sit side by side. Plus one overlay panel per piece (fresh + D-loop + ORIG, three colours, as in 203).
3. Per-step panels for ONE piece only (C03 -- the interesting one: split leg holds at ~1.2-1.5mm yet output sits 6.5mm off per 204 worker): densify / split / thin / walk stages overlaid, 199 d/d2/e/f/g pattern.
4. Name-don't-fake: any loop file missing or unreadable is named, never synthesized. 203 already covers C01-both-versions; do not redo it, cite it.
5. Eye-check every PNG yourself (read_image) before reporting: state what changed per piece in one line each (closer to author? new damage? untouched?).

## Acceptance
4 triplets + 4 overlays + C03 per-step strip under artifacts/pota205/, all eye-checked by worker, paths + one-line verdicts per piece in Comments + final output. No E2E, no bundle, no sources touched.

## Required evidence
Ticket Comments + final output: PNG paths, per-piece one-line verdicts (BEFORE vs AFTER vs AUTHOR), any named-missing inputs.

## Comments (worker -- append below, do not edit above)

**Done (worker, 2026-10-20 -- laptop matplotlib only; COMMIT NOTHING). 4 triplets + 4 overlays + C03 strip in artifacts/pota205/ (untracked), all eye-checked PASS, script + numbers alongside.**

Panels (same mesh + same camera + same limits within each piece; mesh frame throughout; 20mm scale bars; mm axes; rerunnable: artifacts/pota205/p205_render.py; gates in artifacts/pota205/p205_numbers.txt):
- artifacts/pota205/p205_C01_triplet.png + p205_C01_overlay.png
- artifacts/pota205/p205_C02_triplet.png + p205_C02_overlay.png
- artifacts/pota205/p205_C03_triplet.png + p205_C03_overlay.png
- artifacts/pota205/p205_C04_triplet.png + p205_C04_overlay.png
- artifacts/pota205/p205_C03_steps.png (per-step strip: densify / split / thin / walk-final-vs-ORIG)

Loop sources + md5 (BEFORE = pristine fresh bundle Bl_0; AFTER = 204 D-loop true_seated; AUTHOR = ORIG Bl_0):
- BEFORE fresh = .scratch/pota204_repro/FRESH_C0X_Bl0.pcd (md5 8: dcb078dd / 7d48c6c7 / 9d2d6183 / 1ae68ad1); C01 n=132, C02 n=267, C03 n=167, C04 n=191. Note: BEFORE here is the pristine 132-pt C01 loop, NOT 203's 439-pt doubled walk (that panel is 203's; cited, not redone).
- AFTER D = .scratch/pota204_repro/p204_C0X_true_seated.npy (md5 8: 32b80e8b / 550a03d6 / 355ee5bf / e1f4299c); C01 n=204, C02 n=231, C03 n=191, C04 n=126. C01 AFTER is byte-identical to 203's panel-(b) 197-thin loop (p204 log: C01-TRUE-vs-197 maxdiff 0.0); the other three are new in 205.
- AUTHOR = ORIG Bl_0: C01 .scratch/pota162_repro/.../Pot_C_Piece_01_Breakline_0.pcd (bbc28cd0, 211); C02-C04 .scratch/pota204_repro/ORIG_C0X_Bl0.pcd (d0f2d3a8 / 22c8f0e3 / 4787a2e3; 221/191/131).
- C03 strip extras: densify bag = .scratch/pota176_repro/p176_C03_F0/F1_bag.npy (322+221=543, dupes 0); split TRUE/OUTER re-derived by the verbatim p204 rule (counts 503/40/fold 418 asserted EXACT vs p204 log); thin centreline = p204_C03_true_centreline.npy (191).
- Meshes: temp_download/Mesh/Pot_C/Pot_C_Piece_0X_Mesh_DS.obj (same files as 199/203). Views: C01 elev=15 azim=-60 (as 199/203-C01); C02-C04 elev=20 azim=-60 (as 200/203).

Numbers (mesh frame; mesh-prox med/max per loop; rim-truth vs ORIG):
- C01: prox fresh 0.91/2.54, AFTER 0.62/2.40, ORIG 0.53/1.28. Rim-truth: fresh 3.90/31.1%, AFTER 0.64/97.1%. Eye PASS -- (b) AFTER and (c) ORIG coincide along the whole rim (overlay: blue/green one line; known kink-sector wiggle shared); (a) BEFORE is sparse with a long chord.
- C02: prox fresh 0.47/1.25, AFTER 0.48/2.49, ORIG 0.32/0.78. Rim-truth: fresh 6.07/0.0%, AFTER 0.83/72.7%. Eye PASS -- AFTER is a clean single loop tracing ORIG's ring (right tall-sector wiggle follows ORIG's kink); fresh's bowl-crossing chords are gone.
- C03: prox fresh 0.49/2.80, AFTER 2.54/3.90, ORIG 0.34/1.12. Rim-truth: fresh 0.95/86.8%, AFTER 6.52/7.3%. Eye PASS WITH NOTED REGRESSION -- AFTER runs a lower/inner ring across the left + bottom (overlay: blue inside red/green), rejoining only at the tall neck right; it is on/near the wall (no float) but it is NOT the author's rim. Strip (a)->(d) shows why: densify bag holds TWO strands (outer F0 ring + inner F1 ring); split put both into TRUE (503 = inner 85 + fold 418, fold share 77%); thin averaged them into an interior ring that the walk then closed cleanly.
- C04: prox fresh 0.45/1.17, AFTER 0.51/1.40, ORIG 0.32/0.76. Rim-truth: fresh 5.48/5.8%, AFTER 0.70/97.6%. Eye PASS -- AFTER cures 203's wider-ring finding: blue tracks green's ring all round; fresh's outer ring + right-side chords are gone.

Per-piece one-line verdicts (BEFORE vs AFTER vs AUTHOR):
- C01: D holds the proven ring (AFTER == 197-thin == author, 97.1%); BEFORE shown here is the sparser pristine loop, not 203's doubled walk.
- C02: D cures the chord disease -- fresh 0% in-word coverage becomes a clean author-tracking ring (72.7%).
- C03: D REGRESSES the one piece that was already good -- fresh tracked the author (86.8%) but the split pooled inner+fold and thinned an interior ring (7.3%).
- C04: D cures the wider-ring + chord piece -- fresh 5.8% becomes 97.6% on the author's ring.

No missing inputs; nothing faked. Split TRUE/OUTER clouds are verbatim-rule re-derivations with exact count asserts, not saved intermediates (named as such).

## Lead eye-check (2026-10-20)
Viewed all 5 PNGs. C01(b) traces C01(c) all round. C02(b) clean, kink included, chords gone. C03(b) rides lower/inner vs C03(c), rejoins at tall neck; steps strip (a) shows the two strands (outer cyan + inner magenta ring) that split pooled into TRUE and thin averaged -- regression mechanism confirmed visually, genuine rim-level miss not a bad panel. C04(b) clean and on the author ring, chords gone. Worker verdicts stand. E2E (204, jobs 33499348/49/50) still running; these pictures are the pre-score record.
