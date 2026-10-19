# Port the cure to the copy production runs — sub-copy admission + sequencer

GOAL: THE VETO IN THE BINARY THAT MAKES THE DOTS.

**Answers:** E1

**Blocked by:** 154 lead-review finding 2026-10-19 (shipped cure patched the ROOT edgeline_extraction_headless.cpp; every production run script binds + builds original_nurbs_preprocessing/ — the SUB-copy — whose flow differs: same 0.6pi gate :909, unclustered K=1 snap, LIVE Ticket-05 filterBoundaryNoise, sequencer in edge_line_ordering.cpp, NO dead reload-over). Root-copy cure commit 1c6a8f9 stands harmless but non-production.

**Status:** ready-for-agent

**What to deliver:** (1) sub-copy admission audit at cloud level — does its 0.6pi gate + unclustered-snap admit both faces (veto-field probe, same bars as 153: outer kept<=10%, inner>=95%)? does the LIVE Ticket-05 filter keep dense outer-face clusters (min_neighbors=6, cf. 120)? name the exact push_back line(s) where outer dots enter; (2) ported patch as staged diff (face veto at the sub-copy admission loop + sequencer guard assessment for edge_line_ordering.cpp — port, adapt, or rule-out with numbers); ORIG-free rules throughout (mesh-observable gates only, no ORIG constants); (3) build+run STAGED for lead relay in the sfs_cure_1c6a8f9 Spartan worktree (exact apptainer/cmake/run commands, piece-01 C-base, [FACE VETO] watches, score vs 182/195).

**Starting position:** 150 §1-2 (mechanism family), 153 (veto field, staged hunks as port template), sub-copy sources (laptop checkout has both copies), Spartan worktree /data/gpfs/projects/punim2657/sfs_cure_1c6a8f9 (lead-owned relay ground — do NOT create jobs there, stage commands only). Remote main checkout is foreign WIP (dirty) — never touch it.

**Rules:** ORIG Bl_0 ruler-only; worker COMMIT NOTHING (lead reviews + lands); no Slurm; no remote writes; tickets 39-154 read-only; Comments-only ticket edits.

- [ ] Sub-copy admission audit (gate + snap + live-filter verdicts, numbers vs bars)
- [ ] Ported patch staged (veto + sequencer assessment)
- [ ] Relay commands staged for lead (worktree build + piece-01 run + scoring)
