Status: ready-for-agent

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

## Required evidence to report
- Mesh + edge job IDs + sacct; per-stage stats table; lane scores; overshoot counts; one paragraph: what changed in the corner vs @4.5 (trimmed toward the line, or new holes, with dot counts).
