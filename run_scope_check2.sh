#!/bin/bash
# Ticket 08: is the ordering defect Juglet-specific, or general?
#
# WHAT THE PIPELINE ACTUALLY NEEDS (learned the hard way, recorded here so
# the next person does not rediscover it one error at a time):
#
#   The edgeline stage does NOT read the .obj meshes. It reads SURFACE point
#   clouds produced by the earlier mesh stage:
#     - Temp/Data/<pot>/<piece>_Surface_0.xyz   and _Surface_1.xyz
#     - Temp/Data/<pot>/<piece>_unclustered.ply
#   and it enumerates pieces by the .obj files sitting beside them. Missing
#   Surface xyz -> exit 255 "cannot copy file". Missing unclustered.ply ->
#   PLYReader parse error, then a KdTree assertion and SIGABRT (exit 134).
#
#   Juglet: a COMPLETE staging set already exists in an archived run output,
#   Juglet_Dataset_tidycheck/SfS_pp/Surfaces/ (Mesh.obj, Point.pcd,
#   SampledWithNormals.ply, Surface_{0,1}.{ply,xyz}, unclustered.ply,
#   unclustered.plyCluster_*.pcd). So the Juglet needs only the edgeline
#   stage.
#
#   Pot_A: NO _unclustered.ply exists anywhere in the project, so its mesh
#   stage must be run first. That stage reads Dataset/Mesh/<pot>/ and
#   Dataset/Point/<pot>/ (both present: 8 meshes, 16 point clouds) and
#   writes Temp/Data/<pot>/.
#
#   Axes are NOT required -- the code prints "Axis information is not
#   available." and continues.
#
# ISOLATION: the binary uses relative paths, so cwd decides everything.
# Each pot runs in its own throwaway tree. Nothing outside diag_scope/ and
# diag_scope_snapshots/ is written -- in particular not Temp/Temp_edge/ or
# Dataset/, which may hold live inputs of the current assembly runs.
#
# SNAPSHOTTING: Temp/Temp_edge/<pot>/boundary.pcd is overwritten per sherd,
# so a plain run leaves only the last one. The watcher polls every 0.3 s and
# de-duplicates by md5. The script reports snapshots-vs-pieces and warns if
# they disagree, because an incomplete snapshot is not a sound measurement.
#
# Run inside a holder:  srun --jobid=<ID> --overlap bash run_scope_check2.sh

set -uo pipefail

ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing
BUILD="${ROOT}/original_nurbs_preprocessing/build"
SCRATCH="${ROOT}/diag_scope"
SNAP="${ROOT}/diag_scope_snapshots"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF="${ROOT}/pcl_191_nurbs.sif"
JUGLET_STAGE="${ROOT}/Juglet_Dataset_tidycheck/SfS_pp/Surfaces"

[ -f "${SIF}" ] || { echo "ERROR: container ${SIF} missing"; exit 1; }
[ -x "${BUILD}/EdgeLineExtractionHeadless" ] || { echo "ERROR: build the pipeline first"; exit 1; }
[ -d "${JUGLET_STAGE}" ] || { echo "ERROR: Juglet staging ${JUGLET_STAGE} missing"; exit 1; }

mkdir -p "${SNAP}"

snapshot_loop() {
    local src="$1" dst="$2" last="" n=0 h
    mkdir -p "${dst}"
    while :; do
        if [ -f "${src}" ]; then
            h=$(md5sum "${src}" 2>/dev/null | cut -d' ' -f1)
            if [ -n "${h}" ] && [ "${h}" != "${last}" ]; then
                n=$((n + 1))
                cp "${src}" "${dst}/boundary_$(printf '%02d' ${n})_${h:0:8}.pcd"
                last="${h}"
            fi
        fi
        sleep 0.3
    done
}

new_tree() {
    local pot="$1" tree="${SCRATCH}/$1"
    rm -rf "${tree}" "${SNAP}/${pot}"
    mkdir -p "${tree}/Temp/Data/${pot}" "${tree}/Temp/Axes" \
             "${tree}/Dataset/Mesh/${pot}" "${tree}/Dataset/Point/${pot}" \
             "${tree}/Dataset/Surfaces/${pot}" "${tree}/Dataset/Breaklines/${pot}" \
             "${SNAP}/${pot}"
    echo "${tree}"
}

# ---- Juglet: staging exists, run only the edgeline stage ----------------
echo "=============================================================="
echo "=== Juglet -- staging from ${JUGLET_STAGE}"
echo "=============================================================="
JT=$(new_tree Juglet)
n=0
for f in "${JUGLET_STAGE}"/Juglet_Piece_*; do
    [ -e "${f}" ] || continue
    cp -L "${f}" "${JT}/Temp/Data/Juglet/"
    n=$((n + 1))
done
echo "  staged ${n} files (complete per-piece set)"
ls "${JT}/Temp/Data/Juglet" | head -n 4 | sed 's/^/    /'

snapshot_loop "${JT}/Temp/Temp_edge/Juglet/boundary.pcd" "${SNAP}/Juglet" &
JW=$!
( cd "${JT}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" \
    env POT_NAME=Juglet "${BUILD}/EdgeLineExtractionHeadless" ) \
    > "${SNAP}/Juglet.log" 2>&1
JRC=$?
kill "${JW}" 2>/dev/null; wait "${JW}" 2>/dev/null

# ---- Pot_A: run the mesh stage, then the edgeline stage ----------------
echo
echo "=============================================================="
echo "=== Pot_A -- mesh stage first (no _unclustered.ply exists yet)"
echo "=============================================================="
PT=$(new_tree Pot_A)
n=0
for f in "${ROOT}/Dataset/Mesh/Pot_A"/*.obj; do
    [ -e "${f}" ] || continue
    cp -L "${f}" "${PT}/Dataset/Mesh/Pot_A/"; n=$((n + 1))
done
for f in "${ROOT}/Dataset/Point/Pot_A"/*; do
    [ -e "${f}" ] || continue
    cp -L "${f}" "${PT}/Dataset/Point/Pot_A/"
done
echo "  staged ${n} meshes and $(ls "${PT}/Dataset/Point/Pot_A" | wc -l) point clouds"

if [ -x "${BUILD}/MeshProcessingHeadless" ]; then
    ( cd "${PT}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" \
        env POT_NAME=Pot_A "${BUILD}/MeshProcessingHeadless" ) \
        > "${SNAP}/Pot_A_mesh.log" 2>&1
    MRC=$?
    echo "  mesh stage exit ${MRC}; produced $(ls "${PT}/Temp/Data/Pot_A" 2>/dev/null | wc -l) files in Temp/Data/Pot_A"
    if [ "${MRC}" -ne 0 ]; then
        echo "  ** mesh stage FAILED. Tail:"
        tail -n 6 "${SNAP}/Pot_A_mesh.log" | sed 's/^/     /'
    fi
else
    echo "  ** MeshProcessingHeadless not built -- cannot produce the inputs"
    MRC=1
fi

if [ "${MRC:-1}" -eq 0 ]; then
    snapshot_loop "${PT}/Temp/Temp_edge/Pot_A/boundary.pcd" "${SNAP}/Pot_A" &
    PW=$!
    ( cd "${PT}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" \
        env POT_NAME=Pot_A "${BUILD}/EdgeLineExtractionHeadless" ) \
        > "${SNAP}/Pot_A.log" 2>&1
    PRC=$?
    kill "${PW}" 2>/dev/null; wait "${PW}" 2>/dev/null
else
    PRC=1
fi

# ---- report -----------------------------------------------------------
echo
echo "=============================================================="
echo "=== RESULT"
echo "=============================================================="
for pot in Juglet Pot_A; do
    log="${SNAP}/${pot}.log"
    [ -f "${log}" ] || continue
    # grep -c prints 0 AND exits 1 on no match, so `|| echo 0` would append
    # a second line and break the integer test. `|| true` is correct.
    pieces=$(grep -c "ADAPTIVE SEQUENCING" "${log}" 2>/dev/null || true)
    [ -n "${pieces}" ] || pieces=0
    snaps=$(ls "${SNAP}/${pot}"/boundary_*.pcd 2>/dev/null | wc -l)
    echo "  ${pot}: pieces sequenced=${pieces}  snapshots=${snaps}"
    if [ "${pieces}" -gt 0 ] && [ "${snaps}" -lt "${pieces}" ]; then
        echo "     ** INCOMPLETE -- fewer snapshots than pieces; NOT a sound sample"
    fi
    grep "ADAPTIVE SEQUENCING" "${log}" 2>/dev/null \
        | sed 's/.*Boundary has \([0-9]*\) points, using K=\([0-9]*\).*/     n=\1 K=\2/' \
        | sort | uniq -c | sed 's/^/  /'
done
echo
echo "Juglet edgeline exit ${JRC}; Pot_A mesh exit ${MRC:-skipped}, edgeline exit ${PRC}"
echo
echo "Fetch:  scp -r spartan:${SNAP} <laptop>/SfSpp_preprocessing/artifacts/scope_snapshots"
