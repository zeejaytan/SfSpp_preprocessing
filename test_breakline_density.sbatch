#!/bin/bash
#SBATCH --job-name=bl_density
#SBATCH --output=breakline_density_test.log
#SBATCH --error=breakline_density_test.err
#SBATCH --time=00:30:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
#SBATCH --partition=sapphire

module load Apptainer

CONTAINER="/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif"
BIND="/data/gpfs/projects/punim2657:/data/gpfs/projects/punim2657"
WORK_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"

cd $WORK_DIR

echo "========== Rebuilding EdgeLineExtractionHeadless =========="
cd build_new
apptainer exec --bind $BIND $CONTAINER make EdgeLineExtractionHeadless -j4
cd ..

echo ""
echo "========== Testing Piece 01 breakline with 2.3× multiplier =========="

for piece in 01 02; do
    echo ""
    echo "--- Testing Piece_${piece} ---"
    apptainer exec --bind $BIND $CONTAINER \
        ./build_new/EdgeLineExtractionHeadless \
        --potID Pot_A \
        --pieceNo Piece_${piece} \
        --datasetPath Dataset \
        --tempPath Temp
done

echo ""
echo "========== Results =========="
SAMPLE="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
for piece in 01 02; do
    echo "Piece ${piece}:"
    new_bl0=$(/bin/grep "^POINTS" Dataset/Breaklines/Pot_A/Pot_A_Piece_${piece}_Breakline_0.pcd | awk '{print $2}')
    new_bl1=$(/bin/grep "^POINTS" Dataset/Breaklines/Pot_A/Pot_A_Piece_${piece}_Breakline_1.pcd | awk '{print $2}')
    sample_bl0=$(/bin/grep "^POINTS" ${SAMPLE}/Breaklines/Pot_A_Piece_${piece}_Breakline_0.pcd | awk '{print $2}')
    sample_bl1=$(/bin/grep "^POINTS" ${SAMPLE}/Breaklines/Pot_A_Piece_${piece}_Breakline_1.pcd | awk '{print $2}')
    echo "  BL0: New=$new_bl0 vs Sample=$sample_bl0"
    echo "  BL1: New=$new_bl1 vs Sample=$sample_bl1"
done
