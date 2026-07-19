#!/bin/bash
#SBATCH --job-name=test_p01
#SBATCH --output=test_piece01.log
#SBATCH --error=test_piece01.err
#SBATCH --time=00:30:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
#SBATCH --partition=sapphire

module load Apptainer

CONTAINER="/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif"
BIND="/data/gpfs/projects/punim2657:/data/gpfs/projects/punim2657"
WORK_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"

cd $WORK_DIR

echo "========== Testing Piece 01 with fixed MIN caps =========="
echo "Binary timestamp: $(ls -lh build_new/EdgeLineExtractionHeadless)"
echo ""

apptainer exec --bind $BIND $CONTAINER \
    ./build_new/EdgeLineExtractionHeadless \
    --potID Pot_A \
    --pieceNo Piece_01 \
    --datasetPath Dataset \
    --tempPath Temp

echo ""
echo "========== Results =========="
echo "Breakline 0:"
head -2 Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_0.pcd
echo ""
echo "Breakline 1:"
head -2 Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_1.pcd
