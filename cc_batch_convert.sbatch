#!/bin/bash
#SBATCH --job-name=cc_mesh2pcd
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=128G
#SBATCH --partition=sapphire
#SBATCH --output=cc_batch_%A_%a.out
#SBATCH --error=cc_batch_%A_%a.err

#
# CloudCompare Batch Mesh-to-PCD Conversion
#
# Usage:
#   Single piece:  sbatch cc_batch_convert.sbatch
#   Array job:     sbatch --array=1-8 cc_batch_convert.sbatch
#
# Environment variables (optional):
#   POT_ID    - Pot identifier (default: Pot_A)
#   PIECE_NUM - Specific piece number, overrides array task ID
#

set -euo pipefail

# Configuration
POT_ID="${POT_ID:-Pot_A}"
PIECE_NUM="${PIECE_NUM:-${SLURM_ARRAY_TASK_ID:-1}}"
PIECE=$(printf "%02d" "$PIECE_NUM")

# Paths
SCRIPT_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"
INPUT_DIR="$SCRIPT_DIR/Dataset/Mesh/${POT_ID}"
OUTPUT_DIR="$SCRIPT_DIR/Dataset/Point/${POT_ID}"

# Input/Output files
INPUT_FILE="$INPUT_DIR/${POT_ID}_Piece_${PIECE}_Mesh.obj"
OUTPUT_PCD="$OUTPUT_DIR/${POT_ID}_Piece_${PIECE}_Point.pcd"

echo "=============================================="
echo "CloudCompare Mesh-to-PCD Batch Conversion"
echo "=============================================="
echo "Job ID: ${SLURM_JOB_ID:-local}"
echo "Array Task: ${SLURM_ARRAY_TASK_ID:-N/A}"
echo "Pot: $POT_ID"
echo "Piece: $PIECE"
echo "Input: $INPUT_FILE"
echo "Output: $OUTPUT_PCD"
echo "Started: $(date)"
echo "=============================================="

# Check input exists
if [[ ! -f "$INPUT_FILE" ]]; then
    # Check if it's a symlink that needs resolving
    if [[ -L "$INPUT_FILE" ]]; then
        echo "ERROR: Input is a broken symlink: $INPUT_FILE"
        echo "Target: $(readlink "$INPUT_FILE")"
    else
        echo "ERROR: Input file not found: $INPUT_FILE"
    fi
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Run conversion
echo ""
echo "Running CloudCompare conversion..."
"$SCRIPT_DIR/cc_mesh_to_pcd.sh" \
    -i "$INPUT_FILE" \
    -o "$OUTPUT_DIR" \
    -m 1000000 \
    -n medium \
    -f

# Verify output
if [[ -f "$OUTPUT_PCD" ]]; then
    POINTS=$(grep "^POINTS " "$OUTPUT_PCD" | awk '{print $2}')
    echo ""
    echo "=============================================="
    echo "Conversion successful!"
    echo "Output: $OUTPUT_PCD"
    echo "Points: $POINTS"
    echo "Completed: $(date)"
    echo "=============================================="
else
    echo ""
    echo "ERROR: Output file not created"
    exit 1
fi
