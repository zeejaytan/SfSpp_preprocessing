#!/bin/bash
# Rebuild MeshPreprocessingHeadless inside the container. In a file because
# inline srun chains with nested quoting break; this exact failure has
# happened twice before and the file approach worked both times.
#
# Run inside a holder:  srun --jobid=<ID> --overlap bash build_mesh.sh

set -uo pipefail

ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing
SRC="${ROOT}/original_nurbs_preprocessing"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF="${ROOT}/pcl_191_nurbs.sif"
LOG=/tmp/mesh_build.log

"${APPTAINER}" exec --bind /data:/data "${SIF}" /bin/bash -c \
    "cd '${SRC}/build' && cmake .. && make -j8 MeshPreprocessingHeadless" \
    > "${LOG}" 2>&1
rc=$?
echo "BUILD-EXIT=${rc}"
if [ "${rc}" -ne 0 ]; then
    grep -E 'error:|Error [0-9]|No rule to make|CMake Error' "${LOG}" | head -n 15 || true
    tail -n 10 "${LOG}"
    exit 1
fi
ls -lh "${SRC}/build/MeshPreprocessingHeadless" | awk '{print "  built:", $5, $9}'
