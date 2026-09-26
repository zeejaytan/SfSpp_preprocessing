#!/bin/bash
# Ticket 09, continued: run ONLY the edgeline stage for Pot_A, against the
# mesh-stage output that already exists from the previous attempt.
#
# WHAT WENT WRONG LAST TIME, so it is not repeated: NURBS_OUTPUT_BASE
# redirects tempDataPath(), which is where the MESH stage writes. With it
# set, the mesh stage wrote 102 files to $TREE/out/SfS_pp/Surfaces/ and the
# edgeline stage -- which looks in Temp/Data/Pot_A/ by default -- found
# nothing. Both stages exited 0. Two silent no-ops that a "did it work?"
# check on the exit code would have called a success.
#
# So: keep NURBS_OUTPUT_BASE (it is where the surfaces already are), run
# only the edgeline stage, and VERIFY BY COUNTING FILES, never by exit code.
#
#   srun --jobid=<ID> --overlap bash run_pota_fresh2.sh

set -uo pipefail

ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing
BUILD="${ROOT}/original_nurbs_preprocessing/build"
TREE="${ROOT}/diag_pota_fresh"
OUT="${TREE}/out"
SURF="${OUT}/SfS_pp/Surfaces"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF="${ROOT}/pcl_191_nurbs.sif"
POT=Pot_A
LOG=/tmp/fresh_edge2.log

[ -x "${BUILD}/EdgeLineExtractionHeadless" ] || { echo "ERROR: binary not built"; exit 1; }

echo "### inputs present?"
echo "    surfaces on disk: $(ls "${SURF}" 2>/dev/null | wc -l)"
if [ "$(ls "${SURF}"/*_Surface_0.xyz 2>/dev/null | wc -l)" -eq 0 ]; then
    echo "ERROR: no Surface_0.xyz under ${SURF} -- the edgeline stage would"
    echo "       silently do nothing again. Aborting before burning a run."
    exit 1
fi

echo
echo "### edgeline stage (NURBS_OUTPUT_BASE kept, so it finds the surfaces)"
( cd "${TREE}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" \
    env POT_NAME="${POT}" NURBS_OUTPUT_BASE="${OUT}" \
    "${BUILD}/EdgeLineExtractionHeadless" ) > "${LOG}" 2>&1
erc=$?
BL="${OUT}/SfS_pp/Breaklines"
nbl=$(ls "${BL}"/*.pcd 2>/dev/null | wc -l)
echo "    exit ${erc}   (not trusted)"
echo "    breakline .pcd written: ${nbl}"

if [ "${nbl}" -eq 0 ]; then
    echo "    ** NOTHING PRODUCED despite the exit code. Tail:"
    tail -n 12 "${LOG}" | sed 's/^/       /'
    exit 1
fi

pieces=$(grep -c "ADAPTIVE SEQUENCING" "${LOG}" 2>/dev/null || true)
[ -n "${pieces}" ] || pieces=0
echo "    pieces sequenced: ${pieces}"
if [ "${pieces}" -lt 8 ]; then
    echo "    ** fewer than 8 pieces sequenced -- Pot_A has 8. Incomplete."
    tail -n 12 "${LOG}" | sed 's/^/       /'
fi

echo
echo "### FRAME CHECK -- breakline centroid vs mesh centroid, per piece"
# Mesh centroids from temp_download/Mesh/Pot_A/*.obj, measured on the
# cluster. These are the scan frame; nothing downstream fitted them.
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
echo "Reference points:"
echo "  - the AUTHORS' breaklines sit within ~1 mm of these mesh centroids."
echo "  - the Nov-2025 bundle of ours: pieces 4.5x too far apart (331 mm vs 73 mm)."
echo "  - the Juglet bundle of ours: 9/9 within 0.32 of a sherd diagonal."
echo "  So gaps of a few mm here mean the CURRENT code writes a common frame,"
echo "  and the Nov-2025 bundle is a stale artifact rather than a live bug."
echo
echo "Fetch:  scp -r spartan:${BL} <laptop>/structure-from-sherds-pp/artifacts/pot_a_fresh_bl"
