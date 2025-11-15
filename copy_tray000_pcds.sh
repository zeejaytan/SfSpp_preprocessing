#!/bin/bash
# Copy Tray-000 CloudCompare PCDs to NURBS preprocessing Pot_A location

for i in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40; do
    cp "Tray-000_Dataset_20251021/SfS_pp/Point/Tray-000_Piece_${i}_Point.pcd" \
       "original_nurbs_preprocessing/Dataset/Point/Pot_A/Pot_A_Piece_${i}_Point.pcd"
    echo "Copied piece ${i}"
done

echo "All 40 PCDs copied successfully"
ls original_nurbs_preprocessing/Dataset/Point/Pot_A/*.pcd | wc -l
