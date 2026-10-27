#!/usr/bin/env bash
# ticket 30: one (arm, piece) dump cell. The nine clouds ticket 29 measured were deleted when
# that ticket closed, so they are re-derived here with SFS_DUMP_STAGE set, as stage25 did it,
# and the rung-2 cloud is what parts A and B are measured on: those normals are the normals the
# surface growth read.
# usage: run_dump30.sh <tag>            tag = PA | B | E
# env: CELLROOT DUMPROOT POT PIECE AXIS BIN SIF APT STAGER COMMIT
# keeps: out/dump/<tag>/<piece>/ (the deliverable), surfaces/, the [..] log lines, one row per
#        cell in cells30.tsv; deletes the staged tree with a counted record per extension.
set -uo pipefail
TAG=$1
: "${CELLROOT:?}" "${DUMPROOT:?}" "${POT:?}" "${PIECE:?}" "${AXIS:?}" "${BIN:?}" "${SIF:?}" "${APT:?}" "${STAGER:?}" "${COMMIT:?}"
CELL=$CELLROOT/$TAG/$PIECE
ST=$CELL/stage
mkdir -p "$CELL/logs" "$CELL/surfaces"
STATUS_RAW=$CELL/status_raw.tsv
: > "$STATUS_RAW"

case "$TAG" in
  PA) DUMPENV="SFS_DUMP_STAGE=$DUMPROOT/PA SFS_DUMP_PIECES=$PIECE"; SCHEME="defaults" ;;
  B)  DUMPENV="SFS_DUMP_STAGE=$DUMPROOT/B SFS_DUMP_PIECES=$PIECE"; SCHEME="defaults" ;;
  E)  DUMPENV="SFS_DUMP_STAGE=$DUMPROOT/E SFS_DUMP_PIECES=$PIECE SFS_PAPER_CHAIN=0 SFS_DOWNSAMPLE_TARGET=-1"; SCHEME="chain0-raw" ;;
  *)  echo "[CELL] FATAL unknown tag $TAG"; exit 3 ;;
esac

T0=$(date +%s)
bash "$STAGER" "$ST" "$POT" "$PIECE" "$AXIS" > "$CELL/logs/stage.log" 2>&1
SS=$?
LOG=$CELL/logs/mesh.log
: > "$LOG"
MS=99
if [ "$SS" -eq 0 ]; then
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" \
      SFS_AXIS_FILE="$ST/Dataset/Axes/${PIECE}_Axis.xyz" SFS_STATUS_FILE="$STATUS_RAW" \
      $DUMPENV "$BIN" ) >> "$LOG" 2>&1
  MS=$?
else
  echo "[CELL] stage failed for $POT/$PIECE tag=$TAG stage_exit=$SS" >> "$LOG"
fi
T1=$(date +%s); EL=$((T1 - T0))

grep -E "\[(WINDOW-26|RETRY-23|SINGLE-23|STATUS-23|SWITCH-23|FLOOR-23|SPACING-22|COUNT-22|REASSIGN-22|PAPER-234|DUMP-25)\]|Warning: Source file not found|Normals flipped" \
  "$LOG" > "$CELL/logs/lines30.log" 2>/dev/null || true

fld() { grep -m1 "\[STATUS-23\]" "$LOG" 2>/dev/null | tr " " "\n" | grep -m1 "^$1=" | cut -d= -f2- ; }
OUTCOME=$(fld outcome); [ -z "${OUTCOME:-}" ] && OUTCOME=NA
NPTS=$(fld npts); [ -z "${NPTS:-}" ] && NPTS=NA
S0P=$(fld surf0_points); [ -z "${S0P:-}" ] && S0P=NA
S1P=$(fld surf1_points); [ -z "${S1P:-}" ] && S1P=NA
CLUSTERS=$(fld clusters); [ -z "${CLUSTERS:-}" ] && CLUSTERS=NA
SIZES=$(grep -m1 "\[STATUS-23\]" "$LOG" 2>/dev/null | tr " " "\n" | grep -m1 "^sizes=" | cut -d= -f2-); [ -z "${SIZES:-}" ] && SIZES=none

S0=no; S1=no; N0=0; N1=0
for k in 0 1; do
  src=$ST/Temp/Data/$POT/${PIECE}_Surface_$k.ply
  if [ -f "$src" ]; then
    cp -f "$src" "$CELL/surfaces/${PIECE}_Surface_$k.ply"
    if [ -f "$ST/Temp/Data/$POT/${PIECE}_Surface_$k.xyz" ]; then
      cp -f "$ST/Temp/Data/$POT/${PIECE}_Surface_$k.xyz" "$CELL/surfaces/"
    fi
    n=$(grep -m1 '^element vertex' "$src" | awk '{print $3}' | tr -d '\n')
    eval "S$k=yes"; eval "N$k=${n:-0}"
  fi
done

UNC=-1
UNCP=$ST/Temp/Data/$POT/${PIECE}_unclustered.ply
if [ -f "$UNCP" ]; then UNC=$(grep -m1 '^element vertex' "$UNCP" | awk '{print $3}'); [ -z "${UNC:-}" ] && UNC=-1; fi

if [ -d "$DUMPROOT/$TAG/$PIECE" ]; then
  for f in "$DUMPROOT/$TAG/$PIECE"/*.ply; do
    [ -f "$f" ] || continue
    printf "%s\t%s\t%s\t%s\t%s\t%s\n" "$TAG" "$POT" "$PIECE" "$(basename "$f")" \
      "$(grep -m1 '^element vertex' "$f" | awk '{print $3}')" "$(wc -c < "$f")" >> "$CELLROOT/dumpcounts30.tsv"
  done
fi

if [ -d "$ST" ]; then
  find "$ST" -type f -printf "%f\t%s\n" 2>/dev/null | awk -F"\t" -v c="$TAG/$POT/$PIECE" '{
      n = split($1, a, "."); e = (n > 1 ? a[n] : "none");
      if (e == "pcd" || e == "ply" || e == "xyz" || e == "obj") f = e; else f = "other";
      cnt[f]++; byt[f] += $2 }
    END { for (k in cnt) printf "%s\t%s\t%d\t%d\n", c, k, cnt[k], byt[k] }' >> "$CELLROOT/geometry_counts.tsv"
  rm -rf "$ST"
fi

if [ -s "$STATUS_RAW" ]; then
  awk -v a="$TAG" -v p="$POT" 'BEGIN{OFS="\t"} {print a,p,$0}' "$STATUS_RAW" >> "$CELLROOT/status30.tsv"
else
  printf "%s\t%s\t%s\tNO_STATUS_ROW\n" "$TAG" "$POT" "$PIECE" >> "$CELLROOT/status30.tsv"
fi

printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
  "$TAG" "$SCHEME" "$POT" "$PIECE" "$COMMIT" "$SS" "$MS" "$EL" "$OUTCOME" "$N0" "$N1" "$NPTS" "$UNC" "$CLUSTERS" "$SIZES" "$S0P/$S1P" \
  >> "$CELLROOT/cells30.tsv"
echo "[CELL] tag=$TAG scheme=$SCHEME $POT/$PIECE stage=$SS mesh=$MS elapsed=${EL}s outcome=$OUTCOME surf0=$S0($N0) surf1=$S1($N1) npts=$NPTS unclustered=$UNC clusters=$CLUSTERS sizes=$SIZES"
