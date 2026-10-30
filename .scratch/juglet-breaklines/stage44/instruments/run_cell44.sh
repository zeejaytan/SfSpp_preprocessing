#!/bin/bash
# ticket 44 -- the one untested step of ticket 43: run the pipeline at the CURVATURE-DERIVED
# angle, the theta each sherd's own geometry predicts.  One cell per piece and arm on the REAL
# RELEASED clouds, single-delta design:
#   A  today exactly: NO SFS_* env at all (shipped defaults; theta 3.4, paper chain on, own
#      reassign mode, adaptive spacing);
#   B  arm A + SFS_PAPER_THETA=<formula theta of this piece>  (theta = k x S / R_fold, k =
#      3.3573 fixed on the Pot A median; values verbatim from ticket 43's k-rule table);
#   N  a second NO-ENV cell on the defaults-unchanged pieces: its SampledWithNormals md5 must
#      equal arm A's, which is the proof that nothing upstream of the growth moved.
# The thetas come from thetas44.tsv, COMMITTED WITH THIS TICKET verbatim from ticket 43's
# prediction table, never recomputed here.  NO pipeline source change: SFS_PAPER_THETA
# already exists (mesh_processing_headless.cpp:4574, consumed at :3191).
#
# Paid-for traps named on purpose: CRLF in a script (two grids died on "set: pipefail: invalid
# option name"); brace-stripping when a submit template renders; unbound variables under set -u;
# no xargs -d anywhere; grep -a on binary PLY/PCD headers; PLY header length varies (parsed to
# end_header by the instruments, never assumed); scipy exists only in the TORA env.
set -uo pipefail

CELL_LIST=${CELL_LIST:-"Juglet:Juglet_Piece_1"}
THETAS=${THETAS:-}
MIN_LEFT_S=${MIN_LEFT_S:-300}
CELL_BUDGET_S=${CELL_BUDGET_S:-9000}
PROOF_LIST=${PROOF_LIST:-""}

: "${INSTR:?}" "${PY:?}" "${OUT:?}" "${DS:?}" "${CORP:?}" "${BIN:?}" "${APT:?}" "${SIF:?}"
: "${STAGER:?}" "${RUN:?}" "${JOBID:?}" "${THETAS:?}"

GROW38=$INSTR/grow38.py
NEST39=$INSTR/nest39.py
WALL40=$INSTR/wall40.py
PIPECELL=$OUT/cells-pipeline
mkdir -p "$PIPECELL" || exit 7

log() { echo "[CELL43] $*"; }
jget() { "$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])' "$1" "$2" 2>/dev/null || echo ""; }
jgetna() {
  local v
  v=$(jget "$1" "$2") || { echo na; return 0; }
  [ -z "$v" ] && { echo na; return 0; }
  [ "$v" = "None" ] && v=na
  printf "%s\n" "$v"
}
pcd_points() { grep -am1 "^POINTS" "$1" | awk '{print $2}'; }

# thetas.tsv from Part B: pot piece R1 R2
theta_of() {  # $1 pot  $2 piece  $3 column (3=R1 4=R2)
  awk -F'\t' -v p="$1" -v c="$2" -v k="$3" '$1==p && $2==c {print $k; exit}' "$THETAS"
}

# ticket 35's recorded wall medians (mm) -- recorded beside the measurement, not gated
anc_wall() { case "$1" in   # one argument "Pot/Piece": $2 is unset here and set -u made this print na
  Juglet/Juglet_Piece_1) echo 2.35376 ;; Juglet/Juglet_Piece_2) echo 2.69305 ;; Juglet/Juglet_Piece_3) echo 2.4516 ;;
  Juglet/Juglet_Piece_5) echo 2.8998 ;; Juglet/Juglet_Piece_7) echo 3.26316 ;; Juglet/Juglet_Piece_9) echo 2.59484 ;;
  Pot_A/Pot_A_Piece_01) echo 8.2857 ;; Pot_A/Pot_A_Piece_07) echo 4.05609 ;;
  *) echo "" ;; esac; }

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
printf "pot\tpiece\tarm\ttheta_env\tcloud_points\tpipeline_rc\tclusters\tstatus_outcome\tsurf0_points\tsurf1_points\tpaper_grow_theta\tgot_paper_grow_theta\tnote\n" > "$SUM"
SURFSUM=$PIPECELL/surfaces.tsv
printf "pot\tpiece\tarm\tsurface\tpoints\tdistinct\text_x\text_y\text_z\tdiag\tcov_2mm\tfold_deg\tnormal_src\tply_bytes\n" > "$SURFSUM"
PAIRSUM=$PIPECELL/surface_pairs.tsv
printf "pot\tpiece\tarm\tn0\tn1\tmed_nn\tmed_along\tmed_across\tmed_angle_deg\tcoin\tmed_t_signed\tp05_t_signed\tp95_t_signed\tnormal_src_a\tnormal_src_b\n" > "$PAIRSUM"
NESTSUM=$PIPECELL/nest.tsv
printf "pot\tpiece\tarm\tn0\tn0_distinct\tn1\tn1_distinct\tshared\tshared_over_a\tshared_over_b\tshared_over_smaller\tmean_normal_dot\tmatched\tmedian_point_normal_angle_deg\n" > "$NESTSUM"
WALLSUM=$PIPECELL/walls.tsv
printf "pot\tpiece\tarm\tcloud_pts\trays\tthick_med_mm\tthick_p10_mm\tthick_p90_mm\tanchor_med_mm\tabs_diff\tanchor_hit\n" > "$WALLSUM"

# arm -> the env this cell carries.  A and N carry NOTHING (that is the point of the design and
# of the defaults-unchanged proof); B and C carry exactly one variable.
arm_env() {  # $1 arm  $2 pot  $3 piece
  case "$1" in
    A|N) echo "" ;;
    B) local t; t=$(theta_of "$2" "$3" 3); [ -n "$t" ] && echo "SFS_PAPER_THETA=$t" || echo "" ;;
    C) local t; t=$(theta_of "$2" "$3" 4); [ -n "$t" ] && echo "SFS_PAPER_THETA=$t" || echo "" ;;
    *) return 1 ;;
  esac
}

run_arm() {
  local POT=$1 PIECE=$2 ARM=$3
  local TAG CELL ST LOG RC=0 F K NCLUST ENVS MESH CLOUD AXIS RUN_CLOUD SYNN
  TAG=${PIECE}_arm${ARM}
  CELL=$PIPECELL/$TAG
  ST=$PIPECELL/stage_$TAG
  MESH=$(piece_mesh "$POT" "$PIECE"); CLOUD=$(piece_cloud "$POT" "$PIECE"); AXIS=$(piece_axis "$POT" "$PIECE")
  RUN_CLOUD=$CLOUD
  [ -f "$RUN_CLOUD" ] || { log "FATAL no released cloud $RUN_CLOUD"; return 1; }
  SYNN=$(pcd_points "$RUN_CLOUD")
  ENVS=$(arm_env "$ARM" "$POT" "$PIECE")
  log "=============================================================="
  log "cell $POT/$PIECE arm $ARM env='${ENVS:-<none>}' -> $CELL"

  mkdir -p "$CELL/logs" "$CELL/surfaces" "$CELL/measure"
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

  grep -aE "\[(SPACING|COUNT|SPLITTER|SWITCH)-2[234]\]|\[(FLOOR|RETRY|SINGLE|STATUS)-23\]|\[NORMAL-3[34]\]|\[PAPER-234\]|\[MERGE-41\]|\[REASSIGN-22\]|\[GROWTH-42|Number of clusters" \
    "$LOG" > "$CELL/logs/lines43.log" || true
  log "kept $(wc -l < "$CELL/logs/lines43.log") key log lines (full mesh.log kept beside them)"

  NCLUST=$(grep -am1 "Number of clusters" "$LOG" | sed -n "s/.*equal to \([0-9]*\).*/\1/p")
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
    echo "paper_grow_lines	$(grep -ac "\[PAPER-234\] paper grow" "$LOG")"
    echo "paper_grow_first	$(grep -am1 "\[PAPER-234\] paper grow" "$LOG" | tr -d '\r')"
    echo "ladder_lines	$(grep -ac "^\[GROWTH-42\] piece" "$LOG")"
    echo "status_outcome	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*outcome=\([^ ]*\).*/\1/p")"
    echo "status_surf0_points	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*surf0_points=\([^ ]*\).*/\1/p")"
    echo "status_surf1_points	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*surf1_points=\([^ ]*\).*/\1/p")"
    echo "final_sizes	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*sizes=\([^ ]*\) npts.*/\1/p")"
  } > "$CELL/cell.tsv"
  cat "$CELL/cell.tsv"

  # ---- SampledWithNormals md5 BEFORE the stage is deleted (the defaults-unchanged proof)
  ARMP=$ST/Temp/Data/$POT/${PIECE}_SampledWithNormals.ply
  if [ -f "$ARMP" ]; then
    echo "sampled_md5	$(md5sum "$ARMP" | cut -d' ' -f1)" >> "$CELL/cell.tsv"
    echo "sampled_points	$(grep -am1 "^element vertex" "$ARMP" | awk '{print $3}')" >> "$CELL/cell.tsv"
  else
    echo "sampled_md5	-" >> "$CELL/cell.tsv"
    echo "sampled_points	-" >> "$CELL/cell.tsv"
  fi

  # ---- wall thickness from this cell's own SampledWithNormals
  if [ -f "$ARMP" ]; then
    WJ=$CELL/measure/wall_$TAG.json
    if "$PY" "$WALL40" --group g43 --pot "$POT" --piece "$PIECE" --mesh "$MESH" --arm "$ARMP" --out "$WJ"; then
      local WMED WP10 WP90 WANCM WABS WHIT
      WMED=$(jget "$WJ" thick_med_mm); WP10=$(jget "$WJ" thick_p10_mm); WP90=$(jget "$WJ" thick_p90_mm)
      WANCM=$(anc_wall "$POT/$PIECE")
      WABS=na; WHIT=na
      if [ -n "$WANCM" ]; then
        WABS=$("$PY" -c "print('%.5f' % abs(float('$WMED')-float('$WANCM')))")
        WHIT=$("$PY" -c "print('yes' if abs(float('$WMED')-float('$WANCM'))<=0.05*float('$WANCM') else 'no')")
      fi
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "$POT" "$PIECE" "$ARM" "$(jget "$WJ" cloud_pts)" "$(jget "$WJ" rays)" "$WMED" "$WP10" "$WP90" \
        "${WANCM:-na}" "$WABS" "$WHIT" >> "$WALLSUM"
      log "wall $POT/$PIECE arm $ARM: med $WMED mm (anchor ${WANCM:-na}, diff $WABS)"
    else
      log "WARN wall measurement failed on $PIECE"
    fi
  else
    log "wall: no SampledWithNormals.ply written, no wall row"
  fi

  log "=== the surfaces this arm wrote, measured against the ORIGINAL cloud and mesh ==="
  for K in 0 1; do
    F=""
    for ext in ply xyz; do
      if [ -f "$ST/Temp/Data/$POT/${PIECE}_Surface_${K}.$ext" ]; then
        F=$ST/Temp/Data/$POT/${PIECE}_Surface_${K}.$ext
        break
      fi
    done
    if [ -z "$F" ]; then
      log "surface $K: the pipeline wrote none"
      continue
    fi
    cp -f "$F" "$CELL/surfaces/" 2>/dev/null || true
    log "surface $K: ${F##*.} $F ($(stat -c %s "$F" 2>/dev/null || echo 0) bytes)"
    if [ "${F##*.}" != "ply" ]; then
      log "surface $K is ${F##*.} and no .ply was written beside it: kept as written, not measured"
      continue
    fi
    SJ=$CELL/measure/surface_${TAG}_Surface_$K.json
    DJ=$CELL/measure/distinct_${TAG}_Surface_$K.json
    if "$PY" "$GROW38" surface --ply "$F" --mesh "$MESH" --orig-cloud "$CLOUD" \
         --tag "${TAG}_Surface_$K" --outdir "$CELL/measure" \
       && "$PY" "$NEST39" count --ply "$F" --tag "${TAG}_Surface_$K" --outdir "$CELL/measure"; then
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "$POT" "$PIECE" "$ARM" "$K" "$(jget "$SJ" points)" "$(jget "$DJ" distinct)" \
        "$(jget "$SJ" ext_x)" "$(jget "$SJ" ext_y)" "$(jget "$SJ" ext_z)" \
        "$(jget "$SJ" diag)" "$(jget "$SJ" cov_2mm)" "$(jget "$SJ" fold_deg)" \
        "$(jget "$SJ" normal_src)" "$(stat -c %s "$F" 2>/dev/null || echo 0)" >> "$SURFSUM"
    else
      log "WARN surface $K not measured"
    fi
  done

  log "=== the corrected signed-t pair statistic between the two surfaces ==="
  if [ -f "$CELL/surfaces/${PIECE}_Surface_0.ply" ] && [ -f "$CELL/surfaces/${PIECE}_Surface_1.ply" ]; then
    PJ=$CELL/measure/surfacepair_$TAG.json
    NJ=$CELL/measure/nest_$TAG.json
    if "$PY" "$GROW38" surfacepair --a "$CELL/surfaces/${PIECE}_Surface_0.ply" \
         --b "$CELL/surfaces/${PIECE}_Surface_1.ply" --tag "$TAG" --outdir "$CELL/measure" \
       && "$PY" "$NEST39" pair --a "$CELL/surfaces/${PIECE}_Surface_0.ply" \
         --b "$CELL/surfaces/${PIECE}_Surface_1.ply" --tag "$TAG" --outdir "$CELL/measure"; then
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "$POT" "$PIECE" "$ARM" "$(jget "$PJ" n0)" "$(jget "$PJ" n1)" "$(jget "$PJ" med_nn)" \
        "$(jget "$PJ" med_along)" "$(jget "$PJ" med_across)" "$(jget "$PJ" med_angle_deg)" \
        "$(jget "$PJ" coin)" "$(jget "$PJ" med_t_signed)" "$(jget "$PJ" p05_t_signed)" \
        "$(jget "$PJ" p95_t_signed)" "$(jget "$PJ" normal_src_a)" "$(jget "$PJ" normal_src_b)" >> "$PAIRSUM"
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "$POT" "$PIECE" "$ARM" "$(jget "$NJ" n0)" "$(jget "$NJ" n0_distinct)" "$(jget "$NJ" n1)" \
        "$(jget "$NJ" n1_distinct)" "$(jget "$NJ" shared)" "$(jget "$NJ" shared_over_a)" \
        "$(jget "$NJ" shared_over_b)" "$(jget "$NJ" shared_over_smaller)" \
        "$(jget "$NJ" mean_normal_dot)" "$(jget "$NJ" matched)" \
        "$(jgetna "$NJ" median_point_normal_angle_deg)" >> "$NESTSUM"
    else
      log "WARN the two surfaces were not paired"
    fi
  else
    log "surface pair: this arm did not write both surfaces, no pair row"
  fi

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
  log "deleted stage $ST after the counted record above (cell surfaces, logs and measures are KEPT)"

  local NOTE=ok PGT GGT
  [ "$RC" -ne 0 ] && NOTE="pipeline rc=$RC"
  PGT=$(sed -n "s/^paper_grow_first	//p" "$CELL/cell.tsv" | sed -n "s/.*thetaDeg=\([^ ]*\).*/\1/p")
  GGT=$(theta_of "$POT" "$PIECE" 3); [ "$ARM" = "C" ] && GGT=$(theta_of "$POT" "$PIECE" 4)
  [ "$ARM" = "A" ] || [ "$ARM" = "N" ] && GGT=3.4
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$POT" "$PIECE" "$ARM" "${ENVS:-<none>}" "$SYNN" "$RC" "${NCLUST:-na}" \
    "$(sed -n "s/^status_outcome	//p" "$CELL/cell.tsv")" \
    "$(sed -n "s/^status_surf0_points	//p" "$CELL/cell.tsv")" \
    "$(sed -n "s/^status_surf1_points	//p" "$CELL/cell.tsv")" \
    "${PGT:-na}" "${GGT:-na}" "$NOTE" >> "$SUM"
  [ "$RC" -eq 0 ] || FAILED="$FAILED $POT/$PIECE/arm$ARM"
  return 0
}

# SPEC is POT:PIECE or POT:PIECE:ARMS (e.g. Juglet:Juglet_Piece_5:ABC)
spec_arms() { case ${1#*:*} in *:*) echo "${1##*:}" | fold -w1 ;; *) echo A B C ;; esac; }
in_proof() {
  local P="$1:$2" S
  for S in $PROOF_LIST; do [ "$S" = "$P" ] && return 0; done
  return 1
}
for SPEC in $CELL_LIST; do
  POT=${SPEC%%:*}; PIECE=${SPEC#*:}; PIECE=${PIECE%%:*}
  ARMS="$(spec_arms "$SPEC")"
  if in_proof "$POT" "$PIECE"; then
    case "$ARMS" in *N*) : ;; *) ARMS="$ARMS N" ;; esac
  fi
  for ARM in $ARMS; do
    LEFT=$(budget_left)
    if [ "$LEFT" -lt "$MIN_LEFT_S" ]; then
      log "SKIP $POT/$PIECE arm $ARM: only ${LEFT}s of this script's ${CELL_BUDGET_S}s budget left"
      printf "%s\t%s\t%s\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\tonly ${LEFT}s left\n" \
        "$POT" "$PIECE" "$ARM" >> "$SUM"
      continue
    fi
    # a missing theta for B/C is recorded, not silently run at 3.4
    if { [ "$ARM" = "B" ] || [ "$ARM" = "C" ]; }; then
      COL=3; [ "$ARM" = "C" ] && COL=4
      TH=$(theta_of "$POT" "$PIECE" "$COL")
      if [ -z "$TH" ]; then
        log "SKIP $POT/$PIECE arm $ARM: no theta in $THETAS"
        printf "%s\t%s\t%s\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\tno theta for this arm\n" \
          "$POT" "$PIECE" "$ARM" >> "$SUM"
        continue
      fi
    fi
    run_arm "$POT" "$PIECE" "$ARM" || log "WARN arm $ARM on $POT/$PIECE did not complete"
  done
done

log "=== every cell, as recorded ==="
cat "$SUM"
log "=== the surfaces ==="
cat "$SURFSUM"
log "=== the corrected pair statistic ==="
cat "$PAIRSUM"
log "=== the nesting quantities ==="
cat "$NESTSUM"
log "=== the walls ==="
cat "$WALLSUM" 2>/dev/null || true

# ---- defaults-unchanged proof: arm N (a second no-env run) must reproduce arm A's
# SampledWithNormals md5.  Ticket 291 measured run-to-run spread on the unseeded sampler, so a
# mismatch is recorded as measured, not gated.
P=$PIPECELL/defaults_proof.tsv
printf "pot\tpiece\tA_sampled_md5\tN_sampled_md5\tsame\tA_sampled_points\tN_sampled_points\tA_outcome\tN_outcome\tA_s0s1\tN_s0s1\n" > "$P"
for SPEC in $PROOF_LIST; do
  POT=${SPEC%%:*}; PIECE=${SPEC#*:}
  CA=$PIPECELL/${PIECE}_armA/cell.tsv; CN=$PIPECELL/${PIECE}_armN/cell.tsv
  if [ -f "$CA" ] && [ -f "$CN" ]; then
    G() { sed -n "s/^$2	//p" "$1"; }
    AM=$(G "$CA" sampled_md5); NM=$(G "$CN" sampled_md5)
    S=same; [ "$AM" != "$NM" ] && S=DIFF
    printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s/%s\t%s/%s\n" \
      "$POT" "$PIECE" "$AM" "$NM" "$S" "$(G "$CA" sampled_points)" "$(G "$CN" sampled_points)" \
      "$(G "$CA" status_outcome)" "$(G "$CN" status_outcome)" \
      "$(G "$CA" status_surf0_points)" "$(G "$CA" status_surf1_points)" \
      "$(G "$CN" status_surf0_points)" "$(G "$CN" status_surf1_points)" >> "$P"
  else
    printf "%s\t%s\tmissing-A-or-N-cell\n" "$POT" "$PIECE" >> "$P"
  fi
done
log "=== defaults-unchanged proof (arm A vs a second no-env cell, arm N) ==="
cat "$P"

# ---- the theta switch proof: the paper grow line must carry the theta the arm asked for
SP=$PIPECELL/theta_proof.tsv
printf "pot\tpiece\tarm\trequested_theta\tpaper_grow_theta\tmatch\n" > "$SP"
for C in "$PIPECELL"/*/cell.tsv; do
  [ -f "$C" ] || continue
  POT=$(sed -n "s/^pot	//p" "$C"); PIECE=$(sed -n "s/^piece	//p" "$C"); ARM=$(sed -n "s/^arm	//p" "$C")
  REQ=$(sed -n "s/^env	//p" "$C" | sed -n "s/.*SFS_PAPER_THETA=\([^ ]*\).*/\1/p")
  [ -n "$REQ" ] || REQ=3.4
  GOT=$(sed -n "s/^paper_grow_first	//p" "$C" | sed -n "s/.*thetaDeg=\([^ ]*\).*/\1/p")
  M=no
  if [ -n "$GOT" ]; then
    M=$("$PY" -c "print('yes' if abs(float('$GOT')-float('$REQ'))<1e-9 else 'no')")
  fi
  printf "%s\t%s\t%s\t%s\t%s\t%s\n" "$POT" "$PIECE" "$ARM" "$REQ" "${GOT:-na}" "$M" >> "$SP"
done
log "=== theta switch proof ==="
cat "$SP"

if [ -n "$FAILED" ]; then
  log "FAILED cells:$FAILED"
  exit 8
fi
log "all cells ran"
log "done"
