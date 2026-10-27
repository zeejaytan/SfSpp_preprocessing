#!/usr/bin/env bash
# ticket 27: one (arm, piece) mesh cell.
# usage: run_cell27.sh <tag>          (tag = OLD | A | A2 | P | B)
# env: CELLROOT POT PIECE AXIS BIN SIF APT STAGER COMMIT [ENVS] [DUMPROOT]
# Keeps: logs (slurm-side logs of this cell), surfaces/*.ply + *.xyz, one tab row of cells27.tsv.
# Deletes: the staged tree, with a counted record per extension.
set -uo pipefail
TAG=$1
: "${CELLROOT:?}" "${POT:?}" "${PIECE:?}" "${AXIS:?}" "${BIN:?}" "${SIF:?}" "${APT:?}" "${STAGER:?}" "${COMMIT:?}"
ENVS=${ENVS:-}
CELL=$CELLROOT/$TAG/$POT/$PIECE
ST=$CELL/stage
mkdir -p "$CELL/logs" "$CELL/surfaces"
STATUS_RAW=$CELL/logs/status_raw.tsv
: > "$STATUS_RAW"
T0=$(date +%s)
bash "$STAGER" "$ST" "$POT" "$PIECE" "$AXIS" > "$CELL/logs/stage.log" 2>&1
SS=$?
LOG=$CELL/logs/mesh.log
: > "$LOG"
MS=99
if [ "$SS" -eq 0 ]; then
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" \
      SFS_AXIS_FILE="$ST/Dataset/Axes/${PIECE}_Axis.xyz" \
      SFS_STATUS_FILE="$STATUS_RAW" $ENVS "$BIN" ) >> "$LOG" 2>&1
  MS=$?
else
  echo "[CELL] stage failed for $POT/$PIECE tag=$TAG stage_exit=$SS" >> "$LOG"
fi
T1=$(date +%s); EL=$((T1-T0))
grep -E "\\[DEDUPE-27\\]|\\[RETRY-23\\]|\\[SINGLE-23\\]|\\[STATUS-23\\]|\\[SPACING-22\\]|\\[COUNT-22\\]|\\[REASSIGN-22\\]|\\[PAPER-234\\]|\\[DUMP-25\\]|\\[WINDOW-26\\]|\\[STAGE\\]" "$LOG" > "$CELL/logs/lines27.log" 2>/dev/null
S0=no; S1=no; N0=0; N1=0; DEDN=0
for k in 0 1; do
  src=$ST/Temp/Data/$POT/${PIECE}_Surface_$k.ply
  if [ -f "$src" ]; then
    cp -f "$src" "$CELL/surfaces/${PIECE}_Surface_$k.ply"
    srcx=$ST/Temp/Data/$POT/${PIECE}_Surface_$k.xyz
    [ -f "$srcx" ] && cp -f "$srcx" "$CELL/surfaces/${PIECE}_Surface_$k.xyz"
    n=$(grep -m1 '^element vertex' "$src" | awk '{print $3}')
    eval "S$k=yes"; eval "N$k=${n:-0}"
  fi
done
# Every <piece>_* file the mesh stage left in Temp/Data/<pot>/ is kept, because the edgeline pass
# reads more than the surfaces: <piece>_SampledWithNormals.ply and <piece>_unclustered.ply (written
# at mesh_processing_headless.cpp:4007). Job 33860966 kept only the former, so
# edgeline_extraction_headless.cpp:1273 loaded nothing and the KD-tree at :1275 killed all 32 cells.
: > "$CELL/logs/kept_inputs.txt"
for f in "$ST/Temp/Data/$POT/${PIECE}"_*; do
  [ -f "$f" ] || continue
  cp -f "$f" "$CELL/surfaces/"
  printf "%s\t%s\n" "$(basename "$f")" "$(wc -c < "$f")" >> "$CELL/logs/kept_inputs.txt"
done
DEDN=$(grep -c '\[DEDUPE-27\]' "$LOG" 2>/dev/null || echo 0)
STATUSLINE=$(grep -m1 '\[STATUS-23\]' "$LOG" 2>/dev/null | tr '\t' ' ')
# counted deletion of the staged tree (geometry dies here; the record survives)
if [ -d "$ST" ]; then
  find "$ST" -type f -printf "%f\\t%s\\n" 2>/dev/null | awk -F'\t' -v k="$TAG/$POT/$PIECE/stage" '{
      n=split($1,a,"."); ext=(n>1)?a[n]:"(noext)";
      cnt[ext]++; byt[ext]+=$2 }
    END { for (e in cnt) printf "%s\t%s\t%d\t%d\n", k, e, cnt[e], byt[e] }' >> "$CELLROOT/geometry_counts.tsv"
  rm -rf "$ST"
fi
printf "%s\\t%s\\t%s\\t%s\\t%d\\t%d\\t%s\\t%s\\t%s\\t%s\\t%d\\t%s\\n" \
  "$TAG" "$POT" "$PIECE" "$COMMIT" "$SS" "$MS" "$EL" "$S0" "$S1" "$N0" "$N1" "$DEDN" >> "$CELLROOT/cells27.tsv"
echo "[CELL] tag=$TAG pot=$POT piece=$PIECE stage=$SS mesh=$MS elapsed=${EL}s surf0=$S0($N0) surf1=$S1($N1) dedupe_lines=$DEDN $STATUSLINE"
