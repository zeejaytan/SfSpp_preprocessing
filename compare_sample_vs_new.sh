#!/bin/bash

SAMPLE_DIR="/data/gpfs/projects/punim2657/sfs_main/original_samples_backup/SfS_pp"
NEW_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset"

echo "=========================================="
echo "SAMPLE vs NEW DATASET COMPARISON"
echo "=========================================="
echo ""
echo "Sample dataset: $SAMPLE_DIR"
echo "New dataset:    $NEW_DIR"
echo ""

# Function to count points in XYZ file
count_xyz_points() {
    wc -l < "$1" 2>/dev/null || echo "0"
}

# Function to count points in PCD file
count_pcd_points() {
    grep "^POINTS " "$1" 2>/dev/null | awk '{print $2}' || echo "0"
}

# Function to get segments from PCD
get_pcd_segments() {
    head -3 "$1" 2>/dev/null | tail -1 | awk '{print $2}' || echo "0"
}

echo "========== SURFACES COMPARISON =========="
echo ""
echo "Pot A Surfaces (Piece 01-08):"
echo ""
printf "%-20s %15s %15s %15s\n" "Surface" "Sample Points" "New Points" "Ratio"
printf "%-20s %15s %15s %15s\n" "--------------------" "---------------" "---------------" "---------------"

total_sample_surf=0
total_new_surf=0
count_surf=0

for piece in 01 02 03 04 05 06 07 08; do
    for surf in 0 1; do
        sample_file="${SAMPLE_DIR}/Surfaces/Pot_A_Piece_${piece}_Surface_${surf}.xyz"
        new_file="${NEW_DIR}/Surfaces/Pot_A/Pot_A_Piece_${piece}_Surface_${surf}.xyz"
        
        if [ -f "$sample_file" ] && [ -f "$new_file" ]; then
            sample_pts=$(count_xyz_points "$sample_file")
            new_pts=$(count_xyz_points "$new_file")
            
            total_sample_surf=$((total_sample_surf + sample_pts))
            total_new_surf=$((total_new_surf + new_pts))
            count_surf=$((count_surf + 1))
            
            ratio=$(echo "scale=2; $new_pts / $sample_pts" | bc)
            printf "%-20s %15s %15s %15s\n" "Piece_${piece}_S${surf}" "$sample_pts" "$new_pts" "${ratio}×"
        fi
    done
done

echo ""
avg_sample_surf=$((total_sample_surf / count_surf))
avg_new_surf=$((total_new_surf / count_surf))
ratio_avg=$(echo "scale=2; $avg_new_surf / $avg_sample_surf" | bc)

echo "Total points:        $(printf '%15s %15s %15s' "$total_sample_surf" "$total_new_surf" "${ratio_avg}×")"
echo "Average per surface: $(printf '%15s %15s' "$avg_sample_surf" "$avg_new_surf")"
echo ""

echo "========== BREAKLINES COMPARISON =========="
echo ""
echo "Pot A Breaklines (Piece 01-08):"
echo ""
printf "%-20s %12s %12s %8s %12s %12s %8s\n" "Breakline" "Sample Pts" "Sample Seg" "Ratio" "New Pts" "New Seg" "Ratio"
printf "%-20s %12s %12s %8s %12s %12s %8s\n" "--------------------" "------------" "------------" "--------" "------------" "------------" "--------"

total_sample_break=0
total_new_break=0
count_break=0
min_sample=999999
max_sample=0
min_new=999999
max_new=0

for piece in 01 02 03 04 05 06 07 08; do
    for b in 0 1; do
        sample_file="${SAMPLE_DIR}/Breaklines/Pot_A_Piece_${piece}_Breakline_${b}.pcd"
        new_file="${NEW_DIR}/Breaklines/Pot_A/Pot_A_Piece_${piece}_Breakline_${b}.pcd"
        
        if [ -f "$sample_file" ] && [ -f "$new_file" ]; then
            sample_pts=$(count_pcd_points "$sample_file")
            sample_seg=$(get_pcd_segments "$sample_file")
            new_pts=$(count_pcd_points "$new_file")
            new_seg=$(get_pcd_segments "$new_file")
            
            total_sample_break=$((total_sample_break + sample_pts))
            total_new_break=$((total_new_break + new_pts))
            count_break=$((count_break + 1))
            
            if [ $sample_pts -lt $min_sample ]; then min_sample=$sample_pts; fi
            if [ $sample_pts -gt $max_sample ]; then max_sample=$sample_pts; fi
            if [ $new_pts -lt $min_new ]; then min_new=$new_pts; fi
            if [ $new_pts -gt $max_new ]; then max_new=$new_pts; fi
            
            ratio=$(echo "scale=2; $new_pts / $sample_pts" | bc)
            printf "%-20s %12s %12s %8s %12s %12s %8s\n" "Piece_${piece}_B${b}" "$sample_pts" "$sample_seg" "${ratio}×" "$new_pts" "$new_seg" ""
        fi
    done
done

echo ""
avg_sample_break=$((total_sample_break / count_break))
avg_new_break=$((total_new_break / count_break))
ratio_break=$(echo "scale=2; $avg_new_break / $avg_sample_break" | bc)

echo "Total points:          $(printf '%12s %34s' "$total_sample_break" "$total_new_break")"
echo "Average per breakline: $(printf '%12s %34s' "$avg_sample_break" "$avg_new_break")"
echo "Range:                 $(printf '%12s %34s' "$min_sample-$max_sample" "$min_new-$max_new")"
echo "Overall ratio:         $(printf '%46s' "${ratio_break}×")"
echo ""

echo "========== AXES COMPARISON =========="
echo ""
echo "Pot A Axes (Piece 01-08):"
echo ""

sample_axes_count=0
new_axes_count=0

for piece in 01 02 03 04 05 06 07 08; do
    sample_file="${SAMPLE_DIR}/Axes/Pot_A_Piece_${piece}_Axis.xyz"
    new_file="${NEW_DIR}/Axes/Pot_A_Piece_${piece}_Axis.txt"
    
    sample_exists="✗"
    new_exists="✗"
    
    if [ -f "$sample_file" ]; then
        sample_exists="✓"
        sample_axes_count=$((sample_axes_count + 1))
    fi
    
    if [ -f "$new_file" ]; then
        new_exists="✓"
        new_axes_count=$((new_axes_count + 1))
    fi
    
    echo "Piece_${piece}: Sample=$sample_exists  New=$new_exists"
done

echo ""
echo "Total axes: Sample=$sample_axes_count/8  New=$new_axes_count/8"
echo ""

echo "========== COORDINATE SCALE COMPARISON =========="
echo ""
echo "Checking coordinate ranges..."
echo ""

sample_surf="${SAMPLE_DIR}/Surfaces/Pot_A_Piece_01_Surface_0.xyz"
new_surf="${NEW_DIR}/Surfaces/Pot_A/Pot_A_Piece_01_Surface_0.xyz"

if [ -f "$sample_surf" ]; then
    echo "Sample (Piece_01_Surface_0):"
    head -5 "$sample_surf"
    echo ""
fi

if [ -f "$new_surf" ]; then
    echo "New (Piece_01_Surface_0):"
    head -5 "$new_surf"
    echo ""
fi

echo "=========================================="
