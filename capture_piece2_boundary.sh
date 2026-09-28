#!/bin/bash
# Defect 2: capture piece 2's boundary cloud (the walk's actual input).
#
# Piece 2's rim is 46% of the reference on Surface_0 and 27% on Surface_1.
# Both truncate, so the walk stalls on both clouds. Temp_edge/boundary.pcd
# is overwritten per piece, so a full run keeps only the last piece. This
# stages a tree with ONLY piece 2's inputs, runs just the edgeline stage,
# and copies out its boundary.pcd before anything overwrites it.
#
# Verification by file count and by the ADAPTIVE SEQUENCING line naming the
# point count, never by exit code alone.
#
# Run inside a holder:  srun --jobid=<ID> --overlap bash capture_piece2_boundary.sh

set -uo pipefail

ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing
BUILD="${ROOT}/original_nurbs_preprocessing/build"
SRC="${ROOT}/diag_t04_pota/Temp/Data/Pot_A"
TREE="${ROOT}/diag_piece2"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF="${ROOT}/pcl_191_nurbs.sif"
POT=Pot_A
LOG=/tmp/piece2_edge.log
OUT="${ROOT}/diag_piece2_out"

[ -x "${BUILD}/EdgeLineExtractionHeadless" ] || { echo "ERROR: not built"; exit 1; }
[ -d "${SRC}" ] || { echo "ERROR: no mesh-stage output at ${SRC}"; exit 1; }
# Stage from the UNEXCHANGED mesh output. diag_t04_pota's Temp/Data was
# exchanged in place by the ticket-04 run, so staging from it silently puts
# old-Surface_1 content under the Surface_0 name -- which is how the first
# capture grabbed the wrong wall's cloud. diag_pota3 predates the classifier.
SRC="${ROOT}/diag_pota3/Temp/Data/Pot_A"

rm -rf "${TREE}" "${OUT}"
mkdir -p "${TREE}/Temp/Data/${POT}" "${TREE}/Temp/Axes" \
         "${TREE}/Dataset/Mesh/${POT}" "${TREE}/Dataset/Point/${POT}" \
         "${TREE}/Dataset/Surfaces/${POT}" "${TREE}/Dataset/Breaklines/${POT}" \
         "${TREE}/Dataset/Axes" "${OUT}"
# Only piece 2's obj + surfaces. The 14-char key is Pot_A_Piece_02.
for f in "${SRC}"/Pot_A_Piece_02*; do
    [ -e "${f}" ] || continue
    cp -L "${f}" "${TREE}/Temp/Data/${POT}/"
done
for f in "${ROOT}/Dataset/Axes/${POT}"/Pot_A_Piece_02_Axis.xyz; do
    [ -e "${f}" ] || continue
    cp -L "${f}" "${TREE}/Dataset/Axes/"
done
echo "    staged: $(ls "${TREE}/Temp/Data/${POT}" | wc -l) files"
echo "    axis: $(ls "${TREE}/Dataset/Axes" 2>/dev/null | wc -l)"

# Ticket 13: Temp_edge/ is overwritten per surface, so poll and snapshot
# EVERY intermediate, each with its own dedupe state. Surface_0 is processed
# first, Surface_1 second; without this only the second survives, which is
# how the first capture grabbed the wrong wall's cloud.
# The intermediates that map the surface->boundary path:
#   cloud_Surface_AllSamples_Cleaned.pcd (input to boundary estimation)
#   boundary.pcd (the walk's input, after the line-974 reload)
#   boundaryImproved.pcd, cloud_Filtered.pcd (computed then discarded)
#   cloudForSpline.pcd, CompleteBreakline.pcd (downstream, for context)
EDGE="${TREE}/Temp/Temp_edge/${POT}"
WATCH="cloud_Surface_AllSamples_Cleaned.pcd boundary.pcd boundaryImproved.pcd cloud_Filtered.pcd cloudForSpline.pcd CompleteBreakline.pcd"
snapshot_loop() {
    mkdir -p "${OUT}/snaps"
    declare -A last n
    while :; do
        for w in ${WATCH}; do
            local f="${EDGE}/${w}" h tag
            [ -f "${f}" ] || continue
            h=$(md5sum "${f}" 2>/dev/null | cut -d' ' -f1)
            [ -n "${h}" ] || continue
            tag="${w%.pcd}"
            if [ "${h}" != "${last[$tag]:-}" ]; then
                last[$tag]="${h}"
                n[$tag]=$(( ${n[$tag]:-0} + 1 ))
                cp "${f}" "${OUT}/snaps/${tag}_$(printf '%02d' ${n[$tag]})_${h:0:8}.pcd"
            fi
        done
        sleep 0.3
    done
}
snapshot_loop &
WATCHER=$!
( cd "${TREE}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" \
    env POT_NAME="${POT}" "${BUILD}/EdgeLineExtractionHeadless" ) > "${LOG}" 2>&1
echo "    exit $? (not trusted)"
kill "${WATCHER}" 2>/dev/null; wait "${WATCHER}" 2>/dev/null
grep "ADAPTIVE SEQUENCING" "${LOG}" 2>/dev/null | head -n 4 | sed 's/^/    /'
grep "SFS-T04" "${LOG}" 2>/dev/null | head -n 4 | sed 's/^/    /'

if [ "$(ls "${OUT}"/snaps/*.pcd 2>/dev/null | wc -l)" -eq 0 ]; then
    echo "    ** no snapshots captured"
    tail -n 8 "${LOG}" | sed 's/^/       /'
    exit 1
fi
for f in "${OUT}"/snaps/*.pcd; do
    echo "    $(basename "$f"): $(grep -m1 "^POINTS" "$f" | awk '{print $2}') points"
done
BL="${TREE}/Dataset/Breaklines/${POT}"
cp "${BL}"/Pot_A_Piece_02_Breakline_*.pcd "${OUT}/" 2>/dev/null || true
echo "    out: $(ls "${OUT}" | wc -l) files"
echo
echo "Fetch:  scp -r spartan:${OUT} <laptop>/structure-from-sherds-pp/artifacts/piece2_boundary"
