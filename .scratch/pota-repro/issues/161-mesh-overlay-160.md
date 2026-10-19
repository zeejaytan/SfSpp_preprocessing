# Mesh-overlay render of the 160 result (BASE vs VAR walks on C01 mesh)

GOAL: A PICTURE THAT MEANS SOMETHING -- BOTH WALKS SEEN AGAINST THE SHERD.

**Answers:** E1

**Blocked by:** 160 (BASE n=402 vs VAR n=226 walks gated, renders are mesh-less 3D scatter) + 157 (mesh-overlay render pattern p157_render.py, C01 mesh handling).

**Status:** ready-for-agent

**What to deliver:** renders showing, on the C01 piece mesh: (a) BASE walk (current output, red), (b) VAR walk (fix attempt, green), (c) author's ORIG loops (grey/black) as reference. Same camera for all; one side-by-side panel + one overlay panel minimum. Each walk drawn as an ORDERED trace (line through sequenced points, not scatter) so walk order is visible; label clearly which is dots-vs-walk: these are WALKS (ordered breakline traces), not raw dot clouds. Eye-check before reporting.

**Starting position:** 160 Comments (BASE/VAR pcd paths, staged trees); 157 Comments + .scratch/pota157_repro/p157_render.py (mesh overlay pattern). Renders to artifacts/pota161/.

**Rules:** read-only over tickets 39-160; no builds, no runs (render-only, laptop-side acceptable if data fetchable, else minimal Spartan read job); COMMIT NOTHING; Comments-only ticket edits; state for each panel: what is drawn (walk/dots/mesh), colors, camera.

- [ ] BASE walk on mesh (+ ORIG loops)
- [ ] VAR walk on mesh (+ ORIG loops)
- [ ] Overlay or side-by-side, same camera, labeled
