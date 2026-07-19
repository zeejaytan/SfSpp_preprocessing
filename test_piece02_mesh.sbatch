#!/bin/bash
#SBATCH --job-name=mesh_p02
#SBATCH --output=test_piece02_mesh.log
#SBATCH --error=test_piece02_mesh.err
#SBATCH --time=00:30:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
#SBATCH --partition=sapphire

module load Apptainer

CONTAINER="/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif"
BIND="/data/gpfs/projects/punim2657:/data/gpfs/projects/punim2657"
WORK_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"

cd $WORK_DIR

echo "========== Testing Piece 02 Mesh Processing =========="
echo "Binary timestamp: $(ls -lh build_new/MeshPreprocessingHeadless)"
echo "Source timestamp: $(ls -lh mesh_processing_headless.cpp)"
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
