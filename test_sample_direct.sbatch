#!/bin/bash
#SBATCH --job-name=test_sample_dir
#SBATCH --output=test_sample_direct_%j.log
#SBATCH --time=00:20:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --partition=sapphire

echo "=== Direct Test: Edge Extraction on SAMPLE Surfaces ==="
date

module load Apptainer

CONTAINER="/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif"
BINARY="/data/gpfs/projects/punim2657/sfs_preprocessing/build_new/EdgeLineExtractionHeadless"
WORK_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"
SAMPLE_DIR="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

cd "$WORK_DIR"

# First backup our current surfaces
echo "Step 1: Backing up current surfaces..."
mkdir -p Dataset/Surfaces/Pot_A_our_backup_direct
cp Dataset/Surfaces/Pot_A/*.xyz Dataset/Surfaces/Pot_A_our_backup_direct/
echo "Backed up $(ls Dataset/Surfaces/Pot_A_our_backup_direct/*.xyz | wc -l) files"

# Copy sample surfaces
echo ""
echo "Step 2: Copying SAMPLE surfaces..."
for i in 01 02 03 04 05 06 07 08; do
    cp -f "$SAMPLE_DIR/Surfaces/Pot_A_Piece_${i}_Surface_0.xyz" "Dataset/Surfaces/Pot_A/"
    cp -f "$SAMPLE_DIR/Surfaces/Pot_A_Piece_${i}_Surface_1.xyz" "Dataset/Surfaces/Pot_A/"
done

# Verify the copy worked
echo ""
echo "Step 3: Verifying copy - P01 Surface_0 should have 19463 lines (sample count):"
wc -l "Dataset/Surfaces/Pot_A/Pot_A_Piece_01_Surface_0.xyz"
echo "Sample file has:"
wc -l "$SAMPLE_DIR/Surfaces/Pot_A_Piece_01_Surface_0.xyz"

# Now run edge extraction
echo ""
echo "Step 4: Running edge extraction on SAMPLE surfaces..."
echo ""

apptainer exec \
    --bind /data/gpfs/projects/punim2657:/data/gpfs/projects/punim2657 \
    --pwd "$WORK_DIR" \
    "$CONTAINER" "$BINARY" 2>&1

echo ""
echo "=== Step 5: Comparing Generated vs Sample Breaklines ==="
echo ""

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

# Restore our surfaces
echo ""
echo "Step 6: Restoring our original surfaces..."
cp -f Dataset/Surfaces/Pot_A_our_backup_direct/*.xyz Dataset/Surfaces/Pot_A/
echo "Restored. Verifying - P01 Surface_0 should have 20755 lines (our count):"
wc -l "Dataset/Surfaces/Pot_A/Pot_A_Piece_01_Surface_0.xyz"

echo ""
echo "=== Test Complete ==="
date
