

### Verdicts, and what is left to the fix

| bar | verdict |
|---|---|
| 1 | **PASS** — the split is exactly 2/6/9 outer; Bl0 rides the foreign wall on 9/9, so the defect is upstream of the line. |
| 2 | **PASS** — the rule is `classifyAndOrderPaper234` (`mesh_processing_headless.cpp:3688`, called :4008), a two-input vote; on 2 and 9 the staged axis line is on the wrong side of the wall, on 6 the normals it reads were inverted (`Normals flipped: true`, the only piece of nine), and nothing checks the answer against geometry. |
| 3 | **ANSWERED** — the pre-1031 geometry survives for t30 and t41 only; the inverted set there was {4,7}, piece 6 was right then, and pieces 2/9 produced no surfaces at all on the vertex-dump clouds. The misfiling set moved with the 1031 regen + chain change. |
| 4 | **FAIL at its criterion** (3 of 5: 1-2 +0.704, 2-5 +0.948, 7-9 +0.708 pass; 1-9 −0.039 and 6-7 −0.183 fail, no strict inlier on either). Every one of the five moved off the control, and the wall side is causally load-bearing — but not sufficient. |
| 4b | **Residual located** — no per-piece sign flip reaches the bar (all variants land on ±0.039 / ±0.183); the failures are sign mixing *inside* one line, so the fix needs both halves: file by the wall, and re-sign the exported line normals per point against that wall. |
| 5 | **PASS** — three before/after renders, eye-checked; the fringe that fails 1-9 is visible on piece 9's swapped-in line. |

**Jobs, sacct-recorded** (`ssh spartan sacct -j <id> --format=JobID,State,ExitCode`):
`34687732` **COMPLETED 0:0** (bar 4, 44 s, partition sapphire);
`34690603` **COMPLETED 0:0** (bar 4b, 18 s — it ran to completion before my withdrawal landed).
Both under `/data/gpfs/projects/punim2657/SfSpp/runs/20261110-2028_1b131dc_t327-swap/` with `run.json`,
`submit.sbatch`, `logs/`, `out/`; the sign-variant trees and `work/setup_neg.sh`, `work/submit_neg.sbatch`
live there too. Nothing outside that run dir was written on Spartan.

**Inputs untouched** (listed before and after; the after-listing is this one, and `find -newermt
"2026-11-10 20:00"` returns nothing under any of the four trees):
t66 bundle `20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom` = 36 files (`Juglet_Piece_N.{S0,S1}`
PLY + `{Bl0,Bl1}` PCD, N=1..9); `Dataset/Axes/Juglet` = 9 `_Axis.xyz` + `README-not-a-reference.md`;
`Dataset/Juglet_GT` = 9×(`_T.txt`, `_Axis.xyz`) + `Juglet_simple_graph.txt` + `README-axes.md`;
`sfs_main/original_samples/SfS_pp/Point` = `Pot_A..Pot_J` + `MANIFEST_released.tsv`/`MANIFEST_derived.tsv`/`README.md`.
(The Juglet_GT axis files carry mtime 2026-11-10 07:23 from the ticket-322 work recorded in AGENTS.md, i.e.
before this session; nothing in this ticket touched them.) No ORIG or GT points entered any diagnostic input:
the GT key only defines the radial coordinate in bars 1/3/5 and the pair placement in bar 4, and the only
geometry handed to the harness is the t66 export (and its copies).

**Scripts** (all under `.scratch/pota-repro/t327/`): `census327.py`, `census327_old.py`, `classifier327.py`,
`blnormals327.py`, `pairprobe327.py`, `check_radii.py`, `parse_bar4.py`, `parse_bar4b.py`, `render327.py`,
`setup_swap.sh`, `submit_swap.sbatch`, `setup_neg.sh`, `submit_neg.sbatch`.
**Data kept** under `artifacts/pota327/`: `geom/`, `gt/`, `dsaxis/`, `old_t30/`, `old_t41/`, `swap/`,
`renders/`, and the JSONs `census_bar1.json`, `census_bar3_old.json`, `classifier_bar2.json`.
