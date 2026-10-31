# stage48 instruments -- what is a byte copy, and what is new

Ticket 48 PART 1 (verify arm).  Every shared instrument is a BYTE COPY of the stage45 file
(itself byte-identical to stage46's, which is how the 44/45/46 grid stayed comparable); the
run's own drivers are new, and the ticket says what changed in each.  md5s below were taken
from the files as committed in this directory.

## Byte copies (unmodified -- md5 identical to stage45/instruments)

| file | md5 | source | why unmodified |
|---|---|---|---|
| dist43.py | 33fc4bb124225a61d124c570479a8667 | .scratch/juglet-breaklines/stage45/instruments/dist43.py | the frozen distance protocol; changing it would break comparability with 43/44/45/46 |
| grow38.py | 2935869749eea7ae44341bdfe1d9e17a | .../stage45/instruments/grow38.py | the frozen surfacepair/grow statistics the pair table is measured with |
| measure34.py | 055090a5577ca1e8066a6e4f5146a3f2 | .../stage45/instruments/measure34.py | the frozen measure34 protocol (cell/agg, read_ply/read_pcd helpers figures48 imports) |
| mesh38.py | a5e8ff2523229a592189acd82be02cef | .../stage45/instruments/mesh38.py | frozen OBJ reader used for the silhouette in the panel |
| nest39.py | 03a747b72d3acb65062451ca8a8b5685 | .../stage45/instruments/nest39.py | frozen nest/pair counting beside grow38 |
| replica37.py | e190a7948fdf1d65a9f7195e0450a764 | .../stage45/instruments/replica37.py | frozen replica helper carried by the stage's instrument set |
| wall40.py | fcd710b66b6c960119f71ed47e79f651 | .../stage45/instruments/wall40.py | frozen wall-face helper carried by the stage's instrument set |
| stage_synth_p40.sh | 9bb59676bc08157687010955d1d9ebc8 | .../stage45/instruments/stage_synth_p40.sh | the stager that lays out the per-cell Dataset the pipeline reads; ticket 48 runs the same pipeline the same way |
| .gitattributes | 50e02870ff69bcacb0b67593ceeca161 | .../stage45/instruments/.gitattributes | `* -text`: no eol conversion, the files must be committed LF |
| .gitignore | ee0ddfac36a14ff01578b1a9fab32ed8 | .../stage45/instruments/.gitignore | same ignore set the earlier stages ship |

## Adapted or new (NOT copies)

| file | adapted from | what changed, and why |
|---|---|---|
| run_cell48.sh | stage46/instruments/run_cell46.sh | Pass 1 is now the CORPUS-MANIFEST gate, not the covering gate: every Juglet cloud's md5 must equal `MANIFEST_JUGLET_CC.tsv`'s `pcd_md5` read BY HEADER NAME (the manifest opens with two `#` comment lines, so the header is the first non-comment line), plus a sweep proving no `*_covering.pcd` sits under `$DS/Point` or `$CORP/Point`. Pot A released clouds are recorded, not gated. Arm E/arm A are gone: one arm V, `arm_env` returns exactly `SFS_GROWTH_FORMULA=1`, display `formula`, stager KIND `REAL-RELEASED-CLOUD`, and `RUN_CLOUD=$CLOUD` always (no covering). The covering/spacing proof passes of 46 are replaced by `env_proof.tsv` (must read exactly `SFS_GROWTH_FORMULA=1`) and `theta_proof.tsv` (paper-grow `thetaDeg=` vs the `[GROWTH-45]` theta). 14 columns, and the SKIP row carries 14 fields. |
| theta_check48.py | stage46/instruments/theta_check46.py | REPORT ONLY, by the ticket's wording ("report where it lands and STOP -- no tuning, no re-runs"): it exits 0 with the table even when every piece lands outside the band, and exits nonzero only when it cannot produce the table at all (unreadable inputs, or a cell with no theta evidence). Band is the ~2% the ticket names, not 46's 0.30 deg. Reads `thetas48.tsv` and emits `pot piece arm theta_computed_deg theta_ref_deg delta_abs delta_pct within_2pct note`. |
| run_pair48.py | stage45/instruments/run_measure34.py (wrapper shape) + the pair commands at run_cell44.sh:238-261 | The pair commands are the stage44 protocol byte-for-byte (`grow38.py surfacepair` then `nest39.py pair`, same flags, same outdir), run on the surfaces each cell KEPT. Writes `pairs48.tsv`, `nests48.tsv`, `surfaces48.tsv`. A cell that grew only one surface gets a surfaces48 row and no pair row -- that is a result, not a crash. measure34's cell/agg path is not used here because ticket 48 asks for the pair table, not the coverage/fold census. |
| figures48.py | stage46/instruments/figures46.py | Only the panel survives (fig_a compared a covering against a shipped cloud, and ticket 48 has no covering). 3x3 over the nine Juglet pieces, one arm, `juglet_panel48.png`, title carries outcome + surface counts + the `[GROWTH-45]` theta. |
| submit48.sh | stage45/instruments/submit45.sh | Branch/tag/runid names, single phase, `run_cell48.sh` + `thetas48.tsv` as the required instruments, run.json rewritten for this ticket (part 1 of 3, corpus gate, source unchanged). |
| submit48.sbatch.tmpl | stage45/instruments/submit45.sbatch.tmpl | Single phase, arm V only, `CELL_BUDGET_S=1200 MIN_LEFT_S=120` (t45 took 00:04:56 with 21 cells; 17 cells + theta check + pairs + one panel fit 00:30:00). `SFS_GROWTH_FORMULA` added to the `unset` list so no inherited env can leak in. `md5_corpus` now also covers `$DS/Point/Pot_A/*.pcd` and the manifest file itself. Adds the theta check, the Pot A control report against t45 arm F's committed numbers, the pair table and the panel. Index row still written with verdict/human_note EMPTY. |
| thetas48.tsv | stage45/instruments/thetas44.tsv | Same ticket-43 k-rule numbers, column renamed `theta_ref_deg`; REFERENCE ONLY, no cell reads it. 17 rows (Juglet 1-9, Pot A 01-08). |
