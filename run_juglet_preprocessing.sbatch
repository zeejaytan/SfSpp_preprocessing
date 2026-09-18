#!/bin/bash
#SBATCH --job-name=juglet_prep
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=4:00:00
#SBATCH --output=juglet_prep_%j.out
#SBATCH --error=juglet_prep_%j.err

# =====================================================================
# Juglet preprocessing: 9 sherds, scan-table poses, millimetres.
# Meshes staged at Dataset/Mesh/Juglet/Juglet_Piece_0X_Mesh.obj (from
# tora juglet_norm.hdf5 at vessel scale: longest side = 65 mm).
# GT (SFS++ format) staged at Dataset/Juglet_GT/ (not needed here,
# copied into the final bundle for the assembly run).
# Chain: OBJ -> PCD (ObjToPcd) -> Surfaces (MeshPreprocessingHeadless)
#        -> Breaklines (EdgeLineExtractionHeadless) -> Axes (MATLAB PotSAC)
# Binaries: original_nurbs_preprocessing/build{,_obj2pcd} (Nov-2025 fixed)
#
# NAMING (single digit, Juglet_Piece_1..9 — NOT 01..09): the Nov-2025
# binaries truncate every stem to its first 14 chars
# (fileNameOnly = stem.substr(0, 14), tuned for "Pot_A_Piece_01").
# "Juglet_Piece_01" is 15 chars, so all 9 pieces collapsed to
# "Juglet_Piece_0" and overwrote each other (job 30694326: Surfaces: 2,
# then breaklines crashed on stale Pot_A names). "Juglet_Piece_1" is
# exactly 14 chars, so the truncation is a no-op and mesh/edge/axis
# stages agree. Proper fix (suffix-strip helper + rebuild) is follow-up
# work; this keeps the tested Nov-2025 binaries untouched.
# =====================================================================

echo "=== Juglet Preprocessing Pipeline (9 pieces) ==="
echo "Started: $(date)"
echo "Job ID: ${SLURM_JOB_ID}"

cd /data/gpfs/projects/punim2657/sfs_preprocessing

POT_ID="A"                    # legacy label only; naming comes from POT_NAME
POT_NAME="Juglet"
NUM_PIECES=9
OUTPUT_BASE="/data/gpfs/projects/punim2657/sfs_preprocessing/Juglet_Dataset_20260916"
REPO_ROOT="/data/gpfs/projects/punim2657/sfs_preprocessing"
APPTAINER="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
NURBS_IMG="pcl_191_nurbs.sif"

export POT_NAME
export NURBS_OUTPUT_BASE="${OUTPUT_BASE}"

echo "POT_NAME: ${POT_NAME}, pieces: ${NUM_PIECES}"
echo "OUTPUT_BASE: ${OUTPUT_BASE}"
echo ""

# ---------- Step 0: OBJ -> PCD (single-digit names, see header) ----------
echo "=== Step 0: OBJ -> PCD ==="
OBJ2PCD="original_nurbs_preprocessing/build_obj2pcd/ObjToPcd"
if [ ! -x "${OBJ2PCD}" ]; then
    echo "ObjToPcd missing; building..."
    ${APPTAINER} exec --bind /data:/data "${NURBS_IMG}" /bin/bash -lc \
        "cd ${REPO_ROOT}/original_nurbs_preprocessing && rm -rf build_obj2pcd && mkdir -p build_obj2pcd && cd build_obj2pcd && cmake .. && make -j2 ObjToPcd"
fi
mkdir -p Dataset/Point/${POT_NAME}
# Single-digit mesh copies: the binaries derive the mesh name from the PCD
# stem, so both must use Juglet_Piece_N (2-digit originals stay untouched).
for p in $(seq 1 ${NUM_PIECES}); do
    src="Dataset/Mesh/${POT_NAME}/${POT_NAME}_Piece_$(printf '%02d' $p)_Mesh.obj"
    dst="Dataset/Mesh/${POT_NAME}/${POT_NAME}_Piece_${p}_Mesh.obj"
    if [ ! -f "${src}" ]; then echo "ERROR: missing ${src}"; exit 1; fi
    cp -f "${src}" "${dst}"
done
# Move aside 2-digit PCDs from earlier runs: the binaries scan the whole
# Point dir, and 2-digit stems would re-collide under truncation.
mkdir -p Dataset/Point/${POT_NAME}/backup_02digit
mv -f Dataset/Point/${POT_NAME}/${POT_NAME}_Piece_0?_Point.pcd Dataset/Point/${POT_NAME}/backup_02digit/ 2>/dev/null || true
for p in $(seq 1 ${NUM_PIECES}); do
    mesh="Dataset/Mesh/${POT_NAME}/${POT_NAME}_Piece_${p}_Mesh.obj"
    pcd="Dataset/Point/${POT_NAME}/${POT_NAME}_Piece_${p}_Point.pcd"
    ./${OBJ2PCD} "${mesh}" "${pcd}" || exit 1
done
FOUND=$(ls Dataset/Point/${POT_NAME}/${POT_NAME}_Piece_[1-9]_Point.pcd 2>/dev/null | wc -l)
echo "PCD files: ${FOUND} (expected ${NUM_PIECES})"
[ "${FOUND}" -ne ${NUM_PIECES} ] && { echo "ERROR: PCD count mismatch"; exit 1; }
echo ""

# ---------- Output dirs ----------
mkdir -p ${OUTPUT_BASE}/SfS_pp/Surfaces
mkdir -p ${OUTPUT_BASE}/SfS_pp/Breaklines
mkdir -p ${OUTPUT_BASE}/SfS_pp/Axes
mkdir -p ${OUTPUT_BASE}/SfS_pp/Mesh
mkdir -p "${OUTPUT_BASE}/SfS_pp/Ground Truth"
mkdir -p Temp/Data/${POT_NAME}
mkdir -p Temp/Temp/${POT_NAME}
mkdir -p Temp/Temp_edge/${POT_NAME}
mkdir -p original_nurbs_preprocessing/build/Segments/
rm -f Temp/Data/${POT_NAME}/*.xyz
rm -f Temp/Temp/${POT_NAME}/*.ply
rm -f Temp/Temp_edge/${POT_NAME}/*.ply
# Fresh bundle: drop previous-run outputs incl. 30694326's truncated
# "Juglet_Piece_0_*" files and the binary-copied Mesh/Point duplicates.
rm -f ${OUTPUT_BASE}/SfS_pp/Surfaces/*
rm -f ${OUTPUT_BASE}/SfS_pp/Breaklines/*
rm -f ${OUTPUT_BASE}/SfS_pp/Axes/*
# Breakline discovery scans Temp/ for *.obj (Pot_A-era mechanism). Stale
# Pot_A meshes left there would hijack the run (crashed 30694326 on
# Pot_A_Piece_01 names), and in OUTPUT_BASE mode our meshes never land in
# Temp/ — so quarantine every pre-existing *.obj, then stage ours.
mkdir -p Temp/stale_obj_backup
find Temp -maxdepth 3 -name "*.obj" -not -path "*/stale_obj_backup/*" -exec mv -f {} Temp/stale_obj_backup/ \; 2>/dev/null || true
cp -f Dataset/Mesh/${POT_NAME}/${POT_NAME}_Piece_[1-9]_Mesh.obj Temp/Data/${POT_NAME}/
echo "Staged for breakline discovery: $(ls Temp/Data/${POT_NAME}/*.obj 2>/dev/null | wc -l) (expected ${NUM_PIECES})"

# ---------- Step 1: surfaces ----------
echo "=== Step 1: Surface Generation ==="
# NOTE: binaries run with cwd = repo root; their Dataset/...,
# Temp/... paths are root-relative (the Dataset symlink lives at
# original_nurbs_preprocessing/Dataset -> ../Dataset, NOT under build/).
# Bind is /data:/data (NOT ...:/workspace): /workspace is already a GPFS
# mount inside the container so that bind is shadowed — verified 2026-09-17
# (Step 1 saw a stale /workspace/Dataset and failed on Dataset/Point/Juglet/).
${APPTAINER} exec --bind /data:/data \
    --env POT_NAME="${POT_NAME}" \
    --env NURBS_OUTPUT_BASE="${OUTPUT_BASE}" \
    ${NURBS_IMG} /bin/bash -c \
    "cd ${REPO_ROOT} && ./original_nurbs_preprocessing/build/MeshPreprocessingHeadless"
[ $? -ne 0 ] && { echo "ERROR: surface generation failed"; exit 1; }
echo "Surfaces: $(ls ${OUTPUT_BASE}/SfS_pp/Surfaces/${POT_NAME}_Piece_*_Surface_*.xyz 2>/dev/null | wc -l) (expected $((NUM_PIECES * 2)))"
echo "Sample coords (mm expected, not e+07):"
head -n 1 ${OUTPUT_BASE}/SfS_pp/Surfaces/${POT_NAME}_Piece_1_Surface_0.xyz
echo ""

# ---------- Step 2: breaklines ----------
echo "=== Step 2: Breakline Extraction ==="
${APPTAINER} exec --bind /data:/data \
    --env POT_NAME="${POT_NAME}" \
    --env NURBS_OUTPUT_BASE="${OUTPUT_BASE}" \
    ${NURBS_IMG} /bin/bash -c \
    "cd ${REPO_ROOT} && ./original_nurbs_preprocessing/build/EdgeLineExtractionHeadless"
[ $? -ne 0 ] && { echo "ERROR: breakline extraction failed"; exit 1; }
echo "Breaklines: $(ls ${OUTPUT_BASE}/SfS_pp/Breaklines/${POT_NAME}_Piece_*_Breakline_*.pcd 2>/dev/null | wc -l) (expected $((NUM_PIECES * 2)))"
echo ""

# ---------- Step 3: axes (MATLAB PotSAC) ----------
echo "=== Step 3: MATLAB Axis Extraction ==="
module load MATLAB/2024b_Update_3
matlab -batch "
addpath('.');
for piece = 1:${NUM_PIECES}
    piece_str = sprintf('%d', piece);
    surface_file = sprintf('${OUTPUT_BASE}/SfS_pp/Surfaces/${POT_NAME}_Piece_%s_Surface_0.xyz', piece_str);
    output_file = sprintf('${OUTPUT_BASE}/SfS_pp/Axes/${POT_NAME}_Piece_%s_Axis.xyz', piece_str);
    fprintf('Processing piece %s/%d...\n', piece_str, ${NUM_PIECES});
    if exist(surface_file, 'file')
        try
            extract_single_axis('${POT_ID}', piece, surface_file, output_file);
            fprintf('ok piece %s\n', piece_str);
        catch ME
            fprintf('FAILED piece %s: %s\n', piece_str, ME.message);
        end
    else
        fprintf('missing surface: %s\n', surface_file);
    end
end
fprintf('axis extraction done\n');
quit;
"
echo "Axes: $(ls ${OUTPUT_BASE}/SfS_pp/Axes/${POT_NAME}_Piece_*_Axis.xyz 2>/dev/null | wc -l) (expected ${NUM_PIECES})"
echo ""

# ---------- Stage Mesh + GT into the bundle (single-digit meshes) ----------
cp -f Dataset/Mesh/${POT_NAME}/${POT_NAME}_Piece_[1-9]_Mesh.obj ${OUTPUT_BASE}/SfS_pp/Mesh/
cp -f Dataset/Juglet_GT/${POT_NAME}_Piece_*_T.txt "${OUTPUT_BASE}/SfS_pp/Ground Truth/"
cp -f Dataset/Juglet_GT/${POT_NAME}_simple_graph.txt "${OUTPUT_BASE}/SfS_pp/Ground Truth/"

echo "=== Final Bundle ==="
echo "Surfaces:   $(ls ${OUTPUT_BASE}/SfS_pp/Surfaces/${POT_NAME}_Piece_*_Surface_*.xyz 2>/dev/null | wc -l)"
echo "Breaklines: $(ls ${OUTPUT_BASE}/SfS_pp/Breaklines/${POT_NAME}_Piece_*_Breakline_*.pcd 2>/dev/null | wc -l)"
echo "Axes:       $(ls ${OUTPUT_BASE}/SfS_pp/Axes/${POT_NAME}_Piece_*_Axis.xyz 2>/dev/null | wc -l)"
echo "Mesh:       $(ls ${OUTPUT_BASE}/SfS_pp/Mesh/*.obj 2>/dev/null | wc -l)"
echo "GT:         $(ls "${OUTPUT_BASE}/SfS_pp/Ground Truth/" 2>/dev/null | wc -l)"
echo "Done: $(date)"
