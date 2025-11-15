#!/bin/bash
#SBATCH --job-name=nurbs_from_objdir
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=12:00:00
#SBATCH --output=nurbs_from_objdir_%j.out
#SBATCH --error=nurbs_from_objdir_%j.err

set -euo pipefail

echo "=== NURBS Preprocessing From OBJ Directory ==="
echo "Started: $(date)"
echo "Job ID: ${SLURM_JOB_ID:-N/A}"

BASE_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"
cd "$BASE_DIR"

# Input directory with OBJ files (default to Tray-000 if not provided)
INPUT_DIR="${1:-/data/gpfs/projects/punim2657/GARF/input/Tray-000}"
# Optional dataset name (defaults to basename of input dir)
DATASET_NAME="${2:-}"
# Optional third arg: 'skip' to skip sampling
SKIP_SAMPLING="${3:-}"
if [ -z "$DATASET_NAME" ]; then
  DATASET_NAME="$(basename "$INPUT_DIR")"
fi
echo "Dataset name: $DATASET_NAME"
echo "Input OBJ directory: $INPUT_DIR"

if [ ! -d "$INPUT_DIR" ]; then
  echo "ERROR: Input directory not found: $INPUT_DIR" >&2
  exit 1
fi

# Tools and container
APPTAINER="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
CONTAINER_IMAGE="pcl_191_nurbs.sif"

if [ ! -f "$CONTAINER_IMAGE" ]; then
  echo "ERROR: Container image not found: $CONTAINER_IMAGE" >&2
  exit 1
fi

# Prepare expected project structure
echo "Preparing project directories..."
mkdir -p Dataset/{Mesh,Point,Surfaces,Breaklines,Axes}
mkdir -p Dataset/{Mesh,Point}/Pot_A
mkdir -p Temp Temp/Data/Pot_A Temp/Temp/Pot_A Temp/Temp_edge/Pot_A

# Step 1: Generate PCDs with normals using CloudCompare and stage meshes
echo "=== Step 1: Sampling OBJ -> PCD and staging meshes ==="
if [ "$SKIP_SAMPLING" != "skip" ]; then
  module -q load CloudCompare/2.12.4 || true
  # Try to load ICU dependency for CloudCompare
  module -q load icu4c/71.1 || module -q load ICU/71.1 || module -q load libicu/71 || true
fi

# Enumerate OBJ files in INPUT_DIR (sorted)
mapfile -t OBJ_LIST < <(find "$INPUT_DIR" -maxdepth 1 -type f -name '*.obj' | sort)
if [ ${#OBJ_LIST[@]} -eq 0 ]; then
  echo "ERROR: No OBJ files found in $INPUT_DIR" >&2
  exit 1
fi

piece_count=0
for obj_path in "${OBJ_LIST[@]}"; do
  obj_file=$(basename "$obj_path")
  # Extract a 2-digit numeric id if present, else auto-increment
  if [[ "$obj_file" =~ ([0-9]{2}) ]]; then
    piece_num="${BASH_REMATCH[1]}"
  else
    ((piece_count++))
    piece_num=$(printf "%02d" "$piece_count")
  fi

  mesh_dst="Dataset/Mesh/Pot_A/Pot_A_Piece_${piece_num}_Mesh.obj"
  pcd_dst="Dataset/Point/Pot_A/Pot_A_Piece_${piece_num}_Point.pcd"

  echo "Processing $obj_file -> piece $piece_num"
  # Copy mesh into expected Mesh folder
  cp -f "$obj_path" "$mesh_dst"
  # Also copy into Temp root so EdgeLineExtractionHeadless can find it
  cp -f "$obj_path" "Temp/Pot_A_Piece_${piece_num}_Mesh.obj"

  if [ "$SKIP_SAMPLING" != "skip" ]; then
    # Try to sample with CloudCompare if available
    if command -v CloudCompare >/dev/null 2>&1; then
      CloudCompare -SILENT -NO_TIMESTAMP \
        -O "$mesh_dst" \
        -SAMPLE_MESH POINTS 50000 \
        -COMPUTE_NORMALS \
        -C_EXPORT_FMT PCD -SAVE_CLOUDS FILE "$pcd_dst" || {
          echo "WARNING: CloudCompare sampling failed for $obj_file; continuing" >&2
        }
    fi
  fi

  if [ -f "$pcd_dst" ]; then
    echo "  Found PCD: $pcd_dst"
  else
    echo "  NOTE: No PCD present for $obj_file (will rely on pre-generated PCDs)"
  fi
done

echo "Sampling complete at: $(date)"

# Step 2: Run MeshPreprocessingHeadless (NURBS surfaces)
echo "=== Step 2: NURBS Surface Generation ==="
$APPTAINER exec \
  --bind "$BASE_DIR:/workspace" \
  --pwd /workspace \
  "$CONTAINER_IMAGE" \
  /bin/bash -lc "set -e; cd /workspace/original_nurbs_preprocessing; if [ ! -x build/MeshPreprocessingHeadless ]; then rm -rf build; mkdir -p build; cd build; cmake ..; make -j2 MeshPreprocessingHeadless; else cd build; true; fi"
$APPTAINER exec \
  --bind "$BASE_DIR:/workspace" \
  --pwd /workspace \
  "$CONTAINER_IMAGE" \
  /workspace/original_nurbs_preprocessing/build/MeshPreprocessingHeadless

echo "Surface generation finished at: $(date)"
ls -la Temp/Data/Pot_A/*_Surface_*.xyz 2>/dev/null || echo "No Surface XYZ files found yet"

# Step 3: Stage surfaces for MATLAB axis extraction under Dataset/SfS_pp/Surfaces
echo "=== Step 3: Prepare surfaces for MATLAB axis extraction ==="

# Step 4: MATLAB PotSAC Axis Extraction (NURBS surfaces)
echo "=== Step 4: MATLAB PotSAC Axis Extraction ==="
module -q load MATLAB/2024b_Update_3 || true
# Pass surfaces dir via environment variable so MATLAB reads from our staged Pot_A surfaces
export SURFACES_DIR="$BASE_DIR/Temp/Data/Pot_A"
matlab -batch "try; addpath('original_nurbs_preprocessing'); addpath('original_nurbs_preprocessing/AxisExtraction'); addpath('AxisExtraction'); extract_axes_for_surfaces; catch ME; disp(getReport(ME)); exit(1); end; exit(0);"

echo "Axis extraction finished at: $(date)"
ls -la original_nurbs_preprocessing/AxisExtraction/*NURBS_Axis.xyz 2>/dev/null || true
ls -la NURBS_Output/Axes/*.xyz 2>/dev/null || true

# Make axes available to EdgeLine for rim classification
mkdir -p Dataset/Axes
if compgen -G "NURBS_Output/Axes/Pot_A_Piece_*_Axis.xyz" > /dev/null; then
  cp -f NURBS_Output/Axes/Pot_A_Piece_*_Axis.xyz Dataset/Axes/
fi

# Prune Temp meshes to only those with generated surfaces
echo "Pruning Temp meshes to match available surfaces..."
have_pieces=$(ls Temp/Data/Pot_A/Pot_A_Piece_*_Surface_0.xyz 2>/dev/null | sed -E 's/.*Piece_([0-9]{2})_.*/\1/' | sort -u)
for mesh in Temp/Pot_A_Piece_*_Mesh.obj; do
  [ -e "$mesh" ] || continue
  pn=$(echo "$mesh" | sed -E 's/.*Piece_([0-9]{2})_.*/\1/')
  if ! echo "$have_pieces" | grep -q "^$pn$"; then
    echo "  Removing $mesh (no surfaces for piece $pn)"
    rm -f "$mesh"
  fi
done

# Step 5: EdgeLine extraction (breaklines + Surface_F), now with axis available for classification
echo "=== Step 5: EdgeLine Extraction (NURBS) ==="
$APPTAINER exec \
  --bind "$BASE_DIR:/workspace" \
  --pwd /workspace \
  "$CONTAINER_IMAGE" \
  /bin/bash -lc "set -e; cd /workspace/original_nurbs_preprocessing; rm -rf build; mkdir -p build; cd build; cmake ..; make -j2 EdgeLineExtractionHeadless"

$APPTAINER exec \
  --bind "$BASE_DIR:/workspace" \
  --pwd /workspace \
  "$CONTAINER_IMAGE" \
  /workspace/original_nurbs_preprocessing/build/EdgeLineExtractionHeadless

echo "EdgeLine extraction finished at: $(date)"
ls -la Dataset/Breaklines/Pot_A/Pot_A_Piece_*_Breakline_*.pcd 2>/dev/null || echo "No Breakline PCD files found"

# Step 6: Organize outputs into clean dataset
echo "=== Step 6: Organize outputs ==="
OUT_DIR="${DATASET_NAME}_Dataset_$(date +%Y%m%d)"
mkdir -p "$OUT_DIR/SfS_pp/"{Surfaces,Breaklines,Axes,Mesh,Point}

echo "Copying and renaming Surfaces..."
shopt -s nullglob
for f in Temp/Data/Pot_A/Pot_A_Piece_*_Surface_*.xyz; do
  base=$(basename "$f")
  new="${base/Pot_A/${DATASET_NAME}}"
  cp -f "$f" "$OUT_DIR/SfS_pp/Surfaces/$new"
done

echo "Copying and renaming Breaklines..."
for f in Dataset/Breaklines/Pot_A/Pot_A_Piece_*_Breakline_*.pcd; do
  base=$(basename "$f")
  new="${base/Pot_A/${DATASET_NAME}}"
  cp -f "$f" "$OUT_DIR/SfS_pp/Breaklines/$new"
done

echo "Copying and renaming Mesh..."
for f in Dataset/Mesh/Pot_A/Pot_A_Piece_*_Mesh.obj; do
  base=$(basename "$f")
  new="${base/Pot_A/${DATASET_NAME}}"
  cp -f "$f" "$OUT_DIR/SfS_pp/Mesh/$new"
done

echo "Copying and renaming Point clouds..."
mkdir -p "$OUT_DIR/SfS_pp/Point/$DATASET_NAME"
for f in Dataset/Point/Pot_A/Pot_A_Piece_*_Point.pcd; do
  base=$(basename "$f")
  new="${base/Pot_A/${DATASET_NAME}}"
  cp -f "$f" "$OUT_DIR/SfS_pp/Point/$DATASET_NAME/$new"
done

# Copy axes (prefer NURBS_Output/Axes if present, fallback to AxisExtraction outputs)
echo "Copying and renaming Axes..."
if compgen -G "NURBS_Output/Axes/*_Axis.xyz" > /dev/null; then
  for f in NURBS_Output/Axes/*_Axis.xyz; do
    base=$(basename "$f")
    new="${base/Pot_A/${DATASET_NAME}}"
    cp -f "$f" "$OUT_DIR/SfS_pp/Axes/$new"
  done
fi

# Optional: axis extraction can be added later if needed

# Step 7: Optional curvature fix for NURBS breaklines
if [ -f fix_nurbs_curvature_values.py ]; then
  echo "Fixing curvature fields in Breakline PCDs..."
  python3 fix_nurbs_curvature_values.py "$OUT_DIR" || true
fi

# Symlink latest
rm -f latest_nurbs_dataset
ln -s "$OUT_DIR" latest_nurbs_dataset

echo "=== Output Summary ==="
echo "Dataset: $OUT_DIR"
find "$OUT_DIR/SfS_pp" -type f | sort | sed 's#^#  #'

echo "Completed: $(date)"
echo "=== NURBS Preprocessing From OBJ Directory DONE ==="
