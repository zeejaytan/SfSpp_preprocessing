#!/usr/bin/env bash
# ticket 27: run our own edgeline stage on the surfaces one mesh cell kept, and count its dots.
# The mesh stage does not write Breakline files; edgeline_extraction_headless.cpp does, reading
# <piece>_Surface_{0,1}.xyz from Temp/Data/<pot>/, a <piece>_Mesh.obj found under Temp/, the axis
# from Dataset/Axes/, an empty Segments/, and (optionally) <piece>_SampledWithNormals.ply.
# usage: run_edge27.sh <tag>
# env: CELLROOT POT PIECE EDGEBIN SIF APT MESH AXIS COMMIT
set -uo pipefail
TAG=$1
: "${CELLROOT:?}" "${POT:?}" "${PIECE:?}" "${EDGEBIN:?}" "${SIF:?}" "${APT:?}" "${MESH:?}" "${AXIS:?}" "${COMMIT:?}"
CELL=$CELLROOT/$TAG/$POT/$PIECE
ES=$CELL/edgestage
DOT=$CELL/breakdots.tsv
mkdir -p "$CELL/logs" "$CELL/breaklines"
: > "$DOT"
if [ ! -f "$CELL/surfaces/${PIECE}_Surface_0.xyz" ] && [ ! -f "$CELL/surfaces/${PIECE}_Surface_1.xyz" ]; then
  printf "%s\\t%s\\t%s\\t-\\t(no-surface)\\t0\\t0\\t0\\t0\\n" "$TAG" "$POT" "$PIECE" >> "$DOT"
  echo "[EDGE] tag=$TAG pot=$POT piece=$PIECE skipped=no-surface"
  exit 0
fi
rm -rf "$ES"
mkdir -p "$ES/Dataset/Axes" "$ES/Dataset/Mesh/$POT" "$ES/Dataset/Surfaces/$POT" \
         "$ES/Dataset/Breaklines/$POT" "$ES/Temp/Data/$POT" "$ES/Temp/Temp_edge/$POT" \
         "$ES/Temp/Temp/$POT" "$ES/Segments"
for k in 0 1; do
  [ -f "$CELL/surfaces/${PIECE}_Surface_$k.xyz" ] && cp -f "$CELL/surfaces/${PIECE}_Surface_$k.xyz" "$ES/Temp/Data/$POT/"
done
[ -f "$CELL/surfaces/${PIECE}_SampledWithNormals.ply" ] && cp -f "$CELL/surfaces/${PIECE}_SampledWithNormals.ply" "$ES/Temp/Data/$POT/"
ln -s "$MESH" "$ES/Temp/Data/$POT/${PIECE}_Mesh.obj"
cp -f "$AXIS" "$ES/Dataset/Axes/${PIECE}_Axis.xyz"
ELOG=$CELL/logs/edge.log
: > "$ELOG"
T0=$(date +%s)
( cd "$ES" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" "$EDGEBIN" ) >> "$ELOG" 2>&1
EX=$?
T1=$(date +%s); EL=$((T1-T0))
for f in "$ES/Dataset/Breaklines/$POT"/*; do
  [ -f "$f" ] || continue
  cp -f "$f" "$CELL/breaklines/"
done
for f in "$CELL/breaklines"/*_Breakline_*.pcd; do
  [ -f "$f" ] || continue
  b=$(basename "$f")
  sk=$(echo "$b" | sed -e 's/.*_Breakline_\([01]\)\.pcd$/\1/')
  pts=$(grep -m1 '^POINTS' "$f" | awk '{print $2}')
  segs=$(grep -m1 '^#' "$f" | awk '{print $2}')
  hpts=$(grep -m1 '^#' "$f" | awk '{print $3}')
  xf="${f%.pcd}.xyz"
  if [ -f "$xf" ]; then xl=$(wc -l < "$xf"); else xl=0; fi
  printf "%s\\t%s\\t%s\\t%s\\t%s\\t%s\\t%s\\t%s\\t%s\\n" \
    "$TAG" "$POT" "$PIECE" "$sk" "$b" "${pts:-0}" "${segs:-0}" "${hpts:-0}" "$xl" >> "$DOT"
done
if ! ls "$CELL/breaklines"/*_Breakline_*.pcd >/dev/null 2>&1; then
  printf "%s\\t%s\\t%s\\t-\\t(none-written)\\t0\\t0\\t0\\t0\\n" "$TAG" "$POT" "$PIECE" >> "$DOT"
fi
if [ -d "$ES" ]; then
  find "$ES" -type f -printf "%f\\t%s\\n" 2>/dev/null | awk -F'\t' -v k="$TAG/$POT/$PIECE/edgestage" '{
      n=split($1,a,"."); ext=(n>1)?a[n]:"(noext)";
      cnt[ext]++; byt[ext]+=$2 }
    END { for (e in cnt) printf "%s\t%s\t%d\t%d\n", k, e, cnt[e], byt[e] }' >> "$CELLROOT/geometry_counts.tsv"
  rm -rf "$ES"
fi
NBD=$(wc -l < "$DOT")
printf "%s\\t%s\\t%s\\t%s\\t%d\\t%d\\n" "$TAG" "$POT" "$PIECE" "$COMMIT" "$EX" "$EL" >> "$CELLROOT/cells27_edge.tsv"
echo "[EDGE] tag=$TAG pot=$POT piece=$PIECE edge_exit=$EX elapsed=${EL}s rows=$NBD dir=$CELL/breaklines"
