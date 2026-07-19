#!/bin/bash
# Compare breakline segment counts between new and sample datasets

NEW_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Breaklines/Pot_A"
SAMPLE_DIR="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines"

echo "=== Breakline Segment Comparison: New vs Sample ==="
echo ""
echo "| Piece | BL | New Segs | Sample Segs | Match |"
echo "|-------|----|---------:|------------:|-------|"

total_new=0
total_sample=0

for piece in 01 02 03 04 05 06 07 08; do
    for bl in 0 1; do
        new_file="${NEW_DIR}/Pot_A_Piece_${piece}_Breakline_${bl}.pcd"
        sample_file="${SAMPLE_DIR}/Pot_A_Piece_${piece}_Breakline_${bl}.pcd"

        if [ -f "$new_file" ]; then
            new_segs=$(head -2 "$new_file" | tail -1 | awk '{print $2}')
        else
            new_segs="-"
        fi

        if [ -f "$sample_file" ]; then
            sample_segs=$(head -2 "$sample_file" | tail -1 | awk '{print $2}')
        else
            sample_segs="-"
        fi

        if [ "$new_segs" = "$sample_segs" ]; then
            match="YES"
        else
            match="no"
        fi

        echo "| ${piece}    | ${bl}  | ${new_segs} | ${sample_segs} | ${match} |"

        if [ "$new_segs" != "-" ]; then
            total_new=$((total_new + new_segs))
        fi
        if [ "$sample_segs" != "-" ]; then
            total_sample=$((total_sample + sample_segs))
        fi
    done
done

echo ""
echo "Total segments - New: $total_new, Sample: $total_sample"
echo "Difference: $((total_new - total_sample))"
