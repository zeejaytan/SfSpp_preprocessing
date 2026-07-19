#!/bin/bash
#SBATCH --job-name=edge_all
#SBATCH --output=edge_all_pieces.log
#SBATCH --error=edge_all_pieces.err
#SBATCH --time=02:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --partition=sapphire

module load Apptainer

CONTAINER="/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif"
BIND="/data/gpfs/projects/punim2657:/data/gpfs/projects/punim2657"
WORK_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"

cd $WORK_DIR

for piece in 01 02 03 04 05 06 07 08; do
    echo "========== Processing Piece ${piece} =========="

    apptainer exec --bind $BIND $CONTAINER \
        ./build_new/EdgeLineExtractionHeadless \
        --potID Pot_A \
        --pieceNo "Piece_${piece}" \
        --datasetPath Dataset \
        --tempPath Temp

    echo "Completed Piece ${piece}"
    echo ""
done

echo "========== All pieces completed =========="
