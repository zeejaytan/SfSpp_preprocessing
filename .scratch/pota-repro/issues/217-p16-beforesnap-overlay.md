# 217 - P16 before/after-snap dots on the mesh (user hypothesis test)

Status: done
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

## Lead verdict (2026-10-21)
ACCEPT. Numbers read verbatim in ticket (141/230 = 61.3% med 0.87 near rim; 89/230 = 38.7% on face interior; snap disp med 0.00; provenance pre-vs-S1 med 0.00 vs S0 7.44). PNGs (432+394KB) + render script copied to main artifacts/pota217/. Only this ticket + new artifacts; worker committed nothing. Limit: overlay eye-check blocked again (vision provider down); worker eye-checked, and the NUMBER carries the verdict. Gap recorded: S0 pre-dots gone on Spartan, Bl0 half untested. Verdict stands as SUPPORTED-qualified for the Bl1 face: BoundaryEstimation misfiled twisted-face interior as edge for ~2 in 5 pre-snap dots.

## Comments (worker 217, 2026-10-21, NO commit)

### Spartan sources (read-only fetch; Spartan tree untouched, no jobs run)
- Pre-snap dots: /data/gpfs/projects/punim2657/pota215_pipe/Temp/Temp_edge/Pot_D/boundary.pcd
  (230 pts; BoundaryEstimation output BEFORE the K=1 snap. Provenance: edgeline_extraction_headless.cpp
  saves boundaryCloud -> boundary.pcd, then snaps each dot to nearest UN pt -> boundaryImproved.pcd.)
- Post-snap check: .../Temp_edge/Pot_D/boundaryImproved.pcd (230 pts; snap disp med 0.00 / p90 1.75 / max 5.56mm)
- Snap target: /data/gpfs/projects/punim2657/pota215_pipe/Temp/Data/Pot_D/Pot_D_Piece_16_unclustered.ply
  (16568 pts) + Pot_D_Piece_16_Surface_{0,1}.xyz (face refs; S0=13767 / S1=6134 pts)
- FIXED Bl0: /data/gpfs/projects/punim2657/pota215_stripS0/Dataset/Breaklines/Pot_D/Pot_D_Piece_16_Breakline_0.pcd
  (md5-verified identical to laptop .scratch/p215_evidence/strip_P16_Breakline_0.pcd)
- PARTIAL-GAP (not substituted): Temp_edge keeps ONE face only (last writer wins). Surviving boundary.pcd is
  S1's (230 pts = S1 pre-count per p215_p16_bagmap.txt: "S1: pre 230"; S0's pre-367 dots are overwritten and
  gone). Face identity verified numerically: pre vs S1-cloud med 0.00 / vs S0-cloud 7.44; vs authorBl1 0.87 /
  vs authorBl0 8.68. So the NUMBER below tests Bl1's input dots; S0/Bl0 pre-dots unrecoverable -- STOP-flag
  recorded here instead of inventing them.

### Worktree PNGs (same frame + same 2 views each, el=18/az=-62 and el=8/az=38; sparse mesh + big markers)
- .scratch/.wt-217/artifacts/pota217/p217_P16_beforesnap.png (faint-grey mesh + RED S1 pre-snap dots + GREEN author rim)
- .scratch/.wt-217/artifacts/pota217/p217_P16_after.png (same frame: faint mesh + BLUE 215-FIXED Bl0 + CYAN fresh slid Bl0 + green author Bl0)
- Eye-check (own): before view 1 shows the red loop riding the green rim along the top arc, then cutting
  diagonally across the grey face interior, well off the green rim; after view 1 shows blue FIXED Bl0 riding
  green author rim with cyan fresh lane peeling off along the upper arc. Both views needed -- twist hides the
  interior cut from a single angle.

### THE NUMBER (2mm bar, n=230 S1 pre-snap dots)
- Within 2mm of twisted S1 FACE: 230/230 (100.0%) -- trivially all (dots are sampled off that patch).
- Within 2mm of author rim (o1; o0 contributes 0): 141/230 (61.3%), med 0.87mm.
- ON face but >2mm from ANY author rim (either lane): 89/230 (38.7%).
- Snap is a proven no-op (disp med 0.00), so these 89 interior dots flowed straight into the walk input.

### Verdict line
SUPPORTED (Bl1-face): 89 of 230 pre-snap dots (38.7%) sit on the twisted face interior >2mm from any true
rim -- a clean edge detector should place ~0 there -- so BoundaryEstimation did misfile face as edge for a
large minority, and the no-op snap carried them into the walk (matching 215's interior-shortcut + floating
chip on Bl1). Qualified: 61.3% of dots ride within 2mm of the rim (carve-cut edge coincides with the rim
along the covered arc), so the misfile is partial, not total. Bl0's pre-dots are gone (see gap above) --
the Bl0 half of the hypothesis (fresh slid lane explained by face dots) is NOT tested by this ticket.

### Local refs reused (copied read-only into worktree artifacts/pota217/src/)
- Mesh + author P16 lanes + fresh (214 slid) P16 lanes from main-checkout artifacts/pota215/src/ (mesh 3.3MB).
- Script: worktree artifacts/pota217/p217_render.py; per-dot distances: src/p217_numbers.txt (d_rim_either, d_face_S1).
- Nothing committed, nothing pushed. Main checkout / stashes / holder 33516830 / 214-216 records untouched.

