Status: ready-for-agent

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

## Required evidence to report
- Bottom line first: verdict + per-piece selections and scores. Then jobs, md5s, tables.
