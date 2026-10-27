#!/usr/bin/env bash
# ticket 36: one (arm, piece) cell.
# Reads from the environment: CELLROOT POT PIECE TAG ENVS BIN SIF APT STAGER COMMIT PY MEAS AXIS
# Keeps: the two surfaces (.ply and .xyz), every [SPACING-22]/[COUNT-22]/[NORMAL-33]/[RETRY-23]/
# [STATUS-23] line, and one row per cell.  Deletes the stage and the ticket-25 rung dump AFTER the
# measurement has read them, with a per-extension count written before the delete, and writes
# <cell>/cell.tsv.  Nothing is appended to a shared file here: the cells run in parallel.
#
# There is no retry ladder here on purpose.  Ticket 23's floor ceiling is armed only when the counts
# are scaled (mesh_processing_headless.cpp:3625, g_floorCeilingOn && g_countScaleAuto) and ticket 36
# leaves SFS_COUNT_SCALE unset in every arm, so nothing may step the floor down.
set -uo pipefail
TAG=$1
: "${CELLROOT:?}" "${POT:?}" "${PIECE:?}" "${AXIS:?}" "${BIN:?}" "${SIF:?}" \
  "${APT:?}" "${STAGER:?}" "${COMMIT:?}" "${PY:?}" "${MEAS:?}"
ENVS=${ENVS:-}
CELL=$CELLROOT/$TAG/$POT/$PIECE
ST=$CELL/stage
mkdir -p "$CELL/logs" "$CELL/surfaces" "$CELL/measure" "$CELL/dump"
STATUS_RAW=$CELL/status_raw.tsv
: > "$STATUS_RAW"
LOG=$CELL/logs/mesh.log

T0=$(date +%s)
bash "$STAGER" "$ST" "$POT" "$PIECE" "$AXIS" > "$CELL/logs/stage.log" 2>&1
SS=$?
MS=99
if [ "$SS" -eq 0 ]; then
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" \
      SFS_AXIS_FILE="$ST/Dataset/Axes/${PIECE}_Axis.xyz" \
      SFS_STATUS_FILE="$STATUS_RAW" \
      SFS_DUMP_STAGE="$CELL/dump" \
      $ENVS "$BIN" ) > "$LOG" 2>&1
  MS=$?
else
  echo "[CELL] staging failed rc=$SS" > "$LOG"
fi
T1=$(date +%s); EL=$((T1 - T0))

grep -E '\[(SPACING|COUNT|SPLITTER|SWITCH)-2[234]\]|\[(FLOOR|RETRY|SINGLE|STATUS)-23\]|\[NORMAL-3[34]\]|\[PAPER-234\]|\[DUMP-25\]' \
  "$LOG" > "$CELL/logs/lines36.log" 2>/dev/null || true

fld() { grep -m1 "$1" "$LOG" 2>/dev/null | tr ' ' '\n' | grep -m1 "^$2=" | cut -d= -f2- ; }
# the [SPACING-22] line is the only place the step the sampler actually used is printed
SPOL=$(fld '\[SPACING-22\]' policy);        [ -z "${SPOL:-}" ] && SPOL=NA
SDIAG=$(fld '\[SPACING-22\]' diagMM);       [ -z "${SDIAG:-}" ] && SDIAG=NA
SS0=$(fld '\[SPACING-22\]' s0MM);           [ -z "${SS0:-}" ] && SS0=NA
SSAMP=$(fld '\[SPACING-22\]' samples);      [ -z "${SSAMP:-}" ] && SSAMP=NA
SRAW=$(fld '\[SPACING-22\]' rawMM);         [ -z "${SRAW:-}" ] && SRAW=NA
SSMM=$(fld '\[SPACING-22\]' S);             [ -z "${SSMM:-}" ] && SSMM=NA
# [COUNT-22] is printed twice; the first line is the policy line (scale, minCluster, k1, k2)
CPOL=$(fld '\[COUNT-22\]' policy);          [ -z "${CPOL:-}" ] && CPOL=NA
CSCL=$(fld '\[COUNT-22\]' scale);           [ -z "${CSCL:-}" ] && CSCL=NA
CMIN=$(fld '\[COUNT-22\]' minCluster);      [ -z "${CMIN:-}" ] && CMIN=NA
CK1=$(fld '\[COUNT-22\]' k1);               [ -z "${CK1:-}" ] && CK1=NA
CK2=$(fld '\[COUNT-22\]' k2);               [ -z "${CK2:-}" ] && CK2=NA
NPTS=$(fld '\[STATUS-23\]' npts);           [ -z "${NPTS:-}" ] && NPTS=NA
FLOOR=$(fld '\[STATUS-23\]' floor);         [ -z "${FLOOR:-}" ] && FLOOR=NA
FLOORFROM=$(fld '\[STATUS-23\]' floor_from); [ -z "${FLOORFROM:-}" ] && FLOORFROM=NA
CAPPED=$(fld '\[STATUS-23\]' capped);       [ -z "${CAPPED:-}" ] && CAPPED=NA
OUTCOME=$(fld '\[STATUS-23\]' outcome);     [ -z "${OUTCOME:-}" ] && OUTCOME=NA
S0P=$(fld '\[STATUS-23\]' surf0_points);    [ -z "${S0P:-}" ] && S0P=NA
S1P=$(fld '\[STATUS-23\]' surf1_points);    [ -z "${S1P:-}" ] && S1P=NA
SIZES=$(grep '\[RETRY-23\]' "$LOG" | tail -1 | sed -n 's/.* sizes=\([^ ]*\) .*/\1/p'); [ -z "${SIZES:-}" ] && SIZES=none
CLUSTERS=$(grep '\[RETRY-23\]' "$LOG" | tail -1 | sed -n 's/.* clusters=\([^ ]*\) .*/\1/p'); [ -z "${CLUSTERS:-}" ] && CLUSTERS=NA
CLPRE=$(grep '\[RETRY-23\]' "$LOG" | tail -1 | sed -n 's/.* clusters_pre=\([^ ]*\) .*/\1/p'); [ -z "${CLPRE:-}" ] && CLPRE=NA
RETRIES=$(grep -c '\[RETRY-23\]' "$LOG" 2>/dev/null); [ -z "${RETRIES:-}" ] && RETRIES=0

S0=no; S1=no; B0=0
for k in 0 1; do
  src=$ST/Temp/Data/$POT/${PIECE}_Surface_$k.ply
  if [ -f "$src" ]; then
    cp -f "$src" "$CELL/surfaces/${PIECE}_Surface_$k.ply"
    [ -f "$ST/Temp/Data/$POT/${PIECE}_Surface_$k.xyz" ] && cp -f "$ST/Temp/Data/$POT/${PIECE}_Surface_$k.xyz" "$CELL/surfaces/"
    if [ "$k" = 0 ]; then S0=yes; B0=$(stat -c %s "$CELL/surfaces/${PIECE}_Surface_0.ply"); else S1=yes; fi
  fi
done
if [ -f "$ST/Temp/Data/$POT/${PIECE}_SampledWithNormals.ply" ]; then
  cp -f "$ST/Temp/Data/$POT/${PIECE}_SampledWithNormals.ply" "$CELL/surfaces/"
fi

# the measurement runs while the rung dump still exists: it reads the sampled normals and the
# pre-merge cluster ids out of it, and none of that survives the delete.
MRC=99
if [ "$MS" -eq 0 ]; then
  "$PY" "$MEAS" cell --cell "$CELL" --pot "$POT" --piece "$PIECE" --arm "$TAG" \
      --mesh "$ST/Dataset/Mesh/$POT/${PIECE}_Mesh.obj" \
      --cloud "$ST/Dataset/Point/$POT/${PIECE}_Point.pcd" \
      >> "$CELL/logs/measure.log" 2>&1
  MRC=$?
else
  echo "[MEASURE] skipped: pipeline exit $MS" >> "$CELL/logs/measure.log"
fi

KEPT=no
COUNTS=$CELL/logs/geometry_counts.tsv
printf "path\text\tfiles\tbytes\n" > "$COUNTS"
count_tree() {
  local root=$1 tag=$2
  [ -d "$root" ] || return 0
  find "$root" -type f -printf '%p\t%s\n' 2>/dev/null | awk -F'\t' -v t="$tag" -v c="$TAG/$POT/$PIECE" '{
      n = split($1, a, "."); e = (n > 1 ? a[n] : "none");
      if (e ~ /^(pcd|ply|xyz|obj|png|json)$/) f = e; else f = "other";
      cnt[f]++; byt[f] += $2
    } END { for (k in cnt) printf "%s\t%s\t%d\t%d\n", c "/" t, k, cnt[k], byt[k] }' >> "$COUNTS"
}
if [ "$MRC" -eq 0 ]; then
  count_tree "$ST" stage
  count_tree "$CELL/dump" dump
  {
    echo "# counted above, then deleted: $(du -sb "$ST" 2>/dev/null | awk '{print $1}') bytes of stage,"
    echo "# $(du -sb "$CELL/dump" 2>/dev/null | awk '{print $1}') bytes of rung dump"
  } >> "$COUNTS"
  rm -rf "$ST"
  rm -rf "$CELL/dump"
  echo "after: stage present=$([ -d "$ST" ] && echo yes || echo no) dump present=$([ -d "$CELL/dump" ] && echo yes || echo no)" >> "$COUNTS"
else
  KEPT=yes
  {
    echo "# NOT DELETED: the measurement did not succeed (exit $MRC), so the stage and the rung"
    echo "# dump are kept for a follow-up job; out/GEOMETRY_KEPT.txt lists these cells."
  } >> "$COUNTS"
fi

printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
  "$TAG" "$POT" "$PIECE" "${ENVS:-none}" "$MS" "$MRC" "$EL" "$SPOL" "$SDIAG" "$SS0" "$SSAMP" \
  "$SRAW" "$SSMM" "$CPOL" "$CSCL" "$CMIN" "$CK1" "$CK2" "$NPTS" "$RETRIES" "$CLPRE" "$CLUSTERS" \
  "$SIZES" "$OUTCOME" "$FLOOR" "$FLOORFROM" "$CAPPED" "$S0" "$S1" "$S0P" "$S1P" "$B0" "$KEPT" > "$CELL/cell.tsv"
echo "[CELL] $TAG $POT/$PIECE exit=$MS meas=$MRC elapsed=${EL}s S=$SSMM (policy=$SPOL) npts=$NPTS floor=$FLOOR from=$FLOORFROM capped=$CAPPED clusters_pre=$CLPRE clusters=$CLUSTERS sizes=$SIZES outcome=$OUTCOME s0=$S0 s1=$S1 kept=$KEPT"
