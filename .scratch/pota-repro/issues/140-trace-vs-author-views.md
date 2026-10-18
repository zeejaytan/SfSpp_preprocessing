# Trace vs author, separated + on the mesh

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 134 (M134d finished walk 278/282) + 100 (mesh-overlay precedent: C01 mesh 11875 verts, ORIG Bl_0 + fresh walk on mesh) + 135 (three-walk comparison precedent)

**Status:** results-in

**What to deliver:** renders for the conservator's eye, no new analysis. Four panels from the frozen 282-bag data: (a) author's ORIG Bl_0 loop ALONE on the C01 mesh; (b) plain greedy-279 walk ALONE on the mesh; (c) finished M134d walk ALONE on the mesh; (d) all three overlaid on the mesh (author green, greedy orange, M134d purple) in two viewpoints (top-oblique + the fold-back constriction close-up). Same scale/orientation across a–c so the eye compares honestly; state the frame. Success bar: four renders with the three walks visually separable, mesh context visible (fold-back region identifiable), no invented geometry (walks plotted as-sequenced, teleports as straight chords).

**Starting position:** .scratch/pota100_repro/ (mesh path, overlay code, frame), pota134_repro/ (M134d sequence), pota128_repro/ (greedy-279 sequence). Login-node numpy only — no Slurm, no E2E. New scratch pota140_repro/; renders under laptop artifacts/pota140/.

**Rules:** read-only on all inputs (ORIG Bl_0 plotted as evidence, never altered); COMMIT NOTHING; Comments-only ticket edits; renders are the deliverable.

- [x] Mesh + three sequences loaded in one frame
- [x] Panels a–d rendered, eye-legible
- [x] Ticket flipped with render paths

## Comments (worker, 2026-10-19 — laptop numpy only; COMMIT NOTHING)

**Verdict: renders landed, eye-checked. Five PNGs under laptop artifacts/pota140/ (a/b/c + d in two viewpoints).**

**Frame (stated):** GT-seated/gate frame via `.scratch/pota115_staging/inputs/TF.txt` (TF==TO byte-identical, so gate frame IS the assembled frame). Mesh seated exactly as ticket-100 (`Vg = V@TF+t`); ORIG already gate-frame (`p119_OG.npy`); both walks seated with the same TF. Full-view limits shared across a/b/c/d-top (mesh-bbox cube, ctr [1.7,51.1,37.8] half-side 62.6; elev 20 / azim -60 = ticket-100 full-sherd precedent). Fold close-up elev 10 / azim -85 centred on ORIG[186] r=38 (ticket-100: the fresh (38,191) touch lands 3.5mm from the author loop at its 88%-along point, i.e. ORIG ~186).

**Sources (read-only, zero ORIG points copied, ORIG plotted as evidence only):** mesh `temp_download/Mesh/Pot_C/Pot_C_Piece_01_Mesh_DS.obj` (11875 verts / 23114 faces — exact match to ticket-100's md5-guarded mesh counts); ORIG `.scratch/pota119_repro/p119_OG.npy` (211); greedy-279 `.scratch/pota134_repro/p134_G279.npy` + `.scratch/pota128_repro/p128_seq_greedy.npy` (seqlen 206, 3 teleports >=40mm); M134d `.scratch/pota134_repro/p134_G282.npy` + `.scratch/pota134_repro/p134_seq_d.npy` (seqlen 290 / 278 unique, 0 teleports >=40mm). Walks plotted as-sequenced, so teleports render as straight chords — no invented geometry. Script `.scratch/pota140_repro/p140_render.py`; frame note `artifacts/pota140/p140_frame.txt`. Tickets 39-139 untouched.

**Renders (all eye-checked on laptop):**
- `artifacts/pota140/p140_a_author.png` — author ORIG Bl_0 ALONE (green, 211): clean closed lip loop hugging the mesh.
- `artifacts/pota140/p140_b_greedy279.png` — plain greedy-279 ALONE (orange, 206): lip loop plus long straight chords (teleports) across the hollow, and blocky right-side excursions.
- `artifacts/pota140/p140_c_m134d.png` — finished M134d ALONE (purple, 290/278u): denser lip coverage, retreat zig-zags, no long chords.
- `artifacts/pota140/p140_d_overlay_top.png` — all three overlaid, top-oblique: green/orange/purple separable; both walks track the author loop round the lip, chords vs loop visible in one glance.
- `artifacts/pota140/p140_d_overlay_fold.png` — all three overlaid, fold-back close-up: the three traces run together through the corner, separable by colour.

**What the eye can compare:** a/b/c share scale+orientation so trace-vs-author differences are honest; d-top shows global agreement (lip) vs disagreement (aerial chords, right-side blocks); d-fold shows local separation at the constriction corner. No analysis beyond this — renders only, per brief.
