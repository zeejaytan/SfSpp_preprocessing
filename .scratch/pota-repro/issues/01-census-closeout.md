# 01: Census close-out (Spartan ls + threshold overrides)

**What to build:** the one Spartan listing that closes the carried gap: per-pot file counts under `original_samples/SfS_pp` plus the runtime-threshold answer, so the expansion list can be confirmed.

**Answers:** E1

**Blocked by:** None (can start immediately).

**Status:** results-in — counts + threshold + exact lines in Comments; E1 write-back still to do

**Working in:** C:\PR\SfSpp_preprocessing @ adadbf2 (ticket-only edit; Spartan read-only, no sbatch)

- [x] Spike: confirm `ls` paths for Mesh/Surfaces/Breaklines/Axes/GT per pot A–J (one Spartan `ls`, no recursion under `/data/gpfs`)
- [x] Per-pot file-count table recorded in ticket Comments
- [x] Threshold answer: whether the mesh run CLI overrides the 4.5/1.5 defaults (`mesh_processing.cpp:1736/1341/1398-1405`) — check sbatch/run scripts + job 33011909 log
- [x] d=1.9mm resample constant + CCW voting lines narrowed to exact lines

## Comments

### 1. Per-pot file counts (2026-10-15, ONE Spartan `ls`-only listing, no find/du)
Source: `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/`
Top-level dirs: `Axes Breaklines "Ground Truth" "Ground Truth Axes" Mesh Surfaces Transformation`.
Per-pot `ls Pot_<L>_* | wc -l` counts (GT = `Ground Truth/` per-pot files = N piece `T.txt` + 1 `simple_graph.txt`):

| Pot | Mesh | Surfaces | Breaklines | Axes | Ground Truth |
|-----|------|----------|------------|------|--------------|
| A | 8 | 16 | 16 | 8 | 9 (8T+graph) |
| B | 9 | 18 | 18 | 9 | 10 (9T+graph) |
| C | 7 | 12 | 12 | 6 | 5 |
| D | 32 | 64 | 64 | 32 | 29 |
| E | 34 | 68 | 68 | 34 | 32 |
| F | 7 | 14 | 14 | 7 | 7 |
| G | 7 | 14 | 14 | 7 | 8 |
| H | 11 | 22 | 22 | 11 | 12 |
| I | 30 | 60 | 60 | 30 | 28 |
| J | 19 | 38 | 38 | 19 | 12 |

Pattern: Surfaces = 2x Mesh, Breaklines = 2x Mesh (2 per piece) for every pot; Axes = 1x Mesh except Pot C (6 axes for 7 meshes — one piece short). Pot A control confirmed: 8/16/16/8/9.

### 2. Threshold answer: NO override — pristine 4.5/1.5 hardcoded
- Pristine control `archive_2025_sfs_modified_src@d5ee6865`: Spartan untouched-build source `untouched_pota_verify_20261015/upstream_src/mesh_processing.cpp:1736` = `double smoothnessAngleThreshold = 4.5, curvatureThreshold = 1.5;` (sole match; `getenv`/`SFS_` grep empty). Def pins source: `sfs_pristine_preproc.def:2,88` = `Upstream DominicoRyu/SfSpp_preprocessing@d5ee6865`. Local `original_nurbs_preprocessing/mesh_processing.cpp:1665` `main(argc,argv)` never touches `argv`, and `:1735-1738` hardcodes `minCluster=50, noOfNeighbours=10` + `4.5/1.5` → `surfaceSegmentation(...)` (`:1341` signature, `:1398-1405` `reg.set*` application). No CLI threshold path exists in pristine.
- Job 33011909 (`untouched_pota`, `sbatch .../untouched_pota_verify_20261015/run_untouched_pota.sbatch`, COMPLETED 0:0): sbatch invokes `$ISO/build/MeshPreprocessing` bare (no args, no `--env SFS_*`); log `logs/run_untouched_pota_33011909.log` grep for `smoothness|curvature|threshold|Segmentation thresholds|SFS_` returns nothing (only SIF sha + binary lines). So the mesh run used compiled-in 4.5/1.5.
- Contrast (fork-only, NOT in this run): `mesh_processing_headless.cpp:2206-2207` `SFS_SMOOTHNESS_DEG`/`SFS_CURVATURE_THRESH` env overrides + `run_juglet_preprocessing.sbatch:163-175` per-piece `--env SFS_SMOOTHNESS_DEG` (P9=12). Ticket-12 sweep default-optimal result stands on the fork, not on this control.

### 3. Exact lines: d=1.9mm resample (fork-only) + CCW voting (pristine)
- d=1.9mm resample does NOT exist in pristine (`upstream_src/edgeline_extraction.cpp` grep `1.9|resample|adaptiveDensify|SFS_RESAMPLE` empty). Fork exact lines — `original_nurbs_preprocessing/edgeline_extraction_headless.cpp:721` (`double resample_spacing_mm = 1.9;`), `:722` (`SFS_RESAMPLE_MM` env override), `:724` (`adaptiveDensifyBreakline(smoothedBreakLine, resample_spacing_mm)` call), `:747` (`MatrixXd adaptiveDensifyBreakline(const MatrixXd& breakline, double target_spacing_mm = 1.9) {`); paper cite comment `:736-738` (§IV-B1 "point-to-point distance of d = 1.9mm").
- CCW voting (pristine control, Spartan `upstream_src/edgeline_extraction.cpp`): `:367-368` (`// Rearrange the matrix array to countclockwise` + `bool Matrix_Rearrange(MatrixXd& src, MatrixXd& src_N)`), `:371` (`double Decision(0);` accumulator), `:402/404` (`Decision++`/`Decision--` per-point normal vote), `:409` (`if (Decision > 0)` keep vs `:416-417` `Change_Sequence(src/src_N)` flip). Local mirrors: `original_nurbs_preprocessing/edgeline_extraction.cpp:365-366,369,399-407,413-415`; fork `edgeline_extraction_headless.cpp:450-451` (def), `:480-502` (vote body), `:2225-2226` (call site `Matrix_Rearrange(MatrixXYZ, MatrixNormals)`). Contract: `edge_line_ordering.h:15-16,48-50` (paper §IV-B1 "reordered counter-clockwise using their normals and a voting algorithm" — released code path via `Matrix_Rearrange`, seam notes the NN-chain defect).
