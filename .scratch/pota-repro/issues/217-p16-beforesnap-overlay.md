# 217 - P16 before/after-snap dots on the mesh (user hypothesis test)

Status: ready-for-agent
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
Draw the dots BEFORE the snap and the lane AFTER the snap on Piece 16's mesh, in one frame, so the conservator can see where each lived. Tests the user's hypothesis (m02579): BoundaryEstimation misfiled the turning sherd face as edge -- i.e. the pre-snap dots already sit ON the twisted face, not on the rim.

## Boundary
- Spartan: READ-ONLY. Fetch P16's unclustered.ply (+ boundary outputs if kept) from the 215 run work dir. Do NOT rerun the pipe, do NOT touch holder 33516830's session beyond listing, do NOT modify 214/215 records.
- Laptop: NEW outputs only under SfSpp_preprocessing/artifacts/pota217/. May reuse pota215/src/ (mesh P16 + author lanes) and pota215_render.py pattern.
- Do NOT touch: stashes, main-checkout live files, any other ticket, visual-qa.

## Constraints
- Mesh decimated for viewing; dots/lanes drawn large (209/211 lesson: sparse mesh + big markers).
- Same frame for before and after; mesh faint grey. Before dots red, after lane blue, author rim green for reference.
- After = 215 FIXED Bl0 (corrected) AND fresh Bl0 (slid lane being explained). Three lanes max, clearly labeled.
- Two viewpoints minimum (twist hides things; 209 occlusion lesson).

## Acceptance
- [ ] artifacts/pota217/p217_P16_beforesnap.png (mesh + red pre-snap dots + green author rim, 2 views)
- [ ] artifacts/pota217/p217_P16_after.png (mesh + blue walked lane(s) + green author rim, same 2 views)
- [ ] A NUMBER: share of pre-snap dots within 2mm of twisted FACE interior vs within 2mm of author rim. Verdict line: SUPPORTED (dots on face) or REFUTED (dots on rim, walk slid afterwards).
- [ ] Nothing committed by worker. Only this ticket file modified (Comments).

## Required evidence to report
- PNG paths + dot-count numbers + verdict line + Spartan source paths of fetched before-dots + job refs if anything rerun (nothing should be).
