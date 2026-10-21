Status: done

## Goal
Test the repaired stopping rule (R4, frozen below) on the five 214-MIXED pieces (P12/P15/P22/P25/P27): does it select a stop whose lanes score at bar, with no new segmentation? Controls P16/P01 (existing lanes) must keep their good stops. User order m03448.

## The rule (R4, FROZEN -- do not retune)
R4 = the LOOSEST threshold (proven search direction, user m03460: start loosest, tighten down) satisfying ALL THREE: (a) third cluster <=8% of cloud; (b) balance 2nd/1st >=0.5; (c) gap-clean: symmetric min S0<->S1 separation >=2mm (222 pattern). Descend the existing ladder from 90 toward 4.5 (continue to 3, 2 only where those stages exist, i.e. P12); FIRST pass wins = the loosest honest stop. The top2>=70% leg is DROPPED (224 verdict: it punishes complex pieces for being complex). Rationale for loose-first (lead): tightest-first risks stopping inside fragmentation -- P12 @3 satisfies gap/balance but its lanes break (Bl1 80.8); loose-first stops at @4.5 by construction and never descends into the fragment zone.

## Boundary (worker: Spartan experiment copy ONLY, fresh dir sfs-fix-225)
- NO re-segmentation: reuse the existing ladder surfaces byte-identical (221 ladder + 220 ladder for P01; 224 thr_3/thr_2 for P12 -- verify md5s).
- MUST reuse 221 mesh/edge binaries byte-identical for any edge run (record md5s). Edge runs ONLY where the R4-selected stop has no scored lanes yet (P12@4.5: 223 lanes exist; P15@8: 222 lanes exist; P22/P25/P27/P16/P01: run edge iff missing).
- MAY touch: fresh run dir + edge logs; fetch newly-run lanes to C:/PR/SfSpp_preprocessing/.scratch/pota225/lanes/ (md5 source-vs-fetched).
- MUST NOT touch: main worktree, .wt-*, other branches/stashes/bundles, tickets except appending ## Comments to THIS ticket. Author lanes in the scorer ONLY.

## Constraints
- Report slots per piece (209 pattern). Bar unchanged: med<2, cov>=90% both lanes.
- 100% dot accounting per applied stop (220 pattern): clusters+UN=cloud.

## Acceptance (lead judges; numbers + cites + paths)
- Per piece (5+2 controls): ladder rows relevant to R4 (cite existing tables where reused, re-verify the three legs from mesh logs), R4-selected stop, lane scores at stop, verdict: R4-SELECTS-GOOD / R4-SELECTS-BAD (scores below bar -- failure with numbers) / R4-NONE (no stop satisfies all three).
- Controls: P16 (expect @10 or @12, both known-good -- cite 222/220 scores, no new runs) and P01 (expect @8 -- cite 220). If R4 moves a control off its good stop, that is a headline finding, not a footnote.
- sacct State/ExitCode for any new job; binary/surface/lane md5s.

## Lead note (2026-10-21, user m01642)
P12 third-share correction: mesh-log 9.29% (not ~6%) -- frozen R4 as written walks past @4.5 to @3. User decision: OPTION 1 -- no mid-run amendment; worker reports all five mechanically (P12 as the book selects it), rule repair (cutoff vs floor vs accept) made once with full evidence.

## Required evidence to report
- Per-piece: R4 table (legs per threshold), selected stop, lane scores, verdict class. Bottom line first: on how many of 5 does R4 select a both-at-bar stop (vs R2's record: 1/6 strict, 4/6 splitting-level).

## Comments (worker 225, 2026-10-21. NO main commit; NO branch -- analysis + one transplant edge run, no code touched)

### Bottom line: 1 of 5 R4 selects a both-at-bar stop (P15@8). P12 SELECTS-BAD (@3, Bl1 80.8), P27 SELECTS-BAD (@4.5, cov 55/62), P22 R4-NONE, P25 R4-NONE. Controls hold: P16@10 both-at-bar, P01@8 both-at-bar.

### What was run
- Fresh Spartan dir sfs-fix-225 (scripts + job logs only; no .git so no pull/divergence applies). Binaries reused read-only from sfs-fix-221/build-220, md5-verified in job log: Mesh 9a0386f54b0ecc70605f9f26371a789e, Edge dc472b0e87c934b6c487ff8637209864 (== 221 pattern).
- NO re-segmentation. Gap job 33592310 (sacct COMPLETED 0:0): gap225sym.py (222 symmetric-min pattern) on 15 candidate steps from EXISTING surfaces (221 ladder + 224 P12 thr_3/thr_2 trees); md5 section in gap225_33592310.out doubles as poison check (thr_12 P25 repeats P22, thr_16 P22 repeats P15, thr_18 P25 repeats P22 -- all single-cluster steps, none used).
- Edge job 33592413 (sacct COMPLETED 0:0): P27@4.5 ONLY -- transplant tree pota225_edgeP27_4p5 (223 pattern: ladder faces byte-identical, scaffolding from pota221_edgeP22_12, P27 inputs from 214/ORIG). All other selected stops already had scored lanes (P12@3: 224; P15@8, P16@10: 222; P01@8: 220) -- cited and re-verified locally EXACT.
- Scoring: Spartan score222.py pattern + local .scratch/pota225/rescore225.py (both slot matrices, 209 pattern). P27 lanes fetched to .scratch/pota225/lanes/ (4 files, md5 source==fetched, sizes match).
- Main worktree, .wt-*, other branches/stashes/bundles untouched. Author lanes ruler ONLY.

### R4 tables (loosest-first descent 90 -> 4.5 -> 3/2 P12-only; legs: third<=8% cloud, bal=c2/c1>=0.5, gap symmin>=2mm; clouds P12 49702 / P15 38542 / P16 29719 / P22 18378 / P25 11182 / P27 8470 / P01 149013)
- P12: @18 (.482 bal FAIL) @16 (.483 FAIL) @14 (.485 FAIL) @12 (6.23/.539/gap0.17 FAIL) @10 (6.13/.572/gap0.18 FAIL) @8 (5.98/.614/gap0.67 FAIL) @4.5 (9.29 third FAIL / .955 / gap5.26) @3 (6.79/.745/gap5.26 PASS) -> SELECT @3. Lanes (224, local EXACT): o0->a1 0.61/99.4 AT-BAR (n160, 0 jumps); o1->a0 0.71/80.8 BELOW-BAR (n146, 1 jump/12.3). ==> R4-SELECTS-BAD.
- P15: @16 (bal .048 FAIL) @14 (4.94/.896/gap0.00 FAIL) @12 (gap0.11 FAIL) @10 (gap0.11 FAIL) @8 (4.72/.737/gap5.29 PASS) -> SELECT @8. Lanes (222, local EXACT): o0->a1 0.43/97.2, o1->a0 0.75/97.6, straight slots, 0 jumps. ==> R4-SELECTS-GOOD.
- P22: @14 (3.37/.960/gap0.00 FAIL) @12 (3.28/.873/gap0.00 FAIL) @10 (1.83/.748/gap0.68 FAIL) @8 (3.05/.804/gap0.00 FAIL) @4.5 (2.73/.701/gap0.17 FAIL) ==> R4-NONE (every balanced step touches).
- P25: @16 (bal .116 FAIL) @14 (bal .116 FAIL) @12 (zero-cluster hole FAIL) @10 (8.85 third FAIL) @8 (8.70 third FAIL) @4.5 (5.86/.915/gap0.79 FAIL) ==> R4-NONE.
- P27: @16 (third 0 / bal .753 / gap0.62 FAIL -- 97/73-pt crumb pair correctly rejected by gap, not size) @14 (11.23 third FAIL) @12 (13.08 FAIL) @10 (10.78 FAIL) @8 (9.70 FAIL) @4.5 (5.07/.776/gap7.36 PASS) -> SELECT @4.5. Lanes (new run, Spartan==local EXACT, SWAPPED slots o0->a1/o1->a0): 1.50/54.9 (n51) + 0.92/62.0 (n50), 0 jumps. ==> R4-SELECTS-BAD.
- P16 control: @14 (gap0.53 FAIL) @12 (gap0.53 FAIL) @10 (7.19/.883/gap5.89 PASS) -> SELECT @10. Lanes (222, local EXACT): 0.61/97.2 + 0.49/100.0. ==> control GOOD (moved off @12 to an equally good stop -- headline-noted, not a break).
- P01 control: @14/@12 (bal FAIL) @10 (gap0.00 FAIL) @8 (4.63/.887/gap4.96 PASS) -> SELECT @8. Lanes (220, local EXACT): 0.61/100.0 + 0.61/96.6. ==> control GOOD (= R2 stop).

### Dot accounting at applied stops (clusters + UN = cloud, EXACT)
- P12@3: 40556 + 9146 = 49702. P15@8: 36608 + 1934 = 38542. P16@10: 27914 + 1805 = 29719. P27@4.5: 4133 + 4337 = 8470 (UN verts read from file headers). P01@8 per 220 (100%).

### Mechanism notes for the rule-amendment decision (lead + user, no proposal)
1. P12: frozen third<=8% fails @4.5 (9.29: 4617/49702) so loosest-first descends INTO @3 and selects the fragment-zone stop (Bl1 80.8). A 4.5 floor gives P12-NONE instead; a third-leg retune gives @4.5 (89.0, near-miss). The book as frozen picks the worst of the three.
2. P27: with top2 dropped, R4 stops where faces hold 33.6% of the cloud; gap-clean (7.36) but lanes cover half the rim each (cov 55/62). Gap-clean != trace-correct on fragmented pieces.
3. P22/P25: bridge class extends beyond P12 -- every R1-balanced step touches (gaps 0.00-0.79 across 11 measured steps).
4. Coincidence verified, not assumed: P12 symmin 5.2629 recurs at @4.5/@3/@2 at the identical surface point (persists across tightening; files byte-distinct), P27 symmin 2.7538 recurs at @12/@10 ditto -- login-node recheck.

## Lead verdict (2026-10-21)
ACCEPT. R6: gap job 33592310 + edge job 33592413 both COMPLETED 0:0; P27 lanes re-scored EXACT (swapped o0->a1 1.50/54.9, o1->a0 0.92/62.0; straight 8.11/8.89); P12@3/P15@8 cited scores re-verified EXACT against 224/222; dot accounting exact; binaries byte-identical; no re-segmentation. Bottom line stands: 1/5 (P15@8 GOOD); P12 SELECTS-BAD@3; P27 SELECTS-BAD@4.5; P22/P25 NONE; controls GOOD (P16 moved @12->@10, equally good -- rule behavior, not a break; P01 stays @8). Amendment evidence endorsed: (1) third<=8% marginally fails honest stops P12@4.5 (9.29) + P25@10/@8 (8.85/8.70) -- the line sits inside the honest cluster; (2) a 4.5 floor gives P12-NONE (worse); (3) P27 proves gap-clean!=trace-correct (top2 33.6%, half-rim lanes) -- no cutoff fixes that class; (4) P22 never separates at any threshold (bridge class). Retune candidate: third<=10% selects P12@4.5 (known near-miss) + P25@10 (lanes unknown) + P27@8 (lanes unknown) -- needs the follow-up lane-sets before it becomes a rule. User amendment decision pending.

### md5s
- Binaries (job log): Mesh 9a0386f54b0ecc70605f9f26371a789e, Edge dc472b0e87c934b6c487ff8637209864.
- P27@4.5 surfaces tree==ladder: 9e0e5174bf394387017bf2a8f6ab4c3e / 503400c67ca0ed9f52d1a6e648940ebb. P27 input cloud tree==214 source: c3b1bb6975184a29de9d134500e2ba25.
- P27 lanes source==fetched: 45c33a5da9eaac9aaea4ce21def49c4a / 61215a6dc786ac809b47cf8dcd763597 / 2bc8afd83822905a43392afe4b79eaf9 / 294912e7a15368d3f453e92bcd24844b.

### Paths
- Spartan: sfs-fix-225 (gap225sym.py, gap225.sbatch, gap225_33592310.out/.err), pota225_edgeP27_4p5 (run_225_edge.sbatch, edge_45.log, edge225_33592413.out/.err, Dataset/Breaklines lanes).
- Laptop: .scratch/pota225/ (lanes/4 P27 files, P27 author pair, rescore225.py). sacct: 33592310 + 33592413 both COMPLETED 0:0.
