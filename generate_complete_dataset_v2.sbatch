#!/bin/bash
#SBATCH --job-name=gen_dataset_v2
#SBATCH --output=generate_complete_dataset_v2_%j.log
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --partition=sapphire

echo "=============================================="
echo "  COMPLETE DATASET GENERATION (Multi-Component Fix)"
echo "=============================================="
date
echo ""

module load Apptainer

CONTAINER="/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif"
EDGE_BINARY="/data/gpfs/projects/punim2657/sfs_preprocessing/build_new/EdgeLineExtractionHeadless"
WORK_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"
SAMPLE_DIR="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

cd "$WORK_DIR"

echo "Step 1: Verifying binaries exist..."
ls -la "$EDGE_BINARY"
echo ""

echo "Step 2: Verifying input surfaces exist..."
for i in 01 02 03 04 05 06 07 08; do
    s0="Temp/Data/Pot_A/Pot_A_Piece_${i}_Surface_0.xyz"
    s1="Temp/Data/Pot_A/Pot_A_Piece_${i}_Surface_1.xyz"
    if [ -f "$s0" ] && [ -f "$s1" ]; then
        echo "  Piece $i: Surface_0=$(wc -l < $s0) pts, Surface_1=$(wc -l < $s1) pts"
    else
        echo "  Piece $i: MISSING SURFACES!"
    fi
done
echo ""

echo "Step 3: Running edge extraction on all pieces..."
echo ""

apptainer exec \
    --bind /data/gpfs/projects/punim2657:/data/gpfs/projects/punim2657 \
    --pwd "$WORK_DIR" \
    "$CONTAINER" "$EDGE_BINARY" 2>&1 | grep -E "Processing|BOUNDARY|OUTLIER|SEQUENCING|MULTI-COMPONENT|Saved PCD|time for"

echo ""
echo "=============================================="
echo "  DATASET COMPARISON: NEW vs SAMPLE"
echo "=============================================="
echo ""

echo "=== BREAKLINES COMPARISON ==="
echo ""
printf "%-10s | %-20s | %-20s | %s\n" "Breakline" "New (segs/pts)" "Sample (segs/pts)" "Ratio"
printf "%s\n" "-----------|----------------------|----------------------|-------"

total_new_pts=0
total_sample_pts=0

for i in 01 02 03 04 05 06 07 08; do
    for b in 0 1; do
        new_file="Dataset/Breaklines/Pot_A/Pot_A_Piece_${i}_Breakline_${b}.pcd"
        sample_file="$SAMPLE_DIR/Breaklines/Pot_A_Piece_${i}_Breakline_${b}.pcd"

        if [ -f "$new_file" ] && [ -f "$sample_file" ]; then
            new_info=$(grep "^# [0-9]" "$new_file" | head -1)
            sample_info=$(grep "^# [0-9]" "$sample_file" | head -1)

            new_segs=$(echo "$new_info" | awk '{print $2}')
            new_pts=$(echo "$new_info" | awk '{print $3}')
            sample_segs=$(echo "$sample_info" | awk '{print $2}')
            sample_pts=$(echo "$sample_info" | awk '{print $3}')

            ratio=$(echo "scale=0; $new_pts * 100 / $sample_pts" | bc 2>/dev/null || echo "N/A")

            total_new_pts=$((total_new_pts + new_pts))
            total_sample_pts=$((total_sample_pts + sample_pts))

            printf "P%s_BL%s    | %2d segs / %4d pts   | %2d segs / %4d pts   | %3s%%\n" \
                "$i" "$b" "$new_segs" "$new_pts" "$sample_segs" "$sample_pts" "$ratio"
        fi
    done
done

echo ""
echo "=== TOTALS ==="
total_ratio=$(echo "scale=0; $total_new_pts * 100 / $total_sample_pts" | bc 2>/dev/null || echo "N/A")
printf "Total breakline points: New=%d, Sample=%d (%s%%)\n" "$total_new_pts" "$total_sample_pts" "$total_ratio"

echo ""
echo "=== SURFACES COMPARISON ==="
echo ""
printf "%-12s | %-15s | %-15s | %s\n" "Surface" "New (pts)" "Sample (pts)" "Ratio"
printf "%s\n" "-------------|-----------------|-----------------|-------"

for i in 01 02 03 04 05 06 07 08; do
    for s in 0 1; do
        new_file="Dataset/Surfaces/Pot_A/Pot_A_Piece_${i}_Surface_${s}.xyz"
        sample_file="$SAMPLE_DIR/Surfaces/Pot_A_Piece_${i}_Surface_${s}.xyz"

        if [ -f "$new_file" ] && [ -f "$sample_file" ]; then
            new_pts=$(wc -l < "$new_file")
            sample_pts=$(wc -l < "$sample_file")
            ratio=$(echo "scale=0; $new_pts * 100 / $sample_pts" | bc 2>/dev/null || echo "N/A")

            printf "P%s_Surf_%s  | %8d pts    | %8d pts    | %3s%%\n" \
                "$i" "$s" "$new_pts" "$sample_pts" "$ratio"
        fi
    done
done

echo ""
echo "=== POINT FILES COMPARISON ==="
echo ""

for i in 01 02 03 04 05 06 07 08; do
    new_file="Dataset/Point/Pot_A/Pot_A_Piece_${i}_Point.pcd"
    sample_file="$SAMPLE_DIR/Point/Pot_A_Piece_${i}_Point.pcd"

    if [ -f "$new_file" ] && [ -f "$sample_file" ]; then
        new_pts=$(grep "^POINTS" "$new_file" | awk '{print $2}')
        sample_pts=$(grep "^POINTS" "$sample_file" | awk '{print $2}')
        echo "P${i}_Point: New=$new_pts, Sample=$sample_pts"
    fi
done

echo ""
echo "=============================================="
echo "  GENERATION COMPLETE"
echo "=============================================="
date
