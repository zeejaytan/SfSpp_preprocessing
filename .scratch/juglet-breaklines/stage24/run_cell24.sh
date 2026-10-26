#!/usr/bin/env bash
# ticket 24: one (arm, piece) cell of the normals grid.
# Reads from the environment: CELLROOT POT PIECE TAG ENVS AXIS BIN SIF APT STAGER COMMIT ANGLER PY.
# Keeps the surface bundle (S0/S1 .ply and .xyz), the log, the per-call angle table against the
# MESH normal, the neighbours-used distribution and every [*-24]/[*-23]/[*-22] line; deletes the
# rest of the stage (including the per-call normals PLYs) with a counted record, and appends one
# row to $CELLROOT/cells24.tsv.
set -uo pipefail
TAG=$1
: "${CELLROOT:?}" "${POT:?}" "${PIECE:?}" "${AXIS:?}" "${BIN:?}" "${SIF:?}" "${APT:?}" "${STAGER:?}" "${COMMIT:?}"
ENVS=${ENVS:-}
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
      SFS_NORMAL_DUMP_DIR="$ST/Temp/_n24" $ENVS "$BIN" ) >> "$LOG" 2>&1
  MS=$?
fi
T1=$(date +%s); EL=$((T1 - T0))

# every line the stage prints that this ticket is read from, kept verbatim
grep -E '\[(SWITCH|FLOOR|RETRY|SINGLE|STATUS)-23\]|\[(SPACING|COUNT)-22\]|\[NORMAL-24(-SWITCH)?\]|\[ADAPTIVE CGAL\]|\[ARM-E\]|Warning: Source file not found|Proceeding with available clusters|Successfully found' \
  "$LOG" > "$CELL/logs/lines24.log" 2>/dev/null || true

fld() { grep -m1 "$1" "$LOG" 2>/dev/null | tr ' ' '\n' | grep -m1 "^$2=" | cut -d= -f2- ; }
CL_PRE=$(grep -m1 'Number of clusters is equal to' "$LOG" | awk '{print $NF}')
[ -z "${CL_PRE:-}" ] && CL_PRE=NA
RETRIES=$(grep -c '\[RETRY-23\]' "$LOG" 2>/dev/null); [ -z "${RETRIES:-}" ] && RETRIES=0
SIZES=$(grep '\[RETRY-23\]' "$LOG" | tail -1 | sed -n 's/.* sizes=\([^ ]*\) .*/\1/p')
[ -z "${SIZES:-}" ] && SIZES=none
CLUSTERS=$(grep '\[RETRY-23\]' "$LOG" | tail -1 | sed -n 's/.* clusters=\([^ ]*\) .*/\1/p')
[ -z "${CLUSTERS:-}" ] && CLUSTERS=NA
OUTCOME=$(fld '\[STATUS-23\]' outcome);   [ -z "${OUTCOME:-}" ] && OUTCOME=NA
NPTS=$(fld '\[STATUS-23\]' npts);         [ -z "${NPTS:-}" ] && NPTS=NA
FLOOR=$(fld '\[STATUS-23\]' floor);       [ -z "${FLOOR:-}" ] && FLOOR=NA
FLOORFROM=$(fld '\[STATUS-23\]' floor_from); [ -z "${FLOORFROM:-}" ] && FLOORFROM=NA
CAPPED=$(fld '\[STATUS-23\]' capped);     [ -z "${CAPPED:-}" ] && CAPPED=NA
S0P=$(fld '\[STATUS-23\]' surf0_points);  [ -z "${S0P:-}" ] && S0P=NA
S1P=$(fld '\[STATUS-23\]' surf1_points);  [ -z "${S1P:-}" ] && S1P=NA
SWITCHL=$(grep -m1 '\[SWITCH-23\]' "$LOG" | sed 's/^.*\[SWITCH-23\] //'); [ -z "${SWITCHL:-}" ] && SWITCHL=none
FLOORL=$(grep -m1 '\[FLOOR-23\]' "$LOG" | sed 's/^.*\[FLOOR-23\] //');  [ -z "${FLOORL:-}" ] && FLOORL=none
SINGLEL=$(grep -m1 '\[SINGLE-23\]' "$LOG" | sed 's/^.*\[SINGLE-23\] //'); [ -z "${SINGLEL:-}" ] && SINGLEL=none
STATUSL=$(grep -m1 '\[STATUS-23\]' "$LOG" | sed 's/^.*\[STATUS-23\] //'); [ -z "${STATUSL:-}" ] && STATUSL=none
SPACING=$(grep -m1 '\[SPACING-22\]' "$LOG" | sed 's/^.*\[SPACING-22\] //'); [ -z "${SPACING:-}" ] && SPACING=none
COUNT=$(grep -m1 '\[COUNT-22\] policy=' "$LOG" | sed 's/^.*\[COUNT-22\] //'); [ -z "${COUNT:-}" ] && COUNT=none
WARN=$(grep -c 'Warning: Source file not found' "$LOG" 2>/dev/null); [ -z "${WARN:-}" ] && WARN=0

# ticket 24: the normals calls, from the stage's own lines
CALLS=$(grep -c '\[NORMAL-24\] piece=' "$LOG" 2>/dev/null); [ -z "${CALLS:-}" ] && CALLS=0
NMODEL=$(grep -m1 '\[NORMAL-24\] piece=' "$LOG" | sed -n 's/.* mode=\([^ ]*\) .*/\1/p'); [ -z "${NMODEL:-}" ] && NMODEL=none
CGAKL=$(grep -m1 '\[ADAPTIVE CGAL\]' "$LOG" | sed -n 's/.*Using \([0-9]*\) neighbors.*/\1/p'); [ -z "${CGAKL:-}" ] && CGAKL=NA
RADII=$(grep '\[NORMAL-24\] piece=' "$LOG" | sed -n 's/.* radiusMM=\([^ ]*\) .*/\1/p' | paste -sd, -)
[ -z "${RADII:-}" ] && RADII=none
NMED=$(grep '\[NORMAL-24\] piece=' "$LOG" | sed -n 's/.* nbrMedian=\([0-9]*\) .*/\1/p' | paste -sd, -)
[ -z "${NMED:-}" ] && NMED=none
NMIN=$(grep '\[NORMAL-24\] piece=' "$LOG" | sed -n 's/.* nbrMin=\([0-9]*\) .*/\1/p' | paste -sd, -)
[ -z "${NMIN:-}" ] && NMIN=none
NMAX=$(grep '\[NORMAL-24\] piece=' "$LOG" | sed -n 's/.* nbrMax=\([0-9]*\) .*/\1/p' | paste -sd, -)
[ -z "${NMAX:-}" ] && NMAX=none
OK24=$(grep '\[NORMAL-24\] piece=' "$LOG" | sed -n 's/.* orientK=\([0-9]*\) .*/\1/p' | paste -sd, -)
[ -z "${OK24:-}" ] && OK24=none
FLR24=$(grep '\[NORMAL-24\] piece=' "$LOG" | sed -n 's/.* flooredToMinK=\([0-9]*\) .*/\1/p' | paste -sd, -)
[ -z "${FLR24:-}" ] && FLR24=none
CAP24=$(grep '\[NORMAL-24\] piece=' "$LOG" | sed -n 's/.* cappedAtMaxK=\([0-9]*\) .*/\1/p' | paste -sd, -)
[ -z "${CAP24:-}" ] && CAP24=none
SP24=$(grep '\[NORMAL-24\] piece=' "$LOG" | sed -n 's/.* cloudSpacingMM=\([^ ]*\) .*/\1/p' | paste -sd, -)
[ -z "${SP24:-}" ] && SP24=none
SW24=$(grep -m1 '\[NORMAL-24-SWITCH\]' "$LOG" | sed 's/^.*\[NORMAL-24-SWITCH\] //'); [ -z "${SW24:-}" ] && SW24=none

# ticket 24: the angle between each estimated normal and the MESH normal at the nearest surface
# point, measured on the per-call PLYs the stage dumped, while the stage still exists.
ANGN=0
if [ -d "$ST/Temp/_n24" ] && [ -n "$(ls -A "$ST/Temp/_n24" 2>/dev/null)" ]; then
  "$PY" "$ANGLER" "$ST/Dataset/Mesh/$POT/${PIECE}_Mesh.obj" "$ST/Temp/_n24" \
      "$CELL/angles24.tsv" "$CELL/angle_points.tsv" "$TAG" "$POT" "$PIECE" --max-calls 24 >> "$CELL/logs/angles.log" 2>&1
  AN=$?
  ANGN=$(($(wc -l < "$CELL/angles24.tsv") - 1))
  echo "[ANGLES] $TAG $POT/$PIECE exit=$AN rows=$ANGN" >> "$CELL/logs/angles.log"
else
  printf "%s\t%s\t%s\t0\tNA\tNA\tNA\tNA\tNA\tNA\tNA\tNA\tNA\n" "$TAG" "$POT" "$PIECE" >> "$CELL/angles24.tsv"
fi

S0=no; S1=no; B0=0; B1=0
for k in 0 1; do
  src=$ST/Temp/Data/$POT/${PIECE}_Surface_$k.ply
  if [ -f "$src" ]; then
    cp -f "$src" "$CELL/surfaces/${PIECE}_Surface_$k.ply"
    [ -f "$ST/Temp/Data/$POT/${PIECE}_Surface_$k.xyz" ] && cp -f "$ST/Temp/Data/$POT/${PIECE}_Surface_$k.xyz" "$CELL/surfaces/"
    if [ "$k" = 0 ]; then S0=yes; B0=$(stat -c %s "$CELL/surfaces/${PIECE}_Surface_0.ply"); else S1=yes; B1=$(stat -c %s "$CELL/surfaces/${PIECE}_Surface_1.ply"); fi
  fi
done

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

if [ -s "$STATUS_RAW" ]; then
  awk -v a="$TAG" -v p="$POT" 'BEGIN{OFS="\t"} {print a,p,$0}' "$STATUS_RAW" >> "$CELLROOT/status23.tsv"
else
  printf "%s\t%s\t%s\t%s\tNO_STATUS_ROW\n" "$TAG" "$POT" "$PIECE" "mesh_exit=$MS" >> "$CELLROOT/status23.tsv"
fi

printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
  "$TAG" "$POT" "$PIECE" "${ENVS:-none}" "$MS" "$EL" "$NPTS" "$RETRIES" "$CLUSTERS" "$SIZES" \
  "$OUTCOME" "$FLOOR" "$FLOORFROM" "$CAPPED" "$S0" "$S1" "$S0P" "$S1P" \
  "$SWITCHL" "$FLOORL" "$SINGLEL" "$STATUSL" "$SPACING" "$COUNT" "$WARN" "$B0" \
  "$CALLS" "$NMODEL" "$CGAKL" "$RADII" "$NMED" "$NMIN" "$NMAX" "$OK24" "$FLR24" "$CAP24" "$SP24" "$SW24" >> "$CELLROOT/cells24.tsv"
printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "$TAG" "$POT" "$PIECE" "$MS" "$EL" "$S0" "$S1" "$DUB" > "$CELL/cell.tsv"
echo "[CELL] $TAG $POT/$PIECE exit=$MS elapsed=${EL}s clusters=$CLUSTERS sizes=$SIZES outcome=$OUTCOME normals=$CALLS mode=$NMODEL radius=$RADII nbrMed=$NMED angl=$ANGN s0=$S0 s1=$S1 warn=$WARN"
