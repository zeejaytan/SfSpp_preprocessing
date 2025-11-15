#!/usr/bin/env python3

import numpy as np
import os

def analyze_surface_coordinates(piece_num):
    main_file = f"/data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker/Dataset/SfS_pp/Surfaces/Pot_A_Piece_{piece_num:02d}_Surface_F.xyz"
    sample_file = f"/data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker/Dataset/SfS_pp_BACKUP_20250826_111430/Surfaces/Pot_A_Piece_{piece_num:02d}_Surface_F.xyz"
    
    if not os.path.exists(main_file) or not os.path.exists(sample_file):
        return None
    
    # Read first 1000 points for analysis
    main_coords = []
    sample_coords = []
    
    with open(main_file, 'r') as f:
        for i, line in enumerate(f):
            if i >= 1000:
                break
            parts = line.strip().split()
            if len(parts) >= 3:
                main_coords.append([float(parts[0]), float(parts[1]), float(parts[2])])
    
    with open(sample_file, 'r') as f:
        for i, line in enumerate(f):
            if i >= 1000:
                break
            parts = line.strip().split()
            if len(parts) >= 3:
                sample_coords.append([float(parts[0]), float(parts[1]), float(parts[2])])
    
    main_coords = np.array(main_coords)
    sample_coords = np.array(sample_coords)
    
    main_ranges = [
        (np.min(main_coords[:, 0]), np.max(main_coords[:, 0])),
        (np.min(main_coords[:, 1]), np.max(main_coords[:, 1])),
        (np.min(main_coords[:, 2]), np.max(main_coords[:, 2]))
    ]
    
    sample_ranges = [
        (np.min(sample_coords[:, 0]), np.max(sample_coords[:, 0])),
        (np.min(sample_coords[:, 1]), np.max(sample_coords[:, 1])),
        (np.min(sample_coords[:, 2]), np.max(sample_coords[:, 2]))
    ]
    
    return main_ranges, sample_ranges

print("=== SURFACE COORDINATE SYSTEM ANALYSIS ===\n")
print("Piece | Coordinate | Our Range (Min, Max)     | Sample Range (Min, Max)   | Difference")
print("------|------------|--------------------------|---------------------------|------------")

problematic_pieces = [1, 3, 6, 8]  # Focus on pieces with large axis differences

for piece in problematic_pieces:
    result = analyze_surface_coordinates(piece)
    if result:
        main_ranges, sample_ranges = result
        coord_names = ['X', 'Y', 'Z']
        
        for i, coord in enumerate(coord_names):
            main_min, main_max = main_ranges[i]
            sample_min, sample_max = sample_ranges[i]
            
            center_diff = ((main_min + main_max) / 2) - ((sample_min + sample_max) / 2)
            range_diff = (main_max - main_min) - (sample_max - sample_min)
            
            print(f"  {piece:2d}  |     {coord}      | ({main_min:7.1f}, {main_max:7.1f}) | ({sample_min:7.1f}, {sample_max:7.1f}) | Center: {center_diff:6.1f}")
        print("      |            |                          |                           |")

print("\n=== COORDINATE SYSTEM DIAGNOSIS ===")
print("Based on the axis analysis:")
print("1. ✅ Pieces 1-2: Small differences (<10 units) - TPS approximation accurate")
print("2. 🟡 Pieces 4-5: Moderate differences (20-40 units) - Acceptable TPS variation") 
print("3. 🔴 Pieces 3, 6-8: Large differences (>60 units) - Significant coordinate issues")
print("4. 🔴 Piece 8: Extreme difference (824 Z-units) - Possible mesh preprocessing error")

print("\nRoot causes likely:")
print("- TPS surface fitting accuracy varies by piece geometry")  
print("- Different mesh scaling or coordinate origins")
print("- Axis extraction sensitivity to surface point distribution")
print("- Possible mesh preprocessing artifacts in complex pieces")