# stage38 instruments: what is copied, what is new

## Copied verbatim from stage37/instruments, then line endings converted

These three files are the ticket-37 growth and measurement code. They are copied so a
stage-38 job runs the same arithmetic as ticket 37 rather than a re-typed version of it.
The copies were byte-identical to their stage-37 originals as copied; they were then
converted from CRLF to LF (all three stage-37 files carry CRLF) so that the run's CRLF gate
covers `*.py` as well as the shell drivers. Line counts are unchanged, no line content
changes, so the behaviour and the numbering of every line quoted in ticket 37's report are
preserved.

| file | lines | stage37 md5 (CRLF) | stage38 md5 (LF) |
|---|---|---|---|
| replica37.py | 386 | 7c5d88d94a88a99738ee130807062459 | e190a7948fdf1d65a9f7195e0450a764 |
| measure34.py | 890 | e9f3b28be4908b4008b99d8085c8c948 | 2cbf7ffee6740ef0cc6cedb2b64c7135 |
| fig37.py | 238 | ac90f56b05e3a123e0517f0a74ec433b | 20e4a633ce6063ee8594a60a76fea527 |

## New in stage 38

| file | what it does |
|---|---|
| mesh38.py | mesh reader, midpoint subdivision, measured displacement to the original surface, surface sampler with analytic face normals, nearest-neighbour spacing, PCD writer, sampler validation, selftests |
| grow38.py | the four normal arms (scan / A analytic / F analytic+viewpoint flip / B PCA re-estimation) run through replica37's unchanged growth, ranked pre-floor dumps, the largest-region and pair measurements, and the aggregate tables |
| fig38.py | one figure per target piece: a row per level against the original mesh, plus largest region against achieved spacing with the 50-point floor |
| parte38.py | Part E: the ticket-37 style re-rendered for calibration, and every region drawn from a continuous rank palette at full opacity, with the ink / grey / colour fractions measured from the PNGs |
| run_targets38.sh | phase 1: validation, subdivision, sampling, growth cells for the two target sherds, figures, aggregate |
| run_controls38.sh | phase 2: control sherds 3, 5, 7 and Pot_A 07, then Part E and the aggregate |
| run_cell38.sh | phase 3: one real pipeline cell on a synthetic cloud |
| stage_synth_p38.sh | staging with a synthetic cloud in place of the shipped one, every row tagged SYNTHETIC |
| submit38.sbatch.tmpl, submit38.sh | the batch script and its renderer (placeholder check, CRLF gate, bash -n, run.json) |
