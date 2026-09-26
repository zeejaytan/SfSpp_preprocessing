#!/bin/bash
# Ticket 08, part 2: build MeshProcessingHeadless and run the Pot_A arm.
#
# Pot_A has no _unclustered.ply anywhere in the project, so its mesh stage
# must run before the edgeline stage can. MeshProcessingHeadless was not
# built in this build dir (only the edgeline binary and the seam test were),
# so build it first.
#
# In a file, because an inline `srun bash -c` chain with the apptainer path
# inside it has broken repeatedly: ${APPTAINER} gets expanded by the outer
# shell before srun ever sees it.
#
# Run inside a holder:  srun --jobid=<ID> --overlap bash run_scope_pota.sh

set -uo pipefail

ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing
BUILD="${ROOT}/original_nurbs_preprocessing/build"
SCRATCH="${ROOT}/diag_scope"
SNAP="${ROOT}/diag_scope_snapshots"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF="${ROOT}/pcl_191_nurbs.sif"
POT=Pot_A
TREE="${SCRATCH}/${POT}"

in_container() {
    "${APPTAINER}" exec --bind /data:/data "${SIF}" /bin/bash -c "$1"
}

echo "### 1. build the mesh stage"
# The target is MeshPreprocessingHeadless, built from mesh_processing_headless.cpp.
# "MeshProcessingHeadless" does not exist and make says so plainly.
LOG=/tmp/mesh_build.log
in_container "cd '${BUILD}' && make -j8 MeshPreprocessingHeadless" > "${LOG}" 2>&1
rc=$?
echo "    build exit ${rc}"
if [ "${rc}" -ne 0 ]; then
    grep -E 'error:|Error [0-9]|No rule to make|CMake Error' "${LOG}" | head -n 15 || true
    tail -n 8 "${LOG}"
    exit 1
fi
ls -lh "${BUILD}/MeshPreprocessingHeadless" | awk '{print "    built:", $5, $9}'

echo
echo "### 2. stage Pot_A inputs"
rm -rf "${TREE}" "${SNAP}/${POT}"
mkdir -p "${TREE}/Temp/Data/${POT}" "${TREE}/Temp/Axes" \
         "${TREE}/Dataset/Mesh/${POT}" "${TREE}/Dataset/Point/${POT}" \
         "${TREE}/Dataset/Surfaces/${POT}" "${TREE}/Dataset/Breaklines/${POT}" \
         "${SNAP}/${POT}"
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
echo "### 3. mesh stage"
( cd "${TREE}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" \
    env POT_NAME="${POT}" "${BUILD}/MeshPreprocessingHeadless" ) \
    > "${SNAP}/${POT}_mesh.log" 2>&1
mrc=$?
produced=$(ls "${TREE}/Temp/Data/${POT}" 2>/dev/null | wc -l)
echo "    exit ${mrc}; ${produced} files now in Temp/Data/${POT}"
if [ "${mrc}" -ne 0 ]; then
    echo "    ** mesh stage FAILED. Tail:"
    tail -n 8 "${SNAP}/${POT}_mesh.log" | sed 's/^/       /'
    exit 1
fi
echo "    unclustered.ply produced: $(ls "${TREE}/Temp/Data/${POT}"/*unclustered.ply 2>/dev/null | wc -l)"
ls "${TREE}/Temp/Data/${POT}" 2>/dev/null | head -n 6 | sed 's/^/      /'

echo
echo "### 4. edgeline stage, snapshotting every sherd"
snapshot_loop() {
    local src="$1" dst="$2" last="" k=0 h
    mkdir -p "${dst}"
    while :; do
        if [ -f "${src}" ]; then
            h=$(md5sum "${src}" 2>/dev/null | cut -d' ' -f1)
            if [ -n "${h}" ] && [ "${h}" != "${last}" ]; then
                k=$((k + 1))
                cp "${src}" "${dst}/boundary_$(printf '%02d' ${k})_${h:0:8}.pcd"
                last="${h}"
            fi
        fi
        sleep 0.3
    done
}
snapshot_loop "${TREE}/Temp/Temp_edge/${POT}/boundary.pcd" "${SNAP}/${POT}" &
W=$!
( cd "${TREE}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" \
    env POT_NAME="${POT}" "${BUILD}/EdgeLineExtractionHeadless" ) \
    > "${SNAP}/${POT}.log" 2>&1
erc=$?
kill "${W}" 2>/dev/null; wait "${W}" 2>/dev/null

pieces=$(grep -c "ADAPTIVE SEQUENCING" "${SNAP}/${POT}.log" 2>/dev/null || true)
[ -n "${pieces}" ] || pieces=0
snaps=$(ls "${SNAP}/${POT}"/boundary_*.pcd 2>/dev/null | wc -l)
echo "    edgeline exit ${erc}"
echo "    pieces sequenced ${pieces}   snapshots ${snaps}"
if [ "${pieces}" -gt 0 ] && [ "${snaps}" -lt "${pieces}" ]; then
    echo "    ** INCOMPLETE snapshot -- fewer snapshots than pieces. NOT sound."
fi
grep "ADAPTIVE SEQUENCING" "${SNAP}/${POT}.log" 2>/dev/null \
    | sed 's/.*Boundary has \([0-9]*\) points, using K=\([0-9]*\).*/      n=\1 K=\2/' \
    | sort | uniq -c
echo
echo "Fetch: scp -r spartan:${SNAP}/${POT} <laptop>/.../artifacts/scope_snapshots/Pot_A"
