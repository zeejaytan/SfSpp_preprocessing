#!/bin/bash
#SBATCH --job-name=rebuild_p02
#SBATCH --output=rebuild_piece02.log
#SBATCH --error=rebuild_piece02.err
#SBATCH --time=00:30:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
#SBATCH --partition=sapphire

module load Apptainer

CONTAINER="/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif"
BIND="/data/gpfs/projects/punim2657:/data/gpfs/projects/punim2657"
WORK_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"

cd $WORK_DIR

echo "========== Rebuilding MeshPreprocessingHeadless =========="
cd build_new
apptainer exec --bind $BIND $CONTAINER cmake ..
apptainer exec --bind $BIND $CONTAINER make MeshPreprocessingHeadless -j4
cd ..

echo ""
echo "========== Testing Piece 02 with conservative adaptive parameters =========="
echo "New binary timestamp: $(ls -lh build_new/MeshPreprocessingHeadless)"
echo ""

apptainer exec --bind $BIND $CONTAINER \
    ./build_new/MeshPreprocessingHeadless \
    Dataset/Point/Pot_A/Pot_A_Piece_02_Point.pcd \
    Dataset/Mesh/Pot_A/Pot_A_Piece_02_Mesh.obj \
    Pot_A

echo ""
echo "========== Results =========="
echo "Surface 0:"
wc -l Temp/Data/Pot_A/Pot_A_Piece_02_Surface_0.xyz
echo ""
echo "Surface 1:"
wc -l Temp/Data/Pot_A/Pot_A_Piece_02_Surface_1.xyz
echo ""
echo "Sample comparison:"
echo "Sample S0: $(wc -l < /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Surfaces/Pot_A_Piece_02_Surface_0.xyz)"
echo "Sample S1: $(wc -l < /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Surfaces/Pot_A_Piece_02_Surface_1.xyz)"
