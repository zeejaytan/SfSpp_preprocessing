#!/bin/bash
# Ticket 14 experiment: does boundary detection return piece 2's rim from
# Surface_0 + nearby-unclustered union?
#
# THREE ARMS, differing ONLY in the S0-path input file (no axis staged, so
# Breakline_0 always comes from the S0 path -- the vote cannot confound it):
#   control  unmodified S0 (11,263 pts; expect the known 138mm / 2.82mm rim)
#   D3       S0 + unclustered within 3mm (12,652 pts)
#   D5       S0 + unclustered within 5mm (12,690 pts)
#
# The union files are built on the laptop (build_union_surface.py); this
# script stages them as the S0-path input. No rebuild, existing binary.
#
# Decisive OUTCOMES, stated before running:
#   a D-arm rim near 303mm long and <1mm from the reference -> the union is
#     sufficient; design the pipeline merge step next
#   neither D-arm moves vs control -> the union is not sufficient; the
#     surface shortfall needs a different fix (recorded, not forced)
# Either way the gate pairs are scored on the laptop afterwards, never here.
#
# Run inside a holder:  srun --jobid=<ID> --overlap bash run_union_experiment.sh

set -uo pipefail

ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing
BUILD="${ROOT}/original_nurbs_preprocessing/build"
BASE="${ROOT}/diag_pota3/Temp/Data/Pot_A"
LAPTOP_UNION="piece2_union"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF="${ROOT}/pcl_191_nurbs.sif"
OUT="${ROOT}/diag_union_out"
POT=Pot_A

[ -x "${BUILD}/EdgeLineExtractionHeadless" ] || { echo "ERROR: not built"; exit 1; }
[ -d "${BASE}" ] || { echo "ERROR: no mesh output at ${BASE}"; exit 1; }
rm -rf "${OUT}"; mkdir -p "${OUT}"

run_arm() {
    local tag="$1" s0src="$2"
    local tree="${ROOT}/diag_union_${tag}"
    local log="/tmp/union_${tag}.log"
    rm -rf "${tree}"
    mkdir -p "${tree}/Temp/Data/${POT}" "${tree}/Temp/Axes" \
             "${tree}/Dataset/Mesh/${POT}" "${tree}/Dataset/Point/${POT}" \
             "${tree}/Dataset/Surfaces/${POT}" "${tree}/Dataset/Breaklines/${POT}" \
             "${tree}/Dataset/Axes"
    # Piece-2 inputs from the unexchanged mesh output. NO axis files staged:
    # without an axis the vote warns and keeps historic order, so Breakline_0
    # comes from the S0 path in every arm by construction.
    for f in "${BASE}"/Pot_A_Piece_02*; do
        [ -e "${f}" ] || continue
        cp -L "${f}" "${tree}/Temp/Data/${POT}/"
    done
    # The one variable: replace the S0-path input with the arm's file.
    cp -L "${s0src}" "${tree}/Temp/Data/${POT}/Pot_A_Piece_02_Surface_0.xyz"
    echo "    ${tag}: S0-path input: $(wc -l < "${tree}/Temp/Data/${POT}/Pot_A_Piece_02_Surface_0.xyz") lines"
    ( cd "${tree}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" \
        env POT_NAME="${POT}" "${BUILD}/EdgeLineExtractionHeadless" ) > "${log}" 2>&1
    local bl="${tree}/Dataset/Breaklines/${POT}"
    local nbl nseq
    nbl=$(ls "${bl}"/Pot_A_Piece_02_Breakline_0.pcd 2>/dev/null | wc -l)
    nseq=$(grep -c "ADAPTIVE SEQUENCING" "${log}" 2>/dev/null || true)
    [ -n "${nseq}" ] || nseq=0
    echo "    ${tag}: exit $? (not trusted)  sequenced=${nseq}  Breakline_0 present=${nbl}"
    if [ "${nbl}" -eq 0 ]; then
        echo "    ** no Breakline_0. Tail:"
        tail -n 8 "${log}" | sed 's/^/       /'
        return 1
    fi
    mkdir -p "${OUT}/${tag}"
    cp "${bl}"/Pot_A_Piece_02_Breakline_0.pcd "${OUT}/${tag}/"
    # boundary cloud for coverage diagnosis (Temp_edge keeps the last only,
    # but single-surface interest is the S0 path; record both files present)
    local edge="${tree}/Temp/Temp_edge/${POT}"
    cp "${edge}"/boundary.pcd "${OUT}/${tag}/boundary.pcd" 2>/dev/null || true
    rm -rf "${tree}"
    return 0
}

echo "### control: unmodified S0"
run_arm control "${BASE}/Pot_A_Piece_02_Surface_0.xyz" || exit 1
for D in 3 5; do
    echo
    echo "### union D=${D}mm"
    # Uploaded beforehand (see fetch step below); abort loudly if absent
    # rather than silently running the control input twice.
    UPL="${ROOT}/upload_piece2_union/Pot_A_Piece_02_Surface_0_D${D}.xyz"
    if [ ! -s "${UPL}" ]; then
        echo "    ERROR: union file missing at ${UPL} -- upload first"
        exit 1
    fi
    run_arm "D${D}" "${UPL}" || exit 1
done

echo
echo "### out: ${OUT}"
for d in "${OUT}"/*/; do
    echo "  $(basename "$d"): $(ls "$d" 2>/dev/null | wc -l) files"
done
echo
echo "Score on the laptop vs the 169-pt / 303.5mm reference and the gate pairs."
