#!/usr/bin/env bash
# ticket 26: one (scheme, piece) cell of the three-millimetre-window grid.
# Reads from the environment: CELLROOT POT PIECE TAG SCHEME ROLE ENVS AXIS BIN SIF APT STAGER COMMIT PY.
# Keeps the surface bundle (S0/S1 .ply and .xyz) and the log -- the lead re-measures them --
# keeps every [WINDOW-26*] and [*-2x] line, deletes the rest of the stage with a counted record,
# and appends one row to $CELLROOT/cells26.tsv plus the [STATUS-23] rows.
set -uo pipefail
TAG=$1
: "${CELLROOT:?}" "${POT:?}" "${PIECE:?}" "${AXIS:?}" "${BIN:?}" "${SIF:?}" "${APT:?}" "${STAGER:?}" "${COMMIT:?}"
ENVS=${ENVS:-}
SCHEME=${SCHEME:-none}
ROLE=${ROLE:-grid}
case "$ENVS" in
  *SFS_PAPER_CHAIN=0*) PAPER=off ;;
  *) PAPER=on ;;
esac
CELL=$CELLROOT/$TAG/$POT/$PIECE
ST=$CELL/stage
mkdir -p "$CELL/logs" "$CELL/surfaces"
STATUS_RAW=$CELL/status_raw.tsv
: > "$STATUS_RAW"
T0=$(date +%s)
bash "$STAGER" "$ST" "$POT" "$PIECE" "$AXIS" > "$CELL/logs/stage.log" 2>&1
SS=$?
LOG=$CELL/logs/mesh.log
: > "$LOG"
MS=99
if [ "$SS" -eq 0 ]; then
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" \
      SFS_AXIS_FILE="$ST/Dataset/Axes/${PIECE}_Axis.xyz" SFS_STATUS_FILE="$STATUS_RAW" \
      SFS_WINDOW_REPORT="$CELL/window26.tsv" $ENVS "$BIN" ) >> "$LOG" 2>&1
  MS=$?
fi
T1=$(date +%s); EL=$((T1 - T0))

# every line this ticket is read from, kept verbatim
grep -E "\[WINDOW-26\]|\[WINDOW-26-(MEASURE|FINAL|SWITCH)\]|\[(SWITCH|FLOOR|RETRY|SINGLE|STATUS)-23\]|\[(SPACING|COUNT)-22\]|\[REASSIGN-22\]|\[PAPER-234\]|Warning: Source file not found|Proceeding with available clusters|Successfully found|Normals flipped" \
  "$LOG" > "$CELL/logs/lines26.log" 2>/dev/null || true

fld() { grep -m1 "$1" "$LOG" 2>/dev/null | tr " " "\n" | grep -m1 "^$2=" | cut -d= -f2- ; }
wrow() { grep "^\[WINDOW-26\] " "$LOG" 2>/dev/null | grep -m1 " surface=$1 " ; }
wfld() { wrow "$1" | tr " " "\n" | grep -m1 "^$2=" | cut -d= -f2- ; }
mrow() { grep "^\[WINDOW-26-MEASURE\] " "$LOG" 2>/dev/null | grep -m1 " surface=$1 " ; }
mfld() { mrow "$1" | tr " " "\n" | grep -m1 "^$2=" | cut -d= -f2- ; }
ffld() { grep "^\[WINDOW-26-FINAL\] " "$LOG" 2>/dev/null | grep -m1 " surface=$1 " | tr " " "\n" | grep -m1 "^$2=" | cut -d= -f2- ; }

WINLINES=$(grep -c "^\[WINDOW-26\] " "$LOG" 2>/dev/null); [ -z "${WINLINES:-}" ] && WINLINES=0
for k in 0 1; do
  eval "W${k}MM=$(wfld $k clamped_mm)"
  eval "R${k}MM=$(wfld $k residual_mm)"
  eval "O${k}MM=$(wfld $k other_mm)"
  eval "RULE${k}=$(mfld $k rule)"
  eval "REASON${k}=$(mfld $k reason)"
  eval "CFROM${k}=$(mfld $k clamped_from_mm)"
  eval "AOWN${k}=$(wfld $k admitted_own)"
  eval "AOTH${k}=$(wfld $k admitted_other)"
  eval "FINAL${k}=$(ffld $k final_points)"
  eval "COP${k}=$(ffld $k other_copied_over)"
  for v in W${k}MM R${k}MM O${k}MM RULE${k} REASON${k} CFROM${k} AOWN${k} AOTH${k} FINAL${k} COP${k}; do
    eval "[ -z \"\${$v:-}\" ] && $v=NA"
  done
done

CL_PRE=$(grep -m1 "\[RETRY-23\]" "$LOG" | sed -n "s/.* clusters_pre=\([^ ]*\) .*/\1/p"); [ -z "${CL_PRE:-}" ] && CL_PRE=NA
CLUSTERS=$(grep "\[RETRY-23\]" "$LOG" | tail -1 | sed -n "s/.* clusters=\([^ ]*\) .*/\1/p"); [ -z "${CLUSTERS:-}" ] && CLUSTERS=NA
SIZES=$(grep "\[RETRY-23\]" "$LOG" | tail -1 | sed -n "s/.* sizes=\([^ ]*\) .*/\1/p"); [ -z "${SIZES:-}" ] && SIZES=none
OUTCOME=$(fld "\[STATUS-23\]" outcome); [ -z "${OUTCOME:-}" ] && OUTCOME=NA
NPTS=$(fld "\[STATUS-23\]" npts); [ -z "${NPTS:-}" ] && NPTS=NA
S0P=$(fld "\[STATUS-23\]" surf0_points); [ -z "${S0P:-}" ] && S0P=NA
S1P=$(fld "\[STATUS-23\]" surf1_points); [ -z "${S1P:-}" ] && S1P=NA
SINGLE=$(grep -m1 "\[SINGLE-23\]" "$LOG" | sed "s/^.*\[SINGLE-23\] //"); [ -z "${SINGLE:-}" ] && SINGLE=none
SPACING=$(grep -m1 "\[SPACING-22\]" "$LOG" | sed "s/^.*\[SPACING-22\] //"); [ -z "${SPACING:-}" ] && SPACING=none
COUNT=$(grep -m1 "\[COUNT-22\] policy=" "$LOG" | sed "s/^.*\[COUNT-22\] //"); [ -z "${COUNT:-}" ] && COUNT=none
WSW=$(grep -m1 "\[WINDOW-26-SWITCH\]" "$LOG" | sed "s/^.*\[WINDOW-26-SWITCH\] //"); [ -z "${WSW:-}" ] && WSW=none
STATUSL=$(grep -m1 "\[STATUS-23\]" "$LOG" | sed "s/^.*\[STATUS-23\] //"); [ -z "${STATUSL:-}" ] && STATUSL=none
WARN=$(grep -c "Warning: Source file not found" "$LOG" 2>/dev/null); [ -z "${WARN:-}" ] && WARN=0

S0=no; S1=no; B0=0
for k in 0 1; do
  src=$ST/Temp/Data/$POT/${PIECE}_Surface_$k.ply
  if [ -f "$src" ]; then
    cp -f "$src" "$CELL/surfaces/${PIECE}_Surface_$k.ply"
    [ -f "$ST/Temp/Data/$POT/${PIECE}_Surface_$k.xyz" ] && cp -f "$ST/Temp/Data/$POT/${PIECE}_Surface_$k.xyz" "$CELL/surfaces/"
    if [ "$k" = 0 ]; then S0=yes; B0=$(stat -c %s "$CELL/surfaces/${PIECE}_Surface_0.ply"); else S1=yes; fi
  fi
done

if [ -d "$ST" ]; then
  find "$ST" -type f -printf "%f\t%s\n" 2>/dev/null | awk -F"\t" -v c="$TAG/$POT/$PIECE" '{
      n = split($1, a, "."); e = (n > 1 ? a[n] : "none");
      if (e == "pcd" || e == "ply" || e == "xyz" || e == "obj") f = e; else f = "other";
      cnt[f]++; byt[f] += $2
    } END { for (k in cnt) printf "%s\t%s\t%d\t%d\n", c, k, cnt[k], byt[k] }' >> "$CELLROOT/geometry_counts.tsv"
  rm -rf "$ST"
fi

if [ -s "$STATUS_RAW" ]; then
  awk -v a="$TAG" -v p="$POT" 'BEGIN{OFS="\t"} {print a,p,$0}' "$STATUS_RAW" >> "$CELLROOT/status23.tsv"
else
  printf "%s\t%s\t%s\t%s\tNO_STATUS_ROW\n" "$TAG" "$POT" "$PIECE" "mesh_exit=$MS" >> "$CELLROOT/status23.tsv"
fi

printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
  "$ROLE" "$TAG" "$SCHEME" "$POT" "$PIECE" "$PAPER" "${ENVS:-none}" "$MS" "$EL" "$WINLINES" \
  "$W0MM" "$W1MM" "$R0MM" "$R1MM" "$O0MM" "$O1MM" "$RULE0" "$RULE1" "$REASON0" "$REASON1" \
  "$CFROM0" "$CFROM1" "$AOWN0" "$AOWN1" "$AOTH0" "$AOTH1" "$FINAL0" "$FINAL1" "$COP0" "$COP1" \
  "$CL_PRE" "$CLUSTERS" "$SIZES" "$OUTCOME" "$SINGLE" "$S0" "$S1" "$S0P" "$S1P" "$NPTS" \
  "$WSW" "$SPACING" "$COUNT" "$WARN" "$B0" "$STATUSL" >> "$CELLROOT/cells26.tsv"
printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "$TAG" "$POT" "$PIECE" "$MS" "$EL" "$S0" "$S1" > "$CELL/cell.tsv"
echo "[CELL] $ROLE $TAG $SCHEME paper=$PAPER $POT/$PIECE exit=$MS elapsed=${EL}s win=$WINLINES s0=$W0MM s1=$W1MM res=$R0MM/$R1MM other=$O0MM/$O1MM clusters_pre=$CL_PRE clusters=$CLUSTERS sizes=$SIZES outcome=$OUTCOME surf=$S0/$S1 pts=$S0P/$S1P"
