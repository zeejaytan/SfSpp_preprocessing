#!/bin/bash
# Ticket 14: capture the decorative rims the pipeline now persists.
#
# Stages a piece-2-only tree, runs the mesh stage, fetches
# *Decorative_*.pcd. Verification by file count + the SFS-T14 log lines,
# never by exit code.
#
# Run inside a holder:  srun --jobid=<ID> --overlap bash run_decorative_capture.sh

set -uo pipefail

ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing
BUILD="${ROOT}/original_nurbs_preprocessing/build"
TREE="${ROOT}/diag_decor"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF="${ROOT}/pcl_191_nurbs.sif"
POT=Pot_A
LOG=/tmp/decor_mesh.log
OUT="${ROOT}/diag_decor_out"

[ -x "${BUILD}/MeshPreprocessingHeadless" ] || { echo "ERROR: not built"; exit 1; }
if [ "$(strings "${BUILD}/MeshPreprocessingHeadless" 2>/dev/null | grep -c "SFS-T14" || true)" = "0" ]; then
    echo "ERROR: persist change not in the binary. Rebuild first."
    exit 1
fi
echo "persist change present in binary: yes"

rm -rf "${TREE}" "${OUT}"
mkdir -p "${TREE}/Temp/Data/${POT}" "${TREE}/Temp/Axes" \
         "${TREE}/Dataset/Mesh/${POT}" "${TREE}/Dataset/Point/${POT}" \
         "${TREE}/Dataset/Surfaces/${POT}" "${TREE}/Dataset/Breaklines/${POT}" \
         "${OUT}"
for f in "${ROOT}/Dataset/Mesh/${POT}"/Pot_A_Piece_02*.obj; do
    [ -e "${f}" ] || continue
    cp -L "${f}" "${TREE}/Dataset/Mesh/${POT}/"
done
for f in "${ROOT}/Dataset/Point/${POT}"/*Piece_02*; do
    [ -e "${f}" ] || continue
    cp -L "${f}" "${TREE}/Dataset/Point/${POT}/"
done

( cd "${TREE}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" \
    env POT_NAME="${POT}" "${BUILD}/MeshPreprocessingHeadless" ) > "${LOG}" 2>&1
echo "    exit $? (not trusted)"
echo "--- SFS-T14 lines:"
grep "SFS-T14" "${LOG}" 2>/dev/null | head -n 8 || echo "    ** NO SFS-T14 LINES"
echo "--- decorative rims in tree:"
find "${TREE}/Temp" -name "*Decorative_*.pcd" 2>/dev/null | sed "s|${TREE}/||" | head -n 8
N=0
while IFS= read -r f; do
    [ -e "${f}" ] || continue
    cp -L "${f}" "${OUT}/"
    N=$((N + 1))
done < <(find "${TREE}/Temp" -name "*Decorative_*.pcd" 2>/dev/null)
echo "    fetched to OUT: ${N} files"
[ "${N}" -ge 1 ] || { echo "    ** nothing persisted"; exit 1; }
echo
echo "Fetch:  scp -r spartan:${OUT} <laptop>/artifacts/"
