# 203 - Pot C all pieces: our trace vs author on mesh (197 follow-up)

Status: open
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
