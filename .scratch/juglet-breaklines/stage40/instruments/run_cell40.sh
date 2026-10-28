#!/bin/bash
# ticket 40 -- is own mode a general repair, or a two-piece coincidence?
#
# Ticket 39 proved the switch separates the two faces on the two silent Juglet sherds, on synthetic
# clouds.  This driver runs the SAME two-arm cell (A = radius control, B = own) over three groups:
#   g1  dense synthetic clouds, all nine Juglet sherds, mesh sampled at each piece's own spacing
#       (ticket 39's recipe), SFS_DOWNSAMPLE_TARGET pinned to the cloud size; pieces 2 and 9 are
#       CONTROL CELLS that must reproduce ticket 39 exactly before any other number is read;
#   g2  the released .pcd clouds of all nine Juglet sherds, NO downsample override;
#   g3  the released .pcd clouds of all eight Pot A pieces, NO downsample override -- the
#       regression control: a Pot A pair whose shared points rise above 0 is the regression line.
# Both arms of a piece run in the SAME job on the SAME staged cloud.  Nothing outside the run
# directory is written; the pipeline binary is built from the pushed commit by the sbatch wrapper.
set -uo pipefail

# CELL_LIST entries are GROUP:POT:PIECE:LEVEL:KIND, KIND in SYN|REAL (LEVEL is only used by SYN).
CELL_LIST=${CELL_LIST:-"g1:Juglet:Juglet_Piece_2:1:SYN g1:Juglet:Juglet_Piece_9:1:SYN"}
MIN_LEFT_S=${MIN_LEFT_S:-240}
CELL_BUDGET_S=${CELL_BUDGET_S:-1500}

: "${INSTR:?}" "${PY:?}" "${OUT:?}" "${GEOM:?}" "${MREG:?}" "${DS:?}" "${CORP:?}" "${BIN:?}"
: "${APT:?}" "${SIF:?}" "${STAGER:?}" "${RUN:?}" "${JOBID:?}"

MESH38=$INSTR/mesh38.py
GROW38=$INSTR/grow38.py
NEST39=$INSTR/nest39.py
WALL40=$INSTR/wall40.py
PIPECELL=$OUT/cells-pipeline
mkdir -p "$PIPECELL" "$MREG" "$GEOM" || exit 7

log() { echo "[CELL40] $*"; }
jget() { "$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])' "$1" "$2" 2>/dev/null || echo ""; }
jgetna() {
  local v
  v=$(jget "$1" "$2") || { echo na; return 0; }
  [ -z "$v" ] && { echo na; return 0; }
  [ "$v" = "None" ] && v=na
  printf "%s\n" "$v"
}
pcd_points() { grep -am1 "^POINTS" "$1" | awk '{print $2}'; }

# ---------------------------------------------------------------- anchors, per group and piece
# ticket 39's run 20261028-1624_ed0fc16 (g1), ticket 37 arm A (g2), the shipped default (g3).
anc_cloud_n()  { case "$2" in Juglet_Piece_2) echo 6259 ;; Juglet_Piece_9) echo 5257 ;; *) echo "" ;; esac; }
anc_cloud_mm() { case "$2" in Juglet_Piece_2) echo 0.209043 ;; Juglet_Piece_9) echo 0.201511 ;; *) echo "" ;; esac; }
anc_surf0() { case "$1/$2/$3" in
  g1/Juglet_Piece_2/A) echo 4155 ;; g1/Juglet_Piece_2/B) echo 4155 ;;
  g1/Juglet_Piece_9/A) echo 2229 ;; g1/Juglet_Piece_9/B) echo 2087 ;;
  g2/Juglet_Piece_1/A) echo 10800 ;; g2/Juglet_Piece_5/A) echo 229 ;;
  g2/Juglet_Piece_7/A) echo 1753 ;; g2/Juglet_Piece_3/A) echo one-cluster ;;
  g3/Pot_A_Piece_01/A) echo 66763 ;; g3/Pot_A_Piece_07/A) echo 24636 ;; g3/Pot_A_Piece_08/A) echo 26774 ;;
  *) echo "" ;; esac; }
anc_surf1() { case "$1/$2/$3" in
  g1/Juglet_Piece_2/A) echo 3979 ;; g1/Juglet_Piece_2/B) echo 3762 ;;
  g1/Juglet_Piece_9/A) echo 3512 ;; g1/Juglet_Piece_9/B) echo 3510 ;;
  g2/Juglet_Piece_1/A) echo 15780 ;; g2/Juglet_Piece_5/A) echo 2317 ;;
  g2/Juglet_Piece_7/A) echo 1997 ;; g2/Juglet_Piece_3/A) echo one-cluster ;;
  g3/Pot_A_Piece_01/A) echo 57286 ;; g3/Pot_A_Piece_07/A) echo 26739 ;; g3/Pot_A_Piece_08/A) echo 29286 ;;
  *) echo "" ;; esac; }
anc_shared() { case "$1/$2/$3" in
  g1/Juglet_Piece_2/A) echo 2352 ;; g1/Juglet_Piece_2/B) echo 0 ;;
  g1/Juglet_Piece_9/A) echo 1616 ;; g1/Juglet_Piece_9/B) echo 0 ;;
  g2/Juglet_Piece_1/A) echo 0 ;; g2/Juglet_Piece_5/A) echo 0 ;; g2/Juglet_Piece_7/A) echo 0 ;;
  g3/Pot_A_Piece_01/A) echo 0 ;; g3/Pot_A_Piece_07/A) echo 0 ;; g3/Pot_A_Piece_08/A) echo 0 ;;
  *) echo "" ;; esac; }
anc_dot()    { case "$1/$2/$3" in
  g1/Juglet_Piece_2/A) echo +0.9960274472338446 ;; g1/Juglet_Piece_2/B) echo -0.9993570511406065 ;;
  g1/Juglet_Piece_9/A) echo +0.9993183797978673 ;; g1/Juglet_Piece_9/B) echo -0.9999474210970047 ;;
  g2/Juglet_Piece_1/A) echo lt-0.9 ;; g2/Juglet_Piece_5/A) echo lt-0.9 ;; g2/Juglet_Piece_7/A) echo lt-0.9 ;;
  g3/Pot_A_Piece_01/A) echo lt-0.9 ;; g3/Pot_A_Piece_07/A) echo lt-0.9 ;; g3/Pot_A_Piece_08/A) echo lt-0.9 ;;
  *) echo "" ;; esac; }
# ticket 35's recorded wall medians (mm), reproduced by this run's own thickness step; g2/g3 cells
# are measured on the released clouds, which is the configuration ticket 35's rows came from.
anc_wall() { case "$1" in
  g2/Juglet_Piece_1) echo 2.35376 ;; g2/Juglet_Piece_2) echo 2.69305 ;; g2/Juglet_Piece_3) echo 2.4516 ;;
  g2/Juglet_Piece_5) echo 2.8998 ;; g2/Juglet_Piece_7) echo 3.26316 ;; g2/Juglet_Piece_9) echo 2.59484 ;;
  g3/Pot_A_Piece_01) echo 8.2857 ;; g3/Pot_A_Piece_07) echo 4.05609 ;;
  *) echo "" ;; esac; }

piece_mesh()  { if [ "$1" = "Pot_A" ]; then echo "$CORP/Mesh/$2_Mesh.obj"; else echo "$DS/Mesh/$1/$2_Mesh.obj"; fi; }
piece_cloud() { if [ "$1" = "Pot_A" ]; then echo "$CORP/Point/$1/$2_Point.pcd"; else echo "$DS/Point/$1/$2_Point.pcd"; fi; }
piece_axis()  { echo "$DS/Axes/$1/$2_Axis.xyz"; }

# ticket 39's spacing recipe, unchanged: mesh38's validate pass divides the shipped cloud's own
# median spacing by the level; the cloud's file name carries the spacing.
cloud_path() {
  local p=$1 l=$2 s0 s
  s0=$(jget "$MREG/sampler_validate_$p.json" shipped_median_mm)
  [ -n "$s0" ] || return 1
  s=$("$PY" -c "print('%.8f' % (float('$s0')/float('$l')))") || return 1
  echo "$GEOM/${p}_synthetic_x${l}_spacing_${s}.pcd"
}
cloud_spacing() {
  "$PY" -c 'import re,sys; print(re.search(r"spacing_([0-9.]+)\\.pcd$", sys.argv[1]).group(1))' "$1"
}

START_S=$(date +%s)
budget_left() { echo $(( CELL_BUDGET_S - ( $(date +%s) - START_S ) )); }

# ---------------------------------------------------------------- pass 1: the clouds, and the gate
# Only SYN samples; only pieces with a cloud anchor are gated (Juglet 2 and 9).  A gate failure on
# an anchored piece stops the whole run before any cell: a comparison against a different cloud is
# not the comparison the ticket asks for.  Pieces without anchors are recorded with na anchors.
GATE=$PIPECELL/cloud_gate.tsv
printf "group\tpiece\tpot\tlevel\tkind\texpected_points\tactual_points\texpected_mm\tactual_mm\tcount_ok\tspacing_ok\tgate\tcloud\tcloud_md5\n" > "$GATE"
GATE_FAILED=""
for SPEC in $CELL_LIST; do
  GROUP=${SPEC%%:*}; REST=${SPEC#*:}; POT=${REST%%:*}; REST2=${REST#*:}; PIECE=${REST2%%:*}; REST3=${REST2#*:}; LEVEL=${REST3%%:*}; KIND=${REST3##*:}
  MESH=$(piece_mesh "$POT" "$PIECE"); CLOUD0=$(piece_cloud "$POT" "$PIECE"); AXIS=$(piece_axis "$POT" "$PIECE")
  [ -f "$MESH" ] || { log "FATAL missing mesh $MESH"; GATE_FAILED="$GATE_FAILED $PIECE/mesh"; continue; }
  [ -f "$CLOUD0" ] || { log "FATAL missing cloud $CLOUD0"; GATE_FAILED="$GATE_FAILED $PIECE/cloud"; continue; }
  [ -f "$AXIS" ] || { log "FATAL missing axis $AXIS"; GATE_FAILED="$GATE_FAILED $PIECE/axis"; continue; }
  if [ "$KIND" = "SYN" ]; then
    VJ=$MREG/sampler_validate_$PIECE.json
    if [ ! -f "$VJ" ]; then
      log "sampler check against the shipped cloud: $PIECE"
      "$PY" "$MESH38" validate --mesh "$MESH" --cloud "$CLOUD0" --piece "$PIECE" --outdir "$MREG" \
        || log "WARN sampler check outside 5% on $PIECE (recorded, not hidden)"
    fi
    SYN=$(cloud_path "$PIECE" "$LEVEL") || { log "FATAL no sampler json for $PIECE"; GATE_FAILED="$GATE_FAILED $PIECE/nojson"; continue; }
    S=$(cloud_spacing "$SYN") || { log "FATAL cannot read the spacing out of $SYN"; GATE_FAILED="$GATE_FAILED $PIECE/spacing"; continue; }
    printf "%s\n" "$S" > "$MREG/spacing40_${PIECE}_x${LEVEL}.txt"
    log "sampling $PIECE x$LEVEL at $S mm -> $SYN"
    if [ ! -f "$SYN" ]; then
      "$PY" "$MESH38" sample --mesh "$MESH" --spacing "$S" --level "$LEVEL" --sample-from 1 \
        --piece "$PIECE" --outdir "$MREG" --out "$SYN" || { log "FATAL sample $PIECE"; GATE_FAILED="$GATE_FAILED $PIECE/sample"; continue; }
    fi
    SYNN=$(jget "$MREG/sample_${PIECE}_x${LEVEL}.json" points)
    [ -n "$SYNN" ] || { log "FATAL sample json $PIECE"; GATE_FAILED="$GATE_FAILED $PIECE/samplejson"; continue; }
    SYNACH=$(jget "$MREG/sample_${PIECE}_x${LEVEL}.json" achieved_median_mm)
    RUN_CLOUD=$SYN
    EXP_N=$(anc_cloud_n "$GROUP" "$PIECE"); EXP_MM=$(anc_cloud_mm "$GROUP" "$PIECE")
  else
    RUN_CLOUD=$CLOUD0
    SYNN=$(pcd_points "$RUN_CLOUD")
    SYNACH=na; S=na
    EXP_N=""; EXP_MM=""
    log "real released cloud $PIECE: $SYNN points, no downsample override"
  fi
  [ -n "$SYNN" ] || { log "FATAL no point count for $PIECE"; GATE_FAILED="$GATE_FAILED $PIECE/npts"; continue; }
  COUNT_OK=na; SPACE_OK=na; G=ok
  if [ -n "$EXP_N" ]; then
    COUNT_OK=no; [ "$SYNN" = "$EXP_N" ] && COUNT_OK=yes
    SPACE_OK=$("$PY" -c "import sys; e=float(sys.argv[1]); a=float(sys.argv[2]); print('yes' if abs(a-e)<=1e-6 else 'no')" "$EXP_MM" "$SYNACH")
    if [ "$COUNT_OK" != "yes" ] || [ "$SPACE_OK" != "yes" ]; then G=FAILED; GATE_FAILED="$GATE_FAILED $PIECE/cloud"; fi
  fi
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$GROUP" "$PIECE" "$POT" "$LEVEL" "$KIND" "${EXP_N:-na}" "$SYNN" "${EXP_MM:-na}" "$SYNACH" \
    "$COUNT_OK" "$SPACE_OK" "$G" "$RUN_CLOUD" "$(md5sum "$RUN_CLOUD" | cut -d' ' -f1)" >> "$GATE"
  log "cloud gate $GROUP/$PIECE: points $SYNN (anchor ${EXP_N:-na}) median $SYNACH mm (anchor ${EXP_MM:-na}) -> $G"
done
cat "$GATE"
if [ -n "$GATE_FAILED" ]; then
  log "STOP: an anchored cloud did not reproduce:$GATE_FAILED"
  log "no cell was run"
  exit 9
fi
log "clouds staged; the cells may run"

# ---------------------------------------------------------------- pass 2: the cells, two arms each
FAILED=""
SUM=$PIPECELL/pipeline_cells.tsv
printf "group\tpiece\tarm\tpot\tlevel\tcloud_kind\tcloud_points\trequested_mm\tachieved_mm\tpipeline_rc\tclusters\tspacing_policy\tstatus_outcome\tsurf0_points\tsurf1_points\tanchor_surf0\tanchor_surf1\tanchor_hit\tnote\n" > "$SUM"
SURFSUM=$PIPECELL/surfaces.tsv
printf "group\tpiece\tarm\tsurface\tpoints\tdistinct\text_x\text_y\text_z\tdiag\tcov_2mm\tfold_deg\tnormal_src\text\tply_bytes\n" > "$SURFSUM"
PAIRSUM=$PIPECELL/surface_pairs.tsv
printf "group\tpiece\tarm\tn0\tn1\tmed_nn\tmed_along\tmed_across\tmed_angle_deg\tcoin\tmed_t_signed\tp05_t_signed\tp95_t_signed\tnormal_src_a\tnormal_src_b\n" > "$PAIRSUM"
NESTSUM=$PIPECELL/nest.tsv
printf "group\tpiece\tarm\tn0\tn0_distinct\tn1\tn1_distinct\tshared\tshared_over_a\tshared_over_b\tshared_over_smaller\tmean_normal_dot\tmatched\tmedian_point_normal_angle_deg\tnormal_src_a\tnormal_src_b\n" > "$NESTSUM"
WALLSUM=$PIPECELL/walls.tsv
printf "group\tpiece\tcloud_pts\trays\tthick_med_mm\tthick_p10_mm\tthick_p90_mm\tanchor_med_mm\tabs_diff\tanchor_hit\tarm_ply\n" > "$WALLSUM"
XYZSUM=$PIPECELL/xyz_census.tsv
printf "group\tpiece\tarm\tsurface\twritten_ext\tmeasured\n" > "$XYZSUM"

run_arm() {
  local GROUP=$1 POT=$2 PIECE=$3 LEVEL=$4 ARM=$5 MODE=$6 KIND=$7
  local TAG CELL ST LOG RC=0 F K NCLUST
  local RUN_CLOUD SYNN SYNACH S
  TAG=${PIECE}_x${LEVEL}_arm${ARM}
  CELL=$PIPECELL/$TAG
  ST=$PIPECELL/stage_$TAG
  local MESH CLOUD AXIS
  MESH=$(piece_mesh "$POT" "$PIECE"); CLOUD=$(piece_cloud "$POT" "$PIECE"); AXIS=$(piece_axis "$POT" "$PIECE")
  if [ "$KIND" = "SYN" ]; then
    RUN_CLOUD=$(cloud_path "$PIECE" "$LEVEL") || { log "FATAL no sampler json for $PIECE"; return 1; }
    [ -f "$RUN_CLOUD" ] || { log "FATAL no synthetic cloud $RUN_CLOUD"; return 1; }
    SYNN=$(jget "$MREG/sample_${PIECE}_x${LEVEL}.json" points)
    [ -n "$SYNN" ] || { log "FATAL sample json"; return 1; }
    SYNACH=$(jget "$MREG/sample_${PIECE}_x${LEVEL}.json" achieved_median_mm)
    S=$(cat "$MREG/spacing40_${PIECE}_x${LEVEL}.txt" 2>/dev/null)
    [ -n "$S" ] || { log "FATAL no recorded spacing for $PIECE"; return 1; }
    KINDLABEL=SYNTHETIC
  else
    RUN_CLOUD=$CLOUD
    [ -f "$RUN_CLOUD" ] || { log "FATAL no released cloud $RUN_CLOUD"; return 1; }
    SYNN=$(pcd_points "$RUN_CLOUD")
    SYNACH=na; S=na
    KINDLABEL=REAL-RELEASED-CLOUD
  fi
  log "=============================================================="
  log "cell $GROUP/$PIECE ($POT) x$LEVEL arm $ARM SFS_REASSIGN_MODE=$MODE -> $CELL"
  log "the same cloud both arms see: $RUN_CLOUD ($SYNN points)"

  mkdir -p "$CELL/logs" "$CELL/surfaces" "$CELL/measure"
  bash "$STAGER" "$ST" "$POT" "$PIECE" "$AXIS" "$RUN_CLOUD" "$KINDLABEL" || { log "FATAL stage"; return 1; }
  cp -f "$ST/inputs.md5" "$CELL/inputs.md5"
  cat "$CELL/inputs.md5"

  LOG=$CELL/logs/mesh.log
  STATUS_RAW=$CELL/status_raw.tsv
  local ENVS="SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0 SFS_REASSIGN_MODE=$MODE"
  # group 1 pins the target to the synthetic cloud's own size; groups 2 and 3 set NOTHING so the
  # pipeline downsamples itself, exactly as it ships.
  [ "$KIND" = "SYN" ] && ENVS="$ENVS SFS_DOWNSAMPLE_TARGET=$SYNN"
  log "env: $ENVS"
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" \
      SFS_AXIS_FILE="$ST/Dataset/Axes/${PIECE}_Axis.xyz" \
      SFS_STATUS_FILE="$STATUS_RAW" $ENVS "$BIN" ) > "$LOG" 2>&1
  RC=$?
  log "pipeline rc=$RC log=$(stat -c %s "$LOG" 2>/dev/null || echo 0) bytes"
  [ -f "$LOG" ] || { log "FATAL no pipeline log (rc=$RC)"; return 1; }

  grep -E "\[(SPACING|COUNT|SPLITTER|SWITCH)-2[234]\]|\[(FLOOR|RETRY|SINGLE|STATUS)-23\]|\[NORMAL-3[34]\]|\[PAPER-234\]|\[DOWNSAMPLING|Number of clusters" \
    "$LOG" > "$CELL/logs/lines40.log" || true
  grep -E "\[REASSIGN-22\]|\[WINDOW-26" "$LOG" > "$CELL/logs/admission40.log" || true
  log "kept $(wc -l < "$CELL/logs/lines40.log") log lines and $(wc -l < "$CELL/logs/admission40.log") admission lines"
  sed -e 's/^/  admission: /' "$CELL/logs/admission40.log"

  NCLUST=$(grep -m1 "Number of clusters" "$LOG" | sed -n "s/.*equal to \([0-9]*\).*/\1/p")
  {
    echo "group	$GROUP"
    echo "piece	$PIECE"
    echo "arm	$ARM"
    echo "kind	$KIND"
    echo "reassign_mode	$MODE"
    echo "pot	$POT"
    echo "level	$LEVEL"
    echo "cloud_kind	$KINDLABEL"
    echo "cloud	$RUN_CLOUD"
    echo "cloud_md5	$(md5sum "$RUN_CLOUD" | cut -d' ' -f1)"
    echo "cloud_points	$SYNN"
    echo "cloud_achieved_spacing_mm	$SYNACH"
    echo "requested_spacing_mm	$S"
    echo "pipeline_rc	$RC"
    echo "pipeline_clusters	$NCLUST"
    echo "spacing_policy	$(grep -m1 "\[SPACING-22\]" "$LOG" | sed -n "s/.*policy=\([^ ]*\).*/\1/p")"
    echo "spacing_s0MM	$(grep -m1 "\[SPACING-22\]" "$LOG" | sed -n "s/.*s0MM=\([^ ]*\).*/\1/p")"
    echo "spacing_S	$(grep -m1 "\[SPACING-22\]" "$LOG" | sed -n "s/.* S=\([^ ]*\).*/\1/p")"
    echo "reassign_line	$(grep -m1 "\[REASSIGN-22\]" "$LOG")"
    echo "count_minCluster	$(grep -m1 "\[COUNT-22\]" "$LOG" | sed -n "s/.*minCluster=\([^ ]*\).*/\1/p")"
    echo "status_npts	$(grep -m1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*npts=\([^ ]*\).*/\1/p")"
    echo "status_floor	$(grep -m1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*floor=\([^ ]*\).*/\1/p")"
    echo "status_outcome	$(grep -m1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*outcome=\([^ ]*\).*/\1/p")"
    echo "status_surf0_points	$(grep -m1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*surf0_points=\([^ ]*\).*/\1/p")"
    echo "status_surf1_points	$(grep -m1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*surf1_points=\([^ ]*\).*/\1/p")"
    echo "retry_sizes	$(grep -m1 "\[RETRY-23\]" "$LOG" | sed -n "s/.*sizes=\([^ ]*\).*/\1/p")"
    echo "downsampling	$(grep -m1 "DOWNSAMPLING RESULT" "$LOG" | sed -n "s/.*Result=\([0-9]*\).*/\1/p")"
  } > "$CELL/cell.tsv"
  cat "$CELL/cell.tsv"

  # ---- wall thickness from this cell's own SampledWithNormals, before the stage is deleted
  ARMP=$ST/Temp/Data/$POT/${PIECE}_SampledWithNormals.ply
  if [ -f "$ARMP" ]; then
    WJ=$CELL/measure/wall_$TAG.json
    if "$PY" "$WALL40" --group "$GROUP" --pot "$POT" --piece "$PIECE" --mesh "$MESH" --arm "$ARMP" --out "$WJ"; then
      local WMED WP10 WP90 WANCM WABS WHIT
      WMED=$(jget "$WJ" thick_med_mm); WP10=$(jget "$WJ" thick_p10_mm); WP90=$(jget "$WJ" thick_p90_mm)
      WANCM=$(anc_wall "$GROUP/$PIECE")
      WABS=na; WHIT=na
      if [ -n "$WANCM" ]; then
        WABS=$("$PY" -c "print('%.5f' % abs(float('$WMED')-float('$WANCM')))")
        WHIT=$("$PY" -c "print('yes' if abs(float('$WMED')-float('$WANCM'))<=0.05*float('$WANCM') else 'no')")
      fi
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "$GROUP" "$PIECE" "$(jget "$WJ" cloud_pts)" "$(jget "$WJ" rays)" "$WMED" "$WP10" "$WP90" \
        "${WANCM:-na}" "$WABS" "$WHIT" "$ARMP" >> "$WALLSUM"
      log "wall $GROUP/$PIECE: med $WMED mm (anchor ${WANCM:-na}, diff $WABS)"
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
      printf "%s\t%s\t%s\t%s\tnone\tno\n" "$GROUP" "$PIECE" "$ARM" "$K" >> "$XYZSUM"
      continue
    fi
    cp -f "$F" "$CELL/surfaces/" 2>/dev/null || true
    log "surface $K: ${F##*.} $F ($(stat -c %s "$F" 2>/dev/null || echo 0) bytes)"
    printf "%s\t%s\t%s\t%s\t%s\t%s\n" "$GROUP" "$PIECE" "$ARM" "$K" "${F##*.}" "$([ "${F##*.}" = ply ] && echo yes || echo no)" >> "$XYZSUM"
    if [ "${F##*.}" != "ply" ]; then
      log "surface $K is ${F##*.} and no .ply was written beside it: cannot measure normals, kept as written"
      continue
    fi
    SJ=$CELL/measure/surface_${TAG}_Surface_$K.json
    DJ=$CELL/measure/distinct_${TAG}_Surface_$K.json
    if "$PY" "$GROW38" surface --ply "$F" --mesh "$MESH" --orig-cloud "$CLOUD" \
         --tag "${TAG}_Surface_$K" --outdir "$CELL/measure" \
       && "$PY" "$NEST39" count --ply "$F" --tag "${TAG}_Surface_$K" --outdir "$CELL/measure"; then
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%d\n" \
        "$GROUP" "$PIECE" "$ARM" "$K" "$(jget "$SJ" points)" "$(jget "$DJ" distinct)" \
        "$(jget "$SJ" ext_x)" "$(jget "$SJ" ext_y)" "$(jget "$SJ" ext_z)" \
        "$(jget "$SJ" diag)" "$(jget "$SJ" cov_2mm)" "$(jget "$SJ" fold_deg)" \
        "$(jget "$SJ" normal_src)" "ply" "$(stat -c %s "$F" 2>/dev/null || echo 0)" >> "$SURFSUM"
    else
      log "WARN surface $K not measured"
    fi
  done

  log "=== the pair statistic between the two surfaces this arm wrote ==="
  if [ -f "$CELL/surfaces/${PIECE}_Surface_0.ply" ] && [ -f "$CELL/surfaces/${PIECE}_Surface_1.ply" ]; then
    PJ=$CELL/measure/surfacepair_$TAG.json
    NJ=$CELL/measure/nest_$TAG.json
    if "$PY" "$GROW38" surfacepair --a "$CELL/surfaces/${PIECE}_Surface_0.ply" \
         --b "$CELL/surfaces/${PIECE}_Surface_1.ply" --tag "$TAG" --outdir "$CELL/measure" \
       && "$PY" "$NEST39" pair --a "$CELL/surfaces/${PIECE}_Surface_0.ply" \
         --b "$CELL/surfaces/${PIECE}_Surface_1.ply" --tag "$TAG" --outdir "$CELL/measure"; then
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "$GROUP" "$PIECE" "$ARM" "$(jget "$PJ" n0)" "$(jget "$PJ" n1)" "$(jget "$PJ" med_nn)" \
        "$(jget "$PJ" med_along)" "$(jget "$PJ" med_across)" "$(jget "$PJ" med_angle_deg)" \
        "$(jget "$PJ" coin)" "$(jget "$PJ" med_t_signed)" "$(jget "$PJ" p05_t_signed)" \
        "$(jget "$PJ" p95_t_signed)" "$(jget "$PJ" normal_src_a)" "$(jget "$PJ" normal_src_b)" \
        >> "$PAIRSUM"
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "$GROUP" "$PIECE" "$ARM" "$(jget "$NJ" n0)" "$(jget "$NJ" n0_distinct)" "$(jget "$NJ" n1)" \
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
  log "deleted stage $ST after the counted record above (cell surfaces and measures are KEPT)"

  local NOTE=ok AHIT=na S0A S1A G0 G1
  [ "$RC" -ne 0 ] && NOTE="pipeline rc=$RC"
  S0A=$(anc_surf0 "$GROUP" "$PIECE" "$ARM"); S1A=$(anc_surf1 "$GROUP" "$PIECE" "$ARM")
  G0=$(sed -n "s/^status_surf0_points	//p" "$CELL/cell.tsv")
  G1=$(sed -n "s/^status_surf1_points	//p" "$CELL/cell.tsv")
  if [ -n "$S0A" ]; then
    AHIT=no
    [ "$G0" = "$S0A" ] && [ "$G1" = "$S1A" ] && AHIT=yes
    if [ "$AHIT" = "yes" ]; then
      log "anchor $GROUP/$PIECE arm $ARM reproduced: $G0 / $G1"
    else
      log "anchor $GROUP/$PIECE arm $ARM NOT reproduced: got '$G0 / $G1', anchor '$S0A / $S1A'"
    fi
  fi
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$GROUP" "$PIECE" "$ARM" "$POT" "$LEVEL" "$KINDLABEL" "$SYNN" "$S" "$SYNACH" "$RC" \
    "${NCLUST:-na}" "$(sed -n "s/^spacing_policy	//p" "$CELL/cell.tsv")" \
    "$(sed -n "s/^status_outcome	//p" "$CELL/cell.tsv")" \
    "$G0" "$G1" "${S0A:-na}" "${S1A:-na}" "$AHIT" "$NOTE" >> "$SUM"
  [ "$RC" -eq 0 ] || FAILED="$FAILED $GROUP/$PIECE/arm$ARM"
  return 0
}

for SPEC in $CELL_LIST; do
  GROUP=${SPEC%%:*}; REST=${SPEC#*:}; POT=${REST%%:*}; REST2=${REST#*:}; PIECE=${REST2%%:*}; REST3=${REST2#*:}; LEVEL=${REST3%%:*}; KIND=${REST3##*:}
  LEFT=$(budget_left)
  if [ "$LEFT" -lt "$MIN_LEFT_S" ]; then
    log "SKIP $GROUP/$PIECE: only ${LEFT}s of this script's ${CELL_BUDGET_S}s budget left"
    printf "%s\t%s\tA,B\t%s\t%s\tSKIPPED\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\tonly %ss left\n" \
      "$GROUP" "$PIECE" "$POT" "$LEVEL" "$LEFT" >> "$SUM"
    continue
  fi
  log "wall clock left: ${LEFT}s"
  run_arm "$GROUP" "$POT" "$PIECE" "$LEVEL" A radius "$KIND" || log "WARN arm A on $GROUP/$PIECE did not complete"
  LEFT=$(budget_left)
  if [ "$LEFT" -lt 60 ]; then
    log "SKIP $GROUP/$PIECE arm B: only ${LEFT}s left"
    printf "%s\t%s\tB\t%s\t%s\tSKIPPED\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\tonly %ss left\n" \
      "$GROUP" "$PIECE" "$POT" "$LEVEL" "$LEFT" >> "$SUM"
    continue
  fi
  run_arm "$GROUP" "$POT" "$PIECE" "$LEVEL" B own "$KIND" || log "WARN arm B on $GROUP/$PIECE did not complete"
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
log "=== the xyz census ==="
cat "$XYZSUM"

# ---- the switch proof, counted from the cells' own recorded [REASSIGN-22] lines
PLANNED_A=0; PLANNED_B=0
for SPEC in $CELL_LIST; do
  PLANNED_A=$((PLANNED_A+1)); PLANNED_B=$((PLANNED_B+1))
done
GOT_A=0; GOT_B=0
for C in "$PIPECELL"/*/cell.tsv; do
  [ -f "$C" ] || continue
  if grep -q "	reassign_mode	radius" "$C" && grep -q "reassign_line	.*mode=radius" "$C"; then GOT_A=$((GOT_A+1)); fi
  if grep -q "	reassign_mode	own" "$C" && grep -q "reassign_line	.*mode=own" "$C"; then GOT_B=$((GOT_B+1)); fi
done
SW=$PIPECELL/switch_proof.tsv
printf "arm\tplanned\tmode_line_present\n" > "$SW"
printf "A\t%d\t%d\n" "$PLANNED_A" "$GOT_A" >> "$SW"
printf "B\t%d\t%d\n" "$PLANNED_B" "$GOT_B" >> "$SW"
log "=== the switch proof ==="
cat "$SW"

if [ -n "$FAILED" ]; then
  log "FAILED cells:$FAILED"
  exit 8
fi
log "all cells ran"
log "done"
