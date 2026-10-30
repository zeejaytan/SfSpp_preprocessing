# 2026-10-31 — third `artifacts/` sweep (laptop, SfSpp_preprocessing)

**Why.** Rule 13 of the workspace `AGENTS.md` (“nothing is deleted without a record, proved by reading
it back”) run as a one-shot cleanup on the laptop, following
`docs/agents/workspace-hygiene.md`. The record below was written **before** the `rm` and is the
INDEX rule 13 asks for; the census after the delete is the last section.

## What the gate said before anything was touched

`python C:/PR/scripts/check_artifacts.py SfSpp_preprocessing` (exit 1):

```
artifacts/ — C:/PR/SfSpp_preprocessing/artifacts
  7897 files, 337.1 MB across 296 entries (ceiling 300 MB)
  cited paths in tracked files: 637
  geometry no tracked file cites: 137 files, 21.3 MB (ceiling 50 MB)
  largest offenders:
         5.6 MB  artifacts/mesh_for_viewing/Pot_E_Piece_16_Mesh_DS.obj
         4.2 MB  artifacts/mesh_for_viewing/Pot_H_Piece_02_Mesh_DS.obj
         3.7 MB  artifacts/mesh_for_viewing/Pot_C_Piece_03_Mesh_DS.obj
         2.3 MB  artifacts/mesh_for_viewing/Pot_H_Piece_10_Mesh_DS.obj
         2.0 MB  artifacts/mesh_for_viewing/Pot_D_Piece_22_Mesh_DS.obj
         1.3 MB  artifacts/mesh_for_viewing/Pot_J_Piece_09_Mesh_DS.obj
         1.2 MB  artifacts/mesh_for_viewing/Pot_D_Piece_27_Mesh_DS.obj
         0.0 MB  artifacts/pota275/C01_S0/Pot_C_Piece_01_Breakline_1.pcd
         0.0 MB  artifacts/pota275/C01_V0/Pot_C_Piece_01_Breakline_1.pcd
         0.0 MB  artifacts/pota273/J01_bag.pcd
  (re-fetch from the run directory, or cite the file from a ticket)

Result: artifacts/ needs a sweep -- folder is 337.1 MB, over the 300 MB ceiling
```

## The four offenders this sweep was sent for were already gone

The brief named `artifacts/pcdcheck/C01_ours.pcd` (49,781,270 B), `artifacts/pcdcheck/C01_release.pcd`
(28,000,957 B), `artifacts/pota273/C01_bag.pcd` (30,867 B) and `artifacts/pota293/png.tgz` (8,537,397 B),
and quoted 7,895 files / 417.0 MB / 140 uncited geometry files 95.5 MB as “measured today”. Those four
are the ones deleted by the previous pass, `docs/notes/2026-10-30-artifacts-sweep-2.md` (82.3 MB dropped);
its “Why” paragraph carries exactly the 7,895 / 417.0 MB / 95.5 MB figures. Measured here: `ls` of
`artifacts/pcdcheck/` returns one file, `cmp.py`, 2,428 B; `artifacts/pota293/png/` holds 11 files; all four
paths do not exist. So this pass starts from 337.1 MB, not 417.0 MB.

## Classes, stated before the first delete (rule 13)

- **record class — kept:** `*.log *.out *.err *.md *.sbatch *.sh *.json *.csv *.txt *.tsv *.patch *.py`
  **and every image** (`*.png *.jpg *.jpeg *.svg *.pdf`).
- **geometry class — deletable, but only with a named source:** `*.pcd *.obj *.ply *.xyz *.npy *.npz`.
  A cloud is re-fetched in seconds; a picture of it is not re-derivable.
- **never-delete class:** anything a tracked file cites, anything written in the last 24 h,
  `artifacts/visual-qa/` and `artifacts/mesh_for_viewing/` whole, source (`.py` that is not glue), symlinks.

## Dropped: 73 files, 420,213 B (0.40 MB)

| path | bytes | class | verdict | reason | re-fetch from |
|---|---|---|---|---|---|
| `artifacts/pota20/p20fetch2.tar.gz` | 3744 | spent tarball | dropped | unpacked and byte-identical beside it (48/48 members) | none needed - byte-identical unpacked copy beside it |
| `artifacts/pota210/pota210_T_fetch.tgz` | 833 | spent tarball | dropped | unpacked and byte-identical beside it (9/9 members) | none needed - byte-identical unpacked copy beside it |
| `artifacts/pota22/p22fix2.tgz` | 2057 | spent tarball | dropped | unpacked and byte-identical beside it (24/24 members) | none needed - byte-identical unpacked copy beside it |
| `artifacts/pota22/p22swap.tgz` | 1339 | spent tarball | dropped | unpacked and byte-identical beside it (15/15 members) | none needed - byte-identical unpacked copy beside it |
| `artifacts/pota22/p22t.tgz` | 1233 | spent tarball | dropped | unpacked and byte-identical beside it (14/14 members) | none needed - byte-identical unpacked copy beside it |
| `artifacts/pota23/pota23_scores.tgz` | 2389 | spent tarball | dropped | unpacked and byte-identical beside it (29/29 members) | none needed - byte-identical unpacked copy beside it |
| `artifacts/pota240_evidence.tgz` | 3720 | spent tarball | dropped | unpacked and byte-identical beside it (15/15 members) | none needed - byte-identical unpacked copy beside it |
| `artifacts/pota287/out/C01_after/Pot_C_Piece_01_Breakline_0.pcd` | 13824 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_C_Piece_01_Breakline_0.pcd | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_C_Piece_01_Breakline_0.pcd` |
| `artifacts/pota287/out/C01_after/Pot_C_Piece_01_Breakline_0.ply` | 16413 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_C_Piece_01_Breakline_0.ply | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_C_Piece_01_Breakline_0.ply` |
| `artifacts/pota287/out/C01_after/Pot_C_Piece_01_Breakline_0.xyz` | 11255 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_C_Piece_01_Breakline_0.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_C_Piece_01_Breakline_0.xyz` |
| `artifacts/pota287/out/C01_after/Pot_C_Piece_01_Breakline_0_stepring.xyz` | 0 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_C_Piece_01_Breakline_0_stepring.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_C_Piece_01_Breakline_0_stepring.xyz` |
| `artifacts/pota287/out/C01_after/Pot_C_Piece_01_Breakline_1.pcd` | 14988 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_C_Piece_01_Breakline_1.pcd | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_C_Piece_01_Breakline_1.pcd` |
| `artifacts/pota287/out/C01_after/Pot_C_Piece_01_Breakline_1.ply` | 17768 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_C_Piece_01_Breakline_1.ply | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_C_Piece_01_Breakline_1.ply` |
| `artifacts/pota287/out/C01_after/Pot_C_Piece_01_Breakline_1.xyz` | 12197 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_C_Piece_01_Breakline_1.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_C_Piece_01_Breakline_1.xyz` |
| `artifacts/pota287/out/C01_after/Pot_C_Piece_01_Breakline_1_stepring.xyz` | 0 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_C_Piece_01_Breakline_1_stepring.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_C_Piece_01_Breakline_1_stepring.xyz` |
| `artifacts/pota287/out/C01_before/Pot_C_Piece_01_Breakline_0.pcd` | 1906 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_C_Piece_01_Breakline_0.pcd | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_C_Piece_01_Breakline_0.pcd` |
| `artifacts/pota287/out/C01_before/Pot_C_Piece_01_Breakline_0.ply` | 2629 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_C_Piece_01_Breakline_0.ply | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_C_Piece_01_Breakline_0.ply` |
| `artifacts/pota287/out/C01_before/Pot_C_Piece_01_Breakline_0.xyz` | 1352 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_C_Piece_01_Breakline_0.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_C_Piece_01_Breakline_0.xyz` |
| `artifacts/pota287/out/C01_before/Pot_C_Piece_01_Breakline_0_stepring.xyz` | 0 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_C_Piece_01_Breakline_0_stepring.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_C_Piece_01_Breakline_0_stepring.xyz` |
| `artifacts/pota287/out/C01_before/Pot_C_Piece_01_Breakline_1.pcd` | 5611 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_C_Piece_01_Breakline_1.pcd | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_C_Piece_01_Breakline_1.pcd` |
| `artifacts/pota287/out/C01_before/Pot_C_Piece_01_Breakline_1.ply` | 6894 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_C_Piece_01_Breakline_1.ply | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_C_Piece_01_Breakline_1.ply` |
| `artifacts/pota287/out/C01_before/Pot_C_Piece_01_Breakline_1.xyz` | 4385 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_C_Piece_01_Breakline_1.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_C_Piece_01_Breakline_1.xyz` |
| `artifacts/pota287/out/C01_before/Pot_C_Piece_01_Breakline_1_stepring.xyz` | 0 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_C_Piece_01_Breakline_1_stepring.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_C_Piece_01_Breakline_1_stepring.xyz` |
| `artifacts/pota287/out/H02_after/Pot_H_Piece_02_Breakline_0.pcd` | 10330 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_02_Breakline_0.pcd | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_02_Breakline_0.pcd` |
| `artifacts/pota287/out/H02_after/Pot_H_Piece_02_Breakline_0.ply` | 12351 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_02_Breakline_0.ply | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_02_Breakline_0.ply` |
| `artifacts/pota287/out/H02_after/Pot_H_Piece_02_Breakline_0.xyz` | 8226 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_02_Breakline_0.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_02_Breakline_0.xyz` |
| `artifacts/pota287/out/H02_after/Pot_H_Piece_02_Breakline_0_stepring.xyz` | 0 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_02_Breakline_0_stepring.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_02_Breakline_0_stepring.xyz` |
| `artifacts/pota287/out/H02_after/Pot_H_Piece_02_Breakline_1.pcd` | 9489 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_02_Breakline_1.pcd | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_02_Breakline_1.pcd` |
| `artifacts/pota287/out/H02_after/Pot_H_Piece_02_Breakline_1.ply` | 11345 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_02_Breakline_1.ply | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_02_Breakline_1.ply` |
| `artifacts/pota287/out/H02_after/Pot_H_Piece_02_Breakline_1.xyz` | 7553 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_02_Breakline_1.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_02_Breakline_1.xyz` |
| `artifacts/pota287/out/H02_after/Pot_H_Piece_02_Breakline_1_stepring.xyz` | 0 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_02_Breakline_1_stepring.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_02_Breakline_1_stepring.xyz` |
| `artifacts/pota287/out/H02_before/Pot_H_Piece_02_Breakline_0.pcd` | 10180 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_02_Breakline_0.pcd | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_02_Breakline_0.pcd` |
| `artifacts/pota287/out/H02_before/Pot_H_Piece_02_Breakline_0.ply` | 12221 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_02_Breakline_0.ply | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_02_Breakline_0.ply` |
| `artifacts/pota287/out/H02_before/Pot_H_Piece_02_Breakline_0.xyz` | 8228 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_02_Breakline_0.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_02_Breakline_0.xyz` |
| `artifacts/pota287/out/H02_before/Pot_H_Piece_02_Breakline_0_stepring.xyz` | 0 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_02_Breakline_0_stepring.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_02_Breakline_0_stepring.xyz` |
| `artifacts/pota287/out/H02_before/Pot_H_Piece_02_Breakline_1.pcd` | 9337 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_02_Breakline_1.pcd | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_02_Breakline_1.pcd` |
| `artifacts/pota287/out/H02_before/Pot_H_Piece_02_Breakline_1.ply` | 11199 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_02_Breakline_1.ply | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_02_Breakline_1.ply` |
| `artifacts/pota287/out/H02_before/Pot_H_Piece_02_Breakline_1.xyz` | 7539 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_02_Breakline_1.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_02_Breakline_1.xyz` |
| `artifacts/pota287/out/H02_before/Pot_H_Piece_02_Breakline_1_stepring.xyz` | 0 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_02_Breakline_1_stepring.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_02_Breakline_1_stepring.xyz` |
| `artifacts/pota287/out/H10_after/Pot_H_Piece_10_Breakline_0.pcd` | 6594 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_10_Breakline_0.pcd | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_10_Breakline_0.pcd` |
| `artifacts/pota287/out/H10_after/Pot_H_Piece_10_Breakline_0.ply` | 8141 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_10_Breakline_0.ply | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_10_Breakline_0.ply` |
| `artifacts/pota287/out/H10_after/Pot_H_Piece_10_Breakline_0.xyz` | 5338 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_10_Breakline_0.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_10_Breakline_0.xyz` |
| `artifacts/pota287/out/H10_after/Pot_H_Piece_10_Breakline_0_stepring.xyz` | 0 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_10_Breakline_0_stepring.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_10_Breakline_0_stepring.xyz` |
| `artifacts/pota287/out/H10_after/Pot_H_Piece_10_Breakline_1.pcd` | 6074 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_10_Breakline_1.pcd | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_10_Breakline_1.pcd` |
| `artifacts/pota287/out/H10_after/Pot_H_Piece_10_Breakline_1.ply` | 7595 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_10_Breakline_1.ply | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_10_Breakline_1.ply` |
| `artifacts/pota287/out/H10_after/Pot_H_Piece_10_Breakline_1.xyz` | 4890 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_10_Breakline_1.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_10_Breakline_1.xyz` |
| `artifacts/pota287/out/H10_after/Pot_H_Piece_10_Breakline_1_stepring.xyz` | 0 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_10_Breakline_1_stepring.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_10_Breakline_1_stepring.xyz` |
| `artifacts/pota287/out/H10_before/Pot_H_Piece_10_Breakline_0.pcd` | 6790 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_10_Breakline_0.pcd | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_10_Breakline_0.pcd` |
| `artifacts/pota287/out/H10_before/Pot_H_Piece_10_Breakline_0.ply` | 8141 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_10_Breakline_0.ply | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_10_Breakline_0.ply` |
| `artifacts/pota287/out/H10_before/Pot_H_Piece_10_Breakline_0.xyz` | 5338 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_10_Breakline_0.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_10_Breakline_0.xyz` |
| `artifacts/pota287/out/H10_before/Pot_H_Piece_10_Breakline_0_stepring.xyz` | 0 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_10_Breakline_0_stepring.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_10_Breakline_0_stepring.xyz` |
| `artifacts/pota287/out/H10_before/Pot_H_Piece_10_Breakline_1.pcd` | 6258 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_10_Breakline_1.pcd | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_10_Breakline_1.pcd` |
| `artifacts/pota287/out/H10_before/Pot_H_Piece_10_Breakline_1.ply` | 7595 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_10_Breakline_1.ply | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_10_Breakline_1.ply` |
| `artifacts/pota287/out/H10_before/Pot_H_Piece_10_Breakline_1.xyz` | 4890 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_10_Breakline_1.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_10_Breakline_1.xyz` |
| `artifacts/pota287/out/H10_before/Pot_H_Piece_10_Breakline_1_stepring.xyz` | 0 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_H_Piece_10_Breakline_1_stepring.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_H_Piece_10_Breakline_1_stepring.xyz` |
| `artifacts/pota287/out/J01_after/Pot_J_Piece_01_Breakline_0.pcd` | 11508 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_J_Piece_01_Breakline_0.pcd | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_J_Piece_01_Breakline_0.pcd` |
| `artifacts/pota287/out/J01_after/Pot_J_Piece_01_Breakline_0.ply` | 13638 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_J_Piece_01_Breakline_0.ply | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_J_Piece_01_Breakline_0.ply` |
| `artifacts/pota287/out/J01_after/Pot_J_Piece_01_Breakline_0.xyz` | 9198 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_J_Piece_01_Breakline_0.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_J_Piece_01_Breakline_0.xyz` |
| `artifacts/pota287/out/J01_after/Pot_J_Piece_01_Breakline_0_stepring.xyz` | 0 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_J_Piece_01_Breakline_0_stepring.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_J_Piece_01_Breakline_0_stepring.xyz` |
| `artifacts/pota287/out/J01_after/Pot_J_Piece_01_Breakline_1.pcd` | 12377 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_J_Piece_01_Breakline_1.pcd | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_J_Piece_01_Breakline_1.pcd` |
| `artifacts/pota287/out/J01_after/Pot_J_Piece_01_Breakline_1.ply` | 14732 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_J_Piece_01_Breakline_1.ply | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_J_Piece_01_Breakline_1.ply` |
| `artifacts/pota287/out/J01_after/Pot_J_Piece_01_Breakline_1.xyz` | 9899 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_J_Piece_01_Breakline_1.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_J_Piece_01_Breakline_1.xyz` |
| `artifacts/pota287/out/J01_after/Pot_J_Piece_01_Breakline_1_stepring.xyz` | 0 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_J_Piece_01_Breakline_1_stepring.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_J_Piece_01_Breakline_1_stepring.xyz` |
| `artifacts/pota287/out/J01_before/Pot_J_Piece_01_Breakline_0.pcd` | 3293 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_J_Piece_01_Breakline_0.pcd | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_J_Piece_01_Breakline_0.pcd` |
| `artifacts/pota287/out/J01_before/Pot_J_Piece_01_Breakline_0.ply` | 4280 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_J_Piece_01_Breakline_0.ply | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_J_Piece_01_Breakline_0.ply` |
| `artifacts/pota287/out/J01_before/Pot_J_Piece_01_Breakline_0.xyz` | 2522 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_J_Piece_01_Breakline_0.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_J_Piece_01_Breakline_0.xyz` |
| `artifacts/pota287/out/J01_before/Pot_J_Piece_01_Breakline_0_stepring.xyz` | 0 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_J_Piece_01_Breakline_0_stepring.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_J_Piece_01_Breakline_0_stepring.xyz` |
| `artifacts/pota287/out/J01_before/Pot_J_Piece_01_Breakline_1.pcd` | 5488 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_J_Piece_01_Breakline_1.pcd | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_J_Piece_01_Breakline_1.pcd` |
| `artifacts/pota287/out/J01_before/Pot_J_Piece_01_Breakline_1.ply` | 6791 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_J_Piece_01_Breakline_1.ply | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_J_Piece_01_Breakline_1.ply` |
| `artifacts/pota287/out/J01_before/Pot_J_Piece_01_Breakline_1.xyz` | 4332 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_J_Piece_01_Breakline_1.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_J_Piece_01_Breakline_1.xyz` |
| `artifacts/pota287/out/J01_before/Pot_J_Piece_01_Breakline_1_stepring.xyz` | 0 | uncited geometry | dropped | copy of that run's out/; uncited; re-fetch <run>/out/Pot_J_Piece_01_Breakline_1_stepring.xyz | `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out/Pot_J_Piece_01_Breakline_1_stepring.xyz` |
| `artifacts/pota39/pota39_fetch_B_R2.tgz` | 1148 | spent tarball | dropped | unpacked and byte-identical beside it (11/11 members) | none needed - byte-identical unpacked copy beside it |
| `artifacts/untouched_pota_verify_20261015/task3_gt.tgz` | 828 | spent tarball | dropped | unpacked and byte-identical beside it (9/9 members) | none needed - byte-identical unpacked copy beside it |

Totals: uncited geometry 64 files / 402,922 B (0.384 MB); spent tarballs 9 files / 17,291 B (0.017 MB).

The 64 geometry files are a copy of one run's `out/`; the run directory is named in the file that put them
here — `artifacts/pota287/out/score287.txt:3` reads
`out dir: /data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/out` (also
`artifacts/pota287/out/score287b.txt:3`). Their ticket numbers live in `.scratch/pota-repro/`; the `edge.log`,
`exit.txt` and `sheets_*.md5` beside them are record class and stay.

The 9 tarballs were proved spent member by member: every member extracted and its SHA-256 compared with an
unpacked copy of the same basename and size found elsewhere under `artifacts/`; all members matched in each
case (example: `artifacts/pota23/pota23_scores.tgz`, 29/29 members == `artifacts/pota23/scores/before/`,
`after/`). Nothing else about them is re-fetchable, which is why only these 9 of 158 went.

## Kept, with the numbers, and why (all of it before the delete)

| kept | files | MB | why |
|---|---|---|---|
| `artifacts/visual-qa/` | 46 | 112.9 | every file cited by a tracked file; the conservator's staged eye |
| `artifacts/mesh_for_viewing/` | 9 | 24.0 | 2 cited (3.9 MB), 7 uncited (20.2 MB); the conservator's eye |
| images elsewhere, uncited | 361 | 79.3 | record class (every image); a picture is not re-derivable |
| images elsewhere, cited | 266 | 50.7 | cited |
| geometry elsewhere, cited | 30 | 39.7 | cited by a tracked file |
| uncited tarballs | 149 | 19.78 | not unpacked locally: 0 members matched an unpacked copy, so no `cmp` |
| uncited text / tables / scripts | 6,780 | 8.2 | record class, each under 1 MB |
| fetched logs over 1 MB | 2 | 3.13 | no run directory named in the directory (see below) |
| uncited geometry, no run dir named | 66 | 0.71 | provenance not nameable locally (see below) |
| cited text / tables | 111 | 1.1 | cited |
| cited archives | 6 | 0.4 | cited |

**Provenance-less geometry, kept — 66 files, 747,177 B, in 16 directories.** Their directories carry no
run-directory text, so they are not re-fetchable by the brief's own test:
pota275 (`C01_D` 4, `C01_F0` 4, `C01_S0` 4, `C01_V0` 4, `J01_D` 4, `J01_F0` 4, `J01_S0` 4, `J01_V0` 4,
`P22_D` 4, `P22_S0` 4, `author` 6, root 5 zero-byte files), `pota289/data` 7, `pota287/auth` 4,
`pota295_lead` 3, `pota273/J01_bag.pcd` 1. `pota275/*` do carry `run.log`, `config.txt` and `sheets.md5`
(the record), but no run id; `pota289/data` holds locally derived clouds (`lane0.pcd`, `authO_0.pcd`,
`boundaryImproved.pcd`) whose inputs are the frozen corpus, again with no run id in the directory.

**The 149 tarballs kept (19.78 MB).** They are fetch bundles whose contents were read from a temporary
unpack and never unpacked beside themselves, so rule 13's extract-and-`cmp` has nothing to compare against.
Provenance is a lookup away, not in hand: 130 of the 158 embed their Slurm job id in the filename
(`pota84_fetch_33361199.tgz`, `fetch_33387455.tgz`) and 12 embed it in member paths
(`pota63_fetch_D_R1_33275817/…`), and job id to run id is a row in
`/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv` — a Spartan read this cleanup may not make. Branch
taken: keep, and record the key. The arithmetic says the same: 19.78 MB against a 37.1 MB deficit does
not reach the ceiling, and a bundle is the only local copy of what it carries.

**The 2 fetched logs over 1 MB kept (3,282,547 B).** `artifacts/pota295_lead/E16.diag276.txt` (1,587,347 B)
and `H02.diag276.txt` (1,695,200 B), both 2026-10-25 18:18-18:21. The run ids named anywhere in that
directory are `20261025-2356_66d4ad9_p277-axis-loud` (`fill277.py:4`), `20261025-2234_3d5d537_p296-*`
(`fill296.py:5-7`) and `20261026-000*_05ae973|a21822e_p297-chord` (`fill297.py:5-6`) — other tickets',
none of them the run that wrote `diag276`. Left rather than guessed.

## Guards, in the order they ran

1. **Listing completeness** (the truncated-read trap): `git ls-files -z` parsed 4,838 paths, plain
   `git ls-files` listed 4,838 — MATCH.
2. **Cited set** rebuilt with the gate's own regex over the same 4,838 tracked files: 637 tokens, the
   gate's own count; a file was dropped only if no token equalled it or was a parent directory of it.
3. **`visual-qa/` and `mesh_for_viewing/` excluded whole** before any candidate was formed.
4. **Nothing younger than 24 h.** Cutoff 2026-10-30T02:08 (sampled 2026-10-31T02:08 local). Youngest
   dropped file: `artifacts/pota240_evidence.tgz`, 2026-10-22 11:52; youngest dropped geometry 2026-10-24 20:59.
5. **Three assertions before the `rm`, all required to print 0:** cited files among the 73 = 0; files
   younger than 24 h among the 73 = 0; listed paths missing from disk = 0 (73/73 present).
6. **One `rm` per path, from the 73 rows above**, no wildcards, no directory removes.

## The census after the delete

Same command, after the 73 removals (exit 1):

```
artifacts/ — C:/PR/SfSpp_preprocessing/artifacts
  7824 files, 336.7 MB across 295 entries (ceiling 300 MB)
  cited paths in tracked files: 637
  geometry no tracked file cites: 73 files, 20.9 MB (ceiling 50 MB)
  ...
Result: artifacts/ needs a sweep -- folder is 336.7 MB, over the 300 MB ceiling
```

**Before → after, per class (files / MB):**

| class | before | after |
|---|---|---|
| folder | 7,897 files / 337.1 MB / 296 entries | 7,824 files / 336.7 MB / 295 entries |
| uncited geometry | 137 / 21.3 | 73 / 20.9 |
| — of which `mesh_for_viewing/` | 7 / 20.2 | 7 / 20.2 |
| — of which elsewhere | 130 / 1.10 | 66 / 0.71 |
| spent tarballs | 158 / 19.80 | 149 / 19.78 |
| fetched logs over 1 MB | 2 / 3.13 | 2 / 3.13 |
| images (`visual-qa/` 112.86 + uncited 79.25 + cited 50.68) | 673 / 242.8 | 673 / 242.8 |
| cited geometry elsewhere | 30 / 39.68 | 30 / 39.68 |
| text / tables / scripts | 6,891 / 9.30 | 6,891 / 9.30 |
| folders | 296 entries | 295 (“`artifacts/pota240_evidence.tgz`” was a top-level file) |

**What holds the 336.7 MB, and the deficit.** 300 MB ceiling, so 36.7 MB over. Images are
242.8 MB of it (72% of the folder); the two staged viewer areas are 136.9 MB (40.6%) and are cited or
the conservator's eye; cited evidence outside them adds 50.68 MB of images, 39.68 MB of geometry, 1.07 MB of
tables and 0.39 MB of archives. Of the classes that are neither an image nor staged, the largest is
39.68 MB of cited geometry and the largest *uncited* one is the 149 fetch bundles at 19.78 MB: removing
every one of those, and every remaining provenance-less cloud (0.71 MB) and the two `diag276` logs
(3.13 MB) as well, leaves 313.0 MB — still over. The geometric classes in this brief cannot reach 300 MB;
what remains is pictures (242.8 MB) and staged viewer pairs (136.9 MB).

**Three directories are empty and were left alone** (not on the delete list, so not removed):
`artifacts/pota294/data/`, `artifacts/pota287/out/B01_after/`, `artifacts/pota287/out/B01_before/` — all
three were already empty before this pass (no file of them is in the 73 rows above).

## Rules that had to be interpreted

1. **“Spent tarball”** was read as hygiene line 48 (“unpack in place under `artifacts/`, then the tarball
   is spent; delete once unpacked and read”) plus rule 13's extract-and-`cmp`. Applied only where every
   member had a byte-identical unpacked twin (9 of 158); the other 149 kept.
2. **The protected-directory clause is self-contradictory** in the brief (“keep them unless the gate
   would stay red without them; if so, keep them”). Taken in the parenthetical's sense — they are not a
   sweep's to delete — so both stay; the numbers are in the kept table.
3. **“Fetched log > 1 MB”** was read as a log whose run directory can be named from local text. Both
   candidates failed that test and were kept.
4. **Images were not treated as a candidate class.** The brief lists three; rule 13 puts every image in
   the record class and `docs/agents/workspace-hygiene.md` says a picture is not re-derivable, which is
   why the picture stays and the cloud goes. 79.3 MB of uncited overlays therefore remain, and they are
   the single largest item that a different ruling could remove.
