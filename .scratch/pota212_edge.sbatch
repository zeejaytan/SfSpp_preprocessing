#!/bin/bash
# POTA-212 pristine split-walk re-extract: edge stage ONLY on pota212_pipe (copy of 208 pipe tree).
# Mesh outputs reused as-is; only the edgeline binary differs (ported 154 cure).
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --time=06:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --job-name=pota212_edge
#SBATCH --output=pota212_edge_%j.out
#SBATCH --error=pota212_edge_%j.err
set -uo pipefail
WROOT=/data/gpfs/projects/punim2657/sfs-splitwalk-212
BUILD="$WROOT/build-212"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif
POT=Pot_A
TREE=/data/gpfs/projects/punim2657/pota212_pipe
echo "=== POTA-212 EDGE RE-EXTRACT ==="; date; hostname
echo "### guard: ported source differs from e2e-pristine by hunks only"
diff /data/gpfs/projects/punim2657/sfs-e2e-pristine/edgeline_extraction_headless.cpp "$WROOT/edgeline_extraction_headless.cpp" | grep -c '^[<>]'
grep -q "SPLIT-WALK" "$WROOT/edgeline_extraction_headless.cpp" || { echo NO-SPLITWALK-MARKER; exit 1; }
grep -q "FACE VETO" "$WROOT/edgeline_extraction_headless.cpp" || { echo NO-FACEVETO-MARKER; exit 1; }
grep -q "boundary reload size" "$WROOT/edgeline_extraction_headless.cpp" && { echo RELOAD-STILL-PRESENT; exit 1; } || echo "reload-over absent OK"
[ -x "$BUILD/EdgeLineExtractionHeadless" ] || { echo EDGE-BINARY-MISSING; exit 1; }
ls -la "$BUILD/EdgeLineExtractionHeadless"
md5sum "$BUILD/EdgeLineExtractionHeadless" | tee "$WROOT/edge_binary_md5.txt"
echo "### edge run (split-walk binary; mesh inputs reused from 208 tree copy)"
mkdir -p "$TREE/Dataset/Breaklines/$POT"
( cd "$TREE" && "$APPTAINER" exec --bind /data:/data "$SIF" env POT_NAME="$POT" "$BUILD/EdgeLineExtractionHeadless" ) > "$TREE/edgeline_stage_212.log" 2>&1
echo "edge exit $? (not trusted)"
echo "### P01-focused log watches"
grep -a "FACE VETO" "$TREE/edgeline_stage_212.log" | head -n 20
grep -a "SPLIT-WALK" "$TREE/edgeline_stage_212.log" | head -n 40
echo "### header census (Bl0 + Bl1)"
for i in 01 02 03 04 05 06 07 08; do for b in 0 1; do f="$TREE/Dataset/Breaklines/$POT/Pot_A_Piece_${i}_Breakline_${b}.pcd"; [ -f "$f" ] && echo "p${i} Bl${b} pts=$(grep -a '^POINTS' "$f" | awk '{print $2}')" || echo "p${i} Bl${b} MISSING"; done; done
echo "=== POTA-212 EDGE DONE ==="; date
