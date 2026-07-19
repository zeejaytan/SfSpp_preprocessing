#!/bin/bash
#SBATCH --job-name=density_v2
#SBATCH --output=density_v2.log
#SBATCH --error=density_v2.err
#SBATCH --time=02:00:00
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
echo "=== Running mesh preprocessing (all pieces) ==="
apptainer exec --bind $BIND $CONTAINER ./build_new/MeshPreprocessingHeadless 2>&1 | grep -E "DENSITY-ADAPTIVE|Number of clusters|Piece"

echo ""
echo "=== Checking cluster counts ==="
for i in 01 02 03 04 05 06 07 08; do
    cnt=$(ls Temp/Data/Pot_A/Pot_A_Piece_${i}_unclustered.plyCluster_*.pcd 2>/dev/null | wc -l)
    echo "P${i}: ${cnt} clusters"
done

echo ""
echo "=== Running edge extraction for all pieces ==="
for piece in 01 02 03 04 05 06 07 08; do
    echo "--- Piece_${piece} ---"
    apptainer exec --bind $BIND $CONTAINER \
        ./build_new/EdgeLineExtractionHeadless \
        --potID Pot_A --pieceNo Piece_${piece} \
        --datasetPath Dataset --tempPath Temp 2>&1 | grep -E "segments to"
done

echo ""
echo "=== FINAL COMPARISON ==="
for i in 01 02 03 04 05 06 07 08; do
    for b in 0 1; do
        new=$(/bin/grep "^# [0-9]" Dataset/Breaklines/Pot_A/Pot_A_Piece_${i}_Breakline_${b}.pcd 2>/dev/null | head -1)
        sam=$(/bin/grep "^# [0-9]" /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines/Pot_A_Piece_${i}_Breakline_${b}.pcd 2>/dev/null | head -1)
        echo "P${i}_BL${b}: NEW=${new} | SAMPLE=${sam}"
    done
done
