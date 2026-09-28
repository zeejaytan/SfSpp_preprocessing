#!/bin/bash
# Ticket 12 redirect: sweep RegionGrowing smoothness, NOT Euclidean tolerance.
#
# WHY THIS AND NOT THE EUCLIDEAN SWEEP
# Surface_0/1 come from RegionGrowing in surfaceSegmentation
# (mesh_processing_headless.cpp:1641-1649, :1686), NOT from the two
# EuclideanClusterExtraction sites (:658 feeds decorative breaklines from
# unclustered points; :1948 getClusters has no callers). The ticket-12 file
# records this correction. Sweeping Euclidean tolerance would test the wrong
# stage.
#
# The split already has env hooks, so no rebuild is needed:
#   SFS_SMOOTHNESS_DEG (default 4.5), SFS_CURVATURE_THRESH (default 1.5)
# One variable per experiment: smoothness only, curvature stays default.
#
# WHAT WOULD SETTLE IT
#   cluster behaviour of the RegionGrowing split changes AND gate moves from
#   7/15 -> clusters alone moving is necessary, not sufficient (ticket 11 rule).
#
# Control arm first with both vars unset. Without it a staging drift looks
# like a smoothness effect.
#
# Run inside holder: srun --jobid=<ID> --overlap bash run_smoothness_sweep.sh

set -uo pipefail

ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing
BUILD="${ROOT}/original_nurbs_preprocessing/build"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF="${ROOT}/pcl_191_nurbs.sif"
OUT="${ROOT}/diag_smooth_out"
POT=Pot_A
# Control + 4 values: tighter, default-ish, looser, much looser.
# Default is 4.5; 25 matches the Juglet note (piece 3 needs ~25 deg).
SMOOTHS="2.0 8.0 15.0 25.0"

for b in MeshPreprocessingHeadless EdgeLineExtractionHeadless; do
    [ -x "${BUILD}/${b}" ] || { echo "ERROR: ${b} not built"; exit 1; }
done
rm -rf "${OUT}"; mkdir -p "${OUT}"

stage() {
    local tree="$1"
    rm -rf "${tree}"
    mkdir -p "${tree}/Temp/Data/${POT}" "${tree}/Temp/Axes" \
             "${tree}/Dataset/Mesh/${POT}" "${tree}/Dataset/Point/${POT}" \
             "${tree}/Dataset/Surfaces/${POT}" "${tree}/Dataset/Breaklines/${POT}"
    for f in "${ROOT}/Dataset/Mesh/${POT}"/*.obj; do
        [ -e "${f}" ] || continue
        cp -L "${f}" "${tree}/Dataset/Mesh/${POT}/"
    done
    for f in "${ROOT}/Dataset/Point/${POT}"/*; do
        [ -e "${f}" ] || continue
        cp -L "${f}" "${tree}/Dataset/Point/${POT}/"
    done
    echo "    staged $(ls "${tree}/Dataset/Mesh/${POT}" 2>/dev/null | wc -l) meshes, $(ls "${tree}/Dataset/Point/${POT}" 2>/dev/null | wc -l) point clouds"
}

run_arm() {
    local tag="$1" smooth="$2"
    local tree="${ROOT}/diag_smooth_${tag}"
    local mlog="/tmp/smooth_${tag}_mesh.log" elog="/tmp/smooth_${tag}_edge.log"
    stage "${tree}" || return 1
    if [ "${smooth}" = "unset" ]; then
        ( cd "${tree}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" \
            env -u SFS_SMOOTHNESS_DEG -u SFS_CURVATURE_THRESH POT_NAME="${POT}" \
            "${BUILD}/MeshPreprocessingHeadless" ) > "${mlog}" 2>&1
    else
        ( cd "${tree}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" \
            env SFS_SMOOTHNESS_DEG="${smooth}" POT_NAME="${POT}" \
            "${BUILD}/MeshPreprocessingHeadless" ) > "${mlog}" 2>&1
    fi
    local data="${tree}/Temp/Data/${POT}"
    local n_s0 n_un
    n_s0=$(ls "${data}"/*_Surface_0.xyz 2>/dev/null | wc -l)
    n_un=$(ls "${data}"/*_unclustered.ply 2>/dev/null | wc -l)
    echo "    ${tag}: mesh exit $? (not trusted)  Surface_0.xyz=${n_s0}  unclustered=${n_un}"
    if [ "${n_s0}" -lt 8 ]; then
        echo "    ** expected 8 Surface_0.xyz, got ${n_s0}. Tail:"
        tail -n 8 "${mlog}" | sed 's/^/       /'
        return 1
    fi
    echo "    ${tag}: RegionGrowing cluster lines:"
    grep -E "Number of clusters is equal to|Segmentation thresholds" "${mlog}" 2>/dev/null | head -n 20 | sed 's/^/      /'
    ( cd "${tree}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" \
        env POT_NAME="${POT}" "${BUILD}/EdgeLineExtractionHeadless" ) > "${elog}" 2>&1
    local bl="${tree}/Dataset/Breaklines/${POT}" n
    n=$(ls "${bl}"/Pot_A_Piece_*_Breakline_0.pcd 2>/dev/null | wc -l)
    local pieces
    pieces=$(grep -c "ADAPTIVE SEQUENCING" "${elog}" 2>/dev/null || true)
    [ -n "${pieces}" ] || pieces=0
    echo "    ${tag}: edgeline exit $? (not trusted)  sequenced=${pieces}  breaklines=${n}"
    if [ "${n}" -lt 8 ]; then
        echo "    ** expected 8 breaklines, got ${n}. Tail:"
        tail -n 8 "${elog}" | sed 's/^/       /'
        mkdir -p "${OUT}/${tag}"
        echo "edgeline produced ${n}/8 breaklines" > "${OUT}/${tag}.FAILED"
        cp "${elog}" "${OUT}/${tag}.edgeline.log"
        cp "${mlog}" "${OUT}/${tag}.mesh.log"
        rm -rf "${tree}"
        return 1
    fi
    mkdir -p "${OUT}/${tag}"
    cp "${bl}"/Pot_A_Piece_*_Breakline_0.pcd "${OUT}/${tag}/"
    cp "${mlog}" "${OUT}/${tag}/mesh.log"
    rm -rf "${tree}"
    return 0
}

echo "### control arm: both vars UNSET (pipeline as it stands)"
run_arm control unset || echo "CONTROL FAILED -- sweep is void"
# Continue on arm failure: a crashed arm is a result (fragility), not a
# reason to skip the remaining arms. Each failure is recorded in OUT as
# <tag>.FAILED with the tail of the log.
for s in ${SMOOTHS}; do
    echo
    echo "### smoothness ${s} deg"
    run_arm "s${s}" "${s}" || echo "    ${s}: arm recorded as failed, continuing"
done

echo
echo "### out: ${OUT}"
for d in "${OUT}"/*/; do
    echo "  $(basename "$d"): $(ls "$d"/Pot_A_Piece_*_Breakline_0.pcd 2>/dev/null | wc -l) breaklines"
done
echo
echo "Fetch and score each arm against the authors' rims + gate probe:"
echo "  scp -r spartan:${OUT} <laptop>/structure-from-sherds-pp/artifacts/smooth_sweep_out"
