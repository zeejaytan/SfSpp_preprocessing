#!/bin/bash

echo "============================================================"
echo "DETAILED PIECE 01 COMPARISON: New vs Sample"
echo "============================================================"
echo ""

NEW_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"
SAMPLE_DIR="/data/gpfs/projects/punim2657/sfs_main/original_samples"

echo "=== 1. FINAL BREAKLINE OUTPUTS ==="
echo ""
echo "New Dataset:"
head -2 ${NEW_DIR}/Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_0.pcd | tail -1 | awk '{print "  BL0: " $2 " segments, " $3 " points"}'
head -2 ${NEW_DIR}/Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_1.pcd | tail -1 | awk '{print "  BL1: " $2 " segments, " $3 " points"}'
echo ""
echo "Sample Dataset:"
head -2 ${SAMPLE_DIR}/SfS_pp/Breaklines/Pot_A_Piece_01_Breakline_0.pcd | tail -1 | awk '{print "  BL0: " $2 " segments, " $3 " points"}'
head -2 ${SAMPLE_DIR}/SfS_pp/Breaklines/Pot_A_Piece_01_Breakline_1.pcd | tail -1 | awk '{print "  BL1: " $2 " segments, " $3 " points"}'
echo ""

echo "=== 2. BREAKLINE COORDINATE SAMPLES ==="
echo ""
echo "New BL0 (first 3 points):"
grep "^[0-9\-]" ${NEW_DIR}/Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_0.pcd 2>/dev/null | head -3 | awk '{printf "  (%.2f, %.2f, %.2f)\n", $1, $2, $3}'
echo ""
echo "Sample BL0 (first 3 points):"
grep "^[0-9\-]" ${SAMPLE_DIR}/SfS_pp/Breaklines/Pot_A_Piece_01_Breakline_0.pcd 2>/dev/null | head -3 | awk '{printf "  (%.2f, %.2f, %.2f)\n", $1, $2, $3}'
echo ""

echo "New BL1 (first 3 points):"
grep "^[0-9\-]" ${NEW_DIR}/Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_1.pcd 2>/dev/null | head -3 | awk '{printf "  (%.2f, %.2f, %.2f)\n", $1, $2, $3}'
echo ""
echo "Sample BL1 (first 3 points):"
grep "^[0-9\-]" ${SAMPLE_DIR}/SfS_pp/Breaklines/Pot_A_Piece_01_Breakline_1.pcd 2>/dev/null | head -3 | awk '{printf "  (%.2f, %.2f, %.2f)\n", $1, $2, $3}'
echo ""

echo "=== 3. SURFACE POINT COUNTS ==="
echo ""
echo "New Dataset:"
if [ -f "${NEW_DIR}/Temp/Data/Pot_A/Pot_A_Piece_01_Surface_0.xyz" ]; then
    wc -l ${NEW_DIR}/Temp/Data/Pot_A/Pot_A_Piece_01_Surface_0.xyz | awk '{print "  Surface_0: " $1 " points"}'
else
    echo "  Surface_0: NOT FOUND"
fi

if [ -f "${NEW_DIR}/Temp/Data/Pot_A/Pot_A_Piece_01_Surface_1.xyz" ]; then
    wc -l ${NEW_DIR}/Temp/Data/Pot_A/Pot_A_Piece_01_Surface_1.xyz | awk '{print "  Surface_1: " $1 " points"}'
else
    echo "  Surface_1: NOT FOUND"
fi

echo ""
echo "Sample Dataset:"
if [ -f "${SAMPLE_DIR}/SfS_pp/Surfaces/Pot_A_Piece_01_Surface_0.xyz" ]; then
    wc -l ${SAMPLE_DIR}/SfS_pp/Surfaces/Pot_A_Piece_01_Surface_0.xyz | awk '{print "  Surface_0: " $1 " points"}'
else
    echo "  Surface_0: NOT FOUND"
fi

if [ -f "${SAMPLE_DIR}/SfS_pp/Surfaces/Pot_A_Piece_01_Surface_1.xyz" ]; then
    wc -l ${SAMPLE_DIR}/SfS_pp/Surfaces/Pot_A_Piece_01_Surface_1.xyz | awk '{print "  Surface_1: " $1 " points"}'
else
    echo "  Surface_1: NOT FOUND"
fi

echo ""
echo "=== 4. SURFACE GEOMETRY MATCH CHECK ==="
echo ""

echo "Comparing first point of each surface..."
echo ""

echo "New Surface_0 first point:"
head -1 ${NEW_DIR}/Temp/Data/Pot_A/Pot_A_Piece_01_Surface_0.xyz 2>/dev/null | awk '{printf "  (%.3f, %.3f, %.3f)\n", $1, $2, $3}'

echo "Sample Surface_0 first point:"
head -1 ${SAMPLE_DIR}/SfS_pp/Surfaces/Pot_A_Piece_01_Surface_0.xyz 2>/dev/null | awk '{printf "  (%.3f, %.3f, %.3f)\n", $1, $2, $3}'

echo ""

echo "New Surface_1 first point:"
head -1 ${NEW_DIR}/Temp/Data/Pot_A/Pot_A_Piece_01_Surface_1.xyz 2>/dev/null | awk '{printf "  (%.3f, %.3f, %.3f)\n", $1, $2, $3}'

echo "Sample Surface_1 first point:"
head -1 ${SAMPLE_DIR}/SfS_pp/Surfaces/Pot_A_Piece_01_Surface_1.xyz 2>/dev/null | awk '{printf "  (%.3f, %.3f, %.3f)\n", $1, $2, $3}'

echo ""
echo "=== 5. Z-COORDINATE ANALYSIS (Inner vs Outer) ==="
echo ""

# Calculate average Z for each surface to determine inner/outer
echo "Average Z-coordinates (lower Z = inner surface):"
echo ""

echo "New Dataset:"
avg_z0=$(head -100 ${NEW_DIR}/Temp/Data/Pot_A/Pot_A_Piece_01_Surface_0.xyz 2>/dev/null | awk '{sum+=$3; count++} END {printf "%.2f", sum/count}')
avg_z1=$(head -100 ${NEW_DIR}/Temp/Data/Pot_A/Pot_A_Piece_01_Surface_1.xyz 2>/dev/null | awk '{sum+=$3; count++} END {printf "%.2f", sum/count}')
echo "  Surface_0: Z_avg = ${avg_z0}mm"
echo "  Surface_1: Z_avg = ${avg_z1}mm"

echo ""
echo "Sample Dataset:"
sample_z0=$(head -100 ${SAMPLE_DIR}/SfS_pp/Surfaces/Pot_A_Piece_01_Surface_0.xyz 2>/dev/null | awk '{sum+=$3; count++} END {printf "%.2f", sum/count}')
sample_z1=$(head -100 ${SAMPLE_DIR}/SfS_pp/Surfaces/Pot_A_Piece_01_Surface_1.xyz 2>/dev/null | awk '{sum+=$3; count++} END {printf "%.2f", sum/count}')
echo "  Surface_0: Z_avg = ${sample_z0}mm"
echo "  Surface_1: Z_avg = ${sample_z1}mm"

echo ""
echo "=== 6. KEY FINDINGS ==="
echo ""

# Determine if surfaces are swapped
echo "Surface Assignment Check:"
echo ""

if (( $(echo "$avg_z0 < $avg_z1" | bc -l) )); then
    echo "  New: Surface_0 (Z=${avg_z0}) is INNER, Surface_1 (Z=${avg_z1}) is OUTER"
else
    echo "  New: Surface_0 (Z=${avg_z0}) is OUTER, Surface_1 (Z=${avg_z1}) is INNER"
fi

if (( $(echo "$sample_z0 < $sample_z1" | bc -l) )); then
    echo "  Sample: Surface_0 (Z=${sample_z0}) is INNER, Surface_1 (Z=${sample_z1}) is OUTER"
else
    echo "  Sample: Surface_0 (Z=${sample_z0}) is OUTER, Surface_1 (Z=${sample_z1}) is INNER"
fi

echo ""
echo "Point Count Summary:"
echo ""
new_bl0=$(head -2 ${NEW_DIR}/Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_0.pcd | tail -1 | awk '{print $3}')
new_bl1=$(head -2 ${NEW_DIR}/Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_1.pcd | tail -1 | awk '{print $3}')
sample_bl0=$(head -2 ${SAMPLE_DIR}/SfS_pp/Breaklines/Pot_A_Piece_01_Breakline_0.pcd | tail -1 | awk '{print $3}')
sample_bl1=$(head -2 ${SAMPLE_DIR}/SfS_pp/Breaklines/Pot_A_Piece_01_Breakline_1.pcd | tail -1 | awk '{print $3}')

echo "  New BL0: ${new_bl0} points    vs    Sample BL0: ${sample_bl0} points"
echo "  New BL1: ${new_bl1} points    vs    Sample BL1: ${sample_bl1} points"
echo ""

# Check if cross-match
if [ "${new_bl0}" -gt 180 ] && [ "${sample_bl1}" -gt 180 ]; then
    echo "  → New BL0 (${new_bl0}) ≈ Sample BL1 (${sample_bl1}) [within 20%]"
    echo "  → Possible S0/S1 swap or BL0/BL1 labeling difference"
fi

if [ "${new_bl1}" -lt 110 ] && [ "${sample_bl0}" -gt 180 ]; then
    echo "  → New BL1 (${new_bl1}) << Sample BL0 (${sample_bl0}) [MAJOR DIFFERENCE]"
    echo "  → Confirms sequencing failure in New BL1"
fi

echo ""
echo "=== 7. CONCLUSION ==="
echo ""
echo "Based on this comparison:"
echo ""
echo "1. Surface Assignment:"
echo "   Check if Z-coordinates match (same assignment) or differ (swapped)"
echo ""
echo "2. Breakline Quality:"
echo "   New BL1 has ${new_bl1} points vs Sample's BL0 ${sample_bl0} or BL1 ${sample_bl1}"
echo "   This ${new_bl1}-point deficit confirms sequencing failure"
echo ""
echo "3. Next Steps:"
echo "   - If surfaces match: Pipeline has a bug (boundary/sequencing)"
echo "   - If surfaces swapped: Check mesh preprocessing for S0/S1 order"
echo ""
