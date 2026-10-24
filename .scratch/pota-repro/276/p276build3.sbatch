#!/bin/bash
#SBATCH --job-name=p276build3
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --output=/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1121_0ab0935_p276-merge/logs/p276build3_%j.out
set -u
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif
WT=/data/gpfs/projects/punim2657/sfs_preprocessing.wt/276
cd $WT || exit 9
echo SRC_MD5=$(md5sum mesh_processing_headless.cpp | cut -d' ' -f1)
grep -c 'PAIR-276' mesh_processing_headless.cpp
cd build || exit 9
$APT exec --bind /data:/data $SIF make -j8 MeshPreprocessingHeadless > make276c.log 2>&1
echo EXIT_MAKE=$?
grep -E 'error:' make276c.log | head -20
ls -l MeshPreprocessingHeadless | head -2
md5sum MeshPreprocessingHeadless
echo PAIR_STRINGS=$(strings MeshPreprocessingHeadless | grep -c 'PAIR-276')
echo SWITCH_STRINGS=$(strings MeshPreprocessingHeadless | grep -c 'SFS_MERGE_PAIRS')
echo BUILD3_DONE
