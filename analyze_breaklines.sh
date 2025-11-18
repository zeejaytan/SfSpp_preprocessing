#!/bin/bash

echo "========== BREAKLINE SEGMENTATION ANALYSIS =========="
echo "Generated: $(date)"
echo ""

SAMPLE_BASE="/data/gpfs/projects/punim2657/sfs_preprocessing/NURBS_Dataset_20251103/SfS_pp"
NEW_BASE="/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset"

echo "========== SAMPLE DATASET BREAKLINES =========="
echo ""
echo "File | Points | Size"
echo "---|---|---"
for f in $SAMPLE_BASE/Breaklines/Pot_A_Piece_*_Breakline_*.pcd; do
    if [ -f "$f" ]; then
        name=$(basename "$f")
        # Extract POINTS count from PCD header
        pts=$(grep "^POINTS " "$f" | awk '{print $2}')
        size=$(ls -lh "$f" | awk '{print $5}')
        printf "%-50s | %7s | %7s\n" "$name" "$pts" "$size"
    fi
done | sort

echo ""
echo "========== NEW DATASET BREAKLINES =========="
echo ""
echo "File | Points | Size"
echo "---|---|---"
for f in $NEW_BASE/Breaklines/Pot_A/Pot_A_Piece_*_Breakline_*.pcd; do
    if [ -f "$f" ]; then
        name=$(basename "$f")
        # Extract POINTS count from PCD header
        pts=$(grep "^POINTS " "$f" | awk '{print $2}')
        size=$(ls -lh "$f" | awk '{print $5}')
        printf "%-50s | %7s | %7s\n" "$name" "$pts" "$size"
    fi
done | sort

echo ""
echo "========== STATISTICAL COMPARISON =========="
echo ""

# Calculate sample stats
sample_total=0
sample_count=0
sample_min=999999
sample_max=0
for f in $SAMPLE_BASE/Breaklines/Pot_A_Piece_*_Breakline_*.pcd; do
    if [ -f "$f" ]; then
        pts=$(grep "^POINTS " "$f" | awk '{print $2}')
        sample_total=$((sample_total + pts))
        sample_count=$((sample_count + 1))
        [ $pts -lt $sample_min ] && sample_min=$pts
        [ $pts -gt $sample_max ] && sample_max=$pts
    fi
done

sample_avg=$((sample_total / sample_count))

# Calculate new dataset stats
new_total=0
new_count=0
new_min=999999
new_max=0
for f in $NEW_BASE/Breaklines/Pot_A/Pot_A_Piece_*_Breakline_*.pcd; do
    if [ -f "$f" ]; then
        pts=$(grep "^POINTS " "$f" | awk '{print $2}')
        new_total=$((new_total + pts))
        new_count=$((new_count + 1))
        [ $pts -lt $new_min ] && new_min=$pts
        [ $pts -gt $new_max ] && new_max=$pts
    fi
done

new_avg=$((new_total / new_count))

echo "Sample Dataset:"
echo "  Total breakline points: $sample_total"
echo "  Average per breakline: $sample_avg"
echo "  Min: $sample_min"
echo "  Max: $sample_max"
echo "  Breakline files: $sample_count"
echo ""
echo "New Dataset:"
echo "  Total breakline points: $new_total"
echo "  Average per breakline: $new_avg"
echo "  Min: $new_min"
echo "  Max: $new_max"
echo "  Breakline files: $new_count"
echo ""

if [ $new_count -eq $sample_count ]; then
    echo "✓ Breakline file count matches ($new_count files)"
    diff=$((new_avg - sample_avg))
    pct=$(( (diff * 100) / sample_avg ))
    echo "  Average point difference: $diff points ($pct%)"
else
    echo "✗ Breakline file count mismatch: sample=$sample_count, new=$new_count"
fi

echo ""
echo "Analysis complete: $(date)"
