#!/usr/bin/env bash
# ticket 38 phase 3: stage ONE piece on a SYNTHETIC cloud.
# usage: stage_synth_p38.sh <stage_dir> <pot> <piece_name> <axis_file> <synthetic_cloud.pcd>
# Same staging as stage_piece_p37.sh -- geometry symlinked, never copied, never written -- except
# that the cloud linked in as <piece>_Point.pcd is this ticket's synthetic cloud, whose own path
# and md5 go into inputs.md5 so no reader can mistake it for a scan.  The mesh stays the real one.
set -uo pipefail
ST=$1
POT=$2
P=$3
AXIS=$4
SYNTH=$5
if [ -z "${ST:-}" ] || [ -z "${POT:-}" ] || [ -z "${P:-}" ] || [ -z "${AXIS:-}" ] || [ -z "${SYNTH:-}" ]; then
  echo "[STAGE] FATAL empty argument"
  exit 3
fi
DSET=/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
if [ "$POT" = "Pot_A" ]; then
  MESH=$CORP/Mesh/"$P"_Mesh.obj
else
  MESH=$DSET/Mesh/"$POT"/"$P"_Mesh.obj
fi
[ -f "$SYNTH" ] || { echo "[STAGE] FATAL synthetic cloud missing $SYNTH"; exit 3; }
[ -f "$MESH" ] || { echo "[STAGE] FATAL mesh missing $MESH"; exit 3; }
[ -f "$AXIS" ] || { echo "[STAGE] FATAL axis missing $AXIS"; exit 3; }
rm -rf "$ST"
mkdir -p "$ST"/Dataset/Point/"$POT" "$ST"/Dataset/Mesh/"$POT" "$ST"/Dataset/Axes \
         "$ST"/Dataset/Breaklines/"$POT" "$ST"/Dataset/Surfaces/"$POT" \
         "$ST"/Temp/Data/"$POT" "$ST"/Temp/Temp_edge/"$POT" "$ST"/Temp/Temp/"$POT"
ln -s "$SYNTH" "$ST"/Dataset/Point/"$POT"/"$P"_Point.pcd
ln -s "$MESH" "$ST"/Dataset/Mesh/"$POT"/"$P"_Mesh.obj
cp -f "$AXIS" "$ST"/Dataset/Axes/"$P"_Axis.xyz
md5_of() { md5sum "$1" | awk '{print $1}'; }
: > "$ST"/inputs.md5
printf "SYNTHETIC\t%s\t%s\t%s\n" "$(md5_of "$SYNTH")" "$SYNTH" "$(grep -m1 '^POINTS' "$SYNTH" | awk '{print $2}')" >> "$ST"/inputs.md5
printf "REAL-MESH\t%s\t%s\t-\n" "$(md5_of "$MESH")" "$MESH" >> "$ST"/inputs.md5
printf "REAL-AXIS\t%s\t%s\t-\n" "$(md5_of "$AXIS")" "$AXIS" >> "$ST"/inputs.md5
echo "[STAGE] $P pot=$POT SYNTHETIC cloud=$SYNTH mesh=$MESH axis=$AXIS"
