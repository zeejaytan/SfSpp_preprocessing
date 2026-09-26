#!/bin/bash
#SBATCH --job-name=tidy_verify
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=tidy_verify_%j.out
#SBATCH --error=tidy_verify_%j.err

# Verification after the 2026-09-26 tidy-up (Temp/ untracked, nested repo
# dissolved into the main repo). The question this answers: does the
# pipeline still produce the KNOWN-GOOD breaklines from the tidied tree?
#
# Runs the existing binary (source is byte-identical, already proven by
# vendor_check job 31342607) with no patches beyond the seven already
# applied on disk, then diffs the output against the reference bundle.
# If the outputs match, the tidy changed nothing that matters.

set -o pipefail
REPO_ROOT="/data/gpfs/projects/punim2657/sfs_preprocessing"
SRC="${REPO_ROOT}/original_nurbs_preprocessing"
APPTAINER="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
IMG="${REPO_ROOT}/pcl_191_nurbs.sif"
REF="${REPO_ROOT}/Juglet_Dataset_20260916/SfS_pp"
OUT="${REPO_ROOT}/Juglet_Dataset_tidycheck"

echo "=== Tidy-up verification: does the pipeline still reproduce the known-good bundle? ==="
echo "Started: $(date)  Job: ${SLURM_JOB_ID}"

echo "--- preconditions"
md5sum "${SRC}/edgeline_extraction_headless.cpp"
echo "  expect aecfe83007a7de0b4c115cee577d6e71 (unchanged source)"
[ -x "${SRC}/build/EdgeLineExtractionHeadless" ] || { echo "ERROR: binary missing"; exit 1; }
echo "  binary present"

echo "--- Temp/ is empty/untracked now; the run must recreate it"
echo "  Temp/ file count before: $(find "${REPO_ROOT}/Temp" -type f 2>/dev/null | wc -l)"

rm -rf "${OUT}"
mkdir -p "${OUT}/SfS_pp/Breaklines"
cp -r "${REF}/Surfaces" "${OUT}/SfS_pp/"

# Stage the 9 single-digit meshes BY NAME (14-char truncation collides
# the 2-digit forms onto Juglet_Piece_0).
STAGE="${REPO_ROOT}/Temp/Data/Juglet"
rm -rf "${STAGE}"; mkdir -p "${STAGE}"
for p in $(seq 1 9); do
    cp -f "${REPO_ROOT}/Dataset/Mesh/Juglet/Juglet_Piece_$(printf '%02d' $p)_Mesh.obj" \
          "${STAGE}/Juglet_Piece_${p}_Mesh.obj" || { echo "ERROR: missing mesh $p"; exit 1; }
done
echo "  staged objs: $(ls ${STAGE}/*.obj 2>/dev/null | wc -l) (expected 9)"

export POT_NAME="Juglet" POT_ID="A" NURBS_OUTPUT_BASE="${OUT}"
${APPTAINER} exec --bind /data:/data "${IMG}" /bin/bash -lc \
    "cd ${REPO_ROOT} && ./original_nurbs_preprocessing/build/EdgeLineExtractionHeadless" \
    > "${OUT}/extract.log" 2>&1
rc=$?
echo "  extraction exit: ${rc}"
[ ${rc} -ne 0 ] && { tail -n 20 "${OUT}/extract.log"; echo "ERROR: extraction failed"; exit 1; }

n=$(ls "${OUT}/SfS_pp/Breaklines/"*_Breakline_0.pcd 2>/dev/null | wc -l)
echo "  produced Breakline_0 files: ${n} (expected 9)"
[ "${n}" -eq 9 ] || { echo "ERROR: expected 9"; exit 1; }

echo "--- Temp/ recreated by the run: $(find "${REPO_ROOT}/Temp" -type f 2>/dev/null | wc -l) files"

echo "--- compare against the known-good bundle (md5 per file)"
same=0; diff_files=""
for p in $(seq 1 9); do
    a="${REF}/Breaklines/Juglet_Piece_${p}_Breakline_0.pcd"
    b="${OUT}/SfS_pp/Breaklines/Juglet_Piece_${p}_Breakline_0.pcd"
    if [ ! -f "${a}" ]; then echo "  (no reference for piece ${p})"; continue; fi
    ma=$(md5sum "${a}" | cut -d' ' -f1); mb=$(md5sum "${b}" | cut -d' ' -f1)
    if [ "${ma}" = "${mb}" ]; then same=$((same+1)); else diff_files="${diff_files} ${p}"; fi
done
echo "  byte-identical to reference: ${same}/9"
if [ -n "${diff_files}" ]; then
    echo "  differing pieces:${diff_files}"
    echo "  NOTE: byte differences are expected if the run is not bit-deterministic;"
    echo "        the real question is whether the GEOMETRY matches, which the"
    echo "        laptop gate probe measures. Reporting both honestly."
fi
echo "Finished: $(date)"
