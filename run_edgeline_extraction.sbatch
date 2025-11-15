#!/bin/bash
#SBATCH --job-name=edgeline_extraction
#SBATCH --time=00:30:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=2
#SBATCH --partition=sapphire
#SBATCH --output=edgeline_extraction_%j.out
#SBATCH --error=edgeline_extraction_%j.err

echo "=== EdgeLine Extraction for TPS Breaklines ==="
echo "Job ID: $SLURM_JOB_ID"
echo "Start time: $(date)"
echo

cd /data/gpfs/projects/punim2657/sfs_preprocessing

echo "Running edgeline extraction for Pot A (8 pieces)..."
/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer exec \
    --overlay /tmp \
    --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/data/gpfs/projects/punim2657/sfs_preprocessing \
    --pwd /data/gpfs/projects/punim2657/sfs_preprocessing \
    cache/sfs_prep_from_working.sif \
    ./build/edgeline_extraction A 8

echo
echo "EdgeLine extraction completed at: $(date)"

# Check for generated files
echo "=== Generated Files ==="
find . -name "*Breakline*.pcd" -exec echo "Breakline: {}" \;
find . -name "*Surface_F.pcd" -exec echo "Surface_F: {}" \;

echo "=== Job Finished ==="