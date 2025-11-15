#!/usr/bin/env python3
"""
Add segment headers to existing PCD breakline files for SFS compatibility
"""
import os
import sys

def add_segment_headers_to_pcd(input_file, output_file, num_segments=4):
    """
    Add segment headers to a PCD file based on point distribution
    """
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    # Find the data section
    data_start = None
    width = None
    for i, line in enumerate(lines):
        if line.startswith('WIDTH'):
            width = int(line.split()[1])
        elif line.startswith('DATA ascii'):
            data_start = i + 1
            break
    
    if data_start is None or width is None:
        print(f"Error: Could not parse PCD file {input_file}")
        return False
    
    # Calculate segment ranges
    points_per_segment = width // num_segments
    remainder = width % num_segments
    
    segment_ranges = []
    start_idx = 1  # PCD uses 1-based indexing
    
    for i in range(num_segments):
        segment_size = points_per_segment
        if i < remainder:  # Distribute remainder points
            segment_size += 1
        
        end_idx = start_idx + segment_size - 1
        segment_ranges.append((start_idx, end_idx))
        start_idx = end_idx + 1
    
    # Create output with segment headers
    with open(output_file, 'w') as f:
        # Write PCD header
        f.write("# .PCD v0.7 - Point Cloud Data file format\n")
        f.write(f"# {num_segments} {width} 0\n")
        
        # Write segment ranges
        for start, end in segment_ranges:
            f.write(f"# {start} {end} 0\n")
        
        # Write the rest of the original file (skipping the first comment line)
        for i, line in enumerate(lines):
            if i > 0:  # Skip the first comment line
                f.write(line)
    
    print(f"Added {num_segments} segment headers to {output_file}")
    return True

def main():
    # Process all breakline files in the dataset
    base_dir = "/data/gpfs/projects/punim2657/sfs_preprocessing/NURBS_Dataset_20250904_ProperCurvature/SfS_pp/Breaklines"
    
    if not os.path.exists(base_dir):
        print(f"Error: Directory {base_dir} does not exist")
        return 1
    
    processed = 0
    for filename in os.listdir(base_dir):
        if filename.endswith('.pcd') and 'Breakline' in filename:
            input_path = os.path.join(base_dir, filename)
            output_path = input_path  # Overwrite the original
            
            if add_segment_headers_to_pcd(input_path, output_path):
                processed += 1
    
    print(f"\nProcessed {processed} breakline PCD files with segment headers")
    return 0

if __name__ == "__main__":
    sys.exit(main())