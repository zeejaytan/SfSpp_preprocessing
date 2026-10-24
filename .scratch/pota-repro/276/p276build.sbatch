#!/bin/bash
#SBATCH --job-name=p276build
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --output=/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1121_0ab0935_p276-merge/logs/p276build_%j.out
set -u
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif
WT=/data/gpfs/projects/punim2657/sfs_preprocessing.wt/276
cd $WT || exit 9
echo "SRC_MD5=$(md5sum mesh_processing_headless.cpp | cut -d' ' -f1)"
echo "HEAD=$(git log --oneline -1)"
mkdir -p build && cd build || exit 9
$APT exec --bind /data:/data $SIF cmake -DCMAKE_BUILD_TYPE=Release $WT > cmake276.log 2>&1
echo "EXIT_CMAKE=$?"
grep -E 'CMAKE_BUILD_TYPE|CMAKE_HOME_DIRECTORY' CMakeCache.txt
$APT exec --bind /data:/data $SIF make -j8 MeshPreprocessingHeadless > make276.log 2>&1
echo "EXIT_MAKE=$?"
grep -E 'error:' make276.log | head -10
grep -c 'warning:' make276.log
ls -l MeshPreprocessingHeadless 2>&1 | head -2
md5sum MeshPreprocessingHeadless 2>&1
echo "DIAG_STRINGS=$(strings MeshPreprocessingHeadless | grep -c 'MERGE-DIAG-276')"
echo "SFS_MERGE_DIAG_STRINGS=$(strings MeshPreprocessingHeadless | grep -c 'SFS_MERGE_DIAG')"
echo BUILD_DONE
