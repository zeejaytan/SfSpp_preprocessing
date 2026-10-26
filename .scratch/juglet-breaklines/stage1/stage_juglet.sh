#!/usr/bin/env bash
# Stage one Juglet piece the way scripts/stage_piece.sh stages a corpus piece,
# for the parts the frozen corpus cannot supply: the corpus has no Juglet cloud
# and no manifest row, so this links the Dataset/ tree that is on Spartan.
#
#   Dataset/Point/Juglet/<piece>_Point.pcd   (symlink, the cloud the stage reads)
#   Dataset/Mesh/Juglet/<piece>_Mesh.obj     (symlink, baseName = pcd stem - "_Point")
#   Dataset/Axes/<piece>_Axis.xyz            (copy of the axis handed in)
#   Temp/{Data,Temp_edge,Temp}/Juglet        (the stage's own scratch)
#
# usage: stage_juglet.sh <stage_dir> <N> <axis file>
set -uo pipefail
ST=${1:?stage dir}; N=${2:?piece number}; AXIS=${3:?axis file}
POT=Juglet
P=Juglet_Piece_${N}
DSET=/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset
CLOUD=$DSET/Point/Juglet/${P}_Point.pcd
MESH=$DSET/Mesh/Juglet/${P}_Mesh.obj
[ -f "$CLOUD" ] || { echo "[STAGE] FATAL cloud missing $CLOUD"; exit 3; }
[ -f "$MESH" ]  || { echo "[STAGE] FATAL mesh missing $MESH"; exit 3; }
[ -f "$AXIS" ]  || { echo "[STAGE] FATAL axis missing $AXIS"; exit 3; }
rm -rf "$ST"
mkdir -p "$ST/Dataset/Point/$POT" "$ST/Dataset/Mesh/$POT" "$ST/Dataset/Axes" \
         "$ST/Dataset/Breaklines/$POT" "$ST/Dataset/Surfaces/$POT" \
         "$ST/Temp/Data/$POT" "$ST/Temp/Temp_edge/$POT" "$ST/Temp/Temp/$POT"
ln -s "$CLOUD" "$ST/Dataset/Point/$POT/${P}_Point.pcd"
ln -s "$MESH"  "$ST/Dataset/Mesh/$POT/${P}_Mesh.obj"
cp -f "$AXIS" "$ST/Dataset/Axes/${P}_Axis.xyz"
md5_of() { md5sum "$1" | awk '{print $1}'; }
: > "$ST/inputs.md5"
printf "%s\t%s\t%s\t%s\n" "$(md5_of "$CLOUD")" "$CLOUD" "$(grep -m1 '^POINTS' "$CLOUD" | awk '{print $2}')" "$ST/Dataset/Point/$POT/${P}_Point.pcd" >> "$ST/inputs.md5"
printf "%s\t%s\t%s\t%s\n" "$(md5_of "$MESH")" "$MESH" "-" "$ST/Dataset/Mesh/$POT/${P}_Mesh.obj" >> "$ST/inputs.md5"
printf "%s\t%s\t%s\t%s\n" "$(md5_of "$ST/Dataset/Axes/${P}_Axis.xyz")" "$AXIS" "-" "$ST/Dataset/Axes/${P}_Axis.xyz" >> "$ST/inputs.md5"
echo "[STAGE] $P staged from $CLOUD + $MESH, axis $AXIS"
