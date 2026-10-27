#!/usr/bin/env bash
# ticket 25: one (arm, piece) cell of the per-step geometry dump ladder.
# Reads from the environment: CELLROOT DUMPROOT POT PIECE AXIS BIN SIF APT STAGER COMMIT.
# Arm B = today's defaults, D = paper chain off, E = paper chain off at native density,
# A / A2 = the same binary twice with SFS_DUMP_STAGE unset (the defaults proof and its
# run-to-run control), OLD = the pre-change binary with SFS_DUMP_STAGE unset.
# Keeps: the five rung dumps (deliverable), the written surfaces, the log lines this ticket
# is read from. Deletes the stage tree with a counted record.
set -uo pipefail
TAG=$1
: "${CELLROOT:?}" "${DUMPROOT:?}" "${POT:?}" "${PIECE:?}" "${AXIS:?}" "${BIN:?}" "${SIF:?}" "${APT:?}" "${STAGER:?}" "${COMMIT:?}"
CELL=$CELLROOT/$TAG/$PIECE
ST=$CELL/stage
mkdir -p "$CELL/logs" "$CELL/surfaces"
STATUS_RAW=$CELL/status_raw.tsv
: > "$STATUS_RAW"

case "$TAG" in
  B) DUMPENV="SFS_DUMP_STAGE=$DUMPROOT/B SFS_DUMP_PIECES=$PIECE"; ARM=NEW ;;
  D) DUMPENV="SFS_DUMP_STAGE=$DUMPROOT/D SFS_DUMP_PIECES=$PIECE SFS_PAPER_CHAIN=0"; ARM=NEW ;;
  E) DUMPENV="SFS_DUMP_STAGE=$DUMPROOT/E SFS_DUMP_PIECES=$PIECE SFS_PAPER_CHAIN=0 SFS_DOWNSAMPLE_TARGET=-1"; ARM=NEW ;;
  A|A2) DUMPENV=""; ARM=NEW ;;
  OLD) DUMPENV=""; ARM=OLD ;;
  DOLD) DUMPENV="SFS_PAPER_CHAIN=0"; ARM=OLD ;;
  EOLD) DUMPENV="SFS_PAPER_CHAIN=0 SFS_DOWNSAMPLE_TARGET=-1"; ARM=OLD ;;
  *) DUMPENV=""; ARM=NEW ;;
esac
[ -n "${EXTRA:-}" ] && DUMPENV="$DUMPENV ${EXTRA}"
DUMP_ENV_LABEL="unset"
case "$TAG" in B|D|E) DUMP_ENV_LABEL="set" ;; esac

T0=$(date +%s)
bash "$STAGER" "$ST" "$POT" "$PIECE" "$AXIS" > "$CELL/logs/stage.log" 2>&1
SS=$?
LOG=$CELL/logs/mesh.log
: > "$LOG"
MS=99
if [ "$SS" -eq 0 ]; then
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" \
      SFS_AXIS_FILE="$ST/Dataset/Axes/${PIECE}_Axis.xyz" SFS_STATUS_FILE="$STATUS_RAW" \
      SFS_WINDOW_REPORT="$CELL/window26.tsv" $DUMPENV "$BIN" ) >> "$LOG" 2>&1
  MS=$?
fi
T1=$(date +%s); EL=$((T1 - T0))

grep -E "\[DUMP-25\]|\[(WINDOW-26|WINDOW-26-MEASURE|WINDOW-26-FINAL|WINDOW-26-SWITCH)\]|\[(SWITCH|FLOOR|RETRY|SINGLE|STATUS)-23\]|\[(SPACING|COUNT)-22\]|\[REASSIGN-22\]|\[PAPER-234\]|Warning: Source file not found|Successfully found|Normals flipped" \
  "$LOG" > "$CELL/logs/lines25.log" 2>/dev/null || true

fld() { grep -m1 "$1" "$LOG" 2>/dev/null | tr " " "\n" | grep -m1 "^$2=" | cut -d= -f2- ; }
OUTCOME=$(fld "\[STATUS-23\]" outcome); [ -z "${OUTCOME:-}" ] && OUTCOME=NA
NPTS=$(fld "\[STATUS-23\]" npts); [ -z "${NPTS:-}" ] && NPTS=NA
S0P=$(fld "\[STATUS-23\]" surf0_points); [ -z "${S0P:-}" ] && S0P=NA
S1P=$(fld "\[STATUS-23\]" surf1_points); [ -z "${S1P:-}" ] && S1P=NA
CLUSTERS=$(grep "\[RETRY-23\]" "$LOG" | tail -1 | sed -n "s/.* clusters=\([^ ]*\) .*/\1/p"); [ -z "${CLUSTERS:-}" ] && CLUSTERS=NA
SIZES=$(grep "\[RETRY-23\]" "$LOG" | tail -1 | sed -n "s/.* sizes=\([^ ]*\) .*/\1/p"); [ -z "${SIZES:-}" ] && SIZES=none
SINGLEL=$(grep -m1 "\[SINGLE-23\]" "$LOG" | sed "s/^.*\[SINGLE-23\] //"); [ -z "${SINGLEL:-}" ] && SINGLEL=none
STATUSL=$(grep -m1 "\[STATUS-23\]" "$LOG" | sed "s/^.*\[STATUS-23\] //"); [ -z "${STATUSL:-}" ] && STATUSL=none
DUMPWROTE=$(grep -c "^\[DUMP-25\] wrote" "$LOG" 2>/dev/null); [ -z "${DUMPWROTE:-}" ] && DUMPWROTE=0
DUMPREF=$(grep -c "REFUSED\|CANNOT WRITE" "$LOG" 2>/dev/null); [ -z "${DUMPREF:-}" ] && DUMPREF=0

S0=no; S1=no
for k in 0 1; do
  src=$ST/Temp/Data/$POT/${PIECE}_Surface_$k.ply
  if [ -f "$src" ]; then
    cp -f "$src" "$CELL/surfaces/${PIECE}_Surface_$k.ply"
    [ -f "$ST/Temp/Data/$POT/${PIECE}_Surface_$k.xyz" ] && cp -f "$ST/Temp/Data/$POT/${PIECE}_Surface_$k.xyz" "$CELL/surfaces/"
    if [ "$k" = 0 ]; then S0=yes; else S1=yes; fi
  fi
done

DUMPS=0; R1=0; R2=0; R3=0; R4=0; R5=0
if [ -d "$DUMPROOT/$TAG/$PIECE" ]; then
  DUMPS=$(find "$DUMPROOT/$TAG/$PIECE" -name "*.ply" | wc -l)
  [ -f "$DUMPROOT/$TAG/$PIECE/r1_downsampled.ply" ] && R1=1
  [ -f "$DUMPROOT/$TAG/$PIECE/r2_clusters_premerge.ply" ] && R2=1
  [ -f "$DUMPROOT/$TAG/$PIECE/r3_after_merge.ply" ] && R3=1
  [ -f "$DUMPROOT/$TAG/$PIECE/r4_after_reassign.ply" ] && R4=1
  [ -f "$DUMPROOT/$TAG/$PIECE/r5_write.ply" ] && R5=1
fi
RDIR=no; [ -d "$DUMPROOT/$TAG" ] && RDIR=yes
STRAY=$(find "$CELL" -name "r[1-5]_*" 2>/dev/null | wc -l)
STAGEDUMPDIR=$(find "$ST" -type d -name "dump" 2>/dev/null | wc -l)

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

printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
  "$TAG" "$PIECE" "$POT" "$ARM" "$DUMP_ENV_LABEL" "$DUMPENV" "$MS" "$EL" "$DUMPS" "$R1" "$R2" "$R3" "$R4" "$R5" \
  "$RDIR" "$STRAY" "$STAGEDUMPDIR" "$DUMPWROTE" "$DUMPREF" "$S0" "$S1" "$OUTCOME" "$CLUSTERS" \
  >> "$CELLROOT/cells25.tsv"
printf "%s\t%s\t%s\t%s\t%s\t%s\n" "$TAG" "$PIECE" "$MS" "$EL" "$DUMPS" "$S0/$S1" >> "$CELLROOT/extra25.tsv"
echo "[CELL] $TAG $POT/$PIECE arm=$ARM exit=$MS elapsed=${EL}s dumps=$DUMPS rungs=$R1$R2$R3$R4$R5 dumproot=$RDIR stray=$STRAY wrote=$DUMPWROTE refused=$DUMPREF outcome=$OUTCOME clusters=$CLUSTERS sizes=$SIZES surf=$S0/$S1 pts=$S0P/$S1P single=${SINGLEL}"
echo "[CELLROW] $TAG\t$PIECE\t$MS\t$S0\t$S1\t$S0P\t$S1P\t$NPTS\t$STATUSL"
