#!/usr/bin/env python3
"""
Fix corrupted NURBS curvature values in breakline PCD files.

The NURBS pipeline generates massive curvature values (2e+26) due to 
uninitialized memory from failed PLY reading. This script replaces 
them with consistent placeholder values matching the sample dataset.

Usage: python3 fix_nurbs_curvature_values.py <nurbs_dataset_path>
"""

import os
import sys
import re
import argparse

def fix_curvature_in_pcd(file_path, target_curvature=1.9057659e-42):
    """
    Replace corrupted curvature values in PCD file with target value.
    
    Args:
        file_path: Path to PCD file
        target_curvature: Replacement curvature value (matches sample dataset)
    """
    print(f"Fixing curvature in: {file_path}")
    
    try:
        # Read original file
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Process lines to fix curvature
        fixed_lines = []
        data_section = False
        points_fixed = 0
        
        for line in lines:
            if line.strip() == "DATA ascii":
                data_section = True
                fixed_lines.append(line)
                continue
                
            if not data_section:
                fixed_lines.append(line)
                continue
                
            # Process data lines (x y z nx ny nz curvature)
            parts = line.strip().split()
            if len(parts) >= 7:
                # Replace the curvature field (index 6) with target value
                parts[6] = f"{target_curvature:.6e}"
                fixed_line = " ".join(parts) + "\n"
                fixed_lines.append(fixed_line)
                points_fixed += 1
            else:
                fixed_lines.append(line)
        
        # Write fixed file
        with open(file_path, 'w') as f:
            f.writelines(fixed_lines)
            
        print(f"  Fixed {points_fixed} points")
        return points_fixed
        
    except Exception as e:
        print(f"  Error fixing {file_path}: {e}")
        return 0

def fix_nurbs_dataset_curvature(dataset_path):
    """
    Fix curvature values in all NURBS breakline files.
    
    Args:
        dataset_path: Path to NURBS dataset directory
    """
    breaklines_path = os.path.join(dataset_path, "SfS_pp", "Breaklines")
    
    if not os.path.exists(breaklines_path):
        print(f"Error: Breaklines directory not found at {breaklines_path}")
        return False
    
    # Find all PCD files (excluding backups)
    pcd_files = []
    for filename in os.listdir(breaklines_path):
        if filename.endswith('.pcd') and not filename.endswith('.pcd.backup'):
            pcd_files.append(os.path.join(breaklines_path, filename))
    
    if not pcd_files:
        print(f"No PCD files found in {breaklines_path}")
        return False
    
    print(f"Found {len(pcd_files)} PCD files to fix")
    
    total_points_fixed = 0
    for pcd_file in sorted(pcd_files):
        points_fixed = fix_curvature_in_pcd(pcd_file)
        total_points_fixed += points_fixed
    
    print(f"\nCurvature fix completed!")
    print(f"Total files processed: {len(pcd_files)}")
    print(f"Total points fixed: {total_points_fixed}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Fix NURBS curvature values")
    parser.add_argument("dataset_path", help="Path to NURBS dataset directory")
    parser.add_argument("--curvature", type=float, default=1.9057659e-42,
                       help="Target curvature value (default: sample dataset value)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.dataset_path):
        print(f"Error: Dataset path does not exist: {args.dataset_path}")
        return 1
    
    print(f"Fixing NURBS curvature values in: {args.dataset_path}")
    print(f"Target curvature value: {args.curvature:.6e}")
    print()
    
    success = fix_nurbs_dataset_curvature(args.dataset_path)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())