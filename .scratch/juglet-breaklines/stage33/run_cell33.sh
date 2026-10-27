#!/usr/bin/env bash
# ticket 33: one (arm, piece) cell.
# Reads from the environment: CELLROOT POT PIECE TAG ENVS BIN SIF APT STAGER COMMIT PY MEAS
# and, for the arms whose floor is forced down, CEIL_LADDER (tried in order until the floor the
# binary reports is at most 2 % of the cloud it segmented).
# Keeps: the two surfaces (.ply and .xyz), every [NORMAL-33]/[PAPER-234]/[*-2x] line, and one row
# per attempt.  Deletes the stage and the ticket-25 rung dump AFTER the measurement has read them,
# with a per-extension count written before the delete, and writes <cell>/cell.tsv.  Nothing is
# appended to a shared file here: the cells run in parallel.
set -uo pipefail
TAG=$1
: "${CELLROOT:?}" "${POT:?}" "${PIECE:?}" "${AXIS:?}" "${BIN:?}" "${SIF:?}" \
  "${APT:?}" "${STAGER:?}" "${COMMIT:?}" "${PY:?}" "${MEAS:?}"
ENVS=${ENVS:-}
CEIL_LADDER=${CEIL_LADDER:-}
CELL=$CELLROOT/$TAG/$POT/$PIECE
ST=$CELL/stage
mkdir -p "$CELL/logs" "$CELL/surfaces" "$CELL/measure" "$CELL/dump"
STATUS_RAW=$CELL/status_raw.tsv
: > "$STATUS_RAW"
LOG=$CELL/logs/mesh.log
ATT=$CELL/logs/attempts.tsv
printf "frac\tnpts\tfloor\tcapped\tcap\tstatus\tat_most_2pct\texit\n" > "$ATT"

T0=$(date +%s)
bash "$STAGER" "$ST" "$POT" "$PIECE" "$AXIS" > "$CELL/logs/stage.log" 2>&1
SS=$?
MS=99
FRAC_USED=none
if [ "$SS" -eq 0 ]; then
  run_bin() {
    : > "$LOG"
    ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" \
        SFS_AXIS_FILE="$ST/Dataset/Axes/${PIECE}_Axis.xyz" \
        SFS_STATUS_FILE="$STATUS_RAW" \
        SFS_DUMP_STAGE="$CELL/dump" \
        $ENVS $1 "$BIN" ) >> "$LOG" 2>&1
    return $?
  }
  fld() { grep -m1 "$1" "$LOG" 2>/dev/null | tr ' ' '\n' | grep -m1 "^$2=" | cut -d= -f2- ; }
  if [ -n "$CEIL_LADDER" ]; then
    for FRAC in $CEIL_LADDER; do
      run_bin "SFS_FLOOR_CEILING=$FRAC"
      MS=$?
      N=$(fld '\[FLOOR-23\]' npts); F=$(fld '\[FLOOR-23\]' minCluster)
      C=$(fld '\[FLOOR-23\]' cap); K=$(fld '\[FLOOR-23\]' clamped)
      N=${N:-0}; F=${F:-0}
      OK=no
      if [ "$N" -gt 0 ] && [ $((F * 100)) -le $((2 * N)) ]; then OK=yes; fi
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "$FRAC" "${N:-NA}" "${F:-NA}" "${K:-NA}" "${C:-NA}" "attempt" "$OK" "$MS" >> "$ATT"
      FRAC_USED=$FRAC
      if [ "$OK" = "yes" ]; then break; fi
      echo "[CELL] $TAG $POT/$PIECE floor $F above 2 % of $N at frac=$FRAC, stepping down"
    done
  else
    run_bin ""
    MS=$?
  fi
fi
T1=$(date +%s); EL=$((T1 - T0))

grep -E '\[(NORMAL|PAPER)-33\]|\[(SWITCH|FLOOR|RETRY|SINGLE|STATUS)-23\]|\[(SPACING|COUNT|SPLITTER)-2[234]\]|\[DUMP-25\]' \
  "$LOG" > "$CELL/logs/lines33.log" 2>/dev/null || true

fld() { grep -m1 "$1" "$LOG" 2>/dev/null | tr ' ' '\n' | grep -m1 "^$2=" | cut -d= -f2- ; }
NPTS=$(fld '\[STATUS-23\]' npts);            [ -z "${NPTS:-}" ] && NPTS=NA
FLOOR=$(fld '\[STATUS-23\]' floor);          [ -z "${FLOOR:-}" ] && FLOOR=NA
FLOORFROM=$(fld '\[STATUS-23\]' floor_from); [ -z "${FLOORFROM:-}" ] && FLOORFROM=NA
CAPPED=$(fld '\[STATUS-23\]' capped);        [ -z "${CAPPED:-}" ] && CAPPED=NA
OUTCOME=$(fld '\[STATUS-23\]' outcome);      [ -z "${OUTCOME:-}" ] && OUTCOME=NA
S0P=$(fld '\[STATUS-23\]' surf0_points);     [ -z "${S0P:-}" ] && S0P=NA
S1P=$(fld '\[STATUS-23\]' surf1_points);     [ -z "${S1P:-}" ] && S1P=NA
SIZES=$(grep '\[RETRY-23\]' "$LOG" | tail -1 | sed -n 's/.* sizes=\([^ ]*\) .*/\1/p'); [ -z "${SIZES:-}" ] && SIZES=none
CLUSTERS=$(grep '\[RETRY-23\]' "$LOG" | tail -1 | sed -n 's/.* clusters=\([^ ]*\) .*/\1/p'); [ -z "${CLUSTERS:-}" ] && CLUSTERS=NA
CLPRE=$(grep '\[RETRY-23\]' "$LOG" | tail -1 | sed -n 's/.* clusters_pre=\([^ ]*\) .*/\1/p'); [ -z "${CLPRE:-}" ] && CLPRE=NA
RETRIES=$(grep -c '\[RETRY-23\]' "$LOG" 2>/dev/null); [ -z "${RETRIES:-}" ] && RETRIES=0
SPLIT=$(grep -m1 '\[SPLITTER-234\]' "$LOG" | sed 's/^.*\[SPLITTER-234\] //'); [ -z "${SPLIT:-}" ] && SPLIT=none
PAPER=$(grep -m1 '\[PAPER-234\] appendix-A merge' "$LOG" | sed 's/^.*merge: //'); [ -z "${PAPER:-}" ] && PAPER=none

S0=no; S1=no; B0=0; B1=0
for k in 0 1; do
  src=$ST/Temp/Data/$POT/${PIECE}_Surface_$k.ply
  if [ -f "$src" ]; then
    cp -f "$src" "$CELL/surfaces/${PIECE}_Surface_$k.ply"
    [ -f "$ST/Temp/Data/$POT/${PIECE}_Surface_$k.xyz" ] && cp -f "$ST/Temp/Data/$POT/${PIECE}_Surface_$k.xyz" "$CELL/surfaces/"
    if [ "$k" = 0 ]; then S0=yes; B0=$(stat -c %s "$CELL/surfaces/${PIECE}_Surface_0.ply");
    else S1=yes; B1=$(stat -c %s "$CELL/surfaces/${PIECE}_Surface_1.ply"); fi
  fi
done
if [ -f "$ST/Temp/Data/$POT/${PIECE}_SampledWithNormals.ply" ]; then
  cp -f "$ST/Temp/Data/$POT/${PIECE}_SampledWithNormals.ply" "$CELL/surfaces/"
fi

# the measurement runs while the rung dump still exists: it reads the carried normals and the
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
DUB=0
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
  DUB=$(du -sb "$ST" 2>/dev/null | awk '{print $1}')
  count_tree "$ST" stage
  count_tree "$CELL/dump" dump
  DUB=$(du -sb "$ST" "$CELL/dump" 2>/dev/null | awk '{s+=$1} END {print s+0}')
  rm -rf "$ST"
  if [ -d "$CELL/dump" ]; then
    {
      echo "# ticket 33 rung dump, counted above, deleted after the measurement read it"
      echo "dump_bytes $(du -sb "$CELL/dump" 2>/dev/null | awk '{print $1}')"
      rm -rf "$CELL/dump"
      echo "after: $(find "$CELL/dump" -type f 2>/dev/null | wc -l) files, present=$([ -d "$CELL/dump" ] && echo yes || echo no)"
    } >> "$COUNTS"
  fi
else
  KEPT=yes
  {
    echo "# NOT DELETED: the measurement did not succeed (exit $MRC), so the stage and the rung"
    echo "# dump are kept for a follow-up job; out/GEOMETRY_KEPT.txt lists these cells."
  } >> "$COUNTS"
fi

printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
  "$TAG" "$POT" "$PIECE" "${ENVS:-none}" "${FRAC_USED:-none}" "$MS" "$MRC" "$EL" "$NPTS" \
  "$RETRIES" "$CLPRE" "$CLUSTERS" "$SIZES" "$OUTCOME" "$FLOOR" "$FLOORFROM" "$CAPPED" \
  "$S0" "$S1" "$S0P" "$S1P" "$B0" "$KEPT" > "$CELL/cell.tsv"
printf "%s\n" "$SPLIT" > "$CELL/logs/splitter.txt"
printf "%s\n" "$PAPER" > "$CELL/logs/paper.txt"
echo "[CELL] $TAG $POT/$PIECE exit=$MS meas=$MRC elapsed=${EL}s npts=$NPTS floor=$FLOOR from=$FLOORFROM capped=$CAPPED clusters_pre=$CLPRE clusters=$CLUSTERS sizes=$SIZES s0=$S0 s1=$S1 frac=$FRAC_USED kept=$KEPT"
