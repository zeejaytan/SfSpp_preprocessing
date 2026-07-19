#!/bin/bash
#SBATCH --job-name=test_sample_td
#SBATCH --output=test_sample_tempdata_%j.log
#SBATCH --time=00:20:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --partition=sapphire

echo "=== CORRECT TEST: Edge Extraction on SAMPLE Surfaces in Temp/Data ==="
date

module load Apptainer

CONTAINER="/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif"
BINARY="/data/gpfs/projects/punim2657/sfs_preprocessing/build_new/EdgeLineExtractionHeadless"
WORK_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"
SAMPLE_DIR="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

cd "$WORK_DIR"

# Backup current Temp/Data surfaces
echo "Step 1: Backing up current Temp/Data surfaces..."
mkdir -p Temp/Data/Pot_A_backup_for_test
cp Temp/Data/Pot_A/*.xyz Temp/Data/Pot_A_backup_for_test/
echo "Backed up: $(ls Temp/Data/Pot_A_backup_for_test/*.xyz 2>/dev/null | wc -l) xyz files"

# Copy sample surfaces to Temp/Data
echo ""
echo "Step 2: Copying SAMPLE surfaces to Temp/Data/Pot_A/..."
for i in 01 02 03 04 05 06 07 08; do
    cp -f "$SAMPLE_DIR/Surfaces/Pot_A_Piece_${i}_Surface_0.xyz" "Temp/Data/Pot_A/Pot_A_Piece_${i}_Surface_0.xyz"
    cp -f "$SAMPLE_DIR/Surfaces/Pot_A_Piece_${i}_Surface_1.xyz" "Temp/Data/Pot_A/Pot_A_Piece_${i}_Surface_1.xyz"
done

# Verify copy
echo ""
echo "Step 3: Verifying - P01 Surface_0 should have 19463 lines (sample count):"
wc -l "Temp/Data/Pot_A/Pot_A_Piece_01_Surface_0.xyz"
echo "Sample has:"
wc -l "$SAMPLE_DIR/Surfaces/Pot_A_Piece_01_Surface_0.xyz"

# Run edge extraction (only Piece_01 for speed)
echo ""
echo "Step 4: Running edge extraction with SAMPLE surfaces..."
echo ""

apptainer exec \
    --bind /data/gpfs/projects/punim2657:/data/gpfs/projects/punim2657 \
    --pwd "$WORK_DIR" \
    "$CONTAINER" "$BINARY" 2>&1 | grep -E "BOUNDARY|OUTLIER|SEQUENCING|MULTI-COMPONENT|Processing|Saved PCD|Piece_01"

echo ""
echo "=== Step 5: Comparing Generated vs Sample Breaklines ==="
echo ""

# Focus on P01 which has the problematic BL1
echo "--- P01_BL0 ---"
echo "Generated (using sample surfaces):"
grep "^# [0-9]" Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_0.pcd | head -1
echo "Original sample breakline:"
grep "^# [0-9]" "$SAMPLE_DIR/Breaklines/Pot_A_Piece_01_Breakline_0.pcd" | head -1

echo ""
echo "--- P01_BL1 (the problematic one) ---"
echo "Generated (using sample surfaces):"
grep "^# [0-9]" Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_1.pcd | head -1
echo "Original sample breakline:"
grep "^# [0-9]" "$SAMPLE_DIR/Breaklines/Pot_A_Piece_01_Breakline_1.pcd" | head -1

echo ""
echo "=== Full Summary ==="
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
            printf "P%s_BL%s: Gen %2d seg/%3d pts vs Sample %2d seg/%3d pts (%s%%)\n" \
                "$i" "$b" "$gen_segs" "$gen_pts" "$sample_segs" "$sample_pts" "$ratio"
        fi
    done
done

# Restore original Temp/Data surfaces
echo ""
echo "Step 6: Restoring original Temp/Data surfaces..."
cp -f Temp/Data/Pot_A_backup_for_test/*.xyz Temp/Data/Pot_A/
echo "Restored. Verifying:"
wc -l "Temp/Data/Pot_A/Pot_A_Piece_01_Surface_0.xyz"

echo ""
echo "=== Test Complete ==="
date
