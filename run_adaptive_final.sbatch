#!/bin/bash
#SBATCH --job-name=adaptive_final
#SBATCH --time=00:15:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G

# Run edgeline extraction with adaptive sensitivity + all bug fixes
# This should match the sample dataset parameters

cd /data/gpfs/projects/punim2657/sfs_preprocessing

# Load modules
module load GCCcore/11.3.3
module load Apptainer/1.3.3

echo "=== Running Edgeline Extraction with Adaptive Sensitivity ==="
echo "Started: $(date)"

# Clean previous breakline output
rm -rf Dataset/Breaklines/Pot_A/*

apptainer exec --bind /data:/data pcl_191_nurbs.sif \
  ./build_new/EdgeLineExtractionHeadless

echo "Completed: $(date)"

# Summary
echo ""
echo "=== Output Summary ==="
echo "Breaklines (PCD): $(find Dataset/Breaklines/Pot_A -name "*.pcd" 2>/dev/null | wc -l) files"
echo ""
echo "Adaptive sensitivity usage:"
grep "ADAPTIVE PEAK" slurm-${SLURM_JOB_ID}.out | head -20
