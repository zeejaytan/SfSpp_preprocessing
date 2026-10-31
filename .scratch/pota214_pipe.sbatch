#!/bin/bash
# POTA-214 Pot D full pipe (mesh + edge, 208 pattern) with the 213-cured binary.
# Inputs: sampled Point PCDs (pota214_sample job) + ORIG Mesh_DS renamed + ORIG Axes 01-29.
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --job-name=pota214_pipe
#SBATCH --output=pota214_pipe_%j.out
#SBATCH --error=pota214_pipe_%j.err
set -uo pipefail
WROOT=/data/gpfs/projects/punim2657/sfs-potD-214
BUILD="$WROOT/build-214"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif
POT=Pot_D
ORIG=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
TREE=/data/gpfs/projects/punim2657/pota214_pipe
SAMPLED=$WROOT/Dataset_Input/Point/Pot_D
echo "=== POTA-214 POT D PIPE ==="; date; hostname
echo "### guard: cured edge source + pristine mesh source"
grep -q "FACE_ALIGN_VETO = 2.0f" "$WROOT/edgeline_extraction_headless.cpp" || { echo NO-KEEPALL-VETO; exit 1; }
grep -q "LOOP-SELECT" "$WROOT/edgeline_extraction_headless.cpp" || { echo NO-LOOPSELECT; exit 1; }
diff -q /data/gpfs/projects/punim2657/sfs-e2e-pristine/mesh_processing_headless.cpp "$WROOT/mesh_processing_headless.cpp" || { echo MESH-SOURCE-DIRTY; exit 1; }
echo "sources OK"
[ -x "$BUILD/MeshPreprocessingHeadless" ] || { echo MESH-BINARY-MISSING; exit 1; }
[ -x "$BUILD/EdgeLineExtractionHeadless" ] || { echo EDGE-BINARY-MISSING; exit 1; }
md5sum "$BUILD/MeshPreprocessingHeadless" "$BUILD/EdgeLineExtractionHeadless" | tee "$WROOT/bin214_md5.txt"
echo "### guard: 29 sampled PCDs present"
for i in $(seq -w 1 29); do [ -f "$SAMPLED/Pot_D_Piece_${i}_Point.pcd" ] || { echo "MISSING-PCD $i"; exit 1; }; done
echo "29/29 PCDs present"
echo "### stage fresh tree"
rm -rf "$TREE"
mkdir -p "$TREE/Temp/Data/$POT" "$TREE/Dataset/Mesh/$POT" "$TREE/Dataset/Point/$POT" "$TREE/Dataset/Surfaces/$POT" "$TREE/Dataset/Breaklines/$POT" "$TREE/Dataset/Axes"
cp -L "$SAMPLED"/*.pcd "$TREE/Dataset/Point/$POT/"
for i in $(seq -w 1 29); do cp -L "$ORIG/Mesh/Pot_D_Piece_${i}_Mesh_DS.obj" "$TREE/Dataset/Mesh/$POT/Pot_D_Piece_${i}_Mesh.obj"; cp -L "$ORIG/Axes/Pot_D_Piece_${i}_Axis.xyz" "$TREE/Dataset/Axes/"; done
md5sum "$TREE/Dataset/Mesh/$POT"/*.obj | sed 's|.*/||' | sort > "$WROOT/pota214_mesh_rename_md5.txt"
echo "staged: $(ls "$TREE/Dataset/Point/$POT" | wc -l) pcd, $(ls "$TREE/Dataset/Mesh/$POT" | wc -l) obj, $(ls "$TREE/Dataset/Axes" | wc -l) axes"
echo "### mesh run (cured line, pristine mesh binary)"
( cd "$TREE" && "$APPTAINER" exec --bind /data:/data "$SIF" env POT_NAME="$POT" "$BUILD/MeshPreprocessingHeadless" ) > "$TREE/mesh_stage.log" 2>&1
echo "mesh exit $? (not trusted)"
for i in $(seq -w 1 29); do for s in 0 1; do f="$TREE/Temp/Data/$POT/Pot_D_Piece_${i}_Surface_${s}.xyz"; [ -f "$f" ] && echo "  p${i} S${s}: $(wc -l < "$f") pts" || echo "  p${i} S${s}: MISSING"; done; done
echo "### edge run (213-cured binary)"
( cd "$TREE" && "$APPTAINER" exec --bind /data:/data "$SIF" env POT_NAME="$POT" "$BUILD/EdgeLineExtractionHeadless" ) > "$TREE/edgeline_stage.log" 2>&1
echo "edge exit $? (not trusted)"
echo "### LOOP-SELECT watches"
grep -a "LOOP-SELECT" "$TREE/edgeline_stage.log" | head -n 70
grep -a "FACE VETO" "$TREE/edgeline_stage.log" | head -n 35
echo "### header census (Bl0 + Bl1, 29 pieces)"
for i in $(seq -w 1 29); do for b in 0 1; do f="$TREE/Dataset/Breaklines/$POT/Pot_D_Piece_${i}_Breakline_${b}.pcd"; [ -f "$f" ] && echo "p$i Bl$b pts=$(grep -a '^POINTS' "$f" | awk '{print $2}')" || echo "p$i Bl$b MISSING"; done; done
echo "### stepring sidecars"
ls "$TREE/Dataset/Breaklines/$POT" | grep -c stepring || true
for i in $(seq -w 1 29); do for b in 0 1; do for f in "$TREE/Dataset/Breaklines/$POT"/Pot_D_Piece_${i}_Breakline_${b}_stepring.pcd; do [ -f "$f" ] && echo "p$i Bl${b}-ring pts=$(grep -a '^POINTS' "$f" | awk '{print $2}')"; done; done; done
echo "=== POTA-214 pipe DONE ==="; date
