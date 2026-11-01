# 53 — measure the growth angle from the sherd's own growth walk

**What to build:** the growth angle the pipeline uses is **measured on the sherd in front of it,
by the growth operator itself**, not set by a constant calibrated on another pot and not by the
k-NN fuse crossing. For each piece: run the pipeline's own growth (the `growPaper234` join rule
exactly — seed by ascending curvature, BFS over neighbours, join iff curvature < kappa AND angle
to the **current front point's normal** <= theta) on a ladder of theta values on the same
downsampled cloud growth eats; from the outcome curve pick the piece's own split threshold
theta_split; ship theta = 0.9 x theta_split. No constant from any other vessel enters.

**Answers:** U19 (does the pipeline put the Juglet back together), E1 (do our breaklines let SfS find joins)

**Blocked by:** None — ticket 52 closed 2026-11-01 with the flip unmerged; main 8e30a6c holds everything.

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-01)
**Branch:** 53-measure-the-growth-angle-from-the-sherds-own-growth-walk, in /c/PR/worktrees/sfs/53

**Worker:** unassigned

## Why

The conservator's rule: *"The fix is to stop guessing theta and measure the edge."* Ticket 51's
cap (k-NN graph, 60% fuse, 0.9x) IS a measured edge, but ticket 52's corpus regression measured
it **biased loose on big clean pieces**: on the 148 corpus pieces the fuse crossing reads 8-12
deg, so theta = 0.9 x crossing would sit at 7-10 deg where those pots are healthy at 3.4 — and
theta 4.1-9.6 already cost 41 lanes (237/292 vs 281/292). Two measured reasons the fuse reads
high: (a) shortcut paths — glue60 FALLS as k grows (more neighbours = cheaper bridges across a
worn ramp; ticket 50 edge run); (b) the fuse tests single-link turns while growth compares to a
DRIFTING front — growth crosses an edge through many small turns no single link betrays. The
operator-faithful measurement is to run growth itself on a theta ladder.

## The gate (pre-registered; measured brackets, not negotiable in-flight)

1. **Corpus:** the 148-piece 292 regression at the new default must score **>= 276 of 292** sound
   lanes at bar (same bar ticket 52 failed at 237). Baseline 281/292 at flat 3.4.
2. **Juglet:** the 17-piece harness must give two **face-sized** (each >= 20% of npts) surfaces
   with genuine wall pairs (med_nn 0.70-1.05 x wall, med_across <= 0.05 mm) on **>= 8 of 9**
   Juglet pieces. J8 is EXEMPT and reported separately: its collapse tracks the uniform 0.6 mm
   spacing (at theta 3.4 + new spacing it grows NO surface), an open defect owned elsewhere.
3. **theta distribution, reported not gated:** per-piece theta_ship for all 165 pieces (148 corpus
   + 17), beside the flat 3.4 and each piece's ladder bracket. The story must be visible: does
   the walk-measured theta land near 3.4 on the corpus and 5.5-8.3 on the Juglet?
4. **Decision rule:** gate 1 AND gate 2 pass -> merge and write the FIXES-LEDGER section Q row
   (superseding row 5). Either fails -> do NOT merge, report number + mechanism. Identical to
   ticket 52's rule; no renegotiation after seeing the numbers.

## The measurement, precisely

- **The walk:** exactly `growPaper234` semantics (mesh_processing_headless.cpp:3228 — ascending-curvature
  seeds, nearestKSearch(paperNB+1), join iff kappaThresh AND angle(candidate, front normal) <= theta,
  dynMinCluster floor, NO merge pass for the ladder probe — the merge pass is part of the real
  pipeline, not of the split/glue question). The ladder implementation may reuse the operator's
  code path, not a re-implementation: if a re-implementation is cheaper, it must reproduce the
  pipeline's split behaviour on the 17-piece set FIRST (same gate as dist43/foldcheck45 precedent).
- **The ladder:** coarse 1.0-12.0 deg step 1.0, then refine the crossing bracket to 0.25 deg.
  Outcome per run: cluster sizes. Definitions: **split** = >= 2 clusters each >= 20% npts
  (the face-sized bar ticket 50 established); **glued** = largest cluster >= 80% npts.
- **theta_split** = the largest theta on the ladder that still SPLITS. **theta_ship = 0.9 x theta_split**
  (same 10% safety margin as the cap, now anchored to the operator's own threshold).
  A piece that never splits at any theta (all one cluster): FALLBACK to 3.4 with a
  [GROWTH-53] FALLBACK log line (never a FATAL; count must be reported, expected 0 on the corpus).
- **Cost bound:** the ladder is ~13 + ~8 growth runs on the downsampled cloud; a full pipeline
  cell ran in ~15 s on these clouds, so the probe must stay under ~5 min/piece. Log per-piece
  ladder seconds; if it exceeds the bound, coarsen the ladder, do not skip the refine.
- **Wiring:** opt-in first via SFS_GROWTH_WALK=1 (default off, byte-identical when unset), one
  env knob; SFS_PAPER_THETA still outranks everything. Flipping the default is NOT in this
  ticket — it is the conservator's call after the gates, exactly as ticket 52 should have been
  run (and was).

## Run plan

- Run 1: 17-piece harness (stage52 instruments copied), arms W (SFS_GROWTH_WALK=1) / X
  (SFS_PAPER_THETA=3.4 control) / C (SFS_GROWTH_FORMULA=1 SFS_GROWTH_CAP=1, the current
  opt-in best). Gate 2 judged on arm W.
- Run 2: 148-corpus 292 regression, build292.sbatch COMMIT re-pointed at the ticket commit,
  with the walk as the CODE default FOR THE RUN ONLY if that is what the array can express
  (the array refuses any SFS_* env; if the walk cannot be made the array's default without
  shipping it, gate the corpus run on a W-default build and say so in run.json).
- One runs/index.tsv row per run, verdict/human_note EMPTY for the lead.

## Predictions (falsifiable)

1. Arm W reproduces the ladder's theta_split-derived theta in the pipeline log to 5 dp.
2. Corpus theta_ship lands in 2.5-4.5 deg on >= 90% of pieces (it should rediscover ~3.4,
   the value the corpus was tuned at — if it lands at 7-10 like the fuse crossing, the walk
   measurement inherits the bias and the ticket fails its own gate).
3. Juglet theta_ship lands 5.5-8.5 on the 8 non-exempt pieces.
4. Zero [GROWTH-53] FALLBACK lines on the corpus.
5. 292 headline >= 276 (gate 1).
6. J8 under arm W behaves as under arm X (spacing-bound, not theta-bound).

## Acceptance

- [ ] Ladder probe reproduces growPaper234 split behaviour on the 17-piece set (or is the operator itself).
- [ ] Run 1 + Run 2 of record with sacct State/ExitCode recorded; corpus md5s unchanged.
- [ ] Gates 1 and 2 judged against the pre-registered brackets, with the theta distribution table.
- [ ] No merge without both gates; the ticket records which fired.
- [ ] run.json, index rows, and the per-piece theta table (out/thetas53.tsv) in the run dir.
- [ ] Code tickets: branch merged into main and pushed, no job still running from it, worktree removed, branch deleted locally and on GitHub — ONLY if the gates pass.

## Out of scope

- J8's spacing starvation (own defect; candidate fix = a real s0 floor on the step, separate ticket).
- Any change to the spacing law, the merge pass, or the assembler.
- Flipping any default (the conservator decides after the gates).
- Seating / e2e (U19's assembly run) — blocked until the growth step is settled.

## Facts already established (do not re-derive)

- Ticket 52 (run 20261101-0428_ba9e425_p292-flipcap): formula-as-default = 237/292, 41 lanes
  lost, 0 gained, pots C-J only, Pot A untouched; spacing is a NO-OP on the corpus (S = 0.6
  under both laws); cap fired 16/148 corpus pieces; formula theta range 2.81-13.82.
- Ticket 51 (run 20261101-0210_863d4f8_t51-cap): cap = 0.9 x k-NN fuse crossing; Juglet pairs
  78-96% of wall when capped; Pot A formula thetas already below crossings.
- Fuse-crossing bias: glue60 falls with k (shortcut paths); fuse crossing on corpus 8-12 deg.
- Growth semantics: join vs CURRENT FRONT normal (drifting reference) — mesh_processing_headless.cpp:3228,
  called at :3773 with paperNB=10, kappa 1.0.
- The face-sized bar (each top-2 cluster >= 20% npts) is the honest split criterion
  (ticket 50 fine sweep; PA08's "two to 15 deg" was one face + a fragment).
- Juglet genuine-pair zone: med_nn 0.70-1.05 x wall, med_across <= 0.05 mm (tickets 51/52);
  capped thetas 5.5-8.3 delivered it on 8 of 9 (J8 excepted, spacing-linked).

**Status:** ready-for-agent
