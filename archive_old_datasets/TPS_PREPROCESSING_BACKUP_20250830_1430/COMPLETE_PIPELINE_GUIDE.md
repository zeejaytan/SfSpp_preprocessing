# Complete SFS Pipeline Build & Run Guide

## Overview

This document provides comprehensive instructions for building and running the complete Structure-from-Sherds (SFS) pipeline, covering both preprocessing and main assembly phases.

## Prerequisites

### Environment Setup
```bash
module load MATLAB/2024b_Update_3
module load Apptainer/1.3.3
cd /data/gpfs/projects/punim2657/sfs_preprocessing
```

### Required Containers
- **SFS Main Container**: `/data/gpfs/projects/punim2657/sfs_main/sfspreproc.sif` (815MB)
- **Preprocessing Container**: `/data/gpfs/projects/punim2657/sfs_preprocessing/cache/sfs_prep_from_working.sif`

---

## Phase 1: TPS Preprocessing Pipeline

### 1.1 Build Preprocessing Tools

#### Method A: Container Build (Recommended)
```bash
cd /data/gpfs/projects/punim2657/sfs_preprocessing
./build_in_container.sh
```
- **Container Used**: `cache/sfs_prep_from_working.sif`
- **Output Location**: `build/`
- **Generated Binaries**:
  - `build/mesh_processing_complete`
  - `build/edgeline_extraction`

#### Method B: Manual Container Build
```bash
APPTAINER="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
$APPTAINER exec --bind $PWD:/workspace --pwd /workspace cache/sfs_prep_from_working.sif /bin/bash -c "cd build && make clean && make -j2"
```

### 1.2 Mesh-to-Surface Processing

#### Run Command
```bash
for piece in {01..08}; do
  /apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer exec \
    cache/sfs_prep_from_working.sif \
    ./build/mesh_processing_complete A $piece
done
```

#### Input/Output
- **Input**: `Dataset/Mesh/Pot_A/Pot_A_Piece_XX_Mesh.obj`
- **Output Locations**:
  - `Temp/Data/Pot_A/Pot_A_Piece_XX_Point.pcd` (point cloud from mesh)
  - `Surfaces/Pot_A_Piece_XX_Surface_0.xyz` (outer TPS surface)
  - `Surfaces/Pot_A_Piece_XX_Surface_1.xyz` (inner TPS surface)
- **Processing Time**: ~60-120 seconds per piece

### 1.3 Axis Extraction (MATLAB PotSAC Algorithm)

#### SLURM Method (Recommended - Parallel)
```bash
./submit_axis_jobs.sh           # Submit all 8 pieces in parallel
squeue -u $USER                 # Monitor job progress
./check_axis_results.sh         # Verify completion and copy results
```

#### Sequential Method (Fallback)
```bash
for piece in {01..08}; do
  ./matlab_axis_wrapper.sh A $piece
done
```

#### Input/Output
- **Input**: TPS surface files (`Surfaces/Pot_A_Piece_XX_Surface_*.xyz`)
- **Output Location**: `TPS_Output/Axes/Pot_A_Piece_XX_Axis.xyz`
- **Format**: Position Direction (6 values per line: `pos_x pos_y pos_z dir_x dir_y dir_z`)
- **Processing Time**: ~30-60 seconds per piece (parallel), ~20 minutes sequential

### 1.4 EdgeLine Extraction (Breakline Generation)

#### SLURM Method (Required - Computationally Intensive)
```bash
sbatch run_edgeline_extraction.sbatch
```

#### Manual Container Method (Testing Only)
```bash
/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer exec \
  --overlay /tmp \
  --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/data/gpfs/projects/punim2657/sfs_preprocessing \
  --pwd /data/gpfs/projects/punim2657/sfs_preprocessing \
  cache/sfs_prep_from_working.sif \
  ./build/edgeline_extraction A 8
```

#### Input/Output
- **Input**: Original mesh files and TPS surfaces
- **Output Locations**:
  - Root directory: `Pot_A_Piece_XX_Breakline_0.pcd`, `Pot_A_Piece_XX_Breakline_1.pcd`
  - Root directory: `Pot_A_Piece_XX_Surface_F.pcd` (fracture surfaces)
- **Processing Time**: ~80-120 seconds per piece (~12-15 minutes total for 8 pieces)
- **Format**: Automatically generates custom PCD with segment headers for SFS compatibility

### 1.5 Dataset Organization

#### Auto-Organization (Recommended)
```bash
./organize_dataset.sh
```

#### Output Structure
```
TPS_Dataset_YYYYMMDD/SfS_pp/
├── Surfaces/
│   ├── Pot_A_Piece_01_Surface_0.xyz
│   ├── Pot_A_Piece_01_Surface_1.xyz  
│   ├── Pot_A_Piece_01_Surface_F.pcd
│   └── ... (26 files total: 16 .xyz + 8 .pcd + 2 duplicates)
├── Breaklines/
│   ├── Pot_A_Piece_01_Breakline_0.pcd
│   ├── Pot_A_Piece_01_Breakline_1.pcd
│   └── ... (16 files total)
├── Axes/
│   ├── Pot_A_Piece_01_Axis.xyz
│   └── ... (8 files total)
└── Mesh/
    ├── Pot_A_Piece_01_Mesh.obj
    └── ... (8 files total)
```

---

## Phase 2: SFS Main Assembly Pipeline

### 2.1 Build SFS Binary

#### Setup Fixed Source Files
```bash
cd /data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker
cp ../sfs_modified_src/class/ranking_system.cpp class/
cp ../sfs_modified_src/main_headless_correct.cpp .
```

#### Fix CMakeLists.txt
```bash
rm -f main.cpp
cp CMakeLists.txt CMakeLists.txt.backup
sed 's/main\.cpp/main_headless_correct.cpp/g' CMakeLists.txt.backup > CMakeLists.txt
```

#### Build in Container
```bash
CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
$CONTAINER_PATH exec --bind /data/gpfs/projects/punim2657/sfs_main:/workspace /data/gpfs/projects/punim2657/sfs_main/sfspreproc.sif /bin/bash -c "cd /workspace/sfspreproc-docker && rm -f Hierarchy-Clear && make clean && cmake . && make -j4"
```

#### Output Location
- **Fixed Binary**: `/data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker/Hierarchy-Clear`

### 2.2 Run SFS Assembly

#### SLURM Method (Recommended)
```bash
cd /data/gpfs/projects/punim2657/sfs_main
sbatch test_clean_tps_relaxed.sbatch
```

#### Manual Container Method
```bash
CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
$CONTAINER_PATH exec \
  --bind /data/gpfs/projects/punim2657/sfs_main:/workspace \
  --bind "/data/gpfs/projects/punim2657/sfs_preprocessing/TPS_Dataset_20250829/SfS_pp:/Dataset/SfS_pp" \
  /data/gpfs/projects/punim2657/sfs_main/sfspreproc.sif \
  /workspace/sfspreproc-docker/Hierarchy-Clear 8
```

#### Input/Output
- **Input**: Clean TPS dataset (bound directly via `--bind`)
- **Output Location**: SLURM output files (`sfs_clean_tps_relaxed_*.out`)
- **Key Output Sections**:
  - Data loading verification
  - Feature matching statistics
  - Pairwise pruning results
  - Graph building progress

---

## File Formats and Specifications

### Surface Files (.xyz)
```
Format: X Y Z Nx Ny Nz (6 columns)
Example: -16.1577 -7.48717 407.001 -0.0836252 -0.302476 -0.949482
Location: Surfaces/Pot_A_Piece_XX_Surface_{0|1}.xyz
```

### Axis Files (.xyz)
```
Format: pos_x pos_y pos_z dir_x dir_y dir_z (6 columns)
Example: -53.701454 -131.813210 60.064485 0.216160 0.330565 0.918695
Location: Axes/Pot_A_Piece_XX_Axis.xyz
```

### Breakline Files (.pcd) - Custom Format (Auto-Generated)
```
Header Format:
# .PCD v0.7 - Point Cloud Data file format
# 5 5496 0                    <-- segments, total_points, info
# 1 1099 0                    <-- segment 1: points 1-1099  
# 1100 2198 0                 <-- segment 2: points 1100-2198
# 2199 3297 0                 <-- segment 3: points 2199-3297
# 3298 4396 0                 <-- segment 4: points 3298-4396
# 4397 5496 0                 <-- segment 5: points 4397-5496
VERSION 0.7
FIELDS x y z normal_x normal_y normal_z curvature
[standard PCD header...]
DATA ascii
[point data with 7 fields per point]
```
**Note**: This format is automatically generated by the `edgeline_extraction` binary using the built-in `savePCDFileWithSegmentHeaders()` function.

---

## Troubleshooting

### Common Build Issues

#### Missing PCL/CGAL Dependencies
```bash
# Must build in container - host system lacks required versions
$CONTAINER_PATH exec --bind $PWD:/workspace --pwd /workspace cache/sfs_prep_from_working.sif /bin/bash
```

#### Segmentation Fault in SFS
- **Cause**: Using old binary without bounds checking fix
- **Solution**: Rebuild with fixed `ranking_system.cpp` from `sfs_modified_src/`

#### Format Errors in Breaklines
- **Cause**: Using old `edgeline_extraction` binary that generates standard PCD format
- **Solution**: Rebuild with current code that includes `savePCDFileWithSegmentHeaders()` function

### Performance Issues

#### EdgeLine Extraction Timeout
- **Problem**: Process takes >10 minutes, interactive sessions timeout
- **Solution**: Always use SLURM: `sbatch run_edgeline_extraction.sbatch`

#### MATLAB Axis Extraction Timeout
- **Problem**: Sequential processing takes ~20 minutes
- **Solution**: Use parallel SLURM: `./submit_axis_jobs.sh`

---

## Key File Locations Summary

### Preprocessing Outputs
- **Surfaces**: `Surfaces/Pot_A_Piece_XX_Surface_{0|1}.xyz`
- **Axes**: `TPS_Output/Axes/Pot_A_Piece_XX_Axis.xyz`
- **Breaklines**: `Pot_A_Piece_XX_Breakline_{0|1}.pcd` (root level)
- **Surface_F**: `Pot_A_Piece_XX_Surface_F.pcd` (root level)

### Organized Dataset
- **Complete Dataset**: `TPS_Dataset_20250829/SfS_pp/`
- **Documentation**: `TPS_Dataset_20250829/SfS_pp/*/README.md`

### SFS Assembly
- **Binary**: `sfspreproc-docker/Hierarchy-Clear`
- **Results**: `sfs_clean_tps_relaxed_*.out`
- **Container**: `sfspreproc.sif`

---

## Processing Time Estimates

| Stage | Method | Per Piece | Total (8 pieces) |
|-------|--------|-----------|------------------|
| Mesh Processing | Container | 60-120s | 8-16 minutes |
| Axis Extraction | SLURM Parallel | 30-60s | 2-4 minutes |
| Axis Extraction | Sequential | 30-60s | 20 minutes |
| EdgeLine Extraction | SLURM | 80-120s | 12-15 minutes |
| Dataset Organization | Script | - | 30 seconds |
| SFS Assembly | SLURM | - | 30-60 seconds |

**Total Pipeline Time**: ~25-35 minutes (with SLURM optimization)