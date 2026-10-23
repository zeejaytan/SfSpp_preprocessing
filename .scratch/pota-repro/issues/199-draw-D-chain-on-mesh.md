# 199 - Draw the D chain on the mesh: before / after / author

Status: landed (lead 2026-10-20: all 8 panels eye-checked incl. side-by-side -- (b) AFTER traces the same ring as (c) AUTHOR; per-step overlays complete, no missing step)
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
User request (m04539): for the D chain (143 densify -> 175 split -> 185 thin -> 144 recovery) show EACH step applied and how it changed the edgeline, drawn OVERLAID ON THE MESH: before, after, and author side by side.

Subject: Pot C C01 (the rim the chain was proven on). Three panels minimum, same mesh + same camera:
(a) BEFORE: fresh doubled input (439-pt zigzag walk, ticket 176/182) overlaid on the C01 mesh;
(b) AFTER: the D-chain output (185-v3 thinned loop + M144 walk) overlaid on the C01 mesh;
(c) AUTHOR: ORIG loop overlaid on the same mesh.
Plus per-step overlays where the data exists: after-densify strip, after-split face clouds, after-thin loop -- each on the mesh, so the user can see what each step did to the line.

## Boundary
Laptop-side rendering only (matplotlib). Find the C01 mesh + the three loops in existing artifacts (pota176/180/185/186 dirs, ticket Comments of 176/182/185); do NOT recompute walks, do NOT touch tracked files except this ticket. New PNGs under artifacts/pota199/ (untracked) only.

## Constraints
Same camera + same mesh for (a)/(b)/(c) or the comparison is void. Mark scales (mm). Eye-check every panel: the line must sit ON the rim, not float. COMMIT NOTHING.

## Acceptance
Panels (a)/(b)/(c) + per-step overlays that the data supports, all in artifacts/pota199/, eye-checked, paths listed in Comments.
Honest gaps allowed: if a step\u2019s intermediate (e.g. post-densify strip) was not saved anywhere, say so in Comments instead of faking it.

## Required evidence
Comments: panel paths + which artifact each loop came from (md5 where available) + eye-check verdict per panel + any step that could not be drawn and why. Final output: same, self-contained.

## Comments (worker, 2026-10-20 -- laptop matplotlib only; COMMIT NOTHING)

**Done: all drawable steps drawn. 8 PNGs in artifacts/pota199/ (untracked), eye-checked, scripts + numbers alongside.**

Panels (mesh = temp_download/Mesh/Pot_C/Pot_C_Piece_01_Mesh_DS.obj, 11875v/23114f):
- p199_a_before.png -- (a) BEFORE: .scratch/pota176_repro/p176_C01_TRUE_walk.npy, 439 pts, md5 5f902355dd99a4fe35885bf596193733. Rim-truth med 0.95 <2mm 92.0%; mesh-prox med 0.55 max 1.61mm. Eye: PASS -- red zigzag doubled line rides the rim band, doubling visible, sits on mesh.
- p199_b_after.png -- (b) AFTER: .scratch/pota185_repro/p185_thin_walk_v3.npy, 204 pts, md5 57e7077cec514c5e7511de63547bf59. Rim-truth med 0.64 <2mm 97.1%; mesh-prox med 0.62 max 2.40mm. Eye: PASS -- clean single loop on rim (known kink-sector wiggle at right curl, same class as 180/186 qualifications).
- p199_c_author.png -- (c) AUTHOR: .scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd, 211 pts (seated via Pot_C_Piece_1_T.txt). Eye: PASS -- clean green loop on rim.
- p199_abc_sidebyside.png -- (a)/(b)/(c) one figure, same seated mesh + same camera (elev=15 azim=-60) + same limits, 20mm scale bar, axes in mm. Eye: PASS.
- p199_d_densify.png -- after-densify direct parent of the split: .scratch/pota173_repro/p173_bag.npz BAG 753 dots (seated). Eye: PASS -- two strands visible (the width the split later separates).
- p199_d2_densify143.png -- ticket-named densify output: .scratch/pota143_repro/p143_G314.npy, 314 dots, mesh-prox med 0.75 max 1.70mm [mesh frame, same relative camera; rigid-T from seated]. Eye: PASS -- dots on rim band, denser cover incl O37 region.
- p199_e_split.png -- after-split face clouds (175 parent-surface rule re-derived ORIG-free from 173 bag + mesh tris: TRUE inner+fold 476 red + OUTER 277 blue; counts exact). Eye: PASS -- red/blue separate cleanly along the rim.
- p199_f_thin.png -- after-thin: .scratch/pota185_repro/p185_centreline_v3.npy, 204 dots + closed polygon (pre-walk). Eye: PASS -- single centreline on rim.
- p199_g_recovery144.png -- recovery: .scratch/pota144_repro/p144_seq_m144.npy (322 steps, 310 unique) indexed into p143_G314.npy (same order asserted by p144_step1.py, W==314), purple, [mesh frame]. Eye: PASS WITH NOTED FEATURE -- line tracks rim; diagonal interior chords are the 12 licensed retreats (max 21.56 <= envelope 21.72, 144 Comments s2), not float.
- p199_numbers.txt (all gates/proximity/md5s) + p199_render.py + p199_render2.py (rerunnable).

Frames: (a)/(b)/(c)/(d)/(e)/(f) seated (Vg=V@R.T+t); (d2)/(g) mesh frame (V as-shipped, G314 native). Same geometry up to the rigid T; same relative camera throughout.

Honest gaps: NONE drawable missing. 143's Pool-A/Pool-B admit lists and 144's latch/firing record are start-state diagnostics, not geometry -- nothing to overlay. 144's walk is on the older 314-bag generation (branch), NOT the parent of AFTER: AFTER's order already IS a verbatim walk_m144 product on the thinned centreline (185 ticket), so thin+M144 are jointly embodied in panel (b); panel (g) shows the 144-branch recovery separately. No intermediates faked; nothing recomputed (all loops byte-identical to staged artifacts); tracked diff = this Comments section only.


**Evidence-path note (2026-10-23):** paths under .scratch/pota1xx_repro/ and .scratch/pota22x/ cited above were removed by the scratch cleanup of this date (untracked intermediates; not recoverable). The numbers, quotes and verdicts in this ticket stand as recorded -- do not chase those paths or re-derive from them.
