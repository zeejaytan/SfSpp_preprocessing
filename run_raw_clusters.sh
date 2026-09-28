#!/bin/bash
# Ticket 15, step 2: capture RAW pre-fit region clusters for piece 2.
#
# The fitted Surface_0/1 survive to disk; the raw clusters never did, so
# split-loss vs fit-inset could not be told apart. With the SFS-T15 save in
# place, this runs the mesh stage once on a piece-2-only tree and fetches
# raw + fitted side by side. Laptop measures each against the reference rim.
#
# Run inside a holder:  srun --jobid=<ID> --overlap bash run_raw_clusters.sh

set -uo pipefail

ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing
BUILD="${ROOT}/original_nurbs_preprocessing/build"
TREE="${ROOT}/diag_rawcl"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF="${ROOT}/pcl_191_nurbs.sif"
POT=Pot_A
LOG=/tmp/rawcl_mesh.log
OUT="${ROOT}/diag_rawcl_out"

[ -x "${BUILD}/MeshPreprocessingHeadless" ] || { echo "ERROR: not built"; exit 1; }
if [ "$(strings "${BUILD}/MeshPreprocessingHeadless" 2>/dev/null | grep -c "tmpSurfaceCluster_Raw" || true)" = "0" ]; then
    echo "ERROR: SFS-T15 save not in the binary. Rebuild first."
    exit 1
fi
echo "raw-cluster save present in binary: yes"

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
echo "--- raw vs fitted cluster files in the tree:"
find "${TREE}/Temp" -name "*Cluster_*.ply" 2>/dev/null | sed "s|${TREE}/||" | head -n 8
for f in "${TREE}"/Temp/Temp/"${POT}"/tmpSurfaceCluster_Raw_?.ply \
         "${TREE}"/Temp/Temp/"${POT}"/tmpSurfaceCluster_Improved_?.ply; do
    [ -e "${f}" ] || continue
    cp -L "${f}" "${OUT}/"
done
echo "    fetched to OUT: $(ls "${OUT}" 2>/dev/null | wc -l) files"
[ "$(ls "${OUT}" 2>/dev/null | wc -l)" -ge 2 ] || {
    echo "    ** expected raw+fitted cluster files"; exit 1; }
echo
echo "Fetch:  scp -r spartan:${OUT} <laptop>/artifacts/"
