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

cd "${REPO_ROOT}" || exit 1

echo "=== Syncing code ==="
git pull --ff-only || { echo "ERROR: pull failed (diverged?)"; exit 1; }

# 165 tracked data files are skip-worktree flagged on this checkout; if a
# pull touches them it errors above. Report the state either way.
echo "skip-worktree flagged files: $(git ls-files -v | grep -c '^S' || true)"

# ---------- apply patches ----------
echo "=== Applying patches ==="
git checkout -- edgeline_extraction_headless.cpp mesh_processing_headless.cpp 2>/dev/null || true
for p in ../patches/juglet_boundary_radius.patch \
         ../patches/juglet_mesh_diag.patch \
         ../patches/juglet_mesh_filter.patch \
         ../patches/juglet_mesh_thresholds.patch \
         ../patches/juglet_edgeline_spheremin.patch \
         ../patches/juglet_edgeline_sphereradii.patch \
         ../patches/juglet_edgeline_nowriteconvert.patch \
         ../patches/juglet_edgeline_walkk_headless.patch; do
    patch -p1 --forward --fuzz=0 < "${p}"
    rc=$?
    if [ ${rc} -ne 0 ]; then
        echo "ERROR: patch failed (rc=${rc}): ${p}"
        exit 1
    fi
    echo "  applied ${p}"
done

# ---------- verify markers in the SOURCE, before building ----------
echo "=== Verifying markers in patched source ==="
grep -q "g_boundary_radius_mm" edgeline_extraction_headless.cpp \
    || { echo "ERROR: boundary radius marker absent"; exit 1; }
grep -q "SFS_WALK_K_LOCAL" edgeline_extraction_headless.cpp \
    || { echo "ERROR: WALK-K MARKER ABSENT -- patch silently dropped, VOID RUN"; exit 1; }
echo "  boundary radius marker: present"
echo "  SFS_WALK_K_LOCAL marker: present"
echo "  walk K line(s):"
grep -n "SFS_WALK_K_LOCAL" edgeline_extraction_headless.cpp
grep -n "int K = " edgeline_extraction_headless.cpp | head -3

# ---------- build ----------
echo "=== Building EdgeLineExtractionHeadless ==="
${APPTAINER} exec --bind /data:/data "${NURBS_IMG}" /bin/bash -lc \
    "cd ${REPO_ROOT}/original_nurbs_preprocessing && rm -rf build && mkdir -p build && cd build && cmake .. && make -j8 EdgeLineExtractionHeadless" \
    2>&1 | tail -n 15
[ ${PIPESTATUS[0]} -ne 0 ] && { echo "ERROR: build failed"; exit 1; }
[ -x original_nurbs_preprocessing/build/EdgeLineExtractionHeadless ] \
    || { echo "ERROR: binary missing"; exit 1; }
ls -lh original_nurbs_preprocessing/build/EdgeLineExtractionHeadless

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
mkdir -p Temp/Data/Juglet
cp -f Dataset/Mesh/Juglet/Juglet_Piece_*_Mesh.obj Temp/Data/Juglet/ 2>/dev/null
echo "  staged objs: $(ls Temp/Data/Juglet/*.obj 2>/dev/null | wc -l) (expected 9)"

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
