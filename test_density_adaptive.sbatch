#!/bin/bash
#SBATCH --job-name=density_adapt
#SBATCH --output=density_adaptive.log
#SBATCH --error=density_adaptive.err
#SBATCH --time=01:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --partition=sapphire

module load Apptainer

CONTAINER="/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif"
BIND="/data/gpfs/projects/punim2657:/data/gpfs/projects/punim2657"
WORK_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"

cd $WORK_DIR

echo "=== Rebuilding mesh preprocessing with density-based adaptive ==="
cd build_new
apptainer exec --bind $BIND $CONTAINER make MeshPreprocessingHeadless -j4
cd ..

echo ""
echo "=== Testing P01 mesh preprocessing ==="
apptainer exec --bind $BIND $CONTAINER \
    ./build_new/MeshPreprocessingHeadless \
    --potID Pot_A --pieceNo Piece_01 \
    --datasetPath Dataset --tempPath Temp 2>&1 | tee mesh_p01.log

echo ""
echo "=== Checking P01 cluster count ==="
ls Temp/Data/Pot_A/Pot_A_Piece_01_unclustered.plyCluster_*.pcd 2>/dev/null | wc -l

echo ""
echo "=== Running edge extraction on P01 ==="
apptainer exec --bind $BIND $CONTAINER \
    ./build_new/EdgeLineExtractionHeadless \
    --potID Pot_A --pieceNo Piece_01 \
    --datasetPath Dataset --tempPath Temp 2>&1 | grep -E "ADAPTIVE|segments to|BREAKLINE"

echo ""
echo "=== P01 Results ==="
echo "BL0:" && /bin/grep "^# [0-9]" Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_0.pcd | head -1
echo "BL1:" && /bin/grep "^# [0-9]" Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_1.pcd | head -1
echo ""
echo "Sample comparison:"
echo "Sample BL0:" && /bin/grep "^# [0-9]" /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines/Pot_A_Piece_01_Breakline_0.pcd | head -1
echo "Sample BL1:" && /bin/grep "^# [0-9]" /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines/Pot_A_Piece_01_Breakline_1.pcd | head -1
