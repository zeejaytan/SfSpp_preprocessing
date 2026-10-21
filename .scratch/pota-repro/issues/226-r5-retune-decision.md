Status: ready-for-agent

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

## Required evidence to report
- Bottom line first: the rule verdict + per-piece selections and scores. Then jobs, md5s, tables.
