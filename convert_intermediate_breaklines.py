#!/usr/bin/env python3
"""
Convert intermediate breakline files to final SFS-compatible format.
Converts from *_IntExtSurfacePtsNearBreakline.pcd to Pot_A_Piece_XX_Breakline_Y.pcd
"""

import os
import shutil
import glob
import re
from pathlib import Path

def convert_intermediate_breaklines():
    """Convert intermediate breakline files to final format expected by SFS."""
    
    # Find all intermediate breakline files
    intermediate_files = glob.glob("Pot_A_Piece_*_Surface_*_IntExtSurfacePtsNearBreakline.pcd")
    
    if not intermediate_files:
        print("❌ No intermediate breakline files found!")
        return False
    
    print(f"🔍 Found {len(intermediate_files)} intermediate breakline files")
    
    # Create target directory
    breaklines_dir = "Dataset/Breaklines/Pot_A"
    os.makedirs(breaklines_dir, exist_ok=True)
    
    # Convert intermediate files to final format
    converted_count = 0
    
    for intermediate_file in intermediate_files:
        # Extract piece number and surface number from filename
        # Format: Pot_A_Piece_XX_Surface_Y_IntExtSurfacePtsNearBreakline.pcd
        match = re.match(r'Pot_A_Piece_(\d+)_Surface_([01])_IntExtSurfacePtsNearBreakline\.pcd', intermediate_file)
        
        if not match:
            print(f"⚠️ Could not parse filename: {intermediate_file}")
            continue
            
        piece_num = match.group(1)
        surface_num = match.group(2)
        
        # Create final breakline filename
        # Surface_0 -> Breakline_0, Surface_1 -> Breakline_1
        final_filename = f"Pot_A_Piece_{piece_num}_Breakline_{surface_num}.pcd"
        final_path = os.path.join(breaklines_dir, final_filename)
        
        # Copy intermediate file to final location
        try:
            shutil.copy2(intermediate_file, final_path)
            print(f"✅ {intermediate_file} → {final_path}")
            converted_count += 1
        except Exception as e:
            print(f"❌ Failed to convert {intermediate_file}: {e}")
    
    print(f"\n🎯 **Conversion Summary:**")
    print(f"   - Processed: {len(intermediate_files)} intermediate files")
    print(f"   - Converted: {converted_count} breakline files")
    print(f"   - Location: {breaklines_dir}/")
    
    # Verify expected files
    expected_files = []
    for piece in range(1, 9):  # Pieces 01-08
        for breakline in [0, 1]:  # Breakline_0 and Breakline_1
            expected_files.append(f"Pot_A_Piece_{piece:02d}_Breakline_{breakline}.pcd")
    
    existing_files = glob.glob(f"{breaklines_dir}/Pot_A_Piece_*_Breakline_*.pcd")
    existing_basenames = [os.path.basename(f) for f in existing_files]
    
    missing_files = [f for f in expected_files if f not in existing_basenames]
    
    print(f"\n📊 **File Coverage:**")
    print(f"   - Expected: {len(expected_files)} breakline files (16 total)")
    print(f"   - Generated: {len(existing_files)} breakline files")
    
    if missing_files:
        print(f"   - Missing: {len(missing_files)} files")
        print("   - Missing files:")
        for missing in missing_files[:5]:  # Show first 5 missing files
            print(f"     • {missing}")
        if len(missing_files) > 5:
            print(f"     ... and {len(missing_files) - 5} more")
    else:
        print(f"   - ✅ All expected breakline files present!")
    
    return converted_count > 0

if __name__ == "__main__":
    print("=== Converting Intermediate Breaklines to Final Format ===")
    success = convert_intermediate_breaklines()
    
    if success:
        print("🏆 Breakline conversion completed successfully!")
    else:
        print("❌ Breakline conversion failed!")
    
    print("=== Conversion Complete ===")