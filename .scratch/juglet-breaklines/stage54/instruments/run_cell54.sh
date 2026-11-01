#!/bin/bash
# ticket 54 -- THE WORNESS DIAL.  FOUR arms per piece in ONE job, on the REAL corpus clouds:
#   D   nothing set -- the shipped default (flat 3.4); NO GROWTH-45/51/WORNESS-54 line at all.
#   X   SFS_PAPER_THETA=3.4 -- the explicit flat-theta control; D must match it (thetas +
#       surface point counts; the mesh stage is unseeded, so geometry bytes are compared as
#       point counts, never raw).
#   W   SFS_WORNESS=0.9 -- the calibrated dial: [GROWTH-45] then [WORNESS-54] piece=
#       formula_theta= crossing= w= capped= theta=; must reproduce the t51/t52 capped thetas.
#   W7  SFS_WORNESS=0.7 -- the dial turned down; thetas must be <= arm W's.
# Plus TWO FATAL probes (Juglet_Piece_1 only, after the cells): SFS_WORNESS=0 and =abc must
# both exit non-zero with the [WORNESS-54] FATAL line and grow nothing.
# Pass 1 is the ticket-48 CORPUS-MANIFEST GATE (unchanged from ticket 53): md5 AND
# kept_points of every Juglet corpus cloud must equal MANIFEST_JUGLET_CC.tsv, and no
# *_covering.pcd may sit under the corpus Point trees.  Pot A released clouds are recorded,
# not gated (the unchanged control).
# Pass 2 env proof is POSITIVE: an apptainer env probe per cell records every SFS_* variable
# the process would see; D must see NO SFS_(GROWTH|PAPER|WORNESS) var, X exactly
# SFS_PAPER_THETA=3.4, W exactly SFS_WORNESS=0.9, W7 exactly SFS_WORNESS=0.7.
#
# Paid-for traps named on purpose (inherited from 44/45/46/48/51/53): CRLF in a script;
# unbound variables under set -u; a SKIP row must carry the SAME field count as the header
# (19 and 19 here); no xargs -d anywhere; grep -a on binary PLY/PCD; PLY header length varies.
set -uo pipefail

CELL_LIST=${CELL_LIST:-"Juglet:Juglet_Piece_1:D,X,W,W7"}
MIN_LEFT_S=${MIN_LEFT_S:-300}
CELL_BUDGET_S=${CELL_BUDGET_S:-42000}

: "${INSTR:?}" "${PY:?}" "${OUT:?}" "${DS:?}" "${CORP:?}" "${BIN:?}" "${APT:?}" "${SIF:?}"
: "${STAGER:?}" "${RUN:?}" "${JOBID:?}"
MANIFEST=$DS/Point/Juglet/MANIFEST_JUGLET_CC.tsv
[ -f "$MANIFEST" ] || { echo "[CELL54] FATAL no manifest at $MANIFEST"; exit 7; }

PIPECELL=$OUT/cells-pipeline
mkdir -p "$PIPECELL" || exit 7

log() { echo "[CELL54] $*"; }
pcd_points() { grep -am1 "^POINTS" "$1" | awk '{print $2}'; }

piece_mesh()  { if [ "$1" = "Pot_A" ]; then echo "$CORP/Mesh/$2_Mesh.obj"; else echo "$DS/Mesh/$1/$2_Mesh.obj"; fi; }
piece_cloud() { if [ "$1" = "Pot_A" ]; then echo "$CORP/Point/$1/$2_Point.pcd"; else echo "$DS/Point/$1/$2_Point.pcd"; fi; }
piece_axis()  { echo "$DS/Axes/$1/$2_Axis.xyz"; }

manifest_field() {
  awk -F"\t" -v piece="$1" -v fld="$2" '
    /^#/ { next }
    !seen { for (i=1;i<=NF;i++) col[$i]=i; want=col[fld]; seen=1; next }
    want && $1==piece { print $want; exit }
  ' "$MANIFEST"
}

START_S=$(date +%s)
budget_left() { echo $(( CELL_BUDGET_S - ( $(date +%s) - START_S ) )); }

# ------------------------------------------------- pass 1: the corpus-manifest gate
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
  log "no cell was run -- ticket 54 never measures an unverified corpus"
  exit 9
fi
log "corpus verified against the ticket-47 manifest; the cells may run"

# ---------------------------------------------------------------- pass 2: the cells
FAILED=""
SUM=$PIPECELL/pipeline_cells.tsv
printf "pot\tpiece\tarm\ttheta_env\tcloud_points\tshipped_cloud_points\tpipeline_rc\tclusters\tstatus_outcome\tsurf0_points\tsurf1_points\tsplitter_theta\ttheta45\tformula_theta\tcrossing_deg\tw\tcapped\tworn_theta\tnote\n" > "$SUM"

arm_env() {
  case "$1" in
    D)  echo "" ;;
    X)  echo "SFS_PAPER_THETA=3.4" ;;
    W)  echo "SFS_WORNESS=0.9" ;;
    W7) echo "SFS_WORNESS=0.7" ;;
    *) return 1 ;;
  esac
}
arm_display() {
  case "$1" in
    D)  echo default ;;
    X)  echo paper34 ;;
    W)  echo worn09 ;;
    W7) echo worn07 ;;
    *) return 1 ;;
  esac
}
arm_kind() {
  case "$1" in
    D|X|W|W7) echo REAL-RELEASED-CLOUD ;;
    *) return 1 ;;
  esac
}

run_arm() {
  local POT=$1 PIECE=$2 ARM=$3
  local TAG CELL ST LOG RC=0 F K NCLUST ENVS MESH CLOUD AXIS RUN_CLOUD SYNN SHIPPED_P KIND PGT T45 G45 G54 FT54 X54 W54 CAP54 TH54 NOTE SPLIT_T
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
  log "cell $POT/$PIECE arm $ARM ($KIND) env='${ENVS:-<none>}' cloud=$RUN_CLOUD -> $CELL"

  mkdir -p "$CELL/logs" "$CELL/surfaces"
  bash "$STAGER" "$ST" "$POT" "$PIECE" "$AXIS" "$RUN_CLOUD" "$KIND" || { log "FATAL stage"; return 1; }
  cp -f "$ST/inputs.md5" "$CELL/inputs.md5"
  cat "$CELL/inputs.md5"

  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" \
      SFS_AXIS_FILE="$ST/Dataset/Axes/${PIECE}_Axis.xyz" \
      SFS_STATUS_FILE="$CELL/status_raw.tsv" $ENVS env ) > "$CELL/env_probe.txt" 2>"$CELL/env_probe.err"
  PROBE_RC=$?
  grep -a -E "^SFS_(GROWTH_|PAPER_|WORNESS)" "$CELL/env_probe.txt" | sort > "$CELL/env_probe_sfs.txt" || true
  log "env probe rc=$PROBE_RC saw: [$(tr "\n" ";" < "$CELL/env_probe_sfs.txt")]"

  LOG=$CELL/logs/mesh.log
  STATUS_RAW=$CELL/status_raw.tsv
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" \
      SFS_AXIS_FILE="$ST/Dataset/Axes/${PIECE}_Axis.xyz" \
      SFS_STATUS_FILE="$STATUS_RAW" $ENVS "$BIN" ) > "$LOG" 2>&1
  RC=$?
  log "pipeline rc=$RC log=$(stat -c %s "$LOG" 2>/dev/null || echo 0) bytes"
  [ -f "$LOG" ] || { log "FATAL no pipeline log (rc=$RC)"; return 1; }

  grep -aE "\[(SPACING|COUNT|SPLITTER|SWITCH)-2[234]\]|\[(FLOOR|RETRY|SINGLE|STATUS)-23\]|\[NORMAL-3[34]\]|\[PAPER-234\]|\[MERGE-41\]|\[REASSIGN-22\]|\[GROWTH-42|\[GROWTH-45\]|\[GROWTH-51\]|\[WORNESS-54\]|Number of clusters" \
    "$LOG" > "$CELL/logs/lines54.log" || true
  log "kept $(wc -l < "$CELL/logs/lines54.log") key log lines (full mesh.log kept beside them)"

  NCLUST=$(grep -am1 "Number of clusters" "$LOG" | sed -n "s/.*equal to \([0-9]*\).*/\1/p")
  SPLIT_T=$(grep -am1 "\[SPLITTER-234\]" "$LOG" | tr -d "\r" | sed -n "s/.* theta=\([^ ]*\).*/\1/p")
  G45=$(grep -am1 "\[GROWTH-45\]" "$LOG" | tr -d "\r")
  T45=""
  [ -n "$G45" ] && T45=$(printf "%s\n" "$G45" | sed -n "s/.* theta=\([^ ]*\).*/\1/p")
  G54=$(grep -am1 "\[WORNESS-54\] piece=" "$LOG" | tr -d "\r")
  FT54=""; X54=""; W54=""; CAP54=""; TH54=""
  if [ -n "$G54" ]; then
    FT54=$(printf "%s\n" "$G54" | sed -n "s/.* formula_theta=\([^ ]*\).*/\1/p")
    X54=$(printf "%s\n" "$G54" | sed -n "s/.* crossing=\([^ ]*\).*/\1/p")
    W54=$(printf "%s\n" "$G54" | sed -n "s/.* w=\([^ ]*\).*/\1/p")
    CAP54=$(printf "%s\n" "$G54" | sed -n "s/.* capped=\([^ ]*\).*/\1/p")
    TH54=$(printf "%s\n" "$G54" | sed -n "s/.* theta=\([^ ]*\).*/\1/p")
  fi
  {
    echo "pot	$POT"
    echo "piece	$PIECE"
    echo "arm	$ARM"
    echo "env	${ENVS:-}"
    echo "env_probe_sfs	$(tr "\n" ";" < "$CELL/env_probe_sfs.txt")"
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
    echo "splitter_theta	$SPLIT_T"
    echo "growth45_line	$G45"
    echo "growth45_theta	$T45"
    echo "worness54_line	$G54"
    echo "worness54_formula_theta	$FT54"
    echo "worness54_crossing	$X54"
    echo "worness54_w	$W54"
    echo "worness54_capped	$CAP54"
    echo "worness54_theta	$TH54"
    echo "growth51_line	$(grep -am1 "\[GROWTH-51\]" "$LOG" | tr -d "\r")"
    echo "paper_grow_first	$(grep -am1 "\[PAPER-234\] paper grow" "$LOG" | tr -d "\r")"
    echo "status_outcome	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*outcome=\([^ ]*\).*/\1/p")"
    echo "status_surf0_points	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*surf0_points=\([^ ]*\).*/\1/p")"
    echo "status_surf1_points	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*surf1_points=\([^ ]*\).*/\1/p")"
    echo "final_sizes	$(grep -am1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*sizes=\([^ ]*\) npts.*/\1/p")"
  } > "$CELL/cell.tsv"
  cat "$CELL/cell.tsv"

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
  case "$ARM" in
    D)
      [ -n "$G45" ] && NOTE="$NOTE unexpected GROWTH-45 line (D sets nothing)"
      [ -n "$G54" ] && NOTE="$NOTE unexpected WORNESS-54 line (D sets nothing)"
      ;;
    X)
      [ -n "$G45" ] && NOTE="$NOTE unexpected GROWTH-45 line (X takes SFS_PAPER_THETA)"
      [ -n "$G54" ] && NOTE="$NOTE unexpected WORNESS-54 line (X takes SFS_PAPER_THETA)"
      ;;
    W|W7)
      [ -z "$T45" ] && NOTE="$NOTE no GROWTH-45 line"
      [ -z "$G54" ] && NOTE="$NOTE no WORNESS-54 line"
      [ -n "$(grep -am1 "\[GROWTH-51\]" "$LOG")" ] && NOTE="$NOTE unexpected GROWTH-51 line (the dial replaces CAP)"
      ;;
  esac
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$POT" "$PIECE" "$(arm_display "$ARM")" "${ENVS:-<none>}" "$SYNN" "$SHIPPED_P" "$RC" "${NCLUST:-na}" \
    "$(sed -n "s/^status_outcome\t//p" "$CELL/cell.tsv")" \
    "$(sed -n "s/^status_surf0_points\t//p" "$CELL/cell.tsv")" \
    "$(sed -n "s/^status_surf1_points\t//p" "$CELL/cell.tsv")" \
    "${SPLIT_T:-na}" "${T45:-}" "${FT54:--}" "${X54:--}" "${W54:--}" "${CAP54:--}" "${TH54:--}" "$NOTE" >> "$SUM"
  [ "$RC" -eq 0 ] || FAILED="$FAILED $POT/$PIECE/arm$ARM"
  return 0
}

# SPEC is POT:PIECE or POT:PIECE:ARMS with ARMS comma-separated (D,X,W,W7)
spec_arms() { case ${1#*:*} in *:*) echo "${1##*:}" | tr ',' ' ' ;; *) echo "D X W W7" ;; esac; }
for SPEC in $CELL_LIST; do
  POT=${SPEC%%:*}; PIECE=${SPEC#*:}; PIECE=${PIECE%%:*}
  ARMS="$(spec_arms "$SPEC")"
  for ARM in $ARMS; do
    LEFT=$(budget_left)
    if [ "$LEFT" -lt "$MIN_LEFT_S" ]; then
      log "SKIP $POT/$PIECE arm $ARM: only ${LEFT}s of this script's ${CELL_BUDGET_S}s budget left"
      # 19 fields, exactly the header count
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "$POT" "$PIECE" "$(arm_display "$ARM" 2>/dev/null || echo "?")" "<none>" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "only ${LEFT}s left" >> "$SUM"
      continue
    fi
    run_arm "$POT" "$PIECE" "$ARM" || log "WARN arm $ARM on $POT/$PIECE did not complete"
  done
done

# ---------------- the FATAL probes: bad SFS_WORNESS values must exit non-zero, grow nothing
FATALPROBE=$OUT/worness_fatal_probes.tsv
printf "probe\tenv\trc\tfatal_line\tgrew_surface\n" > "$FATALPROBE"
for PV in 0 abc; do
  PROBE_CELL=$PIPECELL/probe_fatal_${PV}
  ST=$PIPECELL/stage_probe_fatal_${PV}
  mkdir -p "$PROBE_CELL/logs"
  PPIECE=Juglet_Piece_1; PPOT=Juglet
  bash "$STAGER" "$ST" "$PPOT" "$PPIECE" "$(piece_axis "$PPOT" "$PPIECE")" "$(piece_cloud "$PPOT" "$PPIECE")" REAL-RELEASED-CLOUD \
    || { log "WARN fatal probe $PV: stage failed"; printf "%s\tSFS_WORNESS=%s\tstage_fail\t\t\n" "$PV" "$PV" >> "$FATALPROBE"; continue; }
  LOG=$PROBE_CELL/logs/mesh.log
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$PPOT" \
      SFS_AXIS_FILE="$ST/Dataset/Axes/${PPIECE}_Axis.xyz" \
      SFS_WORNESS="$PV" "$BIN" ) > "$LOG" 2>&1
  PRC=$?
  FL=$(grep -am1 "WORNESS-54\] FATAL" "$LOG" | tr -d "\r")
  GREW=no
  [ -f "$ST/Temp/Data/$PPOT/${PPIECE}_Surface_0.ply" ] && GREW=yes
  printf "%s\tSFS_WORNESS=%s\t%s\t%s\t%s\n" "$PV" "$PV" "$PRC" "${FL:-MISSING}" "$GREW" >> "$FATALPROBE"
  cp -f "$LOG" "$PROBE_CELL/mesh.log" 2>/dev/null || true
  log "fatal probe SFS_WORNESS=$PV: rc=$PRC fatal_line=${FL:-MISSING} grew=$GREW"
  if [ "$PRC" -eq 0 ] || [ -z "$FL" ]; then
    FAILED="$FAILED fatal-probe-$PV"
  fi
  rm -rf "$ST"
done
cat "$FATALPROBE"

log "=== every cell, as recorded ==="
cat "$SUM"

# ---- env proof, POSITIVE
EP=$PIPECELL/env_proof.tsv
printf "pot\tpiece\tarm\ttheta_env\tenv_probe_sfs\n" > "$EP"
ENV_BAD=""
for C in "$PIPECELL"/*/cell.tsv; do
  [ -f "$C" ] || continue
  POT=$(sed -n "s/^pot\t//p" "$C"); PIECE=$(sed -n "s/^piece\t//p" "$C"); A=$(sed -n "s/^arm\t//p" "$C")
  TE=$(sed -n "s/^env\t//p" "$C")
  PR=$(sed -n "s/^env_probe_sfs\t//p" "$C")
  AD=$(arm_display "$A" 2>/dev/null || echo "?")
  printf "%s\t%s\t%s\t%s\t%s\n" "$POT" "$PIECE" "$AD" "${TE:-<none>}" "${PR:-}" >> "$EP"
  WANT=""
  [ "$A" = "X" ] && WANT="SFS_PAPER_THETA=3.4;"
  [ "$A" = "W" ] && WANT="SFS_WORNESS=0.9;"
  [ "$A" = "W7" ] && WANT="SFS_WORNESS=0.7;"
  if [ "${PR-<missing>}" != "$WANT" ]; then
    ENV_BAD="$ENV_BAD $POT/$PIECE/$A(saw:[$PR] want:[$WANT])"
  fi
done
log "=== env proof (D = nothing; X = PAPER_THETA=3.4; W = WORNESS=0.9; W7 = WORNESS=0.7) ==="
cat "$EP"
if [ -n "$ENV_BAD" ]; then
  log "FAILED env proof, a cell's probe did not read exactly its arm env:$ENV_BAD"
  FAILED="$FAILED env-proof"
fi

# ---- theta proof: the paper-grow thetaDeg the log carried vs the theta the arm chose:
# D/X = 3.4 (the default / the override), W/W7 = the [WORNESS-54] theta (post-cap).
TP=$PIPECELL/theta_proof.tsv
printf "pot\tpiece\tarm\tpaper_grow_thetaDeg\ttheta_evidence\tdelta_abs\tnote\n" > "$TP"
for C in "$PIPECELL"/*/cell.tsv; do
  [ -f "$C" ] || continue
  POT=$(sed -n "s/^pot\t//p" "$C"); PIECE=$(sed -n "s/^piece\t//p" "$C"); A=$(sed -n "s/^arm\t//p" "$C")
  AD=$(arm_display "$A" 2>/dev/null || echo "?")
  PGT=$(sed -n "s/^paper_grow_first\t//p" "$C" | sed -n "s/.*thetaDeg=\([^ ]*\).*/\1/p")
  if [ "$A" = "W" ] || [ "$A" = "W7" ]; then EV=$(sed -n "s/^worness54_theta\t//p" "$C"); SRC=worness54
  else EV=3.4; SRC=override; fi
  D=na; N=ok
  if [ "$A" = "D" ]; then N="shipped default: theta is 3.4 by construction"; fi
  if [ "$A" = "X" ]; then N="SFS_PAPER_THETA override: theta is 3.4 by construction"; fi
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
log "all cells ran, every env probe read exactly its arm's SFS_* set, corpus == manifest"
log "done"
