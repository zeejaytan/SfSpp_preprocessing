#!/bin/bash
# ticket 41 -- fix the pieces-4/6 loss and make own mode the default.
#
# Ticket 40 measured the whole vessel and found two things: own admission separates both faces on
# 9/9 Juglet sherds (radius nests on 8/9, Pot A untouched 8/8), but the ticket-37 adaptive-spacing
# default silently loses Juglet pieces 4 and 6 (one cluster, no surface).  This driver runs the
# FOUR-arm grid of ticket 41 on REAL RELEASED clouds only (no synthetic, no downsample override):
#   A  today exactly: adaptive spacing, radius admission, literal merge (the control; anchors from
#      ticket 40's g2/g3 arm A);
#   B  SFS_REASSIGN_MODE=own, literal merge -- the default-flip arm (proof 1 rides on arm A:
#      explicit radius on the NEW binary reproduces the pre-change numbers);
#   C  SFS_REASSIGN_MODE=own SFS_MERGE_SCALE=spacing -- the repair candidate for pieces 4/6;
#   D  SFS_SPACING_POLICY=fixed SFS_REASSIGN_MODE=own -- the revert arm that must restore pieces
#      4 and 6 to two surfaces (ticket 23 fixed-0.6 pairs 182/732 and 608/1016; with own admission
#      the counts may move, reported beside the recorded ones).
# Paid-for traps named here on purpose: CRLF (two grids died on "set: pipefail: invalid option
# name"); brace-stripping when a submit template renders (33875391); unbound variables under
# set -u (33874615, 33870012); xargs -n 2 splitting inside a line (33869854); a leading-tab grep
# gave a false switch-proof 0/9 (ticket 40) -- the switch-proof grep below is tested on a
# known-true line before it is counted.
set -uo pipefail

# CELL_LIST entries are POT:PIECE (all REAL released clouds).
CELL_LIST=${CELL_LIST:-"Juglet:Juglet_Piece_1"}
MIN_LEFT_S=${MIN_LEFT_S:-300}
CELL_BUDGET_S=${CELL_BUDGET_S:-9000}

: "${INSTR:?}" "${PY:?}" "${OUT:?}" "${MREG:?}" "${DS:?}" "${CORP:?}" "${BIN:?}"
: "${APT:?}" "${SIF:?}" "${STAGER:?}" "${RUN:?}" "${JOBID:?}"

GROW38=$INSTR/grow38.py
NEST39=$INSTR/nest39.py
WALL40=$INSTR/wall40.py
PIPECELL=$OUT/cells-pipeline
mkdir -p "$PIPECELL" "$MREG" || exit 7

log() { echo "[CELL41] $*"; }
jget() { "$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]))' "$1" "$2" 2>/dev/null || echo ""; }
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
  Juglet/Juglet_Piece_1/B) echo 532 ;; Juglet/Juglet_Piece_5/B) echo 0 ;;
  Juglet/Juglet_Piece_7/B) echo 10 ;; Juglet/Juglet_Piece_8/B) echo 0 ;;
  *) echo "" ;; esac; }
# ticket 35's recorded wall medians (mm)
anc_wall() { case "$1/$2" in
  Juglet/Juglet_Piece_1) echo 2.35376 ;; Juglet/Juglet_Piece_2) echo 2.69305 ;; Juglet/Juglet_Piece_3) echo 2.4516 ;;
  Juglet/Juglet_Piece_5) echo 2.8998 ;; Juglet/Juglet_Piece_7) echo 3.26316 ;; Juglet/Juglet_Piece_9) echo 2.59484 ;;
  Pot_A/Pot_A_Piece_01) echo 8.2857 ;; Pot_A/Pot_A_Piece_07) echo 4.05609 ;;
  *) echo "" ;; esac; }
# ticket 23 arm A, fixed 0.6 mm: the pair sizes arm D must restore (own admission may move them)
anc_pairD() { case "$1/$2" in
  Juglet/Juglet_Piece_4) echo "182/732" ;; Juglet/Juglet_Piece_6) echo "608/1016" ;;
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
  POT=${SPEC%%:*}; PIECE=${SPEC#*:}
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
printf "pot\tpiece\tarm\treassign\tmerge_scale\tspacing_policy\tcloud_points\tpipeline_rc\tclusters\tstatus_outcome\tsurf0_points\tsurf1_points\tanchor_surf0\tanchor_surf1\tanchor_hit\tanchor_shared\tgot_shared\tnote\n" > "$SUM"
SURFSUM=$PIPECELL/surfaces.tsv
printf "pot\tpiece\tarm\tsurface\tpoints\tdistinct\text_x\text_y\text_z\tdiag\tcov_2mm\tfold_deg\tnormal_src\text\tply_bytes\n" > "$SURFSUM"
PAIRSUM=$PIPECELL/surface_pairs.tsv
printf "pot\tpiece\tarm\tn0\tn1\tmed_nn\tmed_along\tmed_across\tmed_angle_deg\tcoin\tmed_t_signed\tp05_t_signed\tp95_t_signed\tnormal_src_a\tnormal_src_b\tanchor_pair\n" > "$PAIRSUM"
NESTSUM=$PIPECELL/nest.tsv
printf "pot\tpiece\tarm\tn0\tn0_distinct\tn1\tn1_distinct\tshared\tshared_over_a\tshared_over_b\tshared_over_smaller\tmean_normal_dot\tmatched\tmedian_point_normal_angle_deg\tnormal_src_a\tnormal_src_b\n" > "$NESTSUM"
WALLSUM=$PIPECELL/walls.tsv
printf "pot\tpiece\tarm\tcloud_pts\trays\tthick_med_mm\tthick_p10_mm\tthick_p90_mm\tanchor_med_mm\tabs_diff\tanchor_hit\tarm_ply\n" > "$WALLSUM"
MERGESUM=$PIPECELL/merge41.tsv
printf "pot\tpiece\tarm\tmerge_scale_line\tspacing_line\tn_clusters\tretry_sizes\tfinal_clusters\tfinal_sizes\tmerge_passes\n" > "$MERGESUM"

arm_env() {  # $1 arm -> prints the env assignments
  case "$1" in
    A) echo "SFS_REASSIGN_MODE=radius SFS_MERGE_SCALE=literal" ;;
    B) echo "SFS_REASSIGN_MODE=own SFS_MERGE_SCALE=literal" ;;
    C) echo "SFS_REASSIGN_MODE=own SFS_MERGE_SCALE=spacing" ;;
    D) echo "SFS_REASSIGN_MODE=own SFS_MERGE_SCALE=literal SFS_SPACING_POLICY=fixed" ;;
    *) return 1 ;;
  esac
}

run_arm() {
  local POT=$1 PIECE=$2 ARM=$3 MODE=$4 MSCALE=$5
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
  log "cell $POT/$PIECE arm $ARM reassign=$MODE merge_scale=$MSCALE -> $CELL"
  log "the same cloud every arm sees: $RUN_CLOUD ($SYNN points)"

  mkdir -p "$CELL/logs" "$CELL/surfaces" "$CELL/measure"
  bash "$STAGER" "$ST" "$POT" "$PIECE" "$AXIS" "$RUN_CLOUD" REAL-RELEASED-CLOUD || { log "FATAL stage"; return 1; }
  cp -f "$ST/inputs.md5" "$CELL/inputs.md5"
  cat "$CELL/inputs.md5"

  LOG=$CELL/logs/mesh.log
  STATUS_RAW=$CELL/status_raw.tsv
  local ENVS="SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0 $(arm_env "$ARM")"
  # arm D pins the pre-37 fixed spacing; A/B/C leave the policy unset (the shipped adaptive default)
  log "env: $ENVS"
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" \
      SFS_AXIS_FILE="$ST/Dataset/Axes/${PIECE}_Axis.xyz" \
      SFS_STATUS_FILE="$STATUS_RAW" $ENVS "$BIN" ) > "$LOG" 2>&1
  RC=$?
  log "pipeline rc=$RC log=$(stat -c %s "$LOG" 2>/dev/null || echo 0) bytes"
  [ -f "$LOG" ] || { log "FATAL no pipeline log (rc=$RC)"; return 1; }

  grep -aE "\[(SPACING|COUNT|SPLITTER|SWITCH)-2[234]\]|\[(FLOOR|RETRY|SINGLE|STATUS)-23\]|\[NORMAL-3[34]\]|\[PAPER-234\]|\[MERGE-41\]|\[REASSIGN-22\]|\[WINDOW-26|DOWNSAMPLING|Number of clusters" \
    "$LOG" > "$CELL/logs/lines41.log" || true
  log "kept $(wc -l < "$CELL/logs/lines41.log") key log lines (full mesh.log kept beside them)"

  NCLUST=$(grep -am1 "Number of clusters" "$LOG" | sed -n "s/.*equal to \([0-9]*\).*/\1/p")
  {
    echo "pot	$POT"
    echo "piece	$PIECE"
    echo "arm	$ARM"
    echo "reassign_mode	$MODE"
    echo "merge_scale	$MSCALE"
    echo "cloud	$RUN_CLOUD"
    echo "cloud_md5	$(md5sum "$RUN_CLOUD" | cut -d' ' -f1)"
    echo "cloud_points	$SYNN"
    echo "pipeline_rc	$RC"
    echo "pipeline_clusters	$NCLUST"
    echo "spacing_line	$(grep -am1 "\[SPACING-22\]" "$LOG" | tr -d '\r')"
    echo "merge41_line	$(grep -am1 "\[MERGE-41\]" "$LOG" | tr -d '\r')"
    echo "reassign_line	$(grep -am1 "\[REASSIGN-22\]" "$LOG" | tr -d '\r')"
    echo "status_npts	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*npts=\([^ ]*\).*/\1/p")"
    echo "status_outcome	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*outcome=\([^ ]*\).*/\1/p")"
    echo "status_surf0_points	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*surf0_points=\([^ ]*\).*/\1/p")"
    echo "status_surf1_points	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*surf1_points=\([^ ]*\).*/\1/p")"
    echo "retry_sizes	$(grep -am1 "\[RETRY-23\]" "$LOG" | sed -n "s/.*sizes=\([^ ]*\).*/\1/p")"
    echo "final_clusters	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*clusters=\([^ ]*\).*/\1/p")"
    echo "final_sizes	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*sizes=\([^ ]*\) npts.*/\1/p")"
    echo "merge_passes	$(grep -ac "merge " "$CELL/logs/lines41.log")"
  } > "$CELL/cell.tsv"
  cat "$CELL/cell.tsv"
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$POT" "$PIECE" "$ARM" "$(grep -am1 "\[MERGE-41\]" "$LOG" | tr -d '\r')" \
    "$(grep -am1 "\[SPACING-22\]" "$LOG" | tr -d '\r')" "${NCLUST:-na}" \
    "$(sed -n "s/^retry_sizes	//p" "$CELL/cell.tsv")" \
    "$(sed -n "s/^final_clusters	//p" "$CELL/cell.tsv")" \
    "$(sed -n "s/^final_sizes	//p" "$CELL/cell.tsv")" \
    "$(sed -n "s/^merge_passes	//p" "$CELL/cell.tsv")" >> "$MERGESUM"

  # ---- wall thickness from this cell's own SampledWithNormals, before the stage is deleted
  ARMP=$ST/Temp/Data/$POT/${PIECE}_SampledWithNormals.ply
  if [ -f "$ARMP" ]; then
    WJ=$CELL/measure/wall_$TAG.json
    if "$PY" "$WALL40" --group g41 --pot "$POT" --piece "$PIECE" --mesh "$MESH" --arm "$ARMP" --out "$WJ"; then
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
        "$(jget "$PJ" p95_t_signed)" "$(jget "$PJ" normal_src_a)" "$(jget "$PJ" normal_src_b)" \
        "${ANC_PAIR:-}" >> "$PAIRSUM"
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
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$POT" "$PIECE" "$ARM" "$MODE" "$MSCALE" \
    "$(sed -n "s/^spacing_line	//p" "$CELL/cell.tsv" | sed -n "s/.*policy=\([^ ]*\).*/\1/p")" \
    "$SYNN" "$RC" "${NCLUST:-na}" \
    "$(sed -n "s/^status_outcome	//p" "$CELL/cell.tsv")" \
    "$G0" "$G1" "${S0A:-na}" "${S1A:-na}" "$AHIT" "${ASH:-na}" "$GSH" "$NOTE" >> "$SUM"
  [ "$RC" -eq 0 ] || FAILED="$FAILED $POT/$PIECE/arm$ARM"
  return 0
}

for SPEC in $CELL_LIST; do
  POT=${SPEC%%:*}; PIECE=${SPEC#*:}
  for ARM in A B C D; do
    LEFT=$(budget_left)
    if [ "$LEFT" -lt "$MIN_LEFT_S" ]; then
      log "SKIP $POT/$PIECE arm $ARM: only ${LEFT}s of this script's ${CELL_BUDGET_S}s budget left"
      printf "%s\t%s\t%s\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\tonly %ss left\n" \
        "$POT" "$PIECE" "$ARM" "$LEFT" >> "$SUM"
      continue
    fi
    MODE=own; MSCALE=literal
    [ "$ARM" = "A" ] && MODE=radius
    [ "$ARM" = "C" ] && MSCALE=spacing
    ANC_PAIR=$(anc_pairD "$POT" "$PIECE") run_arm "$POT" "$PIECE" "$ARM" "$MODE" "$MSCALE" \
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
log "=== the merge/spacing rungs (merge41) ==="
cat "$MERGESUM"

# ---- the switch proof, counted from the cells' own recorded lines.
# Trap from ticket 40: a leading-tab grep gave a false 0/9.  So the grep is TESTED on a known-true
# line first: cell.tsv was written by this script with literal tab separators, and the first cell's
# own arm letter must be found by exactly the pattern the counting uses -- if that self-test fails,
# the proof is marked unreliable and the counting is not trusted.
SW=$PIPECELL/switch_proof.tsv
FIRST=$(ls "$PIPECELL"/*/cell.tsv 2>/dev/null | head -1)
SELFTEST=unreliable
FA=""
if [ -n "$FIRST" ]; then
  FA=$(sed -n "s/^arm	//p" "$FIRST" | head -1)
  if [ -n "$FA" ] && grep -qP "^arm	${FA}$" "$FIRST"; then SELFTEST=ok; fi
fi
NPLANNED=0
for SPEC in $CELL_LIST; do NPLANNED=$((NPLANNED+4)); done
{
  echo "grep_selftest	$SELFTEST	(first cell $FIRST, arm $FA)"
  for A in A B C D; do
    EXP_MODE=own; [ "$A" = "A" ] && EXP_MODE=radius
    EXP_SCALE=literal; [ "$A" = "C" ] && EXP_SCALE=spacing
    GOT=0
    for C in "$PIPECELL"/*/cell.tsv; do
      [ -f "$C" ] || continue
      if grep -qP "^arm	${A}$" "$C" \
         && grep -qP "^reassign_line	.*mode=${EXP_MODE}" "$C" \
         && grep -qP "^merge41_line	.*scale=${EXP_SCALE}" "$C" \
         && grep -qP "^merge41_line	.*rhod_eff=" "$C"; then GOT=$((GOT+1)); fi
    done
    # arm D must additionally show policy=fixed, arms A/B/C the adaptive (piece) policy
    POL_OK=0
    for C in "$PIPECELL"/*/cell.tsv; do
      [ -f "$C" ] || continue
      grep -qP "^arm	${A}$" "$C" || continue
      if [ "$A" = "D" ]; then
        grep -qP "^spacing_line	.*policy=fixed" "$C" && POL_OK=$((POL_OK+1))
      else
        grep -qP "^spacing_line	.*policy=piece" "$C" && POL_OK=$((POL_OK+1))
      fi
    done
    echo "arm${A}	planned_per_piece_cells=$NPLANNED mode+scale_lines=$GOT spacing_policy_ok=$POL_OK expected_mode=$EXP_MODE expected_scale=$EXP_SCALE"
  done
} > "$SW"
log "=== the switch proof ==="
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
