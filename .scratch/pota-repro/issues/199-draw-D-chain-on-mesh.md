# 199 - Draw the D chain on the mesh: before / after / author

Status: open
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
