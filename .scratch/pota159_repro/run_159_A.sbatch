#!/bin/bash
# POTA-159 Pot A: EDGE-ONLY, same staged binary, CTL then ADAPT. Own tree pota159_A.
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --time=06:00:00
#SBATCH --nodes=1 --cpus-per-task=8 --mem=32G
#SBATCH --job-name=p159_A
set -uo pipefail
P159=/data/gpfs/projects/punim2657/pota159_repro
TREE=$P159/pota159_A
EDGEBIN=$P159/EdgeLineExtractionHeadless_ADAPT
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif
echo "=== POTA-159 PotA job ${SLURM_JOB_ID} ==="; date; hostname
for m in "FACE VETO" "ADAPT VETO" "POTA159_ADAPT"; do grep -aq "$m" "$EDGEBIN" || { echo EDGE-NO-MARKER-$m; exit 1; }; done
echo "adapt edge binary markers OK"
for PASS in CTL ADAPT; do
  echo "### edge run (POT_NAME=Pot_A, $PASS)"
  if [ $PASS = CTL ]; then unset POTA159_ADAPT; else export POTA159_ADAPT=1; fi
  if [ $PASS = CTL ]; then ( cd "$TREE" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="Pot_A" "$EDGEBIN" ) > "$TREE/edgeline_stage_$PASS.log" 2>&1; else ( cd "$TREE" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="Pot_A" POTA159_ADAPT=1 "$EDGEBIN" ) > "$TREE/edgeline_stage_$PASS.log" 2>&1; fi
  echo "edge exit $? (not trusted)"
  grep -a "FACE VETO" "$TREE/edgeline_stage_$PASS.log"
  grep -a "ADAPT VETO" "$TREE/edgeline_stage_$PASS.log"
  grep -a "SPLIT-WALK" "$TREE/edgeline_stage_$PASS.log"
  D=$P159/PA_$PASS; rm -rf "$D"; mkdir -p "$D"
  cp "$TREE"/Dataset/Breaklines/Pot_A/*.pcd "$D"/
  cp "$TREE"/Temp/Temp_edge/Pot_A/veto_align_*.csv "$D"/ 2>/dev/null || echo "(no CSVs for $PASS)"
  for f in "$D"/*.pcd; do pt=$(grep -a '^POINTS' "$f" | awk '{print $2}'); echo "$PASS $(basename $f) points=$pt"; done
done
date; echo P159-A-DONE
