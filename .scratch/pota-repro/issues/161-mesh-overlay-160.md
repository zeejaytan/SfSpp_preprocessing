# Mesh-overlay render of the 160 result (BASE vs VAR walks on C01 mesh)

GOAL: A PICTURE THAT MEANS SOMETHING -- BOTH WALKS SEEN AGAINST THE SHERD.

**Answers:** E1

**Blocked by:** 160 (BASE n=402 vs VAR n=226 walks gated, renders are mesh-less 3D scatter) + 157 (mesh-overlay render pattern p157_render.py, C01 mesh handling).

**Status:** results-in

## Revisit note (user, 2026-10-19)

Bl_1's identity is UNRESOLVED: whether it is the outer edgeline or the inner edgeline is not established, and against the author's output it looks wildly incorrect either way. Known slot semantics (2026-10-17): slot 0 = interior wall face, slot 1 = exterior wall face (Surface_0 -> Breakline_0, Surface_1 -> Breakline_1); the assembler opens only slot 0. Open questions for revisit: (1) which physical edge Bl_1 is supposed to be; (2) gate Bl_1 vs ORIG Bl_0/Bl_1 to quantify 'wildly'; (3) whether the face-hop stitching artifact (wall-thickness fingerprint) affects Bl_1 too. Evidence: artifacts/pota161/ (black loop, BASE==VAR 92 pts).

**What to deliver:** renders showing, on the C01 piece mesh: (a) BASE walk (current output, red), (b) VAR walk (fix attempt, green), (c) author's ORIG loops (grey/black) as reference. Same camera for all; one side-by-side panel + one overlay panel minimum. Each walk drawn as an ORDERED trace (line through sequenced points, not scatter) so walk order is visible; label clearly which is dots-vs-walk: these are WALKS (ordered breakline traces), not raw dot clouds. Eye-check before reporting.

**Starting position:** 160 Comments (BASE/VAR pcd paths, staged trees); 157 Comments + .scratch/pota157_repro/p157_render.py (mesh overlay pattern). Renders to artifacts/pota161/.

**Rules:** read-only over tickets 39-160; no builds, no runs (render-only, laptop-side acceptable if data fetchable, else minimal Spartan read job); COMMIT NOTHING; Comments-only ticket edits; state for each panel: what is drawn (walk/dots/mesh), colors, camera.

- [x] BASE walk on mesh (+ ORIG loops)
- [x] VAR walk on mesh (+ ORIG loops)
- [x] Overlay or side-by-side, same camera, labeled

## Comments (worker, 2026-10-20, render-only)

Run: `python .scratch/pota161_repro/p161_render.py` (repo root, system python numpy+matplotlib, no env change, no science). All asserts passed: mesh Pot_C_Piece_01_Mesh_DS.obj 11875 verts/23114 faces; ORIG p119_OG.npy (211,3) gate-frame; BASE Bl_0 402 pts/13 segs; VAR Bl_0 226 pts/6 segs; Bl_1 92 pts BASE==VAR bit-identical (max abs diff 0.0). Frame: 140 frame verbatim via .scratch/pota115_staging/inputs/TF.txt (TF==TO; mesh Vg=V@TF+t; BASE/VAR pcd walks seated with same TF -- pcd raw bbox matches mesh RAW bbox, i.e. extraction frame; ORIG already gate-frame). Walks drawn as ORDERED traces, one polyline per pcd `# a b` segment range, no chords across segment boundaries (within-segment teleports show as honest straight chords). Author ORIG comparison-only, zero author points in any fix. COMMITTED NOTHING.

Renders (all under artifacts/pota161/, eye-checked: mesh present, traces on the lip, titles/legends correct, no empty axes, sbs caption moved to bottom to avoid title overlap):
- artifacts/pota161/p161_a_base_top.png -- mesh + BASE Bl_0 ALONE (red, 402) + ORIG (grey, 211) + Bl_1 (black, 92)
- artifacts/pota161/p161_b_var_top.png -- mesh + VAR Bl_0 ALONE (green, 226) + ORIG + Bl_1
- artifacts/pota161/p161_overlay_top.png -- overlay top-oblique: BASE (red) + VAR (green) + ORIG (grey) + Bl_1
- artifacts/pota161/p161_overlay_fold.png -- overlay fold-back close-up (ctr ORIG[186] r=38)
- artifacts/pota161/p161_sbs_top.png -- side-by-side, same view (elev 20 / azim -60), same scale (140 frame)
- artifacts/pota161/p161_frame.txt -- frame/provenance note

Per-panel description: panel 1 (BASE, red) hugs the grey ORIG loop along the left, top and bottom lip but fires long straight teleport chords across the sherd interior (13 segs); panel 2 (VAR, green) tracks the left and bottom lip tightly with fewer chords (6 segs) but leaves a top-left rim span where grey ORIG runs alone -- the veto-eaten rim from 160. The overlay shows both walks against the same grey loop: green stays on the lip where it exists, red covers more rim at the cost of interior chords. Bl_1 (black, near spout) identical in both.

Verdict: the eye sees both 160 walks seated on the C01 lip against the author's loop in one shared view -- BASE covers the rim with teleport chords, VAR is cleaner but misses rim the veto ate; the picture supports the 160 clean-negative verdict.
