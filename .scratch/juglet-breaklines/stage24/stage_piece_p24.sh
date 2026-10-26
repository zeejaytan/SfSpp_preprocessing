#!/usr/bin/env bash
# ticket 24: stage one piece. Same staging as tickets 20/22/23 so the cells are comparable.
# usage: stage_piece_p24.sh <stage_dir> <pot> <piece_name> <axis_file>
# Juglet geometry comes from the repo Dataset tree; Pot_A geometry from the frozen
# corpus -- symlinked, never copied, never written.
set -uo pipefail
ST=$1
POT=$2
P=$3
AXIS=$4
if [ -z "$ST" ] || [ -z "$POT" ] || [ -z "$P" ] || [ -z "$AXIS" ]; then
  echo "[STAGE] FATAL empty argument"
  exit 3
fi
DSET=/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
if [ "$POT" = "Pot_A" ]; then
  CLOUD=$CORP/Point/Pot_A/"$P"_Point.pcd
  MESH=$CORP/Mesh/"$P"_Mesh.obj
else
  CLOUD=$DSET/Point/"$POT"/"$P"_Point.pcd
  MESH=$DSET/Mesh/"$POT"/"$P"_Mesh.obj
fi
[ -f "$CLOUD" ] || { echo "[STAGE] FATAL cloud missing $CLOUD"; exit 3; }
[ -f "$MESH" ] || { echo "[STAGE] FATAL mesh missing $MESH"; exit 3; }
[ -f "$AXIS" ] || { echo "[STAGE] FATAL axis missing $AXIS"; exit 3; }
rm -rf "$ST"
mkdir -p "$ST"/Dataset/Point/"$POT" "$ST"/Dataset/Mesh/"$POT" "$ST"/Dataset/Axes \
         "$ST"/Dataset/Breaklines/"$POT" "$ST"/Dataset/Surfaces/"$POT" \
         "$ST"/Temp/Data/"$POT" "$ST"/Temp/Temp_edge/"$POT" "$ST"/Temp/Temp/"$POT" \
         "$ST"/Temp/_n24
ln -s "$CLOUD" "$ST"/Dataset/Point/"$POT"/"$P"_Point.pcd
ln -s "$MESH" "$ST"/Dataset/Mesh/"$POT"/"$P"_Mesh.obj
cp -f "$AXIS" "$ST"/Dataset/Axes/"$P"_Axis.xyz
md5_of() { md5sum "$1" | awk '{print $1}'; }
: > "$ST"/inputs.md5
printf "%s\t%s\t%s\n" "$(md5_of "$CLOUD")" "$CLOUD" "$(grep -m1 '^POINTS' "$CLOUD" | awk '{print $2}')" >> "$ST"/inputs.md5
printf "%s\t%s\t%s\n" "$(md5_of "$MESH")" "$MESH" "-" >> "$ST"/inputs.md5
printf "%s\t%s\t%s\n" "$(md5_of "$AXIS")" "$AXIS" "-" >> "$ST"/inputs.md5
echo "[STAGE] $P pot=$POT cloud=$CLOUD mesh=$MESH axis=$AXIS"
