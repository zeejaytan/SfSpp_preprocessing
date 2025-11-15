#!/bin/bash
# Fix Tray-000 dataset by copying and renaming Pot_A files to Tray-000

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║        FIX TRAY-000 DATASET - RENAME POT_A TO TRAY-000        ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "This script copies properly generated NURBS files (with normals+curvature)"
echo "from their actual locations and renames them to Tray-000 format"
echo ""

cd /data/gpfs/projects/punim2657/sfs_preprocessing

# 1. Copy and rename BREAKLINES
echo "=== Step 1: Copy and Rename Breaklines ==="
echo "Source: Dataset/Breaklines/Pot_A/*.pcd"
echo "Destination: Tray-000_Dataset_20251021/SfS_pp/Breaklines/"

BREAKLINE_COUNT=0
for src_file in Dataset/Breaklines/Pot_A/Pot_A_Piece_*_Breakline_*.pcd; do
    if [ -f "$src_file" ]; then
        filename=$(basename "$src_file")
        dest_file="Tray-000_Dataset_20251021/SfS_pp/Breaklines/${filename/Pot_A/Tray-000}"
        cp "$src_file" "$dest_file"
        ((BREAKLINE_COUNT++))
        if [ $((BREAKLINE_COUNT % 10)) -eq 0 ]; then
            echo "  Copied $BREAKLINE_COUNT files..."
        fi
    fi
done
echo "✓ Copied and renamed $BREAKLINE_COUNT breakline files"

# Verify breakline format
echo ""
echo "Verifying breakline format (checking first file)..."
FIRST_BREAKLINE=$(ls Tray-000_Dataset_20251021/SfS_pp/Breaklines/Tray-000_Piece_01_Breakline_0.pcd 2>/dev/null)
if [ -f "$FIRST_BREAKLINE" ]; then
    echo "Format check:"
    grep "^FIELDS" "$FIRST_BREAKLINE"
    echo "Point count:"
    grep "^POINTS" "$FIRST_BREAKLINE"
fi

# 2. Copy and rename AXES
echo ""
echo "=== Step 2: Copy and Rename Axes ==="
echo "Source: Dataset/Axes/Pot_A_Piece_*.xyz"
echo "Destination: Tray-000_Dataset_20251021/SfS_pp/Axes/"

AXIS_COUNT=0
for src_file in Dataset/Axes/Pot_A_Piece_*_Axis.xyz; do
    if [ -f "$src_file" ]; then
        filename=$(basename "$src_file")
        dest_file="Tray-000_Dataset_20251021/SfS_pp/Axes/${filename/Pot_A/Tray-000}"
        cp "$src_file" "$dest_file"
        ((AXIS_COUNT++))
    fi
done
echo "✓ Copied and renamed $AXIS_COUNT axis files"

# Verify axis format
echo ""
echo "Verifying axis format (checking first file)..."
FIRST_AXIS=$(ls Tray-000_Dataset_20251021/SfS_pp/Axes/Tray-000_Piece_01_Axis.xyz 2>/dev/null)
if [ -f "$FIRST_AXIS" ]; then
    echo "Axis data:"
    cat "$FIRST_AXIS"
fi

# 3. Final Verification
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                   FINAL DATASET VERIFICATION                  ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Tray-000_Dataset_20251021/SfS_pp/ contents:"
echo "  Surfaces:   $(ls Tray-000_Dataset_20251021/SfS_pp/Surfaces/*.xyz 2>/dev/null | wc -l) files (expected 80)"
echo "  Breaklines: $(ls Tray-000_Dataset_20251021/SfS_pp/Breaklines/*.pcd 2>/dev/null | wc -l) files (expected 80)"
echo "  Axes:       $(ls Tray-000_Dataset_20251021/SfS_pp/Axes/*.xyz 2>/dev/null | wc -l) files (expected 40)"
echo "  Mesh:       $(ls Tray-000_Dataset_20251021/SfS_pp/Mesh/*.obj 2>/dev/null | wc -l) files (expected 40)"
echo "  Point:      $(ls Tray-000_Dataset_20251021/SfS_pp/Point/*.pcd 2>/dev/null | wc -l) files (expected 40)"
echo ""

# Check if all expected files are present
SURFACES=$(ls Tray-000_Dataset_20251021/SfS_pp/Surfaces/*.xyz 2>/dev/null | wc -l)
BREAKLINES=$(ls Tray-000_Dataset_20251021/SfS_pp/Breaklines/*.pcd 2>/dev/null | wc -l)
AXES=$(ls Tray-000_Dataset_20251021/SfS_pp/Axes/*.xyz 2>/dev/null | wc -l)

if [ "$SURFACES" -eq 80 ] && [ "$BREAKLINES" -eq 80 ] && [ "$AXES" -eq 40 ]; then
    echo "✓✓✓ SUCCESS: All files present and properly named!"
    echo ""
    echo "Dataset is now READY for SFS assembly"
    echo "Location: /data/gpfs/projects/punim2657/sfs_preprocessing/Tray-000_Dataset_20251021/SfS_pp/"
else
    echo "⚠ WARNING: File counts don't match expected values"
    if [ "$BREAKLINES" -ne 80 ]; then
        echo "  - Breaklines: $BREAKLINES (expected 80)"
    fi
    if [ "$AXES" -ne 40 ]; then
        echo "  - Axes: $AXES (expected 40)"
    fi
fi

echo ""
echo "Fix completed at: $(date)"
