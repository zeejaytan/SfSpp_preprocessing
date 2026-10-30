# stage44/instruments -- COPIES.md

Byte-copies from stage43/instruments (0 CR bytes each, md5 recorded at copy time):

| file | md5 | status |
|------|-----|--------|
| dist43.py | 33fc4bb124225a61d124c570479a8667 | byte-copy from stage43/instruments |
| grow38.py | 2935869749eea7ae44341bdfe1d9e17a | byte-copy from stage43/instruments |
| measure34.py | 055090a5577ca1e8066a6e4f5146a3f2 | byte-copy from stage43/instruments |
| mesh38.py | a5e8ff2523229a592189acd82be02cef | byte-copy from stage43/instruments |
| nest39.py | 03a747b72d3acb65062451ca8a8b5685 | byte-copy from stage43/instruments |
| replica37.py | e190a7948fdf1d65a9f7195e0450a764 | byte-copy from stage43/instruments |
| wall40.py | fcd710b66b6c960119f71ed47e79f651 | byte-copy from stage43/instruments |
| stage_synth_p40.sh | 9bb59676bc08157687010955d1d9ebc8 | byte-copy from stage43/instruments |
| .gitattributes | 50e02870ff69bcacb0b67593ceeca161 | byte-copy from stage43/instruments |
| .gitignore | ee0ddfac36a14ff01578b1a9fab32ed8 | byte-copy from stage43/instruments |

Adapted from stage43 (diff-reviewed before commit):

- run_cell44.sh -- run_cell43.sh with the ticket-44 header only; the BODY is byte-identical.
  Arm B still reads column 3 of the thetas tsv, which here is the formula theta.
- submit44.sh + submit44.sbatch.tmpl -- single phase (4), both vessels in one CELL_LIST with
  the :AB arm suffix, THETAS from the committed thetas44.tsv (no partA dependency), run dir
  t44-<tag>, everything else (gates, corpus md5, geom_delete, index row) unchanged.

New in stage44 (not copies):

- thetas44.tsv -- pot piece theta_formula_deg, VERBATIM from ticket 43's committed k-rule
  prediction table (theta = k x S/R_fold, k = 3.3573); never recomputed.
- spec44.tsv -- provenance of every theta: the spacing and fold radius it came from
  (stage43/results/partA.tsv), k, the formula value, and the ticket-42 ladder theta.
