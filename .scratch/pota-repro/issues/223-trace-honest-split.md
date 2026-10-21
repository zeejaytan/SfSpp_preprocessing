Status: ready-for-agent

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

## Required evidence to report
- Edge job ID + sacct; lane scores table; jumps/gapmax; md5s; one paragraph on WHERE the trace deviates if it fails (which rim stretch, dot counts).
