# 210 - Swap P02-P08 Bl0/Bl1 to the author convention + fresh re-seat (209 follow-up)

Status: done
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
User order (2026-10-20): swap our slot 0/1 edgelines to match the author
convention, then re-seat. Lead check (same day): the assembler (POT_A_ORIG
block, class/data_path.h:1610+) loads ONLY Breakline_0.pcd per piece -- so
the 208 fresh arm (7/8+9/15) seated while reading the opposite rims from the
green ORIG control on P02-P08. 209 proved both lanes are true edges
(matched-lane coincidence 100%<2mm all pieces), so filing the author-side
rim in slot 0 is legitimate (ticket-73 precedent). P01 slots already agree:
NO swap for P01. (P01-Bl1 short at 92 vs 214 stands as a separate open item
from 209 -- diagnose, do not fix inside this ticket.)

## Boundary
Spartan-side, new bundle copy pota210_bundle_v1 (copy of v0; NEVER modify
v0): for pieces 02-08 ONLY, swap Breakline_0 <-> Breakline_1 contents
(byte-identical copies, verify with md5 before/after). Everything else
(Mesh, Axes, GT, Surfaces, P01 files) identical to v0. Do NOT touch the
preprocessing sources, the live Spartan main checkout, or the 2 pre-E2E
stashes. Re-seat the FRESH arm only (same scorer b56bc80, same stage recipe
as 208 job 33505947); the ORIG control stays as run (no rerun). COMMIT
NOTHING (lead commits).

## Constraints
Standing submit sign-off covers sbatches (fresh-only recipe per 208:
request 24h; laptop-side poll per sbatch, sacct State/ExitCode in Comments).
Held allocation for iterative checks. If seating diverges from the 208
fresh run for non-swap reasons (different snapshot layout, missing files),
STOP and report -- do not reinterpret. No MATLAB re-run (axes as-is).

## Acceptance
Fresh arm seated on the swapped v1 bundle, reported as fragments x/8 +
joins y/15 with Acc-file verbatim lines, strict table (same robust-align
recipe as 208: align on pieces 2-8 excl. outliers, per-piece rot/trans),
and a side-by-side render vs the 208 fresh result. Comparison stated
plainly: swapped-v1 vs unswapped-v0 (7/8+9/15) vs ORIG control (8/8+15/15).

## Required evidence
Comments: v1 bundle path + swap md5 table (per piece: old-Bl0 md5 == new-Bl1
md5 and vice versa) + job ID/state + Acc verbatim + strict table + render
paths + the comparison. Final report: same, self-contained, plus verdict on
whether convention alignment moved seating.

## Lead verdict (2026-10-20)
ACCEPT -- swap lands at the bar. R6: sacct 33510738 COMPLETED 0:0 00:16:26; swap verified both-ways on P03 sample (v1-Bl0=7631238f=old Bl1, v0-Bl0 still 2999dd1a); strict_fresh210.txt read verbatim (7/8, only P5 trans FAIL; 208 reprint 4/8 matches committed); seat_fresh210_vs_gt.png eye-checked (coherent vessel, all 8 on GT shell, P01 on rim); v0/main/stashes untouched. Claim: convention alignment closed 208's search gap on this arm (fresh 7/8+9/15 -> 8/8+15/15 = ORIG control; strict 4/8 -> 7/8).

## Comments (worker)
(worker, 2026-10-20/21 -- SWAP + FRESH RE-SEAT DONE, 8/8+15/15)

Bundle: /data/gpfs/projects/punim2657/pota210_bundle_v1/SfS_pp (cp -a of
pota208_bundle_v0; v0 NEVER modified -- re-read after the run, P03-Bl0 md5
unchanged at 2999dd1a11d1b762bc538b79cb05fa31). P02-P08 Breakline_0 <->
Breakline_1 contents swapped via temp-rename (byte copies); P01 untouched;
Mesh/Axes/Surfaces/Ground-Truth verified identical (diff -r -q clean on all
four dirs).

Swap md5 table (v0 read before copy, v1 read after swap -- per piece,
old-Bl0 == new-Bl1 AND old-Bl1 == new-Bl0):
| piece | v0-Bl0 ^ | v0-Bl1 ^ | v1-Bl0 (=v0-Bl1) | v1-Bl1 (=v0-Bl0) | swap? |
| P01 | 3d4b46bb | 95ecb257 | 3d4b46bb | 95ecb257 | NO (untouched) |
| P02 | 14af04f5 | 38b63b82 | 38b63b82 | 14af04f5 | YES |
| P03 | 2999dd1a | 7631238f | 7631238f | 2999dd1a | YES |
| P04 | 8c841046 | a51ccd99 | a51ccd99 | 8c841046 | YES |
| P05 | 7cf1d8ce | 38d6b294 | 38d6b294 | 7cf1d8ce | YES |
| P06 | b38cc064 | fcfd487b | fcfd487b | b38cc064 | YES |
| P07 | cae426e5 | 99a8c162 | 99a8c162 | cae426e5 | YES |
| P08 | ce81f413 | f2e7ca78 | f2e7ca78 | ce81f413 | YES |
(^ = 8-hex prefix; full 32-hex md5s verified on Spartan, recorded in
pota210_e2e/pota210_bun_v1_md5.txt. All 14 swapped slots match both ways.)

Seating (fresh arm ONLY, 208 recipe: pristine scorer b56bc80 via symlinked
pota210_e2e/src, run_pota210_freshonly.sbatch adapted from
run_pota208_freshonly.sbatch -- same guards, same shim/driver asserts, 24h
request): job 33510738 COMPLETED ExitCode 0:0 Elapsed 00:16:26.
Guards: HEAD b56bc80 OK, tree clean, no cure markers, SIF + GTSTUB present,
bundle 16/16/8/8, SNAPSHOT-T-COUNT=8. LINK-SHIM-OK / LINK-FORKMAIN-ABSENT-OK
/ DRIVER-SHIM-OK all green.

Acc verbatim (L_fresh_binary.log):
********* Sherd accuracy : 8 / 8 (100%) *********
********* Edge accuracy : 15 / 15 (100%) *********
FRESH-VERDICT: 8/8+15/15. Acc.txt: Time : 999395 Sec / Sherd 8/8 (100 %) /
(edge line, mislabeled Sherd in file as in 208) 15/15 (100 %).
Forest: Total 541 / pruned 123 (vs 208 fresh Total 253 / pruned 70 -- same
scorer + recipe, inputs differ only by the verified swap, so the forest
change is an effect of the swap, not a non-swap divergence; pruned 123 ~=>
ORIG 124). No STOP condition: layout/files/recipe identical to 208.

Strict table (208 robust-align recipe -- Kabsch on pieces 2-8 excl p1;
script artifacts/pota210/strict_render_210.py, table
artifacts/pota210/strict_fresh210.txt):
1 | 1.41 | 7.05 | PASS
2 | 2.44 | 4.35 | PASS
3 | 0.92 | 6.47 | PASS
4 | 0.39 | 4.41 | PASS
5 | 1.94 | 11.19 | FAIL
6 | 1.57 | 4.63 | PASS
7 | 1.54 | 8.67 | PASS
8 | 1.13 | 4.51 | PASS
STRICT-SHERD: 7/8 (only P5 misses, on translation 11.19 vs 10mm line).
208 v0 reprinted with the same script: 4/8, verbatim match to committed
strict_fresh208.txt (pipeline validated).

Renders (worker eye-checked): artifacts/pota210/seat_fresh210_vs_gt.png
(GT gray + 210 attempt color, side + top) and
artifacts/pota210/seat_208_vs_210.png (208 attempt vs 210 attempt
side-by-side). 210 shows a coherent vessel with all 8 pieces hugging the
GT shell; the red P01 cloud that sat scattered in the middle of the 208
render now sits on the rim.

Comparison, plainly: swapped-v1 8/8+15/15 vs unswapped-v0 7/8+9/15 vs ORIG
control 8/8+15/15 (as run, no rerun). Convention alignment moved seating to
the bar -- the fresh arm now matches the ORIG control. Verdict: YES, filing
the author-side rim in slot 0 fixed seating (claim-1 search/selection gap
from 208 closed on this arm; strict 4/8 -> 7/8).

Boundary held: no preprocessing-source touch, live Spartan main checkout
untouched (still @ eac8482, only pre-existing Juglet untracked residue),
both pre-E2E stashes shelved intact, scorer src @ b56bc80, v0 intact.
Spartan-side evidence: pota210_e2e/pota210_run_33510738/
(L_fresh_binary.log, L_fresh_Result_snapshot with T_0to_0..T_7to_7 +
Acc.txt); laptop-side: artifacts/pota210/ (T fetch, strict table+script,
both renders). Status left for lead to flip -- NOT set to done.
