#!/bin/bash
#SBATCH --job-name=nurbs_param_fix
#SBATCH --output=nurbs_param_fix_%j.out
#SBATCH --error=nurbs_param_fix_%j.err
#SBATCH --time=02:00:00
#SBATCH --partition=cascade
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G

echo "=== NURBS Parameter Fix Test ==="
echo "Testing RadiusSearch=3 consistency fix"
echo "Job ID: $SLURM_JOB_ID"
echo "Start time: $(date)"

cd /data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing

# Create output directory
DATASET_NAME="NURBS_Dataset_20250909_ParameterFix"
mkdir -p "../$DATASET_NAME/SfS_pp/"{Breaklines,Surfaces,Axes}

echo "Creating dataset: $DATASET_NAME"

# Set container path
CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"

echo "Running EdgeLine extraction with fixed RadiusSearch=3 parameter..."

# Run EdgeLine extraction with fixed parameters
$CONTAINER_PATH exec \
    --bind /data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing:/workspace \
    --pwd /workspace \
    /data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif \
    ./build/EdgeLineExtractionHeadless A 8

# Move results to organized dataset
echo "Moving results to dataset directory..."
mv Pot_A_Piece_*_Breakline_*.pcd "../$DATASET_NAME/SfS_pp/Breaklines/" 2>/dev/null || echo "No breakline files to move"
mv Pot_A_Piece_*_Surface_F.xyz "../$DATASET_NAME/SfS_pp/Surfaces/" 2>/dev/null || echo "No Surface_F files to move"

echo "Parameter fix test completed at $(date)"
echo "Results in: $DATASET_NAME"