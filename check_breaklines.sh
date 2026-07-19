#!/bin/bash
echo "========== BREAKLINE DETAILED COMPARISON =========="
echo ""
printf "%-20s %12s %12s %12s %12s\n" "Breakline" "Sample Pts" "Sample Seg" "New Pts" "New Seg"
printf "%-20s %12s %12s %12s %12s\n" "--------------------" "------------" "------------" "------------" "------------"

for piece in 01 02 03 04 05 06 07 08; do
  for b in 0 1; do
    sample="/data/gpfs/projects/punim2657/sfs_main/original_samples_backup/SfS_pp/Breaklines/Pot_A_Piece_${piece}_Breakline_${b}.pcd"
    new="/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Breaklines/Pot_A/Pot_A_Piece_${piece}_Breakline_${b}.pcd"
    
    sample_pts=$(grep "^POINTS " "$sample" 2>/dev/null | awk '{print $2}')
    sample_seg=$(head -3 "$sample" 2>/dev/null | tail -1 | awk '{print $2}')
    new_pts=$(grep "^POINTS " "$new" 2>/dev/null | awk '{print $2}')
    new_seg=$(head -3 "$new" 2>/dev/null | tail -1 | awk '{print $2}')
    
    printf "%-20s %12s %12s %12s %12s\n" "Piece_${piece}_B${b}" "${sample_pts:-MISSING}" "${sample_seg:-?}" "${new_pts:-MISSING}" "${new_seg:-?}"
  done
done
