# stage53 instrument provenance

Copied verbatim from stage52 (origin branch 52-ship-the-capped-curvature-angle-by-default,
tip f690c07, unmerged -- restored with git restore --source): stage_synth_p40.sh, wall40.py,
dist43.py, grow38.py, measure34.py, mesh38.py, nest39.py, replica37.py, .gitattributes,
.gitignore, thetas51.tsv (record only; the ticket-52 reference copy thetas52-reference.tsv
was NOT carried over -- no stage53 cell reads a reference table).

Renamed and edited for ticket 53 (modeled on the stage51/stage52 lineage; changes are only
what ticket 53 names):

- run_cell53.sh     cells driver: same corpus-manifest gate, arms W/C/X (W =
  SFS_GROWTH_WALK=1, C = SFS_GROWTH_FORMULA=1 SFS_GROWTH_CAP=1, X =
  SFS_PAPER_THETA=3.4), pipeline_cells.tsv 18 columns (theta_split + theta_ship replace
  fallback52), POSITIVE apptainer env probe per cell, [GROWTH-53] parsing (line,
  theta_split, theta_ship, fallback, ladder) into cell.tsv, theta_proof (W =
  growth53_theta_ship)
- thetas53.py       mechanical assembler -> out/thetas53.tsv (per piece x arm: rc,
  clusters, outcome, surf points, splitter theta, theta45, crossing, capped, theta_split,
  theta_ship, fallback, chosen) + theta_check53.tsv (prediction 1: W theta_ship == the
  pipeline's own paper-grow thetaDeg to 5 dp; ship == 0.9*split unless FALLBACK; no
  GROWTH-53 line outside arm W)
- pairquality53.py  paircheck45.py protocol parameterised over
  <PIECE>_arm{W,C,X}/surfaces, wall40.py medians on the arm-W cells
- submit53.sh       submitter (render, gates, run dir, sbatch), branch
  53-measure-the-growth-angle-from-the-sherds-own-growth-walk, tag t53-<tag>
- submit53.sbatch.tmpl  the job: build from the pushed commit, instruments md5, corpus
  gates, arms WXC phase, thetas53 table + check, wall40 + pairquality53 on W cells,
  corpus before/after diffs, guarded geometry delete, index row append
