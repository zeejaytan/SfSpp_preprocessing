# NURBS Preprocessing Build and Usage Guide

## Overview
This guide documents how to build and run the NURBS preprocessing executables that replace the problematic TPS preprocessing approach. The NURBS method generates significantly fewer feature matches (124 vs 4492 with TPS), preventing optimization system overload.

## System Requirements

### Container Environment
- **Apptainer/Singularity** (version 1.3.3 or later)
- **RHEL 9.4 or compatible Linux** system
- **Minimum 8GB RAM** for building
- **Minimum 2GB disk space** for container and build files

### Host System Dependencies
```bash
# Required system tools
/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
```

## Build Process

### 1. PCL 1.9.1 Container with NURBS Support

The NURBS preprocessing requires PCL 1.9.1 with NURBS support enabled, which is not available in standard PCL distributions.

#### Container Definition
- **File**: `pcl_191_nurbs.def`
- **Base**: AlmaLinux 9 (GLIBC 2.34 compatible with RHEL 9.4)
- **Key Features**: 
  - PCL 1.9.1 with `BUILD_surface_on_nurbs=ON`
  - CGAL for mesh processing (replaces VTK)
  - Headless build (no graphics dependencies)

#### Build Container
```bash
cd /data/gpfs/projects/punim2657/sfs_preprocessing

# Submit SLURM job to build container (takes ~45 minutes)
sbatch build_pcl191_container.sbatch

# Check job status
squeue -u $USER

# Verify container creation
ls -la pcl_191_nurbs.sif
# Expected: ~305MB container file
```

#### Verify NURBS Headers
```bash
CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"

# Check critical NURBS headers are available
$CONTAINER_PATH exec pcl_191_nurbs.sif find /usr/local/include -name "fitting_surface_tdm.h"
# Expected: /usr/local/include/pcl-1.9/pcl/surface/on_nurbs/fitting_surface_tdm.h

# Check all NURBS functionality
$CONTAINER_PATH exec pcl_191_nurbs.sif find /usr/local/include -name "*nurbs*" | wc -l
# Expected: 90+ header files
```

### 2. NURBS Preprocessing Executables

#### Source Files Location
```
/data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing/
├── mesh_processing_headless.cpp      # Mesh preprocessing (headless)
├── edgeline_extraction_headless.cpp  # Edge line extraction (headless)  
├── CMakeLists.txt                     # Build configuration
├── alglib/                            # Mathematical algorithms library
└── tiny_obj_loader.h                  # OBJ file format support
```

#### Build Command
```bash
cd /data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing

# Build both executables using PCL 1.9.1 container
CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
$CONTAINER_PATH exec --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/workspace \
    ../pcl_191_nurbs.sif /bin/bash -c \
    "cd /workspace/original_nurbs_preprocessing && \
     mkdir -p build && cd build && \
     cmake .. -DCMAKE_BUILD_TYPE=Release -DCGAL_DIR=/usr/share/cmake/CGAL && \
     make -j4 MeshPreprocessingHeadless EdgeLineExtractionHeadless"
```

#### Build Verification
```bash
# Check executables were created
ls -la original_nurbs_preprocessing/build/*Headless
# Expected output:
# -rwxrwxr-x 1 user group 5270512 Aug 30 21:49 EdgeLineExtractionHeadless
# -rwxrwxr-x 1 user group 1363880 Aug 30 21:34 MeshPreprocessingHeadless

# Test executables run
CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
$CONTAINER_PATH exec --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/workspace \
    pcl_191_nurbs.sif /bin/bash -c \
    "cd /workspace/original_nurbs_preprocessing/build && ./EdgeLineExtractionHeadless"
# Expected: "Processing directory: ../Temp/" + timing info
```

## Usage

### Complete NURBS Pipeline (RECOMMENDED)

#### SLURM-Based Complete Pipeline
The complete NURBS preprocessing pipeline is available as a single SLURM job that handles all steps automatically.

**Script**: `run_nurbs_preprocessing.sbatch`

#### Usage
```bash
cd /data/gpfs/projects/punim2657/sfs_preprocessing

# Submit complete NURBS pipeline
sbatch run_nurbs_preprocessing.sbatch

# Monitor job progress
squeue -u $USER

# Check job output
tail -f nurbs_complete_pipeline_JOBID.out
```

#### Pipeline Steps
The complete pipeline executes the following steps automatically:

1. **Step 1: NURBS Surface Generation**
   - Runs `MeshPreprocessingHeadless` using CloudCompare PCD files
   - Generates NURBS-fitted surface files with proper XYZ headers
   
2. **Step 2: NURBS Edge Line Extraction**  
   - Runs `EdgeLineExtractionHeadless` on generated surfaces
   - Creates breakline PCD files for fracture edge detection
   
3. **Step 3: MATLAB PotSAC Axis Extraction**
   - Sequential axis extraction for all 8 pottery pieces
   - Generates axis files compatible with SFS system
   
4. **Step 4: Dataset Organization**
   - Creates organized `NURBS_Dataset_YYYYMMDD` structure
   - Copies all generated files to proper SFS dataset format
   - Creates `latest_nurbs_dataset` symlink

#### Expected Pipeline Output
```
NURBS_Dataset_20250901/SfS_pp/
├── Surfaces/
│   ├── Pot_A_Piece_01_Surface_0.xyz    # NURBS outer surface
│   ├── Pot_A_Piece_01_Surface_1.xyz    # NURBS inner surface
│   └── ... (all 8 pieces)
├── Breaklines/
│   ├── Pot_A_Piece_01_Breakline_0.pcd  # NURBS edge features
│   ├── Pot_A_Piece_01_Breakline_1.pcd
│   └── ... (all 8 pieces)
├── Axes/
│   ├── Pot_A_Piece_01_Axis.xyz         # PotSAC axis extraction
│   └── ... (all 8 pieces)
└── Mesh/
    ├── Pot_A_Piece_01_Mesh.obj         # Original mesh files
    └── ... (all 8 pieces)
```

#### SLURM Configuration
- **Job time**: 3 hours (sufficient for complete pipeline)
- **Memory**: 16GB (handles NURBS fitting and MATLAB)  
- **CPU**: 4 cores (parallel processing where possible)
- **Partition**: sapphire (computational requirements)

#### Prerequisites
Before running the complete pipeline:

1. **CloudCompare PCD Files Required**:
   ```bash
   # Verify CloudCompare files exist
   ls -la cloudcompare_piece*_sampled.pcd
   
   # Files should be copied to Dataset/Point/Pot_A/ automatically
   ls -la Dataset/Point/Pot_A/Pot_A_Piece_*_Point.pcd
   ```

2. **Mesh Files Required**:
   ```bash
   # Verify mesh files exist  
   ls -la Dataset/Mesh/Pot_A/Pot_A_Piece_*_Mesh.obj
   ```

3. **MATLAB Functions Available**:
   ```bash
   # Verify axis extraction function exists
   ls -la extract_single_axis.m
   ```

### Individual Component Usage (Advanced)

#### 1. MeshPreprocessingHeadless

#### Purpose
Converts CloudCompare-sampled pottery fragment point clouds into NURBS surface representations.

#### Input Requirements
- **Point clouds**: CloudCompare-generated PCD files with proper sampling
- **Mesh files**: OBJ format pottery fragment meshes  
- **Location**: `Dataset/Point/Pot_A/Pot_A_Piece_XX_Point.pcd` (CloudCompare output)
- **Location**: `Dataset/Mesh/Pot_A/Pot_A_Piece_XX_Mesh.obj`

#### Manual Usage
```bash
cd /data/gpfs/projects/punim2657/sfs_preprocessing

# Run mesh preprocessing on Pot A pieces
CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
$CONTAINER_PATH exec --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/workspace \
    pcl_191_nurbs.sif /bin/bash -c \
    "cd /workspace/original_nurbs_preprocessing/build && \
     ./MeshPreprocessingHeadless"
```

#### Expected Output
- **Surface files**: `original_nurbs_preprocessing/Temp/Data/Pot_A/Pot_A_Piece_XX_Surface_0.xyz`
- **Surface files**: `original_nurbs_preprocessing/Temp/Data/Pot_A/Pot_A_Piece_XX_Surface_1.xyz`
- **Processing logs**: Real-time NURBS fitting progress with proper XYZ headers

#### 2. EdgeLineExtractionHeadless

#### Purpose
Extracts edge lines and surface features from NURBS-fitted surfaces using the original NURBS-based algorithms.

#### Input Requirements  
- **Surface files**: XYZ format with normals from mesh preprocessing
- **Point clouds**: PCD format point clouds (CloudCompare generated)
- **Configuration**: Pot ID and piece numbers hardcoded for Pot A

#### Manual Usage
```bash
cd /data/gpfs/projects/punim2657/sfs_preprocessing

# Run edge line extraction
CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
$CONTAINER_PATH exec --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/workspace \
    pcl_191_nurbs.sif /bin/bash -c \
    "cd /workspace/original_nurbs_preprocessing/build && \
     ./EdgeLineExtractionHeadless"
```

#### Expected Output
- **Breaklines**: `original_nurbs_preprocessing/build/Pot_A_Piece_XX_Breakline_0.pcd`
- **Breaklines**: `original_nurbs_preprocessing/build/Pot_A_Piece_XX_Breakline_1.pcd`  
- **Surface features**: `original_nurbs_preprocessing/build/Pot_A_Piece_XX_Surface_F.pcd`
- **Timing logs**: Processing time per fragment (~90 seconds per piece)

#### 3. MATLAB PotSAC Axis Extraction

#### Purpose
Extracts pottery axis information from NURBS surface files using PotSAC algorithm.

#### Input Requirements
- **Surface files**: NURBS-generated XYZ files with normals
- **MATLAB function**: `extract_single_axis.m` (available in repository)
- **Module**: MATLAB/2024b_Update_3

#### Manual Usage
```bash
cd /data/gpfs/projects/punim2657/sfs_preprocessing

# Load MATLAB module
module load MATLAB/2024b_Update_3

# Run axis extraction for all pieces
mkdir -p TPS_Output/Axes
matlab -batch "
for piece = 1:8
    piece_str = sprintf('%02d', piece);
    surface_file = sprintf('original_nurbs_preprocessing/Temp/Data/Pot_A/Pot_A_Piece_%s_Surface_0.xyz', piece_str);
    output_file = sprintf('TPS_Output/Axes/Pot_A_Piece_%s_Axis.xyz', piece_str);
    extract_single_axis('A', piece, surface_file, output_file);
end
"
```

#### Expected Output
- **Axis files**: `TPS_Output/Axes/Pot_A_Piece_XX_Axis.xyz`
- **Format**: Position Direction (6 values per line: X Y Z Dx Dy Dz)
- **Processing time**: ~2-3 minutes per piece (sequential execution)

### 3. Integration with Main SFS System

#### Dataset Structure
The NURBS preprocessing generates files compatible with the main SFS reconstruction system:

```
SfS_pp/
├── Mesh/
│   └── Pot_A_Piece_XX_Mesh.obj
├── Surfaces/
│   ├── Pot_A_Piece_XX_Surface_0.xyz    # NURBS outer surface
│   └── Pot_A_Piece_XX_Surface_1.xyz    # NURBS inner surface
├── Breaklines/
│   ├── Pot_A_Piece_XX_Breakline_0.pcd  # NURBS edge features
│   └── Pot_A_Piece_XX_Breakline_1.pcd
└── Axes/
    └── Pot_A_Piece_XX_Axis.xyz         # From MATLAB PotSAC
```

#### Running Main SFS System
```bash
cd /data/gpfs/projects/punim2657/sfs_main

# Use NURBS dataset instead of TPS dataset
CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
$CONTAINER_PATH exec \
    --bind "/path/to/nurbs/dataset:/Dataset/SfS_pp" \
    sfspreproc.sif /workspace/sfspreproc-docker/Hierarchy-Clear 8
```

## Key Advantages of NURBS vs TPS

### Feature Match Comparison
- **NURBS preprocessing**: ~124 feature matches per fragment pair
- **TPS preprocessing**: ~4492 feature matches per fragment pair  
- **Result**: 36x fewer matches = No optimization system overload

### Mathematical Accuracy
- **NURBS**: Industry-standard spline representation
- **Surface continuity**: C² continuity guaranteed
- **Geometric precision**: Exact representation of smooth surfaces

### Computational Efficiency  
- **Memory usage**: 36x less feature data to process
- **Processing time**: Faster optimization convergence
- **System stability**: No memory exhaustion from excessive matches

## Troubleshooting

### Container Build Issues
```bash
# Check GLIBC compatibility
ldd --version
# Must be 2.34 or compatible with AlmaLinux 9

# Check container permissions
ls -la pcl_191_nurbs.sif
# Must be executable (x flag)

# Rebuild container if needed
rm pcl_191_nurbs.sif
sbatch build_pcl191_container.sbatch
```

### Compilation Errors
```bash
# Missing tiny_obj_loader.h
cp ../tiny_obj_loader.h .

# CGAL header path issues  
grep -n "CGAL/IO/" mesh_processing_headless.cpp
# Verify paths match: CGAL/IO/OFF/generic_copy_OFF.h, CGAL/IO/OBJ.h
```

### Runtime Issues
```bash
# Check container binding
$CONTAINER_PATH exec --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/workspace \
    pcl_191_nurbs.sif /bin/bash -c "ls -la /workspace"

# Verify input data exists
ls -la Dataset/Mesh/Pot_A/
# Should contain Pot_A_Piece_XX_Mesh.obj files
```

## Performance Expectations

### Container Build Time
- **PCL 1.9.1 compilation**: ~45 minutes (SLURM recommended)
- **NURBS executable build**: ~5 minutes
- **Container size**: ~305MB

### Processing Times
- **MeshPreprocessingHeadless**: ~2-3 minutes per fragment  
- **EdgeLineExtractionHeadless**: ~90 seconds per fragment
- **Total per fragment**: ~5 minutes (vs hours with TPS issues)

## Maintenance

### Container Updates
The PCL 1.9.1 container with NURBS support is stable and should not require frequent updates. Rebuild only if:
- Host system GLIBC version changes
- PCL NURBS algorithms need modification
- Additional mathematical libraries required

### Source Code Location
- **Primary**: `/data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing/`
- **Container definition**: `/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.def`
- **Build scripts**: `/data/gpfs/projects/punim2657/sfs_preprocessing/build_pcl191_container.sbatch`

This completes the NURBS preprocessing restoration, providing the "only option" to resolve the Structure-from-Sherds optimization issues caused by TPS preprocessing.