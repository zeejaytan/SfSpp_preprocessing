#!/bin/bash
# ticket 55 -- all nine Juglet pieces through the SHIPPED chain at the conservator's
# recommended dial SFS_WORNESS=0.7: mesh stage (two surfaces per piece) then the edge-line
# stage, exporting the bundle out/geom/<P>.{S0,S1,Bl0,Bl1} that the future assembly ticket
# consumes.  ONE arm, no env probe, no D/X/W arms (ticket 54 measured the dial; this runs it).
# Pass 1 is the ticket-48 CORPUS-MANIFEST GATE (identical to t54 pass 1, Juglet only):
# md5 AND kept_points of every Juglet corpus cloud must equal MANIFEST_JUGLET_CC.tsv, and no
# *_covering.pcd may sit under the corpus Point trees.
# Per piece: stage (STAGER) -> mesh stage, REQUIRED log lines '[PAPER-234] classify: face0'
# (ticket 277 gate) and '[WORNESS-54] piece=' with theta -- a piece missing either is a
# FAILED cell, reported, never dropped -> export S0/S1 (either ext; PLY header length varies,
# so only size+md5 are recorded, never parsed) -> rm -rf the staged Breaklines -> edge stage
# (POT_NAME only, p298 pattern) -> export Bl0/Bl1 -> count the stage, then delete it (the
# out/geom bundle IS kept).
# Paid-for traps named on purpose (inherited from 44/45/46/48/51/53/54): CRLF in a script;
# unbound variables under set -u; a FAILED row must carry the SAME field count as the header
# (12 and 12 here); no xargs -d anywhere; grep -a on binary PLY/PCD; PLY header length varies;
# every SFS_* (and POT_NAME) unset between pieces.
set -uo pipefail

PIECES=${PIECES:-"Juglet_Piece_1 Juglet_Piece_2 Juglet_Piece_3 Juglet_Piece_4 Juglet_Piece_5 Juglet_Piece_6 Juglet_Piece_7 Juglet_Piece_8 Juglet_Piece_9"}
WORNESS=${WORNESS:-0.7}

: "${INSTR:?}" "${PY:?}" "${OUT:?}" "${DS:?}" "${CORP:?}" "${MESH_BIN:?}" "${EDGE_BIN:?}" "${APT:?}" "${SIF:?}" "${STAGER:?}" "${RUN:?}" "${JOBID:?}"
MANIFEST=$DS/Point/Juglet/MANIFEST_JUGLET_CC.tsv
[ -f "$MANIFEST" ] || { echo "[CELL55] FATAL no manifest at $MANIFEST"; exit 7; }

mkdir -p "$OUT/geom" "$OUT/pieces" "$OUT/stages" || exit 7

log() { echo "[CELL55] $*"; }
pcd_points() { grep -am1 "^POINTS" "$1" | awk '{print $2}'; }
manifest_field() {
  awk -F"\t" -v piece="$1" -v fld="$2" '
    /^#/ { next }
    !seen { for (i=1;i<=NF;i++) col[$i]=i; want=col[fld]; seen=1; next }
    want && $1==piece { print $want; exit }
  ' "$MANIFEST"
}

# ------------------------------------------------- pass 1: the corpus-manifest gate
GATE=$OUT/corpus_gate.tsv
printf "piece\tpot\tcloud\tcloud_points\tcloud_md5\tmesh\tmesh_md5\tmanifest_pcd_md5\tmanifest_kept_points\tmanifest_spacing_mm\tgate\tnote\n" > "$GATE"
GATE_FAILED=""
for P in $PIECES; do
  MESH=$DS/Mesh/Juglet/${P}_Mesh.obj
  CLOUD=$DS/Point/Juglet/${P}_Point.pcd
  AXIS=$DS/Axes/Juglet/${P}_Axis.xyz
  G=ok
  [ -f "$MESH" ]  || { log "FATAL missing mesh $MESH"; G=FAILED; GATE_FAILED="$GATE_FAILED $P/mesh"; }
  [ -f "$CLOUD" ] || { log "FATAL missing cloud $CLOUD"; G=FAILED; GATE_FAILED="$GATE_FAILED $P/cloud"; }
  [ -f "$AXIS" ]  || { log "FATAL missing axis $AXIS"; G=FAILED; GATE_FAILED="$GATE_FAILED $P/axis"; }
  SYNN=$(pcd_points "$CLOUD" 2>/dev/null)
  [ -n "$SYNN" ]  || { log "FATAL no point count for $P"; G=FAILED; GATE_FAILED="$GATE_FAILED $P/npts"; }
  SHMD5=$(md5sum "$CLOUD" 2>/dev/null | cut -d" " -f1)
  MMMD5=$(md5sum "$MESH" 2>/dev/null | cut -d" " -f1)
  MMD5=$(manifest_field "$P" pcd_md5)
  MKEPT=$(manifest_field "$P" kept_points)
  MSPAC=$(manifest_field "$P" spacing_mm)
  if [ -z "$MMD5" ]; then
    log "FATAL $P not in manifest $MANIFEST"; G=FAILED; GATE_FAILED="$GATE_FAILED $P/not-in-manifest"
  elif [ "$SHMD5" != "$MMD5" ]; then
    log "FATAL corpus md5 moved on $P: disk=$SHMD5 manifest=$MMD5"; G=FAILED; GATE_FAILED="$GATE_FAILED $P/md5"
  fi
  if [ -n "$MKEPT" ] && [ -n "$SYNN" ] && [ "$MKEPT" != "$SYNN" ]; then
    log "FATAL $P point count disagrees: pcd=$SYNN manifest kept_points=$MKEPT"; G=FAILED; GATE_FAILED="$GATE_FAILED $P/count"
  fi
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$P" Juglet "$CLOUD" "${SYNN:-na}" "$SHMD5" "$MESH" "$MMMD5" "${MMD5:-na}" "${MKEPT:-na}" "${MSPAC:-na}" "$G" "corpus cloud == ticket-47 manifest" >> "$GATE"
  log "corpus gate $P: ${SYNN:-na} points, md5 ${SHMD5:0:8} vs manifest ${MMD5:-absent} -> $G"
done

SWEEP=$OUT/corpus_covering_sweep.txt
find "$DS/Point" "$CORP/Point" -name "*_covering.pcd" 2>/dev/null | sort > "$SWEEP" || true
SWN=$(wc -l < "$SWEEP" | tr -d " ")
if [ "$SWN" -ne 0 ]; then
  log "FATAL $SWN covering artifact(s) under the corpus Point trees:"
  cat "$SWEEP"
  GATE_FAILED="$GATE_FAILED corpus-covering-artifacts"
fi

cat "$GATE"
if [ -n "$GATE_FAILED" ]; then
  log "STOP: the corpus-manifest gate did not pass:$GATE_FAILED"
  log "no piece was run -- ticket 55 never measures an unverified corpus"
  exit 9
fi
log "corpus verified against the ticket-47 manifest; the pieces may run"

# ---------------------------------------------------------------- pass 2: the pieces
FAILED=""
SUM=$OUT/pieces55.tsv
# 12 columns -- every row (ok or FAILED) carries exactly this count (the t54 trap)
printf "piece\tcapped_theta\tsurf0_points\tsurf1_points\tbl0_points\tbl1_points\tmesh_rc\tedge_rc\tclassify\tworness54_line\tstatus\tnote\n" > "$SUM"
emit_row() { # 12 fields, in header order
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$1" "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9" "${10}" "${11}" "${12}" >> "$SUM"
}

for P in $PIECES; do
  # every SFS_* and POT_NAME unset before each piece (the t54 trap list carries over)
  unset SFS_AXIS_FILE SFS_STATUS_FILE SFS_WORNESS SFS_PAPER_THETA SFS_PAPER_KAPPA \
        SFS_GROWTH_MODE SFS_GROWTH_FORMULA SFS_GROWTH_CAP SFS_GROWTH_WALK POT_NAME 2>/dev/null || true

  CELL=$OUT/pieces/$P
  ST=$OUT/stages/stage_$P
  mkdir -p "$CELL"
  log "=============================================================="
  log "piece $P  (SFS_WORNESS=$WORNESS) stage=$ST"

  MESH=$DS/Mesh/Juglet/${P}_Mesh.obj
  CLOUD=$DS/Point/Juglet/${P}_Point.pcd
  AXIS=$DS/Axes/Juglet/${P}_Axis.xyz

  bash "$STAGER" "$ST" Juglet "$P" "$AXIS" "$CLOUD" REAL-RELEASED-CLOUD > "$CELL/stage.log" 2>&1
  SRC=$?
  if [ "$SRC" -ne 0 ]; then
    log "FATAL stage failed rc=$SRC for $P (see $CELL/stage.log)"
    emit_row "$P" - - - - - - - - - FAILED "stage rc=$SRC"
    FAILED="$FAILED $P/stage"
    continue
  fi
  cp -f "$ST/inputs.md5" "$CELL/inputs.md5"

  # ---- mesh stage: POT_NAME + SFS_AXIS_FILE + SFS_STATUS_FILE + SFS_WORNESS, nothing else
  LOG=$CELL/mesh.log
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME=Juglet \
      SFS_AXIS_FILE="$ST/Dataset/Axes/${P}_Axis.xyz" \
      SFS_STATUS_FILE="$CELL/status_raw.tsv" \
      SFS_WORNESS="$WORNESS" "$MESH_BIN" ) > "$LOG" 2>&1
  MRC=$?
  log "mesh rc=$MRC log=$(stat -c %s "$LOG" 2>/dev/null || echo 0) bytes"

  CLS=$(grep -am1 "PAPER-234] classify: face0" "$LOG" | tr -d "\r" || true)
  G54=$(grep -am1 "\[WORNESS-54\] piece=" "$LOG" | tr -d "\r" || true)
  TH54=""
  [ -n "$G54" ] && TH54=$(printf "%s\n" "$G54" | sed -n "s/.* theta=\([^ ]*\).*/\1/p")
  STLINE=$(grep -am1 "\[STATUS-23\]" "$LOG" | tr -d "\r" || true)
  S0P=""; S1P=""
  if [ -n "$STLINE" ]; then
    S0P=$(printf "%s\n" "$STLINE" | sed -n "s/.*surf0_points=\([^ ]*\).*/\1/p")
    S1P=$(printf "%s\n" "$STLINE" | sed -n "s/.*surf1_points=\([^ ]*\).*/\1/p")
  fi
  log "classify: ${CLS:-MISSING}"
  log "worness : ${G54:-MISSING}"
  log "status  : ${STLINE:-MISSING}"

  # ---- export S0/S1 (either ext, ply first; only size+md5 recorded, never parsed)
  S0EXT=""; S1EXT=""
  for K in 0 1; do
    F=""; FE=""
    for ext in ply xyz; do
      if [ -f "$ST/Temp/Data/Juglet/${P}_Surface_${K}.${ext}" ]; then
        F=$ST/Temp/Data/Juglet/${P}_Surface_${K}.${ext}; FE=$ext; break
      fi
    done
    if [ -n "$F" ]; then
      cp -f "$F" "$OUT/geom/${P}.S${K}"
      if [ "$K" -eq 0 ]; then S0EXT=$FE; else S1EXT=$FE; fi
      log "surface $K: $FE $F -> $OUT/geom/${P}.S${K} ($(stat -c %s "$F" 2>/dev/null || echo 0) bytes)"
    else
      log "surface $K: the pipeline wrote none"
    fi
  done

  # ---- edge stage: the staged Breaklines tree is wiped first; env is POT_NAME ONLY
  rm -rf "$ST/Dataset/Breaklines/Juglet"
  mkdir -p "$ST/Dataset/Breaklines/Juglet"
  ELOG=$CELL/edge.log
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME=Juglet "$EDGE_BIN" ) > "$ELOG" 2>&1
  ERC=$?
  log "edge rc=$ERC log=$(stat -c %s "$ELOG" 2>/dev/null || echo 0) bytes"

  B0N=""; B1N=""
  for K in 0 1; do
    BF=$ST/Dataset/Breaklines/Juglet/${P}_Breakline_${K}.pcd
    if [ -f "$BF" ]; then
      cp -f "$BF" "$OUT/geom/${P}.Bl${K}"
      BN=$(pcd_points "$BF")
      if [ "$K" -eq 0 ]; then B0N=$BN; else B1N=$BN; fi
      log "breakline $K: $BF -> $OUT/geom/${P}.Bl${K} (${BN:-?} points, $(stat -c %s "$BF" 2>/dev/null || echo 0) bytes)"
    else
      log "breakline $K: the pipeline wrote none"
    fi
  done

  # ---- the per-piece record (cell.tsv, the t54 shape)
  {
    printf 'piece\t%s\n' "$P"
    printf 'worness\t%s\n' "$WORNESS"
    printf 'mesh_rc\t%s\n' "$MRC"
    printf 'edge_rc\t%s\n' "$ERC"
    printf 'classify_line\t%s\n' "$CLS"
    printf 'worness54_line\t%s\n' "$G54"
    printf 'worness54_theta\t%s\n' "$TH54"
    printf 'status_line\t%s\n' "$STLINE"
    printf 'surf0_points\t%s\n' "$S0P"
    printf 'surf1_points\t%s\n' "$S1P"
    printf 'bl0_points\t%s\n' "${B0N:-}"
    printf 'bl1_points\t%s\n' "${B1N:-}"
    printf 'surface_ext\tS0=%s,S1=%s\n' "${S0EXT:-none}" "${S1EXT:-none}"
    printf 'geom_S0\t%s\n' "$OUT/geom/${P}.S0"
    printf 'geom_S1\t%s\n' "$OUT/geom/${P}.S1"
    printf 'geom_Bl0\t%s\n' "$OUT/geom/${P}.Bl0"
    printf 'geom_Bl1\t%s\n' "$OUT/geom/${P}.Bl1"
  } > "$CELL/cell.tsv"

  # ---- count the stage, then delete it (counted record; the out/geom bundle IS kept)
  {
    find "$ST" -type f -printf "%p\t%s\n" 2>/dev/null | awk -F"\t" '
      { n=split($1,a,"."); ext=(n>1?a[n]:"none");
        if (ext !~ /^(pcd|ply|xyz|obj|png|json)$/) ext="other";
        files[ext]++; bytes[ext]+=$2; tf++; tb+=$2 }
      END { printf "ext\tfiles\tbytes\n";
            for (e in files) printf "%s\t%d\t%d\n", e, files[e], bytes[e];
            printf "TOTAL\t%d\t%d\n", tf, tb }' | sort
  } > "$CELL/geometry_counts.tsv"
  cat "$CELL/geometry_counts.tsv"
  rm -rf "$ST"
  log "deleted stage $ST after the counted record above (the geom exports in out/geom are KEPT)"

  # ---- the fact row: every required marker and export, or FAILED with the reasons named
  NOTE=""
  [ "$MRC" -ne 0 ] && NOTE="$NOTE mesh_rc=$MRC"
  [ "$ERC" -ne 0 ] && NOTE="$NOTE edge_rc=$ERC"
  [ -z "$CLS" ] && NOTE="$NOTE no-classify-line(t277)"
  [ -z "$G54" ] && NOTE="$NOTE no-WORNESS-54-line"
  [ -z "$S0EXT" ] && NOTE="$NOTE no-S0"
  [ -z "$S1EXT" ] && NOTE="$NOTE no-S1"
  [ -z "$B0N" ] && NOTE="$NOTE no-Bl0"
  [ -z "$B1N" ] && NOTE="$NOTE no-Bl1"
  STT=ok
  [ -n "$NOTE" ] && { STT=FAILED; FAILED="$FAILED $P"; }
  CLSQ=yes; G54Q=yes
  [ -z "$CLS" ] && CLSQ=MISSING
  [ -z "$G54" ] && G54Q=MISSING
  emit_row "$P" "${TH54:--}" "${S0P:--}" "${S1P:--}" "${B0N:--}" "${B1N:--}" "$MRC" "$ERC" \
    "$CLSQ" "$G54Q" "$STT" "${NOTE:-all markers + S0/S1/Bl0/Bl1 present}"
done

log "=== every piece, as recorded ==="
cat "$SUM"
if [ -n "$FAILED" ]; then
  log "FAILED:$FAILED"
  exit 8
fi
log "all 9 pieces ran with both markers and the full geom bundle exported"
log "done"
