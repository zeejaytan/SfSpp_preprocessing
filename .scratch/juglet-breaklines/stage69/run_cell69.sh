#!/bin/bash
# run_cell69.sh -- ticket 69. run_cell66.sh restructured so that ONE mesh stage feeds TWO
# edge stages: the shipped sphere walk (1.8 mm) and the densified one (0.9 mm).
#
# Why: the mesh stage draws 30 random ray-cast points from an unseeded generator
# (mesh_processing_headless.cpp:1526-1527), so two full-chain runs on the same cloud are NOT
# the same input. Varying only the edgeline constants on one staged surface pair is the only
# clean density comparison, and it also makes the two lanes a PAIRED measurement of a piece.
#
# Each arm runs in its own FRESH copy of the post-mesh-stage snapshot, so the second arm
# cannot read anything the first arm wrote (Temp/Temp_edge/ and Dataset/Surfaces/ are
# scratch). The snapshot is taken once, after the mesh stage.
#
# Env: POT_NAME PIECES WORNESS MESH_ENV CLOUD_DIR MESH_DIR AXIS_DIR MANIFEST
#      MAN_MD5_COL MAN_PTS_COL (as run_cell66.sh), plus
#      E18   extra env for the shipped edge stage   (default: empty = shipped defaults)
#      E09   extra env for the densified edge stage (default: SFS_SPHERE_RADIUS_MM=0.9 SFS_RESAMPLE_D_MM=0.95)
#      STAGER PY OUT DS CORP MESH_BIN EDGE_BIN APT SIF RUN JOBID
# Pass 1 is the ticket-48 corpus-manifest gate, unchanged: md5 AND point count of every cloud
# must equal the manifest, and no *_covering.pcd may sit under the corpus Point trees.
set -uo pipefail

POT_NAME=${POT_NAME:-Juglet}
POT=$POT_NAME
PIECES=${PIECES:?}
WORNESS=${WORNESS-}
MESH_ENV=${MESH_ENV:-}
E18=${E18-}
E09=${E09-SFS_SPHERE_RADIUS_MM=0.9 SFS_RESAMPLE_D_MM=0.95}

: "${STAGER:?}" "${PY:?}" "${OUT:?}" "${DS:?}" "${CORP:?}" "${MESH_BIN:?}" "${EDGE_BIN:?}" "${APT:?}" "${SIF:?}" "${RUN:?}" "${JOBID:?}"
CLOUD_DIR=${CLOUD_DIR:-$DS/Point/$POT}
MESH_DIR=${MESH_DIR:-$DS/Mesh/$POT}
AXIS_DIR=${AXIS_DIR:-$DS/Axes/$POT}
MANIFEST=${MANIFEST:?}
MAN_MD5_COL=${MAN_MD5_COL:-md5}
MAN_PTS_COL=${MAN_PTS_COL:-points}
[ -f "$MANIFEST" ] || { echo "[CELL69] FATAL no manifest at $MANIFEST"; exit 7; }
unset POT_NAME

mkdir -p "$OUT/geom18" "$OUT/geom09" "$OUT/pieces" "$OUT/stages" || exit 7

log() { echo "[CELL69] $*"; }
pcd_points() { grep -am1 "^POINTS" "$1" | awk '{print $2}'; }
manifest_field() {
  awk -F"\t" -v piece="$1" -v fld="$2" '
    /^#/ { next }
    !seen { for (i=1;i<=NF;i++) col[$i]=i; want=col[fld]; key=col["piece"]; seen=1; next }
    want && key && $key==piece { print $want; exit }
  ' "$MANIFEST"
}

# ------------------------------------------------- pass 1: the corpus-manifest gate
GATE=$OUT/corpus_gate.tsv
printf "piece\tpot\tcloud\tcloud_points\tcloud_md5\tmesh\tmesh_md5\tmanifest_pcd_md5\tmanifest_kept_points\tgate\tnote\n" > "$GATE"
GATE_FAILED=""
for P in $PIECES; do
  MESH=$(ls "$MESH_DIR/${P}_Mesh.obj" "$MESH_DIR/${P}_Mesh_DS.obj" 2>/dev/null | head -1)
  CLOUD=$CLOUD_DIR/${P}_Point.pcd
  AXIS=$AXIS_DIR/${P}_Axis.xyz
  G=ok
  [ -f "$MESH" ]  || { log "FATAL missing mesh $MESH"; G=FAILED; GATE_FAILED="$GATE_FAILED $P/mesh"; }
  [ -f "$CLOUD" ] || { log "FATAL missing cloud $CLOUD"; G=FAILED; GATE_FAILED="$GATE_FAILED $P/cloud"; }
  [ -f "$AXIS" ]  || { log "FATAL missing axis $AXIS"; G=FAILED; GATE_FAILED="$GATE_FAILED $P/axis"; }
  SYNN=$(pcd_points "$CLOUD" 2>/dev/null)
  [ -n "$SYNN" ]  || { log "FATAL no point count for $P"; G=FAILED; GATE_FAILED="$GATE_FAILED $P/npts"; }
  SHMD5=$(md5sum "$CLOUD" 2>/dev/null | cut -d" " -f1)
  MMMD5=$(md5sum "$MESH" 2>/dev/null | cut -d" " -f1)
  MMD5=$(manifest_field "$P" "$MAN_MD5_COL")
  MKEPT=$(manifest_field "$P" "$MAN_PTS_COL")
  if [ -z "$MMD5" ]; then
    log "FATAL $P not in manifest $MANIFEST"; G=FAILED; GATE_FAILED="$GATE_FAILED $P/not-in-manifest"
  elif [ "$SHMD5" != "$MMD5" ]; then
    log "FATAL corpus md5 moved on $P: disk=$SHMD5 manifest=$MMD5"; G=FAILED; GATE_FAILED="$GATE_FAILED $P/md5"
  fi
  if [ -n "$MKEPT" ] && [ -n "$SYNN" ] && [ "$MKEPT" != "$SYNN" ]; then
    log "FATAL $P point count disagrees: pcd=$SYNN manifest $MAN_PTS_COL=$MKEPT"; G=FAILED; GATE_FAILED="$GATE_FAILED $P/count"
  fi
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$P" "$POT" "$CLOUD" "${SYNN:-na}" "$SHMD5" "$MESH" "$MMMD5" "${MMD5:-na}" "${MKEPT:-na}" "$G" "corpus cloud == $(basename "$MANIFEST")" >> "$GATE"
  log "corpus gate $P: ${SYNN:-na} points, md5 ${SHMD5:0:8} vs manifest ${MMD5:-absent} -> $G"
done

SWEEP=$OUT/corpus_covering_sweep.txt
find "$DS/Point" "$CORP/Point" -name "*_covering.pcd" 2>/dev/null | sort > "$SWEEP" || true
SWN=$(wc -l < "$SWEEP" | tr -d " ")
if [ "$SWN" -ne 0 ]; then
  log "FATAL $SWN covering artifact(s) under the corpus Point trees:"; cat "$SWEEP"
  GATE_FAILED="$GATE_FAILED corpus-covering-artifacts"
fi
cat "$GATE"
if [ -n "$GATE_FAILED" ]; then
  log "STOP: the corpus-manifest gate did not pass:$GATE_FAILED"
  log "no piece was run -- an unverified corpus is never measured"
  exit 9
fi
log "corpus verified against $MANIFEST; the pieces may run"

# ---------------------------------------------------------------- pass 2: the pieces
FAILED=""
SUM=$OUT/pieces69.tsv
printf "piece\tpot\tsurf0_points\tsurf1_points\tbl0_18\tbl1_18\tbl0_09\tbl1_09\tmesh_rc\tedge18_rc\tedge09_rc\tclassify\tstatus\tnote\n" > "$SUM"
emit_row() {
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$1" "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9" "${10}" "${11}" "${12}" "${13}" "${14}" >> "$SUM"
}
WENV=""
[ -n "$WORNESS" ] && WENV="SFS_WORNESS=$WORNESS"

for P in $PIECES; do
  unset SFS_AXIS_FILE SFS_STATUS_FILE SFS_WORNESS SFS_PAPER_THETA SFS_PAPER_KAPPA \
        SFS_GROWTH_MODE SFS_GROWTH_FORMULA SFS_GROWTH_CAP SFS_GROWTH_WALK POT_NAME 2>/dev/null || true

  CELL=$OUT/pieces/$P
  ST=$OUT/stages/stage_$P
  SNAP=$OUT/stages/snap_$P
  mkdir -p "$CELL"
  log "=============================================================="
  log "piece $P  pot=$POT  worness=${WORNESS:-unset} mesh_env=[${MESH_ENV}] E18=[${E18}] E09=[${E09}]"

  CLOUD=$CLOUD_DIR/${P}_Point.pcd
  AXIS=$AXIS_DIR/${P}_Axis.xyz

  MESH_DIR_69=$MESH_DIR bash "$STAGER" "$ST" "$POT" "$P" "$AXIS" "$CLOUD" REAL-RELEASED-CLOUD > "$CELL/stage.log" 2>&1
  SRC=$?
  if [ "$SRC" -ne 0 ]; then
    log "FATAL stage failed rc=$SRC for $P (see $CELL/stage.log)"
    emit_row "$P" "$POT" - - - - - - - - - - - FAILED "stage rc=$SRC"
    FAILED="$FAILED $P/stage"; continue
  fi
  cp -f "$ST/inputs.md5" "$CELL/inputs.md5"

  LOG=$CELL/mesh.log
  # shellcheck disable=SC2086
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" \
      SFS_AXIS_FILE="$ST/Dataset/Axes/${P}_Axis.xyz" \
      SFS_STATUS_FILE="$CELL/status_raw.tsv" \
      $WENV $MESH_ENV "$MESH_BIN" ) > "$LOG" 2>&1
  MRC=$?
  log "mesh rc=$MRC log=$(stat -c %s "$LOG" 2>/dev/null || echo 0) bytes"
  CLS=$(grep -am1 "PAPER-234] classify: face0" "$LOG" | tr -d "\r" || true)
  STLINE=$(grep -am1 "\[STATUS-23\]" "$LOG" | tr -d "\r" || true)
  S0P=""; S1P=""
  if [ -n "$STLINE" ]; then
    S0P=$(printf "%s\n" "$STLINE" | sed -n "s/.*surf0_points=\([^ ]*\).*/\1/p")
    S1P=$(printf "%s\n" "$STLINE" | sed -n "s/.*surf1_points=\([^ ]*\).*/\1/p")
  fi
  log "classify: ${CLS:-MISSING}"
  log "status  : ${STLINE:-MISSING}"

  # export S0/S1 once -- BOTH arms read these same two files
  S0EXT=""; S1EXT=""
  for K in 0 1; do
    F=""; FE=""
    for ext in ply xyz; do
      if [ -f "$ST/Temp/Data/$POT/${P}_Surface_${K}.${ext}" ]; then
        F=$ST/Temp/Data/$POT/${P}_Surface_${K}.${ext}; FE=$ext; break
      fi
    done
    if [ -n "$F" ]; then
      cp -f "$F" "$OUT/geom18/${P}.S${K}"
      cp -f "$F" "$OUT/geom09/${P}.S${K}"
      if [ "$K" -eq 0 ]; then S0EXT=$FE; else S1EXT=$FE; fi
      log "surface $K: $FE -> geom18/geom09 ${P}.S${K} ($(stat -c %s "$F" 2>/dev/null || echo 0) bytes)"
    else
      log "surface $K: the pipeline wrote none"
    fi
  done

  # snapshot the post-mesh-stage tree ONCE; every arm gets its own copy of it
  rm -rf "$SNAP"; cp -a "$ST" "$SNAP"
  log "snapshot $(du -sh "$SNAP" | cut -f1) at $SNAP"
  rm -rf "$ST"

  B018=""; B118=""; B009=""; B109=""; E18RC=0; E09RC=0
  for ARM in 18 09; do
    if [ "$ARM" = 18 ]; then AENV="$E18"; GD=geom18; else AENV="$E09"; GD=geom09; fi
    AST=$OUT/stages/arm${ARM}_$P
    rm -rf "$AST"; cp -a "$SNAP" "$AST"
    rm -rf "$AST/Dataset/Breaklines/$POT"; mkdir -p "$AST/Dataset/Breaklines/$POT"
    ELOG=$CELL/edge$ARM.log
    # shellcheck disable=SC2086
    ( cd "$AST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" $AENV "$EDGE_BIN" ) > "$ELOG" 2>&1
    ERC=$?
    log "edge$ARM rc=$ERC env=[$AENV] log=$(stat -c %s "$ELOG" 2>/dev/null || echo 0) bytes"
    grep -am2 "SPHERE-69\|RESAMPLE-69" "$ELOG" | tr -d "\r" | sed "s/^/[CELL69]   /" || true
    for K in 0 1; do
      BF=$AST/Dataset/Breaklines/$POT/${P}_Breakline_${K}.pcd
      if [ -f "$BF" ]; then
        cp -f "$BF" "$OUT/$GD/${P}.Bl${K}"
        BN=$(pcd_points "$BF")
        log "breakline $ARM/$K: ${BN:-?} points -> $GD/${P}.Bl${K}"
        if [ "$ARM" = 18 ]; then
          if [ "$K" -eq 0 ]; then B018=$BN; else B118=$BN; fi
        else
          if [ "$K" -eq 0 ]; then B009=$BN; else B109=$BN; fi
        fi
      else
        log "breakline $ARM/$K: the pipeline wrote none"
      fi
    done
    printf "%s\t%s\t%s\n" "$ARM" "$ERC" "$AENV" >> "$CELL/edge_rc.tsv"
    rm -rf "$AST"
    if [ "$ARM" = 18 ]; then E18RC=$ERC; else E09RC=$ERC; fi
  done
  rm -rf "$SNAP"

  {
    printf 'piece\t%s\n' "$P"
    printf 'pot\t%s\n' "$POT"
    printf 'mesh_rc\t%s\n' "$MRC"
    printf 'classify_line\t%s\n' "$CLS"
    printf 'status_line\t%s\n' "$STLINE"
    printf 'surf0_points\t%s\n' "$S0P"
    printf 'surf1_points\t%s\n' "$S1P"
    printf 'bl0_18\t%s\n' "${B018:-}"
    printf 'bl1_18\t%s\n' "${B118:-}"
    printf 'bl0_09\t%s\n' "${B009:-}"
    printf 'bl1_09\t%s\n' "${B109:-}"
    printf 'surface_ext\tS0=%s,S1=%s\n' "${S0EXT:-none}" "${S1EXT:-none}"
  } > "$CELL/cell.tsv"

  NOTE=""
  [ "$MRC" -ne 0 ] && NOTE="$NOTE mesh_rc=$MRC"
  [ "$E18RC" -ne 0 ] && NOTE="$NOTE edge18_rc=$E18RC"
  [ "$E09RC" -ne 0 ] && NOTE="$NOTE edge09_rc=$E09RC"
  [ -z "$CLS" ] && NOTE="$NOTE no-classify-line(t277)"
  [ -z "$S0EXT" ] && NOTE="$NOTE no-S0"
  [ -z "$S1EXT" ] && NOTE="$NOTE no-S1"
  [ -z "$B018" ] && NOTE="$NOTE no-Bl0@18"
  [ -z "$B118" ] && NOTE="$NOTE no-Bl1@18"
  [ -z "$B009" ] && NOTE="$NOTE no-Bl0@09"
  [ -z "$B109" ] && NOTE="$NOTE no-Bl1@09"
  STT=ok
  [ -n "$NOTE" ] && { STT=FAILED; FAILED="$FAILED $P"; }
  CLSQ=yes; [ -z "$CLS" ] && CLSQ=MISSING
  emit_row "$P" "$POT" "${S0P:--}" "${S1P:--}" "${B018:--}" "${B118:--}" "${B009:--}" "${B109:--}" \
    "$MRC" "$E18RC" "$E09RC" "$CLSQ" "$STT" "${NOTE:-both densities exported}"
done

log "=== every piece, as recorded ==="
cat "$SUM"
if [ -n "$FAILED" ]; then log "FAILED:$FAILED"; exit 8; fi
log "all pieces ran with both densities exported"
log done
