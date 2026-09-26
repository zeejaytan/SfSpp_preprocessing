#!/bin/bash
# Ticket 09, attempt 3: the configuration that is KNOWN to work.
#
# THE TWO FAILED ATTEMPTS, so they are not repeated:
#  1. NURBS_OUTPUT_BASE set -> mesh stage writes to out/SfS_pp/Surfaces,
#     edgeline stage looks in Temp/Data, finds nothing, exits 0.
#  2. NURBS_OUTPUT_BASE kept, edgeline stage re-run -> it enumerates pieces
#     from Temp/ looking for *.obj, and Temp/Data/Pot_A is empty, so it
#     processed 0 pieces and exited 0.
#
# Both exited 0. Neither did any work. The edgeline stage needs the .obj
# files and the Surface_*.xyz to sit TOGETHER under Temp/Data/<pot>/, which
# is what happens with no NURBS_OUTPUT_BASE at all -- the same configuration
# run_scope_pota.sh used successfully (16 pieces sequenced, 16 snapshots).
#
# Breaklines then land in $TREE/Dataset/Breaklines/Pot_A.
#
# VERIFICATION IS BY FILE COUNT, never by exit code. Both prior attempts
# exited 0 having done nothing.
#
#   srun --jobid=<ID> --overlap bash run_pota_fresh3.sh

set -uo pipefail

ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing
BUILD="${ROOT}/original_nurbs_preprocessing/build"
TREE="${ROOT}/diag_pota3"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF="${ROOT}/pcl_191_nurbs.sif"
POT=Pot_A
MLOG=/tmp/pota3_mesh.log
ELOG=/tmp/pota3_edge.log

for b in MeshPreprocessingHeadless EdgeLineExtractionHeadless; do
    [ -x "${BUILD}/${b}" ] || { echo "ERROR: ${b} not built"; exit 1; }
done

echo "### stage inputs (no NURBS_OUTPUT_BASE anywhere in this script)"
rm -rf "${TREE}"
mkdir -p "${TREE}/Temp/Data/${POT}" "${TREE}/Temp/Axes" \
         "${TREE}/Dataset/Mesh/${POT}" "${TREE}/Dataset/Point/${POT}" \
         "${TREE}/Dataset/Surfaces/${POT}" "${TREE}/Dataset/Breaklines/${POT}"
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
    env POT_NAME="${POT}" "${BUILD}/MeshPreprocessingHeadless" ) > "${MLOG}" 2>&1
echo "    exit $? (not trusted)"
DATA="${TREE}/Temp/Data/${POT}"
echo "    files in Temp/Data/${POT}: $(ls "${DATA}" 2>/dev/null | wc -l)"
echo "    *.obj: $(ls "${DATA}"/*.obj 2>/dev/null | wc -l)   *_Surface_0.xyz: $(ls "${DATA}"/*_Surface_0.xyz 2>/dev/null | wc -l)   *_unclustered.ply: $(ls "${DATA}"/*_unclustered.ply 2>/dev/null | wc -l)"

if [ "$(ls "${DATA}"/*.obj 2>/dev/null | wc -l)" -eq 0 ] \
   || [ "$(ls "${DATA}"/*_Surface_0.xyz 2>/dev/null | wc -l)" -eq 0 ]; then
    echo "    ** mesh stage did not produce what the edgeline stage needs."
    tail -n 12 "${MLOG}" | sed 's/^/       /'
    exit 1
fi

echo
echo "### edgeline stage"
( cd "${TREE}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" \
    env POT_NAME="${POT}" "${BUILD}/EdgeLineExtractionHeadless" ) > "${ELOG}" 2>&1
echo "    exit $? (not trusted)"
BL="${TREE}/Dataset/Breaklines/${POT}"
nbl=$(ls "${BL}"/*.pcd 2>/dev/null | wc -l)
pieces=$(grep -c "ADAPTIVE SEQUENCING" "${ELOG}" 2>/dev/null || true)
[ -n "${pieces}" ] || pieces=0
echo "    pieces sequenced: ${pieces}   (Pot_A has 8 sherds x 2 faces = 16)"
echo "    breakline .pcd written: ${nbl}"
if [ "${nbl}" -eq 0 ]; then
    echo "    ** NOTHING PRODUCED. Tail:"
    tail -n 12 "${ELOG}" | sed 's/^/       /'
    exit 1
fi

echo
echo "### boundary cloud sizes, per sherd face"
grep "ADAPTIVE SEQUENCING" "${ELOG}" 2>/dev/null \
    | sed 's/.*Boundary has \([0-9]*\) points.*/    n=\1/' | sort -n -k1.2 | uniq -c

echo
echo "### FRAME CHECK -- breakline centroid vs mesh centroid, per piece"
# Mesh centroids from temp_download/Mesh/Pot_A/*.obj (scan frame).
awk -v BL="${BL}" '
BEGIN{
  mx[1]= 28.9; my[1]= -5.2; mz[1]= 402.2
  mx[2]=-30.5; my[2]=  29.5; mz[2]= 394.9
  mx[3]= 15.9; my[3]=  43.3; mz[3]= 408.3
  mx[4]=-12.9; my[4]=  53.5; mz[4]= 375.4
  mx[5]= 17.9; my[5]=  17.9; mz[5]= 371.2
  mx[6]=  3.4; my[6]=  -6.6; mz[6]= 431.3
  mx[7]=  3.1; my[7]=  40.3; mz[7]= 339.2
  mx[8]=-20.3; my[8]=   7.8; mz[8]= 301.9
  printf "  %-4s %6s %26s %26s %8s\n","pc","npts","breakline centroid","mesh centroid","gap"
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
    printf "  %-4d %6d (%7.1f,%7.1f,%8.1f) (%7.1f,%7.1f,%8.1f) %8.1f\n", $1, n, cx, cy, cz, mx[$1], my[$1], mz[$1], d
  } else {
    printf "  %-4d %6s %26s %26s %8s\n", $1, "MISSING","","","-"
  }
  sx=sy=sz=n=0
}' < <(seq 1 8)

echo
echo "Reference:"
echo "  authors' breaklines : within ~1 mm of these mesh centroids"
echo "  our Nov-2025 bundle : pieces 4.5x too far apart (331 vs 73 mm spread)"
echo "  our Juglet bundle   : 9/9 within 0.32 of a sherd diagonal"
echo
echo "Fetch:  scp -r spartan:${BL} <laptop>/structure-from-sherds-pp/artifacts/pot_a_fresh_bl"
