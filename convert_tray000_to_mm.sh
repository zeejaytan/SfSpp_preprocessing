#!/bin/bash

# Script to convert existing Tray-000 dataset from meters to millimeters
# Converts x,y,z coordinates by multiplying by 1000
# Preserves normals and curvature values unchanged

DATASET_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing/Tray-000_Dataset_20251021/SfS_pp"
BACKUP_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing/Tray-000_Dataset_20251021_METERS_BACKUP"

echo "=========================================="
echo "Tray-000 Unit Conversion: Meters → Millimeters"
echo "=========================================="
echo "Started: $(date)"
echo ""

# Create backup of original files
echo "Step 1: Creating backup of original files (meters)..."
if [ -d "${BACKUP_DIR}" ]; then
    echo "WARNING: Backup directory already exists: ${BACKUP_DIR}"
    echo "Skipping backup creation to avoid overwriting existing backup."
else
    echo "Creating backup: ${BACKUP_DIR}"
    cp -r ${DATASET_DIR} ${BACKUP_DIR}
    echo "✓ Backup created successfully"
fi
echo ""

# Function to convert XYZ file (6 fields: x y z nx ny nz)
convert_xyz_file() {
    local file=$1
    local temp_file="${file}.tmp"

    echo "Converting: $(basename $file)"

    # Convert coordinates (columns 1-3) by multiplying by 1000, keep normals (4-6) unchanged
    awk '{
        printf "%.6f %.6f %.6f %.6f %.6f %.6f\n", $1*1000, $2*1000, $3*1000, $4, $5, $6
    }' "$file" > "$temp_file"

    # Replace original with converted file
    mv "$temp_file" "$file"
}

# Function to convert PCD file (7 fields: x y z nx ny nz curvature)
convert_pcd_file() {
    local file=$1
    local temp_file="${file}.tmp"

    echo "Converting: $(basename $file)"

    # Read PCD file, convert DATA section only
    awk '
    BEGIN { data_section = 0 }
    /^DATA ascii/ {
        data_section = 1
        print $0
        next
    }
    data_section == 0 {
        # Print header unchanged
        print $0
        next
    }
    data_section == 1 {
        # Convert coordinates (1-3) by *1000, keep normals (4-6) and curvature (7) unchanged
        printf "%.6f %.6f %.6f %.6f %.6f %.6f %.6f\n", $1*1000, $2*1000, $3*1000, $4, $5, $6, $7
    }
    ' "$file" > "$temp_file"

    # Replace original with converted file
    mv "$temp_file" "$file"
}

# Step 2: Convert Surface files (XYZ format)
echo "Step 2: Converting Surface files (80 files)..."
SURFACE_DIR="${DATASET_DIR}/Surfaces"
SURFACE_COUNT=0

for file in ${SURFACE_DIR}/Tray-000_Piece_*_Surface_*.xyz; do
    if [ -f "$file" ]; then
        convert_xyz_file "$file"
        ((SURFACE_COUNT++))
    fi
done

echo "✓ Converted ${SURFACE_COUNT} surface files"
echo ""

# Step 3: Convert Breakline files (PCD format)
echo "Step 3: Converting Breakline files (80 files)..."
BREAKLINE_DIR="${DATASET_DIR}/Breaklines"
BREAKLINE_COUNT=0

for file in ${BREAKLINE_DIR}/Tray-000_Piece_*_Breakline_*.pcd; do
    if [ -f "$file" ]; then
        convert_pcd_file "$file"
        ((BREAKLINE_COUNT++))
    fi
done

echo "✓ Converted ${BREAKLINE_COUNT} breakline files"
echo ""

# Step 4: Convert Axis files (XYZ format)
echo "Step 4: Converting Axis files (40 files)..."
AXIS_DIR="${DATASET_DIR}/Axes"
AXIS_COUNT=0

for file in ${AXIS_DIR}/Tray-000_Piece_*_Axis.xyz; do
    if [ -f "$file" ]; then
        convert_xyz_file "$file"
        ((AXIS_COUNT++))
    fi
done

echo "✓ Converted ${AXIS_COUNT} axis files"
echo ""

# Verification
echo "=========================================="
echo "Conversion Complete - Verification"
echo "=========================================="

echo ""
echo "Sample Surface coordinates (should now be hundreds of mm):"
SAMPLE_SURFACE="${SURFACE_DIR}/Tray-000_Piece_01_Surface_0.xyz"
if [ -f "${SAMPLE_SURFACE}" ]; then
    echo "File: $(basename ${SAMPLE_SURFACE})"
    echo "First 3 points:"
    head -3 ${SAMPLE_SURFACE}
    echo ""
fi

echo "Sample Breakline coordinates (should now be hundreds of mm):"
SAMPLE_BREAKLINE="${BREAKLINE_DIR}/Tray-000_Piece_01_Breakline_0.pcd"
if [ -f "${SAMPLE_BREAKLINE}" ]; then
    echo "File: $(basename ${SAMPLE_BREAKLINE})"
    echo "First 3 data points:"
    grep -A 3 "DATA ascii" ${SAMPLE_BREAKLINE} | tail -3
    echo ""
fi

echo "Sample Axis coordinates (should now be hundreds of mm):"
SAMPLE_AXIS="${AXIS_DIR}/Tray-000_Piece_01_Axis.xyz"
if [ -f "${SAMPLE_AXIS}" ]; then
    echo "File: $(basename ${SAMPLE_AXIS})"
    cat ${SAMPLE_AXIS}
    echo ""
fi

echo "=========================================="
echo "Summary"
echo "=========================================="
echo "✓ Surfaces converted: ${SURFACE_COUNT}/80"
echo "✓ Breaklines converted: ${BREAKLINE_COUNT}/80"
echo "✓ Axes converted: ${AXIS_COUNT}/40"
echo ""
echo "Original files (meters) backed up to:"
echo "${BACKUP_DIR}"
echo ""
echo "Converted files (millimeters) in:"
echo "${DATASET_DIR}"
echo ""
echo "Completed: $(date)"
