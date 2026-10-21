Status: ready-for-agent

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

## Required evidence to report
- Per-piece: R4 table (legs per threshold), selected stop, lane scores, verdict class. Bottom line first: on how many of 5 does R4 select a both-at-bar stop (vs R2's record: 1/6 strict, 4/6 splitting-level).
