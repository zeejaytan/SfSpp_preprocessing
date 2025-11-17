#!/bin/bash
echo "=== COMPREHENSIVE DATASET COMPARISON ==="
echo ""
echo "## 1. Point Counts in Breaklines ##"
echo ""
printf "%-25s %10s %10s %10s\n" "File" "Our" "Sample" "Diff"
printf "%-25s %10s %10s %10s\n" "----" "---" "------" "----"

for piece in 01 02 03 04 05 06 07 08; do
  for surf in 0 1; do
    file="Pot_A_Piece_${piece}_Breakline_${surf}"
    our_count=$(grep "^POINTS" Dataset/Breaklines/Pot_A/${file}.pcd 2>/dev/null | awk '{print $2}')
    sample_count=$(grep "^POINTS" /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines/${file}.pcd 2>/dev/null | awk '{print $2}')
    
    if [ -n "$our_count" ] && [ -n "$sample_count" ]; then
      diff=$((our_count - sample_count))
      printf "%-25s %10s %10s %10s\n" "$file" "$our_count" "$sample_count" "$diff"
    fi
  done
done

echo ""
echo "## 2. Segment Counts in Breaklines ##"
echo ""
printf "%-25s %10s %10s\n" "File" "Our" "Sample"
printf "%-25s %10s %10s\n" "----" "---" "------"

for piece in 01 02 03 04 05 06 07 08; do
  for surf in 0 1; do
    file="Pot_A_Piece_${piece}_Breakline_${surf}"
    our_segs=$(head -20 Dataset/Breaklines/Pot_A/${file}.pcd 2>/dev/null | grep "^# [0-9]" | wc -l)
    sample_segs=$(head -20 /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines/${file}.pcd 2>/dev/null | grep "^# [0-9]" | wc -l)
    
    if [ "$our_segs" -gt 0 ] || [ "$sample_segs" -gt 0 ]; then
      printf "%-25s %10s %10s\n" "$file" "$our_segs" "$sample_segs"
    fi
  done
done

echo ""
echo "## 3. Surface Point Counts ##"
echo ""
printf "%-30s %10s %10s %10s\n" "File" "Our" "Sample" "Diff"
printf "%-30s %10s %10s %10s\n" "----" "---" "------" "----"

for piece in 01 02 03 04 05 06 07 08; do
  for surf in 0 1; do
    file="Pot_A_Piece_${piece}_Surface_${surf}"
    our_count=$(wc -l < Dataset/Surfaces/Pot_A/${file}.xyz 2>/dev/null)
    sample_count=$(wc -l < /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Surfaces/${file}.xyz 2>/dev/null)
    
    if [ -n "$our_count" ] && [ -n "$sample_count" ]; then
      diff=$((our_count - sample_count))
      ratio=$(awk "BEGIN {printf \"%.2f\", $sample_count/$our_count}")
      printf "%-30s %10s %10s %10s (%.2fx)\n" "$file" "$our_count" "$sample_count" "$diff" "$ratio"
    fi
  done
done
