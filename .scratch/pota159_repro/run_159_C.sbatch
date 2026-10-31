#!/bin/bash
# POTA-159 C01: same staged binary, CTL (fixed 0.5) then ADAPT. Full chain like 156/158.
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --time=06:00:00
#SBATCH --nodes=1 --cpus-per-task=8 --mem=32G
#SBATCH --job-name=p159_C
set -uo pipefail
P159=/data/gpfs/projects/punim2657/pota159_repro
TREE=$P159/pota159_C
SUB=/data/gpfs/projects/punim2657/sfs_cure_1c6a8f9/original_nurbs_preprocessing
MESHBIN=$SUB/build/MeshPreprocessingHeadless
EDGEBIN=$P159/EdgeLineExtractionHeadless_ADAPT
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif
echo "=== POTA-159 C01 job ${SLURM_JOB_ID} ==="; date; hostname
for m in "FACE VETO" "ADAPT VETO" "POTA159_ADAPT"; do grep -aq "$m" "$EDGEBIN" || { echo EDGE-NO-MARKER-$m; exit 1; }; done
echo "adapt edge binary markers OK"
md5sum "$TREE"/Temp/Data/Pot_C/Pot_C_Piece_01_Mesh.obj "$TREE"/Temp/Data/Pot_C/Pot_C_Piece_01_Point.pcd
for PASS in CTL ADAPT; do
  echo "### mesh+edge run (POT_NAME=Pot_C, $PASS)"
  if [ $PASS = CTL ]; then unset POTA159_ADAPT; else export POTA159_ADAPT=1; fi
  ( cd "$TREE" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="Pot_C" "$MESHBIN" ) > "$TREE/mesh_stage_$PASS.log" 2>&1
  echo "mesh exit $? (not trusted)"
  if [ $PASS = CTL ]; then ( cd "$TREE" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="Pot_C" "$EDGEBIN" ) > "$TREE/edgeline_stage_$PASS.log" 2>&1; else ( cd "$TREE" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="Pot_C" POTA159_ADAPT=1 "$EDGEBIN" ) > "$TREE/edgeline_stage_$PASS.log" 2>&1; fi
  echo "edge exit $? (not trusted)"
  grep -a "FACE VETO" "$TREE/edgeline_stage_$PASS.log" | head -5
  grep -a "ADAPT VETO" "$TREE/edgeline_stage_$PASS.log" | head -5
  grep -a "SPLIT-WALK" "$TREE/edgeline_stage_$PASS.log" | head -5
  D=$P159/C01_$PASS; rm -rf "$D"; mkdir -p "$D"
  cp "$TREE"/Dataset/Breaklines/Pot_C/*.pcd "$D"/
  cp "$TREE"/Temp/Temp_edge/Pot_C/veto_align_*.csv "$D"/ 2>/dev/null || echo "(no CSVs for $PASS)"
  for f in "$D"/*.pcd; do pt=$(grep -a '^POINTS' "$f" | awk '{print $2}'); echo "$PASS $(basename $f) points=$pt"; done
done
date; echo P159-C-DONE
