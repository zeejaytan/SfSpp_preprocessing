Status: done

## Goal
Decide the third-share retune (8% -> 10%) on evidence: confirm the retuned rule's selections for P25/P27 from existing logs, trace + score ONLY confirmed selections, and deliver the rule verdict (write R5 or drop it). P12 needs no run (223 lanes ARE the @4.5 answer). User orders m03515/m03519; lead questions m03518 answered.

## The candidate (R5, NOT frozen -- this ticket decides it)
R5 = R4 with third<=10% (all else identical: loosest-first from 90, balance>=0.5, gap-clean>=2mm, no top2 leg). Predicted: P12->@4.5 (223 lanes, known near-miss 0.63/89.0 + 0.77/98.8), P25->@10 (lanes unknown), P27->@8 (lanes unknown).

## Boundary (worker: Spartan experiment copy ONLY, fresh dir sfs-fix-226)
- STEP 1 (no runs): confirm from EXISTING mesh logs the full three legs at P25@10 and P27@8 (third/bal/gap with numbers). If either stop fails any leg on the full numbers, the descent selects differently -- follow the book where it actually goes and say so.
- STEP 2: edge runs ONLY at confirmed R5 selections lacking scored lanes (expect P25@10, P27@8; P12@4.5 = 223 reuse, NO run). Reuse 221 binaries byte-identical (record md5s); transplant pattern (223); inputs byte-identical to ladder (md5).
- MAY touch: fresh run dir + edge logs; fetch newly-run lanes to C:/PR/SfSpp_preprocessing/.scratch/pota226/lanes/ (md5 source-vs-fetched).
- MUST NOT touch: main worktree, .wt-*, other branches/stashes/bundles, tickets except appending ## Comments to THIS ticket. Author lanes in the scorer ONLY.

## Constraints
- Report slots per piece (209 pattern). Bar unchanged (med<2, cov>=90% both lanes).
- 100% dot accounting at any newly applied stop. sacct State/ExitCode per job.

## Acceptance (lead judges; numbers + cites + paths)
- Step-1 leg table (P25@10, P27@8 full numbers) + where R5 actually lands per piece (P12/P15/P22/P25/P27 + state controls unchanged by citation).
- Lane scores at each R5 selection (223 cite for P12; new runs EXACT).
- Verdict: R5-WRITE (both unknowns at bar -- give the frozen wording) or R5-DROP (any selection below bar -- name it with numbers) or R5-PARTIAL (state exactly which pieces it covers).

## Lead verdict (2026-10-21)
R5-DROP. R6: gap 33592717 + edge 33592730 COMPLETED 0:0; P27@8 re-scored EXACT (swapped o0->a1 0.87/62.9 max16.2, o1->a0 0.81/65.6 max10.6; straight 8.15/8.33); dot accounting exact; binaries/faces md5-verified; P12@4.5 = 223 reuse (no run). Scoreboard R4->R5: P15 GOOD->GOOD; P12 BAD@3->near-miss@4.5; P27 BAD@4.5->BAD@8; P25 NONE->NONE (retune prediction overturned at log check: @10/@8 gap 0.68 fail -- the check-first discipline saved a wasted trace); P22 NONE->NONE. Learnings: (1) the 10% line buys only P12-near-miss -- it does not generalize, DROP as a rule; (2) P27 fails at TWO clean stops with half-rim lanes -- short-lane class is stop-independent, needs its own leg (lane-completeness); (3) P25 never gap-clean anywhere (0.68/0.68/0.79) -- bridge class with P22; (4) P12's answer stays @4.5 (corner call still the user's). No further retune of this leg -- the line is not the problem.

## Required evidence to report
- Bottom line first: the rule verdict + per-piece selections and scores. Then jobs, md5s, tables.

## Comments (worker 226, 2026-10-21. NO main commit; NO branch -- analysis + one transplant edge run, no code touched)

### Bottom line: R5-DROP. P27@8 (the only scorable unknown) traces 0.87/62.9 + 0.81/65.6 -- both lanes below bar. P25@10 is not even selected (gap 0.68 FAIL, and @8/@4.5 also touch) so P25 stays R4-NONE under R5. P12@4.5 selected but near-miss (Bl0 89.0<90). Only P15@8 is both-at-bar. Per the book's letter (any selection below bar) that is DROP, naming P27@8; partial-picture table below for the lead's call.

### STEP 1 -- leg table (third/bal/gap; R5 = R4 with third<=10%; clouds P12 49702 / P15 38542 / P22 18378 / P25 11182 / P27 8470)
- P25@10: clusters 3799/3574/989/919/758/71 (mesh_T10.log:605-612) => third 989/11182=8.84 PASS(R5) / bal 3574/3799=0.941 PASS / gap 0.6798 FAIL (new gap226 job, S0[4.12,34.62,457.01]). Looser legs all fail (@16/@14 bal 0.116, @12 zero-hole). => descend.
- P25@8: clusters 3747/3523/973/838/702 (mesh_T8.log:581-586) => third 973/11182=8.70 PASS(R5) / bal 3523/3747=0.940 PASS / gap 0.6798 FAIL (same touch point as @10, S0[4.12,34.62,457.01]). => descend.
- P25@4.5: 5.86/0.915/gap0.79 FAIL (225 cite; gap re-verified 0.7906 EXACT as pipeline control). => P25 R5-NONE (unchanged from R4). Prediction overturned: no P25 selection, NO P25 run.
- P27@8: clusters 2418/2124/822/650/457/406/220/87 (mesh_T8.log:693-701) => third 822/8470=9.71 PASS(R5) / bal 2124/2418=0.878 PASS / gap 5.2321 PASS (gap225 cite, re-verified EXACT as control). Looser: @16 gap0.62 FAIL; @14 third11.23 FAIL; @12 third13.08 FAIL; @10 third10.78 FAIL (>10). => SELECT @8 (first pass, as predicted).
- P12: descent unchanged down to @4.5 (all looser fail gap); @4.5 third 4617/49702=9.29 PASS(R5) / bal 0.955 / gap 5.26 => SELECT @4.5. Lanes = 223 reuse (lead-verified EXACT): Bl0->o1 0.63/89.0 BELOW-BAR (1.0pp) + Bl1->o0 0.77/98.8 AT-BAR. NO P12 run.
- P15: SELECT @8 unchanged (4.72/0.737/gap5.29; lanes 0.43/97.2 + 0.75/97.6 both AT-BAR, 222 cite).
- P22: R5-NONE unchanged (every balanced step touches, gaps 0.00-0.68).
- Controls unchanged by citation: P16 SELECT @10 (7.19/0.883/gap5.89; lanes 0.61/97.2 + 0.49/100.0); P01 SELECT @8 (4.63/0.887/gap4.96; lanes 0.61/100.0 + 0.61/96.6).
- Mechanism note: P25's touch point persists across thresholds (symmin 0.6798 at identical coords @10/@8; @4.5 nearby 0.79) -- same persistent-touch class as the P12/P27 coincidences in 225. Bridge class extends to P25.

### STEP 2 -- edge P27@8 ONLY (fresh tree pota226_edgeP27_8, 223/225 transplant pattern)
- Binaries reused byte-identical (job log): Mesh 9a0386f54b0ecc70605f9f26371a789e, Edge dc472b0e87c934b6c487ff8637209864 (== 221 pattern). NO mesh rerun.
- Faces tree==ladder: 46fb4f8363ca19295f9409c774c479d2 / def6c9ed0d148efbacab2a19236faf06 (both Temp/Data and Dataset/Surfaces copies). Inputs unchanged vs 225 tree: Point c3b1bb6975184a29de9d134500e2ba25, Mesh 9d83b39feaf19485c68770fa5876e0eb, Axis 75a0880107fb7b0c6470a0cbc94fdbbb.
- Dot accounting at applied stop P27@8: 2418+2124+822+650+457+406+220+87=7184 clusters + UN 1286 (thr_8 unclustered header) = 8470 EXACT.
- Jobs (sacct COMPLETED 0:0): gap 33592717 (P25@10/@8 + P25@4.5/P27@8 controls); edge 33592730 (P27@8, exit 0, 8 LOOP-SELECT).
- P27@8 lane scores vs author (local rescore226.py, 209 slot matrix; refs o0=48 o1=49; bar med<2, cov>=90%): straight sums 16.48 vs swapped 1.68 => SWAPPED slots (o0->a1, o1->a0). o0->a1: n=62 med=0.87 cov=62.9 max=16.2 jumps=0 gapmax=4.3 endgap=1.8 BELOW-BAR. o1->a0: n=64 med=0.81 cov=65.6 max=10.6 jumps=0 gapmax=4.5 endgap=1.8 BELOW-BAR. ==> R5-SELECTS-BAD.
- Fetched lanes (md5 source==fetched MATCH): Pot_D_Piece_27_Breakline_0.pcd 50e057b9526c106a43e07766b069e733 / _1.pcd acaa561b64a226ed8225e67790a80bc7 (+ .xyz pair 3a8e6903/ce0bbd78) in C:/PR/SfSpp_preprocessing/.scratch/pota226/lanes/. Stepring sidecars 0-byte, not fetched (222 pattern).

### Verdict sentence
- R5-DROP: the retune buys P12@4.5 (near-miss 89.0, within 2 dots of bar) but P27@8 -- the only genuinely new selection -- traces two half-rim lanes (cov 62.9/65.6) despite gap-clean faces holding only 53.6% of the cloud in top2. Gap-clean != trace-correct on fragmented pieces (same lesson as 225-P27@4.5). R5 covers P15 fully, P12 nearly, nothing else.

### Paths
- Spartan: sfs-fix-226 (gap226sym.py, gap226.sbatch, gap226_33592717.out/.err, run_226_edge.sbatch), pota226_edgeP27_8 (run_226_edge.sbatch, edge_8.log, edge226_33592730.out/.err, Dataset/Breaklines lanes).
- Laptop: .scratch/pota226/ (gap226sym.py, gap226.sbatch, run_226_edge.sbatch, rescore226.py, lanes/4 P27 files).
- Main worktree, .wt-*, other branches/stashes/bundles untouched. Author lanes ruler ONLY (scorer-side). No pull needed (fresh dirs, no .git); divergence N/A.


**Evidence-path note (2026-10-23):** paths under .scratch/pota1xx_repro/ and .scratch/pota22x/ cited above were removed by the scratch cleanup of this date (untracked intermediates; not recoverable). The numbers, quotes and verdicts in this ticket stand as recorded -- do not chase those paths or re-derive from them.
