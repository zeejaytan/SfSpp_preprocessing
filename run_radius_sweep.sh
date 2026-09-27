#!/bin/bash
# Ticket 11: does our ~1.2 mm outward rim bias track the boundary radius?
#
# THE QUESTION
# Our rims sit ~1.2 mm further from their own centroid than the authors' on
# pieces 3-8, same sign every time, and at a joint the two biases add
# (1.2 + 1.2 ~ 2.4 mm) which straddles the 2 mm gate. The authors' rims are
# 0.09-1.30 mm apart on all fifteen pairs; ours are 3.7-22.9 mm on the eight
# that fail.
#
# The boundary radius is NOT a constant -- it is clamp(spacing * 6, 1, 15) mm,
# computed per sherd. So it is swept by absolute override, via
# SFSPP_BOUNDARY_RADIUS_MM, which is inert when unset.
#
# WHAT WOULD SETTLE IT
#   bias falls as the radius falls  -> the radius is the cause, and the fix is
#                                      a decision about the multiplier or clamp
#   bias is flat across the sweep  -> the radius is innocent, and candidates 2
#                                      and 3 in ticket 11 (smoothing, surface
#                                      construction) remain
#
# The sweep therefore INCLUDES a control arm with the variable unset. Without
# it, a drift in the pipeline or the input staging would be indistinguishable
# from a radius effect -- which is precisely the mistake ticket 10 recorded.
#
# Each arm writes its breaklines to its own output directory so the laptop can
# score them against the authors' rims per sherd.
#
# Run inside a holder:  srun --jobid=<ID> --overlap bash run_radius_sweep.sh

set -uo pipefail

ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing
BUILD="${ROOT}/original_nurbs_preprocessing/build"
BASE="${ROOT}/diag_pota3/Temp/Data/Pot_A"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF="${ROOT}/pcl_191_nurbs.sif"
OUT="${ROOT}/diag_radius_out"
POT=Pot_A
RADII="1.0 2.0 3.0 4.0 6.0 9.0"

[ -x "${BUILD}/EdgeLineExtractionHeadless" ] || { echo "ERROR: binary not built"; exit 1; }
[ -d "${BASE}" ] || { echo "ERROR: no mesh-stage output at ${BASE}"; exit 1; }

# The hook must be IN the binary. A stale object from an earlier failed
# build produced seven identical arms that all reported success, so this
# is checked before anything is staged.
if [ "$(strings "${BUILD}/EdgeLineExtractionHeadless" 2>/dev/null | grep -c "SFS-T11" || true)" = "0" ]; then
    echo "ERROR: the binary does not contain the sweep hook."
    echo "       A sweep without the hook produces identical arms and looks"
    echo "       successful. Run build_with_hook.sh first."
    exit 1
fi
echo "hook present in binary: yes"
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
    for f in "${BASE}"/*; do
        [ -e "${f}" ] || continue
        cp -L "${f}" "${tree}/Temp/Data/${POT}/"
    done
    local n_obj n_s0
    n_obj=$(ls "${tree}/Temp/Data/${POT}"/*.obj 2>/dev/null | wc -l)
    n_s0=$(ls "${tree}/Temp/Data/${POT}"/*_Surface_0.xyz 2>/dev/null | wc -l)
    echo "    staged ${n_obj} obj, ${n_s0} Surface_0.xyz"
    [ "${n_obj}" -eq 8 ] && [ "${n_s0}" -eq 8 ] || { echo "    ERROR: incomplete"; return 1; }
    return 0
}

run_arm() {
    local tag="$1" radius="$2"
    local tree="${ROOT}/diag_radius_${tag}"
    stage "${tree}" || return 1
    local log="/tmp/radius_${tag}.log"
    if [ "${radius}" = "unset" ]; then
        ( cd "${tree}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" \
            env -u SFSPP_BOUNDARY_RADIUS_MM POT_NAME="${POT}" \
            "${BUILD}/EdgeLineExtractionHeadless" ) > "${log}" 2>&1
    else
        ( cd "${tree}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" \
            env SFSPP_BOUNDARY_RADIUS_MM="${radius}" POT_NAME="${POT}" \
            "${BUILD}/EdgeLineExtractionHeadless" ) > "${log}" 2>&1
    fi
    local bl="${tree}/Dataset/Breaklines/${POT}" n
    n=$(ls "${bl}"/Pot_A_Piece_*_Breakline_0.pcd 2>/dev/null | wc -l)
    local adaptive
    adaptive=$(grep -o "boundary_r=[0-9.]*mm" "${log}" 2>/dev/null | head -n 1)
    local override
    # grep -c prints 0 AND exits 1 on no match, so `|| echo 0` appends a
    # second line. `|| true` is correct: the count is already in stdout.
    override=$(grep -c "SFS-T11.*OVERRIDDEN" "${log}" 2>/dev/null || true)
    [ -n "${override}" ] || override=0
    echo "    ${tag}: exit $?  breaklines=${n}  ${adaptive:-no boundary_r line}  overrides=${override}"
    if [ "${n}" -lt 8 ]; then
        echo "    ** expected 8 breaklines, got ${n}. Tail:"
        tail -n 8 "${log}" | sed 's/^/       /'
        return 1
    fi
    if [ "${tag}" = "control" ] && [ "${override}" != "0" ]; then
        echo "    ** the control arm reported an override (${override}) -- the hook"
        echo "       is not inert, so the sweep is void. Check that"
        echo "       SFSPP_BOUNDARY_RADIUS_MM is absent in the control arm."
        return 1
    fi
    mkdir -p "${OUT}/${tag}"
    cp "${bl}"/Pot_A_Piece_*_Breakline_0.pcd "${OUT}/${tag}/"
    rm -rf "${tree}"
    return 0
}

echo "### control arm: variable UNSET (the pipeline as it stands)"
run_arm control unset || exit 1

for r in ${RADII}; do
    echo
    echo "### radius ${r} mm"
    run_arm "r${r}" "${r}" || exit 1
done

echo
echo "### void check: any radius arm identical to the control?"
identical=""
for d in "${OUT}"/r*/; do
    [ -d "$d" ] || continue
    arm=$(basename "$d")
    if diff -r -q "${OUT}/control" "$d" > /dev/null 2>&1; then
        identical="${identical} ${arm}"
    fi
done
if [ -n "${identical}" ]; then
    echo "    ** IDENTICAL TO CONTROL:${identical}"
    echo "       Those arms did not change anything, so the sweep is VOID."
    echo "       The hook is linked but did not alter the output -- check"
    echo "       whether the override is reached on this code path."
    exit 1
fi
echo "    every radius arm differs from the control: sweep is real"
echo
echo "### out: ${OUT}"
for d in "${OUT}"/*/; do
    echo "  $(basename "$d"): $(ls "$d" 2>/dev/null | wc -l) breaklines"
done
echo
echo "Fetch and score each arm against the authors' rims:"
echo "  scp -r spartan:${OUT} <laptop>/structure-from-sherds-pp/artifacts/"
echo
echo "The measure is the radius difference (ours - authors) from the RIM's own"
echo "centroid, per sherd, and the PAIRWISE distance between our two rims. If"
echo "the bias falls with the radius, the radius is the cause."
