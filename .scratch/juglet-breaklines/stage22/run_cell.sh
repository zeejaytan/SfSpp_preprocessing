#!/usr/bin/env bash
# ticket 22: one (arm, piece) cell of the arm grid.
# Reads from the environment: CELLROOT POT PIECE TAG ENVS AXIS BIN SIF APT STAGER COMMIT.
# Keeps the surface bundle (S0/S1 .ply and .xyz) and the log, deletes the rest of the stage
# with a counted record, and appends one row to $CELLROOT/cells.tsv.
set -uo pipefail
TAG=$1
: "${CELLROOT:?}" "${POT:?}" "${PIECE:?}" "${AXIS:?}" "${BIN:?}" "${SIF:?}" "${APT:?}" "${STAGER:?}" "${COMMIT:?}"
ENVS=${ENVS:-}
CELL=$CELLROOT/$TAG/$POT/$PIECE
ST=$CELL/stage
mkdir -p "$CELL/logs" "$CELL/surfaces"
T0=$(date +%s)
bash "$STAGER" "$ST" "$POT" "$PIECE" "$AXIS" > "$CELL/logs/stage.log" 2>&1
SS=$?
LOG=$CELL/logs/mesh.log
: > "$LOG"
MS=99
if [ "$SS" -eq 0 ]; then
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" SFS_AXIS_FILE="$ST/Dataset/Axes/${PIECE}_Axis.xyz" $ENVS "$BIN" ) >> "$LOG" 2>&1
  MS=$?
fi
T1=$(date +%s); EL=$((T1 - T0))

CL_PRE=$(grep -m1 'Number of clusters is equal to' "$LOG" | awk '{print $NF}')
[ -z "${CL_PRE:-}" ] && CL_PRE=NA
CL_POST=$(grep -m1 'pass [0-9]* done:' "$LOG" | awk '{print $(NF-1)}')
[ -z "${CL_POST:-}" ] && CL_POST=NA
SIZES=$(awk '/^Cluster [0-9]+ :/ { if (!s[$2]++) { o = (o == "" ? $NF : o "," $NF) } } END { print o }' "$LOG")
[ -z "${SIZES:-}" ] && SIZES=none
GROW=$(grep -m1 'paper grow:' "$LOG" | sed 's/^.*\[PAPER-234\] //')
[ -z "${GROW:-}" ] && GROW=none
MERGE=$(grep -m1 'pass [0-9]* done:' "$LOG" | sed 's/^.*\[PAPER-234\] //')
[ -z "${MERGE:-}" ] && MERGE=none
CLS=$(grep -m1 'classify: face0' "$LOG" | sed 's/^.*\[PAPER-234\] //')
[ -z "${CLS:-}" ] && CLS=none
FACE=$(grep -m1 -o 'swapped -> Surface_0=interior\|kept -> Surface_0=interior' "$LOG")
[ -z "${FACE:-}" ] && FACE=none
SPACING=$(grep -m1 '\[SPACING-22\]' "$LOG" | sed 's/^.*\[SPACING-22\] //')
[ -z "${SPACING:-}" ] && SPACING=none
COUNT=$(grep -m1 '\[COUNT-22\] policy=' "$LOG" | sed 's/^.*\[COUNT-22\] //')
[ -z "${COUNT:-}" ] && COUNT=none
COUNTM=$(grep -m1 '\[COUNT-22\] merge' "$LOG" | sed 's/^.*\[COUNT-22\] //')
[ -z "${COUNTM:-}" ] && COUNTM=none
REASSIGN=$(grep -m1 '\[REASSIGN-22\]' "$LOG" | sed 's/^.*\[REASSIGN-22\] //')
[ -z "${REASSIGN:-}" ] && REASSIGN=none

declare -a HAS MD5 BTS
S0=no; S1=no; M0=NA; M1=NA; B0=0; B1=0
for k in 0 1; do
  src=$ST/Temp/Data/$POT/${PIECE}_Surface_$k.ply
  HAS[$k]=no
  if [ -f "$src" ]; then
    cp -f "$src" "$CELL/surfaces/${PIECE}_Surface_$k.ply"
    [ -f "$ST/Temp/Data/$POT/${PIECE}_Surface_$k.xyz" ] && cp -f "$ST/Temp/Data/$POT/${PIECE}_Surface_$k.xyz" "$CELL/surfaces/"
    HAS[$k]=yes
  fi
done
[ "${HAS[0]}" = yes ] && S0=yes && M0=$(md5sum "$CELL/surfaces/${PIECE}_Surface_0.ply" | awk '{print $1}') && B0=$(stat -c %s "$CELL/surfaces/${PIECE}_Surface_0.ply")
[ "${HAS[1]}" = yes ] && S1=yes && M1=$(md5sum "$CELL/surfaces/${PIECE}_Surface_1.ply" | awk '{print $1}') && B1=$(stat -c %s "$CELL/surfaces/${PIECE}_Surface_1.ply")

SEG=$(find "$ST" -name '*_SampledWithNormals.ply' 2>/dev/null | head -1)
SEGPTS=NA; SEGMD5=NA; SEGB=0
if [ -n "${SEG:-}" ]; then
  SEGPTS=$(grep -m1 '^element vertex' "$SEG" | awk '{print $3}')
  SEGMD5=$(md5sum "$SEG" | awk '{print $1}')
  SEGB=$(stat -c %s "$SEG")
fi

DUB=0
if [ -d "$ST" ]; then
  DUB=$(du -sb "$ST" | awk '{print $1}')
  find "$ST" -type f -printf '%f\t%s\n' 2>/dev/null | awk -F'\t' -v c="$TAG/$POT/$PIECE" '{
      n = split($1, a, "."); e = (n > 1 ? a[n] : "none");
      if (e == "pcd" || e == "ply" || e == "xyz" || e == "obj") f = e; else f = "other";
      cnt[f]++; byt[f] += $2
    } END { for (k in cnt) printf "%s\t%s\t%d\t%d\n", c, k, cnt[k], byt[k] }' >> "$CELLROOT/geometry_counts.tsv"
  rm -rf "$ST"
fi

printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
  "$TAG" "$POT" "$PIECE" "${ENVS:-none}" "$MS" "$EL" "$CL_PRE" "$CL_POST" "$SIZES" "$GROW" "$MERGE" "$CLS" "$FACE" \
  "$SPACING" "$COUNT" "$COUNTM" "$REASSIGN" "$S0" "$S1" "$M0" "$M1" "$B0" "$B1" "$SEGPTS" "$SEGMD5" >> "$CELLROOT/cells.tsv"
printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "$TAG" "$POT" "$PIECE" "$MS" "$EL" "$S0" "$S1" "$DUB" > "$CELL/cell.tsv"
echo "[CELL] $TAG $POT/$PIECE exit=$MS elapsed=${EL}s clusters=$CL_PRE/$CL_POST surfaces=$S0$S1 S=$SPACING"
