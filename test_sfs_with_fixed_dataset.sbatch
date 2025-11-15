#!/bin/bash
#SBATCH --job-name=test_sfs_fixed
#SBATCH --time=02:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=8
#SBATCH --partition=sapphire
#SBATCH --output=test_sfs_fixed_%j.out
#SBATCH --error=test_sfs_fixed_%j.err

echo "=== Testing SFS with Fixed Headless Dataset ==="
echo "Job ID: $SLURM_JOB_ID" 
echo "Start time: $(date)"
echo "Using dataset: NURBS_Dataset_20250906_FixedHeadless"

cd /data/gpfs/projects/punim2657/sfs_main

# Ensure SFS binary is available
if [ -f "build/SFS_headless" ]; then
    echo "✓ Using SFS_headless binary"
    BINARY="./build/SFS_headless"
elif [ -f "sfspreproc-docker/main_headless_correct" ]; then
    echo "✓ Using main_headless_correct binary"
    BINARY="./sfspreproc-docker/main_headless_correct"
else
    echo "⚠ Building SFS binary..."
    cd sfspreproc-docker && make main_headless_correct && cd ..
    BINARY="./sfspreproc-docker/main_headless_correct"
fi

echo "Running SFS reconstruction with fixed headless dataset..."
CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
$CONTAINER_PATH exec \
  --bind /data/gpfs/projects/punim2657/sfs_main:/workspace \
  --bind "/data/gpfs/projects/punim2657/sfs_preprocessing/NURBS_Dataset_20250906_FixedHeadless/SfS_pp:/Dataset/SfS_pp" \
  sfspreproc.sif \
  /workspace/sfspreproc-docker/Hierarchy-Clear 8

echo
echo "SFS test completed at: $(date)"
