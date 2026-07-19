#!/bin/bash
#SBATCH --job-name=test_sample_surf
#SBATCH --output=test_sample_surfaces_%j.log
#SBATCH --time=00:20:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --partition=sapphire

echo "=== Testing Edge Extraction on SAMPLE Surfaces ==="
echo "Hypothesis: Sample surfaces produce connected boundaries (no multi-component issue)"
date

module load Apptainer

CONTAINER="/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif"
BINARY="/data/gpfs/projects/punim2657/sfs_preprocessing/build_new/EdgeLineExtractionHeadless"
WORK_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"
SAMPLE_DIR="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

cd "$WORK_DIR"

# Backup current surfaces
echo "Backing up current surfaces..."
mkdir -p Dataset/Surfaces/Pot_A_backup
cp Dataset/Surfaces/Pot_A/*.xyz Dataset/Surfaces/Pot_A_backup/ 2>/dev/null || true

# Copy sample surfaces to our location (temporarily)
echo "Copying sample surfaces for Pot_A..."
for i in 01 02 03 04 05 06 07 08; do
    cp "$SAMPLE_DIR/Surfaces/Pot_A_Piece_${i}_Surface_0.xyz" "Dataset/Surfaces/Pot_A/" 2>/dev/null || true
    cp "$SAMPLE_DIR/Surfaces/Pot_A_Piece_${i}_Surface_1.xyz" "Dataset/Surfaces/Pot_A/" 2>/dev/null || true
done

echo ""
echo "Running edge extraction with SAMPLE surfaces..."
echo ""

apptainer exec \
    --bind /data/gpfs/projects/punim2657:/data/gpfs/projects/punim2657 \
    --pwd "$WORK_DIR" \
    "$CONTAINER" "$BINARY" 2>&1 | grep -E "BOUNDARY|OUTLIER|SEQUENCING|MULTI-COMPONENT|Processing|Saved PCD"

echo ""
echo "=== Results using SAMPLE Surfaces ==="
echo ""

# Compare P01 breaklines
echo "--- P01_BL0 ---"
echo "Generated from sample surfaces:"
head -10 Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_0.pcd | grep "^#"
echo "Original sample:"
head -10 "$SAMPLE_DIR/Breaklines/Pot_A_Piece_01_Breakline_0.pcd" | grep "^#"

echo ""
echo "--- P01_BL1 (the problematic one) ---"
echo "Generated from sample surfaces:"
head -10 Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_1.pcd | grep "^#"
echo "Original sample:"
head -10 "$SAMPLE_DIR/Breaklines/Pot_A_Piece_01_Breakline_1.pcd" | grep "^#"

echo ""
echo "=== Full Comparison ==="
for i in 01 02 03 04 05 06 07 08; do
    for b in 0 1; do
        gen_file="Dataset/Breaklines/Pot_A/Pot_A_Piece_${i}_Breakline_${b}.pcd"
        sample_file="$SAMPLE_DIR/Breaklines/Pot_A_Piece_${i}_Breakline_${b}.pcd"
        if [ -f "$gen_file" ] && [ -f "$sample_file" ]; then
            gen_info=$(grep "^# [0-9]" "$gen_file" | head -1)
            sample_info=$(grep "^# [0-9]" "$sample_file" | head -1)
            gen_segs=$(echo "$gen_info" | awk '{print $2}')
            gen_pts=$(echo "$gen_info" | awk '{print $3}')
            sample_segs=$(echo "$sample_info" | awk '{print $2}')
            sample_pts=$(echo "$sample_info" | awk '{print $3}')
            ratio=$(echo "scale=0; $gen_pts * 100 / $sample_pts" | bc 2>/dev/null || echo "N/A")
            printf "P%s_BL%s: Generated %2d seg/%3d pts vs Sample %2d seg/%3d pts (%s%%)\n" \
                "$i" "$b" "$gen_segs" "$gen_pts" "$sample_segs" "$sample_pts" "$ratio"
        fi
    done
done

# Restore original surfaces
echo ""
echo "Restoring original surfaces..."
cp Dataset/Surfaces/Pot_A_backup/*.xyz Dataset/Surfaces/Pot_A/ 2>/dev/null || true

echo ""
echo "=== Test Complete ==="
date
