#!/bin/bash
# Run the edge-line ordering seam tests inside the container.
#   srun --jobid=<ID> --overlap bash run_seam_tests_inner.sh [test-name]
#
# In a file rather than an inline chain: nested quoting through
# srun -> bash -c -> apptainer exec -> bash -c kept breaking, and each
# attempt cost a round trip to find out.
#
# The tests are registered with CTest as DISABLED_ (see CMakeLists.txt), so
# running them here is deliberate: this is how the currently-failing
# assertions are observed and recorded.

set -uo pipefail

ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF="${ROOT}/pcl_191_nurbs.sif"
BIN="${ROOT}/original_nurbs_preprocessing/build/test_edge_line_ordering"
LOG=/tmp/seam_tests.log

[ -x "${BIN}" ] || { echo "ERROR: test binary missing -- build it first"; exit 1; }

echo "=== running seam tests: ${1:-all} ==="
"${APPTAINER}" exec --bind /data:/data "${SIF}" /bin/bash -c \
    "cd '${ROOT}/original_nurbs_preprocessing/build' && ./test_edge_line_ordering ${1:-}" \
    > "${LOG}" 2>&1
rc=$?
cat "${LOG}"
echo "TEST-EXIT=${rc}"
exit 0
