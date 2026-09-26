#!/bin/bash
# Ticket 09 step 1: re-run our CURRENT preprocessing on Pot_A, in an
# isolated tree, and report the breaklines' frame immediately.
#
# WHY
# The Nov-2025 bundle (NURBS_Dataset_20251103, md5-identical to the local
# pot_a_nurbs_bl) has its eight pieces arranged 4.5x further apart than
# Pot_A's real sherds: 331 mm mean pairwise centroid distance against 73 mm
# measured on the meshes. Individually the pieces are small and
# well-shaped. That is the signature of each sherd being written in its own
# local frame.
#
# The Juglet bundle, by contrast, sits on its own sherds (9/9 within 0.32
# of a sherd diagonal, median 0.06). So either the Nov-2025 run had a frame
# bug that has since been fixed, or it still does.
#
# This distinguishes the two, and it has to happen BEFORE any "restore the
# algorithm to match the paper" work -- otherwise we would be editing a
# pipeline whose only failing measurement we have not understood.
#
# NURBS_OUTPUT_BASE is set so the breaklines land inside the tree, and the
# per-piece centroids are printed at the end so the frame verdict is
# available without fetching anything.
#
# Run inside a holder:  srun --jobid=<ID> --overlap bash run_pota_fresh.sh

set -uo pipefail

ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing
BUILD="${ROOT}/original_nurbs_preprocessing/build"
TREE="${ROOT}/diag_pota_fresh"
OUT="${TREE}/out"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF="${ROOT}/pcl_191_nurbs.sif"
POT=Pot_A

[ -f "${SIF}" ] || { echo "ERROR: container missing"; exit 1; }
for b in MeshPreprocessingHeadless EdgeLineExtractionHeadless; do
    [ -x "${BUILD}/${b}" ] || { echo "ERROR: ${b} not built"; exit 1; }
done

echo "### stage inputs"
rm -rf "${TREE}"
mkdir -p "${TREE}/Temp/Data/${POT}" "${TREE}/Temp/Axes" \
         "${TREE}/Dataset/Mesh/${POT}" "${TREE}/Dataset/Point/${POT}" \
         "${TREE}/Dataset/Surfaces/${POT}" "${OUT}"
n=0
for f in "${ROOT}/Dataset/Mesh/${POT}"/*.obj; do
    [ -e "${f}" ] || continue
    cp -L "${f}" "${TREE}/Dataset/Mesh/${POT}/"; n=$((n + 1))
done
for f in "${ROOT}/Dataset/Point/${POT}"/*; do
    [ -e "${f}" ] || continue
    cp -L "${f}" "${TREE}/Dataset/Point/${POT}"
done
echo "    ${n} meshes, $(ls "${TREE}/Dataset/Point/${POT}" | wc -l) point clouds"

echo
echo "### mesh stage"
( cd "${TREE}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" \
    env POT_NAME="${POT}" NURBS_OUTPUT_BASE="${OUT}" \
    "${BUILD}/MeshPreprocessingHeadless" ) > /tmp/fresh_mesh.log 2>&1
mrc=$?
echo "    exit ${mrc}; $(ls "${TREE}/Temp/Data/${POT}" 2>/dev/null | wc -l) files in Temp/Data/${POT}"
if [ "${mrc}" -ne 0 ]; then
    tail -n 8 /tmp/fresh_mesh.log | sed 's/^/      /'
    exit 1
fi

echo
echo "### edgeline stage"
( cd "${TREE}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" \
    env POT_NAME="${POT}" NURBS_OUTPUT_BASE="${OUT}" \
    "${BUILD}/EdgeLineExtractionHeadless" ) > /tmp/fresh_edge.log 2>&1
erc=$?
BL="${OUT}/SfS_pp/Breaklines"
echo "    exit ${erc}"
if [ "${erc}" -ne 0 ]; then
    tail -n 8 /tmp/fresh_edge.log | sed 's/^/      /'
fi
echo "    breaklines written: $(ls "${BL}" 2>/dev/null | wc -l)"
grep "ADAPTIVE SEQUENCING" /tmp/fresh_edge.log 2>/dev/null \
    | sed 's/.*Boundary has \([0-9]*\) points.*/      n=\1/' | sort | uniq -c

echo
echo "### FRAME CHECK -- breakline centroid vs mesh centroid, per piece"
# Mesh centroids measured on the cluster from
# temp_download/Mesh/Pot_A/*.obj (scan frame, nothing downstream fitted it):
#   1 ( 28.9,  -5.2, 402.2)   2 (-30.5,  29.5, 394.9)
#   3 ( 15.9,  43.3, 408.3)   4 (-12.9,  53.5, 375.4)
#   5 ( 17.9,  17.9, 371.2)   6 (  3.4,  -6.6, 431.3)
#   7 (  3.1,  40.3, 339.2)   8 (-20.3,   7.8, 301.9)
awk -v BL="${BL}" '
BEGIN{
  n=8
  mx[1]= 28.9; my[1]= -5.2; mz[1]= 402.2
  mx[2]=-30.5; my[2]=  29.5; mz[2]= 394.9
  mx[3]= 15.9; my[3]=  43.3; mz[3]= 408.3
  mx[4]=-12.9; my[4]=  53.5; mz[4]= 375.4
  mx[5]= 17.9; my[5]=  17.9; mz[5]= 371.2
  mx[6]=  3.4; my[6]=  -6.6; mz[6]= 431.3
  mx[7]=  3.1; my[7]=  40.3; mz[7]= 339.2
  mx[8]=-20.3; my[8]=   7.8; mz[8]= 301.9
  printf "  %-4s %8s %26s %26s %8s\n","pc","npts","breakline centroid","mesh centroid","gap"
}
{
  f = sprintf("%s/Pot_A_Piece_%02d_Breakline_0.pcd", BL, $1)
  while ((getline line < f) > 0) {
    if (line ~ /^#/ || line ~ /^(VERSION|FIELDS|SIZE|TYPE|COUNT|WIDTH|HEIGHT|VIEWPOINT|POINTS|DATA)/) continue
    c = split(line, a, " ")
    if (c >= 3) { n++; sx+=a[1]; sy+=a[2]; sz+=a[3] }
  }
  close(f)
  if (n > 0) {
    cx=sx/n; cy=sy/n; cz=sz/n
    d = sqrt((cx-mx[$1])^2 + (cy-my[$1])^2 + (cz-mz[$1])^2)
    printf "  %-4d %8d (%7.1f,%7.1f,%8.1f) (%7.1f,%7.1f,%8.1f) %8.1f\n", $1, n, cx, cy, cz, mx[$1], my[$1], mz[$1], d
  } else {
    printf "  %-4d %8s %26s %26s %8s\n", $1, "MISSING","","","-"
  }
  sx=sy=sz=n=0
}' < <(seq 1 8)

echo
echo "Reference: the Nov-2025 bundle's mean pairwise centroid distance was"
echo "331 mm against 73 mm for the real sherds (4.5x). If these gaps are a"
echo "few mm, the current code writes a common frame and the Nov-2025"
echo "bundle is a stale artifact rather than a live bug."
echo
echo "Fetch the fresh bundle with:"
echo "  scp -r spartan:${BL} <laptop>/structure-from-sherds-pp/artifacts/pot_a_fresh_bl"
