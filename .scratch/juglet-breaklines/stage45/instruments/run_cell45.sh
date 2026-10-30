#!/bin/bash
# ticket 45 -- the default growth angle becomes the curvature formula (ticket 43's law,
# theta_deg = 3.3573 x S / R_fold x 180/pi, computed per piece on the downsampled cloud the
# growth runs on; mesh_processing_headless.cpp medianFoldRadius45 + the ticket-45 caller block,
# logged [GROWTH-45]).  One cell per piece and arm on the REAL RELEASED clouds:
#   F  no SFS_* env at all: the NEW default path -- the binary computes theta from the piece's
#      own curvature and logs [GROWTH-45] piece=... S=... R_med=... theta=...;
#   O  SFS_PAPER_THETA=3.4 on the four proof pieces: today's path, which must stay
#      byte-for-byte (the override proof: this cell's SampledWithNormals md5 is compared
#      offline against ticket 44's committed defaults_proof arm-A md5).
# thetas44.tsv rides along COMMITTED as the REFERENCE only (col 3 = ticket 43's k-rule theta,
# tolerance 0.30 deg); no cell reads it.  Measurement passes of ticket 44 (wall, surface,
# pair, nest) are NOT run here: the ticket-45 question is the default's theta and outcome
# class, both of which the pipeline's own logs and status carry.
#
# Paid-for traps named on purpose: CRLF in a script (two grids died on "set: pipefail: invalid
# option name"); unbound variables under set -u; no xargs -d anywhere; grep -a on binary
# PLY/PCD headers; PLY header length varies (parsed to end_header by the instruments, never
# assumed); scipy exists only in the TORA env (not used here).
set -uo pipefail

CELL_LIST=${CELL_LIST:-"Juglet:Juglet_Piece_1"}
MIN_LEFT_S=${MIN_LEFT_S:-300}
CELL_BUDGET_S=${CELL_BUDGET_S:-9000}
PROOF_LIST=${PROOF_LIST:-""}

: "${INSTR:?}" "${PY:?}" "${OUT:?}" "${DS:?}" "${CORP:?}" "${BIN:?}" "${APT:?}" "${SIF:?}"
: "${STAGER:?}" "${RUN:?}" "${JOBID:?}"

PIPECELL=$OUT/cells-pipeline
mkdir -p "$PIPECELL" || exit 7

log() { echo "[CELL45] $*"; }
pcd_points() { grep -am1 "^POINTS" "$1" | awk '{print $2}'; }

piece_mesh()  { if [ "$1" = "Pot_A" ]; then echo "$CORP/Mesh/$2_Mesh.obj"; else echo "$DS/Mesh/$1/$2_Mesh.obj"; fi; }
piece_cloud() { if [ "$1" = "Pot_A" ]; then echo "$CORP/Point/$1/$2_Point.pcd"; else echo "$DS/Point/$1/$2_Point.pcd"; fi; }
piece_axis()  { echo "$DS/Axes/$1/$2_Axis.xyz"; }

START_S=$(date +%s)
budget_left() { echo $(( CELL_BUDGET_S - ( $(date +%s) - START_S ) )); }

# ---------------------------------------------------------------- pass 1: the clouds exist
GATE=$PIPECELL/cloud_gate.tsv
printf "piece\tpot\tcloud_points\tcloud_md5\tgate\n" > "$GATE"
GATE_FAILED=""
for SPEC in $CELL_LIST; do
  POT=${SPEC%%:*}; PIECE=${SPEC#*:}; PIECE=${PIECE%%:*}
  MESH=$(piece_mesh "$POT" "$PIECE"); CLOUD=$(piece_cloud "$POT" "$PIECE"); AXIS=$(piece_axis "$POT" "$PIECE")
  G=ok
  [ -f "$MESH" ] || { log "FATAL missing mesh $MESH"; G=FAILED; GATE_FAILED="$GATE_FAILED $PIECE/mesh"; }
  [ -f "$CLOUD" ] || { log "FATAL missing cloud $CLOUD"; G=FAILED; GATE_FAILED="$GATE_FAILED $PIECE/cloud"; }
  [ -f "$AXIS" ] || { log "FATAL missing axis $AXIS"; G=FAILED; GATE_FAILED="$GATE_FAILED $PIECE/axis"; }
  SYNN=$(pcd_points "$CLOUD" 2>/dev/null)
  [ -n "$SYNN" ] || { log "FATAL no point count for $PIECE"; G=FAILED; GATE_FAILED="$GATE_FAILED $PIECE/npts"; }
  printf "%s\t%s\t%s\t%s\t%s\n" "$PIECE" "$POT" "${SYNN:-na}" "$(md5sum "$CLOUD" 2>/dev/null | cut -d' ' -f1)" "$G" >> "$GATE"
  log "cloud gate $PIECE: ${SYNN:-na} points -> $G"
done
cat "$GATE"
if [ -n "$GATE_FAILED" ]; then
  log "STOP: a staged input is missing:$GATE_FAILED"
  log "no cell was run"
  exit 9
fi
log "clouds present; the cells may run"

# ---------------------------------------------------------------- pass 2: the cells
FAILED=""
SUM=$PIPECELL/pipeline_cells.tsv
printf "pot\tpiece\tarm\ttheta_env\tcloud_points\tpipeline_rc\tclusters\tstatus_outcome\tsurf0_points\tsurf1_points\tpaper_grow_theta\ttheta_computed_deg\tnote\n" > "$SUM"

# arm -> the env this cell carries.  F carries NOTHING (the new default computes the theta);
# O carries exactly SFS_PAPER_THETA=3.4 (today's path, the override proof).
arm_env() {  # $1 arm
  case "$1" in
    F) echo "" ;;
    O) echo "SFS_PAPER_THETA=3.4" ;;
    *) return 1 ;;
  esac
}
arm_display() {  # $1 arm -> the pipeline_cells arm vocabulary of this ticket
  case "$1" in
    F) echo formula ;;
    O) echo 3.4 ;;
    *) return 1 ;;
  esac
}

run_arm() {
  local POT=$1 PIECE=$2 ARM=$3
  local TAG CELL ST LOG RC=0 F K NCLUST ENVS MESH CLOUD AXIS RUN_CLOUD SYNN PGT T45
  TAG=${PIECE}_arm${ARM}
  CELL=$PIPECELL/$TAG
  ST=$PIPECELL/stage_$TAG
  MESH=$(piece_mesh "$POT" "$PIECE"); CLOUD=$(piece_cloud "$POT" "$PIECE"); AXIS=$(piece_axis "$POT" "$PIECE")
  RUN_CLOUD=$CLOUD
  [ -f "$RUN_CLOUD" ] || { log "FATAL no released cloud $RUN_CLOUD"; return 1; }
  SYNN=$(pcd_points "$RUN_CLOUD")
  ENVS=$(arm_env "$ARM")
  log "=============================================================="
  log "cell $POT/$PIECE arm $ARM env='${ENVS:-<none>}' -> $CELL"

  mkdir -p "$CELL/logs" "$CELL/surfaces"
  bash "$STAGER" "$ST" "$POT" "$PIECE" "$AXIS" "$RUN_CLOUD" REAL-RELEASED-CLOUD || { log "FATAL stage"; return 1; }
  cp -f "$ST/inputs.md5" "$CELL/inputs.md5"
  cat "$CELL/inputs.md5"

  LOG=$CELL/logs/mesh.log
  STATUS_RAW=$CELL/status_raw.tsv
  log "env: ${ENVS:-<none>}"
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" \
      SFS_AXIS_FILE="$ST/Dataset/Axes/${PIECE}_Axis.xyz" \
      SFS_STATUS_FILE="$STATUS_RAW" $ENVS "$BIN" ) > "$LOG" 2>&1
  RC=$?
  log "pipeline rc=$RC log=$(stat -c %s "$LOG" 2>/dev/null || echo 0) bytes"
  [ -f "$LOG" ] || { log "FATAL no pipeline log (rc=$RC)"; return 1; }

  grep -aE "\[(SPACING|COUNT|SPLITTER|SWITCH)-2[234]\]|\[(FLOOR|RETRY|SINGLE|STATUS)-23\]|\[NORMAL-3[34]\]|\[PAPER-234\]|\[MERGE-41\]|\[REASSIGN-22\]|\[GROWTH-42|\[GROWTH-45\]|Number of clusters" \
    "$LOG" > "$CELL/logs/lines45.log" || true
  log "kept $(wc -l < "$CELL/logs/lines45.log") key log lines (full mesh.log kept beside them)"

  NCLUST=$(grep -am1 "Number of clusters" "$LOG" | sed -n "s/.*equal to \([0-9]*\).*/\1/p")
  G45=$(grep -am1 "\[GROWTH-45\]" "$LOG" | tr -d '\r')
  T45=""
  [ -n "$G45" ] && T45=$(printf "%s\n" "$G45" | sed -n "s/.* theta=\([^ ]*\).*/\1/p")
  {
    echo "pot	$POT"
    echo "piece	$PIECE"
    echo "arm	$ARM"
    echo "env	${ENVS:-<none>}"
    echo "binary	$BIN"
    echo "cloud	$RUN_CLOUD"
    echo "cloud_md5	$(md5sum "$RUN_CLOUD" | cut -d' ' -f1)"
    echo "cloud_points	$SYNN"
    echo "pipeline_rc	$RC"
    echo "pipeline_clusters	$NCLUST"
    echo "spacing_line	$(grep -am1 "\[SPACING-22\]" "$LOG" | tr -d '\r')"
    echo "reassign_line	$(grep -am1 "\[REASSIGN-22\]" "$LOG" | tr -d '\r')"
    echo "growth45_line	$G45"
    echo "growth45_theta	$T45"
    echo "paper_grow_lines	$(grep -ac "\[PAPER-234\] paper grow" "$LOG")"
    echo "paper_grow_first	$(grep -am1 "\[PAPER-234\] paper grow" "$LOG" | tr -d '\r')"
    echo "ladder_lines	$(grep -ac "^\[GROWTH-42\] piece" "$LOG")"
    echo "status_outcome	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*outcome=\([^ ]*\).*/\1/p")"
    echo "status_surf0_points	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*surf0_points=\([^ ]*\).*/\1/p")"
    echo "status_surf1_points	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*surf1_points=\([^ ]*\).*/\1/p")"
    echo "final_sizes	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*sizes=\([^ ]*\) npts.*/\1/p")"
  } > "$CELL/cell.tsv"
  cat "$CELL/cell.tsv"

  # ---- SampledWithNormals md5 BEFORE the stage is deleted (the override proof reads it)
  ARMP=$ST/Temp/Data/$POT/${PIECE}_SampledWithNormals.ply
  if [ -f "$ARMP" ]; then
    echo "sampled_md5	$(md5sum "$ARMP" | cut -d' ' -f1)" >> "$CELL/cell.tsv"
    echo "sampled_points	$(grep -am1 "^element vertex" "$ARMP" | awk '{print $3}')" >> "$CELL/cell.tsv"
    cp -f "$ARMP" "$CELL/surfaces/" 2>/dev/null || true
  else
    echo "sampled_md5	-" >> "$CELL/cell.tsv"
    echo "sampled_points	-" >> "$CELL/cell.tsv"
  fi

  # ---- the surfaces this arm wrote, kept (not measured: that is ticket 44's question, not 45's)
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

  local NOTE=ok
  [ "$RC" -ne 0 ] && NOTE="pipeline rc=$RC"
  PGT=$(sed -n "s/^paper_grow_first	//p" "$CELL/cell.tsv" | sed -n "s/.*thetaDeg=\([^ ]*\).*/\1/p")
  [ "$ARM" = "O" ] && [ -z "$PGT" ] && [ -z "$T45" ] && NOTE="$NOTE no theta evidence (no GROWTH-45, no paper grow line)"
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$POT" "$PIECE" "$(arm_display "$ARM")" "${ENVS:-<none>}" "$SYNN" "$RC" "${NCLUST:-na}" \
    "$(sed -n "s/^status_outcome	//p" "$CELL/cell.tsv")" \
    "$(sed -n "s/^status_surf0_points	//p" "$CELL/cell.tsv")" \
    "$(sed -n "s/^status_surf1_points	//p" "$CELL/cell.tsv")" \
    "${PGT:-na}" "${T45:-}" "$NOTE" >> "$SUM"
  [ "$RC" -eq 0 ] || FAILED="$FAILED $POT/$PIECE/arm$ARM"
  return 0
}

# SPEC is POT:PIECE or POT:PIECE:ARMS (e.g. Juglet:Juglet_Piece_2:FO = formula + 3.4 override)
spec_arms() { case ${1#*:*} in *:*) echo "${1##*:}" | fold -w1 ;; *) echo F ;; esac; }
for SPEC in $CELL_LIST; do
  POT=${SPEC%%:*}; PIECE=${SPEC#*:}; PIECE=${PIECE%%:*}
  ARMS="$(spec_arms "$SPEC")"
  for ARM in $ARMS; do
    LEFT=$(budget_left)
    if [ "$LEFT" -lt "$MIN_LEFT_S" ]; then
      log "SKIP $POT/$PIECE arm $ARM: only ${LEFT}s of this script's ${CELL_BUDGET_S}s budget left"
      printf "%s\t%s\t%s\t-\t-\t-\t-\t-\t-\t-\t-\t-\tonly ${LEFT}s left\n" \
        "$POT" "$PIECE" "$(arm_display "$ARM")" >> "$SUM"
      continue
    fi
    run_arm "$POT" "$PIECE" "$ARM" || log "WARN arm $ARM on $POT/$PIECE did not complete"
  done
done

log "=== every cell, as recorded ==="
cat "$SUM"

# ---- override proof: the SFS_PAPER_THETA=3.4 cells' sampled-cloud md5 (compared offline
# against ticket 44's committed defaults_proof arm-A md5; ticket 291 measured run-to-run
# spread on the unseeded sampler, so a mismatch is recorded as measured, not gated).
P=$PIPECELL/override_proof.tsv
printf "pot\tpiece\toverride_md5\n" > "$P"
for SPEC in $PROOF_LIST; do
  POT=${SPEC%%:*}; PIECE=${SPEC#*:}
  CO=$PIPECELL/${PIECE}_armO/cell.tsv
  if [ -f "$CO" ]; then
    printf "%s\t%s\t%s\n" "$POT" "$PIECE" "$(sed -n "s/^sampled_md5	//p" "$CO")" >> "$P"
  else
    printf "%s\t%s\tmissing-O-cell\n" "$POT" "$PIECE" >> "$P"
  fi
done
log "=== override proof (arm O sampled-cloud md5, one per proof piece) ==="
cat "$P"

# ---- the theta evidence proof: the paper grow line must carry the theta this arm used.
# F: the [GROWTH-45] computed theta; O: the 3.4 the env asked for.
SP=$PIPECELL/theta_proof.tsv
printf "pot\tpiece\tarm\ttheta_source\tpaper_grow_theta\ttheta_evidence\tmatch\n" > "$SP"
for C in "$PIPECELL"/*/cell.tsv; do
  [ -f "$C" ] || continue
  POT=$(sed -n "s/^pot	//p" "$C"); PIECE=$(sed -n "s/^piece	//p" "$C"); ARM=$(sed -n "s/^arm	//p" "$C")
  GOT=$(sed -n "s/^paper_grow_first	//p" "$C" | sed -n "s/.*thetaDeg=\([^ ]*\).*/\1/p")
  SRC=na; EV=na
  if [ "$ARM" = "F" ]; then
    SRC=growth45; EV=$(sed -n "s/^growth45_theta	//p" "$C")
  elif [ "$ARM" = "O" ]; then
    SRC=env; EV=3.4
  fi
  M=no
  if [ -n "$GOT" ] && [ -n "$EV" ] && [ "$EV" != "na" ]; then
    M=$("$PY" -c "print('yes' if abs(float('$GOT')-float('$EV'))<1e-6 else 'no')")
  fi
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "$POT" "$PIECE" "$(arm_display "$ARM")" "$SRC" "${GOT:-na}" "$EV" "$M" >> "$SP"
done
log "=== theta evidence proof ==="
cat "$SP"

if [ -n "$FAILED" ]; then
  log "FAILED cells:$FAILED"
  exit 8
fi
log "all cells ran"
log "done"
