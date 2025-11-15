#!/bin/bash

echo "=== Starting Complete EdgeLineExtraction for ALL Pot A pieces ==="
echo "Start time: $(date)"

# Run EdgeLineExtraction for all 8 pieces
/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer exec \
  --overlay /tmp \
  --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/data/gpfs/projects/punim2657/sfs_preprocessing \
  --pwd /data/gpfs/projects/punim2657/sfs_preprocessing \
  cache/sfs_prep_from_working.sif \
  ./build/edgeline_extraction A 8

echo "End time: $(date)"
echo "=== EdgeLineExtraction Complete ==="

# Check results
echo "Generated files:"
find . -name "*Surface_F*" -o -name "*Breakline*" -name "*Pot_A_Piece_0[4-8]*" | sort