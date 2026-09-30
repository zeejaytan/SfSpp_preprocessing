#!/bin/bash
# Build both headless binaries. In a file: inline nested quoting breaks.
# Run inside a holder:  srun --jobid=<ID> --overlap bash build_all.sh

set -uo pipefail

ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing
SRC="${ROOT}/original_nurbs_preprocessing"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF="${ROOT}/pcl_191_nurbs.sif"
LOG=/tmp/all_build.log

"${APPTAINER}" exec --bind /data:/data "${SIF}" /bin/bash -c \
    "cd '${SRC}/build' && cmake .. && make -j8 MeshPreprocessingHeadless EdgeLineExtractionHeadless test_surface_classify test_edge_line_ordering test_boundary_filter" \
    > "${LOG}" 2>&1
rc=$?
echo "BUILD-EXIT=${rc}"
if [ "${rc}" -ne 0 ]; then
    grep -E 'error:|Error [0-9]|No rule to make|CMake Error' "${LOG}" | head -n 20 || true
    tail -n 12 "${LOG}"
    exit 1
fi
ls -lh "${SRC}/build/MeshPreprocessingHeadless" "${SRC}/build/EdgeLineExtractionHeadless" | awk '{print "  built:", $5, $9}'
echo
echo "=== unit tests ==="
"${APPTAINER}" exec --bind /data:/data "${SIF}" /bin/bash -c \
    "cd '${SRC}/build' && ./test_surface_classify && ./test_edge_line_ordering clean-rim && ./test_edge_line_ordering no-revisit && ./test_boundary_filter" 2>&1 | tail -n 16
