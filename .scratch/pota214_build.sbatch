#!/bin/bash
# POTA-214 build: cured 213 source (pristine-splitwalk worktree file) built INSIDE the PCL container.
#SBATCH --job-name=potD214-build
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --output=build-214_%j.out
#SBATCH --error=build-214_%j.err
set -euo pipefail
WROOT=/data/gpfs/projects/punim2657/sfs-potD-214
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif
echo "### guard: cure markers present, reload-over absent"
grep -q "SPLIT-WALK" "$WROOT/edgeline_extraction_headless.cpp" || { echo NO-SPLITWALK-MARKER; exit 1; }
grep -q "LOOP-SELECT" "$WROOT/edgeline_extraction_headless.cpp" || { echo NO-LOOPSELECT-MARKER; exit 1; }
grep -q "FACE_ALIGN_VETO = 2.0f" "$WROOT/edgeline_extraction_headless.cpp" || { echo NO-KEEPALL-VETO; exit 1; }
md5sum "$WROOT/edgeline_extraction_headless.cpp"
rm -rf "$WROOT/build-214"
"$APPTAINER" exec --bind /data:/data "$SIF" bash -c 'cd "$1" && cmake -S . -B build-214 -DCMAKE_BUILD_TYPE=Release && cmake --build build-214 --target MeshPreprocessingHeadless EdgeLineExtractionHeadless -j8' _ "$WROOT" 2>&1 | tail -n 30
echo "=== BUILD DONE ==="
ls -la "$WROOT/build-214/MeshPreprocessingHeadless" "$WROOT/build-214/EdgeLineExtractionHeadless"
md5sum "$WROOT/build-214/EdgeLineExtractionHeadless" "$WROOT/build-214/MeshPreprocessingHeadless" | tee "$WROOT/bin214_md5.txt"
