# stage46/instruments -- COPIES.md

Byte-copies from stage45/instruments (which are themselves byte-copies from stage44; 0 CR bytes each, md5 recorded at copy time):

| file | md5 | status |
|------|-----|--------|
| dist43.py | 33fc4bb124225a61d124c570479a8667 | byte-copy from stage45/instruments (unchanged) |
| grow38.py | 2935869749eea7ae44341bdfe1d9e17a | byte-copy from stage45/instruments (unchanged) |
| measure34.py | 055090a5577ca1e8066a6e4f5146a3f2 | byte-copy from stage45/instruments (unchanged) |
| mesh38.py | a5e8ff2523229a592189acd82be02cef | byte-copy from stage45/instruments (unchanged) |
| nest39.py | 03a747b72d3acb65062451ca8a8b5685 | byte-copy from stage45/instruments (unchanged) |
| replica37.py | e190a7948fdf1d65a9f7195e0450a764 | byte-copy from stage45/instruments (unchanged) |
| wall40.py | fcd710b66b6c960119f71ed47e79f651 | byte-copy from stage45/instruments (unchanged) |
| stage_synth_p40.sh | 9bb59676bc08157687010955d1d9ebc8 | byte-copy from stage45/instruments (unchanged) |
| .gitattributes | 50e02870ff69bcacb0b67593ceeca161 | byte-copy from stage45/instruments (LF everywhere) |

New in stage46 (written for this ticket):

| file | what it does |
|------|--------------|
| spec46.tsv | one row per piece: the spacing S the ticket-45 run resolved ([SPACING-22]), that run's cloud point count, ticket 43's k-rule theta and ticket 45's measured arm-F theta. The covering is built at column 3; the other columns are references the check compares against. |
| cover_cloud46.py | covers a piece's own shipped mesh with mesh38.sample_at at S, gates achieved spacing (1 pct) and distance to mesh (1e-3 mm, exact over every triangle but on a deterministic 1000-point subsample: the all-point test cost 10+ min a piece and the first attempt was cancelled at phase 1 for it), writes the pcd and a json record. No subdivision (level 1). The covering is projected back onto the mesh after the voxel merge (so every point lies on a triangle) and the spacing gate reads the post-projection median; if that leaves the 1 pct band the sampler is re-asked at the corrected spacing (up to two re-solves, each recorded in spacing_attempts). |
| run_cell46.sh | pass 1 gates the covering and every input (exit 9 before any cell); pass 2 runs the cells with NO SFS_* env, writes pipeline_cells.tsv (14 columns), env_proof.tsv and spacing_proof.tsv, keeps each cell's Surface_0/1 ply and SampledWithNormals, counts the stage geometry then deletes the stage. |
| theta_check46.py | joins pipeline_cells.tsv with spec46.tsv: theta against the k-rule (2 pct gate on the nine Juglet pieces) and against ticket 45's arm-F measurement; also checks the Pot A control's clusters and surface sizes against that run's arm F. |
| run_measure34.py | lays the cells out as measure34.agg expects (tag/pot/piece), measures each with measure34.py cell (covering cloud for arm E, released cloud for arm A) and aggregates into pairs34.tsv. |
| figures46.py | the two eye pictures: j2_covering.png (shipped cloud vs covering on the piece, mm axes) and juglet_surfaces.png (surfaces per piece on the silhouette, counts in the title). |
| submit46.sbatch.tmpl | the job: phase 1 coverings, 4 cells, 7 theta check, 8 pair table, 9 figures; corpus md5 before/after; instruments md5 against the commit; index row with the verdict left empty. |
| submit46.sh | renders, gates and submits the job (CRLF gate, py_compile, placeholder and expansion-count gates, run.json). |

Adapted from stage45 (diff-reviewed before commit):

- run_cell46.sh from run_cell45.sh: arms E (covering) and A (control-released) replacing F/O, both carrying no env;
  the covering gate (pass 1) and the spacing proof are new; pipeline_cells.tsv carries 14 columns so the SKIP row
  prints the same field count as the header (stage44/45 shipped a 14-vs-13 defect, fixed here).
- submit46.sbatch.tmpl from submit45.sbatch.tmpl: stage46 archive path, COVER=$OUT/cells-covering, five phases
  instead of one, covering deleted only after phase 9 has drawn, geom_delete excludes the coverings until then.
- submit46.sh from submit45.sh: BRANCH, t46 tags, PHASE=all, the required-instrument list, run.json content.

The source change of ticket 45 arrives here through the branch merge, not through this directory: main carries
neither of branch 45's commits, so this run builds a binary that computes theta from curvature when no env is set.
