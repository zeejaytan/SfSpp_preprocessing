#!/bin/bash
#SBATCH --job-name=tray_to_pcd
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=2:00:00
#SBATCH --output=tray_to_pcd_%j.out
#SBATCH --error=tray_to_pcd_%j.err

set -euo pipefail

echo "=== Sampling Tray OBJ -> PCD with normals (Open3D in container) ==="
echo "Started: $(date)"
echo "Job ID: ${SLURM_JOB_ID:-N/A}"

BASE_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"
cd "$BASE_DIR"

INPUT_DIR="${1:-/data/gpfs/projects/punim2657/GARF/input/Tray-000}"
DATASET_NAME="${2:-}"
if [ -z "$DATASET_NAME" ]; then
  DATASET_NAME="$(basename "$INPUT_DIR")"
fi
echo "Input: $INPUT_DIR"
echo "Dataset name: $DATASET_NAME"

APPTAINER="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
IMAGE="pcl_191_nurbs.sif"

mkdir -p Dataset/Mesh/Pot_A Dataset/Point/Pot_A

# Build the OBJ->PCD converter inside the container (dedicated build dir)
$APPTAINER exec --bind "$BASE_DIR:/workspace" "$IMAGE" /bin/bash -lc "\
set -e; \
cd /workspace/original_nurbs_preprocessing; \
rm -rf build_obj2pcd; \
mkdir -p build_obj2pcd; \
cd build_obj2pcd; \
cmake ..; \
make -j2 ObjToPcd"

mapfile -t OBJ_LIST < <(find "$INPUT_DIR" -maxdepth 1 -type f -name '*.obj' | sort)
if [ ${#OBJ_LIST[@]} -eq 0 ]; then
  echo "ERROR: No OBJ files in $INPUT_DIR" >&2
  exit 1
fi

piece_count=0
for obj_path in "${OBJ_LIST[@]}"; do
  obj_file=$(basename "$obj_path")
  if [[ "$obj_file" =~ ([0-9]{2}) ]]; then
    piece_num="${BASH_REMATCH[1]}"
  else
    ((piece_count++))
    piece_num=$(printf "%02d" "$piece_count")
  fi

  mesh_dst="Dataset/Mesh/Pot_A/Pot_A_Piece_${piece_num}_Mesh.obj"
  pcd_dst="Dataset/Point/Pot_A/Pot_A_Piece_${piece_num}_Point.pcd"
  echo "Sampling $obj_file -> $pcd_dst"
  cp -f "$obj_path" "$mesh_dst"
  $APPTAINER exec --bind "$BASE_DIR:/workspace" "$IMAGE" /bin/bash -lc \
    "/workspace/original_nurbs_preprocessing/build_obj2pcd/ObjToPcd '$mesh_dst' '$pcd_dst'"
done

echo "Completed: $(date)"
echo "=== Sampling DONE ==="
