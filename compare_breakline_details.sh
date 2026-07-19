#!/bin/bash

NEW_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Breaklines/Pot_A"
SAMPLE_DIR="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines"

echo "=== Breakline Point Count and Segment Comparison ==="
echo ""
echo "| Piece | BL | New Points | Sample Points | New Segs | Sample Segs | Points Ratio |"
echo "|-------|----|-----------:|--------------:|---------:|------------:|--------------|"

for piece in 01 02 03 04 05 06 07 08; do
    for bl in 0 1; do
        new_f="${NEW_DIR}/Pot_A_Piece_${piece}_Breakline_${bl}.pcd"
        sample_f="${SAMPLE_DIR}/Pot_A_Piece_${piece}_Breakline_${bl}.pcd"

        if [ -f "$new_f" ] && [ -f "$sample_f" ]; then
            new_line=$(head -2 "$new_f" | tail -1)
            new_segs=$(echo "$new_line" | awk '{print $2}')
            new_pts=$(echo "$new_line" | awk '{print $3}')

            sample_line=$(head -2 "$sample_f" | tail -1)
            sample_segs=$(echo "$sample_line" | awk '{print $2}')
            sample_pts=$(echo "$sample_line" | awk '{print $3}')

            ratio=$(echo "scale=2; $new_pts / $sample_pts" | bc -l)

            echo "| ${piece}    | ${bl}  | ${new_pts} | ${sample_pts} | ${new_segs} | ${sample_segs} | ${ratio}x |"
        fi
    done
done
