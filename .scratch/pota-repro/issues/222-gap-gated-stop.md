# 222 - Gap-gated stopping rule (user rule m03059, 221 follow-up)

Status: done
Answers: none (splitter-method trial; context 220/221, rulers 214/217)

## Goal
Test the user's rule: keep tightening until the FIRST step with two big balanced faces AND a clean gap between them. Lead-measured on P12@10: S0-S1 min gap = 0.00 at [10.8, 14.3, 465.0] (bridge; rest of rim median ~9.5mm apart) -- R2 stopped while a bridge still joined the faces on one side, both lips pooled, walk crossed (user m03059; amends 221 "splitting RIGHT" to "split leaves a bridge"). Question: does a 2-big-balanced AND gap-clean step exist before shattering, per piece?

## Boundary (worker: read-only except where named)
- PREFER analysis-only: the pota221_ladder tree (Spartan sfs-fix-221) already holds thr_* surfaces per threshold per piece -- compute S0<->S1 min-gap + gap-cleanliness per step from EXISTING outputs. New mesh runs only if a step's surfaces are missing/poisoned (trap 1: single-cluster files repeat the previous piece -- exclude by md5).
- If code is touched (gap metric inside binary): branch exp-222 off origin/exp-221, unmerged. Otherwise no branch needed -- say so.
- MAY run: edge + score vs author lanes at the gap-clean stop IF one is found (bar med<2, cov>=90%, slots per piece, 209 pattern). Spartan work in sfs-fix-221 tree or fresh copy; pull --ff-only; STOP on divergence.
- Do NOT touch: main worktree (user 204-edit live), .wt-*, other branches, stashes, bundles, other tickets (append Comments here only). ORIG-free (author lanes as ruler only).

## Constraints
- Gap-clean definition is the worker's first deliverable (lead suggestion: min S0-S1 separation > wall-thickness scale, e.g. >=2mm, AND/OR overlap fraction ~0%; must also hold P16/P01 controls without breaking their current good splits).
- R1 balance conditions frozen from 220 (top2>=70%, third<=8%, 2nd/1st>=0.5). R3 = first threshold satisfying R1 AND gap-clean. Record R3 per piece (or NONE).
- 100% dot accounting where recomputed; reuse 221 numbers where untouched (cite, don't redo).
- Report channel = this ticket's Comments + completion notice (no send_message downward).

## Acceptance (lead judges; numbers + cites + paths)
- Per piece (P12/P15 primary, P16/P01 controls): threshold -> (top2, third, bal, min-gap, gap-clean?) table; R3 stop or NONE with reason (shatters first / never balances / never separates).
- Stretch (only if R3 found): lane scores at R3 vs bar; Bl0 unharmed?
- Verdict: does the user's rule exist on each piece? If NONE anywhere before shattering, splitter needs bridge-cutting -- report that, propose nothing ungrounded.

## Required evidence to report
- Gap tables per piece (with step surfaces cited), R3 stops or NONE-reasons, stretch scores if run, sacct State/ExitCode for any jobs, branch (only if code touched, unmerged).

## Lead verdict (2026-10-21)
ACCEPT. R6: 6/6 sacct COMPLETED 0:0; P12 bridge cross-checked against lead measurement (worker 0.18 vs lead 0.00, distributions p50 9.51/9.52 identical, verdict identical); all four R3 lane scores re-run locally EXACT (P15@8 0.43/97.2 + 0.75/97.6; P16@10 0.61/97.2 + 0.49/100.0; n's + straight slots match); no branch (analysis-only, consistent). Rule exists 3/4 (P15/P16/P01), NONE on P12 (bridge-cutting class). P15's fix is the headline: @8 lands both lanes where @12 orphaned one. Lanes + scorer committed in .scratch/pota222/. RECOVERY NOTE: lead's first verdict-write clobbered the worker Comments body with a partial-read splice; spec head restored from git, worker block re-emitted verbatim by worker on request and spliced below -- verified complete before commit. Infra note: worker->parent send_message refused twice (ticket-50 pattern); finish-notification + ticket Comments carried the result -- no evidence lost.

## Comments (worker 222, 2026-10-21. NO main commit; NO branch -- analysis-only, no code touched)

### Gap-clean definition (deliverable 1): strict min-S0<->S1-separation >= 2mm
- Adopted the lead's suggested wall-thickness scale verbatim: gap-clean <=> symmetric min S0<->S1 separation >= 2mm (symmetric min verified = one-directional min on all 22 pairs, both directions agree to 4 decimals). Overlap fraction (frac<2mm) reported alongside as the AND/OR leg.
- Control gate: P01's good R2 stop (@8) must stay gap-clean (it does: min 4.96); P16's good R2 stop (@12) is min 0.53 so the strict rule rejects it -- the rule's alternative P16 stop (@10) is therefore stretch-tested below.
- Sensitivity recorded (not run): under a p1>=2mm variant, R3 = P12@8 / P15@8 / P16@12 (=R2 exactly) / P01@8. I.e. the single-point-robust variant keeps P16 exactly at its fully-good stop.

### What was run (all sacct COMPLETED 0:0; Spartan outputs only, nothing committed)
- No code touched, no branch (say so per boundary: analysis-only on EXISTING surfaces). Work dirs (fresh, uncommitted): /data/gpfs/projects/punim2657/pota222_gap/ (scripts+logs), pota222_edgeP15_8r3, pota222_edgeP16_10r3. Binaries reused byte-identical via 221 pattern: Mesh 9a0386f54b0ecc70605f9f26371a789e, Edge dc472b0e87c934b6c487ff863720 (md5 in stretch log). No pull needed (fresh dirs, no .git); main worktree, .wt-*, other branches/stashes/bundles untouched.
- Jobs: gap 33583815 (22-pair S0->S1 min+p1/p5/p50+frac, 22s), gapsym 33583968 (symmetric-min check), geo 33584157 (contact geography at 6 key stops), stretch 33584366 (single-piece mesh+edge P15@8 + P16@10, 221 run_221_edge pattern), validate 33584400 (scorer vs 221 lanes: EXACT -- P15@12 0.64/100.0 + 5.87/3.90, P16@12 0.86/92.5 + 0.52/100.0), score 33584582 (R3 lanes).
- Poisoning exclusions by md5 (verified, extends 221 trap 1): 221-thr_18 all-but-P12 repeat P12's S0/S1; 221-thr_16 P16+P22 repeat P15's; 221-thr_12 P25 repeats P22's (zero-cluster hole); 220-thr_14 has no P01 files (single-giant step, unsurfaced). All excluded pairs listed as n/a below; 220 immune confirmed (all surfaced steps multi).

### Per-piece tables (R1 from 220/221, cited; gap measured here; R1 cells re-verified from mesh logs where asserted)
- P12 (cloud 49702): thr->(top2, third, bal | symmin, p1, frac<2mm | gap-clean?) -- @18 (97.2,1.6,0.482,NO | 0.00,0.88,4.25%,no) @16 (..,..,0.483,NO | 0.00,0.95,3.91%,no) @14 (..,..,0.485,NO | 0.17,1.00,3.74%,no) @12 (89.3,6.2,0.539,R1-FIRST | 0.17,1.07,3.14%,no) @10 (85.6,6.1,0.572,yes | 0.18,1.31,2.05%,no) @8 (81.5,6.0,0.614,yes | 0.67,2.56,0.65%,no) @4.5 (62.5,..,..,NO | 5.26,6.21,0.00%,YES). R3 = NONE (gap never clean while balanced; only shattered @4.5 separates). Near-miss: @8 min 0.67, 0 pts <0.5mm.
- P15 (cloud 38542): @16 (..,..,0.048,NO | 0.00,0.69,2.82%,no) @14 (88.0,4.9,0.896,R1-FIRST | 0.00,0.73,4.67%,no) @12 (87.6,4.9,0.894,yes | 0.11,0.74,4.61%,no) @10 (83.0,..,..,yes | 0.11,1.26,1.84%,no) @8 (79.5,4.7,0.737,yes, log-verified | 5.29,6.74,0.00%,YES) @4.5 (78.4,..,..,yes | 6.55,6.81,0.00%,YES). R3 = @8.
- P16 (cloud 29719): @14 (76.1,7.6,0.855,R1-FIRST | 0.53,4.54,0.27%,no) @12 (75.5,7.4,0.856,yes | 0.53,4.53,0.27%,no) @10 (73.9,7.2,0.883,yes, log-verified | 5.89,6.15,0.00%,YES) @8 (..,..,..,yes | 5.89,..,0.00%,YES) @4.5 (..,..,..,yes | 5.89,..,0.00%,YES). R3 = @10. (@18/@16 poisoned, n/a.)
- P01 control (cloud 149013, 220 tree): @14 (98.05,0.52,0.008,NO | n/a unsurfaced) @12 (96.73,0.74,0.014,NO | 0.00,3.15,0.59%,no) @10 (94.76,1.33,0.867,R1-FIRST | 0.00,0.81,3.96%,no) @8 (86.35,4.63,0.887,yes | 4.96,5.96,0.00%,YES) @4.5 (85.41,2.62,0.883,yes | 5.07,5.96,0.00%,YES). R3 = @8 (= R2 stop exactly).

### Stretch: lane scores at R3 vs bar (med<2, cov>=90%; slots per piece, 209 pattern; scorer validated EXACT vs 221)
- P15@8: ourBl0->o1 0.43/97.2 AT-BAR (n=145, 0 jumps, gapmax 1.8); ourBl1->o0 0.75/97.6 AT-BAR (n=124, 0 jumps). STRAIGHT slots (swap sums far worse: 8.6s). Bl0 unharmed. NOTE: fixes the @12 orphan -- at R3 both lanes land, one per author lane.
- P16@10: ourBl0->o1 0.61/97.2 AT-BAR (n=145, 0 jumps); ourBl1->o0 0.49/100.0 AT-BAR (n=134, 0 jumps). Straight slots. Bl0 unharmed.
- P01@8: not re-run; 220 measured both AT-BAR (0.61/100.0 + 0.61/96.6) -- R3 coincides with the known-good R2 stop, no harm possible.
- Ladder-consistency (invocation-shape trap check): single-piece reruns match ladder faces -- P15@8 6 clusters, S0 +2pts/S1 +2pts; P16@10 6 clusters, S0 +27/S1 +2pts. No P22-style flip; stretch scored the same segmentation the gap was measured on.

### Verdict per piece (user's rule: first 2-big-balanced AND gap-clean step)
- P12: NONE before shattering. Every balanced step (@12/@10/@8) still touches (min 0.17/0.18/0.67); only the shattered @4.5 separates, where R1 already fails. Splitter needs bridge-cutting on this piece -- consistent with the 221 render (red interior shortcut). Near-miss @8 recorded for the p1-variant.
- P15: R3=@8, both lanes AT-BAR. Rule WORKS and improves on R2 (@12 left one orphan lane; @8 lands both).
- P16 control: strict rule rejects the fully-good @12 stop (67-pt touch patch, min 0.53) but R3=@10 is equally good (both AT-BAR). Rule does not break P16 -- it moves one step tighter to an equally good stop.
- P01 control: R3=@8 IS the R2 stop. Rule holds without breaking the good split.
- Overall: rule exists on 3/4 pieces (P15/P16/P01); NONE on P12. Bridge-cutting needed for the P12 class; proposing no mechanism (nothing ungrounded).

### Mechanism notes (refines 221 'split leaves a bridge')
- Contacts at R1/R2 stops are face-wide near-touch on surface sampling, NOT single-point bridges: d<2mm pts -- P12@10 1111 (bbox spans whole wall x38/y63/z62), P15@12 1656 (x89 band), P01@10 6031 (whole piece). Exceptions: P16@12 is a tight 67-pt patch (x5.3/y4.6/z2.4, 0 pts <0.5mm) and P12@8 a localized 331-pt patch ~8mm from the lead's bridge point (0 pts <0.5mm).
- Methods note: my P12@10 symmin 0.18 at [30.2,48.1,414.0] vs lead's 0.00 at [10.8,14.3,465.0] -- distributions agree (p50 9.51 vs 9.52, p1 1.31 vs 1.32); verdict identical (bridge present, fail). Sub-2mm extreme-min difference between samplings; both << threshold.
- p50 wall scale 7.5-9.5mm (P12/P15/P01) and 7.5mm (P16) -- the 2mm gate sits well below wall thickness and well above the bridge zeros; no tuning evident.

### Paths & evidence
- Spartan: pota222_gap/{gap222.py,gap222sym.py,gap222geo.py,score222.py,stretch222.sbatch,gap_33583815.out,gap_sym_33583968.out,gap_geo_33584157.out,stretch_33584366.out,score_val_33584400.out,score_r3_33584582.out}; pota221_ladder/thr_* (+mesh_T*.log, md5 table in worker report); pota220_ladder/thr_*; pota222_edgeP15_8r3 + pota222_edgeP16_10r3 (mesh/edge logs, Dataset/Breaklines lanes). sacct: 33583815, 33583968, 33584157, 33584366, 33584400, 33584582 -- all COMPLETED 0:0.
- Branch: none (no code touched -- stated per boundary).

### Lane fetch for lead R6 (worker 222, 2026-10-21)
- Fetched the 4 R3-stop lane files to C:/PR/SfSpp_preprocessing/.scratch/pota222/lanes/ via ssh_download (nothing else touched). md5 source vs fetched -- all MATCH:
  - source 9c959f221193970cbaafa56ca70f8be2 Pot_D_Piece_15_Breakline_0.xyz == fetched 9c959f221193970cbaafa56ca70f8be2 (7810 B, 145 pts)
  - source d6c7d8285ad4b16584244cd044394e49 Pot_D_Piece_15_Breakline_1.xyz == fetched d6c7d8285ad4b16584244cd044394e49 (6626 B, 124 pts)
  - source 1b1cf0057931ff9c37cd21bda78f31bc Pot_D_Piece_16_Breakline_0.xyz == fetched 1b1cf0057931ff9c37cd21bda78f31bc (7816 B, 145 pts)
  - source c6cc3b332ade9f3840b7900d5d2e7ad8 Pot_D_Piece_16_Breakline_1.xyz == fetched c6cc3b332ade9f3840b7900d5d2e7ad8 (7205 B, 134 pts)
- Counts match the scored n's (145/124/145/134). Stepring sidecars are 0-byte on source (d41d8cd9...) and were not fetched.
