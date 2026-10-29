# stage42/instruments -- COPIES.md

Copies from stage41/instruments, verified md5-identical on the laptop
(md5sum stage41/instruments/<f> vs stage42/instruments/<f>, all SAME, 0 CR bytes):

| file | md5 | status |
|------|-----|--------|
| mesh38.py | a5e8ff2523229a592189acd82be02cef | SAME (copy; added for the measurement rerun) |
| measure34.py | 055090a5577ca1e8066a6e4f5146a3f2 | SAME (copy; added for the measurement rerun; holds the fixed signed-t pair_stats) |
| replica37.py | e190a7948fdf1d65a9f7195e0450a764 | SAME (copy; added for the measurement rerun -- the t42 grid's measurement step died on ModuleNotFoundError replica37, which is exactly what this rerun repairs) |
| grow38.py | 2935869749eea7ae44341bdfe1d9e17a | SAME (copy, was already present) |
| nest39.py | 03a747b72d3acb65062451ca8a8b5685 | SAME (copy, was already present) |
| wall40.py | fcd710dab39855d2c960119f71ed47e79f651 | SAME (copy, was already present) |
| stage_synth_p40.sh | 9bb59676bc08157687010955d1d9ebc8 | SAME (copy, was already present) |

New in stage42 (not copies):

- measure42.sh -- measurement-only driver: fills surfaces.tsv, surface_pairs.tsv (+ wall join)
  and nest.tsv from the run of record's KEPT PLYs vs the original clouds/meshes; hard anchors
  J1 armA 2.0146/1.8152/0.5282 and Pot_A PA01 armA 7.0952/7.0888/0.2709 (+/-0.01, miss -> exit 10)
- measure42.sbatch.tmpl -- the one-job sbatch wrapper (instrument md5 vs commit, in-job
  selftests, corpus + kept-PLY md5 before/after, geometry record, index row, sacct)
- submit_measure42.sh -- renderer + CRLF/parse/py_compile/IMPORT-VERIFICATION gates, then submit
- COPIES.md -- this file
