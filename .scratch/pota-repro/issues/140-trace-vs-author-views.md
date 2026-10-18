# Trace vs author, separated + on the mesh

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 134 (M134d finished walk 278/282) + 100 (mesh-overlay precedent: C01 mesh 11875 verts, ORIG Bl_0 + fresh walk on mesh) + 135 (three-walk comparison precedent)

**Status:** ready-for-agent

**What to deliver:** renders for the conservator's eye, no new analysis. Four panels from the frozen 282-bag data: (a) author's ORIG Bl_0 loop ALONE on the C01 mesh; (b) plain greedy-279 walk ALONE on the mesh; (c) finished M134d walk ALONE on the mesh; (d) all three overlaid on the mesh (author green, greedy orange, M134d purple) in two viewpoints (top-oblique + the fold-back constriction close-up). Same scale/orientation across a–c so the eye compares honestly; state the frame. Success bar: four renders with the three walks visually separable, mesh context visible (fold-back region identifiable), no invented geometry (walks plotted as-sequenced, teleports as straight chords).

**Starting position:** .scratch/pota100_repro/ (mesh path, overlay code, frame), pota134_repro/ (M134d sequence), pota128_repro/ (greedy-279 sequence). Login-node numpy only — no Slurm, no E2E. New scratch pota140_repro/; renders under laptop artifacts/pota140/.

**Rules:** read-only on all inputs (ORIG Bl_0 plotted as evidence, never altered); COMMIT NOTHING; Comments-only ticket edits; renders are the deliverable.

- [ ] Mesh + three sequences loaded in one frame
- [ ] Panels a–d rendered, eye-legible
- [ ] Ticket flipped with render paths
