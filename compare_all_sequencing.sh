#!/bin/bash

echo "============================================================"
echo "HOLISTIC ANALYSIS: Why Does Piece 01 BL1 Fail?"
echo "============================================================"
echo ""

echo "=== Sequencing Performance Across All Surfaces ==="
echo ""
echo "| Surface | Boundary | Filtered | Sequenced | Retention | Loss | Status |"
echo "|---------|----------|----------|-----------|-----------|------|--------|"

awk '
/Processing Piece/ {
    piece = $3
    surface_num = 0
}
/ADAPTIVE BOUNDARY EDGE/ {
    surface_num++
    boundary_pts = $2
}
/ADAPTIVE OUTLIER.*boundary points/ {
    before_filter = $2
}
/After filtering/ {
    after_filter = $4
}
/ADAPTIVE SEQUENCING/ {
    seq_input = $4
}
/ADAPTIVE SPHERE-MARCHING/ {
    seq_output = $3
    gsub(/,/, "", seq_output)

    if (seq_input > 0 && seq_output > 0) {
        retention = int((seq_output / seq_input) * 100)
        loss = seq_input - seq_output
        loss_pct = int((loss / seq_input) * 100)

        status = "OK"
        if (retention < 90) status = "WARN"
        if (retention < 70) status = "POOR"
        if (retention < 40) status = "FAIL"

        printf "| %s S%d | %4d | %4d | %4d | %3d%% | %3d (%2d%%) | %s |\n",
               piece, surface_num, boundary_pts, after_filter, seq_output, retention, loss, loss_pct, status
    }
}
' edge_all_pieces.log | head -20

echo ""
echo "=== Summary Statistics ==="
echo ""

awk '
/ADAPTIVE SEQUENCING/ {
    seq_input = $4
    seq_count++
}
/ADAPTIVE SPHERE-MARCHING/ {
    seq_output = $3
    gsub(/,/, "", seq_output)

    if (seq_input > 0 && seq_output > 0) {
        retention = (seq_output / seq_input) * 100
        total_retention += retention

        if (retention >= 90) excellent++
        else if (retention >= 70) good++
        else if (retention >= 40) poor++
        else fail++

        if (retention < min_retention || min_retention == 0) {
            min_retention = retention
            worst_input = seq_input
            worst_output = seq_output
        }
        if (retention > max_retention) {
            max_retention = retention
            best_input = seq_input
            best_output = seq_output
        }
    }
}
END {
    if (seq_count > 0) {
        avg = total_retention / seq_count
        print "Total Surfaces Processed: " seq_count
        print ""
        print "Sequencing Performance:"
        print "  Excellent (≥90%): " excellent " surfaces"
        print "  Good (70-89%):    " good " surfaces"
        print "  Poor (40-69%):    " poor " surfaces"
        print "  Failed (<40%):    " fail " surfaces"
        print ""
        print "Average Retention: " int(avg) "%"
        print ""
        print "Best:  " int(max_retention) "% (" best_input " → " best_output " pts)"
        print "Worst: " int(min_retention) "% (" worst_input " → " worst_output " pts)"
    }
}
' edge_all_pieces.log

echo ""
echo "=== Why Is Piece 01 BL1 Different? ==="
echo ""

echo "Analyzing boundary detection parameters..."
echo ""

awk '
BEGIN {
    piece_num = 0
}
/Processing Piece/ {
    piece_num++
    piece = $3
    surface_count = 0
}
/ADAPTIVE BOUNDARY EDGE/ {
    surface_count++
    surf_pts = $2
    spacing = $0
    gsub(/.*spacing≈/, "", spacing)
    gsub(/mm.*/, "", spacing)
    spacing_val = spacing + 0

    boundary_r = $0
    gsub(/.*boundary_r=/, "", boundary_r)
    gsub(/mm.*/, "", boundary_r)
}
/ADAPTIVE OUTLIER.*boundary points/ {
    boundary_count = $2
    boundary_pct = (boundary_count / surf_pts) * 100

    outlier_spacing = $0
    gsub(/.*spacing≈/, "", outlier_spacing)
    gsub(/mm.*/, "", outlier_spacing)

    if (piece_num == 1) {
        printf "Piece 01 Surface %d:\n", surface_count
        printf "  Surface points: %d, spacing: %.3fmm\n", surf_pts, spacing_val
        printf "  Boundary points: %d (%.1f%% of surface)\n", boundary_count, boundary_pct
        printf "  Boundary spacing: %smm\n", outlier_spacing
        printf "\n"
    }
}
' edge_all_pieces.log | head -15

echo "Comparing boundary density across pieces..."
echo ""
echo "| Piece | Surface Points | Boundary Points | Boundary % |"
echo "|-------|----------------|-----------------|------------|"

awk '
/Processing Piece/ {
    piece = $3
    surface_count = 0
}
/ADAPTIVE BOUNDARY EDGE/ {
    surface_count++
    surf_pts = $2
}
/ADAPTIVE OUTLIER.*boundary points/ {
    boundary_count = $2

    if (boundary_count > 0 && surf_pts > 0) {
        boundary_pct = (boundary_count / surf_pts) * 100
        printf "| %s S%d | %5d | %4d | %5.2f%% |\n", piece, surface_count, surf_pts, boundary_count, boundary_pct
    }
}
' edge_all_pieces.log | head -20

echo ""
