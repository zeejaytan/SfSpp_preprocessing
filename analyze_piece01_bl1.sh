#!/bin/bash

echo "============================================================"
echo "ANALYSIS: Piece 01 BL1 Sequencing Failure"
echo "============================================================"
echo ""

# Extract Piece 01 Surface_0 (BL1) processing from log
echo "--- Processing Pipeline for Piece 01 BL1 (Surface_0) ---"
echo ""

awk '/Processing Piece 01/,/Processing Piece 02/ {
    if (/Surface 0.*Piece_01/) {
        in_surface0=1
    }
    if (in_surface0) {
        if (/ADAPTIVE BOUNDARY EDGE/) {
            print "1. BOUNDARY DETECTION:"
            print "   " $0
            boundary_pts = $2
        }
        if (/ADAPTIVE OUTLIER.*boundary points/) {
            print ""
            print "2. OUTLIER REMOVAL (Before):"
            print "   " $0
            before_filter = $2
        }
        if (/After filtering/) {
            print "   " $0
            after_filter = $4
            removed = $7
            removal_pct = int((removed / before_filter) * 100)
            print "   → Removed " removal_pct "% of boundary points"
        }
        if (/ADAPTIVE SEQUENCING/) {
            print ""
            print "3. SEQUENCING:"
            print "   " $0
            seq_input = $4
        }
        if (/ADAPTIVE SPHERE-MARCHING/) {
            seq_output = $3
            sub(/,/, "", seq_output)
            loss = seq_input - seq_output
            loss_pct = int((loss / seq_input) * 100)
            print "   → Sequencing output: " seq_output " points"
            print "   → Lost " loss " points (" loss_pct "% loss) ← CRITICAL"
            print ""
            print "4. SPHERE-MARCHING:"
            print "   " $0
        }
        if (/Smoothed breakline output/) {
            print ""
            print "5. B-SPLINE SMOOTHING:"
            print "   Final output: " $5 " points"
        }
        if (/Saved PCD.*Breakline_1/) {
            in_surface0=0
        }
    }
}' edge_all_pieces.log

echo ""
echo "--- Comparison with Sample ---"
echo ""
echo "New BL1:    90 points, 10 segments (from last run with divisor=8)"
echo "Sample BL1: 214 points, 5 segments"
echo "Difference: -124 points (-58%), +5 segments (+100%)"
echo ""

echo "--- Root Cause Analysis ---"
echo ""
echo "The 73% sequencing loss (480 → 129 pts) indicates the boundary"
echo "point cloud has disconnected clusters that cannot be linked by"
echo "K-nearest neighbor sequencing."
echo ""
echo "Possible causes:"
echo "1. Surface has natural gaps/holes (geometry)"
echo "2. Boundary detection missed connecting regions (parameter)"
echo "3. Outlier removal created gaps by removing bridge points"
echo "4. Surface segmentation cut the boundary incorrectly"
echo ""

echo "--- Examining Boundary Files ---"
echo ""

# Check if boundary files exist
TEMP_EDGE="/data/gpfs/projects/punim2657/sfs_preprocessing/Temp/Temp_edge/Pot_A"

if [ -f "${TEMP_EDGE}/boundaryImproved.pcd" ]; then
    boundary_count=$(head -2 "${TEMP_EDGE}/boundaryImproved.pcd" | tail -1 | awk '{print $2}')
    echo "boundaryImproved.pcd: ${boundary_count} points (after cluster removal)"
else
    echo "boundaryImproved.pcd: NOT FOUND"
fi

if [ -f "${TEMP_EDGE}/cloud_Filtered.pcd" ]; then
    filtered_count=$(grep -v "^#" "${TEMP_EDGE}/cloud_Filtered.pcd" | grep -v "^VERSION" | grep -v "^FIELDS" | grep -v "^SIZE" | grep -v "^TYPE" | grep -v "^COUNT" | grep -v "^WIDTH" | grep -v "^HEIGHT" | grep -v "^VIEWPOINT" | grep -v "^POINTS" | grep -v "^DATA" | grep -c "^[0-9]")
    echo "cloud_Filtered.pcd: ${filtered_count} points (after outlier removal)"
else
    echo "cloud_Filtered.pcd: NOT FOUND"
fi

if [ -f "${TEMP_EDGE}/_breakLineFromConcaveHull.pcd" ]; then
    sequenced_count=$(grep -v "^#" "${TEMP_EDGE}/_breakLineFromConcaveHull.pcd" | grep -v "^VERSION" | grep -v "^FIELDS" | grep -v "^SIZE" | grep -v "^TYPE" | grep -v "^COUNT" | grep -v "^WIDTH" | grep -v "^HEIGHT" | grep -v "^VIEWPOINT" | grep -v "^POINTS" | grep -v "^DATA" | grep -c "^[0-9-]")
    echo "_breakLineFromConcaveHull.pcd: ${sequenced_count} points (after sequencing)"
else
    echo "_breakLineFromConcaveHull.pcd: NOT FOUND"
fi

echo ""
echo "--- Recommended Investigations ---"
echo ""
echo "1. Visualize cloud_Filtered.pcd in CloudCompare to see fragmentation"
echo "2. Check if boundary forms multiple disconnected loops"
echo "3. Compare with sample's boundary for same piece"
echo "4. Try reducing K-nearest neighbor value for better gap bridging"
echo "5. Consider alternative sequencing algorithm for fragmented boundaries"
echo ""
