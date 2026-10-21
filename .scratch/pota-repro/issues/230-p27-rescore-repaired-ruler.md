Status: ready-for-agent

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

## Required evidence to report
- Bottom line first (verdict + new med/cov). Then repro check, exclusion shares, sharpness numbers, picture (gold author with excluded segments marked + blue ours), script path.
