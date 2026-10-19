# C01 on the mesh, ours vs author, side by side

GOAL: THE CONSERVATOR SEES THE CURE ON THE MESH.

**Answers:** E1

**Blocked by:** 140 (separated trace views) + 149 (thin-line walk) + 155 (binary veto proven).

**Status:** results-in

**What to deliver:** side-by-side figure: panel 1 = author's C01 trace overlaid on the Pot C mesh; panel 2 = OUR veto-cured C01 trace on the same mesh (same view, same scale). Use the veto-filtered trace (149 thin-line / M144 314 walk from pota144_repro -- state which in Comments; the binary-fresh Pot C extraction is still running in 156, this is the same veto laptop-applied). Pot C mesh from temp_download/Mesh/Pot_C. 2D projections at the established views (140 frame) + one rotatable visual-qa staging if the helper is available, else PNGs.

**Rules:** mapping author's input onto our mesh is comparison-only, no author points enter any fix; eye-check every panel; COMMIT NOTHING; Comments-only ticket edits; renders under laptop artifacts/pota157/.

- [ ] Author C01 on mesh + vetoed C01 on mesh, same view
- [ ] Panels eye-checked, paths reported
- [ ] Verdict (one plain paragraph: what the eye sees)

## Comments (worker, 2026-10-19)

Run: `python .scratch/pota157_repro/p157_render.py` (repo root, system python with numpy+matplotlib 3.11.1, no env change needed, no science change). All asserts passed: mesh Pot_C_Piece_01_Mesh_DS.obj 11875 verts/23114 faces; ORIG p119_OG.npy (211,3); ours = 149 thin-line vetoed walk p149_T.npy (131,3) + p149_seq_thin.npy, seated walk (123,3); walk maxstep 41.0, n>25 = 6, n>=40 = 1. M144 NOT shown (pre-veto dense 314-bag walk, per script). Author data comparison-only, zero author points in any fix.

Panels (all under artifacts/pota157/, eye-checked, mesh present, traces on the lip, titles/legends correct, no empty axes):
- artifacts/pota157/p157_a_author_top.png -- author ORIG Bl_0 ALONE (green, 211)
- artifacts/pota157/p157_b_ourcured_top.png -- OUR veto-cured thin walk ALONE (blue, 123 seq/122u)
- artifacts/pota157/p157_b_ourcured_fold.png -- ours ALONE, fold-back close-up (ctr ORIG[186] r=38)
- artifacts/pota157/p157_overlay_top.png -- overlay top-oblique, author (green) + ours (blue) + honest uncovered ORIG[102:120] red markers (render-only)
- artifacts/pota157/p157_overlay_fold.png -- overlay fold-back close-up
- artifacts/pota157/p157_sbs_top.png -- side-by-side, same view (elev 20/azim -60), same scale (140 frame)
- artifacts/pota157/p157_frame.txt -- frame/provenance note (140 frame verbatim, veto description, views)

Verdict: the eye sees the grey Pot C sherd mesh (spout to the right) carrying both traces on its lip in the same 140-frame view -- the author green loop is smooth and closed while our blue veto-cured thin walk tracks it closely along the right and bottom lip but cuts straight chords across the left side and kinks near the bottom tip (as-sequenced plotting of the 123-seq walk, maxstep 41.0), with the red ORIG[102:120] markers sitting on the top lip where the honest uncovered span is; the fold-back close-ups confirm blue hugging green along the bottom edge segment by segment, so the cure reads as on-mesh and comparable, with the remaining chord deviations plainly visible rather than hidden. Cosmetic only: on p157_sbs_top.png the suptitle overlaps the two panel titles at top centre, still readable, no re-render needed.
