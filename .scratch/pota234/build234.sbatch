#!/bin/bash
# POTA-234: build new mesh binary with plane-continuity rule (inside PCL container).
#SBATCH --job-name=fix234-build
#SBATCH --account=punim2657
#SBATCH --partition=sapphire,cascade
#SBATCH --time=03:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --output=build234_%j.out
#SBATCH --error=build234_%j.err
set -uo pipefail
WROOT=/data/gpfs/projects/punim2657/sfs-fix-234
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif
rm -rf "$WROOT/build-234"
mkdir -p "$WROOT/build-234"
cd "$WROOT/build-234"
"$APPTAINER" exec --bind /data:/data "$SIF" cmake -DCMAKE_BUILD_TYPE=Release .. > cmake_config.log 2>&1
"$APPTAINER" exec --bind /data:/data "$SIF" make MeshPreprocessingHeadless -j8 > make_mesh.log 2>&1
md5sum MeshPreprocessingHeadless
