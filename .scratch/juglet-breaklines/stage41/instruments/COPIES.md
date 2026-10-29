# stage41/instruments — COPIES.md

Copies from stage40/instruments, verified md5-identical on the laptop
(`md5sum stage40/instruments/<f>` vs `stage41/instruments/<f>`, all SAME,
0 CR bytes):

| file | md5 | status |
|------|-----|--------|
| mesh38.py | a5e8ff2523229a592189acd82be02cef | SAME (copy) |
| measure34.py | 055090a5577ca1e8066a6e4f5146a3f2 | SAME (copy) |
| measure35.py | a72284540d807f4239465d8e628b40e6 | SAME (copy) |
| grow38.py | 2935869749eea7ae44341bdfe1d9e17a SAME (copy) |
| nest39.py | 03a747b72d3acb65062451ca8a8b5685 | SAME (copy) |
| wall40.py | fcd710b66b6c960119f71ed47e79f651 | SAME (copy) |
| stage_synth_p40.sh | 9bb59676bc08157687010955d1d9ebc8 | SAME (copy) |
| .gitattributes | 50e02870ff69bcacb0b67593ceeca161 | SAME (copy) |
| replica37.py | e190a7948fdf1d65a9f7195e0450a764 | SAME (copy; missed in the first grid run -- grow38 imports it, which is why surfaces/pairs/nest tsvs came back header-only; added for the measurement rerun) |

New in stage41 (not copies):

- run_cell41.sh — the 4-arm x 17-cell grid driver (real released clouds only)
- submit41.sbatch.tmpl — one-job-per-phase sbatch template (build, gates, grid, prune)
- submit41.sh — renderer + CRLF/parse/py_compile gates, writes run.json
- COPIES.md — this file
