#!/bin/bash
# Ticket 04: run Pot_A with the interior/exterior classification active.
#
# The classifier fires only when an axis file exists at
# Dataset/Axes/<piece>_Axis.xyz relative to the run tree. Earlier isolated
# runs had no axes staged, so every piece would have taken the warn-and-keep
# path. This stages the 8 committed axis files, then runs the proven
# mesh-then-edgeline configuration (run_pota_fresh3.sh pattern).
#
# Verification is by the [SFS-T04] log lines (one decision per piece, with
# the vote margin) and by file count, never by exit code alone.
#
# Run inside a holder:  srun --jobid=<ID> --overlap bash run_ticket04_pota.sh

set -uo pipefail

ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing
BUILD="${ROOT}/original_nurbs_preprocessing/build"
TREE="${ROOT}/diag_t04_pota"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF="${ROOT}/pcl_191_nurbs.sif"
POT=Pot_A
MLOG=/tmp/t04_mesh.log
ELOG=/tmp/t04_edge.log

for b in MeshPreprocessingHeadless EdgeLineExtractionHeadless; do
    [ -x "${BUILD}/${b}" ] || { echo "ERROR: ${b} not built"; exit 1; }
done
if [ "$(strings "${BUILD}/EdgeLineExtractionHeadless" 2>/dev/null | grep -c "SFS-T04" || true)" = "0" ]; then
    echo "ERROR: ticket-04 code not in the binary. Run build_ticket04.sh first."
    exit 1
fi
echo "ticket-04 code present in binary: yes"

echo "### stage inputs"
rm -rf "${TREE}"
mkdir -p "${TREE}/Temp/Data/${POT}" "${TREE}/Temp/Axes" \
         "${TREE}/Dataset/Mesh/${POT}" "${TREE}/Dataset/Point/${POT}" \
         "${TREE}/Dataset/Surfaces/${POT}" "${TREE}/Dataset/Breaklines/${POT}" \
         "${TREE}/Dataset/Axes"
n=0
for f in "${ROOT}/Dataset/Mesh/${POT}"/*.obj; do
    [ -e "${f}" ] || continue
    cp -L "${f}" "${TREE}/Dataset/Mesh/${POT}/"; n=$((n + 1))
done
for f in "${ROOT}/Dataset/Point/${POT}"/*; do
    [ -e "${f}" ] || continue
    cp -L "${f}" "${TREE}/Dataset/Point/${POT}/"
done
for f in "${ROOT}/Dataset/Axes/${POT}"/*_Axis.xyz; do
    [ -e "${f}" ] || continue
    cp -L "${f}" "${TREE}/Dataset/Axes/"
done
echo "    ${n} meshes, $(ls "${TREE}/Dataset/Point/${POT}" | wc -l) point clouds, $(ls "${TREE}/Dataset/Axes" | wc -l) axis files"
[ "$(ls "${TREE}/Dataset/Axes" 2>/dev/null | wc -l)" -eq 8 ] || {
    echo "ERROR: expected 8 axis files"; exit 1; }

echo
echo "### mesh stage"
( cd "${TREE}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" \
    env POT_NAME="${POT}" "${BUILD}/MeshPreprocessingHeadless" ) > "${MLOG}" 2>&1
echo "    exit $? (not trusted)"
DATA="${TREE}/Temp/Data/${POT}"
echo "    Surface_0.xyz: $(ls "${DATA}"/*_Surface_0.xyz 2>/dev/null | wc -l)"
if [ "$(ls "${DATA}"/*_Surface_0.xyz 2>/dev/null | wc -l)" -eq 0 ]; then
    tail -n 10 "${MLOG}" | sed 's/^/       /'
    exit 1
fi

echo
echo "### edgeline stage (classifier active)"
( cd "${TREE}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" \
    env POT_NAME="${POT}" "${BUILD}/EdgeLineExtractionHeadless" ) > "${ELOG}" 2>&1
echo "    exit $? (not trusted)"
echo "--- SFS-T04 decisions:"
grep "SFS-T04" "${ELOG}" 2>/dev/null | head -n 30 || echo "    ** NO SFS-T04 LINES -- the classifier never ran"
BL="${TREE}/Dataset/Breaklines/${POT}"
echo "    breakline .pcd written: $(ls "${BL}"/*.pcd 2>/dev/null | wc -l)"
echo "    pieces sequenced: $(grep -c "ADAPTIVE SEQUENCING" "${ELOG}" 2>/dev/null || true)"
