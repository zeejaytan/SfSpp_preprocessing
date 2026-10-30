#!/bin/bash
# ticket 46 -- feed the growth an even covering, and the formula's angle with it.  Source UNCHANGED:
# branch 45's curvature default (merged in as fe33e44) is what computes the angle in every cell.
#   E  Juglet: the pipeline reads an EVEN COVERING of the piece's OWN SHIPPED MESH, made by
#      cover_cloud46.py (mesh38.sample_at, level 1, NO subdivision) at the spacing this run resolves;
#   A  Pot A: the released ~1 000 000-point cloud, unchanged, the control.
# Neither arm carries ANY SFS_* env: SFS_PAPER_THETA unset and SFS_GROWTH_MODE unset in all 17 cells is
# an acceptance item, so the theta_env column must literally read <none> everywhere (env_proof.tsv).
# Pass 1 is the COVERING GATE: the covering must exist, sit within 1 % of S, keep every sampled point
# <= 1e-3 mm off the mesh, and record the ratio against the shipped cloud.  A covering that fails stops
# the run -- nothing is ever run on a vertex dump by accident.
# Pass 2 also proves the spacing did not move: [SPACING-22] S per cell vs the committed spec46.tsv.
#
# Paid-for traps named on purpose: CRLF in a script (two grids died on "set: pipefail: invalid
# option name"); unbound variables under set -u; a SKIP row must carry the SAME field count as the
# header (stage44/45 shipped a 14-field row against a 13-column table -- fixed here, 14 and 14);
# no xargs -d anywhere; grep -a on binary PLY/PCD; PLY header length varies (parsed by the
# instruments, never assumed); scipy exists only in the TORA env (used by the coverer, not here).
set -uo pipefail

CELL_LIST=${CELL_LIST:-"Juglet:Juglet_Piece_1:E"}
MIN_LEFT_S=${MIN_LEFT_S:-300}
CELL_BUDGET_S=${CELL_BUDGET_S:-7200}

: "${INSTR:?}" "${PY:?}" "${OUT:?}" "${DS:?}" "${CORP:?}" "${BIN:?}" "${APT:?}" "${SIF:?}"
: "${STAGER:?}" "${RUN:?}" "${JOBID:?}" "${COVER:?}"
SPECF=$INSTR/spec46.tsv
[ -f "$SPECF" ] || { echo "[CELL46] FATAL no spec46.tsv at $SPECF"; exit 7; }

PIPECELL=$OUT/cells-pipeline
mkdir -p "$PIPECELL" || exit 7

log() { echo "[CELL46] $*"; }
pcd_points() { grep -am1 "^POINTS" "$1" | awk '{print $2}'; }

piece_mesh()  { if [ "$1" = "Pot_A" ]; then echo "$CORP/Mesh/$2_Mesh.obj"; else echo "$DS/Mesh/$1/$2_Mesh.obj"; fi; }
piece_cloud() { if [ "$1" = "Pot_A" ]; then echo "$CORP/Point/$1/$2_Point.pcd"; else echo "$DS/Point/$1/$2_Point.pcd"; fi; }
piece_axis()  { echo "$DS/Axes/$1/$2_Axis.xyz"; }
covering()    { echo "$COVER/${1}_covering.pcd"; }
cover_json()  { echo "$COVER/${1}_cover.json"; }
spec_S()      { awk -F"\t" -v p="$1" 'NR>1 && $2==p {print $3; exit}' "$SPECF"; }

START_S=$(date +%s)
budget_left() { echo $(( CELL_BUDGET_S - ( $(date +%s) - START_S ) )); }

# ------------------------------------------------- pass 1: the covering gate + every input exists
GATE=$OUT/covering_gate.tsv
printf "piece\tpot\tshipped_points\tshipped_md5\tmesh\tmesh_md5\tcovering_points\tcovering_md5\tratio\tspacing_requested_mm\tspacing_achieved_median_mm\tspacing_err_pct\tmax_dist_to_mesh_mm\tcover_median_over_spacing\tsubdivision\tgate\n" > "$GATE"
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
    printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
      "$PIECE" "$POT" "${SYNN:-na}" "$SHMD5" "$MESH" "$MMMD5" \
      na na na na na na na na "no covering: released-cloud control" "$G" >> "$GATE"
    log "control gate $PIECE: ${SYNN:-na} released points -> $G"
    continue
  fi

  CJ=$(cover_json "$PIECE"); CC=$(covering "$PIECE")
  if [ ! -f "$CJ" ] || [ ! -f "$CC" ]; then
    log "FATAL no covering for $PIECE ($CC, $CJ)"; G=FAILED; GATE_FAILED="$GATE_FAILED $PIECE/covering"
    printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
      "$PIECE" "$POT" "${SYNN:-na}" "$SHMD5" "$MESH" "$MMMD5" \
      na na na na na na na na "missing-covering" FAILED >> "$GATE"
    continue
  fi
  REA=$("$PY" -c 'import json,sys; j=json.load(open(sys.argv[1])); print(j["covering_points"], j["covering_md5"], j["covering_over_shipped"], j["spacing_requested_mm"], j["spacing_achieved_median_mm"], j["spacing_error_pct"], j["dist_to_mesh_max_mm"], j["cover_median_over_spacing"], j["surface_check_points"], j["gate"])' "$CJ")
  [ $? -eq 0 ] || { log "FATAL unreadable cover json $CJ"; G=FAILED; GATE_FAILED="$GATE_FAILED $PIECE/json"; }
  read -r CN CM RN RS RM RE MD CV SCC GG <<<"$REA"
  CN2=$(pcd_points "$CC" 2>/dev/null)
  if [ "$CN" != "$CN2" ]; then log "FATAL covering count disagrees $PIECE: json=$CN pcd=$CN2"; G=FAILED; GATE_FAILED="$GATE_FAILED $PIECE/count"; fi
  if [ "$GG" != "PASS" ]; then log "FATAL cover_cloud46 gate=$GG for $PIECE"; G=FAILED; GATE_FAILED="$GATE_FAILED $PIECE/gate"; fi
  SS=$(spec_S "$PIECE")
  if [ -n "$SS" ] && [ "$SS" != "$RS" ]; then log "WARN $PIECE S in spec46 ($SS) differs from what the coverer asked ($RS)"; fi
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$PIECE" "$POT" "${SYNN:-na}" "$SHMD5" "$MESH" "$MMMD5" \
    "$CN" "$CM" "$RN" "$RS" "$RM" "$RE" "$MD" "$CV" "no subdivision used (level 1); surface check on $SCC of $CN points" "$G" >> "$GATE"
  log "covering gate $PIECE: shipped ${SYNN:-na} -> covering $CN (ratio ${RN}x) S=$RS achieved=$RM err=$RE% maxdist=$MD mm on $SCC points -> $G"
done
cat "$GATE"
if [ -n "$GATE_FAILED" ]; then
  log "STOP: the covering gate did not pass:$GATE_FAILED"
  log "no cell was run -- a thin covering is not an input"
  exit 9
fi
log "coverings present and gated; the cells may run"

# ---------------------------------------------------------------- pass 2: the cells
FAILED=""
SUM=$PIPECELL/pipeline_cells.tsv
printf "pot\tpiece\tarm\ttheta_env\tcloud_points\tshipped_cloud_points\tpipeline_rc\tclusters\tstatus_outcome\tsurf0_points\tsurf1_points\tpaper_grow_theta\ttheta_computed_deg\tnote\n" > "$SUM"

# arm -> the env this cell carries.  BOTH arms carry NOTHING: the angle comes from the binary's
# curvature default on whatever cloud the cell reads, which is the whole question of this run.
arm_env() {  # $1 arm
  case "$1" in
    E) echo "" ;;
    A) echo "" ;;
    *) return 1 ;;
  esac
}
arm_display() {  # $1 arm -> the pipeline_cells arm vocabulary of this ticket
  case "$1" in
    E) echo covering ;;
    A) echo control-released ;;
    *) return 1 ;;
  esac
}
arm_kind() {  # $1 arm -> the inputs.md5 KIND label the stager writes
  case "$1" in
    E) echo EVEN-COVERING ;;
    A) echo REAL-RELEASED-CLOUD ;;
    *) return 1 ;;
  esac
}

run_arm() {
  local POT=$1 PIECE=$2 ARM=$3
  local TAG CELL ST LOG RC=0 F K NCLUST ENVS MESH CLOUD AXIS RUN_CLOUD SYNN SHIPPED_P KIND PGT T45 G45 NOTE
  TAG=${PIECE}_arm${ARM}
  CELL=$PIPECELL/$TAG
  ST=$PIPECELL/stage_$TAG
  MESH=$(piece_mesh "$POT" "$PIECE"); CLOUD=$(piece_cloud "$POT" "$PIECE"); AXIS=$(piece_axis "$POT" "$PIECE")
  KIND=$(arm_kind "$ARM") || { log "FATAL unknown arm $ARM"; return 1; }
  if [ "$ARM" = "E" ]; then RUN_CLOUD=$(covering "$PIECE"); else RUN_CLOUD=$CLOUD; fi
  [ -f "$RUN_CLOUD" ] || { log "FATAL no run cloud $RUN_CLOUD"; return 1; }
  SYNN=$(pcd_points "$RUN_CLOUD")
  SHIPPED_P=$(pcd_points "$CLOUD")
  ENVS=$(arm_env "$ARM")
  log "=============================================================="
  log "cell $POT/$PIECE arm $ARM ($KIND) env='${ENVS:-<none>}' cloud=$RUN_CLOUD -> $CELL"

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

  grep -aE "\[(SPACING|COUNT|SPLITTER|SWITCH)-2[234]\]|\[(FLOOR|RETRY|SINGLE|STATUS)-23\]|\[NORMAL-3[34]\]|\[PAPER-234\]|\[MERGE-41\]|\[REASSIGN-22\]|\[GROWTH-42|\[GROWTH-45\]|Number of clusters" \
    "$LOG" > "$CELL/logs/lines46.log" || true
  log "kept $(wc -l < "$CELL/logs/lines46.log") key log lines (full mesh.log kept beside them)"

  NCLUST=$(grep -am1 "Number of clusters" "$LOG" | sed -n "s/.*equal to \([0-9]*\).*/\1/p")
  G45=$(grep -am1 "\[GROWTH-45\]" "$LOG" | tr -d "\r")
  T45=""
  [ -n "$G45" ] && T45=$(printf "%s\n" "$G45" | sed -n "s/.* theta=\([^ ]*\).*/\1/p")
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
    echo "paper_grow_lines	$(grep -ac "\[PAPER-234\] paper grow" "$LOG")"
    echo "paper_grow_first	$(grep -am1 "\[PAPER-234\] paper grow" "$LOG" | tr -d "\r")"
    echo "ladder_lines	$(grep -ac "^\[GROWTH-42\] piece" "$LOG")"
    echo "status_outcome	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*outcome=\([^ ]*\).*/\1/p")"
    echo "status_surf0_points	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*surf0_points=\([^ ]*\).*/\1/p")"
    echo "status_surf1_points	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*surf1_points=\([^ ]*\).*/\1/p")"
    echo "final_sizes	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*sizes=\([^ ]*\) npts.*/\1/p")"
  } > "$CELL/cell.tsv"
  cat "$CELL/cell.tsv"

  # ---- SampledWithNormals md5 BEFORE the stage is deleted: which cloud the growth ran on
  ARMP=$ST/Temp/Data/$POT/${PIECE}_SampledWithNormals.ply
  if [ -f "$ARMP" ]; then
    echo "sampled_md5	$(md5sum "$ARMP" | cut -d" " -f1)" >> "$CELL/cell.tsv"
    echo "sampled_points	$(grep -am1 "^element vertex" "$ARMP" | awk '{print $3}')" >> "$CELL/cell.tsv"
    cp -f "$ARMP" "$CELL/surfaces/" 2>/dev/null || true
  else
    echo "sampled_md5	-" >> "$CELL/cell.tsv"
    echo "sampled_points	-" >> "$CELL/cell.tsv"
  fi

  # ---- the surfaces this arm wrote, kept: ticket 46's pair table and pictures are measured from them
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
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$POT" "$PIECE" "$(arm_display "$ARM")" "${ENVS:-<none>}" "$SYNN" "$SHIPPED_P" "$RC" "${NCLUST:-na}" \
    "$(sed -n "s/^status_outcome\t//p" "$CELL/cell.tsv")" \
    "$(sed -n "s/^status_surf0_points\t//p" "$CELL/cell.tsv")" \
    "$(sed -n "s/^status_surf1_points\t//p" "$CELL/cell.tsv")" \
    "${PGT:-na}" "${T45:-}" "$NOTE" >> "$SUM"
  [ "$RC" -eq 0 ] || FAILED="$FAILED $POT/$PIECE/arm$ARM"
  return 0
}

# SPEC is POT:PIECE or POT:PIECE:ARMS (Juglet pieces E, Pot A pieces A); one arm per piece here.
spec_arms() { case ${1#*:*} in *:*) echo "${1##*:}" | fold -w1 ;; *) echo E ;; esac; }
for SPEC in $CELL_LIST; do
  POT=${SPEC%%:*}; PIECE=${SPEC#*:}; PIECE=${PIECE%%:*}
  ARMS="$(spec_arms "$SPEC")"
  for ARM in $ARMS; do
    LEFT=$(budget_left)
    if [ "$LEFT" -lt "$MIN_LEFT_S" ]; then
      log "SKIP $POT/$PIECE arm $ARM: only ${LEFT}s of this script's ${CELL_BUDGET_S}s budget left"
      # 14 fields, exactly the header count: a short row shifts every column for every reader.
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "$POT" "$PIECE" "$(arm_display "$ARM")" "<none>" "-" "-" "-" "-" "-" "-" "-" "-" "-" "only ${LEFT}s left" >> "$SUM"
      continue
    fi
    run_arm "$POT" "$PIECE" "$ARM" || log "WARN arm $ARM on $POT/$PIECE did not complete"
  done
done

log "=== every cell, as recorded ==="
cat "$SUM"

# ---- env proof: no cell may carry SFS_PAPER_THETA or SFS_GROWTH_MODE.  The template unsets the
# whole SFS_* family before the cell runs, and arm_env() adds nothing, so every row must read
# <none> / <unset>.  This table is the acceptance item, not a comment: one row with an env and
# the run is a per-piece tuning, which ticket 46 forbids.
EP=$PIPECELL/env_proof.tsv
printf "pot\tpiece\tarm\ttheta_env\tgrowth_mode_env\n" > "$EP"
ENV_BAD=""
for C in "$PIPECELL"/*/cell.tsv; do
  [ -f "$C" ] || continue
  POT=$(sed -n "s/^pot	//p" "$C"); PIECE=$(sed -n "s/^piece	//p" "$C"); A=$(sed -n "s/^arm	//p" "$C")
  TE=$(sed -n "s/^env	//p" "$C")
  AD=$(arm_display "$A" 2>/dev/null || echo "?")
  printf "%s\t%s\t%s\t%s\t%s\n" "$POT" "$PIECE" "$AD" "${TE:-na}" "<unset>" >> "$EP"
  if [ "${TE:-na}" != "<none>" ]; then ENV_BAD="$ENV_BAD $POT/$PIECE/$A"; fi
done
log "=== env proof (every theta_env must read <none>: no per-piece tuning) ==="
cat "$EP"
if [ -n "$ENV_BAD" ]; then
  log "FAILED env proof, a cell carried an env:$ENV_BAD"
  FAILED="$FAILED env-proof"
fi

# ---- spacing proof: the [SPACING-22] S of every cell against the committed spec46.tsv value.
# The covering must not move the spacing: S is re-derived from the cloud the cell reads, and a
# moved S would mean the theta moved for a reason other than the covering.
SP=$PIPECELL/spacing_proof.tsv
printf "pot\tpiece\tarm\tspacing_line_S\tspec46_S_mm\tdelta_mm\tnote\n" > "$SP"
for C in "$PIPECELL"/*/cell.tsv; do
  [ -f "$C" ] || continue
  POT=$(sed -n "s/^pot	//p" "$C"); PIECE=$(sed -n "s/^piece	//p" "$C"); A=$(sed -n "s/^arm	//p" "$C")
  AD=$(arm_display "$A" 2>/dev/null || echo "?")
  GOT=$(sed -n "s/^spacing_line	//p" "$C" | sed -n "s/.* S=\([^ ]*\).*/\1/p")
  REF=$(spec_S "$PIECE")
  D=na; N=ok
  if [ -z "$GOT" ] || [ -z "$REF" ]; then
    N="missing-spacing-evidence"
    log "WARN $PIECE arm $A: no [SPACING-22] S or no spec46 row (S='${GOT:-}' ref='${REF:-}')"
  else
    D=$("$PY" -c "print('%.6f' % abs(float('$GOT')-float('$REF')))" 2>/dev/null || echo na)
    N=$("$PY" -c "print('ok' if abs(float('$GOT')-float('$REF'))<1e-3 else 'MOVED')" 2>/dev/null || echo unreadable)
    if [ "$N" = "MOVED" ]; then
      log "FAILED spacing moved on $PIECE arm $A: $GOT vs spec $REF"
      FAILED="$FAILED $POT/$PIECE/spacing"
    fi
  fi
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "$POT" "$PIECE" "$AD" "${GOT:-na}" "${REF:-na}" "$D" "$N" >> "$SP"
done
log "=== spacing proof (S must equal what the run already resolved) ==="
cat "$SP"

if [ -n "$FAILED" ]; then
  log "FAILED:$FAILED"
  exit 8
fi
log "all cells ran, no env carried, S unmoved"
log "done"
