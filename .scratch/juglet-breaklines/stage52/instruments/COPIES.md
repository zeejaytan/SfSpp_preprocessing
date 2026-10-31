# stage52 instrument provenance

Byte copies from stage51/instruments (verified md5 against stage51's committed copies before
commit; wall40.py fcd710b6 checked both sides):

- dist43.py, grow38.py, measure34.py, mesh38.py, nest39.py, replica37.py, wall40.py,
  stage_synth_p40.sh, .gitattributes, .gitignore
- thetas51.tsv, copied again as thetas52-reference.tsv: REFERENCE ONLY (t48 formula theta +
  t50 edge50 glue60 k=10; the t51 run predates the ticket-50 spacing merge, so no cell is
  EXPECTED to match it); no cell reads it

New for ticket 52 (modeled on stage51's run_cell51.sh / submit51.sh / submit51.sbatch.tmpl /
thetas51.py / pairquality51.py; changes are only what ticket 52 names):

- run_cell52.sh     cells driver: same corpus-manifest gate, arms D/C/X (D = NO SFS_* growth
                    variable, the shipped default; C = SFS_GROWTH_FORMULA=1 SFS_GROWTH_CAP=1;
                    X = SFS_PAPER_THETA=3.4), 17-column pipeline_cells.tsv with
                    paper_theta_log + fallback52, POSITIVE apptainer env probe per cell
                    (arm D must see NO SFS_GROWTH*/SFS_PAPER_THETA at all), env_proof +
                    theta_proof, [GROWTH-45]/[GROWTH-51]/[GROWTH-52] parsing, cell surfaces
                    kept
- thetas52.py       mechanical assembler -> out/thetas52.tsv (the ticket's per piece x arm
                    summary) + theta_check52.tsv (D==C exactness: theta + crossing to 5 dp,
                    surf0/surf1 point counts)
- pairquality52.py  paircheck45.py protocol parameterised over <PIECE>_arm{D,C,X}/surfaces,
                    plus med_nn as a % of the piece's own wall (wall40.py jsons, optional)
- submit52.sh       submitter (render, gates, run dir, sbatch), branch
                    52-ship-the-capped-curvature-angle-by-default, tag t52-<tag>
- submit52.sbatch.tmpl  the job: build from the pushed commit, instruments md5, corpus
                    before/after, arms D+C+X cells (CELL_BUDGET_S=4200), thetas + D==C check,
                    wall40 pass on arm-D cells, pair quality with wall %, geom record/delete,
                    index append with empty verdict
