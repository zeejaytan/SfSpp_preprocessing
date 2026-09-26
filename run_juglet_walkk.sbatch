#!/bin/bash
#SBATCH --job-name=juglet_walkk
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=juglet_walkk_%j.out
#SBATCH --error=juglet_walkk_%j.err

# =====================================================================
# Ticket 02, patch 1 of 4: make the rim walk LOCAL (K=2).
#
# ONE variable. The previous patches (juglet_boundary_radius etc.) are
# applied too, because they are already-merged behaviour, not part of
# this test. The walk-k patch is the only NEW change.
#
# Writes to a SEPARATE output base so the known-good bundle
# (Juglet_Dataset_20260916) is never overwritten: a regression must be
# able to fall back to it.
#
# Marker discipline: patch silently drops misordered hunks while exiting
# 0, so the marker is grepped in the SOURCE after patching AND the K
# value is confirmed in the run log. A run whose marker is absent is
# void, not a negative result.
# =====================================================================

set -o pipefail

REPO_ROOT="/data/gpfs/projects/punim2657/sfs_preprocessing"
APPTAINER="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
NURBS_IMG="${REPO_ROOT}/pcl_191_nurbs.sif"
OUT_BASE="${REPO_ROOT}/Juglet_Dataset_walkk1"

echo "=== Juglet breakline re-extract: walk K=2 (ticket 02 patch 1) ==="
echo "Started: $(date)   Job: ${SLURM_JOB_ID}"
echo "Output base: ${OUT_BASE}  (original bundle untouched)"

# Create the output base FIRST. The build log is redirected into it, and
# a redirect into a missing directory fails before the command runs -- job
# 31337028 reported "build failed (rc=1)" with an empty log for exactly
# this reason, and no build was attempted at all.
mkdir -p "${OUT_BASE}" || { echo "ERROR: cannot create ${OUT_BASE}"; exit 1; }
echo "  output base ready"

cd "${REPO_ROOT}" || exit 1

echo "=== Syncing code ==="
git pull --ff-only || { echo "ERROR: pull failed (diverged?)"; exit 1; }

# 165 tracked data files are skip-worktree flagged on this checkout; if a
# pull touches them it errors above. Report the state either way.
echo "skip-worktree flagged files: $(git ls-files -v | grep -c '^S' || true)"

# ---------- apply patches ----------
# NOTE 1: the compiled source is original_nurbs_preprocessing/
# edgeline_extraction_headless.cpp -- CMakeLists.txt lives in that dir and
# names bare filenames. It is UNTRACKED in git, so `git checkout` on it is
# a silent no-op and there is NO WAY TO RESET IT. Spartan's copy already
# carries an unknown subset of the patch set (verified: g_boundary_radius_mm
# is present, and juglet_boundary_radius.patch therefore refuses under
# --forward). The original run_juglet_preprocessing.sbatch has the same
# latent problem -- it is not re-runnable on the current cluster state.
#
# So: apply IDEMPOTENTLY. Skip a patch whose marker is already present,
# apply it otherwise, then verify EVERY marker before building. If a marker
# is missing the run aborts rather than silently building unpatched code.
SRC_DIR="${REPO_ROOT}/original_nurbs_preprocessing"
echo "=== Applying patches (in ${SRC_DIR}) ==="
cd "${SRC_DIR}" || { echo "ERROR: no ${SRC_DIR}"; exit 1; }
echo "  state before patching:"
md5sum edgeline_extraction_headless.cpp

apply_patch() {   # $1=patch file  $2=marker  $3=target file
    local p="$1" marker="$2" target="$3"
    if grep -qF "${marker}" "${target}"; then
        echo "  SKIP  (already applied) $(basename ${p})"
        return 0
    fi
    if patch -p1 --batch --forward --fuzz=0 < "${p}"; then
        echo "  APPLIED $(basename ${p})"
    else
        echo "  ERROR: patch failed: ${p}"
        return 1
    fi
    if ! grep -qF "${marker}" "${target}"; then
        echo "  ERROR: patch claimed success but marker absent (SILENT DROP): ${p}"
        return 1
    fi
}

E=edgeline_extraction_headless.cpp
M=mesh_processing_headless.cpp
apply_patch ../patches/juglet_boundary_radius.patch   "g_boundary_radius_mm"        "${E}" || exit 1
apply_patch ../patches/juglet_mesh_diag.patch         "GROW-DIAG"                  "${M}" || exit 1
apply_patch ../patches/juglet_mesh_filter.patch       "Single-file filter"         "${M}" || exit 1
apply_patch ../patches/juglet_mesh_thresholds.patch   "Segmentation thresholds"    "${M}" || exit 1
apply_patch ../patches/juglet_edgeline_spheremin.patch    "keep everything in mm"   "${E}" || exit 1
apply_patch ../patches/juglet_edgeline_sphereradii.patch  "mm (was meters-assumed)" "${E}" || exit 1
apply_patch ../patches/juglet_edgeline_nowriteconvert.patch "do NOT convert"        "${E}" || exit 1
apply_patch ../patches/juglet_edgeline_walkk_headless.patch "SFS_WALK_K_LOCAL"    "${E}" || exit 1

echo "=== Verifying all markers present ==="
for m in g_boundary_radius_mm "keep everything in mm" "mm (was meters-assumed)" "do NOT convert" SFS_WALK_K_LOCAL; do
    grep -qF "${m}" "${E}" || { echo "ERROR: edgeline marker absent: ${m}"; exit 1; }
    echo "  edgeline: ${m}"
done
for m in "GROW-DIAG" "Single-file filter" "Segmentation thresholds"; do
    grep -qF "${m}" "${M}" || { echo "ERROR: mesh marker absent: ${m}"; exit 1; }
    echo "  mesh: ${m}"
done
echo "  all markers verified"
rm -f *.orig *.rej
echo "  walk K line(s):"
grep -n "SFS_WALK_K_LOCAL" "${E}"
grep -n "int K = " "${E}" | head -3

# ---------- build ----------
# Absolute paths throughout: the patch block left us cd'd in ${SRC_DIR},
# and a relative check there reported "binary missing" on job 31336993
# even though the build had just succeeded.
BUILD_DIR="${SRC_DIR}/build"
echo "=== Building EdgeLineExtractionHeadless ==="
cd "${REPO_ROOT}" || exit 1
${APPTAINER} exec --bind /data:/data "${NURBS_IMG}" /bin/bash -lc \
    "cd ${SRC_DIR} && rm -rf build && mkdir -p build && cd build && cmake .. && make -j8 EdgeLineExtractionHeadless" \
    > "${OUT_BASE}/build_walkk.log" 2>&1
rc=$?
if [ ${rc} -ne 0 ]; then
    echo "ERROR: build failed (rc=${rc}); last 25 lines:"
    tail -n 25 "${OUT_BASE}/build_walkk.log"
    exit 1
fi
tail -n 3 "${OUT_BASE}/build_walkk.log"
[ -x "${BUILD_DIR}/EdgeLineExtractionHeadless" ] \
    || { echo "ERROR: binary missing at ${BUILD_DIR}"; exit 1; }
ls -lh "${BUILD_DIR}/EdgeLineExtractionHeadless"

# ---------- re-extract breaklines only ----------
# Surfaces and meshes are unchanged by this patch, so they are reused
# from the known-good bundle. Only Step 2 (breaklines) re-runs.
echo "=== Staging surfaces (reused, unchanged) ==="
mkdir -p "${OUT_BASE}/SfS_pp/Breaklines"
cp -r "${REPO_ROOT}/Juglet_Dataset_20260916/SfS_pp/Surfaces" "${OUT_BASE}/SfS_pp/" 2>/dev/null
echo "  surfaces: $(ls ${OUT_BASE}/SfS_pp/Surfaces/*_Surface_*.xyz 2>/dev/null | wc -l) files (expected 18)"

export POT_NAME="Juglet"
export POT_ID="A"
export NURBS_OUTPUT_BASE="${OUT_BASE}"

echo "=== Step 2: Breakline Extraction (walk K=2) ==="
rm -f "${OUT_BASE}/SfS_pp/Breaklines/"*.pcd
# Breakline discovery scans Temp/ recursively for *.obj
mkdir -p "${REPO_ROOT}/Temp/Data/Juglet"
cp -f "${REPO_ROOT}"/Dataset/Mesh/Juglet/Juglet_Piece_*_Mesh.obj "${REPO_ROOT}/Temp/Data/Juglet/" 2>/dev/null
echo "  staged objs: $(ls ${REPO_ROOT}/Temp/Data/Juglet/*.obj 2>/dev/null | wc -l) (expected 9)"

${APPTAINER} exec --bind /data:/data "${NURBS_IMG}" /bin/bash -lc \
    "cd ${REPO_ROOT} && ./original_nurbs_preprocessing/build/EdgeLineExtractionHeadless" \
    > "${OUT_BASE}/edgeline_walkk.log" 2>&1
rc=$?
echo "  extraction exit: ${rc}"
tail -n 20 "${OUT_BASE}/edgeline_walkk.log"

# ---------- confirm K took effect at runtime ----------
echo "=== Runtime K confirmation ==="
grep -a "ADAPTIVE SEQUENCING" "${OUT_BASE}/edgeline_walkk.log" | head -n 12 \
    || echo "ERROR: no sequencing lines -- the patched function did not run"
if grep -qa "ADAPTIVE SEQUENCING" "${OUT_BASE}/edgeline_walkk.log"; then
    n50=$(grep -ac "using K=50" "${OUT_BASE}/edgeline_walkk.log" || true)
    n2=$(grep -ac "using K=2 " "${OUT_BASE}/edgeline_walkk.log" || true)
    echo "  lines with K=50: ${n50}   lines with K=2: ${n2}"
    if [ "${n50}" -gt 0 ]; then
        echo "ERROR: K=50 still in the log -- STALE BINARY, VOID RUN"; exit 1
    fi
fi

# ---------- inventory, no gate here ----------
echo "=== New breaklines ==="
ls -1 "${OUT_BASE}/SfS_pp/Breaklines/" 2>/dev/null
nb=$(ls "${OUT_BASE}/SfS_pp/Breaklines/"*_Breakline_0.pcd 2>/dev/null | wc -l)
echo "  Breakline_0 files: ${nb} (expected 9)"
[ "${nb}" -eq 9 ] || { echo "ERROR: expected 9 breakline files"; exit 1; }

# The real acceptance test runs on the laptop against these files:
#   gate_probe_b0.py <bundle>
# It is NOT run here on purpose -- the gate needs the meshes and GT from
# the assembly repo, and scoring a re-extract from inside the extracting
# job is how a broken input gets certified by its own producer.
echo ""
echo "=== DONE. Bundle at ${OUT_BASE} ==="
echo "Next: fetch to laptop, then run gate_probe_b0.py on the new bundle."
echo "Finished: $(date)"
