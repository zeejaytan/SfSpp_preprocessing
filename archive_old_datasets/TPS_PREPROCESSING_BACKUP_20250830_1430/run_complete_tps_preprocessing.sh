#!/bin/bash
# Complete TPS Preprocessing Pipeline with Auto-Organization
# Runs full TPS preprocessing and automatically organizes outputs

set -e

echo "=== Complete TPS Preprocessing Pipeline ==="
echo "Start time: $(date)"
echo

# Step 1: Mesh-to-Point Conversion
echo "Step 1/5: Mesh-to-Point Conversion"
# [Add your existing mesh-to-point conversion commands here]

# Step 2: TPS Surface Generation
echo "Step 2/5: TPS Surface Generation" 
# [Add your existing TPS surface fitting commands here]

# Step 3: Surface_F Generation
echo "Step 3/5: Surface_F Generation"
# [Add your existing Surface_F generation commands here]

# Step 4: Breakline Generation (SLURM EdgeLine Extraction)
echo "Step 4/6: Breakline Generation"
echo "Submitting SLURM edgeline extraction job..."
echo "This will take ~12-15 minutes for 8 pieces..."
EDGE_JOB=$(sbatch --parsable run_edgeline_extraction.sbatch)
echo "EdgeLine extraction job submitted: $EDGE_JOB"

# Step 5: Axis Extraction (SLURM)
echo "Step 5/6: Axis Extraction" 
echo "Submitting SLURM parallel axis extraction jobs..."
# [Add your existing SLURM axis extraction commands here]

# Step 6: Auto-organize outputs
echo "Step 6/6: Auto-organizing dataset..."
./organize_dataset.sh

echo
echo "=== TPS Preprocessing Complete ==="
echo "End time: $(date)"
echo "Dataset location: $(readlink latest_tps_dataset)"
echo "Ready for SFS integration (except missing breaklines)"