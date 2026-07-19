#!/bin/bash
#SBATCH --job-name=reduce_sens
#SBATCH --output=reduced_sens.log
#SBATCH --error=reduced_sens.err
#SBATCH --time=00:30:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
#SBATCH --partition=sapphire

module load Apptainer

CONTAINER="/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif"
BIND="/data/gpfs/projects/punim2657:/data/gpfs/projects/punim2657"
WORK_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"

cd $WORK_DIR

echo "=== Rebuilding with reduced peak sensitivity ==="
cd build_new && apptainer exec --bind $BIND $CONTAINER make EdgeLineExtractionHeadless -j4 && cd ..

echo ""
echo "=== Testing all pieces ==="
for piece in 01 02 03 04 05 06 07 08; do
    echo "--- Piece_${piece} ---"
    apptainer exec --bind $BIND $CONTAINER \
        ./build_new/EdgeLineExtractionHeadless \
        --potID Pot_A --pieceNo Piece_${piece} \
        --datasetPath Dataset --tempPath Temp 2>&1 | grep -E "ADAPTIVE|segments to"
done

echo ""
echo "=== COMPARISON: Segments and Points ==="
echo "Format: Piece BL# new_seg/new_pts vs sample_seg/sample_pts"
for i in 01 02 03 04 05 06 07 08; do
    for b in 0 1; do
        new_seg=$(/bin/grep "^# [0-9]" Dataset/Breaklines/Pot_A/Pot_A_Piece_${i}_Breakline_${b}.pcd | head -1 | awk '{print $2}')
        new_pts=$(/bin/grep "^POINTS" Dataset/Breaklines/Pot_A/Pot_A_Piece_${i}_Breakline_${b}.pcd | awk '{print $2}')
        sam_seg=$(/bin/grep "^# [0-9]" /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines/Pot_A_Piece_${i}_Breakline_${b}.pcd | head -1 | awk '{print $2}')
        sam_pts=$(/bin/grep "^POINTS" /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines/Pot_A_Piece_${i}_Breakline_${b}.pcd | awk '{print $2}')
        echo "P${i}_BL${b}: ${new_seg}seg/${new_pts}pts vs ${sam_seg}seg/${sam_pts}pts"
    done
done
