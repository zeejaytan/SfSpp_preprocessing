#!/bin/bash
#SBATCH --job-name=debug_p01
#SBATCH --output=debug_p01.log
#SBATCH --error=debug_p01.err
#SBATCH --time=00:30:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
#SBATCH --partition=sapphire

module load Apptainer

CONTAINER="/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif"
BIND="/data/gpfs/projects/punim2657:/data/gpfs/projects/punim2657"
cd /data/gpfs/projects/punim2657/sfs_preprocessing

echo "=== Detailed P01 Edge Extraction Debug ==="
apptainer exec --bind $BIND $CONTAINER \
    ./build_new/EdgeLineExtractionHeadless \
    --potID Pot_A --pieceNo Piece_01 \
    --datasetPath Dataset --tempPath Temp 2>&1 | grep -E "Surface_0|Surface_1|ADAPTIVE|boundary|Input:|Output|Smoothed|segments|BREAKLINE|spacing"

echo ""
echo "=== Comparing Sample vs New P01 Breaklines ==="
echo "--- BL0 ---"
echo "New segments:" && /bin/grep "^# " Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_0.pcd
echo "Sample segments:" && /bin/grep "^# " /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines/Pot_A_Piece_01_Breakline_0.pcd
echo ""
echo "--- BL1 ---"
echo "New segments:" && /bin/grep "^# " Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_1.pcd
echo "Sample segments:" && /bin/grep "^# " /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines/Pot_A_Piece_01_Breakline_1.pcd

echo ""
echo "=== Sample Surface comparison ==="
if [ -f /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Surfaces/Pot_A_Piece_01_Surface_0.xyz ]; then
    echo "Sample Surface_0:" && wc -l /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Surfaces/Pot_A_Piece_01_Surface_0.xyz
fi
if [ -f /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Surfaces/Pot_A_Piece_01_Surface_1.xyz ]; then
    echo "Sample Surface_1:" && wc -l /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Surfaces/Pot_A_Piece_01_Surface_1.xyz
fi
echo "New Surface_0:" && wc -l Temp/Data/Pot_A/Pot_A_Piece_01_Surface_0.xyz
echo "New Surface_1:" && wc -l Temp/Data/Pot_A/Pot_A_Piece_01_Surface_1.xyz
