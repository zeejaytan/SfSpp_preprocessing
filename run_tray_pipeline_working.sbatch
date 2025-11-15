#!/bin/bash
#SBATCH --job-name=tray_pipeline_working
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=6
#SBATCH --mem=32G
#SBATCH --time=8:00:00
#SBATCH --output=tray_pipeline_working_%j.out
#SBATCH --error=tray_pipeline_working_%j.err

set -euo pipefail

echo "=== TRAY Pipeline (Working Path) ==="
echo "Started: $(date)"
echo "Job ID: ${SLURM_JOB_ID:-N/A}"

BASE_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"
INPUT_DIR="${1:-/data/gpfs/projects/punim2657/GARF/input/Tray-000}"
DATASET_NAME="${2:-Tray-000}"
PIECES="${3:-40}"

cd "$BASE_DIR"

APPTAINER="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
PREP_IMAGE="cache/sfs_prep_from_working.sif"

if [ ! -f "$PREP_IMAGE" ]; then
  echo "ERROR: Preprocessing container not found at $PREP_IMAGE" >&2
  exit 1
fi

echo "Input OBJ dir: $INPUT_DIR"
echo "Dataset name: $DATASET_NAME, pieces: $PIECES"

echo "Staging meshes into Dataset/Mesh/Pot_A..."
mkdir -p Dataset/Mesh/Pot_A
piece_count=0
for obj in $(find "$INPUT_DIR" -maxdepth 1 -type f -name '*.obj' | sort); do
  if [[ "$obj" =~ ([0-9]{2}) ]]; then
    p="${BASH_REMATCH[1]}"
  else
    ((piece_count++))
    p=$(printf "%02d" "$piece_count")
  fi
  cp -f "$obj" "Dataset/Mesh/Pot_A/Pot_A_Piece_${p}_Mesh.obj"
done

echo "Building preprocessing tools in working container (if needed)..."
if [ ! -x build/mesh_processing_complete ] || [ ! -x build/edgeline_extraction ]; then
  ./build_in_container.sh
fi

echo "Running mesh_processing_complete for $PIECES pieces..."
for p in $(seq -f "%02g" 1 "$PIECES"); do
  echo "  Piece $p"
  $APPTAINER exec --bind "$BASE_DIR:/workspace" --pwd /workspace "$PREP_IMAGE" ./build/mesh_processing_complete A "$p"
done

echo "Running MATLAB axis extraction sequentially for $PIECES pieces..."
module -q load MATLAB/2024b_Update_3 || true
for p in $(seq -f "%02g" 1 "$PIECES"); do
  echo "  Axis piece $p"
  ./matlab_axis_wrapper.sh A "$p"
done

echo "Running edgeline_extraction for $PIECES pieces..."
$APPTAINER exec --bind "$BASE_DIR:/workspace" --pwd /workspace "$PREP_IMAGE" ./build/edgeline_extraction A "$PIECES"

echo "Organizing dataset..."
./organize_dataset.sh

# Rename outputs from Pot_A_* to TRAY naming
OUT_DIR_LATEST=$(readlink -f latest_nurbs_dataset 2>/dev/null || true)
if [ -z "$OUT_DIR_LATEST" ] || [[ "$OUT_DIR_LATEST" != *TPS_Dataset* ]]; then
  # fallback to most recent TPS_Dataset_*
  OUT_DIR_LATEST=$(ls -1dt TPS_Dataset_*/ 2>/dev/null | head -n1 | sed 's:/$::')
fi

if [ -n "$OUT_DIR_LATEST" ] && [ -d "$OUT_DIR_LATEST/SfS_pp" ]; then
  DEST_DIR="${DATASET_NAME}_Dataset_$(date +%Y%m%d)"
  mkdir -p "$DEST_DIR/SfS_pp/"{Surfaces,Breaklines,Axes,Mesh,Point}
  echo "Copying and renaming to $DEST_DIR..."
  for f in "$OUT_DIR_LATEST/SfS_pp/Surfaces/"*.xyz; do
    [ -f "$f" ] || continue; b=$(basename "$f"); cp -f "$f" "$DEST_DIR/SfS_pp/Surfaces/${b/Pot_A/${DATASET_NAME}}"; done
  for f in "$OUT_DIR_LATEST/SfS_pp/Breaklines/"*.pcd; do
    [ -f "$f" ] || continue; b=$(basename "$f"); cp -f "$f" "$DEST_DIR/SfS_pp/Breaklines/${b/Pot_A/${DATASET_NAME}}"; done
  for f in "$OUT_DIR_LATEST/SfS_pp/Axes/"*.xyz; do
    [ -f "$f" ] || continue; b=$(basename "$f"); cp -f "$f" "$DEST_DIR/SfS_pp/Axes/${b/Pot_A/${DATASET_NAME}}"; done
  for f in "$OUT_DIR_LATEST/SfS_pp/Mesh/"*.obj; do
    [ -f "$f" ] || continue; b=$(basename "$f"); cp -f "$f" "$DEST_DIR/SfS_pp/Mesh/${b/Pot_A/${DATASET_NAME}}"; done
  mkdir -p "$DEST_DIR/SfS_pp/Point/$DATASET_NAME"
  for f in Dataset/Point/Pot_A/Pot_A_Piece_*_Point.pcd; do
    [ -f "$f" ] || continue; b=$(basename "$f"); cp -f "$f" "$DEST_DIR/SfS_pp/Point/$DATASET_NAME/${b/Pot_A/${DATASET_NAME}}"; done
  rm -f latest_tray_dataset
  ln -s "$DEST_DIR" latest_tray_dataset
fi

echo "Completed: $(date)"
echo "=== TRAY Pipeline (Working Path) DONE ==="

