# stage54 instrument provenance

Copied verbatim from stage53 (branch 53-measure-the-growth-angle-from-the-sherds-own-growth-walk,
tip 75c1060): stage_synth_p40.sh, wall40.py, dist43.py, thetas51.tsv (the crossing reference
this run's W arm is checked against), COPIES.md (this file, rewritten), .gitattributes.
Not carried over: grow38.py, measure34.py, mesh38.py, nest39.py, replica37.py (no ticket-54
cell reads them), thetas53.py (replaced by thetas54.py).

Renamed and edited for ticket 54 (changes are only what ticket 54 names):

- run_cell54.sh     cells driver off run_cell53.sh: arms D/X/W/W7 (D = nothing set, X =
  SFS_PAPER_THETA=3.4, W = SFS_WORNESS=0.9, W7 = SFS_WORNESS=0.7), pipeline_cells.tsv 19
  columns (w + capped added), [WORNESS-54] parsing into cell.tsv, NOTE checks (D/X carry
  NO GROWTH-45/WORNESS-54 line; W/W7 carry GROWTH-45+WORNESS-54 and NO GROWTH-51), FATAL
  probe pass -> worness_fatal_probes.tsv, env_proof.tsv, theta_proof.tsv
- thetas54.py       mechanical assembler -> out/thetas54.tsv (per piece: D/X thetas + surf
  point counts, W/W7 formula/crossing/theta/capped, t51_expected = min(t48, 0.9*edge50)
  from thetas51.tsv, W_delta_t51, W7_le_W) + theta_check54.tsv (D vs X no-op, W7 <= W,
  W/W7 internal theta == min(formula, w*crossing)); exit 0 always, FAILS printed
- pairquality54.py pairquality53.py with the arm set D|X|W7|W
- submit54.sh       submitter (render, gates, run dir, sbatch), branch
  54-rename-the-worn-edge-cap-to-worness-a-dial, tag t54-<tag>
- submit54.sbatch.tmpl  the job: build from the pushed commit, instruments md5, corpus
  gates, D+X+W+W7 phase over 17 pieces + FATAL probes, thetas54 table + check, wall40 on
  the arm-W cells, pairquality54, frozen-input before/after diffs, guarded geometry delete
  (cells surfaces kept), index row append with empty verdict/human_note
