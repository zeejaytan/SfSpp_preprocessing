#!/bin/bash
# ticket 51 -- cap the formula growth angle by the piece's own measured cheapest smooth
# crossing (mesh_processing_headless.cpp thetaCross51 + the [GROWTH-51] caller block inside
# the ticket-45 formula path).  TWO arms per piece in ONE job, on the REAL corpus clouds:
#   C  SFS_GROWTH_FORMULA=1 SFS_GROWTH_CAP=1 -- the cap arm: the binary measures thetaCross51
#      (k=11 NN graph, both curvatures < 1.0, Kruskal ascending, largest component first
#      reaching 60% of the points with >=1 eligible edge) and paperTheta = min(formula,
#      0.9*thetaCross51), logged [GROWTH-51] crossing=... capped=... theta=...;
#   U  SFS_GROWTH_FORMULA=1 -- the uncapped control, identical to ticket 48's arm V: same
#      clouds, same code path, [GROWTH-45] only.
# Pass 1 is the ticket-48 CORPUS-MANIFEST GATE: md5 AND kept_points of every Juglet corpus
# cloud must equal MANIFEST_JUGLET_CC.tsv (columns read BY HEADER NAME), and no *_covering.pcd
# may sit anywhere under the corpus Point trees.  A cloud that fails stops the run before any
# cell.  Pot A released clouds are recorded, not gated (the unchanged control).
# Pass 2 env proof: every C cell's theta_env must literally read "SFS_GROWTH_FORMULA=1
# SFS_GROWTH_CAP=1" and every U cell's "SFS_GROWTH_FORMULA=1" (env_proof.tsv); theta_proof.tsv
# records the paper-grow thetaDeg against the [GROWTH-45] formula theta (U) or the [GROWTH-51]
# capped theta (C).
#
# Paid-for traps named on purpose (inherited from 44/45/46/48): CRLF in a script (two grids
# died on "set: pipefail: invalid option name"); unbound variables under set -u; a SKIP row
# must carry the SAME field count as the header (16 and 16 here); no xargs -d anywhere;
# grep -a on binary PLY/PCD; PLY header length varies (parsed by the instruments, never
# assumed).
set -uo pipefail

CELL_LIST=${CELL_LIST:-"Juglet:Juglet_Piece_1:CU"}
MIN_LEFT_S=${MIN_LEFT_S:-300}
CELL_BUDGET_S=${CELL_BUDGET_S:-10800}

: "${INSTR:?}" "${PY:?}" "${OUT:?}" "${DS:?}" "${CORP:?}" "${BIN:?}" "${APT:?}" "${SIF:?}"
: "${STAGER:?}" "${RUN:?}" "${JOBID:?}"
MANIFEST=$DS/Point/Juglet/MANIFEST_JUGLET_CC.tsv
[ -f "$MANIFEST" ] || { echo "[CELL51] FATAL no manifest at $MANIFEST"; exit 7; }

PIPECELL=$OUT/cells-pipeline
mkdir -p "$PIPECELL" || exit 7

log() { echo "[CELL51] $*"; }
pcd_points() { grep -am1 "^POINTS" "$1" | awk '{print $2}'; }

piece_mesh()  { if [ "$1" = "Pot_A" ]; then echo "$CORP/Mesh/$2_Mesh.obj"; else echo "$DS/Mesh/$1/$2_Mesh.obj"; fi; }
piece_cloud() { if [ "$1" = "Pot_A" ]; then echo "$CORP/Point/$1/$2_Point.pcd"; else echo "$DS/Point/$1/$2_Point.pcd"; fi; }
piece_axis()  { echo "$DS/Axes/$1/$2_Axis.xyz"; }

# manifest field BY HEADER NAME (pcd_md5, kept_points, spacing_mm...): never by position.
manifest_field() {  # $1 piece, $2 column name; the manifest opens with '#' comment lines,
  # so the header is the FIRST NON-COMMENT line, never NR==1.
  awk -F"\t" -v piece="$1" -v fld="$2" '
    /^#/ { next }
    !seen { for (i=1;i<=NF;i++) col[$i]=i; want=col[fld]; seen=1; next }
    want && $1==piece { print $want; exit }
  ' "$MANIFEST"
}

START_S=$(date +%s)
budget_left() { echo $(( CELL_BUDGET_S - ( $(date +%s) - START_S ) )); }

# ------------------------------------------------- pass 1: the corpus-manifest gate + every input exists
GATE=$OUT/corpus_gate.tsv
printf "piece\tpot\tcloud\tcloud_points\tcloud_md5\tmesh\tmesh_md5\tmanifest_pcd_md5\tmanifest_kept_points\tmanifest_spacing_mm\tgate\tnote\n" > "$GATE"
GATE_FAILED=""
for SPEC in $CELL_LIST; do
  POT=${SPEC%%:*}; PIECE=${SPEC#*:}; PIECE=${PIECE%%:*}
  MESH=$(piece_mesh "$POT" "$PIECE"); CLOUD=$(piece_cloud "$POT" "$PIECE"); AXIS=$(piece_axis "$POT" "$PIECE")
  G=ok
  [ -f "$MESH" ]  || { log "FATAL missing mesh $MESH"; G=FAILED; GATE_FAILED="$GATE_FAILED $PIECE/mesh"; }
  [ -f "$CLOUD" ] || { log "FATAL missing cloud $CLOUD"; G=FAILED; GATE_FAILED="$GATE_FAILED $PIECE/cloud"; }
  [ -f "$AXIS" ]  || { log "FATAL missing axis $AXIS"; G=FAILED; GATE_FAILED="$GATE_FAILED $PIECE/axis"; }
  SYNN=$(pcd_points "$CLOUD" 2>/dev/null)
  [ -n "$SYNN" ]  || { log "FATAL no point count for $PIECE"; G=FAILED; GATE_FAILED="$GATE_FAILED $PIECE/npts"; }
  SHMD5=$(md5sum "$CLOUD" 2>/dev/null | cut -d" " -f1)
  MMMD5=$(md5sum "$MESH" 2>/dev/null | cut -d" " -f1)

  if [ "$POT" = "Pot_A" ]; then
    printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
      "$PIECE" "$POT" "$CLOUD" "${SYNN:-na}" "$SHMD5" "$MESH" "$MMMD5" na na na "$G" "released corpus cloud: recorded, not gated (control)" >> "$GATE"
    log "control gate $PIECE: ${SYNN:-na} released points -> $G"
    continue
  fi

  MMD5=$(manifest_field "$PIECE" pcd_md5)
  MKEPT=$(manifest_field "$PIECE" kept_points)
  MSPAC=$(manifest_field "$PIECE" spacing_mm)
  if [ -z "$MMD5" ]; then
    log "FATAL $PIECE not in manifest $MANIFEST"; G=FAILED; GATE_FAILED="$GATE_FAILED $PIECE/not-in-manifest"
  elif [ "$SHMD5" != "$MMD5" ]; then
    log "FATAL corpus md5 moved on $PIECE: disk=$SHMD5 manifest=$MMD5"; G=FAILED; GATE_FAILED="$GATE_FAILED $PIECE/md5"
  fi
  if [ -n "$MKEPT" ] && [ -n "$SYNN" ] && [ "$MKEPT" != "$SYNN" ]; then
    log "FATAL $PIECE point count disagrees: pcd=$SYNN manifest kept_points=$MKEPT"; G=FAILED; GATE_FAILED="$GATE_FAILED $PIECE/count"
  fi
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$PIECE" "$POT" "$CLOUD" "${SYNN:-na}" "$SHMD5" "$MESH" "$MMMD5" "${MMD5:-na}" "${MKEPT:-na}" "${MSPAC:-na}" "$G" "corpus cloud == ticket-47 manifest" >> "$GATE"
  log "corpus gate $PIECE: ${SYNN:-na} points, md5 ${SHMD5:0:8} vs manifest ${MMD5:-absent} -> $G"
done

# no covering artifact may sit anywhere the run could read one from
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
  log "no cell was run -- ticket 51 never measures an unverified corpus"
  exit 9
fi
log "corpus verified against the ticket-47 manifest; the cells may run"

# ---------------------------------------------------------------- pass 2: the cells
FAILED=""
SUM=$PIPECELL/pipeline_cells.tsv
printf "pot\tpiece\tarm\ttheta_env\tcloud_points\tshipped_cloud_points\tpipeline_rc\tclusters\tstatus_outcome\tsurf0_points\tsurf1_points\tpaper_grow_theta\ttheta_computed_deg\tcrossing_deg\tcapped\tnote\n" > "$SUM"

# arm -> the env this cell carries.  Both arms ride the formula path; C adds the ticket-51 cap.
arm_env() {  # $1 arm
  case "$1" in
    C) echo "SFS_GROWTH_FORMULA=1 SFS_GROWTH_CAP=1" ;;
    U) echo "SFS_GROWTH_FORMULA=1" ;;
    *) return 1 ;;
  esac
}
arm_display() {  # $1 arm -> the pipeline_cells arm vocabulary of this ticket
  case "$1" in
    C) echo cap ;;
    U) echo uncapped ;;
    *) return 1 ;;
  esac
}
arm_kind() {  # $1 arm -> the inputs.md5 KIND label the stager writes
  case "$1" in
    C|U) echo REAL-RELEASED-CLOUD ;;
    *) return 1 ;;
  esac
}

run_arm() {
  local POT=$1 PIECE=$2 ARM=$3
  local TAG CELL ST LOG RC=0 F K NCLUST ENVS MESH CLOUD AXIS RUN_CLOUD SYNN SHIPPED_P KIND PGT T45 G45 G51 NOTE X51 CAP51 TH51
  TAG=${PIECE}_arm${ARM}
  CELL=$PIPECELL/$TAG
  ST=$PIPECELL/stage_$TAG
  MESH=$(piece_mesh "$POT" "$PIECE"); CLOUD=$(piece_cloud "$POT" "$PIECE"); AXIS=$(piece_axis "$POT" "$PIECE")
  KIND=$(arm_kind "$ARM") || { log "FATAL unknown arm $ARM"; return 1; }
  RUN_CLOUD=$CLOUD
  [ -f "$RUN_CLOUD" ] || { log "FATAL no run cloud $RUN_CLOUD"; return 1; }
  SYNN=$(pcd_points "$RUN_CLOUD")
  SHIPPED_P=$(pcd_points "$CLOUD")
  ENVS=$(arm_env "$ARM")
  log "=============================================================="
  log "cell $POT/$PIECE arm $ARM ($KIND) env='$ENVS' cloud=$RUN_CLOUD -> $CELL"

  mkdir -p "$CELL/logs" "$CELL/surfaces"
  bash "$STAGER" "$ST" "$POT" "$PIECE" "$AXIS" "$RUN_CLOUD" "$KIND" || { log "FATAL stage"; return 1; }
  cp -f "$ST/inputs.md5" "$CELL/inputs.md5"
  cat "$CELL/inputs.md5"

  LOG=$CELL/logs/mesh.log
  STATUS_RAW=$CELL/status_raw.tsv
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" \
      SFS_AXIS_FILE="$ST/Dataset/Axes/${PIECE}_Axis.xyz" \
      SFS_STATUS_FILE="$STATUS_RAW" $ENVS "$BIN" ) > "$LOG" 2>&1
  RC=$?
  log "pipeline rc=$RC log=$(stat -c %s "$LOG" 2>/dev/null || echo 0) bytes"
  [ -f "$LOG" ] || { log "FATAL no pipeline log (rc=$RC)"; return 1; }

  grep -aE "\[(SPACING|COUNT|SPLITTER|SWITCH)-2[234]\]|\[(FLOOR|RETRY|SINGLE|STATUS)-23\]|\[NORMAL-3[34]\]|\[PAPER-234\]|\[MERGE-41\]|\[REASSIGN-22\]|\[GROWTH-42|\[GROWTH-45\]|\[GROWTH-51\]|Number of clusters" \
    "$LOG" > "$CELL/logs/lines51.log" || true
  log "kept $(wc -l < "$CELL/logs/lines51.log") key log lines (full mesh.log kept beside them)"

  NCLUST=$(grep -am1 "Number of clusters" "$LOG" | sed -n "s/.*equal to \([0-9]*\).*/\1/p")
  G45=$(grep -am1 "\[GROWTH-45\]" "$LOG" | tr -d "\r")
  T45=""
  [ -n "$G45" ] && T45=$(printf "%s\n" "$G45" | sed -n "s/.* theta=\([^ ]*\).*/\1/p")
  G51=$(grep -am1 "\[GROWTH-51\]" "$LOG" | tr -d "\r")
  X51=""; CAP51=""; TH51=""
  if [ -n "$G51" ]; then
    X51=$(printf "%s\n" "$G51" | sed -n "s/.* crossing=\([^ ]*\).*/\1/p")
    CAP51=$(printf "%s\n" "$G51" | sed -n "s/.* capped=\([^ ]*\).*/\1/p")
    TH51=$(printf "%s\n" "$G51" | sed -n "s/.* theta=\([^ ]*\).*/\1/p")
  fi
  {
    echo "pot	$POT"
    echo "piece	$PIECE"
    echo "arm	$ARM"
    echo "env	${ENVS:-<none>}"
    echo "binary	$BIN"
    echo "cloud	$RUN_CLOUD"
    echo "cloud_kind	$KIND"
    echo "cloud_md5	$(md5sum "$RUN_CLOUD" | cut -d" " -f1)"
    echo "cloud_points	$SYNN"
    echo "shipped_cloud	$CLOUD"
    echo "shipped_cloud_md5	$(md5sum "$CLOUD" | cut -d" " -f1)"
    echo "shipped_cloud_points	$SHIPPED_P"
    echo "pipeline_rc	$RC"
    echo "pipeline_clusters	$NCLUST"
    echo "spacing_line	$(grep -am1 "\[SPACING-22\]" "$LOG" | tr -d "\r")"
    echo "reassign_line	$(grep -am1 "\[REASSIGN-22\]" "$LOG" | tr -d "\r")"
    echo "growth45_line	$G45"
    echo "growth45_theta	$T45"
    echo "growth51_line	$G51"
    echo "growth51_crossing	$X51"
    echo "growth51_capped	$CAP51"
    echo "growth51_theta	$TH51"
    echo "paper_grow_lines	$(grep -ac "\[PAPER-234\] paper grow" "$LOG")"
    echo "paper_grow_first	$(grep -am1 "\[PAPER-234\] paper grow" "$LOG" | tr -d "\r")"
    echo "ladder_lines	$(grep -ac "^\[GROWTH-42\] piece" "$LOG")"
    echo "status_outcome	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*outcome=\([^ ]*\).*/\1/p")"
    echo "status_surf0_points	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*surf0_points=\([^ ]*\).*/\1/p")"
    echo "status_surf1_points	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*surf1_points=\([^ ]*\).*/\1/p")"
    echo "final_sizes	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*sizes=\([^ ]*\) npts.*/\1/p")"
  } > "$CELL/cell.tsv"
  cat "$CELL/cell.tsv"

  # ---- the surfaces this arm wrote, kept: the pair-quality pass reads them
  for K in 0 1; do
    F=""
    for ext in ply xyz; do
      if [ -f "$ST/Temp/Data/$POT/${PIECE}_Surface_${K}.${ext}" ]; then
        F=$ST/Temp/Data/$POT/${PIECE}_Surface_${K}.${ext}
        break
      fi
    done
    if [ -z "$F" ]; then
      log "surface $K: the pipeline wrote none"
      continue
    fi
    cp -f "$F" "$CELL/surfaces/" 2>/dev/null || true
    log "surface $K: ${F##*.} $F ($(stat -c %s "$F" 2>/dev/null || echo 0) bytes)"
  done

  log "=== count the geometry this arm produced, then delete the stage ==="
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
  log "deleted stage $ST after the counted record above (cell surfaces and logs are KEPT)"

  NOTE=ok
  [ "$RC" -ne 0 ] && NOTE="pipeline rc=$RC"
  PGT=$(sed -n "s/^paper_grow_first\t//p" "$CELL/cell.tsv" | sed -n "s/.*thetaDeg=\([^ ]*\).*/\1/p")
  [ -z "$T45" ] && NOTE="$NOTE no GROWTH-45 line"
  if [ "$ARM" = "C" ]; then
    [ -z "$G51" ] && NOTE="$NOTE no GROWTH-51 line"
  else
    [ -n "$G51" ] && NOTE="$NOTE unexpected GROWTH-51 line (U must not cap)"
  fi
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$POT" "$PIECE" "$(arm_display "$ARM")" "${ENVS:-<none>}" "$SYNN" "$SHIPPED_P" "$RC" "${NCLUST:-na}" \
    "$(sed -n "s/^status_outcome\t//p" "$CELL/cell.tsv")" \
    "$(sed -n "s/^status_surf0_points\t//p" "$CELL/cell.tsv")" \
    "$(sed -n "s/^status_surf1_points\t//p" "$CELL/cell.tsv")" \
    "${PGT:-na}" "${T45:-}" "${X51:--}" "${CAP51:--}" "$NOTE" >> "$SUM"
  [ "$RC" -eq 0 ] || FAILED="$FAILED $POT/$PIECE/arm$ARM"
  return 0
}

# SPEC is POT:PIECE or POT:PIECE:ARMS (arms CU everywhere in this run).
spec_arms() { case ${1#*:*} in *:*) echo "${1##*:}" | fold -w1 ;; *) echo CU ;; esac; }
for SPEC in $CELL_LIST; do
  POT=${SPEC%%:*}; PIECE=${SPEC#*:}; PIECE=${PIECE%%:*}
  ARMS="$(spec_arms "$SPEC")"
  for ARM in $ARMS; do
    LEFT=$(budget_left)
    if [ "$LEFT" -lt "$MIN_LEFT_S" ]; then
      log "SKIP $POT/$PIECE arm $ARM: only ${LEFT}s of this script's ${CELL_BUDGET_S}s budget left"
      # 16 fields, exactly the header count: a short row shifts every column for every reader.
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "$POT" "$PIECE" "$(arm_display "$ARM" 2>/dev/null || echo "?")" "<none>" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "only ${LEFT}s left" >> "$SUM"
      continue
    fi
    run_arm "$POT" "$PIECE" "$ARM" || log "WARN arm $ARM on $POT/$PIECE did not complete"
  done
done

log "=== every cell, as recorded ==="
cat "$SUM"

# ---- env proof: a C cell must carry exactly "SFS_GROWTH_FORMULA=1 SFS_GROWTH_CAP=1", a U cell
# exactly "SFS_GROWTH_FORMULA=1" (and nothing else SFS_*, which the template unsets).
EP=$PIPECELL/env_proof.tsv
printf "pot\tpiece\tarm\ttheta_env\n" > "$EP"
ENV_BAD=""
for C in "$PIPECELL"/*/cell.tsv; do
  [ -f "$C" ] || continue
  POT=$(sed -n "s/^pot\t//p" "$C"); PIECE=$(sed -n "s/^piece\t//p" "$C"); A=$(sed -n "s/^arm\t//p" "$C")
  TE=$(sed -n "s/^env\t//p" "$C")
  AD=$(arm_display "$A" 2>/dev/null || echo "?")
  printf "%s\t%s\t%s\t%s\n" "$POT" "$PIECE" "$AD" "${TE:-na}" >> "$EP"
  WANT=""; [ "$A" = "C" ] && WANT="SFS_GROWTH_FORMULA=1 SFS_GROWTH_CAP=1"; [ "$A" = "U" ] && WANT="SFS_GROWTH_FORMULA=1"
  if [ "${TE:-na}" != "$WANT" ]; then ENV_BAD="$ENV_BAD $POT/$PIECE/$A"; fi
done
log "=== env proof (C = FORMULA+CAP, U = FORMULA only) ==="
cat "$EP"
if [ -n "$ENV_BAD" ]; then
  log "FAILED env proof, a cell did not carry exactly its arm env:$ENV_BAD"
  FAILED="$FAILED env-proof"
fi

# ---- theta proof: the paper-grow thetaDeg the log carried vs the theta the arm chose:
# C = the [GROWTH-51] theta (post-cap), U = the [GROWTH-45] formula theta. REPORT ONLY.
TP=$PIPECELL/theta_proof.tsv
printf "pot\tpiece\tarm\tpaper_grow_thetaDeg\ttheta_evidence\tdelta_abs\tnote\n" > "$TP"
for C in "$PIPECELL"/*/cell.tsv; do
  [ -f "$C" ] || continue
  POT=$(sed -n "s/^pot\t//p" "$C"); PIECE=$(sed -n "s/^piece\t//p" "$C"); A=$(sed -n "s/^arm\t//p" "$C")
  AD=$(arm_display "$A" 2>/dev/null || echo "?")
  PGT=$(sed -n "s/^paper_grow_first\t//p" "$C" | sed -n "s/.*thetaDeg=\([^ ]*\).*/\1/p")
  if [ "$A" = "C" ]; then EV=$(sed -n "s/^growth51_theta\t//p" "$C"); SRC=growth51; else EV=$(sed -n "s/^growth45_theta\t//p" "$C"); SRC=growth45; fi
  D=na; N=ok
  if [ -z "$EV" ]; then N="no $SRC theta in the log"; fi
  if [ -z "$PGT" ]; then N="$N; no paper-grow line"; fi
  if [ -n "$PGT" ] && [ -n "$EV" ]; then
    D=$("$PY" -c "print('%.4f' % abs(float('$PGT')-float('$EV')))" 2>/dev/null || echo na)
  fi
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "$POT" "$PIECE" "$AD" "${PGT:-na}" "${EV:-na}" "$D" "$N" >> "$TP"
done
log "=== theta proof (paper-grow thetaDeg vs the arm's chosen theta, per cell) ==="
cat "$TP"

if [ -n "$FAILED" ]; then
  log "FAILED:$FAILED"
  exit 8
fi
log "all cells ran, every env read its arm's exact SFS_* set, corpus == manifest"
log "done"
