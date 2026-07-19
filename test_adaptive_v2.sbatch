#!/bin/bash
#SBATCH --job-name=adapt_v2
#SBATCH --output=adaptive_v2.log
#SBATCH --error=adaptive_v2.err
#SBATCH --time=00:30:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
#SBATCH --partition=sapphire

module load Apptainer

CONTAINER="/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif"
BIND="/data/gpfs/projects/punim2657:/data/gpfs/projects/punim2657"
WORK_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"

cd $WORK_DIR

echo "=== Rebuilding with 2× avgSpacing formula ==="
cd build_new && apptainer exec --bind $BIND $CONTAINER make EdgeLineExtractionHeadless -j4 && cd ..

echo ""
echo "=== Testing all pieces ==="
for piece in 01 02 03 04 05 06 07 08; do
    echo "--- Piece_${piece} ---"
    apptainer exec --bind $BIND $CONTAINER \
        ./build_new/EdgeLineExtractionHeadless \
        --potID Pot_A --pieceNo Piece_${piece} \
        --datasetPath Dataset --tempPath Temp 2>&1 | grep -E "ADAPTIVE SPHERE-MARCHING|BREAKLINE DEBUG.*Smoothed|Saved PCD"
done

echo ""
echo "=== RESULTS ==="
for i in 01 02 03 04 05 06 07 08; do
    new0=$(/bin/grep "^POINTS" Dataset/Breaklines/Pot_A/Pot_A_Piece_${i}_Breakline_0.pcd | awk '{print $2}')
    new1=$(/bin/grep "^POINTS" Dataset/Breaklines/Pot_A/Pot_A_Piece_${i}_Breakline_1.pcd | awk '{print $2}')
    sam0=$(/bin/grep "^POINTS" /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines/Pot_A_Piece_${i}_Breakline_0.pcd | awk '{print $2}')
    sam1=$(/bin/grep "^POINTS" /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines/Pot_A_Piece_${i}_Breakline_1.pcd | awk '{print $2}')
    echo "P${i}: BL0=${new0}/${sam0} BL1=${new1}/${sam1}"
done
