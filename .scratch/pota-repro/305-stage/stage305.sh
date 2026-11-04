#!/usr/bin/env bash
# stage305.sh -- ticket 305 Stage 1 stager.  Copy of t66's stage_synth_p40.sh with ONE
# change: the mesh is resolved for every pot (the frozen copy only knows Pot_A's flat
# corpus path and the Dataset per-pot path with the plain _Mesh.obj suffix, so pots C..J,
# whose meshes are <stem>_Mesh_DS.obj, were unreachable).
# usage: stage305.sh <stage_dir> <pot> <piece_name> <axis_file> <cloud.pcd> [KIND]
set -uo pipefail
ST=${1:-}
POT=${2:-}
P=${3:-}
AXIS=${4:-}
CLOUD_IN=${5:-}
KIND=${6:-SYNTHETIC}
if [ -z "$ST" ] || [ -z "$POT" ] || [ -z "$P" ] || [ -z "$AXIS" ] || [ -z "$CLOUD_IN" ]; then
  echo "[STAGE] FATAL empty argument"
  exit 3
fi
DSET=/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
if [ -n "${MESH_DIR:-}" ] && [ -f "${MESH_DIR}/${P}_Mesh.obj" ]; then
  MESH=${MESH_DIR}/${P}_Mesh.obj
elif [ -f "$CORP/Mesh/${P}_Mesh_DS.obj" ]; then
  MESH=$CORP/Mesh/${P}_Mesh_DS.obj
elif [ -f "$CORP/Mesh/${P}_Mesh.obj" ]; then
  MESH=$CORP/Mesh/${P}_Mesh.obj
else
  MESH=$DSET/Mesh/"$POT"/${P}_Mesh.obj
fi
[ -f "$CLOUD_IN" ] || { echo "[STAGE] FATAL cloud missing $CLOUD_IN"; exit 3; }
[ -f "$MESH" ] || { echo "[STAGE] FATAL mesh missing $MESH"; exit 3; }
[ -f "$AXIS" ] || { echo "[STAGE] FATAL axis missing $AXIS"; exit 3; }
rm -rf "$ST"
mkdir -p "$ST"/Dataset/Point/"$POT" "$ST"/Dataset/Mesh/"$POT" "$ST"/Dataset/Axes \
         "$ST"/Dataset/Breaklines/"$POT" "$ST"/Dataset/Surfaces/"$POT" \
         "$ST"/Temp/Data/"$POT" "$ST"/Temp/Temp_edge/"$POT" "$ST"/Temp/Temp/"$POT"
ln -s "$CLOUD_IN" "$ST"/Dataset/Point/"$POT"/"${P}_Point.pcd"
ln -s "$MESH" "$ST"/Dataset/Mesh/"$POT"/"${P}_Mesh.obj"
cp -f "$AXIS" "$ST"/Dataset/Axes/"${P}_Axis.xyz"
md5_of() { md5sum "$1" | awk '{print $1}'; }
: > "$ST"/inputs.md5
printf "%s\t%s\t%s\t%s\n" "$KIND" "$(md5_of "$CLOUD_IN")" "$CLOUD_IN" "$(grep -m1 '^POINTS' "$CLOUD_IN" | awk '{print $2}')" >> "$ST"/inputs.md5
printf "REAL-MESH\t%s\t%s\t-\n" "$(md5_of "$MESH")" "$MESH" >> "$ST"/inputs.md5
printf "REAL-AXIS\t%s\t%s\t-\n" "$(md5_of "$AXIS")" "$AXIS" >> "$ST"/inputs.md5
echo "[STAGE] $P pot=$POT kind=$KIND cloud=$CLOUD_IN mesh=$MESH axis=$AXIS"
