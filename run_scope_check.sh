#!/bin/bash
# Ticket 08: is the ordering defect Juglet-specific or general?
#
# Runs the edgeline stage on BOTH pots and snapshots every sherd's
# boundary.pcd, so the two can be compared like for like.
#
# WHY AN ISOLATED TREE
# The binary uses RELATIVE paths ("Temp/", "Dataset/..."), so the working
# directory decides what it reads and writes. Running it in the real tree
# would overwrite Temp/Temp_edge/ -- the live Juglet intermediates -- and
# Dataset/Breaklines/. Those may be live inputs of the current assembly
# runs (see AGENTS.md on skip-worktree data). So each pot gets its own
# throwaway tree and nothing outside diag_scope/ is touched.
#
# WHY A SNAPSHOTTER
# Temp/Temp_edge/<pot>/boundary.pcd is OVERWRITTEN per sherd, so after a
# run only the last sherd survives. Pieces take ~2.2 s each, so polling
# every 0.3 s and de-duplicating by md5 catches each one. The script
# reports how many snapshots it got against how many pieces the run
# processed -- if those disagree, the snapshot is incomplete and the
# comparison is not sound.
#
# Run inside a holder:  srun --jobid=<ID> --overlap bash run_scope_check.sh

set -uo pipefail

ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing
BIN="${ROOT}/original_nurbs_preprocessing/build/EdgeLineExtractionHeadless"
SCRATCH="${ROOT}/diag_scope"
SNAP="${ROOT}/diag_scope_snapshots"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF="${ROOT}/pcl_191_nurbs.sif"

[ -x "${BIN}" ] || { echo "ERROR: ${BIN} missing -- build first"; exit 1; }
[ -f "${SIF}" ] || { echo "ERROR: ${SIF} missing"; exit 1; }

# Where each pot's inputs live. Two things must be staged, because the
# edgeline stage consumes SURFACE point clouds produced by the earlier mesh
# stage -- it does not read the .obj meshes itself:
#
#   <obj meshes>                 -> Temp/Data/<pot>/*.obj        (enumerates pieces)
#   Dataset/Surfaces/<pot>/*     -> Temp/Data/<pot>/*            (the actual input)
#
# Pot_A's .obj files are symlinks into temp_download/, so they are copied
# with -L to bring the real vertices across. Dataset/Surfaces/ currently
# holds 18 Juglet and 24 Pot_A files; the real tree's Temp/Data/ has NO
# Surface_*.xyz at all, so this staging is not optional -- without it the
# binary exits 255 on "cannot copy file ... Surface_0.xyz".
declare -A MESHES=(
    [Juglet]="${ROOT}/Temp/Data/Juglet"
    [Pot_A]="${ROOT}/Dataset/Mesh/Pot_A"
)
SURFACES="${ROOT}/Dataset/Surfaces"

snapshot_loop() {
    # $1 = boundary.pcd to watch, $2 = destination dir
    local src="$1" dst="$2" last="" n=0
    mkdir -p "${dst}"
    while :; do
        if [ -f "${src}" ]; then
            local h
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

run_pot() {
    local pot="$1" src="${MESHES[$1]}"
    local tree="${SCRATCH}/${pot}"
    local edge="${tree}/Temp/Temp_edge/${pot}"
    local snapdir="${SNAP}/${pot}"
    local log="${SNAP}/${pot}.log"

    echo
    echo "=============================================================="
    echo "=== ${pot}"
    echo "=============================================================="
    if [ ! -d "${src}" ]; then echo "SKIP: no meshes at ${src}"; return 1; fi

    rm -rf "${tree}" "${snapdir}"
    mkdir -p "${tree}/Temp/Data/${pot}" "${tree}/Temp/Axes" \
             "${tree}/Dataset/Mesh/${pot}" \
             "${tree}/Dataset/Surfaces/${pot}" \
             "${tree}/Dataset/Breaklines/${pot}" "${snapdir}"

    local n=0 s=0
    for f in "${src}"/*.obj; do
        [ -e "${f}" ] || continue
        cp -L "${f}" "${tree}/Temp/Data/${pot}/"   # -L: follow symlinks
        n=$((n + 1))
    done
    for f in "${SURFACES}/${pot}"/*; do
        [ -e "${f}" ] || continue
        cp -L "${f}" "${tree}/Temp/Data/${pot}/"
        s=$((s + 1))
    done
    echo "  staged ${n} meshes and ${s} surface clouds"

    snapshot_loop "${edge}/boundary.pcd" "${snapdir}" &
    local watcher=$!

    # The binary must run INSIDE the container (PCL libs) and with cwd set to
    # the isolated tree. POT_NAME is what selects the pot at runtime.
    ( cd "${tree}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" \
        env POT_NAME="${pot}" "${BIN}" ) > "${log}" 2>&1
    local rc=$?

    kill "${watcher}" 2>/dev/null
    wait "${watcher}" 2>/dev/null

    local pieces snaps
    # grep -c prints 0 AND exits 1 when there is no match, so `|| echo 0`
    # would append a second line and make the integer test fail. `|| true`
    # alone is correct: the count is already in the output.
    pieces=$(grep -c "ADAPTIVE SEQUENCING" "${log}" 2>/dev/null || true)
    [ -n "${pieces}" ] || pieces=0
    snaps=$(ls "${snapdir}"/boundary_*.pcd 2>/dev/null | wc -l)

    echo "  exit code            ${rc}"
    if [ "${rc}" -ne 0 ]; then
        echo "  ** the binary failed. Tail of its log:"
        tail -n 6 "${log}" 2>/dev/null | sed 's/^/     /'
    fi
    echo "  pieces sequenced     ${pieces}   (from the run log)"
    echo "  boundary snapshots   ${snaps}"
    if [ "${pieces}" -gt 0 ] && [ "${snaps}" -lt "${pieces}" ]; then
        echo "  ** INCOMPLETE: fewer snapshots than pieces. The snapshotter"
        echo "     missed sherd(s), so this pot's comparison is NOT sound."
        echo "     Re-run with a shorter poll interval."
    fi
    echo "  boundary point counts, per sherd, from the log:"
    grep "ADAPTIVE SEQUENCING" "${log}" 2>/dev/null \
        | sed 's/.*Boundary has \([0-9]*\) points, using K=\([0-9]*\).*/    n=\1 K=\2/' \
        | sort | uniq -c | sed 's/^/  /' | head -n 20
    echo "  snapshots in ${snapdir}"
    return 0
}

echo "scope check: ordering defect -- Juglet vs Pot_A"
echo "scratch tree:  ${SCRATCH}   (nothing outside this and ${SNAP} is touched)"
mkdir -p "${SNAP}"

for pot in Juglet Pot_A; do
    run_pot "${pot}"
done

echo
echo "=============================================================="
echo "=== snapshots on disk"
echo "=============================================================="
for pot in Juglet Pot_A; do
    d="${SNAP}/${pot}"
    [ -d "${d}" ] || continue
    echo "  ${pot}: $(ls "${d}"/boundary_*.pcd 2>/dev/null | wc -l) files"
done
echo
echo "Fetch them to the laptop with:"
echo "  scp -r spartan:${SNAP} <laptop>/SfSpp_preprocessing/artifacts/scope_snapshots"
