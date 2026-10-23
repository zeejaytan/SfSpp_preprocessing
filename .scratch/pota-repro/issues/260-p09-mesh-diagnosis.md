# 260 - Pot J P09 whole-piece both-lane miss: mesh diagnosis (render, don't fix)

**What to build:** render-only diagnosis of the ticket-259 Pot J P09 whole-piece miss (both lanes: med 2.41/2.53, rev 39.2/52.2, lengths 1.3-1.5x). Draw the fresh lanes and the author lanes on the P09 mesh from >=2 viewpoints and return a verdict: UPSTREAM (split put wrong dots in the bag / mesh defective at the miss sectors, with sector locations) or WALKER (mesh+split clean, both lanes genuinely mis-walked). No fix, no preprocessing runs, no code edits, no commits to main.

**Answers:** E1

**Blocked by:** 259 (Pot J paper-arm-ON pipe + scores), 199 + 200 (rim-on-mesh render method, reused here).

**Status:** results-in
**Working in:** ticket-260 worker (2026-10-23, laptop renders + Spartan login-node reads only, no sbatch)

- [x] Renders of the P09 mesh with fresh dots + author lanes drawn on it from >=2 viewpoints
- [x] Verdict UPSTREAM or WALKER with sector-level locations
- [x] If upstream, which face/mesh region is at fault
- [x] Ticket file Status results-in + render paths (laptop + Spartan) recorded below

## Boundary (as run)
- READ-ONLY. No preprocessing runs, no code edits, no commits to main. No sbatch (login-node python reads only, seconds each).
- Main worktree touched ONLY by this ticket file. All outputs (untracked) under C:/PR/SfSpp_preprocessing-259/artifacts/pota260/ + Spartan masters in /data/gpfs/projects/punim2657/sfs-potJ-259/overlays260/.
- Method reused from 199/200: same mesh + same camera within each figure, mm axes, 20mm scale bar, eye-checked panels. MSYS2_ARG_CONV_EXCL='*' on laptop ops.
- Colours never reused for different things in one figure: mesh light-gray #CCCCCC, fresh-Bl0 blue #0072B2, fresh-Bl1 vermilion #D55E00, author-Bl0 black #222222, author-Bl1 green #009E73.

## Inputs (all read-only, md5)
- Mesh: sfs_main/original_samples/SfS_pp/Mesh/Pot_J_Piece_09_Mesh_DS.obj (md5 810009272d4ff937876b52fa5d781fcf, 5633 verts/11262 faces, laptop copy temp_download/Mesh/Pot_J/ identical size 1317317 B)
- Axes: sfs_main/original_samples/SfS_pp/Axes/Pot_J_Piece_09_Axis.xyz
- Fresh lanes: pota259_paper_Pot_J_09/Dataset/Breaklines/Pot_J/Pot_J_Piece_09_Breakline_{0,1}.pcd (md5 dc87b084 / 4ac8428b, n=95/95)
- Author lanes: sfs_main/.../Breaklines/Pot_J_Piece_09_Breakline_{0,1}.pcd (md5 ac745d3a / 485b7c19, n=74/69)
- Split-stage boundary: pota259_paper_Pot_J_09/Temp/Temp_edge/Pot_J/boundary.pcd (n=301) + cloudBreaklinePointsOnBSplineSurface.pcd (n=95)

## Comments (worker, 2026-10-23 -- render + read-only analysis, COMMIT NOTHING)

### Plain-language result
Both fresh lanes trace the wrong ring around the sherd: they are closed loops sitting on the mesh surface, but for most of their length they run several millimetres away from the author's ring, on a different line around the same rim band. The mesh itself is fine -- the author's ring and the fresh rings all sit on it (median gap to the surface under half a millimetre everywhere). The wrong turn happens before the final walk: the intermediate boundary cloud from the split/edge stage already follows the fresh (wrong) ring, not the author's. So the fault is upstream of the lane walker, in the split/edge-boundary stage -- not a broken mesh and not a walker straying off good input.

### Verdict: UPSTREAM (split/edge-boundary stage; mesh NOT defective)
- Mesh-defect leg is OUT: fresh-Bl0 mesh-prox med 0.36 max 2.77 (98.9% <2mm), fresh-Bl1 med 0.36 max 0.98 (100%), author-Bl0 med 0.41, author-Bl1 med 0.40 (both 100%). Mesh exists under both rings at the miss sectors.
- Boundary-stage test is decisive: boundary.pcd (n=301) med-to-fresh 0.61 (Bl1, 100% <2mm) / 1.37 (Bl0, 60%) vs med-to-author 2.50 / 3.17. The Bl1 wrong ring is already fully set at the boundary stage (onSurf==fresh, med 0.00); Bl0's boundary is nearer the fresh ring than the author ring but matches neither fully -- the split put the ring in the wrong place and the walk never recovered.
- Both lanes are closed loops (closure 1.8mm fresh and author), so this is not a tail/runaway of the P01/C01 class -- it is a wrong-ring miss on both sides of one small piece.

### Sector-level locations (mesh frame, mm)
- Bl0 (author idx order): uncovered author runs [18-39] low rim z 454.4-467.6, x 7.2-26.0, y 7.3-14.4 + [41-61] mid-high rim z 470.3-481.6, x 8.7-25.9, y 15.1-41.9. Fresh far from its own idx0 (only idx2-4 near author); fresh-far runs [39-70] + [72-94]. At-fault mesh region: the low-south rim band (z ~451-468) and the mid-east wall (z ~470-482) -- the split boundary rode the outer/lower edge while the author ring rides the inner line (see Bl0 VP1 panel).
- Bl1: fresh agrees with author idx0-5 then leaves at idx6. Uncovered author runs [0-12] top rim z 481.6-485.0, x 20.8-39.9, y 28.0-35.1 + [33-44] low rim z 457.6-461.9, x 4.9-20.0, y 0.4-6.7 + [49-52] z 468.5-472.4 + [54-57] z 474.1-477.1. At-fault mesh region: the top curl (z ~482-485) and the low-north rim (z ~458-462).
- In 259's terms this is the Pot J instance of the P03/C03-style miss watch (one piece, both lanes here rather than single-lane).

### Renders (6 PNGs, eye-checked; same mesh + same camera within each figure)
- Laptop: C:/PR/SfSpp_preprocessing-259/artifacts/pota260/p260_{Bl0_vp1,Bl0_vp2,Bl1_vp1,Bl1_vp2,both_vp1,both_vp2}.png + p260_render.py (rerunnable) + lane/axis/boundary inputs alongside.
- Spartan masters: /data/gpfs/projects/punim2657/sfs-potJ-259/overlays260/ (same 6 PNGs + p260_render.py).
- VP1 (elev 12, azim -75) faces the Bl0 low-south miss sector; VP2 (elev 28, azim 40) faces the Bl1 top-curl sector. All panels carry n counts, mm axes, 20mm scale bar.
- Eye-checks: both_vp1 PASS (four rings visibly separate at the low end, all on surface); both_vp2 PASS; Bl0_vp1 PASS (blue outer/lower edge vs black inner line, clean separation); Bl1_vp2 PASS (vermilion/green agree at top curl then split). Depth ambiguity of translucent renders covered by meshprox numbers above (med <=0.41 all four lanes).

### Numbers (mm; login-node recomputation, walk order)
- Bl0: nF=95 nO=74 lenF=172.3 lenO=131.9 (1.31x) fwd med 2.53 cov 32.6 / rev med 2.41 rev 39.2 (matches 259).
- Bl1: nF=95 nO=69 lenF=181.8 lenO=123.5 (1.47x) fwd med 2.41 cov 40.0 / rev med 1.78 rev 52.2 (matches 259).
- Bl1 has 1 jump idx10 jmax 14.4, but the miss is extended divergence (fresh-far runs [14-37] + [58-76] + [81-85] + [87-90]), not the jump.

### Staged for lead (judgement stays with lead)
No fix proposed, nothing committed to main (only this ticket file). Weight: one piece (P09), one 259 pipe run + deterministic rescoring + read-only login-node analysis; single-object lead, not a conclusion. Suggested next question, not a directive: whether the split-stage boundary on P09 can be re-seated without touching the walker.
