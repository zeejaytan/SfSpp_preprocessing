#!/bin/bash
# Ticket 01: build the seam test and run it, in one step inside a holder.
#   srun --jobid=<ID> --overlap bash run_ticket01.sh
#
# Two scripts, one srun. Previously these were separate calls and separate
# round trips; and an inline `srun bash -c "a && b"` chain is exactly the
# nested-quoting shape that failed earlier, so the sequencing lives in a
# file.

set -uo pipefail

echo "############################################################"
echo "# 1. build"
echo "############################################################"
bash build_seam_inner.sh
rc=$?
if [ "${rc}" -ne 0 ]; then
    echo "BUILD FAILED -- not running tests against a stale binary"
    exit 1
fi

echo
echo "############################################################"
echo "# 2. tests"
echo "############################################################"
bash run_seam_tests_inner.sh all

echo
echo "############################################################"
echo "# 3. ctest, so the DISABLED_/enabled split is visible"
echo "############################################################"
ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
"${APPTAINER}" exec --bind /data:/data "${ROOT}/pcl_191_nurbs.sif" \
    ctest --test-dir "${ROOT}/original_nurbs_preprocessing/build" 2>&1 | tail -n 25
