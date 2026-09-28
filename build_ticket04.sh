#!/bin/bash
# Ticket 04: build the edgeline binary (with interior/exterior classification)
# and the classifier unit tests. In a file because inline srun chains with
# nested quoting break; verified approach from the ticket-11 work.
#
# Run inside a holder:  srun --jobid=<ID> --overlap bash build_ticket04.sh

set -uo pipefail

ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing
SRC="${ROOT}/original_nurbs_preprocessing"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF="${ROOT}/pcl_191_nurbs.sif"
LOG=/tmp/ticket04_build.log

echo "=== ticket 04 build ==="
"${APPTAINER}" exec --bind /data:/data "${SIF}" /bin/bash -c \
    "cd '${SRC}/build' && cmake .. && make -j8 EdgeLineExtractionHeadless test_surface_classify" \
    > "${LOG}" 2>&1
rc=$?
echo "BUILD-EXIT=${rc}"
if [ "${rc}" -ne 0 ]; then
    echo "--- errors ---"
    grep -E 'error:|Error [0-9]|No rule to make|CMake Error' "${LOG}" | head -n 20 || true
    echo "--- last 12 lines ---"
    tail -n 12 "${LOG}"
    exit 1
fi
echo "--- built:"
ls -lh "${SRC}/build/EdgeLineExtractionHeadless" "${SRC}/build/test_surface_classify" 2>&1 | awk '{print "  " $5, $9}'

echo
echo "=== classifier unit tests ==="
"${APPTAINER}" exec --bind /data:/data "${SIF}" /bin/bash -c \
    "cd '${SRC}/build' && ./test_surface_classify" 2>&1 | tail -n 12
