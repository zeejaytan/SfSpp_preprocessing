#!/bin/bash
# ticket 49 -- the fold radius measured over a FIXED PHYSICAL PATCH, not a neighbour count.
#
# Ticket 48 proved the curvature law theta = 3.3573 x S / R_fold does not transfer from the
# clouds it was calibrated on to the corpus clouds, and named the cause: medianFoldRadius45()
# took the k = 30 nearest neighbours, so the patch it fitted shrank with the point spacing
# (0.58-0.93x of its calibration radius) and theta came out 1.1-1.7x too steep.  This run feeds
# the SAME estimator a radius (SFS_PATCH_R_MM -> tree45.radiusSearch) so the patch is the same
# physical size on every cloud, and measures what the pair then does.
#
# TWO CLOUD SETS, TWO RADII, one job:
#   corpus    Juglet 1-9 on the ticket-47 corpus clouds + Pot A 01-08 released clouds (the
#             failing case of ticket 48; the pot is its own control, 8/8 two surfaces in 45/48).
#   attic     Juglet 1-9 on the archived 2026-09-25 vertex dumps (SfSpp/attic/
#             20261031-juglet-vertex-dumps) -- the ticket-45 calibration case, the regression
#             guard: the change must not silently move the case that already worked.
#   radii     1.0 mm (the k=30 patch the ticket-45 calibration actually used, 0.63-1.04 mm) and
#             1.5 mm (a larger patch: averages more surface, spans a real fold less faithfully).
#
# Pass 1 is the CORPUS-MANIFEST GATE: md5 of every Juglet corpus cloud must equal the pcd_md5 the
#   ticket-47 MANIFEST_JUGLET_CC.tsv records (column read BY HEADER NAME), and no *_covering.pcd
#   may sit anywhere under the corpus Point trees.  A cloud that fails stops the run before any
#   cell -- this run never measures an unverified corpus.  Pot A released clouds are recorded,
#   not gated (they are the unchanged control).
# Pass 1b is the ATTIC GATE: md5 of every archived vertex dump must equal the md5 its own
#   attic manifest.tsv records, or the calibration case is not the case ticket 45 measured.
# Pass 2 env proof: every cell must carry exactly SFS_GROWTH_FORMULA=1 and
#   SFS_PATCH_R_MM=<its own radius> (env_proof.tsv), and theta_proof.tsv records the paper-grow
#   thetaDeg against the formula theta for every cell.
#
# Paid-for traps named on purpose (inherited from 44/45/46/48): CRLF in a script (two grids died
# on "set: pipefail: invalid option name"); unbound variables under set -u; a SKIP row must carry
# the SAME field count as the header (17 and 17 here); no xargs -d anywhere; grep -a on binary
# PLY/PCD; PLY header length varies (parsed by the instruments, never assumed).
set -uo pipefail

CELL_LIST=${CELL_LIST:-"Juglet:Juglet_Piece_1"}
RADII=${RADII:-"1.0 1.5"}
CLOUDSETS=${CLOUDSETS:-"corpus attic"}
MIN_LEFT_S=${MIN_LEFT_S:-180}
CELL_BUDGET_S=${CELL_BUDGET_S:-3900}

: "${INSTR:?}" "${PY:?}" "${OUT:?}" "${DS:?}" "${CORP:?}" "${BIN:?}" "${APT:?}" "${SIF:?}"
: "${STAGER:?}" "${RUN:?}" "${JOBID:?}" "${ATTIC:?}"
MANIFEST=$DS/Point/Juglet/MANIFEST_JUGLET_CC.tsv
[ -f "$MANIFEST" ] || { echo "[CELL49] FATAL no manifest at $MANIFEST"; exit 7; }
ATTIC_MANIFEST=$ATTIC/manifest.tsv
[ -f "$ATTIC_MANIFEST" ] || { echo "[CELL49] FATAL no attic manifest at $ATTIC_MANIFEST"; exit 7; }

PIPECELL=$OUT/cells-pipeline
mkdir -p "$PIPECELL" || exit 7

log() { echo "[CELL49] $*"; }
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
attic_field() {  # $1 piece, $2 column name (md5, bytes) -- attic manifest has a 2-line header too
  awk -F"\t" -v piece="$1" -v fld="$2" '
    /^#/ { next }
    !seen { for (i=1;i<=NF;i++) col[$i]=i; want=col[fld]; seen=1; next }
    want && $1==piece { print $want; exit }
  ' "$ATTIC_MANIFEST"
}

START_S=$(date +%s)
budget_left() { echo $(( CELL_BUDGET_S - ( $(date +%s) - START_S ))); }

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

# ------------------------------------------------- pass 1b: the attic gate (the calibration case)
AGATE=$OUT/attic_gate.tsv
printf "piece\tcloud\tcloud_points\tcloud_md5\tmanifest_md5\tmanifest_bytes\tgate\tnote\n" > "$AGATE"
for SPEC in $CELL_LIST; do
  POT=${SPEC%%:*}; PIECE=${SPEC#*:}; PIECE=${PIECE%%:*}
  [ "$POT" = "Pot_A" ] && continue   # the pot has no attic dump: its released cloud IS the calibration input
  AC=$ATTIC/${PIECE}_Point.pcd
  G=ok
  if [ ! -f "$AC" ]; then
    log "FATAL attic dump missing $AC"; G=FAILED; GATE_FAILED="$GATE_FAILED $PIECE/attic-missing"
  fi
  AN=$(pcd_points "$AC" 2>/dev/null)
  AMD5=$(md5sum "$AC" 2>/dev/null | cut -d" " -f1)
  AMD5M=$(attic_field "$PIECE" md5)
  ABYT=$(attic_field "$PIECE" bytes)
  if [ -z "$AMD5M" ]; then
    log "FATAL $PIECE not in the attic manifest"; G=FAILED; GATE_FAILED="$GATE_FAILED $PIECE/not-in-attic"
  elif [ "$AMD5" != "$AMD5M" ]; then
    log "FATAL attic dump md5 moved on $PIECE: disk=$AMD5 manifest=$AMD5M"; G=FAILED; GATE_FAILED="$GATE_FAILED $PIECE/attic-md5"
  fi
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$PIECE" "$AC" "${AN:-na}" "${AMD5:-na}" "${AMD5M:-na}" "${ABYT:-na}" "$G" "archived 2026-09-25 vertex dump == attic manifest" >> "$AGATE"
  log "attic gate $PIECE: ${AN:-na} points, md5 ${AMD5:0:8} vs manifest ${AMD5M:-absent} -> $G"
done
cat "$AGATE"

if [ -n "$GATE_FAILED" ]; then
  log "STOP: an input gate did not pass:$GATE_FAILED"
  log "no cell was run -- this run never measures an unverified input"
  exit 9
fi
log "corpus verified against the ticket-47 manifest, attic verified against its own manifest"

# ---------------------------------------------------------------- pass 2: the cells
FAILED=""
SUM=$PIPECELL/pipeline_cells.tsv
printf "pot\tpiece\tarm\tpatch_r\tcloud_points\tshipped_cloud_points\tpipeline_rc\tclusters\tstatus_outcome\tsurf0_points\tsurf1_points\tpaper_grow_theta\ttheta_computed_deg\tr_med_mm\tskipped\tnote\n" > "$SUM"

# arm -> the env this cell carries.  Every cell of this run carries the FORMULA path AND an
# explicit patch radius: the angle is computed by the binary from the spacing and the fold radius
# of the cloud it reads, over a neighbourhood of SFS_PATCH_R_MM millimetres.
arm_env() {  # $1 radius
  case "$1" in
    1.0|1.5) echo "SFS_GROWTH_FORMULA=1 SFS_PATCH_R_MM=$1" ;;
    *) return 1 ;;
  esac
}
arm_kind() {  # $1 cloud set -> the inputs.md5 KIND label the stager writes
  case "$1" in
    corpus) echo REAL-RELEASED-CLOUD ;;
    attic)  echo REAL-ATTIC-CLOUD ;;
    *) return 1 ;;
  esac
}

run_arm() {
  local POT=$1 PIECE=$2 R=$3 CS=$4
  local TAG CELL ST LOG RC=0 F K NCLUST ENVS MESH CLOUD AXIS RUN_CLOUD SYNN SHIPPED_P KIND PGT T45 G45 NOTE RMED SKIP PR
  TAG=${PIECE}_r${R}_${CS}
  CELL=$PIPECELL/$TAG
  ST=$PIPECELL/stage_$TAG
  MESH=$(piece_mesh "$POT" "$PIECE"); CLOUD=$(piece_cloud "$POT" "$PIECE"); AXIS=$(piece_axis "$POT" "$PIECE")
  KIND=$(arm_kind "$CS") || { log "FATAL unknown cloud set $CS"; return 1; }
  if [ "$CS" = "attic" ]; then RUN_CLOUD=$ATTIC/${PIECE}_Point.pcd; else RUN_CLOUD=$CLOUD; fi
  [ -f "$RUN_CLOUD" ] || { log "FATAL no run cloud $RUN_CLOUD"; return 1; }
  SYNN=$(pcd_points "$RUN_CLOUD")
  SHIPPED_P=$(pcd_points "$CLOUD")
  ENVS=$(arm_env "$R") || { log "FATAL unknown radius $R"; return 1; }
  log "=============================================================="
  log "cell $POT/$PIECE radius $R cloud $CS env='${ENVS:-<none>}' cloud=$RUN_CLOUD -> $CELL"

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
    "$LOG" > "$CELL/logs/lines49.log" || true
  log "kept $(wc -l < "$CELL/logs/lines49.log") key log lines (full mesh.log kept beside them)"

  NCLUST=$(grep -am1 "Number of clusters" "$LOG" | sed -n "s/.*equal to \([0-9]*\).*/\1/p")
  G45=$(grep -am1 "\[GROWTH-45\]" "$LOG" | tr -d "\r")
  T45=""; RMED=""; SKIP=""; PR=""
  if [ -n "$G45" ]; then
    T45=$(printf "%s\n" "$G45" | sed -n "s/.* theta=\([^ ]*\).*/\1/p")
    RMED=$(printf "%s\n" "$G45" | sed -n "s/.* R_med=\([^ ]*\).*/\1/p")
    PR=$(printf "%s\n" "$G45" | sed -n "s/.* patch_r=\([^ ]*\).*/\1/p")
    SKIP=$(printf "%s\n" "$G45" | sed -n "s/.* skipped=\([^ ]*\).*/\1/p")
  fi
  {
    echo "pot	$POT"
    echo "piece	$PIECE"
    echo "arm	r${R}-${CS}"
    echo "patch_r_env	$R"
    echo "cloud_set	$CS"
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
    echo "r_med_mm	$RMED"
    echo "patch_r_logged	$PR"
    echo "skipped	$SKIP"
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

  # ---- the surfaces this cell wrote, kept: the pair table and the pictures are measured from them
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

  log "=== count the geometry this cell produced, then delete the stage ==="
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
  PGT=$(sed -n "s/^paper_grow_first	//p" "$CELL/cell.tsv" | sed -n "s/.*thetaDeg=\([^ ]*\).*/\1/p")
  [ -z "$T45" ] && NOTE="$NOTE no GROWTH-45 line"
  [ -z "$SKIP" ] && NOTE="$NOTE no skipped field"
  if [ -n "$PR" ] && [ "$PR" != "$R" ]; then NOTE="$NOTE patch_r logged $PR but asked $R"; fi
  # 17 fields, exactly the header count: a short row shifts every column for every reader.
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$POT" "$PIECE" "r${R}-${CS}" "$R" "$SYNN" "$SHIPPED_P" "$RC" "${NCLUST:-na}" \
    "$(sed -n "s/^status_outcome	//p" "$CELL/cell.tsv")" \
    "$(sed -n "s/^status_surf0_points	//p" "$CELL/cell.tsv")" \
    "$(sed -n "s/^status_surf1_points	//p" "$CELL/cell.tsv")" \
    "${PGT:-na}" "${T45:-}" "${RMED:-}" "${SKIP:-}" "$NOTE" >> "$SUM"
  [ "$RC" -eq 0 ] || FAILED="$FAILED $POT/$PIECE/r$R/$CS"
  return 0
}

# SPEC is POT:PIECE (every combination of RADII x CLOUDSETS is run for it); Pot A has no attic dump.
for SPEC in $CELL_LIST; do
  POT=${SPEC%%:*}; PIECE=${SPEC#*:}; PIECE=${PIECE%%:*}
  for R in $RADII; do
    for CS in $CLOUDSETS; do
      if [ "$CS" = "attic" ] && [ "$POT" = "Pot_A" ]; then continue; fi
      LEFT=$(budget_left)
      if [ "$LEFT" -lt "$MIN_LEFT_S" ]; then
        log "SKIP $POT/$PIECE r$R $CS: only ${LEFT}s of this script's ${CELL_BUDGET_S}s budget left"
        # 17 fields, exactly the header count: a short row shifts every column for every reader.
        printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
          "$POT" "$PIECE" "r${R}-${CS}" "$R" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "only ${LEFT}s left" >> "$SUM"
        continue
      fi
      run_arm "$POT" "$PIECE" "$R" "$CS" || log "WARN cell $POT/$PIECE r$R $CS did not complete"
    done
  done
done

log "=== every cell, as recorded ==="
cat "$SUM"

# ---- env proof: every cell must carry exactly SFS_GROWTH_FORMULA=1 and its own SFS_PATCH_R_MM
# (the template unsets everything else SFS_*).  This table is the acceptance item, not a comment:
# one row reading anything else and the run is not the formula path at the radius it claims.
EP=$PIPECELL/env_proof.tsv
printf "pot\tpiece\tarm\tpatch_r\ttheta_env\tnote\n" > "$EP"
ENV_BAD=""
for C in "$PIPECELL"/*/cell.tsv; do
  [ -f "$C" ] || continue
  POT=$(sed -n "s/^pot	//p" "$C"); PIECE=$(sed -n "s/^piece	//p" "$C"); A=$(sed -n "s/^arm	//p" "$C")
  TE=$(sed -n "s/^env	//p" "$C"); RE=$(sed -n "s/^patch_r_env	//p" "$C")
  WANT="SFS_GROWTH_FORMULA=1 SFS_PATCH_R_MM=${RE}"
  N=ok
  if [ "${TE:-na}" != "$WANT" ]; then N="env reads '${TE:-na}', expected '$WANT'"; ENV_BAD="$ENV_BAD $POT/$PIECE/$A"; fi
  printf "%s\t%s\t%s\t%s\t%s\t%s\n" "$POT" "$PIECE" "$A" "${RE:-na}" "${TE:-na}" "$N" >> "$EP"
done
log "=== env proof (every theta_env must read SFS_GROWTH_FORMULA=1 SFS_PATCH_R_MM=<its radius>) ==="
cat "$EP"
if [ -n "$ENV_BAD" ]; then
  log "FAILED env proof, a cell did not carry the formula env at its own radius:$ENV_BAD"
  FAILED="$FAILED env-proof"
fi

# ---- theta proof: the paper-grow thetaDeg the log carried vs the [GROWTH-45] formula theta,
# per cell, straight out of cell.tsv.  REPORT ONLY -- no table here stops the run.
TP=$PIPECELL/theta_proof.tsv
printf "pot\tpiece\tarm\tpatch_r\tpaper_grow_thetaDeg\tgrowth45_theta\tdelta_abs\tnote\n" > "$TP"
for C in "$PIPECELL"/*/cell.tsv; do
  [ -f "$C" ] || continue
  POT=$(sed -n "s/^pot	//p" "$C"); PIECE=$(sed -n "s/^piece	//p" "$C"); A=$(sed -n "s/^arm	//p" "$C")
  RE=$(sed -n "s/^patch_r_env	//p" "$C")
  PGT=$(sed -n "s/^paper_grow_first	//p" "$C" | sed -n "s/.*thetaDeg=\([^ ]*\).*/\1/p")
  G45T=$(sed -n "s/^growth45_theta	//p" "$C")
  D=na; N=ok
  if [ -z "$G45T" ]; then N="no GROWTH-45 theta in the log"; fi
  if [ -z "$PGT" ]; then N="$N; no paper-grow line"; fi
  if [ -n "$PGT" ] && [ -n "$G45T" ]; then
    D=$("$PY" -c "print('%.4f' % abs(float('$PGT')-float('$G45T')))" 2>/dev/null || echo na)
  fi
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "$POT" "$PIECE" "$A" "${RE:-na}" "${PGT:-na}" "${G45T:-na}" "$D" "$N" >> "$TP"
done
log "=== theta proof (paper-grow thetaDeg vs the formula theta, per cell) ==="
cat "$TP"

if [ -n "$FAILED" ]; then
  log "FAILED:$FAILED"
  exit 8
fi
log "all cells ran, every env read SFS_GROWTH_FORMULA=1 at its own patch radius, corpus == manifest"
log "done"
