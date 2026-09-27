#!/bin/bash
# Ticket 10: extend the surface-swap ablation to ALL EIGHT Pot_A sherds.
#
# WHY
# Piece 3 gave 3.49 mm from Surface_0 and 0.67 mm from Surface_1, with the
# baseline arm reproducing the earlier run to 0.00 mm. That is decisive for
# piece 3 and it revives ticket 04, whose premise I had written off on the
# strength of a normal-direction measurement that used the MESH's normal
# rather than the wall's -- and a wall-to-wall displacement is tangential to
# the mesh, so that test could not have detected it.
#
# One sherd is a lead, not a result. If the swap helps on all eight then
# ticket 04 is the fix. If it helps on some, the rule "Surface_0 = largest
# cluster" is choosing the wrong wall on those and the selection needs to be
# conditional. Either way the per-piece table is what the ticket needs.
#
# For each sherd, both arms are extracted into the isolated tree and the two
# breaklines are copied out for the laptop to score against the authors' rims.
# Nothing outside the tree is touched.
#
# Run inside a holder:  srun --jobid=<ID> --overlap bash run_surface_ablation_all.sh

set -uo pipefail

ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing
BUILD="${ROOT}/original_nurbs_preprocessing/build"
TREE="${ROOT}/diag_surface_all"
OUTDIR="${ROOT}/diag_surface_all_out"
MESHSTAGE="${ROOT}/diag_pota3/Temp/Data/Pot_A"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF="${ROOT}/pcl_191_nurbs.sif"
POT=Pot_A

[ -x "${BUILD}/EdgeLineExtractionHeadless" ] || { echo "ERROR: not built"; exit 1; }
[ -d "${MESHSTAGE}" ] || { echo "ERROR: no mesh-stage output at ${MESHSTAGE}"; exit 1; }

rm -rf "${OUTDIR}"; mkdir -p "${OUTDIR}"

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
    for f in "${MESHSTAGE}"/*; do
        [ -e "${f}" ] || continue
        cp -L "${f}" "${TREE}/Temp/Data/${POT}/"
    done
    local n_obj n_s0
    n_obj=$(ls "${TREE}/Temp/Data/${POT}"/*.obj 2>/dev/null | wc -l)
    n_s0=$(ls "${TREE}/Temp/Data/${POT}"/*_Surface_0.xyz 2>/dev/null | wc -l)
    echo "    staged: ${n_obj} obj, ${n_s0} Surface_0.xyz"
    [ "${n_obj}" -eq 8 ] && [ "${n_s0}" -eq 8 ] || { echo "    ERROR: incomplete"; return 1; }
    return 0
}

extract() {
    local tag="$1"
    ( cd "${TREE}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" \
        env POT_NAME="${POT}" "${BUILD}/EdgeLineExtractionHeadless" ) \
        > "/tmp/surf_all_${tag}.log" 2>&1
    local bl="${TREE}/Dataset/Breaklines/${POT}" n
    n=$(ls "${bl}"/Pot_A_Piece_*_Breakline_0.pcd 2>/dev/null | wc -l)
    echo "    ${tag}: exit $?  breakline_0 files: ${n}"
    if [ "${n}" -lt 8 ]; then
        echo "    ** expected 8, got ${n}. Tail:"
        tail -n 6 "/tmp/surf_all_${tag}.log" | sed 's/^/       /'
        return 1
    fi
    for f in "${bl}"/Pot_A_Piece_*_Breakline_0.pcd; do
        cp "${f}" "${OUTDIR}/$(basename "${f}" .pcd)_${tag}.pcd"
    done
    return 0
}

echo "### arm 1: baseline (surfaces as the mesh stage wrote them)"
stage || exit 1
extract baseline || exit 1

echo
echo "### arm 2: swapped (Surface_0 and Surface_1 exchanged everywhere)"
stage || exit 1
sw=0
for p in 01 02 03 04 05 06 07 08; do
    d="${TREE}/Temp/Data/${POT}"
    s0="${d}/Pot_A_Piece_${p}_Surface_0.xyz"
    s1="${d}/Pot_A_Piece_${p}_Surface_1.xyz"
    if [ ! -s "${s0}" ] || [ ! -s "${s1}" ]; then
        echo "  piece ${p}: missing a surface, skipping swap for it"
        continue
    fi
    if [ ! -s "${s0}.orig" ]; then cp "${s0}" "${s0}.orig"; fi
    cp "${s1}" "${s0}"
    cmp -s "${s0}" "${s1}" || { echo "  piece ${p}: swap FAILED"; continue; }
    sw=$((sw + 1))
done
echo "  swapped ${sw}/8 pieces"
[ "${sw}" -eq 8 ] || { echo "  ERROR: not all swaps took"; exit 1; }
extract swapped || exit 1

echo
echo "### out: ${OUTDIR}"
ls -1 "${OUTDIR}" | head -n 20
echo "  ($(ls -1 "${OUTDIR}" | wc -l) files)"
echo
echo "Fetch, then score every piece against artifacts/pot_a_bl/."
