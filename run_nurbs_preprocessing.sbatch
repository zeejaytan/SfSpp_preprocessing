#!/bin/bash
#SBATCH --job-name=nurbs_complete_pipeline
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=3:00:00
#SBATCH --output=nurbs_complete_pipeline_%j.out
#SBATCH --error=nurbs_complete_pipeline_%j.err

echo "=== Complete NURBS Preprocessing Pipeline ==="
echo "Started: $(date)"
echo "Job ID: ${SLURM_JOB_ID}"

cd /data/gpfs/projects/punim2657/sfs_preprocessing

# Clean previous outputs
echo "Cleaning previous NURBS outputs..."
rm -f original_nurbs_preprocessing/Temp/Data/Pot_A/*.xyz
rm -f original_nurbs_preprocessing/Surfaces/*.xyz
rm -f original_nurbs_preprocessing/build/Pot_A_Piece_*_Breakline_*.pcd
rm -f original_nurbs_preprocessing/build/Pot_A_Piece_*_Surface_F.pcd
rm -f TPS_Output/Axes/Pot_A_Piece_*_Axis.xyz

# Step 1: NURBS Mesh Preprocessing
echo "=== Step 1: NURBS Surface Generation ==="
echo "Running NURBS MeshPreprocessingHeadless..."
CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
$CONTAINER_PATH exec --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/workspace \
    pcl_191_nurbs.sif /bin/bash -c \
    "cd /workspace/original_nurbs_preprocessing/build && ./MeshPreprocessingHeadless"

echo "Mesh preprocessing completed at: $(date)"

# Verify surface files
echo "Surface files generated:"
ls -la original_nurbs_preprocessing/Temp/Data/Pot_A/*.xyz 2>/dev/null || echo "No XYZ files found"

# Step 2: Edge Line Extraction  
echo "=== Step 2: NURBS Edge Line Extraction ==="
echo "Running NURBS EdgeLineExtractionHeadless..."
$CONTAINER_PATH exec --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/workspace \
    pcl_191_nurbs.sif /bin/bash -c \
    "cd /workspace/original_nurbs_preprocessing/build && ./EdgeLineExtractionHeadless"

echo "Edge line extraction completed at: $(date)"

# Verify breakline files
echo "Breakline files generated:"
ls -la original_nurbs_preprocessing/build/Pot_A_Piece_*_Breakline_*.pcd 2>/dev/null || echo "No breakline files found"

# Step 3: Axis Extraction using MATLAB PotSAC
echo "=== Step 3: MATLAB PotSAC Axis Extraction ==="
echo "Loading MATLAB module..."
module load MATLAB/2024b_Update_3

echo "Creating TPS_Output/Axes directory..."
mkdir -p TPS_Output/Axes

echo "Running MATLAB axis extraction..."
matlab -batch "
addpath('.');
for piece = 1:8
    piece_str = sprintf('%02d', piece);
    surface_file = sprintf('original_nurbs_preprocessing/Temp/Data/Pot_A/Pot_A_Piece_%s_Surface_0.xyz', piece_str);
    output_file = sprintf('TPS_Output/Axes/Pot_A_Piece_%s_Axis.xyz', piece_str);
    
    fprintf('Processing piece %s...\n', piece_str);
    if exist(surface_file, 'file')
        try
            extract_single_axis('A', piece, surface_file, output_file);
            fprintf('Piece %s axis extraction completed\n', piece_str);
        catch ME
            fprintf('Error processing piece %s: %s\n', piece_str, ME.message);
        end
    else
        fprintf('Surface file not found: %s\n', surface_file);
    end
end
fprintf('All axis extractions completed\n');
quit;
"

echo "Axis extraction completed at: $(date)"

# Step 4: Organize NURBS Dataset
echo "=== Step 4: Dataset Organization ==="
echo "Creating NURBS dataset structure..."
NURBS_DATASET_DIR="NURBS_Dataset_$(date +%Y%m%d)"
mkdir -p "${NURBS_DATASET_DIR}/SfS_pp/"{Surfaces,Breaklines,Axes,Mesh}

# Copy surfaces
echo "Copying surface files..."
cp original_nurbs_preprocessing/Temp/Data/Pot_A/Pot_A_Piece_*_Surface_*.xyz "${NURBS_DATASET_DIR}/SfS_pp/Surfaces/" 2>/dev/null || echo "No surface files to copy"

# Copy breaklines
echo "Copying breakline files..."
cp original_nurbs_preprocessing/Dataset/Breaklines/Pot_A/Pot_A_Piece_*_Breakline_*.pcd "${NURBS_DATASET_DIR}/SfS_pp/Breaklines/" 2>/dev/null || echo "No breakline files to copy"

# Copy axes
echo "Copying axis files..."
cp original_nurbs_preprocessing/AxisExtraction/Pot_A_Piece_*_NURBS_Axis.xyz "${NURBS_DATASET_DIR}/SfS_pp/Axes/" 2>/dev/null || echo "No axis files to copy"

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

echo "=== Complete NURBS Pipeline Finished at: $(date) ==="