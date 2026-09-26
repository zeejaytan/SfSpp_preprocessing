#!/bin/bash
# Build the edge-line ordering seam test and the pipeline target, inside a
# held allocation. No `| tail` on the build: that swallows the exit code,
# which is how an earlier run reported BUILD-EXIT=0 while the target did
# not exist. The log is read back by the caller instead.

set -uo pipefail
JOBID="${1:?usage: build_seam.sh <HOLDER_JOBID>}"
ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing
SRC="${ROOT}/original_nurbs_preprocessing"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF="${ROOT}/pcl_191_nurbs.sif"
LOG=/tmp/seam_build.log

echo "=== building seam test + pipeline (holder ${JOBID}) ==="
srun --jobid="${JOBID}" --overlap --cpus-per-task=8 bash -lc "
  ${APPTAINER} exec --bind /data:/data ${SIF} bash -c '
    cd ${SRC}/build &&
    rm -rf CMakeCache.txt CMakeFiles &&
    cmake .. &&
    make -j8 test_edge_line_ordering EdgeLineExtractionHeadless
  ' > ${LOG} 2>&1
"
rc=$?
echo "BUILD-EXIT=${rc}"
if [ "${rc}" -ne 0 ]; then
    echo "--- errors from the log ---"
    grep -E "error:|Error [0-9]|No rule to make" "${LOG}" | head -n 20 || true
    echo "--- last lines ---"
    tail -n 12 "${LOG}"
    exit 1
fi
echo "--- targets built:"
ls -lh "${SRC}/build/test_edge_line_ordering" "${SRC}/build/EdgeLineExtractionHeadless" 2>&1 | awk '{print "  " $5, $9}'
