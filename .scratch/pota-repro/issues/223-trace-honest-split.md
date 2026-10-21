Status: done

## Goal
Trace the HONEST split: run the edgeline extraction on P12's @4.5 faces (thr_4p5, gap-clean, 18 clusters, top2 62.5%) and score vs the author lanes. User correction (m03281): the @4.5 fragmentation is not destruction -- the tight threshold correctly refused the false @8 bridge join; the surviving faces fit the author 100% (med 0.24/0.25, lead-measured). Question: does plane-correct give trace-correct? Bar decides whether 222's R3-NONE verdict and R1's balance gate stand.

## Boundary (worker: Spartan experiment copy ONLY, fresh dir sfs-fix-223)
- MUST reuse the EXISTING thr_4p5 surfaces byte-identical (pota221_ladder/thr_4p5/Pot_D_Piece_12_Surface_{0,1}.xyz); verify md5 before running. NO re-segmentation, no threshold changes.
- MUST reuse the 221 edge binary byte-identical (221 pattern); record md5.
- MAY touch: fresh run dir + edge logs; fetch the 2 output lane files to C:/PR/SfSpp_preprocessing/.scratch/pota223/lanes/ (md5 source-vs-fetched).
- MUST NOT touch: main worktree, .wt-*, other branches/stashes/bundles, tickets except appending ## Comments to THIS ticket.

## Constraints
- ORIG-free: author lanes used ONLY in the scorer, never in any input (standing asterisk rule).
- Report slots per piece (209 pattern): score our-Bl0/Bl1 against BOTH author lanes, state straight-vs-swapped by the sums.

## Acceptance (lead judges; numbers + cites + paths)
- Per-lane med/cov vs author (bar med<2, cov>=90% both lanes), n per lane, jump count + gapmax per lane (211 pattern).
- Verdict sentence: does @4.5 trace at bar (rule repair needed: balance gate wrong) or fail (222 stands, failure mode named with numbers)?
- sacct State/ExitCode for the edge job; binary + surface md5s; fetched lane md5s.

## Lead verdict (2026-10-21)
ACCEPT with strict-FAIL recorded. R6: job 33589544 sacct COMPLETED 0:0; local re-score EXACT (o0->a1 0.63/89.0, o1->a0 0.77/98.8; swap sums 10.75/9.45, decisively straight); 19-dot corner bbox matches worker to 0.1; eye-checked (walk cuts one corner, otherwise coincides). Strict bar: Bl0 89.0 < 90 = FAIL by 2 dots' worth (153 vs 155 needed). Substance: user's correction vindicated -- honest split yields sub-mm lanes both sides where R2-accepted @10 orphaned a lane; balance gate, not the split, is the artifact. Slots run swapped (o0->a1/o1->a0), same numbering arbitrariness as the Pot A swap. Open: cosmetic-accept vs corner-fix vs hold-bar -- user's call.

## Required evidence to report
- Edge job ID + sacct; lane scores table; jumps/gapmax; md5s; one paragraph on WHERE the trace deviates if it fails (which rim stretch, dot counts).

## Comments (worker 223, 2026-10-21. NO main commit; NO branch -- edge-only, no code touched)

### What was run (job 33589544, sacct COMPLETED 0:0)
- Fresh tree /data/gpfs/projects/punim2657/pota223_edgeP12_45 (no .git, so no pull/divergence applies). NO mesh rerun: transplanted the EXISTING ladder faces byte-identical -- tree md5 == ladder md5 both files (123a4e3649047cab80bb296038cde68a S0 32686 pts / 0bc8a5847dfd396d3706625951163e2d S1 30952 pts; verified again inside the job log). Sibling files (Mesh.obj, Point.pcd, SampledWithNormals.ply, unclustered.ply) + Dataset inputs copied from pota221_edgeP12_10 (P12-identical, threshold-independent). Edge binary reused byte-identical: dc472b0e87c934b6c487ff8637209864 (== 221 pattern, logged in job out). Ladder cite: P12@4.5 = 18 clusters (mesh_T4p5.log:50), top2 62.5% per 221.
- Main worktree, .wt-*, other branches/stashes/bundles untouched. Author lanes used as ruler ONLY (scorer-side).

### Lane scores vs author (209 slot matrix; refs o0=152 o1=156; bar med<2, cov>=90%)
- Slot matrix: ourBl0->o0 10.75 / ourBl0->o1 0.63 | ourBl1->o0 0.77 / ourBl1->o1 9.45. Swapped-sum 1.40 vs straight-sum 20.20 -- STRAIGHT slots (Pot-D convention, same as P15@8): ourBl0->o1, ourBl1->o0, one lane per author lane, no orphan.
- ourBl0 vs author-o1: n=172 med=0.63 cov=89.0 max=4.5 -- BELOW-BAR (coverage misses by 1.0pp).
- ourBl1 vs author-o0: n=160 med=0.77 cov=98.8 max=4.7 -- AT-BAR.
- Jumps/gapmax (211 pattern, >10mm / end-gap): Bl0 1 jump max 13.4 (idx 2->3), endgap 1.8; Bl1 1 jump max 10.0, endgap 1.8.
- Local scorer: .scratch/pota221/p221_score.py (unchanged 221 pattern); gap/dev scripts .scratch/pota223/gap223.py, dev223.py, dev223b.py.

### WHERE the trace deviates (Bl0's 19 bad dots, all one rim corner)
- 19/172 Bl0 dots >=2mm from o1, in 3 walk-order runs at the SAME corner: idx 0-2 (n=3, maxd 4.49, centroid [39.3,3.9,467.5]) + idx 5-18 (n=14, maxd 4.05, centroid [47.7,-17.6,449.6]) + idx 170-171 (n=2, maxd 3.42, centroid [40.5,3.2,468.3]). Bbox x[38.8,49.0] y[-23.7,5.3] z[440.4,468.5]. The 13.4mm jump at 2->3 exits this corner; walk starts AND ends there (loop nearly closes, endgap 1.8). NOT the lead's @8 bridge point ([10.8,14.3,465.0], ~30mm away in x) and NOT the @10 interior shortcut class -- the excursion stays near the rim (bad-dot median 3.66, max 4.49) at one corner stretch.

### Fetched lanes (md5 source-vs-fetched MATCH)
- Pot_D_Piece_12_Breakline_0.pcd d2ef21a3d6b71f6c5646249b1cb49344 (11276 B, 172 pts)
- Pot_D_Piece_12_Breakline_1.pcd 6e6c87f33266b94bae9734957dbbbbca (10807 B, 160 pts)
- In C:/PR/SfSpp_preprocessing/.scratch/pota223/lanes/. Stepring sidecars 0-byte on source, not fetched (222 pattern).

### Verdict sentence
- STRICT verdict: @4.5 does NOT clear the bar (Bl0 cov 89.0 < 90 by 1.0pp; Bl1 at bar) -- 222's R3-NONE stands on the letter of the bar, failure mode = 19-dot corner excursion above (not an interior shortcut, not the @8 bridge).
- Material caveat for the lead's repair decision: the R1-rejected @4.5 split (top2 62.5%) puts one sub-mm-median lane on EACH author lane (0.63/0.77), while the R2-accepted @10 stop orphaned a whole lane (Bl0 7.06, interior shortcut). Plane-correct nearly gives trace-correct here -- the balance gate, not the splitter, looks like the artifact on this piece.
