#!/bin/bash
#SBATCH --job-name=edgeline_tray
#SBATCH --partition=sapphire
#SBATCH --time=04:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=6
#SBATCH --output=edgeline_tray_%j.out
#SBATCH --error=edgeline_tray_%j.err

set -euo pipefail

BASE_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"
APPTAINER="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
# Use the working SFS container that we build against
IMAGE="/data/gpfs/projects/punim2657/sfs_main/sfspreproc.sif"

if [ ! -f "$IMAGE" ]; then
  echo "ERROR: Container not found: $IMAGE" >&2
  exit 1
fi

cd "${BASE_DIR}"

echo "=== Building EdgeLineExtraction inside container environment ==="
./build_in_container.sh

if [ ! -x ./EdgeLineExtraction ]; then
  echo "ERROR: Failed to build EdgeLineExtraction via build_in_container.sh" >&2
  exit 1
fi

echo "=== Running EdgeLineExtraction (Tray) ==="
echo "Using image: $IMAGE"

# Run from original_nurbs_preprocessing so relative paths (../Dataset, ../Temp) are correct
cd "${BASE_DIR}/original_nurbs_preprocessing"
mkdir -p ../Dataset/Breaklines/Pot_A ../Dataset/Surfaces/Pot_A ../Temp/Temp_edge/Pot_A

$APPTAINER exec --bind "${BASE_DIR}:/workspace" --pwd /workspace/original_nurbs_preprocessing "$IMAGE" ../EdgeLineExtraction

echo "=== EdgeLineExtraction DONE ==="
