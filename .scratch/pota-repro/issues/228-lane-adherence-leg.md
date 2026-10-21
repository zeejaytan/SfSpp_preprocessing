Status: done

## Lead verdict (2026-10-21)
NO-SEPARATION accepted. R6: metrics.csv on disk (16 rows; spot values EXACT: P27@4.5 1.50/54.9, P27@8 0.87/62.9); verdict + lane set + candidate table in Comments verified; picture p228_P27worst_vs_P15control.png on disk (gold/blue/black, lane-only overlay as stated); job-free laptop run, no sacct; only this ticket touched among tracked files. Decisive detail: wandering lanes are smooth (njumps=0 all 6) at the scale of already-accepted defects (P12 corner 14-19 dots, P01 hook 11 dots) -- no lane-only measure can part them from good lanes. 4th leg, if it exists, must be face-based (needs Spartan P27 ladder faces) or P27 stays a known limitation. No rule frozen.

## Goal
Find the 4th leg (lane rim-adherence, author-free): a measure computed WITHOUT author lanes that separates P27's wandering lanes (P27@4.5/@8/@12: med sub-mm yet cov 55-69%, excursions to 16-18mm) from the good lanes (P15@8, P16@10, P01@8, P12@4.5-Bl1, P12-Bl0 modulo the known 19-dot corner). Propose the leg with its line; do NOT freeze anything (user + lead freeze). User order m03577-pick-1; context m03576.

## Boundary (worker: LAPTOP-ONLY analysis, no Spartan runs)
- Inputs (all on disk, verify present before starting): our lanes P27@4.5 (pota225/lanes), P27@8 (pota226/lanes), P27@12 (pota227/lanes), P15@8 + P16@10 (pota222 or 225 cites), P01@8 (220 cite), P12@4.5 (pota223/lanes), P12@3 (pota224/lanes, negative control: interior shortcut), + the face surfaces/boundaries those lanes were walked on (ladder surfaces, .xyz) + mesh for context.
- MAY touch: fresh dir C:/PR/SfSpp_preprocessing/.scratch/pota228/ for scripts + a metrics table (csv) + pictures (gold/blue/black scheme ONLY: author GOLD #ffae00, ours BLUE #0057ff, off-rim BLACK; never similar colours for different things).
- MUST NOT touch: Spartan (no sbatch, no ssh jobs); main worktree tracked files except this ticket's Comments; other tickets; bundles. Author lanes in the SCORER ONLY (to report med/cov of each candidate-filtered lane, never to define the leg).

## Constraints
- Candidate measures must be computable from (lane + faces) alone. Suggested (not mandated): (1) lane-dot-to-face-boundary distance distribution (share of lane dots >2mm off the walked faces' boundary); (2) loop-closure endgap relative to lane length; (3) max single-jump and jump count; (4) lane length vs walked-face boundary length. Report each candidate's value on EVERY lane above (good + wandering + shortcut + corner) before nominating.
- Slots per piece (209 pattern) when scoring; bar med<2/cov>=90% unchanged.

## Acceptance (lead judges; numbers + cites + paths)
- Metrics table (rows = lanes, columns = candidates + author-scored med/cov for reference) + the nominated leg with its line + the separation table (leg value on good vs wandering lanes, no overlap).
- Eye-check pictures for P27@12 (or worst wandering case): our lane vs author on mesh, distinct colours + zoom on the excursion (223/224 pattern).
- Verdict: LEG-NOMINATED (frozen wording proposal + line + which lanes it accepts/rejects) or NO-SEPARATION (all candidates overlap -- report the overlap with numbers).


## Comments (worker 228, 2026-10-21 -- LAPTOP-ONLY, nothing frozen)

**Verdict: NO-SEPARATION.** No author-free candidate separates P27's 6 wandering lanes from the good lanes without overlap or fatal confounding. Closest approach (fixed-window backbone share) is confounded with loop size. No rule frozen (per brief).

**Lane set (16 rows, all verified on disk):** P27@4.5 pota225/lanes, P27@8 pota226/lanes, P27@12 pota227/lanes (refs pota225/*_author.pcd); P15@8+P16@10 pota222/lanes (refs pota221/pota221f/author); P01@8 .wt-220/artifacts/pota220/p01_8_* (refs p01_author_*); P12@4.5 pota223/lanes, P12@3 pota224/lanes (refs pota222/p12/auth_*). Slots per 209 pattern (whole lane vs nearer author lane).

**Candidate results (author-free; scorer med/cov/max reference only):**
- (2) endgap/len: wandering 0.0155-0.0201; good 0.0028-0.0327 -> OVERLAP. REJECTED.
- (3) maxjump / njumps(>10mm): wandering maxjump 1.8-4.5, njumps=0 all 6 rows; good lanes carry the jumps (P01@8/Bl1 11.2/1, P12@4.5/Bl0 13.4/1, P12@4.5/Bl1 10.0/1, P12@3/Bl1 12.3/1) -> wrong direction. REJECTED.
- Backbone-residual max-run grid (w=15/21/25/31/41 x thr 3/4/5/6mm): overlap at EVERY cell (e.g. w15/thr5: wandering maxrun 2 vs good up to 3; w25/thr5: wandering 7-10 vs good 6-9). Size-normalized windows (w=n//4,6,8) invert or overlap. REJECTED.
- Self-neck (min 3D dist, walk-gap>=15): wandering 8.3-17.9 vs good 0.8-21.2 -> OVERLAP. REJECTED.
- Spacing CV: confounded with file provenance (.xyz resampled CV=0.000 vs .pcd raw); wandering 0.011-0.180 inside good 0.000-0.473. REJECTED. len/span: wandering 2.51-2.86 vs good 2.45-3.61. REJECTED.
- (1) off-face-boundary share / (4) lane-vs-face-boundary length: NOT EVALUABLE laptop-only -- P27 ladder faces live on Spartan (pota221_ladder/thr_*), touching Spartan forbidden. Proxy on local-era faces: off-face share on good lanes with local faces is 0-1.7% (tight, but zero wandering rows to compare -> cannot nominate).
- Closest: res15share (w=15 fixed, share resid>2mm): good max 27.3 (P12@4.5/Bl0 corner) / shortcut 30.8 / wandering min 33.8. Only ~3pt margins AND monotonic in 1/loop-length across pieces (P01 7-10 -> P15/P16 18-23 -> P12 23-31 -> P27 34-61): it measures loop size, would reject ANY small-loop lane. NOT nominated.

**Why it is hard (scorer-side structure):** wandering runs are smooth (zero jumps), broad (13-23 consecutive dots >=2mm, max 9.5-17.7) -- same width scale as the accepted P12 corner (14-19 dots, max 4.5) and the P01@8/Bl1 end-hook (11 dots, max 9.6 on an at-bar 0.61/96.6 lane). No tested author-free geometry separates these without overfitting.

**Pictures:** .scratch/pota228/p228_P27worst_vs_P15control.png -- P27@12/Bl0 (worst: 0.83/58.5 max 17.7, 27 off-rim dots across the seam) vs author + P15@8/Bl0 control. Gold #ffae00 author / blue #0057ff ours / black off-rim. NO Pot_D P27 mesh exists on the laptop, so lane-only overlay (stated in picture); no substitution made.

**Artifacts:** .scratch/pota228/metrics.csv (16 rows x candidates + scorer ref) + metrics228.py, grid.py, norm.py, neck2.py, last.py, runs.py, wtest.py, render228.py.

## Required evidence to report
- Bottom line first: nominated leg + line, or no-separation with the closest candidate's overlap. Then table, pictures, scripts, scorer numbers.
