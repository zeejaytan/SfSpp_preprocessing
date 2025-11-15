#!/usr/bin/env python3

import os
import glob
import math

def add_segment_headers_to_breakline(input_file, output_file):
    """
    Add segment headers to NURBS breakline PCD files to match SFS expected format.
    
    The SFS system expects segment headers like:
    # {segment_count} {total_points} {flag}
    # {start_point} {end_point} {flag}
    
    Generate proper multi-segment structure matching original sample format.
    """
    
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    # Find the POINTS line to get point count
    points_count = 0
    width_count = 0
    for line in lines:
        if line.startswith('POINTS '):
            points_count = int(line.split()[1])
        if line.startswith('WIDTH '):
            width_count = int(line.split()[1])
    
    # Use POINTS count as the reliable source
    total_points = points_count if points_count > 0 else width_count
    
    if total_points == 0:
        print(f"Warning: Could not determine point count for {input_file}")
        return False
    
    # Find where to insert segment headers (after first PCD header line)
    insert_index = 1  # After "# .PCD v0.7 - Point Cloud Data file format"
    
    # Calculate proper segmentation (matching edgeline_extraction.cpp logic)
    num_segments = min(5, max(1, total_points // 50))
    points_per_segment = total_points // num_segments
    
    # Create segment headers with proper multi-segment structure
    segment_headers = [f"# {num_segments} {total_points} 0\n"]
    
    # Add individual segment range headers
    for seg in range(num_segments):
        start_idx = seg * points_per_segment + 1  # 1-based indexing
        end_idx = total_points if seg == num_segments - 1 else (seg + 1) * points_per_segment
        segment_headers.append(f"# {start_idx} {end_idx} 0\n")
    
    # Insert segment headers
    new_lines = lines[:insert_index] + segment_headers + lines[insert_index:]
    
    # Write to output file
    with open(output_file, 'w') as f:
        f.writelines(new_lines)
    
    print(f"✅ Added {num_segments}-segment headers to {os.path.basename(output_file)} ({total_points} points)")
    return True

def main():
    # Path to NURBS breakline files
    nurbs_breaklines_dir = "/data/gpfs/projects/punim2657/sfs_preprocessing/NURBS_Dataset_20250903/SfS_pp/Breaklines/"
    
    # Find all breakline PCD files
    breakline_files = glob.glob(os.path.join(nurbs_breaklines_dir, "Pot_A_Piece_*_Breakline_*.pcd"))
    
    if not breakline_files:
        print("No NURBS breakline files found!")
        return
    
    print(f"Found {len(breakline_files)} NURBS breakline files to fix")
    
    success_count = 0
    for breakline_file in sorted(breakline_files):
        print(f"Processing {os.path.basename(breakline_file)}...")
        
        # Create backup
        backup_file = breakline_file + ".backup"
        if not os.path.exists(backup_file):
            os.rename(breakline_file, backup_file)
            print(f"  Created backup: {os.path.basename(backup_file)}")
        
        # Process the backup file and write to original location
        if add_segment_headers_to_breakline(backup_file, breakline_file):
            success_count += 1
    
    print(f"\n✅ Successfully processed {success_count}/{len(breakline_files)} breakline files")
    print("Added segment headers to make NURBS breaklines compatible with SFS system")

if __name__ == "__main__":
    main()