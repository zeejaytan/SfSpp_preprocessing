#!/bin/bash
#SBATCH --job-name=full_dataset
#SBATCH --output=full_dataset.log
#SBATCH --error=full_dataset.err
#SBATCH --time=04:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --partition=sapphire

module load Apptainer

CONTAINER="/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif"
BIND="/data/gpfs/projects/punim2657:/data/gpfs/projects/punim2657"
WORK_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"

cd $WORK_DIR

echo "=========================================="
echo "COMPLETE DATASET GENERATION"
echo "Started: $(date)"
echo "=========================================="

# Step 1: Copy new surfaces from Temp to Dataset
echo ""
echo "=== Step 1: Copying new surfaces to Dataset ==="
for i in 01 02 03 04 05 06 07 08; do
    cp -v Temp/Data/Pot_A/Pot_A_Piece_${i}_Surface_0.xyz Dataset/Surfaces/Pot_A/
    cp -v Temp/Data/Pot_A/Pot_A_Piece_${i}_Surface_1.xyz Dataset/Surfaces/Pot_A/
done

echo ""
echo "=== Step 2: Running breakline extraction for all pieces ==="
for i in 01 02 03 04 05 06 07 08; do
    echo ""
    echo "--- Processing Piece_${i} breaklines ---"
    apptainer exec --bind $BIND $CONTAINER \
        ./build_new/EdgeLineExtractionHeadless \
        --potID Pot_A \
        --pieceNo Piece_${i} \
        --datasetPath Dataset \
        --tempPath Temp
done

echo ""
echo "=========================================="
echo "DATASET GENERATION COMPLETE"
echo "Finished: $(date)"
echo "=========================================="

echo ""
echo "=== Final Surface Counts ==="
for i in 01 02 03 04 05 06 07 08; do
    echo "Piece $i: S0=$(wc -l < Dataset/Surfaces/Pot_A/Pot_A_Piece_${i}_Surface_0.xyz) S1=$(wc -l < Dataset/Surfaces/Pot_A/Pot_A_Piece_${i}_Surface_1.xyz)"
done

echo ""
echo "=== Final Breakline Counts ==="
for i in 01 02 03 04 05 06 07 08; do
    bl0=$(wc -l < Dataset/Breaklines/Pot_A/Pot_A_Piece_${i}_Breakline_0.pcd 2>/dev/null || echo "N/A")
    bl1=$(wc -l < Dataset/Breaklines/Pot_A/Pot_A_Piece_${i}_Breakline_1.pcd 2>/dev/null || echo "N/A")
    echo "Piece $i: BL0=$bl0 BL1=$bl1"
done

echo ""
echo "=== Sample Comparison ==="
SAMPLE_PATH="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
echo "Surfaces:"
for i in 01 02 03 04 05 06 07 08; do
    new_s0=$(wc -l < Dataset/Surfaces/Pot_A/Pot_A_Piece_${i}_Surface_0.xyz)
    new_s1=$(wc -l < Dataset/Surfaces/Pot_A/Pot_A_Piece_${i}_Surface_1.xyz)
    sample_s0=$(wc -l < ${SAMPLE_PATH}/Surfaces/Pot_A_Piece_${i}_Surface_0.xyz)
    sample_s1=$(wc -l < ${SAMPLE_PATH}/Surfaces/Pot_A_Piece_${i}_Surface_1.xyz)
    echo "Piece $i: New(${new_s0}/${new_s1}) vs Sample(${sample_s0}/${sample_s1})"
done

echo ""
echo "Breaklines (segment counts from header):"
for i in 01 02 03 04 05 06 07 08; do
    for b in 0 1; do
        new_seg=$(/bin/grep "^# " Dataset/Breaklines/Pot_A/Pot_A_Piece_${i}_Breakline_${b}.pcd 2>/dev/null | wc -l)
        sample_seg=$(/bin/grep "^# " ${SAMPLE_PATH}/Breaklines/Pot_A_Piece_${i}_Breakline_${b}.pcd 2>/dev/null | wc -l)
        echo "Piece $i BL$b: New=$new_seg segments vs Sample=$sample_seg segments"
    done
done
