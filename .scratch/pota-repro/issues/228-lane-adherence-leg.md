Status: ready-for-agent

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

## Required evidence to report
- Bottom line first: nominated leg + line, or no-separation with the closest candidate's overlap. Then table, pictures, scripts, scorer numbers.
