#!/bin/bash
#SBATCH --job-name=edgeline_tray_only
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=2:00:00
#SBATCH --output=edgeline_tray_only_%j.out
#SBATCH --error=edgeline_tray_only_%j.err

set -euo pipefail

echo "=== EdgeLine Extraction Only (TRAY) ==="
echo "Started: $(date)"
echo "Job ID: ${SLURM_JOB_ID:-N/A}"

BASE_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"
cd "$BASE_DIR"

INPUT_DIR="${1:-/data/gpfs/projects/punim2657/GARF/input/Tray-000}"
DATASET_NAME="${2:-Tray-000}"

APPTAINER="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
IMAGE="pcl_191_nurbs.sif"

# Ensure required dirs exist
mkdir -p Temp Temp/Data/Pot_A Temp/Temp_edge/Pot_A Dataset/{Mesh,Point,Surfaces,Breaklines,Axes}/Pot_A

# Ensure meshes are present in Temp for edgeline to iterate
for obj in Dataset/Mesh/Pot_A/Pot_A_Piece_*_Mesh.obj; do
  [ -f "$obj" ] || continue
  base=$(basename "$obj")
  cp -f "$obj" "Temp/${base}" || true
done

# Stage axes where edgeline expects them
if compgen -G "NURBS_Output/Axes/Pot_A_Piece_*_Axis.xyz" > /dev/null; then
  cp -f NURBS_Output/Axes/Pot_A_Piece_*_Axis.xyz Dataset/Axes/ 2>/dev/null || true
fi

# Symlink expected relative roots inside original_nurbs_preprocessing
(
  cd original_nurbs_preprocessing
  # Remove existing directories if they are plain dirs (keep if they are symlinks)
  if [ -d Temp ] && [ ! -L Temp ]; then rm -rf Temp; fi
  if [ -d Dataset ] && [ ! -L Dataset ]; then rm -rf Dataset; fi
  ln -sfn ../Temp Temp
  ln -sfn ../Dataset Dataset
)

# Build patched edgeline in a clean build dir
echo "Building EdgeLineExtractionHeadless..."
$APPTAINER exec --bind "$BASE_DIR:/workspace" --pwd /workspace "$IMAGE" /bin/bash -lc "\
  set -e; cd /workspace/original_nurbs_preprocessing; rm -rf build; mkdir -p build; cd build; cmake ..; make -j4 EdgeLineExtractionHeadless"

# Run edgeline from original_nurbs_preprocessing CWD
echo "Running edgeline (headless)..."
$APPTAINER exec --bind "$BASE_DIR:/workspace" --pwd /workspace/original_nurbs_preprocessing "$IMAGE" ./build/EdgeLineExtractionHeadless

echo "EdgeLine completed at: $(date)"

# Assemble TRAY dataset
OUT_DIR="${DATASET_NAME}_Dataset_$(date +%Y%m%d)"
mkdir -p "$OUT_DIR/SfS_pp/"{Surfaces,Breaklines,Axes,Mesh,Point}

echo "Copying and renaming Surfaces..."
for f in Temp/Data/Pot_A/Pot_A_Piece_*_Surface_*.xyz; do
  [ -f "$f" ] || continue
  base=$(basename "$f"); new="${base/Pot_A/${DATASET_NAME}}"; cp -f "$f" "$OUT_DIR/SfS_pp/Surfaces/$new";
done

echo "Copying and renaming Breaklines..."
for f in Dataset/Breaklines/Pot_A/Pot_A_Piece_*_Breakline_*.pcd; do
  [ -f "$f" ] || continue
  base=$(basename "$f"); new="${base/Pot_A/${DATASET_NAME}}"; cp -f "$f" "$OUT_DIR/SfS_pp/Breaklines/$new";
done

echo "Copying and renaming Mesh..."
for f in Dataset/Mesh/Pot_A/Pot_A_Piece_*_Mesh.obj; do
  [ -f "$f" ] || continue
  base=$(basename "$f"); new="${base/Pot_A/${DATASET_NAME}}"; cp -f "$f" "$OUT_DIR/SfS_pp/Mesh/$new";
done

echo "Copying and renaming Point clouds..."
mkdir -p "$OUT_DIR/SfS_pp/Point/$DATASET_NAME"
for f in Dataset/Point/Pot_A/Pot_A_Piece_*_Point.pcd; do
  [ -f "$f" ] || continue
  base=$(basename "$f"); new="${base/Pot_A/${DATASET_NAME}}"; cp -f "$f" "$OUT_DIR/SfS_pp/Point/$DATASET_NAME/$new";
done

echo "Copying and renaming Axes..."
for f in NURBS_Output/Axes/Pot_A_Piece_*_Axis.xyz; do
  [ -f "$f" ] || continue
  base=$(basename "$f"); new="${base/Pot_A/${DATASET_NAME}}"; cp -f "$f" "$OUT_DIR/SfS_pp/Axes/$new";
done

rm -f latest_nurbs_dataset
ln -s "$OUT_DIR" latest_nurbs_dataset

echo "=== Output Summary ==="
find "$OUT_DIR/SfS_pp" -type f | sort | sed 's#^#  #'
echo "Completed: $(date)"
echo "=== EdgeLine Extraction Only (TRAY) DONE ==="
