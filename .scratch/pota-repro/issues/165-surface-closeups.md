# Close-up shaded renders: what the surface looks like at the false loop vs the rim

GOAL: JUDGE THE BEND QUESTION WITH EYES, NOT TILT NUMBERS.

**Answers:** E1

**Blocked by:** 164 (tilt numbers say false loop flatter; user disputes without seeing the surface) + 161 (mesh-overlay pattern, but mesh rendered as faint wireframe -- shape unreadable).

**Status:** results-in

## CORRECTION (user, 2026-10-19; lead misread retracted)

The 'daylight through a hole' was a translucency/alpha rendering artifact -- the C01 mesh is SOLID and WHOLE. The lead's hole-rim verdict is RETRACTED; the 'hole-rim third class' claim is CONTESTED, not banked. Standing questions: (a) what are the 4 blue boundary loops traced in the mesh file, if the mesh is whole; (b) do FAR dots coincide with real mesh boundary edges, verified on the FILE not on renders. Lesson: renders for eye-judgement must be OPAQUE -- translucency fabricates holes.

**User's demand (verbatim):** look at how the surface looks like AS AN IMAGE. I.e. shaded, lit renders (not wireframe, not scatter) of the C01 piece surface at: (a) the false-loop region (top, where the FAR/red dots form the parallel loop); (b) the true-rim region (where NEAR/green dots ride the ORIG loop). Same lighting, close-up, several angles each; veto dots + ORIG loop overlaid so the eye can connect dots to ground. The question the eye must answer: does the surface take a sharp turn (junction/crease) at the false loop, and how does that compare with the rim's ground?

**What to deliver:** close-up shaded renders artifacts/pota165/ (mesh with lighting + dots + ORIG overlay, labeled panels), eye-checked, with the worker's own read of what the surface does at each site. No verdict on the bend debate required -- the PICTURES are the deliverable; judgement stays with the lead + user.

**Starting position:** 161 Comments + .scratch/pota157_repro/p157_render.py (mesh handling, frames); 162/163/164 Comments (FAR vs NEAR dot sets, regions). New scratch pota165_repro/.

**Rules:** read-only over tickets 39-164; render-only (laptop-side if data fetchable, else minimal Spartan read); COMMIT NOTHING; Comments-only ticket edits; label every panel (region, camera, colors).

- [x] false-loop region close-ups (shaded, several angles, dots + ORIG)
- [x] true-rim region close-ups (same lighting/scale, dots + ORIG)
- [x] worker's read of the surface shape at each site

## Comments (worker, 2026-10-20, render-only)

Run: `python .scratch/pota165_repro/p165_render.py` (repo root, system python numpy+matplotlib+scipy, no env change, no science). All asserts pass: mesh Pot_C_Piece_01_Mesh_DS.obj 11875 verts/23114 faces; T bit-identical to TF (140 frame verbatim, mesh Vg=V@TF+t, veto c0 seated with T, ORIG loops already gate-frame); c0 n=364 with NEAR<2mm n=86 / MID n=187 / FAR>5mm n=91 vs G=Bl_0+Bl_1 -- counts reproduce 160/162 exactly. COMMITTED NOTHING; tickets 39-164 untouched (read-only); no builds, no Slurm (nothing for sacct).

Renders (all under artifacts/pota165/, eye-checked: shading reads, loops/dots/boxes correctly placed, titles+legends+per-panel kept-counts live, no empty axes):
- artifacts/pota165/p165_overview.png -- full mesh, all 364 dots + ORIG Bl_0 (black, 211) + Bl_1 (orange, 230) + hole rims (blue) + red/lime site boxes (no depth cull)
- artifacts/pota165/p165_falseloop_1_e10_a-120.png -- FALSE LOOP 1/3, faces the loop sheet (near-side MID 24 / NEAR 36 / FAR 45)
- artifacts/pota165/p165_falseloop_2_e15_a-90.png -- FALSE LOOP 2/3 (near-side MID 27 / NEAR 40 / FAR 49)
- artifacts/pota165/p165_falseloop_3_e40_a-100.png -- FALSE LOOP 3/3, from above (near-side MID 34 / NEAR 31 / FAR 34)
- artifacts/pota165/p165_rim_1_e10_a180.png -- RIM 1/3, faces the rim span (near-side MID 42 / NEAR 22 / FAR 2)
- artifacts/pota165/p165_rim_2_e10_a150.png -- RIM 2/3 (near-side MID 39 / NEAR 22 / FAR 2)
- artifacts/pota165/p165_rim_3_e35_a165.png -- RIM 3/3, from above (near-side MID 40 / NEAR 26 / FAR 0)
- artifacts/pota165/p165_frame.txt -- frame/provenance note (light, translucency, cull, sites, cameras)

Method (suffix to the ticket brief): same fixed object-space light every panel (directional L=[0.45,0.85,0.40] + 0.55 ambient, per-face Lambert); mesh translucent alpha=0.45 because veto dots sit med 0.6-0.8mm UNDER the DS facets (solid mesh buries them; only ~1/3 in front from any camera); dots image-plane depth-culled per camera (kept iff within 3mm behind the local front surface, pixel disc 2.5mm) so far-wall ghosts can't misregister -- per-panel kept counts burned into each panel. Cameras face each site (azim sweep: false-loop sheet faces -90..-120, rim span faces 150..180 -- opposite sides). Script: .scratch/pota165_repro/p165_render.py (+p165_frame.txt).

Per-panel description:
- FALSE 1/3 (e10 a-120): red FAR ring circles a blue mesh-boundary loop with white background showing through the hole; sheet around the ring reads smooth; ORIG black/orange loops ride the wall edges left/bottom/right with green NEAR dots on them.
- FALSE 2/3 (e15 a-90): same ring seen side-on -- red dots hug the blue hole rim, white hole interior visible; second blue loop at the protrusion tip (top) with green dots nearby.
- FALSE 3/3 (e40 a-100): from above -- white hole opening with blue rim and red-dot ring; surrounding sheet smooth, no crease under the ring; dark band = wall curving edge-on.
- RIM 1/3 (e10 a180), 2/3 (e10 a150), 3/3 (e35 a165): wall edge with black Bl_0 + orange Bl_1 running along the boundary, green NEAR dots riding them, air beyond the edge; rim ground reads as a smooth ROUNDED edge, no sharp crease; 0-2 red dots in-box (the site is clean rim).

Worker's read of the surface shape (pictures only, no bend-verdict):
(a) At the false loop there is NO sharp turn/junction/crease under the red ring -- the sheet around it is smooth in all three views. Instead the eye finds the ring IS the rim of a HOLE in the mesh: the C01 DS mesh carries 4 boundary loops (traced: 274/247/97/18 edges; the two big ones sit at the ring, centroids [28.7,64.3,36.4]/[23,54.5,36.4]); red FAR dots sit med 7.5mm from mesh boundary (p10 0.3, p25 ~1mm; to loop1 med 7.4/p10 0.3); white background shows through the opening. The hole is a data gap, not DS noise: the staged Surface_0 sheet has ZERO points within 15mm of the loop0 centroid while neighbouring solid-sheet discs same radius hold hundreds (loop1 disc ranks 89/90 in a neighbourhood sweep). So the veto dots are TRUE data-edge dots around a scan hole -- genuinely off the sherd rim (author ORIG ignores the hole), which is consistent with 162 (rim walked denser), 163 (balls still fill at R=8/12 since dots sit ~7mm off the rim) and 164 (hole-wall sheet flatter than the flaring rim) -- but it REVISES the 163/164 "interior false positive on continuous sheet" mechanism: the sheet is not continuous there.
(b) At the rim, the ground is a smooth rounded wall edge with empty half-space beyond it; green dots + both ORIG loops all agree on its course. Visually it is the sharper, more edge-like of the two sites -- yet even it shows no knife-edge crease, just a rounded break.
Heads-up, not a verdict: any future "bend-aware" or position rule must treat hole-rims as a third class (neither rim nor interior) -- and the full-res (non-DS) mesh should be checked to confirm the hole pre-dates decimation. That check is NOT this ticket (render-only); flagged for the lead.
