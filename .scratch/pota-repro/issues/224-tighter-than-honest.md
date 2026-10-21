Status: done

## Goal
Find the tightness where P12's faces fit the author's lines (the overshoot trimmed, no new holes), and record the full author-free formation statistics at every stage so the lead + user can draw up a general rule from them. Phase 1 = facts only; the rule itself is a later ticket. User direction m03398.

## Boundary (worker: Spartan experiment copy ONLY, fresh dir sfs-fix-224)
- MUST reuse the 221 mesh binary AND 221 edge binary byte-identical (record both md5s; 221 pattern). New thresholds ONLY (3, then 2), same single-shot method as exp-220/221 -- no code changes, no retuning.
- MUST reuse the P12 input cloud byte-identical (md5 vs 221 ladder input).
- MAY touch: fresh run dir (mesh_T3/T2 logs, edge outputs, scores); fetch output lanes at the BEST stage to C:/PR/SfSpp_preprocessing/.scratch/pota224/lanes/ (md5 source-vs-fetched).
- MUST NOT touch: main worktree, .wt-*, other branches/stashes/bundles, tickets except appending ## Comments to THIS ticket. Author lanes in the scorer ONLY (standing asterisk rule).
- STOP EARLY only if a stage yields zero face dots (total fragmentation) -- report and stop that arm.

## Constraints
- Report slots per piece (209 pattern): straight-vs-swapped by the sums.
- Overshoot tracker (lead-defined, P12-specific): face dots inside box x[33,54] y[-28,10] z[432,474] at each stage (lead measured @8: 11568+204, @4.5: 7055+204). Report per face.
- Formation statistics per stage (ALL author-free): cluster count, top-5 cluster sizes, S0/S1/UN dot counts, S0<->S1 min/p1/frac<2mm, lane med/cov/n/jumps/gapmax/endgap per lane, face-vs-author distance distribution (med/p90/p99, over-2mm count -- trend indicator only, interior dots dominate).

## Acceptance (lead judges; numbers + cites + paths)
- Per stage (3, 2): formation stats table + lane scores vs bar (med<2, cov>=90%) + overshoot-tracker counts.
- Verdict sentence per stage: closer to perfect fit than @4.5, or holes/fragmentation instead (name it with numbers).
- sacct State/ExitCode per job; binary + input md5s; fetched lane md5s.

## Comments (worker 224, 2026-10-21. NO main commit; NO branch -- mesh+edge only, no code touched)

### What was run
- Fresh Spartan copy /data/gpfs/projects/punim2657/sfs-fix-224 (build-220 copied from sfs-fix-221; no .git so no pull/divergence applies). Binaries reused byte-identical, md5-verified in BOTH job logs: Mesh 9a0386f54b0ecc70605f9f26371a789e, Edge dc472b0e87c934b6c487ff8637209864 (== 221 pattern).
- P12 input cloud byte-identical: b1424533bcc45d54268615b510c43043 (tree Point.pcd == 221 ladder input == 214 sampled source).
- Single-shot 221 method (run_224_edge.sbatch = run_221_edge.sbatch with WROOT/TREE/job-name swapped, SFS_SINGLE_SHOT=1): P12-only trees pota224_edgeP12_3 (DEG=3) and pota224_edgeP12_2 (DEG=2). Thresholds run 3 first, then 2, per brief.
- Jobs (all sacct COMPLETED 0:0): mesh+edge @3 33590867 (26s); mesh+edge @2 33590967 (40s); stats 33591083 (stillborn, script NameError) / 33591147 (mesh half) / 33591273 (full, 87s). Stats script .scratch/pota224/stats224.py (numpy-chunked min-dist, no scipy on Spartan).
- Main worktree, .wt-*, other branches/stashes/bundles untouched. Author lanes ruler ONLY (scorer-side). Neither stage hit zero face dots, so no STOP EARLY.

### Per-stage formation-stats table (author-free except marked ruler-only)

| stage | clusters | top-5 | top2% | third% | bal | R1 | S0 | S1 | UN | accounting | S0<->S1 min/p1/p50 | frac<2mm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| @4.5 (221/223 cite) | 18 | 32686/30952/... | 62.5 | ~6 | ~0.95 | NO | 32686 | 30952 | ~4859 | True | 5.26/6.21/~9.5 | 0.00% |
| @3 | 28 | 15141/11284/3377/2542/2517 | 53.2 | 6.8 | 0.745 | NO | 31552 | 24619 | 9146 | True | 5.26/6.20/9.32 | 0.00% |
| @2 | 44 | 14670/9513/2450/1566/446 | 48.7 | 4.9 | 0.648 | NO | 31068 | 22186 | 16918 | True | 5.26/6.20/9.11 | 0.00% |

### Lane scores vs author (bar med<2, cov>=90%; slots by median-sum, 209 pattern; refs o0=152 o1=156)
- Slot sums @3: straight 17.61 vs swapped 1.32; @2: straight 17.24 vs swapped 1.31 -- Bl0->o1, Bl1->o0 both stages (same assignment as 223).
- @3: ourBl0 vs o1 n=160 med=0.61 cov=99.4 max=2.4 jumps=0 gapmax=8.1 endgap=1.8 AT-BAR. ourBl1 vs o0 n=146 med=0.71 cov=80.8 max=16.9 jumps=1/12.3 gapmax=12.3 endgap=1.8 below-bar.
- @2: ourBl0 vs o1 n=159 med=0.51 cov=100.0 max=1.3 jumps=0 gapmax=6.5 endgap=1.8 AT-BAR. ourBl1 vs o0 n=144 med=0.81 cov=75.7 max=17.9 jumps=0 gapmax=4.9 endgap=1.8 below-bar.
- @4.5 cite (223): Bl0->o1 0.63/89.0 below-bar (19-dot corner excursion, max 4.5); Bl1->o0 0.77/98.8 AT-BAR.

### Overshoot-tracker corner-box counts (box x[33,54] y[-28,10] z[432,474], per face)
- Lead cites: @8: 11568+204; @4.5: 7055+204.
- @3: S0 6212/31552 (19.69%) + S1 204/24619 (0.83%). @2: S0 6028/31068 (19.40%) + S1 202/22186 (0.91%). S0-side trims monotonically (11568->7055->6212->6028); S1 steady ~202-204.

### Face-vs-author distance distribution, ruler-only trend (interior dots dominate)
- @3: S0 med=9.46 p90=21.75 p99=27.81 over2=28232 (89.5%); S1 med=10.14 p90=21.72 p99=27.02 over2=21862 (88.8%).
- @2: S0 med=9.57 p90=21.78 p99=27.82 over2=27979 (90.1%); S1 med=9.96 p90=21.87 p99=27.13 over2=19675 (88.7%). Flat vs @4.5 class -- faces sit rim-proximal, interiors dominate as before.

### WHERE the trace deviates (Bl1 bad-dot geography, .scratch/pota224 badots.py on login node)
- @3 Bl1: 28/146 dots >=2mm in 2 walk-order runs (idx 2-27 x26, idx 33-34 x2); bad-bbox x[9.6,27.6] y[-9.7,18.4] z[436.8,464.0]; bad-median 8.66 max 16.87; 0/28 inside the corner box.
- @2 Bl1: 35/144 dots >=2mm in 2 runs (idx 2-26 x25, idx 28-37 x10); bad-bbox x[10.6,30.6] y[-8.1,14.0] z[433.2,464.0]; bad-median 7.75 max 17.90; 0/35 inside the corner box.
- The bad stretch sits at the lead-measured @8 bridge point ([10.8,14.3,465.0]), NOT the @4.5 corner excursion zone -- interior-shortcut class (cf @10 red lane), max ~17-18mm vs @4.5 corner max 4.5mm.

### Verdict sentences
- @3: FRAGMENTATION, not a closer fit than @4.5 -- clusters 28 vs 18, top2 53.2% vs 62.5%, Bl1 cov 80.8% vs 98.8% with a new 26-dot interior excursion (max 16.9mm) at the old bridge point; Bl0 did reach full bar (0.61/99.4) but the o0 side broke worse than the corner it fixed.
- @2: FRAGMENTATION, worse than @3 -- clusters 44, UN 16918 (34% of cloud), top2 48.7%, Bl1 cov 75.7% with a 35-dot interior excursion (max 17.9mm) in the same bridge zone; tightening past 3 sheds dots to UN without trimming toward either line.

### What changed in the corner vs @4.5
The @4.5 corner excursion is gone -- S0 box counts fall 7055->6212->6028 and Bl0 now traces o1 at full bar both stages (0.61/99.4, 0.51/100.0, zero jumps). But the fix did not come from trimming toward the line: both tighter stages shatter the segmentation (18->28->44 clusters, UN 4859->9146->16918) and open a new interior shortcut on the o0 side at the old @8 bridge point, with 4x the peak deviation (17-18mm vs 4.5mm). Net: one lane fixed, the other broke worse -- neither stage beats @4.5, and @3 beats @2 on every number (Bl1 cov 80.8 vs 75.7, UN 9146 vs 16918).

### Fetched lanes (BEST stage = @3, md5 source-vs-fetched MATCH)
- C:/PR/SfSpp_preprocessing/.scratch/pota224/lanes/Pot_D_Piece_12_Breakline_0.pcd 7a36e65745ebc0bd468281dd30a56f9b
- C:/PR/SfSpp_preprocessing/.scratch/pota224/lanes/Pot_D_Piece_12_Breakline_1.pcd 50aca1fd652ecfd0fac986066ee606a3

### Paths
- Spartan: sfs-fix-224 (code+run_224_edge.sbatch+job logs edge221_33590867/33590967.out), pota224_edgeP12_3 (mesh_3.log/edge_3.log), pota224_edgeP12_2 (mesh_2.log/edge_2.log), pota224_work (stats224.py/stats224.sbatch/stats224_*.out/badots.py).
- Laptop: .scratch/pota224/ (stats224.py, lanes/2 pcds, probe.txt scratch).

## Lead verdict (2026-10-21)
ACCEPT. R6: jobs 33590867/33590967/33591273 all COMPLETED 0:0; local re-score @3 EXACT (o0->a1 0.61/99.4, o1->a0 0.71/80.8; swaps 9.35/8.26); 28 bad dots, 0 in corner box, bbox matches old bridge point; eye-checked (chord shortcut across interior, max 17mm). ANSWER to the user question: @4.5 IS the closest -- no perfect-fit stage below (overshoot box 7055->6212->6028 while clusters explode 18->28->44). Trade-off frontier by combined coverage: @4.5 187.8 (corner excursion ~4.5mm) > @3 180.2 (interior shortcut 17mm) > @2 175.7 (worse). Same disease both ends: where the face goes ragged the walk leaves the rim (corner at @4.5, interior at @3/@2). Rule-hunt input: the signature must select @4.5 = last stage with boundary whole enough for the walk to stay on-rim; formation tables + corner paragraph in worker Comments.

## Required evidence to report
- Mesh + edge job IDs + sacct; per-stage stats table; lane scores; overshoot counts; one paragraph: what changed in the corner vs @4.5 (trimmed toward the line, or new holes, with dot counts).
