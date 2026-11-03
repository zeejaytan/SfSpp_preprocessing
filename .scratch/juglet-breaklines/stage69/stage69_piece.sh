#!/usr/bin/env bash
# stage69_piece.sh -- ticket 69: stage ONE piece on the released cloud.
# stage_synth_p40.sh with the mesh directory overridable, because the canonical
# Dataset/Mesh/ tree carries only Juglet, Pot_A, Pot_C and Pot_TEST -- the released
# Pot D and Pot J meshes exist only in the frozen corpus (Mesh/ is FLAT there).
# usage: stage69_piece.sh <stage_dir> <pot> <piece> <axis_file> <cloud.pcd> [KIND]
set -uo pipefail
ST=${1:-}
POT=${2:-}
P=${3:-}
AXIS=${4:-}
CLOUD_IN=${5:-}
KIND=${6:-SYNTHETIC}
if [ -z "$ST" ] || [ -z "$POT" ] || [ -z "$P" ] || [ -z "$AXIS" ] || [ -z "$CLOUD_IN" ]; then
  echo "[STAGE69] FATAL empty argument"
  exit 3
fi
DSET=/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
pick_mesh() { # $1 = directory; prefer <P>_Mesh.obj, fall back to <P>_Mesh_DS.obj
  if [ -f "$1/$P"_Mesh.obj ]; then echo "$1/$P"_Mesh.obj
  elif [ -f "$1/$P"_Mesh_DS.obj ]; then echo "$1/$P"_Mesh_DS.obj
  else echo "$1/$P"_Mesh.obj; fi
}
if [ -n "${MESH_DIR_69:-}" ]; then
  MESH=$(pick_mesh "$MESH_DIR_69")
elif [ "$POT" = "Pot_A" ]; then
  MESH=$(pick_mesh "$CORP/Mesh")
else
  MESH=$(pick_mesh "$DSET/Mesh/$POT")
fi
[ -f "$CLOUD_IN" ] || { echo "[STAGE69] FATAL cloud missing $CLOUD_IN"; exit 3; }
[ -f "$MESH" ] || { echo "[STAGE69] FATAL mesh missing $MESH"; exit 3; }
[ -f "$AXIS" ] || { echo "[STAGE69] FATAL axis missing $AXIS"; exit 3; }
rm -rf "$ST"
mkdir -p "$ST"/Dataset/Point/"$POT" "$ST"/Dataset/Mesh/"$POT" "$ST"/Dataset/Axes \
         "$ST"/Dataset/Breaklines/"$POT" "$ST"/Dataset/Surfaces/"$POT" \
         "$ST"/Temp/Data/"$POT" "$ST"/Temp/Temp_edge/"$POT" "$ST"/Temp/Temp/"$POT"
ln -s "$CLOUD_IN" "$ST"/Dataset/Point/"$POT"/"$P"_Point.pcd
ln -s "$MESH" "$ST"/Dataset/Mesh/"$POT"/"$P"_Mesh.obj
cp -f "$AXIS" "$ST"/Dataset/Axes/"$P"_Axis.xyz
md5_of() { md5sum "$1" | awk '{print $1}'; }
: > "$ST"/inputs.md5
printf "%s\t%s\t%s\t%s\n" "$KIND" "$(md5_of "$CLOUD_IN")" "$CLOUD_IN" "$(grep -m1 '^POINTS' "$CLOUD_IN" | awk '{print $2}')" >> "$ST"/inputs.md5
printf "REAL-MESH\t%s\t%s\t-\n" "$(md5_of "$MESH")" "$MESH" >> "$ST"/inputs.md5
printf "REAL-AXIS\t%s\t%s\t-\n" "$(md5_of "$AXIS")" "$AXIS" >> "$ST"/inputs.md5
echo "[STAGE69] $P pot=$POT kind=$KIND cloud=$CLOUD_IN mesh=$MESH axis=$AXIS"
