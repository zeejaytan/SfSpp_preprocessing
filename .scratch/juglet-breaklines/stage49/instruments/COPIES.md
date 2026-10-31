# stage49/instruments — what is a copy and what is not

Ticket 49 (make the fold radius scale-free, then re-derive k).  Two kinds of file live here and the
difference matters: a **byte copy** is executed unchanged and its md5 must equal the stage it came
from, so a result measured with it is measured with the same code as before; an **adapted** file
was changed for this ticket and must not be described as a copy.

Every byte copy below was copied with `cp -p` from
`C:/PR/SfSpp_preprocessing/.scratch/juglet-breaklines/stage48/instruments/` (itself a byte copy of
`stage45/instruments`) and its md5 was re-read after the copy.  The job re-proves it independently:
`submit49.sbatch.tmpl` git-archives the pushed commit, md5s `*.py *.sh *.tsv` there, md5s the run
directory copies, and fails with rc=4 if the two lists differ — so a run can never execute an
instrument that is not the committed byte.

## Byte copies (unmodified — md5 identical to stage48/instruments)

| file | md5 | source | why unmodified |
|---|---|---|---|
| dist43.py | 33fc4bb124225a61d124c570479a8667 | stage48/instruments/dist43.py | distance statistics; nothing ticket 49 changes touches them, and a changed copy would make the pair table incomparable with 44/46/48 |
| grow38.py | 2935869749eea7ae44341bdfe1d9e17a | stage48/instruments/grow38.py | the `surfacepair` command of the stage44 protocol — the frozen pair measurement every stage since 44 has used |
| measure34.py | 055090a5577ca1e8066a6e4f5146a3f2 | stage48/instruments/measure34.py | PLY/point readers shared by the figures and the pair scripts; changing a reader silently changes every number it feeds |
| mesh38.py | a5e8ff2523229a592189acd82be02cef | stage48/instruments/mesh38.py | OBJ reader for the released silhouette in the panels |
| nest39.py | 03a747b72d3acb65062451ca8a8b5685 | stage48/instruments/nest39.py | the `pair` command of the stage44 protocol (shared-point / normal-dot statistics) |
| replica37.py | e190a7948fdf1d65a9f7195e0450a764 | stage48/instruments/replica37.py | released-mesh replica check used by the pair protocol |
| wall40.py | fcd710b66b6c960119f71ed47e79f651 | stage48/instruments/wall40.py | ticket 40's 800-ray wall thickness; kept as the reference implementation `wall49.py` was lifted from, and runnable as-is for a single-piece cross-check |
| stage_synth_p40.sh | 9bb59676bc08157687010955d1d9ebc8 | stage48/instruments/stage_synth_p40.sh | the stager: symlinks the cloud and the mesh, copies the axis, writes `inputs.md5`. Staging by symlink is what keeps a 51-cell grid from copying ~50 MB clouds 51 times |
| thetas49.tsv | 53fa273fd429f824fe813f6b66a8c628 | stage48/instruments/thetas48.tsv | the ticket-43 k-rule reference thetas. Byte-identical **on purpose**: ticket 49 must be scored against the same reference numbers ticket 48 was, so the file was renamed, not edited |
| .gitattributes | 50e02870ff69bcacb0b67593ceeca161 | stage48/instruments/.gitattributes | `* -text` — no EOL conversion, so the committed bytes are the executed bytes. This is the file that makes the CRLF gate meaningful |
| .gitignore | ee0ddfac36a14ff01578b1a9fab32ed8 | stage48/instruments/.gitignore | `__pycache__/` and `*.pyc` — the submitter compiles the scripts, and a committed `.pyc` would be a second, stale copy of the code |

## Adapted or new (NOT copies)

| file | adapted from | what changed and why |
|---|---|---|
| run_cell49.sh | run_cell48.sh | The grid is now **2 patch radii x 2 cloud sets x 17 pieces** instead of one arm, so: `RADII` and `CLOUDSETS` loops; `arm_env` returns `SFS_GROWTH_FORMULA=1 SFS_PATCH_R_MM=<R>` (the env the ticket is about); `arm_kind` labels corpus cells `REAL-RELEASED-CLOUD` and calibration cells `REAL-ATTIC-CLOUD`; a **second gate (pass 1b)** md5s every archived vertex dump against its own `manifest.tsv`, because the calibration case is only the calibration case if the dumps are the ones ticket 45 measured; cells read `$ATTIC/<piece>_Point.pcd` when the cloud set is `attic`; `pipeline_cells.tsv` went from 14 to **16 columns** (adds `patch_r`, `r_med_mm`, `skipped`) and the SKIP row carries 16 too; `cell.tsv` gains `patch_r_env`, `cloud_set`, `r_med_mm`, `patch_r_logged`, `skipped`; `env_proof.tsv` now demands the exact two-variable env, and `theta_proof.tsv` carries the patch radius. Budget raised to `CELL_BUDGET_S=3900`/`MIN_LEFT_S=180` for 51 cells. |
| run_pair49.py | run_pair48.py | The pair protocol is **unchanged** (same two commands, same tags, same JSON keys) — only the bookkeeping moved: the arm label is now `r<R>-<cloudset>` instead of a single letter, so `patch_r` and `cloud_set` are split out into their own columns of `pairs49.tsv`/`nests49.tsv`/`surfaces49.tsv`, and the per-pair log line prints `med_nn`, `med_angle_deg` and `coin` so the two radii can be compared straight from the job log. The `{"V": "formula"}` display remap was dropped: it existed to rename one arm letter and would mangle a real label. |
| theta_check49.py | theta_check48.py | Still REPORT ONLY with the same 2% band and the same "a miss is a result" contract, but the table now carries `patch_r` and `cloud_set` and prints **in-band counts per (radius, cloud set)**, not one pooled number — ticket 48's failure was cloud-dependent, so a pooled "0 of 17" would hide exactly the effect this run measures. The pooled total is still printed, labelled as for the record only. |
| figures49.py | figures48.py | One 3x3 panel per (patch radius, cloud set) — four panels, `juglet_panel49_r<R>_<cloudset>.png` — instead of one. Cell directories are `<piece>_r<R>_<cloudset>`; titles gained `R_med` and `skipped`; `figures_summary.tsv` gained `patch_r`, `cloud_set`, `r_med_mm`, `skipped`. The grey silhouette is the same released mesh in all four panels, so the reader compares grown surfaces against one fixed reference. |
| wall49.py | wall40.py | The thickness machinery (`read_obj`, `weld`, `read_ply_vertices`, `unit`, `ray_hits`, `sheets`, `pct`, the 800-ray block) is lifted **verbatim**, so the numbers stay comparable with tickets 35/40. New: it walks the run's cells instead of one mesh+arm, carries `patch_r`/`cloud_set` so a row joins to `pairs49.tsv`, caches on (mesh md5, arm md5) because the patch radius does not resample the cloud, and adds `known_wall_mm` (J2 2.693, J3 2.452, J5 2.900, J7 3.263, J9 2.595 mm) so the earlier stages' measurements sit beside this run's and a disagreement is visible rather than buried. |
| k49.py | — (new) | The ticket's re-derivation of k. Per piece it reports `k_now` (recovered from the `[GROWTH-45]` line) and `k_needed_linear = k_now x wall/pair`; the genuine-wall-pair test is stated in the file (two surfaces, `coin <= 0.01`, `med_angle_deg >= 5`) so a reader can disagree with it, and the test deliberately does not look at the separation it explains. Groups are per vessel at each (radius, cloud set) **and** pooled, with median, spread, n and min/max; the one-k question is answered by comparing the pooled medians at a 10% threshold. The file states in its own header that this is a **fit on the pieces it is reported against**, not a test, and that `k_needed_linear` is a linear projection to be checked by running that k. |
| submit49.sh | submit48.sh | Same gates (CR byte count over `*.sh *.py *.tmpl *.tsv`, `py_compile`, `bash -n`, no surviving placeholder, expansion-count floor, no CR in the render), same "build from `origin/<branch>`, never from this checkout" rule, same refusal to reuse an existing run directory. Changes: requires `run_cell49.sh`, `stage_synth_p40.sh`, `thetas49.tsv`, `submit49.sbatch.tmpl`; `ATTIC` is resolved and passed to the template; the run id is `<stamp>_<git7>_t49-<tag>`; `run.json` records `patch_radii_mm [1.0, 1.5]`, `cloud_sets ["corpus","attic"]` and `cells_planned 51`; the render gate prints the substitution count and line count it measured. |
| submit49.sbatch.tmpl | submit48.sbatch.tmpl | Same shape (fail() writing `RUN-FAILED.txt`, instruments proved against the commit, corpus censused before and after, geometry counted before it is deleted, `finish()` trap on TERM/INT that still appends the index row with **empty verdict**). Changes: `SFS_PATCH_R_MM` added to the `unset` list so a stray value cannot leak into a cell; `ATTIC` defined and included in both the corpus census and `md5_corpus`; `phase_cells` emits `POT:PIECE` and lets `run_cell49.sh` expand the radii and cloud sets; the cells call passes `RADII CLOUDSETS MIN_LEFT_S=180 CELL_BUDGET_S=3900`; the theta check is `theta_check49.py`; new phases 8b `wall49.py` and 8c `k49.py` between the pair table and the figures; the figures call is `figures49.py`. |

## What is deliberately NOT here

- No copy of `wall40.py`'s CLI wrapper: ticket 49 measures every cell inside the grid job, so
  `wall49.py` replaced the wrapper while keeping the measurement itself byte-for-byte.
- No `stage48` figures script: the four-panel layout is a different figure, not a tweak.
- No per-radius pair script: the pair protocol is identical at both radii, and a second copy would
  be a second thing to keep in step.
