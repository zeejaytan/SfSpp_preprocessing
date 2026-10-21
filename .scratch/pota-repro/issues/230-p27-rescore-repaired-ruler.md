Status: done

## Lead verdict (2026-10-21)
RESCORED-NEAR-MISS accepted. R6: repro bit-identical to 229 (baseline 1.294, control 41.63/41.47, line 16.29, disputed 39.22/1.35); rescore new==old (Bl0 0.83/58.5 excl 22.4%, Bl1 0.91/68.9 excl 16.7%) -- meaningful (<50% excluded); Step 3 our dots in excluded zones ride the crease (22/22 + 12/13 on-edge); evidence on disk (script, 4 csvs, eye-checked PNG); only this ticket touched among tracked. Meaning change, not number change: the coverage shortfall now provably punishes exactly the dots where ours rides the edge and the author sits mid-surface (229). P27 grade: still below bar; the bar's local blindness is recorded, not repaired -- repairing it (e.g. crease-credit) is a rule change for the user, not this ticket.

## Goal
Rescore P27's lanes with the ruler repaired where 229 proved the reference wrong (user challenge m03812). Rule: an author segment proven off-edge by the sharpness instrument stops being scored by proximity; coverage counts only against author segments verified on-edge. Ends at rescored numbers + verdict; changes no lanes, no code, no bar values.

## Boundary (worker: LAPTOP-ONLY, no Spartan, no runs)
- Inputs (all local): our lanes .scratch/pota227/lanes/Pot_D_Piece_27_*.pcd; author .scratch/pota225/Pot_D_Piece_27_*_author.pcd; dense ORIG cloud artifacts/pota229/Pot_D_Piece_27_Point.pcd (83,374 pts, 229 provenance); instrument p229_sharpness.py + line 16.29 + baseline (ticket 229 Comments).
- MAY touch: fresh dir C:/PR/SfSpp_preprocessing/.scratch/pota230/ (script + numbers + one picture, gold/blue/black scheme ONLY).
- MUST NOT touch: Spartan; main worktree tracked files except this ticket's Comments; other tickets; bundles; bar definition (med<2/cov>=90% UNCHANGED -- only the reference segments counted change).

## Constraints
- Step 1 (gate, no exceptions): re-run the sharpness instrument along the FULL author lanes (both), and mark every author dot on-edge (S >= line) vs off-edge. The 229 control + disputed results must reproduce first; if they don't, STOP and report REPRO-FAIL.
- Step 2: coverageМед rescore -- our dots scored ONLY against on-edge author dots (nearest on-edge author dot; off-edge author segments invisible to the scorer). Report med + cov per lane, plus the share of the author lane that got excluded (if >50% excluded, the rescore is meaningless -- report MEANINGLESS with the share).
- Step 3: our dots opposite excluded author segments get judged by sharpness (same instrument): report their median S -- on-edge (>=line) or not.
- Slots per 209 pattern throughout. No new thresholds invented; the 229 line stands.

## Acceptance (lead judges; numbers + cites + paths)
- Repro of 229 control/disputed numbers (or REPRO-FAIL with the divergence).
- Per-lane rescore table: old med/cov vs new med/cov, author-excluded share, sharpness of our dots in excluded zones.
- Verdict: RESCORED-AT-BAR / RESCORED-NEAR-MISS (with the remaining gap named) / MEANINGLESS (excluded share too large) / REPRO-FAIL. One line on what changes (P27 grade only; bar values and all other pieces untouched).

## Comments (worker 230, 2026-10-21 -- laptop-only, nothing touched except this ticket + fresh .scratch/pota230/)

**Bottom line: RESCORED-NEAR-MISS.** Repaired ruler changes nothing numerically -- new == old on both lanes (Bl0 med 0.83/cov 58.5, Bl1 med 0.91/cov 68.9 vs bar med<2/cov>=90%). Med passes, coverage is the remaining gap (38/65 and 42/61 within 2mm of on-edge author). Excluded shares 22.4%/16.7% -- rescore is meaningful, not MEANINGLESS. P27 grade only: still below bar on coverage; bar values and all other pieces untouched.

**Step 1 -- REPRO: PASS-EXACT.** Bit-identical to ticket 229: baseline 1.294, control 41.63/41.47 PASS, line 16.29, disputed 39.22/1.35, control max-dist 0.917. Same code path (rng 229, r=2mm, >=8 pts), same cloud artifacts/pota229/Pot_D_Piece_27_Point.pcd (md5 c3b1bb69..., 83,374 pts).

**Step 2 -- gate + rescore (slots fB0<->oB1 per 209; naive pairs confirm swap: med 8.10/8.23, cov 0.0 = wall thickness).** Author-Bl1 (ref for ours-Bl0): 38/49 on-edge, excluded 11/49 = 22.4%. Author-Bl0 (ref for ours-Bl1): 40/48 on-edge, excluded 8/48 = 16.7%. No NaNs anywhere. Rescore table (old -> new): Bl0 0.83/58.5 -> 0.83/58.5; Bl1 0.91/68.9 -> 0.91/68.9. Unchanged because the re-routed dots (ours opposite excluded author) already sat >=2mm from any author dot -- the coverage gap IS the 229 excursion, where ours was proven right.

**Step 3 -- our dots opposite excluded segments ride the crease.** Ours-Bl0 in excluded zones: n=22, med S 40.2, 22/22 >= line -> ON-EDGE. Ours-Bl1 in excluded zones: n=13, med S 35.1, 12/13 >= line -> ON-EDGE.

**Picture (eye-checked).** .scratch/pota230/p230_rescore.png: per matched pair, ours-S profile (blue, above line throughout) + plan map (gold author on-edge, black excluded off-edge mid-face stretches, blue ours on the cloud boundary). Scheme gold/blue/black only.

**Script + numbers.** .scratch/pota230/p230_rescore.py (numpy+matplotlib only), p230_numbers.csv (repro six), p230_rescore.csv (old/new med/cov + excluded share per lane), p230_S_author.csv (per author dot S + on/off), p230_S_ours.csv.

**What this changes.** P27 grade only: still below bar, but the remaining coverage gap now reads as ruling against ours where 229 proved ours at-edge and author mid-face -- a ruler-caveat note for the lead, not a rule or bar change.

## Required evidence to report
- Bottom line first (verdict + new med/cov). Then repro check, exclusion shares, sharpness numbers, picture (gold author with excluded segments marked + blue ours), script path.
