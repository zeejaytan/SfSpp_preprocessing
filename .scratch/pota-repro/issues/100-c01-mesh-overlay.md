# C01 mesh overlay — paint both loops on the fragment (see the fold-back)

GOAL: MATCH AUTHOR'S INPUT.

**What to deliver:** One render of the actual C01 sherd mesh with the author's ORIG Bl_0 loop and our fresh Bl_0 walk painted on it in contrasting colours, from a viewpoint that shows where the lip folds back on itself (the near-touch constrictions). Plus a sentence per visible feature: where the fold-back is on the piece, and where our walk leaves the surface (the aerial spur).

**Answers:** E1

**Blocked by:** 97 (constrictions (38,191)/(39,401)) + 99 (run map, step-across points)

**Status:** results-in

**Starting position:** Fresh C01 mesh/point cloud + ORIG C01 Bl_0 + fresh C01 Bl_0 from the t39-pipe bundles. Login-node render only (matplotlib sampler of the mesh surface or project-to-mesh colouring — no Slurm, no E2E, no gate). New scratch only for scripts; renders under laptop artifacts/pota100/.

**Rules:** read-only (zero ORIG points, bundles md5-guarded); COMMIT NOTHING; Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); if the mesh won't load on login node, say so with the blocking error and STOP (landable negative — do not burn Slurm on a picture).

- [ ] C01 mesh + ORIG loop + fresh walk overlay render
- [ ] Fold-back location + spur departure in plain words

## Comments (worker, 2026-10-18 — COMMIT NOTHING; lead to commit)

**Verdict: render landed.** One two-panel PNG of the actual C01 sherd mesh with ORIG Bl_0 (green, 211 pts) and the fresh Bl_0 walk (red, 402 pts, aerial spur overdrawn magenta) from a viewpoint showing the fold-back; login-node matplotlib only, no Slurm, no E2E, no gate. Mesh loaded fine on the login node — no blocking error.

**Render:** `artifacts/pota100/C100_C01_mesh_overlay.png` (left: full sherd; right: zoom on the fold-back). Eye-checked on laptop. Script: Spartan `/data/gpfs/projects/punim2657/pota100_repro/p100_overlay.py`, laptop mirror `artifacts/pota100/p100_overlay.py`.

**Fold-back in plain words:** on the sherd's lip rim. The fresh walk's two parallel passes touch at file pairs (38,191) and (39,401), both gaps 1.9mm (black dashed links in the zoom panel). The (38,191) touch sits on the lower-left stretch of the lip as viewed and lands 3.5mm from the author's loop (near its 88%-along point); the (39,401) touch sits on the mid-right stretch of the lip, ~32mm past the end of the author's traced arc — the walk overshoots the true lip end and doubles back, outgoing and return passes kissing at these two points instead of closing the author's ring.

**Spur departure in plain words:** the walk leaves the surface at fresh index 10 (the 9→10 jump, 56.8mm teleport). The 29-pt segment [10,39) arcs clean across the hollow interior of the bowl (magenta arc in both panels), floating a median 24mm / max 39mm off the mesh surface, and rejoins the rim at index 39 right beside the (39,401) fold-back touch point. By contrast both lip runs sit on-surface (standoff medians 0.99/1.20mm) and the author's loop hugs the mesh (median 0.53mm) — so the spur is unmistakably aerial, not a surface-hugging detour.

**Mesh + sources (read-only, md5-guarded, zero ORIG points):** mesh `pota39_bundle_C/.../Mesh/Pot_C_Piece_01_Mesh.obj` (11,875 verts / 23,114 faces, md5 a0a341701b252b32f789d55ab4d99e49); fresh Bl_0 md5 e1e59cdf3fc83d4bc19f3461e6a0d99d; ORIG Bl_0 md5 bbc28cd0f18ba4a1a278dd92c0fdeef3. All loops GT-seated per 97/gate73 convention. Spartan leftovers: pota100_repro/ (script + PNG) only. No prep/assembly source touched; no commits.
