#!/bin/bash
#SBATCH --job-name=fixed_nurbs_pipeline
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=2:00:00
#SBATCH --output=fixed_nurbs_pipeline_%j.out
#SBATCH --error=fixed_nurbs_pipeline_%j.err

echo "=== Fixed NURBS Preprocessing Pipeline ==="
echo "Started: $(date)"
echo "Job ID: ${SLURM_JOB_ID}"

cd /data/gpfs/projects/punim2657/sfs_preprocessing

# Clean previous outputs
echo "Cleaning previous NURBS outputs..."
rm -rf original_nurbs_preprocessing/Temp/Data/Pot_A/*
mkdir -p original_nurbs_preprocessing/Temp/Data/Pot_A

# Step 1: Generate PCD files with normals using CloudCompare
echo "=== Step 1: Generating Point Clouds with Normals ==="
module load CloudCompare/2.12.4

for piece in {01..08}; do
    mesh_file="Dataset/Mesh/Pot_A/Pot_A_Piece_${piece}_Mesh.obj"
    output_file="original_nurbs_preprocessing/build/Pot_A_Piece_${piece}_Point.pcd"
    
    if [ -f "$mesh_file" ]; then
        echo "Processing piece ${piece}..."
        CloudCompare -SILENT -O "$mesh_file" \
            -SAMPLE_MESH POINTS 50000 \
            -COMPUTE_NORMALS \
            -C_EXPORT_FMT PCD -SAVE_CLOUDS FILE "$output_file"
        
        if [ -f "$output_file" ]; then
            echo "Generated: $output_file ($(wc -l < $output_file) lines)"
            # Copy to temp directory for NURBS processing
            cp "$output_file" "original_nurbs_preprocessing/Temp/Data/Pot_A/"
        else
            echo "ERROR: Failed to generate $output_file"
        fi
    else
        echo "WARNING: Mesh file not found: $mesh_file"
    fi
done

echo "Point cloud generation completed at: $(date)"

# Step 2: Run NURBS Mesh Preprocessing
echo "=== Step 2: NURBS Surface Generation ==="
CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"

echo "Running NURBS MeshPreprocessingHeadless with proper setup..."
$CONTAINER_PATH exec \
    --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/workspace \
    --bind /tmp:/tmp \
    pcl_191_nurbs.sif bash -c "
    cd /workspace/original_nurbs_preprocessing/build
    mkdir -p ../Temp/Data/Pot_A
    ./MeshPreprocessingHeadless
"

echo "NURBS surface generation completed at: $(date)"

# Verify surface files
echo "Surface files generated:"
ls -la original_nurbs_preprocessing/Temp/Data/Pot_A/*.xyz 2>/dev/null || echo "No XYZ surface files found"

# Step 3: Edge Line Extraction  
echo "=== Step 3: NURBS Edge Line Extraction ==="
$CONTAINER_PATH exec \
    --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/workspace \
    --bind /tmp:/tmp \
    pcl_191_nurbs.sif bash -c "
    cd /workspace/original_nurbs_preprocessing/build
    ./EdgeLineExtractionHeadless
"

echo "Edge line extraction completed at: $(date)"

# Verify breakline files
echo "Breakline files generated:"
ls -la original_nurbs_preprocessing/build/Pot_A_Piece_*_Breakline_*.pcd 2>/dev/null || echo "No breakline files found"

# Step 4: Create organized NURBS dataset
echo "=== Step 4: Dataset Organization ==="
NURBS_DATASET_DIR="NURBS_Dataset_$(date +%Y%m%d)"
mkdir -p "${NURBS_DATASET_DIR}/SfS_pp/"{Surfaces,Breaklines,Axes,Mesh,Point}

# Copy surfaces
echo "Copying surface files..."
cp original_nurbs_preprocessing/Temp/Data/Pot_A/Pot_A_Piece_*_Surface_*.xyz "${NURBS_DATASET_DIR}/SfS_pp/Surfaces/" 2>/dev/null || echo "No surface files to copy"

# Copy breaklines  
echo "Copying breakline files..."
cp original_nurbs_preprocessing/build/Pot_A_Piece_*_Breakline_*.pcd "${NURBS_DATASET_DIR}/SfS_pp/Breaklines/" 2>/dev/null || echo "No breakline files to copy"

# Copy point clouds with normals
echo "Copying point cloud files..."
cp original_nurbs_preprocessing/build/Pot_A_Piece_*_Point.pcd "${NURBS_DATASET_DIR}/SfS_pp/Point/Pot_A/" 2>/dev/null || echo "No point files to copy"

# Copy meshes
echo "Copying mesh files..."
cp Dataset/Mesh/Pot_A/Pot_A_Piece_*_Mesh.obj "${NURBS_DATASET_DIR}/SfS_pp/Mesh/" 2>/dev/null || echo "No mesh files to copy"

# Create symlink to latest dataset
rm -f latest_nurbs_dataset
ln -s "${NURBS_DATASET_DIR}" latest_nurbs_dataset

echo "=== Final Output Verification ==="
echo "NURBS Dataset created: ${NURBS_DATASET_DIR}"
echo "Dataset contents:"
find "${NURBS_DATASET_DIR}" -type f | sort

echo "Surface file samples:"
for file in "${NURBS_DATASET_DIR}/SfS_pp/Surfaces/Pot_A_Piece_01_Surface_"*.xyz; do
    if [ -f "$file" ]; then
        echo "File: $(basename $file)"
        echo "Size: $(wc -l < $file) points"
        echo "Sample:"
        head -3 "$file"
        echo ""
    fi
done

echo "=== Fixed NURBS Pipeline Completed at: $(date) ==="