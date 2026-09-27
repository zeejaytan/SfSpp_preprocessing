#!/bin/bash
# Ticket 10, the real version: does the 3.5 mm offset come from the surface
# choice?
#
# WHY THIS EXISTS INSTEAD OF THE PYTHON TEST
# The Python reimplementation was tried first and correctly reported itself
# UNVALIDATED: its rim from Surface_0 landed 13.74 mm from the reference where
# the real pipeline lands 3.49 mm. A reimplementation that cannot reproduce
# the pipeline has no standing to judge a different surface, so its answer
# would have been noise. This runs the real extractor instead.
#
# THE TEST
# Piece 3 has Surface_0 and Surface_1 as separate point clouds, both already
# produced by the mesh stage. Normally the extractor emits a breakline for
# each. This run SWAPS them, so the file called Breakline_0 is built from
# Surface_1, and:
#
#   - if the swapped Breakline_0 lands near the reference (which is built
#     from Surface_0), the surface choice is the whole story and ticket 04's
#     selection rule is the fix;
#   - if it is still ~3.5 mm off, the rim is displaced whichever surface it
#     comes from, the cause is upstream of the selection, and ticket 04 is
#     the wrong place to be working.
#
# The swap is done by COPYING one file over the other in an isolated tree.
# Nothing outside the tree is touched, and the originals are restored by
# deleting the tree. Verified by file count, never by exit code.
#
# Run inside a holder:  srun --jobid=<ID> --overlap bash run_surface_ablation.sh

set -uo pipefail

ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing
BUILD="${ROOT}/original_nurbs_preprocessing/build"
TREE="${ROOT}/diag_surface_ab"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF="${ROOT}/pcl_191_nurbs.sif"
POT=Pot_A
LOG=/tmp/surf_ab.log

[ -x "${BUILD}/EdgeLineExtractionHeadless" ] || { echo "ERROR: not built"; exit 1; }

stage() {
    rm -rf "${TREE}"
    mkdir -p "${TREE}/Temp/Data/${POT}" "${TREE}/Temp/Axes" \
             "${TREE}/Dataset/Mesh/${POT}" "${TREE}/Dataset/Point/${POT}" \
             "${TREE}/Dataset/Surfaces/${POT}" "${TREE}/Dataset/Breaklines/${POT}"
    for f in "${ROOT}/Dataset/Mesh/${POT}"/*.obj; do
        [ -e "${f}" ] || continue
        cp -L "${f}" "${TREE}/Dataset/Mesh/${POT}/"
    done
    for f in "${ROOT}/Dataset/Point/${POT}"/*; do
        [ -e "${f}" ] || continue
        cp -L "${f}" "${TREE}/Dataset/Point/${POT}/"
    done
}

run_extract() {
    local tag="$1"
    ( cd "${TREE}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" \
        env POT_NAME="${POT}" "${BUILD}/EdgeLineExtractionHeadless" ) \
        > "${LOG}.${tag}" 2>&1
    local bl="${TREE}/Dataset/Breaklines/${POT}"
    local n
    n=$(ls "${bl}"/Pot_A_Piece_03_Breakline_0.pcd 2>/dev/null | wc -l)
    echo "  ${tag}: exit $?  breakline_0 present: ${n}"
    if [ "${n}" -eq 0 ]; then
        echo "     ** nothing produced; tail:"
        tail -n 8 "${LOG}.${tag}" | sed 's/^/        /'
        return 1
    fi
    cp "${bl}/Pot_A_Piece_03_Breakline_0.pcd" \
       "${ROOT}/diag_surface_ab_out_${tag}.pcd"
    return 0
}

echo "### baseline: surfaces as the mesh stage wrote them"
stage
S0="${TREE}/Temp/Data/${POT}/Pot_A_Piece_03_Surface_0.xyz"
S1="${TREE}/Temp/Data/${POT}/Pot_A_Piece_03_Surface_1.xyz"
echo "  Surface_0: $(wc -l < "${S0}" 2>/dev/null || echo MISSING) lines"
echo "  Surface_1: $(wc -l < "${S1}" 2>/dev/null || echo MISSING) lines"
if [ ! -s "${S0}" ] || [ ! -s "${S1}" ]; then
    echo "ERROR: piece 3 surfaces not in the staged tree."
    echo "       They come from the mesh stage; re-run run_pota_fresh3.sh first,"
    echo "       or copy them from ${ROOT}/diag_pota3/Temp/Data/${POT}/."
    exit 1
fi
run_extract baseline || exit 1

echo
echo "### swapped: Breakline_0 will be built from Surface_1"
stage
S0="${TREE}/Temp/Data/${POT}/Pot_A_Piece_03_Surface_0.xyz"
S1="${TREE}/Temp/Data/${POT}/Pot_A_Piece_03_Surface_1.xyz"
cp "${S1}" "${S0}.keep"
cp "${S1}" "${S0}"          # Surface_0 now holds what was Surface_1
echo "  swapped. Surface_0 is now $(wc -l < "${S0}") lines, Surface_1 $(wc -l < "${S1}")"
if cmp -s "${S0}" "${S1}"; then
    echo "  swap confirmed (the two paths now hold identical content)"
else
    echo "  ** swap did not take effect"
    exit 1
fi
run_extract swapped || exit 1

echo
echo "### both breaklines written, for the laptop to measure"
for t in baseline swapped; do
    f="${ROOT}/diag_surface_ab_out_${t}.pcd"
    [ -f "${f}" ] && echo "  ${f} ($(wc -l < "${f}") lines)"
done
echo
echo "Fetch and measure with:"
echo "  scp spartan:${ROOT}/diag_surface_ab_out_*.pcd <laptop>/artifacts/"
echo
echo "Compare each against the AUTHORS' piece-3 rim:"
echo "  artifacts/pot_a_bl/Pot_A_Piece_03_Breakline_0.pcd  (built from Surface_0)"
echo "If 'swapped' is near the reference and 'baseline' is 3.5 mm off, the"
echo "surface choice is the cause. If both are ~3.5 mm off, it is upstream."
