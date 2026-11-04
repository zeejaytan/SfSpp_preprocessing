# 303: Why corrected Pot A axes seat 7/8 — diagnose, then a blind fix that seats 8/8

**What to build:** with the ticket-302 axis chain (MATLAB-faithful per-point cost), Pot A assembles 8/8 pieces and 15/15 joins from the released axis files but only 7/8 and 13/15 from our own. Find which piece and which axis line cause the loss, trace it to the paper or code, and change the axis chain so that **our own axes, chosen without looking at the released files, seat Pot A 8/8 and 15/15**, and do so repeatably.

**Answers:** E1

**Blocked by:** 302 (landed 2026-11-04, merge 3d55af5)

**Status:** ready-for-agent

**Worker:** unassigned

**Budget:** large 8

**Hand-over:** Claude — needs Spartan assembler runs (apptainer SIF), the corpus, and judgement about whether a seat change sits outside run-to-run spread; one session runs the chain.

## What the lead already established (2026-11-04, read from run 20261103-1620_01bff01_t302-e2e; re-check, do not take on trust)

- Control GPA50 (released axes): 8/8, 15/15; 124 matches, 70 after pruning. Treatment GPA50N (our `out/axes302` axes): 7/8, 13/15; 118 matches, 59 after pruning. All 8 OBJs are written in both arms, so in GPA50N one piece is **placed wrong**, not dropped. Which piece has not been identified yet: read `out/GPA50N/T_*to_*.txt` against GT.
- **The assembler uses axis lines in two ways.** Matching loops over every line pair (`sfs_main/sfspreproc-docker/class/feature_matching.cpp:1461-1475`, `axis_x`/`axis_y`; the chosen pair's angle is used at :1665-1668). Root alignment to z and reconstruction read **line 0 only** (`class/ranking_system.cpp:957-958, 1033-1034, 1727-1731`; `class/reconstruction.cpp:156-157`).
- **Our line order differs from the released files on the two suspect pieces** (angle of each of our lines to released line 1): P06 = [24.36°, **2.38°**] (released file has one line); P08 = [35.91°, 16.02°, **7.74°**] (released has two). On P01 our single line is 0.8° from released. Per-seed angle to released (pota302.tsv): P6 24.4 every seed; P8 35.9 on 7/10 seeds and 16.0 on 3/10; P1-P5 0.6-3.2; P7 6.3.
- **How the order is set:** `run_potsac.m:39-45` computes the Huber cost on the 10% subsample after stage-1 refine; stage-2 refine on all points (:66-68) moves the axes, and the final sort (:82) reuses the **stale stage-1 cost**. The port copies this faithfully (`sfs_axes/potsac.py:116-125`). The paper (`papers/text/sfspp-2502.13986v1.md:175`) says all surface points are used for detailed refinement after pruning and the higher-cost axis is pruned; it does not say the cost is recomputed. A candidate deviation, not a proven one. Also open: `extract_axis_nurbs.m` / `read_surfaces_nurbs.m` suggest the released axes may come from NURBS surfaces, not the shipped Surface xyz (ticket 302's residual (a)).
- **Weight warning:** E1 records the released-axis control itself at 6/8 and 7/8 in other runs (density-restore run, "±2 mm wobble"). One 7/8 may be noise. Nothing below is a result until it is shown outside the replay spread.

## Stages

**A — Is 7/8 real?** Replay GPA50 and GPA50N, staged inputs byte-identical (md5 logged), at least **5 replays each** in one job. Report sherd/join counts per replay. If GPA50N reaches 8/8 in some replays and GPA50 drops in some, say so and give best-of-N plus counts (best-of-N rule, AGENTS.md).

**B — Which piece, which line.** Per replay, identify the misplaced piece(s) (T files vs GT: rotation deg, translation mm). Read the assembler logs for which axis-line pair the winning matches on that piece used (add logging in a shim copy only if needed; never edit the SIF or sfs_main).

**C — Single-variable arms** (only Axes/ differs from GPA50N; diff -rq proves it, as in 302's e2e script). All axes from `out/axes302`:
- **C1 oracle reorder** (diagnostic only, never shippable): put the line nearest the released line 1 first on every piece.
- **C2 first line only:** truncate every file to its first line.
- **C3 recompute cost after stage-2:** rank the survivors by the Huber cost on all points after the final refine (the candidate code-vs-paper fix). Runs with the port; the lead wants this one.
- **C4 (only if C1-C3 do not explain it):** NURBS-input axes via the authors' extract_axis_nurbs path, to test the provenance hypothesis.
Replay each arm at least 3 times.

**D — The fix.** Make the smallest **blind** change to `sfs_axes` that seats 8/8 and 15/15: it may use only the piece's own surfaces, never the released axes or GT. If it departs from `run_potsac.m`, cite the paper line that licenses it, and add a switch so the MATLAB-faithful behaviour can still be reproduced. Re-run the 302 MATLAB unit/regression checks wherever the change touches the code they cover. Then re-run the corpus axes (163 pieces, new paths, corpus md5 unchanged) and a Juglet E2E arm for collateral damage.

## Rules

Read `SfSpp_preprocessing/AGENTS.md` first (corpus caveats; runs layout; staging by symlink; unseeded mesh stage). Open the branch with `C:/PR/scripts/ticket_start.sh SfSpp_preprocessing .scratch/pota-repro/issues/303-pota-8of8-axes.md` (Status must still read ready-for-agent when you run it). **SSH from the laptop: use `/c/Windows/System32/OpenSSH/ssh.exe spartan`** — git-bash's `/usr/bin/ssh` cannot use the key ("Permission denied (publickey)"). Runs live under `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_<tag>/` with run.json and an index.tsv row (verdict columns empty). Start from 302's `.scratch/pota-repro/302-stage/submit302_e2e.sbatch` (guarded shim, arm67.sh, apptainer). Poll every sbatch with `sacct -j <id> --format=State,ExitCode` and record it. Released axes and GT may be read **only to score and diagnose**; the shipped selection rule must never read them. No corpus file changes. Renders: Pot A reassembly top+side for the best GPA50N-type arm before and after the fix, plus the misplaced piece (images go to `artifacts/pota303/`; the lead and conservator eye-check them). Comments-only ticket edits (`## Comments (worker, <date>)`); checkboxes and Status stay with the lead. Commit nothing.

- [ ] A: replay spread for GPA50 and GPA50N (≥5 each), counts per replay, best-of-N
- [ ] B: misplaced piece(s) named with rotation/translation error and the axis-line pair used
- [ ] C: arms C1-C3 (and C4 if needed), ≥3 replays each, axes-only diffs proven
- [ ] D: blind fix in sfs_axes behind a switch, paper line cited; 8/8 and 15/15 on every replay (or best-of-N with counts, if the control itself is not stable)
- [ ] D: 302 MATLAB checks still pass where touched; corpus re-run to new paths with md5 unchanged; Juglet arm shows no loss
- [ ] Renders staged; job IDs and sacct states recorded
- [ ] Branch merged and pushed by lead, worktree removed, branch deleted (lead)
