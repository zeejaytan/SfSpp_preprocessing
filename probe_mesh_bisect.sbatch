#!/bin/bash
#SBATCH --job-name=juglet_bisect
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=1:00:00
#SBATCH --output=juglet_bisect_%j.out
#SBATCH --error=juglet_bisect_%j.err

# Bisect piece-3/9 segmentation failures + verify the env-override mechanism.
# Context (all verified, see ticket 02): Step-1 P3 fails identically (1x492)
# in 6/6 full runs at 4.5 deg but succeeds ISOLATED in 3/3 Step-1c runs --
# deterministic + isolation-dependent => in-process cross-piece pollution
# (tmp files are write-only, never read: ruled out). And the
# SFS_SMOOTHNESS_DEG override NEVER compiled in (no "Segmentation
# thresholds" print in any log) -- all "25/45/60" conclusions are VOID.
# This job: rebuild with verified markers, then isolated variants.
echo "=== Juglet segmentation bisect ==="
echo "Started: $(date)"

cd /data/gpfs/projects/punim2657/sfs_preprocessing

POT_NAME="Juglet"
OUTPUT_BASE="/data/gpfs/projects/punim2657/sfs_preprocessing/Juglet_Dataset_20260916"
REPO_ROOT="/data/gpfs/projects/punim2657/sfs_preprocessing"
APPTAINER="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
NURBS_IMG="/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif"
export POT_NAME
export NURBS_OUTPUT_BASE="${OUTPUT_BASE}"
QDIR="${OUTPUT_BASE}/_quarantine"
mkdir -p ${QDIR}/pcd_hold

# ---- 1b: reset, patch (non-interactive), VERIFY markers, rebuild ----
cd ${REPO_ROOT}/original_nurbs_preprocessing
git checkout -- edgeline_extraction_headless.cpp mesh_processing_headless.cpp 2>/dev/null || true
rm -f *.orig
for p in ../patches/juglet_boundary_radius.patch ../patches/juglet_mesh_diag.patch ../patches/juglet_mesh_filter.patch ../patches/juglet_mesh_thresholds.patch; do
    patch -p1 --batch --forward < $p || { echo "ERROR: patch failed ($p)"; exit 1; }
done
grep -q "Single-file filter" mesh_processing_headless.cpp || { echo "ERROR: mesh filter marker absent"; exit 1; }
grep -q "Segmentation thresholds" mesh_processing_headless.cpp || { echo "ERROR: mesh env marker absent"; exit 1; }
grep -q "GROW-DIAG" mesh_processing_headless.cpp || { echo "ERROR: mesh diag marker absent"; exit 1; }
grep -q "g_boundary_radius_mm" edgeline_extraction_headless.cpp || { echo "ERROR: edgeline marker absent"; exit 1; }
echo "patch markers verified"
${APPTAINER} exec --bind /data:/data \
    ${NURBS_IMG} /bin/bash -c \
    "cd ${REPO_ROOT}/original_nurbs_preprocessing/build && rm -rf CMakeCache.txt CMakeFiles && cmake .. >/dev/null && make MeshPreprocessingHeadless -j4 2>&1 | tail -n 2"
[ $? -ne 0 ] && { echo "ERROR: rebuild failed"; exit 1; }
cd ${REPO_ROOT}
echo ""

run_piece_set() {
    # $1 = label, $2 = space-separated pieces to scan, $3 = smoothness (empty = default)
    label="$1"; pieces="$2"; thr="$3"
    mv -f Dataset/Point/${POT_NAME}/${POT_NAME}_Piece_[123456789]_Point.pcd ${QDIR}/pcd_hold/ 2>/dev/null || true
    for q in $pieces; do
        mv -f ${QDIR}/pcd_hold/${POT_NAME}_Piece_${q}_Point.pcd Dataset/Point/${POT_NAME}/ 2>/dev/null || true
    done
    rm -f Temp/Temp/${POT_NAME}/tmpSurfaceCluster_Improved_*.ply
    echo "--- variant ${label}: scanning [${pieces}] SFS_SMOOTHNESS_DEG=${thr:-default} ---"
    if [ -n "$thr" ]; then
        SFSENV="--env SFS_SMOOTHNESS_DEG=${thr}"
    else
        SFSENV=""
    fi
    ${APPTAINER} exec --bind /data:/data \
        --env POT_NAME="${POT_NAME}" \
        --env NURBS_OUTPUT_BASE="${OUTPUT_BASE}" \
        $SFSENV \
        ${NURBS_IMG} /bin/bash -c \
        "cd ${REPO_ROOT} && ./original_nurbs_preprocessing/build/MeshPreprocessingHeadless" 2>&1 | grep -E "Selected file|Number of clusters|Cluster [0-9]+ :|Could not achieve|Successfully found|thresholds:"
    mv -f ${QDIR}/pcd_hold/${POT_NAME}_Piece_*_Point.pcd Dataset/Point/${POT_NAME}/ 2>/dev/null || true
    echo ""
}
run_piece_set "V2-P3-alone-defaults" "3" ""
run_piece_set "V3-P2P3-defaults" "2 3" ""
run_piece_set "V5-P9-alone-25" "9" 25
run_piece_set "V6-P9-alone-60" "9" 60

echo "PCDs restored: $(ls Dataset/Point/${POT_NAME}/${POT_NAME}_Piece_[1-9]_Point.pcd 2>/dev/null | wc -l) (expected 9)"
echo "Done: $(date)"
