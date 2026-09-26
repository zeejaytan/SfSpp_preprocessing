#!/bin/bash
# Build the edge-line ordering seam test and the pipeline target.
# Run INSIDE an allocation:  srun --jobid=<ID> --overlap bash build_seam_inner.sh
#
# Kept as its own file rather than an inline `srun bash -lc "..."` chain:
# four levels of nested quoting inside an apptainer exec is how the build
# ended up not running at all, with an exit code that pointed nowhere.

set -uo pipefail

ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing
SRC="${ROOT}/original_nurbs_preprocessing"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF="${ROOT}/pcl_191_nurbs.sif"
LOG=/tmp/seam_build.log

echo "=== seam build ==="
"${APPTAINER}" exec --bind /data:/data "${SIF}" /bin/bash -c "
    cd '${SRC}/build' &&
    rm -rf CMakeCache.txt CMakeFiles &&
    cmake .. &&
    make -j8 test_edge_line_ordering EdgeLineExtractionHeadless
" > "${LOG}" 2>&1
rc=$?
echo "BUILD-EXIT=${rc}"
if [ "${rc}" -ne 0 ]; then
    echo "--- errors ---"
    # Must include CMake's own wording ("CMake Error at ...", "Configuring
    # incomplete") -- an earlier grep for compiler-style errors only reported
    # a configure failure with no reason attached, which cost a round trip.
    grep -E 'error:|CMake Error|Error [0-9]|No rule to make|Configuring incomplete' "${LOG}" | head -n 20 || true
    echo "--- last 12 lines ---"
    tail -n 12 "${LOG}"
    exit 1
fi
echo "--- built:"
ls -lh "${SRC}/build/test_edge_line_ordering" "${SRC}/build/EdgeLineExtractionHeadless" | awk '{print "  " $5, $9}'
