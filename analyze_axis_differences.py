#!/usr/bin/env python3

import numpy as np

# Axis data: [piece_num, main_pos, main_dir, sample_pos, sample_dir]
axis_data = [
    (1, [-53.70, -131.81, 60.06], [0.216, 0.331, 0.919], 
        [-55.47, -133.90, 62.45], [0.228, 0.332, 0.915]),
    (2, [-107.28, -70.70, 67.06], [0.377, 0.269, 0.886],
        [-106.81, -73.20, 76.26], [0.425, 0.277, 0.862]),
    (3, [56.77, -117.87, 328.90], [-0.106, 0.930, 0.352],
        [89.37, -3.14, 336.49], [-0.966, -0.015, 0.257]),
    (4, [94.30, -64.44, 70.07], [-0.426, 0.304, 0.852],
        [100.35, -62.11, 91.71], [-0.541, 0.291, 0.789]),
    (5, [-192.18, -14.80, 323.36], [0.831, 0.234, 0.505],
        [-211.04, -23.65, 290.01], [0.775, 0.244, 0.584]),
    (6, [-57.77, -33.33, 327.09], [0.985, -0.003, 0.174],
        [-153.45, -55.64, 227.01], [0.809, 0.117, 0.576]),
    (7, [39.04, -26.91, 344.19], [0.344, -0.932, -0.112],
        [15.79, 25.68, 368.89], [0.072, 0.995, -0.072]),
    (8, [218.41, 47.01, 959.27], [0.925, 0.306, -0.226],
        [-115.31, -85.41, 135.20], [0.637, 0.277, 0.719])
]

print("=== AXIS DIFFERENCE ANALYSIS ===\n")
print("Piece | Position Diff (X, Y, Z)      | Pos Magnitude | Direction Diff (X, Y, Z)    | Dir Magnitude")
print("------|------------------------------|---------------|------------------------------|---------------")

large_differences = []

for piece, main_pos, main_dir, sample_pos, sample_dir in axis_data:
    pos_diff = np.array(main_pos) - np.array(sample_pos)
    dir_diff = np.array(main_dir) - np.array(sample_dir)
    
    pos_mag = np.linalg.norm(pos_diff)
    dir_mag = np.linalg.norm(dir_diff)
    
    print(f"  {piece:2d}  | [{pos_diff[0]:6.1f}, {pos_diff[1]:6.1f}, {pos_diff[2]:6.1f}] | {pos_mag:8.1f}      | [{dir_diff[0]:6.3f}, {dir_diff[1]:6.3f}, {dir_diff[2]:6.3f}] | {dir_mag:8.3f}")
    
    if pos_mag > 50 or dir_mag > 0.5:
        large_differences.append((piece, pos_mag, dir_mag))

print(f"\n=== LARGE DIFFERENCE ANALYSIS ===")
print(f"Pieces with significant differences (>50 units position or >0.5 direction):")
for piece, pos_mag, dir_mag in large_differences:
    print(f"  Piece {piece:2d}: Position {pos_mag:6.1f} units, Direction {dir_mag:.3f}")

print(f"\n=== Z-COORDINATE ANALYSIS ===")
print("Piece | Main Z  | Sample Z | Diff    | Analysis")
print("------|---------|----------|---------|----------------------------------")

for piece, main_pos, main_dir, sample_pos, sample_dir in axis_data:
    z_diff = main_pos[2] - sample_pos[2]
    z_ratio = main_pos[2] / sample_pos[2] if sample_pos[2] != 0 else float('inf')
    
    analysis = ""
    if abs(z_diff) < 10:
        analysis = "✅ Similar"
    elif abs(z_diff) < 100:
        analysis = "🟡 Moderate difference"
    else:
        analysis = "🔴 Large difference"
    
    print(f"  {piece:2d}  | {main_pos[2]:7.1f} | {sample_pos[2]:8.1f} | {z_diff:7.1f} | {analysis}")

print(f"\n=== COORDINATE SYSTEM ISSUES ===")
print("Potential issues identified:")
print("1. Pieces 3, 6, 7, 8: Large position differences (>100 units)")
print("2. Pieces 3, 6, 7, 8: Large direction differences (>0.5)")  
print("3. Z-coordinate inconsistencies suggest different coordinate origins")
print("4. Direction vector sign flips in pieces 3, 7 suggest axis orientation issues")