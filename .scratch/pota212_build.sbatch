#!/bin/bash
# POTA-212 build: cmake configure + build INSIDE the PCL container (host cmake has no PCL).
#SBATCH --job-name=splitwalk212-build
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --output=build-212_%j.out
#SBATCH --error=build-212_%j.err
set -euo pipefail
WROOT=/data/gpfs/projects/punim2657/sfs-splitwalk-212
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif
rm -rf "$WROOT/build-212"
"$APPTAINER" exec --bind /data:/data "$SIF" bash -c 'cd "$1" && cmake -S . -B build-212 -DCMAKE_BUILD_TYPE=Release && cmake --build build-212 --target MeshPreprocessingHeadless EdgeLineExtractionHeadless -j8' _ "$WROOT" 2>&1 | tail -n 30
echo "=== BUILD DONE ==="
ls -la "$WROOT/build-212/MeshPreprocessingHeadless" "$WROOT/build-212/EdgeLineExtractionHeadless"
md5sum "$WROOT/build-212/EdgeLineExtractionHeadless" | tee "$WROOT/edge_binary_md5.txt"
