#!/bin/bash
#SBATCH --job-name=vendor_check
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=vendor_check_%j.out
#SBATCH --error=vendor_check_%j.err

# Verification that the vendored source still builds the pipeline.
# The source files are MD5-identical to the pre-vendoring state, so an
# INCREMENTAL build must report nothing to do. If it recompiles or
# errors, something about the move was not clean.

set -o pipefail
REPO_ROOT="/data/gpfs/projects/punim2657/sfs_preprocessing"
SRC="${REPO_ROOT}/original_nurbs_preprocessing"
APPTAINER="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
IMG="${REPO_ROOT}/pcl_191_nurbs.sif"

echo "=== Vendored-source build verification ==="
echo "Started: $(date)  Job: ${SLURM_JOB_ID}"

echo "--- source checksums (must equal the vendored values):"
md5sum "${SRC}/edgeline_extraction_headless.cpp" "${SRC}/mesh_processing_headless.cpp"
echo "  expect aecfe83007a7de0b4c115cee577d6e71 / 3f383619ab55b395da5c0e7f8e969602"

echo "--- nested .git present? (should be GONE: it is vendored now)"
if [ -d "${SRC}/.git" ]; then
    echo "ERROR: nested .git still present -- vendoring incomplete"; exit 1
fi
echo "  absent, as expected"

echo "--- incremental rebuild (expect: nothing to be done)"
${APPTAINER} exec --bind /data:/data "${IMG}" /bin/bash -lc \
    "cd ${SRC}/build && cmake .. && make EdgeLineExtractionHeadless MeshPreprocessingHeadless -j8" \
    > /tmp/vendor_build.log 2>&1
rc=$?
echo "  build exit: ${rc}"
tail -n 8 /tmp/vendor_build.log
if [ ${rc} -ne 0 ]; then
    echo "ERROR: build FAILED after vendoring"
    grep -E "error:" /tmp/vendor_build.log | head -n 10
    exit 1
fi

if grep -q "Built target EdgeLineExtractionHeadless" /tmp/vendor_build.log; then
    echo "RESULT: build OK from vendored source"
else
    echo "RESULT: inconclusive (no 'Built target' line)"
fi
ls -lh "${SRC}/build/EdgeLineExtractionHeadless" "${SRC}/build/MeshPreprocessingHeadless" 2>/dev/null
echo "Finished: $(date)"
