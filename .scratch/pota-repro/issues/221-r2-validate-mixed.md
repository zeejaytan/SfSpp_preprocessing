# 221 - R2 validation on the 5 MIXED pieces + P16 re-baseline (220 follow-up)

Status: done
Answers: none (splitter-method trial; context 220, rulers 214/217)

## Goal
Validate the 220 R2 stopping rule beyond n=2: run the top-down ladder on the five 214-MIXED pieces (P12/P15/P22/P25/P27) plus a P16 re-baseline. Rule FROZEN from 220 (do not retune): R1 = first threshold with top2>=70% AND third<=8% AND 2nd/1st>=0.5; R2 = R1 at TWO CONSECUTIVE thresholds. Question: does R2 stop exist on each piece, and do all lanes score at bar there?

## Boundary (worker: read-only except where named)
- MAY touch (Spartan experiment copy ONLY, fresh dir sfs-fix-221): reuse the exp-220 single-shot method (branch exp-221 off origin/exp-220, unmerged); fresh run dirs (ladder + edge per piece).
- MAY run: top-down ladder (220 schedule) on P12/P15/P22/P25/P27 + P16; edge + score vs author lanes at each R2 stop (stretch is the verdict -- run it).
- Do NOT touch: main worktree (user 204-edit live), .wt-*, other branches (pristine-splitwalk, exp-220, exp-218), stashes, v0/v1 bundles, other tickets (append Comments here only).
- ORIG-free: author lanes as ruler only (214 staged inputs).

## Constraints
- P16 re-baseline is part of the verdict: record default-4.5 segmentation (cluster count, biggest, S0/S1/UN sizes) alongside the ladder, to test the 220 RED FLAG (214 logged 43/biggest 4799; 220 got 9/biggest 11261). Same for each piece vs its 214-era count where logged.
- 100% dot accounting every ladder row (clusters+UN=cloud), 220 pattern.
- Slots flip per piece (209 pattern, ourBl0->o1 typical) -- verify per piece, never blanket-swap.
- Report channel = this ticket's Comments + completion notice (no send_message downward).

## Acceptance (lead judges; numbers + cites + paths)
- Per piece (6 rows): ladder table, R2 stop (thresholds) or FAIL, lane scores at stop (bar med<2, cov>=90% both lanes), Bl0 unharmed.
- Overall: R2 generalizes n-out-of-6? P16 re-baseline vs 214-fresh (stale confirmed or overturned)?
- Landing decision explicitly NOT in scope (needs lead + user).

## Required evidence to report
- Branch exp-221 (unmerged), Spartan job IDs + sacct State/ExitCode, 6 ladder tables + accounting, lane scores at stops, segmentation-vs-214 comparison.

## Lead verdict (2026-10-21)
ACCEPT with the worker's own conclusion: R2 strict 1-of-6, splitting-level 4-of-6 -- port talk premature. Verified: P16@12 (0.86/92.5 + 0.52/100.0, exact 220 replicate), P12 (0.59/95.6 + orphan 5.76/33.0), P15 (0.64/100.0 + Bl1 below-bar alone) re-scored locally EXACT; 7/7 sacct COMPLETED 0:0; exp-221 = exp-220 code, pushed unmerged; both renders eye-checked by lead (P12 red shortcut across interior confirmed; P15 both our-lanes on outer perimeter, inner arc uncovered, confirmed). RED FLAG upgraded to confirmed-and-bounded: 214-P16 stale (good direction), P16-specific (others within +-2). New traps stand (esp. invocation-shape sensitivity: P22 ladder-vs-single flip is deterministic, bit-identical reps). NOTE: worker's file edit clobbered lines 1-27 with [object Object] strings; spec head restored from git, worker Comments preserved verbatim below. Evidence .scratch/pota221/ committed with ticket. NO landing.

## Comments (worker 221, 2026-10-21. NO main commit; branch exp-221 pushed unmerged; Spartan sfs-fix-221 fresh copy)

### What was run
- Branch exp-221 off origin/exp-220 @ a157ab3 (no new code: 220 single-shot method reused frozen). Pushed to origin, unmerged.
- Spartan fresh copy /data/gpfs/projects/punim2657/sfs-fix-221 (cp -r of sfs-fix-220; .git absent by 220-method design so no pull/divergence applies). Binaries reused byte-identical: Mesh 9a0386f54b0ecc70605f9f26371a789e, Edge dc472b0e87c934b6c487ff8637209864 (md5-verified in every job log).
- Inputs ORIG-free: 214 sampled PCDs (sfs-potD-214/Dataset_Input/Point/Pot_D) + ORIG Mesh_DS/Axes + ORIG author Breaklines as ruler only.
- Ladder tree /data/gpfs/projects/punim2657/pota221_ladder, 220 schedule 90/60/45/30/20/18/16/14/12/10/8/4.5, pieces P12/P15/P22/P25/P27/P16 staged together. Clouds (pipeline input): P12 49702, P15 38542, P16 29719, P22 18378, P25 11182, P27 8470.
- Jobs (all sacct COMPLETED 0:0): ladder 33552261; edge P12@10 33552619, P15@12 33552620, P16@12 33552621, P22@12 33552622, P16@4.5 33552623; P22@12 determinism rep (12b tree) 33552765.
- Edge+score at R2 stops used single-piece trees (220 stretch pattern); scoring p221_score.py (slot matrix first, 209 pattern) re-run locally, every number below verified.

### Ladder tables (log cluster sizes desc; UN = file verts; every row sums to cloud EXACTLY)
Loose thresholds 90/60/45/30/20: all six pieces 1 cluster every step (P12: 49702/49699/49683/49628/49273; P15: 38542/38539/38533/38500/38166; P16: 29719/29719/29716/29690/29482; P22: 18378/18376/18373/18329/18090; P25: 11182/11179/11173/11121/10954; P27: 8470/8469/8465/8435/8268; residual UN 0..429). R1 correctly rejects (balance 0).
- P12 (cloud 49702): @18 3(32612/15718/814) top2 97.2 third 1.6 bal 0.482 NO; @16 3(32437/15668/804) bal 0.483 NO; @14 3(32189/15614/789) bal 0.485 NO; @12 4(28836/15555/3096/776) top2 89.3 third 6.2 bal 0.539 R1-FIRST; @10 6(27080/15480/3045/1160/762/228) top2 85.6 third 6.1 bal 0.572 R2-STOP@10; @8 holds (81.5/6.0/0.614); @4.5 18 clusters top2 62.5 NO. UN: 559/793/1110/1439/1947/2656/4859.
- P15 (cloud 38542): @18 1 NO; @16 2(36075/1715) bal 0.048 NO (one-giant correctly rejected); @14 4(17885/16025/1906/1679) top2 88.0 third 4.9 bal 0.896 R1-FIRST; @12 4(17818/15931/1886/1658) top2 87.6 third 4.9 bal 0.894 R2-STOP@12; @10/@8/@4.5 hold (83.0/79.5/78.4 top2). UN: 752/1047/1249/1527/1934/3316.
- P16 (cloud 29719): @14 5(12188/10426/2260/2136/1703) top2 76.1 third 7.6 bal 0.855 R1-FIRST; @12 5(12090/10347/2211/2081/1683) top2 75.5 third 7.4 bal 0.856 R2-STOP@12; @10/@8/@4.5 hold. UN: 1006/1307/1805/2215/3268. (Ladder vs 220: big clusters within ~10 pts.)
- P22 (cloud 18378): @14 3(8621/8280/619) top2 92.0 third 3.4 bal 0.960 R1-FIRST; @12 6(8388/7321/602/304/205/181) top2 85.5 third 3.3 bal 0.873 R2-STOP@12; @10 20 crumbs top2 17.0 NO (shatters); @8 top2 58.6 NO; @4.5 16 clusters top2 60.8 NO. UN: 858/1377/13362/6304/5403.
- P25 (cloud 11182): @16 2(9608/1116) bal 0.116 NO; @14 2(9429/1092) bal 0.116 NO; @12 ZERO clusters (whole cloud 11182 to UN, solver hole, see traps) NO; @10 6(3799/3574/989/...) top2 65.9 NO; @8 top2 65.0 NO; @4.5 7 clusters top2 62.2 NO. R2-FAIL (never satisfies).
- P27 (cloud 8470): @16 2(97/73) top2 2.0 NO; @14 4(5668/1138/951/118) third 11.2 NO (third>8); @12 top2 56.8 NO; @10 55.7 NO; @8 53.6 NO; @4.5 top2 33.6 NO. R2-FAIL (never satisfies).

### Lane scores at R2 stops (bar med<2, cov>=90%; slots verified per piece, global-min assignment)
- P12@10: ourBl1->o0 0.59/95.6 AT-BAR (n=160, 0 jumps); ourBl0 ORPHAN below-bar (vs o0 5.76/33.0, vs o1 7.06; n=191). Faces verified: 715/715 pre-dots rim riders, 0 face-interior. Render (P12_lanes.png): Bl0 traces o1's arc then shortcuts across the face interior (one 36-pt excursion, peak 13.4mm). Splitting RIGHT, one edge lane WRONG (interior shortcut). Bl0 harmed.
- P15@12: ourBl0->o1 0.64/100.0 AT-BAR (n=141, 0 jumps); ourBl1 below-bar vs either author lane alone (vs o0 5.87, vs o1 3.90; n=144) BUT combined-vs-rim med 0.83/cov 93.8 with ONE clean o1->o0 switch: it traces the true edge continuously across the author's split point. Faces verified: 629/656 riders (95.9%), 31 interior-touch pre-dots. Render (P15_lanes.png): BOTH our lanes ride the OUTER perimeter; author's o0 inner arc has no dedicated our-lane (edge loop-selection duplicated the outer loop). Splitting RIGHT, lane bookkeeping WRONG. Bl0 (ourBl0->o1) unharmed.
- P16@12: ourBl0->o1 0.86/92.5 AT-BAR; ourBl1->o0 0.52/100.0 AT-BAR. Both AT BAR, replicates 220 @12 EXACT. Bl0 unharmed.
- P22@12: both below-bar (ourBl0 3.61/32.5 n=40; ourBl1 3.37/39.6 n=53) — resegmentation merged the faces (see traps), lanes are fragments. 0/2.

### P16 re-baseline: 214 STALE CONFIRMED (overturned upward)
- Segmentation @4.5: 214-fresh 43 clusters/biggest 4799/S0 13767/S1 6134/UN 16569 vs 221-rerun 9 clusters/biggest 11261/S0 23308/S1 20721/UN 3295 (220 got 9/11261/23309/20720/3303 — replicated). Whole-structure flip, not jitter.
- Lanes @4.5: 214-fresh 0.80/76.2 + 1.45/51.8 vs 221-rerun ourBl0->o1 0.59/95.9 + ourBl1->o0 0.49/99.3, both AT-BAR (replicates 220 @4.5 EXACT). 214's P16 gate numbers are stale on the current line.
- Segmentation vs 214 for the other pieces (@4.5 cluster counts, 214 tighten-loop vs 221 single-shot): P12 18 vs 18, P15 9 vs 8, P22 14 vs 16, P25 6 vs 7, P27 9 vs 8 — all within +-2. The RED FLAG is P16-specific, not a fleet-wide shift.

### Overall: R2 generalizes 1-of-6 strict (4-of-6 splitting-level)
- R2 stop exists: P12@10, P15@12, P16@12, P22@12. FAIL: P25, P27.
- Both lanes at bar at stop: P16 only. P12/P15 split right but carry one wrong edge lane each (downstream loop-selection fault, faces verified clean). P22's stop does not survive resegmentation (0/2 lanes).
- R2 as a FROZEN splitting rule transfers beyond n=2 (4/6 stops, P16 exact-replicated) but does not deliver both-lanes-at-bar except on P16. Port talk premature.

### Traps found (for lead)
1. Single-cluster surface-file poisoning: when a piece has 1 cluster, the binary writes the PREVIOUS piece's surfaces under its name (thr_18: five files byte-identical 3411475B to P12's). UN files are safe (skipped for singles; every UN matches derived exactly). Ladder tables above use LOG sizes + file UN only. 220 was immune by luck (both pieces multi at every surfaced step).
2. Invocation-shape sensitivity (NEW, bigger than 220's seed-chaos note): single-piece P22@12 = 3 clusters (16384/602/189), deterministically (12b rep bit-identical incl. GROW-DIAG maxcurv 2.03538e+33), but ladder P22@12 (4th in invocation) = 6 balanced clusters (ladder maxcurv 3.689e+19). Same binary/inputs/threshold. Curvature garbage magnitudes are invocation-dependent; segmentation follows. P12/P15/P16 reruns match ladder within 0..200 pts (faces intact), P22 flips wholesale. Any single-number claim off a multi-piece ladder needs a single-piece confirmation.
3. P25@12 zero-cluster hole: region-growing finds 0 clusters at smoothness 12 ("Could not achieve 2 clusters after 1 iterations"), whole cloud to UN; 14 and 10 both segment. Non-monotonic in threshold — a solver hole, not a rule artifact.
4. Worker self-trap (disclosed): first fetch loop overwrote P16@12 lanes with P16@4.5 (same filenames); caught by md5 vs Spartan, re-fetched true @12 (d576516b/2effd8e0) and re-scored. Lesson: fetch multi-config pieces into per-config dirs.

### Paths
- Spartan: sfs-fix-221 (code+scripts), pota221_ladder (mesh_T*.log + thr_*/), pota221_edgeP{12_10,15_12,16_12,22_12,16_4p5,22_12b}, job logs sfs-fix-221/*221_*.out.
- Laptop: .scratch/pota221/ (p221_score.py, p221_diag.py, p221_lanedev.py, p221_seq.py, p221_render.py, P12_lanes.png, P15_lanes.png, pota221f/{lanes,author,logs}, pota221f2/{P12,P15 faces+boundary,lanes45}, pota221f3/{true P16@12 lanes}).
- 214 comparison source: pota214_pipe/mesh_stage.log (cluster counts), 214-fresh P16 lanes/scores per lead R6 on ticket 214.
## Bridge addendum (lead-measured 2026-10-21, P12@10 surfaces)
S0-S1 min gap = 0.00 at [10.8, 14.3, 465.0]; p1 1.32, p5 3.63, p50 9.52. Touching dots spread face-wide at 2mm threshold (rim proximity all round), but the ZERO is a single bridge point in the red-lane excursion zone. 221 splitting verdict amended: faces separate cleanly almost everywhere except this bridge (user m03059). P15 min-gap unmeasured (script timed out) -- 222 covers it.
