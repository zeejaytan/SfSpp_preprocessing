#!/usr/bin/env bash
# ticket 30: one (arm, piece) pipeline cell on the shipped binary -- the mesh stage with
# SFS_PAPER_THETA set to this arm's theta and nothing else changed, then our own edgeline
# stage on the surfaces it wrote, so the piece has a Breakline_0 to count.
# usage: run_arm30.sh <tag>
# env: CELLROOT POT PIECE AXIS BIN EDGEBIN SIF APT STAGER MESH COMMIT THETA ROLE
# keeps: surfaces/*.ply and *.xyz (re-measured by measure_pair30.py), breaklines/,
#        logs/, one row in armcells30.tsv and one row per Breakline in breaks30.tsv.
# deletes: the staged tree and the edgestage, with a counted record per extension.
set -uo pipefail
TAG=${1:-}
: "${CELLROOT:?}" "${POT:?}" "${PIECE:?}" "${AXIS:?}" "${BIN:?}" "${EDGEBIN:?}" "${SIF:?}" "${APT:?}" "${STAGER:?}" "${MESH:?}" "${COMMIT:?}" "${THETA:?}"
if [ -z "$TAG" ]; then echo "[CELL] FATAL empty tag: run_arm30.sh <tag>" >&2; exit 9; fi
ROLE=${ROLE:-test}
CELL=$CELLROOT/$TAG/$POT/$PIECE
ST=$CELL/stage
ES=$CELL/edgestage
mkdir -p "$CELL/logs" "$CELL/surfaces" "$CELL/breaklines"
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
      SFS_STATUS_FILE="$STATUS_RAW" SFS_PAPER_THETA="$THETA" "$BIN" ) >> "$LOG" 2>&1
  MS=$?
else
  echo "[CELL] stage failed for $POT/$PIECE tag=$TAG stage_exit=$SS" >> "$LOG"
fi
T1=$(date +%s); EL=$((T1-T0))

grep -E "\[(STATUS|RETRY|SINGLE|SWITCH|FLOOR)-23\]|\[(SPACING|COUNT)-22\]|\[REASSIGN-22\]|\[PAPER-234\]|\[DUMP-25\]|\[WINDOW-26\]|Warning: Source file not found|Normals flipped" \
  "$LOG" > "$CELL/logs/lines30.log" 2>/dev/null || true

fld() { grep -m1 "\[STATUS-23\]" "$LOG" 2>/dev/null | tr " " "\n" | grep -m1 "^$1=" | cut -d= -f2- ; }
OUTCOME=$(fld outcome); [ -z "${OUTCOME:-}" ] && OUTCOME=NA
NPTS=$(fld npts);       [ -z "${NPTS:-}" ] && NPTS=NA
S0P=$(fld surf0_points); [ -z "${S0P:-}" ] && S0P=NA
S1P=$(fld surf1_points); [ -z "${S1P:-}" ] && S1P=NA
CLUSTERS=$(fld clusters); [ -z "${CLUSTERS:-}" ] && CLUSTERS=NA
SIZES=$(grep -m1 "\[STATUS-23\]" "$LOG" 2>/dev/null | tr " " "\n" | grep -m1 "^sizes=" | cut -d= -f2-); [ -z "${SIZES:-}" ] && SIZES=none

# every <piece>_* file the mesh stage left in Temp/Data/<pot>/ is kept: the two surfaces the
# edgeline pass walks, <piece>_SampledWithNormals.ply and <piece>_unclustered.ply, which
# edgeline_extraction_headless.cpp:1273 loads (its KD-tree at :1275 dies without it).
N0=0; N1=0; UNC=-1
: > "$CELL/logs/kept_inputs.txt"
for f in "$ST/Temp/Data/$POT/${PIECE}"_*; do
  [ -f "$f" ] || continue
  cp -f "$f" "$CELL/surfaces/"
  printf "%s\t%s\n" "$(basename "$f")" "$(wc -c < "$f")" >> "$CELL/logs/kept_inputs.txt"
done
for k in 0 1; do
  p=$CELL/surfaces/${PIECE}_Surface_$k.ply
  if [ -f "$p" ]; then
    n=$(grep -m1 '^element vertex' "$p" | awk '{print $3}')
    eval "N$k=${n:-0}"
  fi
done
if [ -f "$CELL/surfaces/${PIECE}_unclustered.ply" ]; then
  UNC=$(grep -m1 '^element vertex' "$CELL/surfaces/${PIECE}_unclustered.ply" | awk '{print $3}')
fi

if [ -d "$ST" ]; then
  find "$ST" -type f -printf "%f\t%s\n" 2>/dev/null | awk -F'\t' -v k="$TAG/$POT/$PIECE/stage" '{
      n=split($1,a,"."); ext=(n>1)?a[n]:"(noext)";
      cnt[ext]++; byt[ext]+=$2 }
    END { for (e in cnt) printf "%s\t%s\t%d\t%d\n", k, e, cnt[e], byt[e] }' >> "$CELLROOT/geometry_counts.tsv"
  rm -rf "$ST"
fi

# our edgeline stage: Breakline_0 on the interior face is the line the assembler reads
EX=-1; XEL=0
if [ -f "$CELL/surfaces/${PIECE}_Surface_0.xyz" ] || [ -f "$CELL/surfaces/${PIECE}_Surface_1.xyz" ]; then
  rm -rf "$ES"
  mkdir -p "$ES/Dataset/Axes" "$ES/Dataset/Mesh/$POT" "$ES/Dataset/Surfaces/$POT" \
           "$ES/Dataset/Breaklines/$POT" "$ES/Temp/Data/$POT" "$ES/Temp/Temp_edge/$POT" \
           "$ES/Temp/Temp/$POT" "$ES/Segments"
  for f in "$CELL/surfaces/${PIECE}"_*; do
    [ -f "$f" ] || continue
    cp -f "$f" "$ES/Temp/Data/$POT/"
  done
  ln -s "$MESH" "$ES/Temp/Data/$POT/${PIECE}_Mesh.obj"
  cp -f "$AXIS" "$ES/Dataset/Axes/${PIECE}_Axis.xyz"
  ELOG=$CELL/logs/edge.log
  : > "$ELOG"
  E0=$(date +%s)
  ( cd "$ES" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" "$EDGEBIN" ) >> "$ELOG" 2>&1
  EX=$?
  E1=$(date +%s); XEL=$((E1-E0))
  for f in "$ES/Dataset/Breaklines/$POT"/*; do
    [ -f "$f" ] || continue
    cp -f "$f" "$CELL/breaklines/"
  done
  if [ -d "$ES" ]; then
    find "$ES" -type f -printf "%f\t%s\n" 2>/dev/null | awk -F'\t' -v k="$TAG/$POT/$PIECE/edgestage" '{
        n=split($1,a,"."); ext=(n>1)?a[n]:"(noext)";
        cnt[ext]++; byt[ext]+=$2 }
      END { for (e in cnt) printf "%s\t%s\t%d\t%d\n", k, e, cnt[e], byt[e] }' >> "$CELLROOT/geometry_counts.tsv"
    rm -rf "$ES"
  fi
else
  echo "[EDGE] tag=$TAG pot=$POT piece=$PIECE skipped=no-surface" >> "$CELL/logs/edge.log"
fi

B0=0; B0SEG=0
for f in "$CELL/breaklines"/*_Breakline_*.pcd; do
  [ -f "$f" ] || continue
  b=$(basename "$f")
  sk=$(echo "$b" | sed -e 's/.*_Breakline_\([01]\)\.pcd$/\1/')
  pts=$(grep -m1 '^POINTS' "$f" | awk '{print $2}')
  # the PCD's first comment is the format line; the SECOND carries "<segs> <span> <flag>",
  # then one "# <start> <end> <flag>" line per segment. Parsing the first line read ".PCD"/"v0.7".
  segs=$(grep '^#' "$f" | sed -n '2p' | awk '{print $2}')
  hpts=$(grep '^#' "$f" | sed -n '2p' | awk '{print $3}')
  xf="${f%.pcd}.xyz"
  if [ -f "$xf" ]; then xl=$(wc -l < "$xf"); else xl=0; fi
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$TAG" "$POT" "$PIECE" "$sk" "$b" "${pts:-0}" "${segs:-0}" "${hpts:-0}" "$xl" >> "$CELLROOT/breaks30.tsv"
  if [ "$sk" = "0" ]; then B0=${pts:-0}; B0SEG=${segs:-0}; fi
done

printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
  "$ROLE" "$TAG" "$TAG" "$POT" "$PIECE" "$COMMIT" "$THETA" "$SS" "$MS" "$EX" "$EL" "$OUTCOME" \
  "$N0" "$N1" "$NPTS" "$UNC" "$CLUSTERS" "$SIZES" "$S0P" "$S1P" "$B0" "$B0SEG" "$XEL" >> "$CELLROOT/armcells30.tsv"
echo "[CELL] tag=$TAG role=$ROLE theta=$THETA $POT/$PIECE stage=$SS mesh=$MS edge=$EX elapsed=${EL}s outcome=$OUTCOME surf0=$N0 surf1=$N1 npts=$NPTS unclustered=$UNC clusters=$CLUSTERS break0=$B0/$B0SEG"
