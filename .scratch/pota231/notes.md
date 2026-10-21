# POTA-231 worker notes — uniform R6 leg table, six 214-MIXED pieces

Date: 2026-10-21. Spartan READ-ONLY. No sbatch, no re-segmentation, no edge jobs.
Method for every leg: balance + third-share from mesh_T*.log parses
("Starting processing on" blocks, exact "Cluster i : n" lines);
UN from thr_*/`<piece>_unclustered.ply` "element vertex" headers;
gap from saved 222/225/226 symmin outputs (225/226-pattern cKDTree symmetric-min
S0<->S1); P25 fresh-default gap computed on login node with the identical
algorithm (numpy chunked brute force, scipy absent) + P25@4.5-ladder control.

## R6 (frozen, ticket 227 spec head, loosest-first)

Threshold 90 -> 4.5 is R6-selected iff ALL THREE hold:
(a) balance c2/c1 >= 0.5; (b) gap-clean symmin >= 2 mm; (c) UN share <= 12% of cloud.
NO third-share leg, NO top2 leg.

## Piece results

- P12 -> @4.5 SELECT. bal 15176/15887 = 0.9552; gap 5.2629 (gap_sym_33583968.out);
  UN 4859/49702 = 9.78%. Lanes near-miss (227: Bl0 0.63/89.0 + Bl1 0.77/98.8).
  Legs pass, lanes 1 pp short on Bl0 cov -> complicate, not settled here.
- P15 -> @8 SELECT. bal 12993/17639 = 0.7366; gap 5.2864; UN 1934/38542 = 5.02%.
  Lanes GOOD (0.43/97.2 + 0.75/97.6). Agree.
- P16 -> @10 SELECT. bal 10302/11663 = 0.8833; gap 5.8879; UN 1805/29719 = 6.07%.
  Lanes GOOD (0.61/97.2 + 0.49/100). Agree.
- P22 -> NONE. @14 bal 8280/8621 = 0.9604 / UN 858/18378 = 4.67% / gap 0.0000 FAIL;
  @12 bal 7321/8388 = 0.8728 / UN 1377/18378 = 7.49% / gap 0.0000 FAIL;
  @10 gap 0.6803 + UN 13362/18378 = 72.7% FAIL;
  @8 gap 0.0000 + UN 6304/18378 = 34.3% FAIL;
  @4.5 gap 0.1663 + UN 5403/18378 = 29.4% FAIL.
  Fresh-default lane Bl1 0.77/89.7 near-miss (216/score before-column = 214 fresh
  score) exists but no ladder stop passes the legs -> complicate (good lane,
  no legal stop).
- P25 -> NONE everywhere.
  Ladder: @16 bal 1116/9608 = 0.1161 FAIL (UN 458/11182 = 4.10%);
  @14 bal 1092/9429 = 0.1158 FAIL (UN 661/11182 = 5.91%);
  @12 zero-cluster hole (parser ncl=0, "Could not achieve 2 clusters");
  @10 bal 3574/3799 = 0.9408 / UN 1072/11182 = 9.59% PASS / gap 0.6798 FAIL;
  @8 bal 3523/3747 = 0.9402 / UN 1399/11182 = 12.51% FAIL / gap 0.6798 FAIL;
  @4.5 bal 3321/3630 = 0.9149 / UN 2120/11182 = 18.96% FAIL / gap 0.7906 FAIL.
  Fresh-default (214 pipe faces, PRESENT, md5-identical Dataset-vs-Temp copies):
  6 clusters 2911/2342/588/414/356/152 sum 6763 + UN 4419 = cloud 11182;
  bal 2342/2911 = 0.8046 PASS; gap 4.2766 PASS (this ticket, ctrl 0.7906 EXACT);
  UN 4419/11182 = 39.52% FAIL -> gate FAIL.
  Lane state: 214 gate_table.csv = slid Bl0 7.07/0.0 (n71) + Bl1 6.96/0.0 (n68).
  The ticket-231 Goal premise "85.9/91.2 near-miss lanes" was searched across
  .scratch + artifacts and appears NOWHERE in the repo record -> FLAGGED for lead;
  legs-vs-lanes agreement for P25 is judged against the recorded slid scores
  (agree: both bad) unless the lead sources the 85.9/91.2 numbers.
- P27 -> @12 SELECT. bal 2216/2591 = 0.8553; gap 2.7538; UN 753/8470 = 8.89%.
  Lanes BAD (0.83/58.5 + 0.91/68.9) -> DISAGREE, explained downstream:
  229 OURS-AT-EDGE (disputed ours med 39.2 vs author 1.4 deg, line 16.3),
  230 RESCORED-NEAR-MISS (new == old, excluded 22.4%/16.7%).
- Control P01@8 (not a table row): bal 60469/68197 = 0.8867; gap 4.9637;
  UN 5043/149013 = 3.38% -> gate passes (220 ladder, pieces named Pot_D_Piece_XX).

## Accounting

Every clusters-sum + UN-header = cloud identity holds EXACT (P12 49702, P15 38542,
P16 29719, P22 18378, P25 11182, P27 8470, P01 149013).

## Verdict: TABLE-COMPLETE

All six rows filled from verified faces/logs; zero repro-divergence on any leg
(balance/UN/gap all reproduce 227 to the printed digit). One lane-premise caveat
on P25 (85.9/91.2 not in repo record) for the lead — it changes no R6 cell.
