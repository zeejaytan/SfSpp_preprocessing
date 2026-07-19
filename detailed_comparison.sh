#!/bin/bash

NEW_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Breaklines/Pot_A"
SAMPLE_DIR="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines"
LOG_FILE="/data/gpfs/projects/punim2657/sfs_preprocessing/edge_all_pieces.log"

echo "============================================================"
echo "DETAILED COMPARISON: New Dataset vs Sample"
echo "============================================================"
echo ""

for piece in 01 02 03 04 05 06 07 08; do
    echo "========================================="
    echo "PIECE ${piece} - Detailed Analysis"
    echo "========================================="

    for bl in 0 1; do
        new_f="${NEW_DIR}/Pot_A_Piece_${piece}_Breakline_${bl}.pcd"
        sample_f="${SAMPLE_DIR}/Pot_A_Piece_${piece}_Breakline_${bl}.pcd"

        if [ -f "$new_f" ] && [ -f "$sample_f" ]; then
            # Get header info
            new_line=$(head -2 "$new_f" | tail -1)
            new_segs=$(echo "$new_line" | awk '{print $2}')
            new_pts=$(echo "$new_line" | awk '{print $3}')

            sample_line=$(head -2 "$sample_f" | tail -1)
            sample_segs=$(echo "$sample_line" | awk '{print $2}')
            sample_pts=$(echo "$sample_line" | awk '{print $3}')

            seg_diff=$((new_segs - sample_segs))
            pts_diff=$((new_pts - sample_pts))

            echo ""
            echo "--- Breakline ${bl} ---"
            echo "Points:    New=$new_pts  Sample=$sample_pts  Diff=$pts_diff"
            echo "Segments:  New=$new_segs  Sample=$sample_segs  Diff=$seg_diff"

            # Extract processing info from log for this piece
            if [ "$bl" -eq 0 ]; then
                # BL0 is from Surface_1 (processed first)
                surface_marker="Surface 1.*Piece_${piece}"
            else
                # BL1 is from Surface_0 (processed second)
                surface_marker="Surface 0.*Piece_${piece}"
            fi

            # Get boundary, outlier, sequencing, and sphere-marching info
            echo ""
            echo "Processing Pipeline:"

            # Find the section for this surface
            awk -v piece="Piece_${piece}" '
                /Processing Piece/ {
                    if ($0 ~ piece) {
                        in_piece=1
                        surface_count=0
                    } else {
                        in_piece=0
                    }
                }
                in_piece && /ADAPTIVE BOUNDARY EDGE/ {
                    surface_count++
                    if ((surface_count == 1 && "'$bl'" == 0) || (surface_count == 2 && "'$bl'" == 1)) {
                        boundary_pts = $2
                        boundary_r = $0
                        sub(/.*boundary_r=/, "", boundary_r)
                        sub(/mm.*/, "", boundary_r)
                        print "  1. Boundary Detection: " $2 " points, radius=" boundary_r "mm"
                    }
                }
                in_piece && /ADAPTIVE OUTLIER/ && /boundary points/ {
                    surface_count_outlier++
                    if ((surface_count_outlier == 1 && "'$bl'" == 0) || (surface_count_outlier == 2 && "'$bl'" == 1)) {
                        before_outlier = $2
                        outlier_r = $0
                        sub(/.*outlier_r=/, "", outlier_r)
                        sub(/mm.*/, "", outlier_r)
                        min_neighbors = $0
                        sub(/.*min_neighbors=/, "", min_neighbors)
                        getline
                        if (/After filtering/) {
                            after_outlier = $4
                            removed = $7
                            print "  2. Outlier Removal: " before_outlier " → " after_outlier " points (removed " removed "), radius=" outlier_r "mm, min_neighbors=" min_neighbors
                        }
                    }
                }
                in_piece && /ADAPTIVE SEQUENCING/ {
                    surface_count_seq++
                    if ((surface_count_seq == 1 && "'$bl'" == 0) || (surface_count_seq == 2 && "'$bl'" == 1)) {
                        seq_pts = $4
                        k_val = $0
                        sub(/.*K=/, "", k_val)
                        sub(/ .*/, "", k_val)
                        print "  3. Sequencing: " seq_pts " points, K=" k_val
                    }
                }
                in_piece && /ADAPTIVE SPHERE-MARCHING/ {
                    surface_count_sphere++
                    if ((surface_count_sphere == 1 && "'$bl'" == 0) || (surface_count_sphere == 2 && "'$bl'" == 1)) {
                        input_pts = $3
                        sub(/,/, "", input_pts)
                        avg_spacing = $0
                        sub(/.*avgSpacing: /, "", avg_spacing)
                        sub(/mm.*/, "", avg_spacing)
                        radius = $0
                        sub(/.*adaptiveRadius: /, "", radius)
                        sub(/mm.*/, "", radius)
                        print "  4. Sphere-Marching: Input=" input_pts " pts, spacing=" avg_spacing "mm, radius=" radius "mm"
                    }
                }
                in_piece && /Smoothed breakline output points/ {
                    surface_count_smooth++
                    if ((surface_count_smooth == 1 && "'$bl'" == 0) || (surface_count_smooth == 2 && "'$bl'" == 1)) {
                        smooth_pts = $5
                        print "  5. B-spline Smoothing: " smooth_pts " points"
                    }
                }
                in_piece && /ADAPTIVE PEAK DETECTION/ {
                    surface_count_peak++
                    if ((surface_count_peak == 1 && "'$bl'" == 0) || (surface_count_peak == 2 && "'$bl'" == 1)) {
                        divisor = $0
                        sub(/.*divisor=/, "", divisor)
                        sub(/\).*/, "", divisor)
                        print "  6. Peak Detection: divisor=" divisor
                    }
                }
            ' "$LOG_FILE"

            # Suggest action based on difference
            echo ""
            if [ "$seg_diff" -gt 0 ]; then
                echo "ACTION: Reduce segments by $seg_diff → Increase peak detection sensitivity (lower divisor)"
            elif [ "$seg_diff" -lt 0 ]; then
                echo "ACTION: Increase segments by $((-seg_diff)) → Decrease peak detection sensitivity (higher divisor)"
            else
                echo "STATUS: ✓ Segment count matches sample!"
            fi

            if [ "$pts_diff" -lt -50 ]; then
                echo "WARNING: $pts_diff fewer points than sample - check outlier removal and sequencing"
            fi
        fi
    done
    echo ""
done

echo ""
echo "============================================================"
echo "SUMMARY"
echo "============================================================"
echo ""
echo "Total Segments:"
total_new=$(grep "Total segments - New:" <<< "$(./compare_segments.sh)" | awk '{print $NF}')
total_sample=$(grep "Total segments - New:" <<< "$(./compare_segments.sh)" | awk -F'Sample: ' '{print $2}' | awk '{print $1}')
echo "  New: ${total_new:-78}"
echo "  Sample: ${total_sample:-56}"
echo "  Difference: $((${total_new:-78} - ${total_sample:-56}))"
echo ""
echo "Pieces with excess segments:"
./compare_segments.sh | grep "no" | awk '$3 > $4 {print "  Piece " $2 " BL" $4 ": +" ($3-$4) " segments"}'
