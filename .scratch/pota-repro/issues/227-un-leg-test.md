Status: done

## Goal
Test the UN-share leg (candidate R6) mechanically on all five 214-MIXED pieces + controls P16/P01: does balance + gap-clean + UN<=12% (loosest-first, NO third-share, NO top2 leg) select stops whose lanes score at bar? P01@8's UN share is the leg's first validity check (confirm it from 220 logs before anything else). User order m03551; reasoning m03550.

## The candidate (R6, NOT frozen -- this ticket decides it)
R6 = the LOOSEST threshold (descend 90 toward 4.5; continue to 3, 2 only where those stages exist, i.e. P12) satisfying ALL THREE: (a) balance 2nd/1st >=0.5; (b) gap-clean: symmetric min S0<->S1 separation >=2mm (222 pattern); (c) UN share <=12% of cloud (UN = unclustered dots from mesh log headers; 225 pattern). FIRST pass wins. Rationale: UN grows with fragmentation (P12 5.3->9.8->18.4%; P27@4.5 51%, @8 15%), pointing the right way where third-share pointed backwards; predicted line ~12% passes P12@4.5 (9.8) and fails P12@3 (18.4), P27@8 (15.2), P27@4.5 (51%).

## Boundary (worker: Spartan experiment copy ONLY, fresh dir sfs-fix-227)
- STEP 1 (no runs): FIRST confirm P01@8 UN share from 220 mesh logs. If it exceeds 12%, STOP the leg test and report R6-DEAD-ON-ARRIVAL with the number (do not trace anything).
- STEP 2 (no runs): full three-leg table per piece from EXISTING mesh/gap logs (221 ladder + 224 P12 thr_3/thr_2 + 220 P01/P16 where needed). Reuse 225/226 gap numbers where citable; re-run gap ONLY where a needed stop was never measured (one job max expected).
- STEP 3: edge runs ONLY at R6 selections lacking scored lanes. Reuse 221 binaries byte-identical (record md5s); transplant pattern (223); inputs byte-identical to ladder (md5). P12@4.5 = 223 reuse (NO run); P15@8 = 222 reuse; P16/P01 = cite 222/220.
- MAY touch: fresh run dir + logs; fetch newly-run lanes to C:/PR/SfSpp_preprocessing/.scratch/pota227/lanes/ (md5 source-vs-fetched).
- MUST NOT touch: main worktree, .wt-*, other branches/stashes/bundles, tickets except appending ## Comments to THIS ticket. Author lanes in the scorer ONLY.

## Constraints
- Report slots per piece (209 pattern). Bar unchanged (med<2, cov>=90% both lanes).
- 100% dot accounting at any newly applied stop. sacct State/ExitCode per job.

## Acceptance (lead judges; numbers + cites + paths)
- P01@8 UN share (validity gate) + per-piece R6 tables, selections, lane scores (new runs EXACT, old cites re-verified EXACT).
- Verdict: R6-WRITE (frozen wording for the rulebook) / R6-DROP (name the failing piece with numbers) / R6-PARTIAL (exact coverage). If R6 selects P12@4.5, the P12 corner call resolves as ACCEPT-with-corner-noted (user m03550 context).

## Lead verdict (2026-10-21)
R6-DROP as a complete rule, R6-KEPT as the stopping rule. R6: job 33593416 COMPLETED 0:0; P27@12 re-scored EXACT (swapped 0.83/58.5 + 0.91/68.9; straight 8.10/8.23); P01@8 UN 3.38% gate passes; cites re-verified EXACT; binaries/faces md5-verified; zero new gap jobs (all stops pre-measured). Coverage 3.5/7: P15@8/P16@10/P01@8 GOOD, P12@4.5 near-miss, P27@12 BAD, P22/P25 NONE (correct -- nothing good exists). Commonality finding (user program m03559): each leg has exactly one job -- balance rejects one-giant (@18s), gap rejects bridged (@10/@8s), UN rejects fragmented (@3/@2s); good-stop gaps cluster ~5mm (5.29/5.89/4.96/5.26, likely wall scale -- necessary not sufficient, P27@8 5.23 proves it). P27 fails at three clean stops with wandering lanes (longer than author, excursions to 16mm) -- needs the 4th leg (lane rim-adherence, author-free) as acceptance AFTER stopping. No further cutoff moves.

## Required evidence to report
- Bottom line first: verdict + per-piece selections and scores. Then jobs, md5s, tables.
## Comments (worker 227, 2026-10-21. NO main commit; NO branch -- one transplant edge run, no code touched)

### Bottom line: R6-DROP. P27@12 (the R6-novel selection) traces 0.83/58.5 + 0.91/68.9 -- both lanes below bar. P22/P25 select NONE. P12@4.5 near-miss (89.0). Only P15@8, P16@10, P01@8 are both-at-bar. Partial coverage: 3/7 GOOD, 1 near-miss, 1 BAD, 2 NONE.

### STEP 1 -- validity gate: PASS (no STOP)
- P01@8: mesh_T8.log clusters 68197/60469/6906/2866/1913/1902/1075/642 sum 143970 + UN 5043 (thr_8 header element vertex 5043) = 149013 EXACT. UN share 5043/149013 = 3.38% <= 12%. Gate PASSES -- leg test proceeds. (Spartan pota220_ladder.)

### STEP 2 -- R6 three-leg tables (loosest-first 90 -> 4.5; legs: bal=c2/c1>=0.5, gap symmin>=2mm, UN<=12%; clouds P12 49702 / P15 38542 / P16 29719 / P22 18378 / P25 11182 / P27 8470 / P01 149013)
- Balance from mesh_T*.log region clusters (221 ladder + 220 ladder); gap from gap_sym_33583968 (222) + gap225_33592310 (225) + gap226_33592717 (226) -- every R6-relevant stop pre-measured, ZERO new gap jobs needed; UN from thr_* unclustered.ply headers (single-cluster steps: derived residual, balance-fail regardless).
- P12: @18 .482 F(bal) / @16 .483 F / @14 .485 F / @12 .539+gap0.17 F(gap) / @10 .572+gap0.18 F / @8 .614+gap0.67 F / @4.5 .955+gap5.26+UN9.78%(4859) PASS -> SELECT @4.5.
- P15: @16 .048 F / @14 .896+gap0.00 F / @12 .894+gap0.11 F / @10 .803+gap0.11 F / @8 .737+gap5.29+UN5.02%(1934) PASS -> SELECT @8.
- P16: @14 .855+gap0.53 F / @12 .856+gap0.53 F / @10 .883+gap5.89+UN6.07%(1805) PASS -> SELECT @10.
- P22: @14 .960+gap0.00 F / @12 .873+gap0.00 F / @10 .748+gap0.68+UN72.7%(13362) F / @8 .804+gap0.00+UN34.3%(6304) F / @4.5 .701+gap0.17+UN29.4%(5403) F -> NONE.
- P25: @16 .116 F / @14 .116 F / @12 zero-cluster hole F / @10 .941+gap0.68+UN9.59%(1072) F(gap) / @8 .940+gap0.68+UN12.51%(1399) F / @4.5 .915+gap0.79+UN18.96%(2120) F -> NONE.
- P27: @16 .753+gap0.62+UN98.0%(8300) F / @14 .201 F(bal; UN7.02% gap0.00 also F) / @12 .855+gap2.75+UN8.89%(753) PASS -> SELECT @12 (mesh_T12.log:662-669; 2591+2216+1108+942+745+115=7717+753=8470 EXACT).
- P01: @14 .008 F / @12 .014 F / @10 .867+gap0.00 F / @8 .887+gap4.96+UN3.38%(5043) PASS -> SELECT @8 (= R2/R4/R5 stop, control holds).
- Mechanism note: the UN leg does not fix the short-lane class -- P27 passes it at @12 with faces holding 56.7% of the cloud yet traces half-rim lanes (same lesson as 225/226 gap-clean!=trace-correct, now UN-clean!=trace-correct). P25@8 fails UN (12.51%) at the same touch point as @10 (0.6798 both) -- persistent-touch class.

### STEP 3 -- edge P27@12 ONLY (fresh tree pota227_edgeP27_12, 223/225/226 transplant pattern)
- NO mesh rerun. Faces tree==ladder byte-identical both copies: 3ec860a262326e0bba4e94a252bf584a / 1f9d1ca3b62d5f84cb11e62b985ce16c. Inputs == 226 (threshold-independent): Point c3b1bb6975184a29de9d134500e2ba25, Mesh 9d83b39feaf19485c68770fa5876e0eb, Axis 75a0880107fb7b0c6470a0cbc94fdbbb. Binaries byte-identical (job log): Mesh 9a0386f54b0ecc70605f9f26371a789e, Edge dc472b0e87c934b6c487ff8637209864 (== 221 pattern).
- Job 33593416 sacct COMPLETED 0:0 (Elapsed 00:00:06, edge-only), exit 0, 8 LOOP-SELECT. No pull needed (fresh dirs, no .git); main worktree, .wt-*, branches/stashes/bundles untouched. Author lanes ruler ONLY.
- Dot accounting at applied stop P27@12: 7717 + 753 = 8470 EXACT.
- P27@12 lane scores vs author (local rescore227.py, 209 slot matrix; refs o0=48 o1=49; SWAPPED o0->a1/o1->a0): o0->a1 n=65 med=0.83 cov=58.5 max=17.7 jumps=0 BELOW-BAR. o1->a0 n=61 med=0.91 cov=68.9 max=10.1 jumps=0 BELOW-BAR. ==> R6-SELECTS-BAD.
- Fetched lanes (md5 source==fetched MATCH): Pot_D_Piece_27_Breakline_0.pcd fb12e6fc710e618b83f987212f66ddd8 / _1.pcd 604583ea6d9b1bcd7d53e5ac3f18769c (+ .xyz pair 415ad9dd/93fb026e) in C:/PR/SfSpp_preprocessing/.scratch/pota227/lanes/. Stepring sidecars 0-byte, not fetched (222 pattern).

### Reused selections (NO runs; cited scores re-verified EXACT locally via reverify227.py)
- P12@4.5 (223 lanes): swapped o0->a1 0.63/89.0 n172 + o1->a0 0.77/98.8 n160 -- near-miss (Bl0 1.0pp short). P15@8 (222): 0.43/97.2 + 0.75/97.6 GOOD. P16@10 (222): 0.61/97.2 + 0.49/100.0 GOOD. P01@8 (220): 0.61/100.0 + 0.61/96.6 GOOD.

### Verdict sentence
- R6-DROP, naming P27@12 (0.83/58.5 + 0.91/68.9): the UN leg buys P12@4.5-near-miss over R4's @3 but selects a clean-faced stop whose lanes cover half the rim each. Coverage: P15/P16/P01 GOOD (3/7), P12 near-miss, P27 BAD, P22/P25 NONE (bridge class -- every balanced step touches, 0.00-0.79 across 11 measured steps). No further retune of this leg -- the line is not the problem; the short-lane class needs its own leg (lane-completeness).

### Paths
- Spartan: sfs-fix-227 (run_227_edge.sbatch), pota227_edgeP27_12 (run script, edge_12.log, edge227_33593416.out/.err, Dataset/Breaklines lanes).
- Laptop: .scratch/pota227/ (lanes/4 P27 files, rescore227.py, reverify227.py). sacct: 33593416 COMPLETED 0:0.



**Evidence-path note (2026-10-23):** paths under .scratch/pota1xx_repro/ and .scratch/pota22x/ cited above were removed by the scratch cleanup of this date (untracked intermediates; not recoverable). The numbers, quotes and verdicts in this ticket stand as recorded -- do not chase those paths or re-derive from them.
