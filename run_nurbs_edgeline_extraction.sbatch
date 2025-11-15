#!/bin/bash
#SBATCH --job-name=nurbs_edgeline
#SBATCH --time=00:30:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=2
#SBATCH --partition=sapphire
#SBATCH --output=nurbs_edgeline_%j.out
#SBATCH --error=nurbs_edgeline_%j.err

echo "=== EdgeLine Extraction for YOUR Generated NURBS Dataset ==="
echo "Job ID: $SLURM_JOB_ID"
echo "Start time: $(date)"
echo "Processing NURBS Dataset: NURBS_Dataset_20250903"
echo

cd /data/gpfs/projects/punim2657/sfs_preprocessing

# Copy your NURBS surface files to the expected location for processing
echo "Copying your NURBS surface files to processing location..."
cp NURBS_Dataset_20250903/SfS_pp/Surfaces/Pot_A_Piece_*_Surface_*.xyz Temp/Data/Pot_A/

echo "Verifying NURBS surface files are in place:"
ls -la Temp/Data/Pot_A/*Surface*.xyz | head -4

echo "Running EdgeLine extraction on your NURBS surfaces..."
/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer exec \
    --overlay /tmp \
    --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/data/gpfs/projects/punim2657/sfs_preprocessing \
    --pwd /data/gpfs/projects/punim2657/sfs_preprocessing \
    cache/sfs_prep_from_working.sif \
    ./build/EdgeLineExtraction A 8

echo
echo "EdgeLine extraction completed at: $(date)"

# Check for newly generated files
echo "=== Newly Generated NURBS Breakline Files ==="
find . -name "*Breakline*.pcd" -newer run_nurbs_edgeline_extraction.sbatch -exec echo "NURBS Breakline: {}" \;
find . -name "*Surface_F.pcd" -newer run_nurbs_edgeline_extraction.sbatch -exec echo "NURBS Surface_F: {}" \;

echo "=== Job Finished ==="