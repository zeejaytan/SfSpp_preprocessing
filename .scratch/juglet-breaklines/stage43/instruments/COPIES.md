# stage43/instruments -- COPIES.md

Copies from stage42/instruments, md5 recorded on the laptop (0 CR bytes each):

| file | md5 | status |
|------|-----|--------|
| mesh38.py | a5e8ff2523229a592189acd82be02cef | copy from stage42/instruments (CR bytes: 0) |
| measure34.py | 055090a5577ca1e8066a6e4f5146a3f2 | copy from stage42/instruments (CR bytes: 0) |
| replica37.py | e190a7948fdf1d65a9f7195e0450a764 | copy from stage42/instruments (CR bytes: 0) |
| grow38.py | 2935869749eea7ae44341bdfe1d9e17a | copy from stage42/instruments (CR bytes: 0) |
| nest39.py | 03a747b72d3acb65062451ca8a8b5685 | copy from stage42/instruments (CR bytes: 0) |
| wall40.py | fcd710b66b6c960119f71ed47e79f651 | copy from stage42/instruments (CR bytes: 0) |
| stage_synth_p40.sh | 9bb59676bc08157687010955d1d9ebc8 | copy from stage42/instruments (CR bytes: 0) |

New in stage43 (not copies):

- dist43.py -- Part A/B instrument: neighbour-turn distributions on the mesh sampled at the
  pipeline's resolved spacing, labelled within-face / across-fold by source-triangle normals,
  plus rules R1 (k x within p90, k calibrated on Pot A median = 3.4) and R2 (geometric mid-gap).
- run_cell43.sh -- the Part C cell driver (arms A no-env / B SFS_PAPER_THETA=R1 / C =R2 / N
  no-env rerun for the defaults-unchanged proof), thetas read from the run dir's thetas.tsv.
- submit43.sh + submit43.sbatch.tmpl -- renderer, CRLF/parse/py_compile gates, submit.
