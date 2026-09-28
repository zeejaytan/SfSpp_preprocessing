#!/bin/bash
# Ticket 15, step 1: seed test. Run the mesh stage TWICE on identical inputs,
# diff Surface_0. No code change.
#
# WHY FIRST: improveSurfaceBoundaryByFittingBSplineSurface takes an UNSEEDED
# random 10k sample. If Surface_0 moves run to run, every gate number in this
# chain is a single draw without error bars, and the first fix may be a
# one-line seed rather than any geometry. If identical, the sampler is
# effectively stable and random sampling is out.
#
# Piece-2-only tree (proven staging pattern): the question is whether THIS
# sherd's surface moves, and a full-pot run does not fit the holder.
# Verification by cmp + ref-coverage both runs, never by exit code.
#
# Run inside a holder:  srun --jobid=<ID> --overlap bash run_seed_test.sh

set -uo pipefail

ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing
BUILD="${ROOT}/original_nurbs_preprocessing/build"
TREE="${ROOT}/diag_seed"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF="${ROOT}/pcl_191_nurbs.sif"
POT=Pot_A
OUT="${ROOT}/diag_seed_out"

[ -x "${BUILD}/MeshPreprocessingHeadless" ] || { echo "ERROR: not built"; exit 1; }
rm -rf "${TREE}" "${OUT}"
mkdir -p "${TREE}/Temp/Data/${POT}" "${TREE}/Temp/Axes" \
         "${TREE}/Dataset/Mesh/${POT}" "${TREE}/Dataset/Point/${POT}" \
         "${TREE}/Dataset/Surfaces/${POT}" "${TREE}/Dataset/Breaklines/${POT}" \
         "${OUT}"
# Piece 2 only. Mesh stage enumerates Dataset/Point/*.pcd, so staging only
# piece-2 files there limits the run without relying on the argv filter.
for f in "${ROOT}/Dataset/Mesh/${POT}"/Pot_A_Piece_02*.obj; do
    [ -e "${f}" ] || continue
    cp -L "${f}" "${TREE}/Dataset/Mesh/${POT}/"
done
for f in "${ROOT}/Dataset/Point/${POT}"/*Piece_02*; do
    [ -e "${f}" ] || continue
    cp -L "${f}" "${TREE}/Dataset/Point/${POT}/"
done
echo "    staged: $(ls "${TREE}/Dataset/Mesh/${POT}" | wc -l) obj, $(ls "${TREE}/Dataset/Point/${POT}" | wc -l) pcd"
[ "$(ls "${TREE}/Dataset/Point/${POT}" | wc -l)" -ge 1 ] || { echo "ERROR: nothing staged"; exit 1; }

for run in 1 2; do
    LOG="/tmp/seed_mesh_${run}.log"
    ( cd "${TREE}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" \
        env POT_NAME="${POT}" "${BUILD}/MeshPreprocessingHeadless" ) > "${LOG}" 2>&1
    DATA="${TREE}/Temp/Data/${POT}"
    n=$(ls "${DATA}"/Pot_A_Piece_02_Surface_0.xyz 2>/dev/null | wc -l)
    echo "    run ${run}: exit $? (not trusted)  Surface_0 present=${n}"
    if [ "${n}" -eq 0 ]; then
        echo "    ** no Surface_0. Tail:"
        tail -n 8 "${LOG}" | sed 's/^/       /'
        exit 1
    fi
    cp "${DATA}/Pot_A_Piece_02_Surface_0.xyz" "${OUT}/Surface_0_run${run}.xyz"
    cp "${DATA}/Pot_A_Piece_02_Surface_1.xyz" "${OUT}/Surface_1_run${run}.xyz" 2>/dev/null || true
    # clear per-run outputs so run 2 cannot read run 1's files
    rm -f "${DATA}"/Pot_A_Piece_02_Surface_*.xyz "${DATA}"/Pot_A_Piece_02_unclustered.ply
done

echo
echo "### verdict"
if cmp -s "${OUT}/Surface_0_run1.xyz" "${OUT}/Surface_0_run2.xyz"; then
    echo "    Surface_0 IDENTICAL across runs: sampler effectively stable,"
    echo "    random sampling is OUT as a contributor. Proceed to step 2"
    echo "    (save raw clusters)."
else
    echo "    Surface_0 DIFFERS run to run:"
    echo "    run1: $(wc -l < "${OUT}/Surface_0_run1.xyz") lines, run2: $(wc -l < "${OUT}/Surface_0_run2.xyz") lines"
fi
echo
echo "Fetch both for the laptop coverage check:"
echo "  scp spartan:${OUT}/Surface_0_run*.xyz <laptop>/artifacts/"
