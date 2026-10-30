# stage45/instruments -- COPIES.md

Byte-copies from stage44/instruments (0 CR bytes each, md5 recorded at copy time):

| file | md5 | status |
|------|-----|--------|
| dist43.py | 33fc4bb124225a61d124c570479a8667 | byte-copy from stage44/instruments |
| grow38.py | 2935869749eea7ae44341bdfe1d9e17a | byte-copy from stage44/instruments |
| measure34.py | 055090a5577ca1e8066a6e4f5146a3f2 | byte-copy from stage44/instruments |
| mesh38.py | a5e8ff2523229a592189acd82be02cef | byte-copy from stage44/instruments |
| nest39.py | 03a747b72d3acb65062451ca8a8b5685 | byte-copy from stage44/instruments |
| replica37.py | e190a7948fdf1d65a9f7195e0450a764 | byte-copy from stage44/instruments |
| wall40.py | fcd710b66b6c960119f71ed47e79f651 | byte-copy from stage44/instruments |
| stage_synth_p40.sh | 9bb59676bc08157687010955d1d9ebc8 | byte-copy from stage44/instruments |
| thetas44.tsv | 9049bd9d198fde7cb64df17c6d2248b1 | byte-copy from stage44/instruments -- REFERENCE ONLY (ticket 43 k-rule theta, tolerance 0.30 deg); no cell reads it |
| spec44.tsv | 926bafbb8112b7d7615a7a14668b3392 | byte-copy from stage44/instruments -- provenance of the reference thetas |
| .gitattributes | 50e02870ff69bcacb0b67593ceeca161 | byte-copy from stage44/instruments |
| .gitignore | ee0ddfac36a14ff01578b1a9fab32ed8 | byte-copy from stage44/instruments |

Adapted from stage44 (diff-reviewed before commit):

- run_cell45.sh -- run_cell44.sh with: arms F (no env, the new curvature-derived default,
  [GROWTH-45] parsed into cell.tsv) and O (SFS_PAPER_THETA=3.4, today's path) replacing
  A/B/C/N; pipeline_cells.tsv in the ticket-45 dispatch schema (13 columns, arm vocabulary
  "formula"/"3.4", theta_computed_deg from the cell's own [GROWTH-45] line, blank for O);
  the wall/surface/pair/nest measurement passes DROPPED (ticket 44's question, not 45's --
  the surfaces are still copied out per cell, unmeasured); defaults_proof replaced by
  override_proof.tsv (the O cell's SampledWithNormals md5); theta_proof rewritten to compare
  the paper-grow theta against the [GROWTH-45] theta (F) or 3.4 (O).  Staging, cloud gate,
  pipeline invocation, geometry counting and stage deletion are byte-identical logic.
- submit45.sh + submit45.sbatch.tmpl -- single phase (4), both vessels, arm F on all 17
  pieces + arm O on the four proof pieces, ONE binary build (the source change is the
  ticket), run dir t45-<tag>, reference-theta REPORT pass added (theta_check.tsv, 0.30 deg,
  never a gate); gates, corpus md5, geom_delete, index row unchanged from ticket 44.

Two defects fixed in the adapted copies (both would have corrupted a result row, neither is a
gate weakening):

- run_cell45.sh SKIP row printed 14 tab fields against the 13-column pipeline_cells.tsv header
  (inherited from run_cell44.sh:310-311, which has the same defect). Now 13, checked by
  gate45.py.
- submit45.sbatch.tmpl theta_check.tsv awk treated a "-" placeholder in the theta column as a
  number, so a SKIP row produced a spurious delta against the reference instead of a
  no-evidence row. The evidence test now also rejects "-".

New in stage45 (not copies): gate45.py and dryrender45.py at stage45/ top level, the local
gates (CR census, py_compile, bash -n, placeholder census, SKIP-row field count; and a dry
render reproducing submit45.sh's substitution). Same role as stage44/verify44.py; nothing in
the run imports them.
