#!/bin/bash
#
# cc_mesh_to_pcd.sh - Convert OBJ mesh to PCD point cloud using CloudCompare
#
# Usage: ./cc_mesh_to_pcd.sh -i input.obj -o output_dir [-m max_points] [-n noise] [-f]
#
# This script automates the CloudCompare pipeline for converting photogrammetry
# meshes to standardized point clouds with normals, noise filtering, and centering.
#

set -euo pipefail

# Default parameters
MAX_POINTS=1000000
NOISE_FILTER="medium"
NORMAL_RADIUS=0.5
NORMAL_ORIENT_K=6
FORCE_OVERWRITE=false

# Safety thresholds
MAX_REMOVAL_PERCENT=30
MIN_OUTPUT_POINTS=10000

# Exit codes
EXIT_SUCCESS=0
EXIT_INPUT_NOT_FOUND=1
EXIT_CC_FAILED=2
EXIT_NOISE_TOO_AGGRESSIVE=3
EXIT_NO_POINTS=4
EXIT_MISSING_NORMALS=5
EXIT_OUTPUT_NOT_CREATED=6
EXIT_WOULD_OVERWRITE=7

# Script directory for finding helpers
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

usage() {
    cat << EOF
Usage: $(basename "$0") -i INPUT -o OUTPUT_DIR [OPTIONS]

Convert OBJ mesh to PCD point cloud with normals using CloudCompare.

Required:
  -i INPUT        Input OBJ mesh file
  -o OUTPUT_DIR   Output directory for PCD and log files

Options:
  -m MAX_POINTS   Maximum points to sample (default: 1000000)
  -n NOISE        Noise filter strength: low, medium, high (default: medium)
  -f              Force overwrite existing output files
  -h              Show this help message

Examples:
  $(basename "$0") -i Pot_A_Piece_01_Mesh.obj -o Dataset/Point/Pot_A
  $(basename "$0") -i mesh.obj -o output -m 500000 -n high -f

EOF
    exit 1
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Parse command line arguments
while getopts "i:o:m:n:fh" opt; do
    case $opt in
        i) INPUT_FILE="$OPTARG" ;;
        o) OUTPUT_DIR="$OPTARG" ;;
        m) MAX_POINTS="$OPTARG" ;;
        n) NOISE_FILTER="$OPTARG" ;;
        f) FORCE_OVERWRITE=true ;;
        h) usage ;;
        *) usage ;;
    esac
done

# Validate required arguments
if [[ -z "${INPUT_FILE:-}" ]] || [[ -z "${OUTPUT_DIR:-}" ]]; then
    log_error "Missing required arguments"
    usage
fi

# Validate input file exists
if [[ ! -f "$INPUT_FILE" ]]; then
    log_error "Input file not found: $INPUT_FILE"
    exit $EXIT_INPUT_NOT_FOUND
fi

# Get absolute paths
INPUT_FILE="$(realpath "$INPUT_FILE")"
mkdir -p "$OUTPUT_DIR"
OUTPUT_DIR="$(realpath "$OUTPUT_DIR")"

# Generate output filenames
BASENAME=$(basename "$INPUT_FILE" .obj)
# Convert naming: *_Mesh.obj -> *_Point.pcd
OUTPUT_BASENAME="${BASENAME/_Mesh/}"
OUTPUT_PCD="$OUTPUT_DIR/${OUTPUT_BASENAME}_Point.pcd"
OUTPUT_LOG="$OUTPUT_DIR/${OUTPUT_BASENAME}_cc.log"
TEMP_ASC="$OUTPUT_DIR/${OUTPUT_BASENAME}_temp.asc"

# Check for existing output
if [[ -f "$OUTPUT_PCD" ]] && [[ "$FORCE_OVERWRITE" != true ]]; then
    log_error "Output file already exists: $OUTPUT_PCD (use -f to overwrite)"
    exit $EXIT_WOULD_OVERWRITE
fi

# Set noise filter parameters based on preset
case $NOISE_FILTER in
    low)
        SOR_NEIGHBORS=6
        SOR_STD=2.0
        ;;
    medium)
        SOR_NEIGHBORS=6
        SOR_STD=1.0
        ;;
    high)
        SOR_NEIGHBORS=6
        SOR_STD=0.5
        ;;
    *)
        log_error "Invalid noise filter: $NOISE_FILTER (must be low, medium, or high)"
        exit 1
        ;;
esac

# Initialize log file
START_TIME=$(date '+%Y-%m-%d %H:%M:%S')
cat > "$OUTPUT_LOG" << EOF
=== CloudCompare Mesh-to-PCD Log ===
Timestamp: $START_TIME
Input: $INPUT_FILE
Output: $OUTPUT_PCD

Parameters:
  Max Points: $MAX_POINTS
  Noise Filter: $NOISE_FILTER (SOR $SOR_NEIGHBORS $SOR_STD)
  Normal Radius: $NORMAL_RADIUS
  Normal Orient K: $NORMAL_ORIENT_K

EOF

log_info "Starting CloudCompare mesh-to-PCD conversion"
log_info "Input: $INPUT_FILE"
log_info "Output: $OUTPUT_PCD"

# Load CloudCompare module
log_info "Loading CloudCompare module..."
module load GCC/11.3.0 OpenMPI/4.1.4 CloudCompare/2.12.4

# Set Qt to offscreen rendering (required for headless operation)
export QT_QPA_PLATFORM=offscreen

# Get CloudCompare version
CC_VERSION=$(CloudCompare --version 2>&1 | head -1 || echo "Unknown")
echo "CloudCompare Version: $CC_VERSION" >> "$OUTPUT_LOG"
echo "" >> "$OUTPUT_LOG"

# Run CloudCompare pipeline
log_info "Running CloudCompare pipeline..."
log_info "  - Sampling mesh to $MAX_POINTS points"
log_info "  - Computing normals (radius=$NORMAL_RADIUS)"
log_info "  - Applying noise filter ($NOISE_FILTER)"

# CloudCompare command
# Note: -GLOBAL_SHIFT AUTO centers the point cloud
CC_CMD="CloudCompare -SILENT -AUTO_SAVE OFF \
    -C_EXPORT_FMT ASC -PREC 6 -SEP SPACE -ADD_HEADER \
    -O -GLOBAL_SHIFT AUTO \"$INPUT_FILE\" \
    -SAMPLE_MESH POINTS $MAX_POINTS \
    -OCTREE_NORMALS $NORMAL_RADIUS \
    -ORIENT_NORMS_MST $NORMAL_ORIENT_K \
    -SOR $SOR_NEIGHBORS $SOR_STD \
    -SAVE_CLOUDS FILE \"$TEMP_ASC\""

echo "CloudCompare Command:" >> "$OUTPUT_LOG"
echo "$CC_CMD" >> "$OUTPUT_LOG"
echo "" >> "$OUTPUT_LOG"

# Execute CloudCompare with timeout (30 minutes for large meshes)
if ! timeout 1800 bash -c "$CC_CMD" 2>&1 | tee -a "$OUTPUT_LOG"; then
    log_error "CloudCompare failed"
    echo "Status: FAILED - CloudCompare error" >> "$OUTPUT_LOG"
    exit $EXIT_CC_FAILED
fi

# Check if ASC file was created
if [[ ! -f "$TEMP_ASC" ]]; then
    # CloudCompare may add suffix to filename
    TEMP_ASC_ACTUAL=$(ls "${TEMP_ASC%.asc}"*.asc 2>/dev/null | head -1 || true)
    if [[ -z "$TEMP_ASC_ACTUAL" ]]; then
        log_error "CloudCompare did not create output file"
        echo "Status: FAILED - No output file created" >> "$OUTPUT_LOG"
        exit $EXIT_OUTPUT_NOT_CREATED
    fi
    TEMP_ASC="$TEMP_ASC_ACTUAL"
fi

# Count points in ASC file
POINT_COUNT=$(grep -c "^[0-9-]" "$TEMP_ASC" 2>/dev/null || echo "0")
log_info "Points after processing: $POINT_COUNT"

# Safety check: minimum points
if [[ "$POINT_COUNT" -lt "$MIN_OUTPUT_POINTS" ]]; then
    log_error "Too few points remaining: $POINT_COUNT (minimum: $MIN_OUTPUT_POINTS)"
    echo "Status: FAILED - Too few points ($POINT_COUNT)" >> "$OUTPUT_LOG"
    exit $EXIT_NO_POINTS
fi

# Convert ASC to PCD
log_info "Converting ASC to PCD format..."

python3 << PYEOF
import sys

input_file = "$TEMP_ASC"
output_file = "$OUTPUT_PCD"

# Read ASC file
points = []
with open(input_file, 'r') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('//') or line.startswith('#'):
            continue
        parts = line.split()
        if len(parts) >= 6:
            try:
                x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
                nx, ny, nz = float(parts[3]), float(parts[4]), float(parts[5])
                points.append((x, y, z, nx, ny, nz))
            except ValueError:
                continue

if len(points) == 0:
    print("ERROR: No valid points found in ASC file", file=sys.stderr)
    sys.exit(1)

# Check for missing normals
missing_normals = sum(1 for p in points if p[3] == 0 and p[4] == 0 and p[5] == 0)
if missing_normals > len(points) * 0.1:
    print(f"ERROR: Too many points missing normals: {missing_normals}/{len(points)}", file=sys.stderr)
    sys.exit(1)

# Write PCD file
with open(output_file, 'w') as f:
    f.write("# .PCD v0.7 - Point Cloud Data file format\n")
    f.write("VERSION 0.7\n")
    f.write("FIELDS x y z normal_x normal_y normal_z\n")
    f.write("SIZE 4 4 4 4 4 4\n")
    f.write("TYPE F F F F F F\n")
    f.write("COUNT 1 1 1 1 1 1\n")
    f.write(f"WIDTH {len(points)}\n")
    f.write("HEIGHT 1\n")
    f.write("VIEWPOINT 0 0 0 1 0 0 0\n")
    f.write(f"POINTS {len(points)}\n")
    f.write("DATA ascii\n")
    for p in points:
        f.write(f"{p[0]} {p[1]} {p[2]} {p[3]} {p[4]} {p[5]}\n")

# Calculate bounding box
xs = [p[0] for p in points]
ys = [p[1] for p in points]
zs = [p[2] for p in points]

min_x, max_x = min(xs), max(xs)
min_y, max_y = min(ys), max(ys)
min_z, max_z = min(zs), max(zs)

center_x = (min_x + max_x) / 2
center_y = (min_y + max_y) / 2
center_z = (min_z + max_z) / 2

print(f"BBOX_X={min_x:.2f},{max_x:.2f}")
print(f"BBOX_Y={min_y:.2f},{max_y:.2f}")
print(f"BBOX_Z={min_z:.2f},{max_z:.2f}")
print(f"CENTER={center_x:.2f},{center_y:.2f},{center_z:.2f}")
print(f"POINTS={len(points)}")
PYEOF

# Capture Python output for logging
CONVERT_RESULT=$?
if [[ $CONVERT_RESULT -ne 0 ]]; then
    log_error "ASC to PCD conversion failed"
    echo "Status: FAILED - Conversion error" >> "$OUTPUT_LOG"
    exit $EXIT_MISSING_NORMALS
fi

# Clean up temporary file
rm -f "$TEMP_ASC"

# Final verification
if [[ ! -f "$OUTPUT_PCD" ]]; then
    log_error "Output PCD file was not created"
    echo "Status: FAILED - Output not created" >> "$OUTPUT_LOG"
    exit $EXIT_OUTPUT_NOT_CREATED
fi

FINAL_SIZE=$(stat -c%s "$OUTPUT_PCD")
if [[ "$FINAL_SIZE" -lt 100 ]]; then
    log_error "Output PCD file is empty or too small"
    echo "Status: FAILED - Empty output" >> "$OUTPUT_LOG"
    exit $EXIT_OUTPUT_NOT_CREATED
fi

# Complete the log
END_TIME=$(date '+%Y-%m-%d %H:%M:%S')
cat >> "$OUTPUT_LOG" << EOF

Results:
  Final Point Count: $POINT_COUNT
  Output File Size: $FINAL_SIZE bytes

Completed: $END_TIME
Status: SUCCESS
EOF

log_info "Conversion complete!"
log_info "Output: $OUTPUT_PCD"
log_info "Log: $OUTPUT_LOG"

exit $EXIT_SUCCESS
