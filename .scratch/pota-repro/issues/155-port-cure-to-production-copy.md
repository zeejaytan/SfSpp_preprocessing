# Port the cure to the copy production runs — sub-copy admission + sequencer

GOAL: THE VETO IN THE BINARY THAT MAKES THE DOTS.

**Answers:** E1

**Blocked by:** 154 lead-review finding 2026-10-19 (shipped cure patched the ROOT edgeline_extraction_headless.cpp; every production run script binds + builds original_nurbs_preprocessing/ — the SUB-copy — whose flow differs: same 0.6pi gate :909, unclustered K=1 snap, LIVE Ticket-05 filterBoundaryNoise, sequencer in edge_line_ordering.cpp, NO dead reload-over). Root-copy cure commit 1c6a8f9 stands harmless but non-production.

**Status:** results-in

**What to deliver:** (1) sub-copy admission audit at cloud level — does its 0.6pi gate + unclustered-snap admit both faces (veto-field probe, same bars as 153: outer kept<=10%, inner>=95%)? does the LIVE Ticket-05 filter keep dense outer-face clusters (min_neighbors=6, cf. 120)? name the exact push_back line(s) where outer dots enter; (2) ported patch as staged diff (face veto at the sub-copy admission loop + sequencer guard assessment for edge_line_ordering.cpp — port, adapt, or rule-out with numbers); ORIG-free rules throughout (mesh-observable gates only, no ORIG constants); (3) build+run STAGED for lead relay in the sfs_cure_1c6a8f9 Spartan worktree (exact apptainer/cmake/run commands, piece-01 C-base, [FACE VETO] watches, score vs 182/195).

**Starting position:** 150 §1-2 (mechanism family), 153 (veto field, staged hunks as port template), sub-copy sources (laptop checkout has both copies), Spartan worktree /data/gpfs/projects/punim2657/sfs_cure_1c6a8f9 (lead-owned relay ground — do NOT create jobs there, stage commands only). Remote main checkout is foreign WIP (dirty) — never touch it.

**Rules:** ORIG Bl_0 ruler-only; worker COMMIT NOTHING (lead reviews + lands); no Slurm; no remote writes; tickets 39-154 read-only; Comments-only ticket edits.

- [ ] Sub-copy admission audit (gate + snap + live-filter verdicts, numbers vs bars)
- [ ] Ported patch staged (veto + sequencer assessment)
- [ ] Relay commands staged for lead (worktree build + piece-01 run + scoring)
## Comments (worker, 2026-10-19 -- sub-copy audit + ported patch staged; COMMIT NOTHING)

Verdict: SUB-COPY ADMITS BOTH FACES (veto has something to veto); LIVE Ticket-05 FILTER KEEPS THE OUTER LOOP (no operating point); PORT STAGED (veto verbatim-portable, sequencer ADAPT-replace, relay commands staged). No repo sources touched, no Slurm, no remote writes.

## Relay (lead, 2026-10-19 -- BUILT + RAN, veto proven on the binary)

Worktree sfs_cure_1c6a8f9 @ 1c6a8f9 + 155 diffs. Build needed production's vendored sub-copy alglib (md5 differs from laptop root copy -- copied production's, build-local only). Relay path lessons: binary scans Temp/ recursively for .obj; needs mesh-stage Surface xyz (MeshPreprocessingHeadless from Dataset/Point); CWD must be original_nurbs_preprocessing/ with Dataset/Point+Mesh symlinked in (production uses Dataset->../Dataset, Temp->../Temp symlinks); --datasetPath/--tempPath flags IGNORED (relative paths + POT_NAME env). Jobs 33422971/33423092/33423164/33423230 no-op'd on wrong CWD/inputs; 33423358 + 33423411 ran full chain; 33423575 captured base pair.

VETO FIRES on built binary (run_cure5.log, 16 rims): dropped=201/156/227/164/126/111/107/70/60/11/1/0... Base-vs-cure breakline pairs (same staged surfaces): P02_0 97 vs 743, P03_0 80 vs 502, P04_0 103 vs 259, P05_0 97 vs 343; clean rims ~equal; P01_0 217 vs 210 (+7 resample noise, honest note). SPLIT-WALK active. Cured outputs restored in worktree. Foreign-WIP production checkout untouched (only read + exec'd its Oct16 binary as baseline). Pot C E2E still open (no Pot C inputs staged on Spartan) -- Pot A relay proves the binary does what the prototype did.

1. Sub-copy admission audit (p155_step0_admit.py -> .scratch/pota155_repro/p155_admit.txt; render artifacts/pota155/p155_admit.png, eye-checked). Control GREEN: C-base 270 / inner 88 / outer 182 (150 banked exact; all-bag outer 195 per 148/150, share 182/195=0.933). Static map (read-verified): 0.6pi gate :909 with no face test; boundary loop :916-922, OUTER ENTRY push_back :920 (normals in scope, same layout as root); K=1 unclustered snap :956-966, RESAMPLED ENTRY push_back :966 (PointXYZ -- normals dropped, but veto sits upstream so nothing needed there); LIVE Ticket-05 filterBoundaryNoise :991-1007 (radius=g_boundary_radius_mm*8/6 clamp[2,20], min_neighbors=6, loud fallback to unfiltered); NO reload-over (Ticket-05 already deleted it -- nothing to delete); sequencer getPointsInSequence@edge_line_ordering.cpp:51-107 (greedy K=adaptive/10, no heading guard) + SFS-T13 second-chance :112-203.

2. Numbers vs 153 bars (outer kept<=10 pct, inner>=95 pct). Veto-field rescore (saved 153 centroid-align, mesh-observable): outer kept 1/182 red=0.995 PASS; inner kept 88/88 = 1.000 PASS. Ticket-05 sim (numpy ball-count on C-base positions, rigid-TF invariant): at production op point r=9.7/k6 keeps 181/182 outer (red=0.005) and 87/88 inner -- the filter keeps dense outer-face clusters. Full sweep: NO (r,k) operating point reaches outer red>=0.90 with inner>=0.95 (r=6/k6 kills inner first, 25/88 -- same harm direction as 150 s2). The filter cannot substitute for the veto; the veto must sit at the :920 loop so the snap inherits it.

3. Ported patch staged (verify-only; git apply --check PASS both; repo sources untouched): pota155_subcopy_veto.diff (face veto at :916-922, ported verbatim from 153 hunk 1 -- normals+Eigen already in scope, no new includes; [FACE VETO] log); pota155_sequencer_port.diff (split-then-select + half-plane guard into edge_line_ordering.cpp, adds functional/map/limits; REPLACES greedy+T13 with rationale header -- post-veto input is single-face ~90 dots so T13 goes dormant anyway, and the component split walks all fragments with cut-recorded chaining where T13 jumped silently; T13 stays in git history). Sequencer verdict ADAPT (not verbatim, not rule-out): 150 step3b proves the point -- on the vetoed 90-cloud naive == halfplane (hops=7 direct=0 jumps>5=16, identical stations), so the veto stops the teleports and the guard/walk only banks the 16 honest gaps as cuts; relay must regression-check Pot_A piece-2 wall (T13 calibration case). ORIG-free recheck PASS: added-line ORIG/Bl_0/author hits all comment prose (pota155_origfree.md); probe-vs-production centroid residual stated with the FACE VETO log-line tripwire (stop, do not retune 0.5 against ORIG).

4. Relay staged (pota155_relay.md): sfs_cure_1c6a8f9 worktree reconcile (remote main checkout foreign-WIP dirty -- never touch) + apptainer/cmake/make EdgeLineExtractionHeadless + piece-01 C-base run (counters vs 182/195, FACE VETO expect kept~89/dropped~181, SPLIT-WALK watches) + p2-wall regression + renders. Fallback named (paste hunk+logs, no ORIG relaxation). Renders: p155_admit.png (veto histograms + filter sweep). Tickets 39-154 untouched; COMMIT NOTHING done.
