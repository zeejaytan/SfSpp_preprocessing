#!/bin/bash
# POTA-159 BUILD: ADAPT variant in relay worktree.
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --time=02:00:00
#SBATCH --nodes=1 --cpus-per-task=8 --mem=32G
#SBATCH --job-name=p159_build
set -uo pipefail
P159=/data/gpfs/projects/punim2657/pota159_repro
SUB=/data/gpfs/projects/punim2657/sfs_cure_1c6a8f9/original_nurbs_preprocessing
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif
echo "=== POTA-159 BUILD job ${SLURM_JOB_ID} ==="; date; hostname
cd ${SUB}/build
$APT exec --bind /data:/data $SIF /bin/bash -c "cd $SUB/build && make EdgeLineExtractionHeadless -j4" 2>&1 | tail -15
ls -la EdgeLineExtractionHeadless
for m in "FACE VETO" "ADAPT VETO" "POTA159_ADAPT" "veto_align_"; do grep -aq "$m" EdgeLineExtractionHeadless && echo "marker OK: $m" || { echo "MARKER MISSING: $m"; exit 1; }; done
cp EdgeLineExtractionHeadless $P159/EdgeLineExtractionHeadless_ADAPT
md5sum $P159/EdgeLineExtractionHeadless_ADAPT $P159/EdgeLineExtractionHeadless_CURED
date; echo P159-BUILD-DONE
