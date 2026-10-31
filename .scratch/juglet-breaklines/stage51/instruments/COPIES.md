# stage51 instrument provenance

Byte copies from stage44/instruments (verified md5 against stage44/COPIES.md before commit):

- dist43.py 33fc4bb1
- grow38.py 29358697
- measure34.py 055090a5
- mesh38.py a5e8ff25
- nest39.py 03a747b7
- replica37.py e190a794
- wall40.py fcd710b6
- stage_synth_p40.sh 9bb59676
- .gitattributes, .gitignore

New for ticket 51 (modeled on stage48's run_cell48.sh / submit48.sh / submit48.sbatch.tmpl
and the t50-theta45 run's paircheck45.py):

- run_cell51.sh     cells driver: corpus-manifest gate (pcd_md5 AND kept_points vs
                    MANIFEST_JUGLET_CC.tsv), arms C/U, 16-column pipeline_cells.tsv,
                    env_proof + theta_proof, [GROWTH-51] parsing, cell surfaces kept
- thetas51.tsv      REFERENCE ONLY: t48 arm-V formula theta + t50 edge50 glue60 k=10
- thetas51.py       mechanical assembler -> out/thetas51.tsv + reference checks (REPORT ONLY)
- pairquality51.py  paircheck45.py protocol parameterised over <PIECE>_arm{C,U}/surfaces
- submit51.sh       submitter (render, gates, run dir, sbatch)
- submit51.sbatch.tmpl  the job: build from the pushed commit, instruments md5, corpus
                    before/after, arms C+U cells, thetas + pair quality, geom record/delete,
                    index append with empty verdict
