#!/bin/bash
# Ticket 04/07: run the Juglet with the interior/exterior vote live.
#
# The vote could never fire on the Juglet before: no axis files were staged.
# All 9 axes were found in Juglet_Dataset_20260916/SfS_pp/Axes/ and staged
# at Dataset/Axes/Juglet/ (untracked cluster data, like Pot_A's). This is
# the first run where per-sherd wall selection happens on the Juglet.
#
# Mirrors run_ticket04_pota.sh (proven): isolated tree, mesh then edgeline,
# SFS-T04 decisions + exchange audit + file counts. Verification by
# artifacts, never by exit code.
#
# What it can and cannot show: which wall the vote picks per sherd (9 votes
# with margins), and the resulting breaklines for the laptop gate probe
# (honest denominator 10). It cannot change the 8 non-touching pairs --
# material limit, recorded in ticket 07.
#
# Run inside a holder:  srun --jobid=<ID> --overlap bash run_ticket04_juglet.sh

set -uo pipefail

ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing
BUILD="${ROOT}/original_nurbs_preprocessing/build"
TREE="${ROOT}/diag_t04_juglet"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF="${ROOT}/pcl_191_nurbs.sif"
POT=Juglet
MLOG=/tmp/t04j_mesh.log
ELOG=/tmp/t04j_edge.log

for b in MeshPreprocessingHeadless EdgeLineExtractionHeadless; do
    [ -x "${BUILD}/${b}" ] || { echo "ERROR: ${b} not built"; exit 1; }
done
if [ "$(strings "${BUILD}/EdgeLineExtractionHeadless" 2>/dev/null | grep -c "SFS-T04" || true)" = "0" ]; then
    echo "ERROR: ticket-04 code not in the binary. Rebuild first."
    exit 1
fi
echo "ticket-04 code present in binary: yes"

echo "### stage inputs"
rm -rf "${TREE}"
mkdir -p "${TREE}/Temp/Data/${POT}" "${TREE}/Temp/Axes" \
         "${TREE}/Dataset/Mesh/${POT}" "${TREE}/Dataset/Point/${POT}" \
         "${TREE}/Dataset/Surfaces/${POT}" "${TREE}/Dataset/Breaklines/${POT}" \
         "${TREE}/Dataset/Axes"
for f in "${ROOT}/Dataset/Mesh/${POT}"/*.obj; do
    [ -e "${f}" ] || continue
    cp -L "${f}" "${TREE}/Dataset/Mesh/${POT}/"
done
for f in "${ROOT}/Dataset/Point/${POT}"/*; do
    [ -e "${f}" ] || continue
    cp -L "${f}" "${TREE}/Dataset/Point/${POT}/"
done
for f in "${ROOT}/Dataset/Axes/${POT}"/*_Axis.xyz; do
    [ -e "${f}" ] || continue
    cp -L "${f}" "${TREE}/Dataset/Axes/"
done
echo "    meshes: $(ls "${TREE}/Dataset/Mesh/${POT}" | wc -l), point clouds: $(ls "${TREE}/Dataset/Point/${POT}" | wc -l), axes: $(ls "${TREE}/Dataset/Axes" | wc -l)"
[ "$(ls "${TREE}/Dataset/Axes" 2>/dev/null | wc -l)" -eq 9 ] || {
    echo "ERROR: expected 9 Juglet axis files"; exit 1; }

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
echo "--- mergeClusters passes (preproc 03 settlement):"
grep "mergeClusters pass" "${MLOG}" 2>/dev/null || echo "    ** NO PASS LINES"
cp -f "${MLOG}" "${TREE}/mesh_stage.log" 2>/dev/null || true

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
echo "--- exchange audit:"
for p in 1 2 3 4 5 6 7 8 9; do
    t0="${TREE}/Temp/Data/${POT}/Juglet_Piece_${p}_Surface_0.xyz"
    o0="${TREE}/Dataset/Surfaces/${POT}/Juglet_Piece_${p}_Surface_0.xyz"
    o1="${TREE}/Dataset/Surfaces/${POT}/Juglet_Piece_${p}_Surface_1.xyz"
    [ -f "${t0}" ] || { echo "    piece ${p}: MISSING surfaces"; continue; }
    if cmp -s "${t0}" "${o0}"; then st="KEPT(order unchanged)"; elif cmp -s "${t0}" "${o1}"; then st="EXCHANGED"; else st="NEITHER -- unexpected content"; fi
    echo "    piece ${p}: ${st}"
done
