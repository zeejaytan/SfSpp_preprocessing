#!/bin/bash
# ticket 39 -- does SFS_REASSIGN_MODE=own keep the two faces apart?
#
# Ticket 38 measured that the two surfaces the pipeline exports from a silent sherd are real but
# NEST: 95% / 80% of the smaller surface's points also appear in the larger, and the two mean
# normals point the SAME way.  Own mode changes the admission rule from "a point within this
# surface's 3 mm window joins this surface" to "... and this surface's spline is the nearer of the
# two", so this driver runs the SAME cloud twice per piece -- arm A the shipped radius mode as the
# control, arm B own mode -- and measures what ticket 39 asks for.
#
# The pipeline is not modified: it is built from the pushed commit and handed a synthetic cloud
# staged inside this run directory, labelled synthetic in every file name, table row and log line.
#
# The cloud is generated ONCE per piece and staged twice, so arm A and arm B cannot differ by a
# sampler draw.  Before any cell runs, each cloud is checked against ticket 38's own numbers; if it
# does not reproduce them this driver stops and says so, because a comparison against a different
# cloud is not the comparison the ticket asks for.  Arm A is then checked against ticket 38's
# per-surface point counts for the same reason.
set -uo pipefail

CELL_LIST=${CELL_LIST:-"Juglet:Juglet_Piece_2:1 Juglet:Juglet_Piece_9:1"}
MIN_LEFT_S=${MIN_LEFT_S:-300}
CELL_BUDGET_S=${CELL_BUDGET_S:-1500}

: "${INSTR:?}" "${PY:?}" "${OUT:?}" "${GEOM:?}" "${MREG:?}" "${DS:?}" "${CORP:?}" "${BIN:?}"
: "${APT:?}" "${SIF:?}" "${STAGER:?}" "${RUN:?}" "${JOBID:?}"

MESH38=$INSTR/mesh38.py
GROW38=$INSTR/grow38.py
NEST39=$INSTR/nest39.py
PIPECELL=$OUT/cells-pipeline
mkdir -p "$PIPECELL" "$MREG" "$GEOM" || exit 7

log() { echo "[CELL39] $*"; }
jget() { "$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])' "$1" "$2"; }
# a null in the json (the normal-angle has none when the two surfaces share no position) prints as
# na, so a table column is never the word "None" dressed up as a number
jgetna() {
  local v
  v=$(jget "$1" "$2") || { echo na; return 0; }
  [ "$v" = "None" ] && v=na
  printf "%s\n" "$v"
}
pcd_points() { grep -am1 "^POINTS" "$1" | awk '{print $2}'; }

# ticket 38's table, quoted from its issue file.  These are the numbers this driver must reproduce
# before its own cells mean anything: the cloud each piece must sample to, and the two surface
# point counts the control arm must return.
exp_cloud_points() { case "$1" in Juglet_Piece_2) echo 6259 ;; Juglet_Piece_9) echo 5257 ;; *) echo "" ;; esac; }
exp_cloud_mm()     { case "$1" in Juglet_Piece_2) echo 0.209043 ;; Juglet_Piece_9) echo 0.201511 ;; *) echo "" ;; esac; }
exp_ctrl_s0()      { case "$1" in Juglet_Piece_2) echo 4155 ;; Juglet_Piece_9) echo 2229 ;; *) echo "" ;; esac; }
exp_ctrl_s1()      { case "$1" in Juglet_Piece_2) echo 3979 ;; Juglet_Piece_9) echo 3512 ;; *) echo "" ;; esac; }

piece_mesh()  { echo "$DS/Mesh/$1/$2_Mesh.obj"; }
piece_cloud() { echo "$DS/Point/$1/$2_Point.pcd"; }
piece_axis()  { echo "$DS/Axes/$1/$2_Axis.xyz"; }

# The spacing is solved by mesh38's validate pass (the shipped cloud's own median spacing) and then
# divided by the level, exactly as stage 38 did; the cloud's file name carries the spacing so two
# clouds can never be confused for each other.
cloud_path() {
  local p=$1 l=$2 s0 s
  s0=$(jget "$MREG/sampler_validate_$p.json" shipped_median_mm) || return 1
  s=$("$PY" -c "print('%.8f' % (float('$s0')/float('$l')))") || return 1
  echo "$GEOM/${p}_synthetic_x${l}_spacing_${s}.pcd"
}

# the requested spacing is the number in the cloud's own file name, so a cloud and the request that
# produced it can never be separated
cloud_spacing() {
  "$PY" -c 'import re,sys; print(re.search(r"spacing_([0-9.]+)\.pcd$", sys.argv[1]).group(1))' "$1"
}

START_S=$(date +%s)
budget_left() { echo $(( CELL_BUDGET_S - ( $(date +%s) - START_S ) )); }

# ---------------------------------------------------------------- pass 1: the cloud, and its gate
GATE=$PIPECELL/cloud_gate.tsv
printf "piece\tpot\tlevel\texpected_points\tactual_points\texpected_mm\tactual_mm\tcount_ok\tspacing_ok\tgate\tcloud\tcloud_md5\n" > "$GATE"
GATE_FAILED=""
for SPEC in $CELL_LIST; do
  POT=${SPEC%%:*}; REST=${SPEC#*:}; PIECE=${REST%%:*}; LEVEL=${REST##*:}
  MESH=$(piece_mesh "$POT" "$PIECE"); CLOUD0=$(piece_cloud "$POT" "$PIECE")
  [ -f "$MESH" ] || { log "FATAL missing mesh $MESH"; GATE_FAILED="$GATE_FAILED $PIECE/mesh"; continue; }
  [ -f "$CLOUD0" ] || { log "FATAL missing cloud $CLOUD0"; GATE_FAILED="$GATE_FAILED $PIECE/cloud"; continue; }
  VJ=$MREG/sampler_validate_$PIECE.json
  if [ ! -f "$VJ" ]; then
    log "sampler check against the shipped cloud: $PIECE"
    "$PY" "$MESH38" validate --mesh "$MESH" --cloud "$CLOUD0" --piece "$PIECE" --outdir "$MREG" \
      || log "WARN sampler check outside 5% on $PIECE (recorded, not hidden)"
  fi
  SYN=$(cloud_path "$PIECE" "$LEVEL") || { log "FATAL no sampler json for $PIECE"; GATE_FAILED="$GATE_FAILED $PIECE/nojson"; continue; }
  S=$(cloud_spacing "$SYN") || { log "FATAL cannot read the spacing out of $SYN"; GATE_FAILED="$GATE_FAILED $PIECE/spacing"; continue; }
  printf "%s\n" "$S" > "$MREG/spacing39_${PIECE}_x${LEVEL}.txt"
  log "sampling $PIECE x$LEVEL at $S mm -> $SYN"
  if [ ! -f "$SYN" ]; then
    "$PY" "$MESH38" sample --mesh "$MESH" --spacing "$S" --level "$LEVEL" --sample-from 1 \
      --piece "$PIECE" --outdir "$MREG" --out "$SYN" || { log "FATAL sample $PIECE"; GATE_FAILED="$GATE_FAILED $PIECE/sample"; continue; }
  fi
  SYNN=$(jget "$MREG/sample_${PIECE}_x${LEVEL}.json" points) || { log "FATAL sample json $PIECE"; GATE_FAILED="$GATE_FAILED $PIECE/samplejson"; continue; }
  SYNACH=$(jget "$MREG/sample_${PIECE}_x${LEVEL}.json" achieved_median_mm)
  EXP_N=$(exp_cloud_points "$PIECE"); EXP_MM=$(exp_cloud_mm "$PIECE")
  COUNT_OK=no; SPACE_OK=no
  [ -n "$EXP_N" ] && [ "$SYNN" = "$EXP_N" ] && COUNT_OK=yes
  # ticket 38 quotes six decimals; 1e-6 mm is one unit in the last of them, i.e. "reproduces the
  # printed number" and nothing looser.  The table carries expected and actual side by side, so a
  # reader can see the exact delta rather than trusting this tolerance.
  SPACE_OK=$("$PY" -c "import sys; e=float(sys.argv[1]); a=float(sys.argv[2]); print('yes' if abs(a-e)<=1e-6 else 'no')" "${EXP_MM:-0}" "$SYNACH")
  G=ok
  if [ "$COUNT_OK" != "yes" ] || [ "$SPACE_OK" != "yes" ]; then G=FAILED; GATE_FAILED="$GATE_FAILED $PIECE/cloud"; fi
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$PIECE" "$POT" "$LEVEL" "${EXP_N:-na}" "$SYNN" "${EXP_MM:-na}" "$SYNACH" \
    "$COUNT_OK" "$SPACE_OK" "$G" "$SYN" "$(md5sum "$SYN" | cut -d' ' -f1)" >> "$GATE"
  log "cloud gate $PIECE: points $SYNN (ticket 38: ${EXP_N:-na}) median $SYNACH mm (ticket 38: ${EXP_MM:-na}) -> $G"
done
cat "$GATE"
if [ -n "$GATE_FAILED" ]; then
  log "STOP: the sampler did not reproduce ticket 38's clouds:$GATE_FAILED"
  log "no cell was run: a comparison against a different cloud is not the comparison ticket 39 asks for"
  exit 9
fi
log "both clouds reproduce ticket 38 exactly; the cells may run"

# ---------------------------------------------------------------- pass 2: the cells, two arms each
FAILED=""
SUM=$PIPECELL/pipeline_cells.tsv
printf "piece\tarm\tpot\tlevel\tcloud_kind\tcloud_points\trequested_mm\tachieved_mm\tpipeline_rc\tclusters\tspacing_policy\tstatus_outcome\tsurf0_points\tsurf1_points\tctrl38_surf0\tctrl38_surf1\tctrl38_reproduced\tnote\n" > "$SUM"
SURFSUM=$PIPECELL/surfaces.tsv
printf "piece\tarm\tsurface\tpoints\tdistinct\text_x\text_y\text_z\tdiag\tcov_2mm\tfold_deg\tnormal_src\tply_bytes\n" > "$SURFSUM"
PAIRSUM=$PIPECELL/surface_pairs.tsv
printf "piece\tarm\tn0\tn1\tmed_nn\tmed_along\tmed_across\tmed_angle_deg\tcoin\tmed_t_signed\tp05_t_signed\tp95_t_signed\tnormal_src_a\tnormal_src_b\n" > "$PAIRSUM"
NESTSUM=$PIPECELL/nest.tsv
printf "piece\tarm\tn0\tn0_distinct\tn1\tn1_distinct\tshared\tshared_over_a\tshared_over_b\tshared_over_smaller\tmean_normal_dot\tmatched\tmedian_point_normal_angle_deg\tnormal_src_a\tnormal_src_b\n" > "$NESTSUM"

run_arm() {
  local POT=$1 PIECE=$2 LEVEL=$3 ARM=$4 MODE=$5
  local TAG CELL ST LOG RC=0 F K NCLUST SJ PJ NJ DUMP
  local SYN SYNN SYNACH S
  TAG=${PIECE}_x${LEVEL}_arm${ARM}
  CELL=$PIPECELL/$TAG
  ST=$PIPECELL/stage_$TAG
  SYN=$(cloud_path "$PIECE" "$LEVEL") || { log "FATAL no sampler json for $PIECE"; return 1; }
  [ -f "$SYN" ] || { log "FATAL no synthetic cloud $SYN"; return 1; }
  SYNN=$(jget "$MREG/sample_${PIECE}_x${LEVEL}.json" points) || { log "FATAL sample json"; return 1; }
  SYNACH=$(jget "$MREG/sample_${PIECE}_x${LEVEL}.json" achieved_median_mm)
  # the spacing pass 1 gated and sampled at, not a fresh read of the file name: the two arms must
  # carry the same request in their tables as the gate approved
  S=$(cat "$MREG/spacing39_${PIECE}_x${LEVEL}.txt" 2>/dev/null) || { log "FATAL no recorded spacing for $PIECE"; return 1; }
  [ -n "$S" ] || { log "FATAL empty recorded spacing for $PIECE"; return 1; }
  local MESH CLOUD AXIS
  MESH=$(piece_mesh "$POT" "$PIECE"); CLOUD=$(piece_cloud "$POT" "$PIECE"); AXIS=$(piece_axis "$POT" "$PIECE")
  log "=============================================================="
  log "cell $PIECE ($POT) x$LEVEL arm $ARM SFS_REASSIGN_MODE=$MODE -> $CELL"
  log "the same cloud both arms see: $SYN ($SYNN points, achieved median $SYNACH mm)"

  mkdir -p "$CELL/logs" "$CELL/surfaces" "$CELL/measure"
  bash "$STAGER" "$ST" "$POT" "$PIECE" "$AXIS" "$SYN" SYNTHETIC || { log "FATAL stage"; return 1; }
  cp -f "$ST/inputs.md5" "$CELL/inputs.md5"
  cat "$CELL/inputs.md5"

  LOG=$CELL/logs/mesh.log
  STATUS_RAW=$CELL/status_raw.tsv
  local ENVS="SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0 SFS_DOWNSAMPLE_TARGET=$SYNN SFS_REASSIGN_MODE=$MODE"
  log "env: $ENVS"
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" \
      SFS_AXIS_FILE="$ST/Dataset/Axes/${PIECE}_Axis.xyz" \
      SFS_STATUS_FILE="$STATUS_RAW" SFS_DUMP_STAGE="$CELL/dump" $ENVS "$BIN" ) > "$LOG" 2>&1
  RC=$?
  log "pipeline rc=$RC log=$(stat -c %s "$LOG" 2>/dev/null || echo 0) bytes"
  [ -f "$LOG" ] || { log "FATAL no pipeline log (rc=$RC)"; return 1; }

  grep -E "\[(SPACING|COUNT|SPLITTER|SWITCH)-2[234]\]|\[(FLOOR|RETRY|SINGLE|STATUS)-23\]|\[NORMAL-3[34]\]|\[PAPER-234\]|\[DUMP-25\]|\[DOWNSAMPLING|Number of clusters" \
    "$LOG" > "$CELL/logs/lines39.log" || true
  # the admission rule itself, verbatim: [REASSIGN-22] once per cell and every [WINDOW-26*] line
  grep -E "\[REASSIGN-22\]|\[WINDOW-26" "$LOG" > "$CELL/logs/admission39.log" || true
  log "kept $(wc -l < "$CELL/logs/lines39.log") log lines and $(wc -l < "$CELL/logs/admission39.log") admission lines"
  sed -e 's/^/  admission: /' "$CELL/logs/admission39.log"

  NCLUST=$(grep -m1 "Number of clusters" "$LOG" | sed -n "s/.*equal to \([0-9]*\).*/\1/p")
  {
    echo "piece	$PIECE"
    echo "arm	$ARM"
    echo "reassign_mode	$MODE"
    echo "pot	$POT"
    echo "level	$LEVEL"
    echo "cloud_kind	SYNTHETIC"
    echo "cloud	$SYN"
    echo "cloud_md5	$(md5sum "$SYN" | cut -d' ' -f1)"
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
    echo "downsampling	$(grep -m1 "\[DOWNSAMPLING RESULT\]" "$LOG" | sed -n "s/.*Result=\([0-9]*\).*/\1/p")"
  } > "$CELL/cell.tsv"
  cat "$CELL/cell.tsv"

  log "=== the surfaces this arm wrote, measured against the ORIGINAL cloud and mesh ==="
  for K in 0 1; do
    F=""
    for ext in ply xyz; do
      if [ -f "$ST/Temp/Data/$POT/${PIECE}_Surface_${K}.${ext}" ]; then
        F=$ST/Temp/Data/$POT/${PIECE}_Surface_${K}.${ext}
        break
      fi
    done
    if [ -z "$F" ]; then log "surface $K: the pipeline wrote none"; continue; fi
    cp -f "$F" "$CELL/surfaces/" 2>/dev/null || true
    log "surface $K: ${F##*.} $F ($(stat -c %s "$F" 2>/dev/null || echo 0) bytes)"
    if [ "${F##*.}" != "ply" ]; then
      log "surface $K is ${F##*.} and no .ply was written beside it: cannot measure normals, kept as written"
      continue
    fi
    SJ=$CELL/measure/surface_${TAG}_Surface_${K}.json
    DJ=$CELL/measure/distinct_${TAG}_Surface_${K}.json
    if "$PY" "$GROW38" surface --ply "$F" --mesh "$MESH" --orig-cloud "$CLOUD" \
         --tag "${TAG}_Surface_${K}" --outdir "$CELL/measure" \
       && "$PY" "$NEST39" count --ply "$F" --tag "${TAG}_Surface_${K}" --outdir "$CELL/measure"; then
      printf "%s\t%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%d\n" \
        "$PIECE" "$ARM" "$K" "$(jget "$SJ" points)" "$(jget "$DJ" distinct)" \
        "$(jget "$SJ" ext_x)" "$(jget "$SJ" ext_y)" "$(jget "$SJ" ext_z)" \
        "$(jget "$SJ" diag)" "$(jget "$SJ" cov_2mm)" "$(jget "$SJ" fold_deg)" \
        "$(jget "$SJ" normal_src)" "$(stat -c %s "$F" 2>/dev/null || echo 0)" >> "$SURFSUM"
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
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "$PIECE" "$ARM" "$(jget "$PJ" n0)" "$(jget "$PJ" n1)" "$(jget "$PJ" med_nn)" \
        "$(jget "$PJ" med_along)" "$(jget "$PJ" med_across)" "$(jget "$PJ" med_angle_deg)" \
        "$(jget "$PJ" coin)" "$(jget "$PJ" med_t_signed)" "$(jget "$PJ" p05_t_signed)" \
        "$(jget "$PJ" p95_t_signed)" "$(jget "$PJ" normal_src_a)" "$(jget "$PJ" normal_src_b)" \
        >> "$PAIRSUM"
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "$PIECE" "$ARM" "$(jget "$NJ" n0)" "$(jget "$NJ" n0_distinct)" "$(jget "$NJ" n1)" \
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

  F=$ST/Temp/Data/$POT/${PIECE}_SampledWithNormals.ply
  if [ -f "$F" ]; then
    cp -f "$F" "$CELL/surfaces/" 2>/dev/null || true
    "$PY" - "$F" "$CELL/measure/sampled_spacing.json" "$INSTR" <<'PYEOF' || true
import json, sys
sys.path.insert(0, sys.argv[3])
import measure34 as M, mesh38 as S
d = M.read_ply(sys.argv[1])
xyz = M.ply_xyz(d)
sp = S.nn_spacing(xyz)
row = {"ply": sys.argv[1], "points": int(len(xyz)), "median_mm": sp["median"],
       "p10_mm": sp["p10"], "p90_mm": sp["p90"]}
json.dump(row, open(sys.argv[2], "w"), indent=1, sort_keys=True)
print("[CELL39] SampledWithNormals: points=%d median_nn=%.5f mm" % (len(xyz), sp["median"]))
PYEOF
  fi

  log "=== count the geometry this arm produced, then delete it ==="
  {
    find "$ST" "$CELL/dump" -type f -printf "%p\t%s\n" 2>/dev/null | awk -F"\t" '
      { n=split($1,a,"."); ext=(n>1?a[n]:"none");
        if (ext !~ /^(pcd|ply|xyz|obj|png|json)$/) ext="other";
        files[ext]++; bytes[ext]+=$2; tf++; tb+=$2 }
      END { printf "ext\tfiles\tbytes\n";
            for (e in files) printf "%s\t%d\t%d\n", e, files[e], bytes[e];
            printf "TOTAL\t%d\t%d\n", tf, tb }' | sort
  } > "$CELL/geometry_counts.tsv"
  cat "$CELL/geometry_counts.tsv"
  rm -rf "$ST" "$CELL/dump"
  log "deleted stage $ST and dump $CELL/dump after the counted record above"

  local NOTE=ok REPRO=na S0EXP S1EXP
  [ "$RC" -ne 0 ] && NOTE="pipeline rc=$RC"
  S0EXP=$(exp_ctrl_s0 "$PIECE"); S1EXP=$(exp_ctrl_s1 "$PIECE")
  if [ "$ARM" = "A" ]; then
    local G0 G1
    G0=$(sed -n "s/^status_surf0_points	//p" "$CELL/cell.tsv")
    G1=$(sed -n "s/^status_surf1_points	//p" "$CELL/cell.tsv")
    REPRO=no
    [ "$G0" = "$S0EXP" ] && [ "$G1" = "$S1EXP" ] && REPRO=yes
    if [ "$REPRO" = "yes" ]; then
      log "control $PIECE reproduces ticket 38 exactly: $G0 / $G1"
    else
      log "control $PIECE does NOT reproduce ticket 38: got $G0 / $G1, ticket 38 recorded $S0EXP / $S1EXP"
    fi
  fi
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$PIECE" "$ARM" "$POT" "$LEVEL" "SYNTHETIC" "$SYNN" "$S" "$SYNACH" "$RC" \
    "${NCLUST:-na}" "$(sed -n "s/^spacing_policy	//p" "$CELL/cell.tsv")" \
    "$(sed -n "s/^status_outcome	//p" "$CELL/cell.tsv")" \
    "$(sed -n "s/^status_surf0_points	//p" "$CELL/cell.tsv")" \
    "$(sed -n "s/^status_surf1_points	//p" "$CELL/cell.tsv")" \
    "${S0EXP:-na}" "${S1EXP:-na}" "$REPRO" "$NOTE" >> "$SUM"
  [ "$RC" -eq 0 ] || FAILED="$FAILED $PIECE/arm$ARM"
  return 0
}

# Both arms of a piece run in the SAME job, back to back: a control that ran in a different job
# than its test is not a control.  Arm A always runs first, so the control's evidence exists even
# if arm B dies.
for SPEC in $CELL_LIST; do
  POT=${SPEC%%:*}; REST=${SPEC#*:}; PIECE=${REST%%:*}; LEVEL=${REST##*:}
  LEFT=$(budget_left)
  if [ "$LEFT" -lt "$MIN_LEFT_S" ]; then
    log "SKIP $PIECE: only ${LEFT}s of this script's ${CELL_BUDGET_S}s budget left"
    printf "%s\tA,B\t%s\t%s\tSKIPPED\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\tonly %ss left\n" \
      "$PIECE" "$POT" "$LEVEL" "$LEFT" >> "$SUM"
    continue
  fi
  log "wall clock left: ${LEFT}s"
  run_arm "$POT" "$PIECE" "$LEVEL" A radius || log "WARN arm A on $PIECE did not complete"
  run_arm "$POT" "$PIECE" "$LEVEL" B own    || log "WARN arm B on $PIECE did not complete"
done

log "=== every cell, as recorded ==="
cat "$SUM"
log "=== the surfaces ==="
cat "$SURFSUM"
log "=== the pair statistic ==="
cat "$PAIRSUM"
log "=== the nesting quantities ==="
cat "$NESTSUM"
if [ -n "$FAILED" ]; then
  log "FAILED cells:$FAILED"
  exit 8
fi
log "all cells ran"
log "done"
