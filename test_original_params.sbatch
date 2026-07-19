#!/bin/bash
#SBATCH --job-name=test_orig
#SBATCH --output=test_original_params_%j.log
#SBATCH --time=00:20:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --partition=sapphire

echo "=== Testing with ORIGINAL FIXED parameters ==="
date

module load Apptainer

CONTAINER="/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif"
BUILD_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing/build_new"
SRC_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"
WORK_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"

# Rebuild
echo "Rebuilding with original fixed parameters..."
rm -f "$BUILD_DIR/CMakeCache.txt"
rm -rf "$BUILD_DIR/CMakeFiles"

apptainer exec \
    --bind /data/gpfs/projects/punim2657:/data/gpfs/projects/punim2657 \
    --pwd "$BUILD_DIR" \
    "$CONTAINER" bash -c "
        cmake '$SRC_DIR' -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_STANDARD=17 && \
        make EdgeLineExtractionHeadless -j4
    " 2>&1 | tail -20

echo ""
echo "Running edge extraction with original fixed parameters..."
cd "$WORK_DIR"

apptainer exec \
    --bind /data/gpfs/projects/punim2657:/data/gpfs/projects/punim2657 \
    --pwd "$WORK_DIR" \
    "$CONTAINER" "$BUILD_DIR/EdgeLineExtractionHeadless" 2>&1 | grep -E "BOUNDARY|OUTLIER|SEQUENCING|MULTI-COMPONENT|Saved PCD"

echo ""
echo "=== Results with ORIGINAL FIXED parameters ==="
echo ""

# Compare P01 breaklines
echo "--- P01_BL1 (the problematic one) ---"
echo "New (original params):"
head -10 Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_1.pcd | grep "^#"
echo ""
echo "Sample:"
head -10 /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines/Pot_A_Piece_01_Breakline_1.pcd | grep "^#"

echo ""
echo "=== Summary ==="
for i in 01 02 03 04 05 06 07 08; do
    for b in 0 1; do
        new_file="Dataset/Breaklines/Pot_A/Pot_A_Piece_${i}_Breakline_${b}.pcd"
        sample_file="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines/Pot_A_Piece_${i}_Breakline_${b}.pcd"
        if [ -f "$new_file" ] && [ -f "$sample_file" ]; then
            new_info=$(grep "^# [0-9]" "$new_file" | head -1)
            sample_info=$(grep "^# [0-9]" "$sample_file" | head -1)
            new_segs=$(echo "$new_info" | awk '{print $2}')
            new_pts=$(echo "$new_info" | awk '{print $3}')
            sample_segs=$(echo "$sample_info" | awk '{print $2}')
            sample_pts=$(echo "$sample_info" | awk '{print $3}')
            ratio=$(echo "scale=0; $new_pts * 100 / $sample_pts" | bc 2>/dev/null || echo "N/A")
            printf "P%s_BL%s: New %2d seg/%3d pts vs Sample %2d seg/%3d pts (%s%%)\n" \
                "$i" "$b" "$new_segs" "$new_pts" "$sample_segs" "$sample_pts" "$ratio"
        fi
    done
done

echo ""
date
