#!/bin/bash
# ticket 42 -- set the growth angle by the outcome, not as a shipped constant.
#
# Two-arm grid on REAL RELEASED clouds (no synthetic, no downsample override):
#   A  today exactly: paper chain theta=3.4, radius admission, literal merge (the control;
#      anchors from ticket 40 g2/g3 and ticket 41 arm A);
#   B  the same env + SFS_GROWTH_MODE=outcome -- the bidirectional paperTheta ladder of
#      ticket 42 (single-delta design: the only difference is the growth mode).
#   R  reference control (pieces listed in REFLIST only): the SAME env as arm A run on the
#      PRE-change binary (REFBIN, commit REF_GIT7).  Proof 1 rides on A-vs-R: identical
#      SampledWithNormals md5 + identical [RETRY-23] sequences.
# Proof 2 rides on every cell: zero ladder lines in A/R logs, mode=angle in A/R, mode=outcome in B.
# Paid-for traps named here on purpose: CRLF (two grids died on "set: pipefail: invalid option
# name"); brace-stripping when a submit template renders (33875391); unbound variables under
# set -u (33874615, 33870012); xargs -n 2 splitting inside a line (33869854); a leading-tab grep
# gave a false switch-proof 0/9 (ticket 40) -- the switch-proof grep below is tested on a
# known-true line before it is counted.
set -uo pipefail

# CELL_LIST entries are POT:PIECE (all REAL released clouds).
CELL_LIST=${CELL_LIST:-"Juglet:Juglet_Piece_1"}
REFLIST=${REFLIST:-""}
MIN_LEFT_S=${MIN_LEFT_S:-300}
CELL_BUDGET_S=${CELL_BUDGET_S:-9000}

: "${INSTR:?}" "${PY:?}" "${OUT:?}" "${MREG:?}" "${DS:?}" "${CORP:?}" "${BIN:?}"
: "${APT:?}" "${SIF:?}" "${STAGER:?}" "${RUN:?}" "${JOBID:?}" "${REFBIN:?}" "${REF_GIT7:?}"

GROW38=$INSTR/grow38.py
NEST39=$INSTR/nest39.py
WALL40=$INSTR/wall40.py
PIPECELL=$OUT/cells-pipeline
mkdir -p "$PIPECELL" "$MREG" || exit 7

log() { echo "[CELL42] $*"; }
jget() { "$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])' "$1" "$2" 2>/dev/null || echo ""; }
jgetna() {
  local v
  v=$(jget "$1" "$2") || { echo na; return 0; }
  [ -z "$v" ] && { echo na; return 0; }
  [ "$v" = "None" ] && v=na
  printf "%s\n" "$v"
}
pcd_points() { grep -am1 "^POINTS" "$1" | awk '{print $2}'; }

# ---------------------------------------------------------------- anchors (ticket 40 g2/g3, arm A)
anc_surf0() { case "$1/$2/$3" in
  Juglet/Juglet_Piece_1/A) echo 10800 ;; Juglet/Juglet_Piece_5/A) echo 229 ;;
  Juglet/Juglet_Piece_7/A) echo 1753 ;; Juglet/Juglet_Piece_3/A) echo one-cluster ;;
  Juglet/Juglet_Piece_4/A) echo no-surface ;; Juglet/Juglet_Piece_6/A) echo no-surface ;;
  Pot_A/Pot_A_Piece_01/A) echo 66763 ;; Pot_A/Pot_A_Piece_07/A) echo 24636 ;; Pot_A/Pot_A_Piece_08/A) echo 26774 ;;
  *) echo "" ;; esac; }
anc_surf1() { case "$1/$2/$3" in
  Juglet/Juglet_Piece_1/A) echo 15780 ;; Juglet/Juglet_Piece_5/A) echo 2317 ;;
  Juglet/Juglet_Piece_7/A) echo 1997 ;; Juglet/Juglet_Piece_3/A) echo one-cluster ;;
  Juglet/Juglet_Piece_4/A) echo no-surface ;; Juglet/Juglet_Piece_6/A) echo no-surface ;;
  Pot_A/Pot_A_Piece_01/A) echo 57286 ;; Pot_A/Pot_A_Piece_07/A) echo 26739 ;; Pot_A/Pot_A_Piece_08/A) echo 29286 ;;
  *) echo "" ;; esac; }
# ticket 40 g2/g3 arm-A nest anchors (shared distinct points both ways)
anc_shared() { case "$1/$2/$3" in
  Juglet/Juglet_Piece_1/A) echo 5497 ;; Juglet/Juglet_Piece_5/A) echo 34 ;;
  Juglet/Juglet_Piece_7/A) echo 336 ;; Juglet/Juglet_Piece_8/A) echo 200 ;;
  *) echo "" ;; esac; }
# ticket 35's recorded wall medians (mm)
anc_wall() { case "$1/$2" in
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
  log "cloud gate $PIECE: $SYNN points -> $G"
done
cat "$GATE"
if [ -n "$GATE_FAILED" ]; then
  log "STOP: a staged input is missing:$GATE_FAILED"
  log "no cell was run"
  exit 9
fi
log "clouds present; the cells may run"

# ---------------------------------------------------------------- pass 2: the cells, four arms each
FAILED=""
SUM=$PIPECELL/pipeline_cells.tsv
printf "pot\tpiece\tarm\tgrowth_mode\tcloud_points\tpipeline_rc\tclusters\tstatus_outcome\tsurf0_points\tsurf1_points\tchosen_theta\tchosen_rule\trungs\tanchor_surf0\tanchor_surf1\tanchor_hit\tanchor_shared\tgot_shared\tnote\n" > "$SUM"
SURFSUM=$PIPECELL/surfaces.tsv
printf "pot\tpiece\tarm\tsurface\tpoints\tdistinct\text_x\text_y\text_z\tdiag\tcov_2mm\tfold_deg\tnormal_src\text\tply_bytes\n" > "$SURFSUM"
PAIRSUM=$PIPECELL/surface_pairs.tsv
printf "pot\tpiece\tarm\tn0\tn1\tmed_nn\tmed_along\tmed_across\tmed_angle_deg\tcoin\tmed_t_signed\tp05_t_signed\tp95_t_signed\tnormal_src_a\tnormal_src_b\tanchor_pair\n" > "$PAIRSUM"
NESTSUM=$PIPECELL/nest.tsv
printf "pot\tpiece\tarm\tn0\tn0_distinct\tn1\tn1_distinct\tshared\tshared_over_a\tshared_over_b\tshared_over_smaller\tmean_normal_dot\tmatched\tmedian_point_normal_angle_deg\tnormal_src_a\tnormal_src_b\n" > "$NESTSUM"
WALLSUM=$PIPECELL/walls.tsv
printf "pot\tpiece\tarm\tcloud_pts\trays\tthick_med_mm\tthick_p10_mm\tthick_p90_mm\tanchor_med_mm\tabs_diff\tanchor_hit\tarm_ply\n" > "$WALLSUM"

arm_env() {  # $1 arm -> prints the env assignments
  case "$1" in
    A) echo "SFS_REASSIGN_MODE=radius SFS_MERGE_SCALE=literal" ;;
    B) echo "SFS_REASSIGN_MODE=radius SFS_MERGE_SCALE=literal SFS_GROWTH_MODE=outcome" ;;
    R) echo "SFS_REASSIGN_MODE=radius SFS_MERGE_SCALE=literal" ;;
    *) return 1 ;;
  esac
}

run_arm() {
  local POT=$1 PIECE=$2 ARM=$3 MODE=$4 MSCALE=$5
  local THISBIN=$BIN
  [ "$ARM" = "R" ] && THISBIN=$REFBIN
  local TAG CELL ST LOG RC=0 F K NCLUST
  TAG=${PIECE}_arm${ARM}
  CELL=$PIPECELL/$TAG
  ST=$PIPECELL/stage_$TAG
  local MESH CLOUD AXIS RUN_CLOUD SYNN
  MESH=$(piece_mesh "$POT" "$PIECE"); CLOUD=$(piece_cloud "$POT" "$PIECE"); AXIS=$(piece_axis "$POT" "$PIECE")
  RUN_CLOUD=$CLOUD
  [ -f "$RUN_CLOUD" ] || { log "FATAL no released cloud $RUN_CLOUD"; return 1; }
  SYNN=$(pcd_points "$RUN_CLOUD")
  log "=============================================================="
  log "cell $POT/$PIECE arm $ARM growth=$MODE merge_scale=$MSCALE bin=$THISBIN ref=$REF_GIT7 -> $CELL"
  log "the same cloud every arm sees: $RUN_CLOUD ($SYNN points)"

  mkdir -p "$CELL/logs" "$CELL/surfaces" "$CELL/measure"
  bash "$STAGER" "$ST" "$POT" "$PIECE" "$AXIS" "$RUN_CLOUD" REAL-RELEASED-CLOUD || { log "FATAL stage"; return 1; }
  cp -f "$ST/inputs.md5" "$CELL/inputs.md5"
  cat "$CELL/inputs.md5"

  LOG=$CELL/logs/mesh.log
  STATUS_RAW=$CELL/status_raw.tsv
  local ENVS="SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0 $(arm_env "$ARM")"
  log "env: $ENVS"
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" \
      SFS_AXIS_FILE="$ST/Dataset/Axes/${PIECE}_Axis.xyz" \
      SFS_STATUS_FILE="$STATUS_RAW" $ENVS "$BIN" ) > "$LOG" 2>&1
  RC=$?
  log "pipeline rc=$RC log=$(stat -c %s "$LOG" 2>/dev/null || echo 0) bytes"
  [ -f "$LOG" ] || { log "FATAL no pipeline log (rc=$RC)"; return 1; }

  grep -aE "\[(SPACING|COUNT|SPLITTER|SWITCH)-2[234]\]|\[(FLOOR|RETRY|SINGLE|STATUS)-23\]|\[NORMAL-3[34]\]|\[PAPER-234\]|\[MERGE-41\]|\[REASSIGN-22\]|\[WINDOW-26|DOWNSAMPLING|Number of clusters" \
    "$LOG" > "$CELL/logs/lines42.log" || true
  log "kept $(wc -l < "$CELL/logs/lines42.log") key log lines (full mesh.log kept beside them)"

  # the ticket-42 ladder rungs of this cell, as their own table
  grep -a "^\[GROWTH-42\] piece" "$LOG" \
    | sed -n "s/^.*theta=\([0-9.]*\) clusters=\([0-9]*\) ge_floor=\([0-9]*\) largest=\([0-9]*\) second=\([0-9]*\) outcome=\([a-z]*\).*/theta=\1	clusters=\2	ge_floor=\3	largest=\4	second=\5	outcome=\6/p" \
    > "$CELL/ladder.tsv" || true

  NCLUST=$(grep -am1 "Number of clusters" "$LOG" | sed -n "s/.*equal to \([0-9]*\).*/\1/p")
  {
    echo "pot	$POT"
    echo "piece	$PIECE"
    echo "arm	$ARM"
    echo "growth_mode	$MODE"
    echo "binary	$THISBIN"
    echo "merge_scale	$MSCALE"
    echo "cloud	$RUN_CLOUD"
    echo "cloud_md5	$(md5sum "$RUN_CLOUD" | cut -d' ' -f1)"
    echo "cloud_points	$SYNN"
    echo "pipeline_rc	$RC"
    echo "pipeline_clusters	$NCLUST"
    echo "spacing_line	$(grep -am1 "\[SPACING-22\]" "$LOG" | tr -d '\r')"
    echo "merge41_line	$(grep -am1 "\[MERGE-41\]" "$LOG" | tr -d '\r')"
    echo "reassign_line	$(grep -am1 "\[REASSIGN-22\]" "$LOG" | tr -d '\r')"
    echo "mode42_line	$(grep -am1 "\[GROWTH-42-MODE\]" "$LOG" | tr -d '\r')"
    echo "final_theta	$(grep -am1 "\[GROWTH-42-FINAL\]" "$LOG" | sed -n "s/.*chosen_theta=\([^ ]*\).*/\1/p")"
    echo "final_rule	$(grep -am1 "\[GROWTH-42-FINAL\]" "$LOG" | sed -n "s/.*rule=\([^ ]*\).*/\1/p")"
    echo "final_line	$(grep -am1 "\[GROWTH-42-FINAL\]" "$LOG" | tr -d '\r')"
    echo "rung_lines	$(grep -ac "^\[GROWTH-42\] piece" "$LOG")"
    echo "retry_seq_md5	$(grep -a "RETRY-23" "$LOG" | md5sum | cut -d' ' -f1)"
    echo "status_npts	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*npts=\([^ ]*\).*/\1/p")"
    echo "status_outcome	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*outcome=\([^ ]*\).*/\1/p")"
    echo "status_surf0_points	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*surf0_points=\([^ ]*\).*/\1/p")"
    echo "status_surf1_points	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*surf1_points=\([^ ]*\).*/\1/p")"
    echo "retry_sizes	$(grep -am1 "\[RETRY-23\]" "$LOG" | sed -n "s/.*sizes=\([^ ]*\).*/\1/p")"
    echo "final_clusters	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*clusters=\([^ ]*\).*/\1/p")"
    echo "final_sizes	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*sizes=\([^ ]*\) npts.*/\1/p")"
    echo "merge_passes	$(grep -ac "merge " "$CELL/logs/lines42.log")"
  } > "$CELL/cell.tsv"
  cat "$CELL/cell.tsv"
  # ---- SampledWithNormals md5 BEFORE the stage is deleted (proof 1 compares A vs R)
  ARMP=$ST/Temp/Data/$POT/${PIECE}_SampledWithNormals.ply
  if [ -f "$ARMP" ]; then
    echo "sampled_md5	$(md5sum "$ARMP" | cut -d' ' -f1)" >> "$CELL/cell.tsv"
    echo "sampled_points	$(grep -am1 "^element vertex" "$ARMP" | awk '{print $3}')" >> "$CELL/cell.tsv"
  else
    echo "sampled_md5	-" >> "$CELL/cell.tsv"
    echo "sampled_points	-" >> "$CELL/cell.tsv"
  fi

  # ---- wall thickness from this cell's own SampledWithNormals, before the stage is deleted
  if [ -f "$ARMP" ]; then
    WJ=$CELL/measure/wall_$TAG.json
    if "$PY" "$WALL40" --group g42 --pot "$POT" --piece "$PIECE" --mesh "$MESH" --arm "$ARMP" --out "$WJ"; then
      local WMED WP10 WP90 WANCM WABS WHIT
      WMED=$(jget "$WJ" thick_med_mm); WP10=$(jget "$WJ" thick_p10_mm); WP90=$(jget "$WJ" thick_p90_mm)
      WANCM=$(anc_wall "$POT/$PIECE")
      WABS=na; WHIT=na
      if [ -n "$WANCM" ]; then
        WABS=$("$PY" -c "print('%.5f' % abs(float('$WMED')-float('$WANCM')))")
        WHIT=$("$PY" -c "print('yes' if abs(float('$WMED')-float('$WANCM'))<=0.05*float('$WANCM')) else 'no')")
      fi
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "$POT" "$PIECE" "$ARM" "$(jget "$WJ" cloud_pts)" "$(jget "$WJ" rays)" "$WMED" "$WP10" "$WP90" \
        "${WANCM:-na}" "$WABS" "$WHIT" "$ARMP" >> "$WALLSUM"
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
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%d\n" \
        "$POT" "$PIECE" "$ARM" "$K" "$(jget "$SJ" points)" "$(jget "$DJ" distinct)" \
        "$(jget "$SJ" ext_x)" "$(jget "$SJ" ext_y)" "$(jget "$SJ" ext_z)" \
        "$(jget "$SJ" diag)" "$(jget "$SJ" cov_2mm)" "$(jget "$SJ" fold_deg)" \
        "$(jget "$SJ" normal_src)" "ply" "$(stat -c %s "$F" 2>/dev/null || echo 0)" >> "$SURFSUM"
    else
      log "WARN surface $K not measured"
    fi
  done

  log "=== the pair statistic between the two surfaces this arm wrote ==="
  GOTPAIR=0
  if [ -f "$CELL/surfaces/${PIECE}_Surface_0.ply" ] && [ -f "$CELL/surfaces/${PIECE}_Surface_1.ply" ]; then
    PJ=$CELL/measure/surfacepair_$TAG.json
    NJ=$CELL/measure/nest_$TAG.json
    if "$PY" "$GROW38" surfacepair --a "$CELL/surfaces/${PIECE}_Surface_0.ply" \
         --b "$CELL/surfaces/${PIECE}_Surface_1.ply" --tag "$TAG" --outdir "$CELL/measure" \
       && "$PY" "$NEST39" pair --a "$CELL/surfaces/${PIECE}_Surface_0.ply" \
         --b "$CELL/surfaces/${PIECE}_Surface_1.ply" --tag "$TAG" --outdir "$CELL/measure"; then
      GOTPAIR=1
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "$POT" "$PIECE" "$ARM" "$(jget "$PJ" n0)" "$(jget "$PJ" n1)" "$(jget "$PJ" med_nn)" \
        "$(jget "$PJ" med_along)" "$(jget "$PJ" med_across)" "$(jget "$PJ" med_angle_deg)" \
        "$(jget "$PJ" coin)" "$(jget "$PJ" med_t_signed)" "$(jget "$PJ" p05_t_signed)" \
        "$(jget "$PJ" p95_t_signed)" "$(jget "$PJ" normal_src_a)" "$(jget "$PJ" normal_src_b)" >> "$PAIRSUM"
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "$POT" "$PIECE" "$ARM" "$(jget "$NJ" n0)" "$(jget "$NJ" n0_distinct)" "$(jget "$NJ" n1)" \
        "$(jget "$NJ" n1_distinct)" "$(jget "$NJ" shared)" "$(jget "$NJ" shared_over_a)" \
        "$(jget "$NJ" shared_over_b)" "$(jget "$NJ" shared_over_smaller)" \
        "$(jget "$NJ" mean_normal_dot)" "$(jget "$NJ" matched)" \
        "$(jgetna "$NJ" median_point_normal_angle_deg)" \
        "$(jget "$NJ" normal_src_a)" "$(jget "$NJ" normal_src_b)" >> "$NESTSUM"
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

  local NOTE=ok AHIT=na S0A S1A G0 G1 ASH GSH
  [ "$RC" -ne 0 ] && NOTE="pipeline rc=$RC"
  S0A=$(anc_surf0 "$POT" "$PIECE" "$ARM"); S1A=$(anc_surf1 "$POT" "$PIECE" "$ARM")
  ASH=$(anc_shared "$POT" "$PIECE" "$ARM")
  G0=$(sed -n "s/^status_surf0_points	//p" "$CELL/cell.tsv")
  G1=$(sed -n "s/^status_surf1_points	//p" "$CELL/cell.tsv")
  GSH=na
  if [ "$GOTPAIR" = "1" ] && [ -f "$CELL/measure/nest_$TAG.json" ]; then
    GSH=$(jget "$CELL/measure/nest_$TAG.json" shared)
  fi
  if [ -n "$S0A" ]; then
    AHIT=no
    case "$S0A" in
      no-surface) [ "$G0" = "-1" ] && AHIT=yes ;;
      one-cluster) [ "$(sed -n "s/^status_outcome	//p" "$CELL/cell.tsv")" != "two" ] && AHIT=yes ;;
      *) [ "$G0" = "$S0A" ] && [ "$G1" = "$S1A" ] && AHIT=yes ;;
    esac
    if [ "$AHIT" = "yes" ]; then
      log "anchor $POT/$PIECE arm $ARM reproduced: $G0 / $G1"
    else
      log "anchor $POT/$PIECE arm $ARM NOT reproduced: got '$G0 / $G1', anchor '$S0A / $S1A' (run-to-run spread on the unseeded sampler is the standing explanation; recorded, not gated)"
    fi
  fi
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$POT" "$PIECE" "$ARM" "$MODE" \
    "$SYNN" "$RC" "${NCLUST:-na}" \
    "$(sed -n "s/^status_outcome	//p" "$CELL/cell.tsv")" \
    "$G0" "$G1" \
    "$(sed -n "s/^final_theta	//p" "$CELL/cell.tsv")" \
    "$(sed -n "s/^final_rule	//p" "$CELL/cell.tsv")" \
    "$(sed -n "s/^rung_lines	//p" "$CELL/cell.tsv")" \
    "${S0A:-na}" "${S1A:-na}" "$AHIT" "${ASH:-na}" "$GSH" "$NOTE" >> "$SUM"
  [ "$RC" -eq 0 ] || FAILED="$FAILED $POT/$PIECE/arm$ARM"
  return 0
}

# SPEC is POT:PIECE or POT:PIECE:ARMS (e.g. Juglet:Juglet_Piece_5:AB) -- the optional third
# field selects a subset of arms, default A and B.  Pieces in REFLIST additionally get an R
# reference cell on the pre-change binary.
spec_arms() { case ${1#*:*} in *:*) echo "${1##*:}" | fold -w1 ;; *) echo A B ;; esac; }
in_reflist() {
  local P="$1:$2" S
  for S in $REFLIST; do [ "$S" = "$P" ] && return 0; done
  return 1
}
for SPEC in $CELL_LIST; do
  POT=${SPEC%%:*}; PIECE=${SPEC#*:}; PIECE=${PIECE%%:*}
  ARMS="$(spec_arms "$SPEC")"
  if in_reflist "$POT" "$PIECE"; then
    case "$ARMS" in *R*) : ;; *) ARMS="$ARMS R" ;; esac
  fi
  for ARM in $ARMS; do
    LEFT=$(budget_left)
    if [ "$LEFT" -lt "$MIN_LEFT_S" ]; then
      log "SKIP $POT/$PIECE arm $ARM: only ${LEFT}s of this script's ${CELL_BUDGET_S}s budget left"
      printf "%s\t%s\t%s\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\tonly %ss left\n" \
        "$POT" "$PIECE" "$ARM" "$LEFT" >> "$SUM"
      continue
    fi
    MODE=angle
    [ "$ARM" = "B" ] && MODE=outcome
    [ "$ARM" = "R" ] && MODE=angle-ref
    run_arm "$POT" "$PIECE" "$ARM" "$MODE" literal \
      || log "WARN arm $ARM on $POT/$PIECE did not complete"
  done
done

log "=== every cell, as recorded ==="
cat "$SUM"
log "=== the surfaces ==="
cat "$SURFSUM"
log "=== the pair statistic ==="
cat "$PAIRSUM"
log "=== the nesting quantities ==="
cat "$NESTSUM"
log "=== the walls ==="
cat "$WALLSUM" 2>/dev/null || true

# ---- proof 1: A vs R on the same piece -- identical SampledWithNormals md5 and identical
# [RETRY-23] sequences.  Ticket 291 measured run-to-run spread on the unseeded sampler, so a
# mismatch is recorded as measured, not gated.
P1=$PIPECELL/proof1.tsv
printf "piece\tcloud_md5_same\tA_sampled_md5\tR_sampled_md5\tsampled_md5_same\tA_retry_md5\tR_retry_md5\tretry_seq_same\tA_outcome\tR_outcome\tA_s0s1\tR_s0s1\n" > "$P1"
for SPEC in $REFLIST; do
  POT=${SPEC%%:*}; PIECE=${SPEC#*:}
  CA=$PIPECELL/${PIECE}_armA/cell.tsv; CR=$PIPECELL/${PIECE}_armR/cell.tsv
  if [ -f "$CA" ] && [ -f "$CR" ]; then
    G() { sed -n "s/^$2	//p" "$1"; }
    AMD=$(G "$CA" sampled_md5); RMD=$(G "$CR" sampled_md5)
    ART=$(G "$CA" retry_seq_md5); RRT=$(G "$CR" retry_seq_md5)
    CMD_S=same; [ "$(G "$CA" cloud_md5)" != "$(G "$CR" cloud_md5)" ] && CMD_S=DIFF
    MD_S=same; [ "$AMD" != "$RMD" ] && MD_S=DIFF
    RT_S=same; [ "$ART" != "$RRT" ] && RT_S=DIFF
    printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
      "$PIECE" "$CMD_S" "$AMD" "$RMD" "$MD_S" "$ART" "$RRT" "$RT_S" \
      "$(G "$CA" status_outcome)" "$(G "$CR" status_outcome)" \
      "$(G "$CA" status_surf0_points)/$(G "$CA" status_surf1_points)" \
      "$(G "$CR" status_surf0_points)/$(G "$CR" status_surf1_points)" >> "$P1"
  else
    printf "%s\tmissing-A-or-R-cell\n" "$PIECE" >> "$P1"
  fi
done
log "=== proof 1: A vs R (angle on the new binary vs the pre-change binary $REF_GIT7) ==="
cat "$P1"

# ---- proof 2 + the switch proof, counted from the cells' own recorded lines.  The greps are
# self-tested first (ticket 40: a leading-tab grep gave a false 0/9).
SW=$PIPECELL/switch_proof.tsv
FIRST=$(ls "$PIPECELL"/*/cell.tsv 2>/dev/null | head -1)
SELFTEST=unreliable
FA=""
if [ -n "$FIRST" ]; then
  FA=$(sed -n "s/^arm	//p" "$FIRST" | head -1)
  if [ -n "$FA" ] && grep -qP "^arm	${FA}$" "$FIRST"; then SELFTEST=ok; fi
fi
{
  echo "grep_selftest	$SELFTEST	(first cell $FIRST, arm $FA)"
  for A in A B R; do
    NL=0; NMODE=0; CELLS=0
    EXP_MODE=angle; [ "$A" = "B" ] && EXP_MODE=outcome
    for C in "$PIPECELL"/*/cell.tsv; do
      [ -f "$C" ] || continue
      grep -qP "^arm	${A}$" "$C" || continue
      CELLS=$((CELLS+1))
      TAGD=$(dirname "$C")
      L=$(grep -ac "^\[GROWTH-42\] piece" "$TAGD/logs/mesh.log" 2>/dev/null)
      NL=$((NL+${L:-0}))
      grep -qP "^mode42_line	.*mode=$EXP_MODE" "$C" && NMODE=$((NMODE+1))
    done
    echo "proof2	arm $A	cells $CELLS	ladder_lines_got $NL (expect 0 unless arm B)	mode=($EXP_MODE) mode_lines $NMODE"
  done
} > "$SW"
log "=== proof 2 + the switch proof ==="
cat "$SW"
if [ "$SELFTEST" != "ok" ]; then
  log "WARN switch-proof grep self-test FAILED: the counts above are not trusted; read cell.tsv directly"
fi

if [ -n "$FAILED" ]; then
  log "FAILED cells:$FAILED"
  exit 8
fi
log "all cells ran"
log "done"
