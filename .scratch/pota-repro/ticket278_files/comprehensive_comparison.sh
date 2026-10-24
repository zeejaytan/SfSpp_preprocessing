#!/bin/bash

NEW_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Breaklines/Pot_A"
SAMPLE_DIR="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines"

echo "=============================================================================="
echo "COMPREHENSIVE COMPARISON: NEW DATASET vs SAMPLE DATASET"
echo "=============================================================================="
echo ""
echo "New Dataset: $NEW_DIR"
echo "Sample Dataset: $SAMPLE_DIR"
echo ""

echo "=============================================================================="
echo "1. FILE FORMAT COMPARISON"
echo "=============================================================================="
echo ""
echo "--- NEW Piece_01_Breakline_0 Header ---"
head -20 "$NEW_DIR/Pot_A_Piece_01_Breakline_0.pcd"
echo ""
echo "--- SAMPLE Piece_01_Breakline_0 Header ---"
head -20 "$SAMPLE_DIR/Pot_A_Piece_01_Breakline_0.pcd"
echo ""

echo "=============================================================================="
echo "2. SEGMENT COUNT COMPARISON (per breakline)"
echo "=============================================================================="
echo ""
printf "%-35s %10s %10s %10s\n" "File" "New" "Sample" "Diff"
printf "%-35s %10s %10s %10s\n" "----" "---" "------" "----"

total_new=0
total_sample=0

for i in 01 02 03 04 05 06 07 08; do
    for b in 0 1; do
        file="Pot_A_Piece_${i}_Breakline_${b}.pcd"

        new_file="$NEW_DIR/$file"
        sample_file="$SAMPLE_DIR/$file"

        if [ -f "$new_file" ]; then
            new_headers=$(grep "^# [0-9]" "$new_file" | wc -l)
            new_segments=$((new_headers - 2))
            [ $new_segments -lt 0 ] && new_segments=0
        else
            new_segments="-"
        fi

        if [ -f "$sample_file" ]; then
            sample_headers=$(grep "^# [0-9]" "$sample_file" | wc -l)
            sample_segments=$((sample_headers - 2))
            [ $sample_segments -lt 0 ] && sample_segments=0
        else
            sample_segments="-"
        fi

        if [ "$new_segments" != "-" ] && [ "$sample_segments" != "-" ]; then
            diff=$((new_segments - sample_segments))
            total_new=$((total_new + new_segments))
            total_sample=$((total_sample + sample_segments))
            [ $diff -gt 0 ] && diff="+$diff"
        else
            diff="-"
        fi

        printf "%-35s %10s %10s %10s\n" "$file" "$new_segments" "$sample_segments" "$diff"
    done
done

echo ""
printf "%-35s %10s %10s %10s\n" "TOTAL" "$total_new" "$total_sample" "$((total_new - total_sample))"
echo ""

echo "=============================================================================="
echo "3. POINT COUNT COMPARISON (per breakline)"
echo "=============================================================================="
echo ""
printf "%-35s %10s %10s %10s\n" "File" "New" "Sample" "Diff"
printf "%-35s %10s %10s %10s\n" "----" "---" "------" "----"

for i in 01 02 03 04 05 06 07 08; do
    for b in 0 1; do
        file="Pot_A_Piece_${i}_Breakline_${b}.pcd"

        new_file="$NEW_DIR/$file"
        sample_file="$SAMPLE_DIR/$file"

        if [ -f "$new_file" ]; then
            new_points=$(grep "^POINTS" "$new_file" | awk '{print $2}')
        else
            new_points="-"
        fi

        if [ -f "$sample_file" ]; then
            sample_points=$(grep "^POINTS" "$sample_file" | awk '{print $2}')
        else
            sample_points="-"
        fi

        if [ "$new_points" != "-" ] && [ "$sample_points" != "-" ]; then
            diff=$((new_points - sample_points))
            [ $diff -gt 0 ] && diff="+$diff"
        else
            diff="-"
        fi

        printf "%-35s %10s %10s %10s\n" "$file" "$new_points" "$sample_points" "$diff"
    done
done
echo ""

echo "=============================================================================="
echo "4. COORDINATE RANGE COMPARISON"
echo "=============================================================================="
echo ""

echo "--- NEW Piece_01_Breakline_0 First 5 points ---"
grep -v "^#" "$NEW_DIR/Pot_A_Piece_01_Breakline_0.pcd" | grep -v "^[A-Z]" | head -5 | awk '{printf "  X=%8.2f Y=%8.2f Z=%8.2f\n", $1, $2, $3}'

echo ""
echo "--- SAMPLE Piece_01_Breakline_0 First 5 points ---"
grep -v "^#" "$SAMPLE_DIR/Pot_A_Piece_01_Breakline_0.pcd" | grep -v "^[A-Z]" | head -5 | awk '{printf "  X=%8.2f Y=%8.2f Z=%8.2f\n", $1, $2, $3}'

echo ""

echo "=============================================================================="
echo "5. SEGMENT HEADER FORMAT COMPARISON"
echo "=============================================================================="
echo ""
echo "--- NEW Segment Headers (Piece_01_BL0) ---"
grep "^# " "$NEW_DIR/Pot_A_Piece_01_Breakline_0.pcd" | head -10

echo ""
echo "--- SAMPLE Segment Headers (Piece_01_BL0) ---"
grep "^# " "$SAMPLE_DIR/Pot_A_Piece_01_Breakline_0.pcd" | head -10

echo ""

echo "=============================================================================="
echo "6. DATA FIELD COMPARISON"
echo "=============================================================================="
echo ""
echo "--- NEW Data Fields ---"
grep "^FIELDS" "$NEW_DIR/Pot_A_Piece_01_Breakline_0.pcd"
grep "^SIZE" "$NEW_DIR/Pot_A_Piece_01_Breakline_0.pcd"
grep "^TYPE" "$NEW_DIR/Pot_A_Piece_01_Breakline_0.pcd"
grep "^COUNT" "$NEW_DIR/Pot_A_Piece_01_Breakline_0.pcd"

echo ""
echo "--- SAMPLE Data Fields ---"
grep "^FIELDS" "$SAMPLE_DIR/Pot_A_Piece_01_Breakline_0.pcd"
grep "^SIZE" "$SAMPLE_DIR/Pot_A_Piece_01_Breakline_0.pcd"
grep "^TYPE" "$SAMPLE_DIR/Pot_A_Piece_01_Breakline_0.pcd"
grep "^COUNT" "$SAMPLE_DIR/Pot_A_Piece_01_Breakline_0.pcd"

echo ""

echo "=============================================================================="
echo "7. SURFACE FILE COMPARISON"
echo "=============================================================================="
echo ""

NEW_SURF="/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Surfaces/Pot_A"
SAMPLE_SURF="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Surfaces"

echo "--- Surface Point Counts ---"
printf "%-35s %10s %10s %10s\n" "File" "New" "Sample" "Diff"
printf "%-35s %10s %10s %10s\n" "----" "---" "------" "----"

for i in 01 02 03 04 05 06 07 08; do
    for s in 0 1; do
        new_file="$NEW_SURF/Pot_A_Piece_${i}_Surface_${s}.xyz"
        sample_file="$SAMPLE_SURF/Pot_A_Piece_${i}_Surface_${s}.xyz"

        if [ -f "$new_file" ]; then
            new_count=$(wc -l < "$new_file")
        else
            new_count="-"
        fi

        if [ -f "$sample_file" ]; then
            sample_count=$(wc -l < "$sample_file")
        else
            sample_count="-"
        fi

        if [ "$new_count" != "-" ] && [ "$sample_count" != "-" ]; then
            diff=$((new_count - sample_count))
            [ $diff -gt 0 ] && diff="+$diff"
        else
            diff="-"
        fi

        printf "%-35s %10s %10s %10s\n" "Piece_${i}_Surface_${s}.xyz" "$new_count" "$sample_count" "$diff"
    done
done

echo ""

echo "=============================================================================="
echo "8. FIRST POINT COORDINATE COMPARISON (SURFACES)"
echo "=============================================================================="
echo ""
echo "Comparing first point of each surface file:"
echo ""

for i in 01; do
    for s in 0 1; do
        new_file="$NEW_SURF/Pot_A_Piece_${i}_Surface_${s}.xyz"
        sample_file="$SAMPLE_SURF/Pot_A_Piece_${i}_Surface_${s}.xyz"

        echo "Piece_${i}_Surface_${s}:"
        if [ -f "$new_file" ]; then
            echo "  NEW:    $(head -1 "$new_file" | awk '{printf "X=%8.2f Y=%8.2f Z=%8.2f", $1, $2, $3}')"
        else
            echo "  NEW:    (file not found)"
        fi
        if [ -f "$sample_file" ]; then
            echo "  SAMPLE: $(head -1 "$sample_file" | awk '{printf "X=%8.2f Y=%8.2f Z=%8.2f", $1, $2, $3}')"
        else
            echo "  SAMPLE: (file not found)"
        fi
        echo ""
    done
done

echo "=============================================================================="
echo "END OF COMPARISON"
echo "=============================================================================="
