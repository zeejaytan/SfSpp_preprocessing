#!/bin/bash
# ticket 38 phase 3 -- five real pipeline cells: two levels per target sherd, plus the Pot A 07
# reference at its own resolution.
#
# The pipeline is not modified: it is built from the pushed commit and handed each cloud staged
# inside this run directory, exactly as production hands it a scan.  Cells run cheapest-first:
# x1 on both sherds already clears the 50-point floor, so those two are the cells the ticket
# cannot do without; Pot A 07 follows on the frozen released BINARY cloud, then the two x10
# cells.  A cell that fails is recorded and the driver goes on -- one cell failure must not cost
# the others their evidence -- and the driver exits non-zero at the end if any cell failed.
#
# For every surface the pipeline writes: its point count, its extent, the fraction of the
# ORIGINAL cloud within 2 mm of it, and the folded angle between its normals and the ORIGINAL
# mesh.  The pipeline own "Number of clusters" and [STATUS-23] lines are kept verbatim.
set -uo pipefail

CELL_LIST=${CELL_LIST:-"Juglet:Juglet_Piece_2:1 Juglet:Juglet_Piece_9:1 Pot_A:Pot_A_Piece_07:real Juglet:Juglet_Piece_2:10 Juglet:Juglet_Piece_9:10"}
MIN_LEFT_S=${MIN_LEFT_S:-420}

: "${INSTR:?}" "${PY:?}" "${OUT:?}" "${GEOM:?}" "${MREG:?}" "${DS:?}" "${CORP:?}" "${BIN:?}"
: "${APT:?}" "${SIF:?}" "${STAGER:?}" "${FIG:?}" "${RUN:?}" "${JOBID:?}"

MESH38=$INSTR/mesh38.py
GROW38=$INSTR/grow38.py
PIPECELL=$OUT/cells-pipeline
mkdir -p "$PIPECELL" "$MREG" "$GEOM" || exit 7

log() { echo "[PIPELINE] $*"; }
jget() { "$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])' "$1" "$2"; }
pcd_points() { grep -m1 "^POINTS" "$1" | awk '{print $2}'; }

# squeue reports what is left of this job; a cell is only started if it has this long to run
time_left_s() {
  local tl d rest h m s
  tl=$(squeue -h -j "$JOBID" -o %L 2>/dev/null | head -1 | tr -d " ")
  [ -z "$tl" ] && { echo 99999; return; }
  case "$tl" in *-*) d=${tl%%-*}; rest=${tl#*-} ;; *) d=0; rest=$tl ;; esac
  h=${rest%%:*}; rest=${rest#*:}; m=${rest%%:*}; s=${rest#*:}
  echo $(( d * 86400 + 10#${h:-0} * 3600 + 10#${m:-0} * 60 + 10#${s:-0} ))
}

FAILED=""
SUM=$PIPECELL/pipeline_cells.tsv
printf "piece\tpot\tlevel\tcloud_kind\tcloud_points\trequested_mm\tachieved_mm\tpipeline_rc\tclusters\tstatus_outcome\tsurf0_points\tsurf1_points\tnote\n" > "$SUM"

run_cell() {
  POT=$1; PIECE=$2; LEVEL=$3
  local RC=0 TAG CELL ST SYN SYNN SYNACH KIND S0 S F K
  TAG=x$LEVEL
  if [ "$LEVEL" = "real" ]; then TAG=real; fi
  CELL=$PIPECELL/${PIECE}_${TAG}
  ST=$PIPECELL/stage_${PIECE}_${TAG}
  log "=============================================================="
  log "cell $PIECE ($POT) level=$LEVEL -> $CELL"

  if [ "$POT" = "Pot_A" ]; then
    MESH=$CORP/Mesh/${PIECE}_Mesh.obj
    AXIS=$CORP/Axes/${PIECE}_Axis.xyz
    [ -f "$AXIS" ] || AXIS=$DS/Axes/Pot_A/${PIECE}_Axis.xyz
    CLOUD=$CORP/Point/Pot_A/${PIECE}_Point.pcd
  else
    MESH=$DS/Mesh/${POT}/${PIECE}_Mesh.obj
    CLOUD=$DS/Point/${POT}/${PIECE}_Point.pcd
    AXIS=$DS/Axes/${POT}/${PIECE}_Axis.xyz
  fi
  for f in "$MESH" "$CLOUD" "$AXIS"; do
    [ -f "$f" ] || { log "FATAL missing $f"; return 1; }
  done
  log "mesh=$MESH"
  log "cloud=$CLOUD"
  log "axis=$AXIS"

  if [ "$LEVEL" = "real" ]; then
    KIND=REAL-RELEASED-CLOUD
    SYN=$CLOUD
    SYNN=$(pcd_points "$CLOUD")
    SYNACH=$(jget "$CLOUD.json" median_mm 2>/dev/null || echo na)
    S=na
    log "the released cloud itself: $SYNN points (no sampling, no downsampling target change)"
  else
    KIND=SYNTHETIC
    VJ=$MREG/sampler_validate_${PIECE}.json
    if [ ! -f "$VJ" ]; then
      "$PY" "$MESH38" validate --mesh "$MESH" --cloud "$CLOUD" --piece "$PIECE" --outdir "$MREG" \
        || log "WARN sampler check outside 5% on $PIECE (recorded, not hidden)"
    fi
    S0=$(jget "$VJ" shipped_median_mm) || { log "FATAL no sampler json $VJ"; return 1; }
    S=$("$PY" -c "print('%.8f' % (float('$S0')/float('$LEVEL')))") || { log "FATAL spacing arith"; return 1; }
    SYN=$GEOM/${PIECE}_synthetic_x${LEVEL}_spacing_${S}.pcd
    "$PY" "$MESH38" sample --mesh "$MESH" --spacing "$S" --level "$LEVEL" --sample-from 1 \
      --piece "$PIECE" --outdir "$MREG" --out "$SYN" || { log "FATAL sample"; return 1; }
    SYNN=$(jget "$MREG/sample_${PIECE}_x${LEVEL}.json" points) || { log "FATAL sample json"; return 1; }
    SYNACH=$(jget "$MREG/sample_${PIECE}_x${LEVEL}.json" achieved_median_mm)
    log "synthetic cloud $SYN: $SYNN points, achieved median NN $SYNACH mm (requested $S mm)"
    log "synthetic md5=$(md5sum "$SYN" | cut -d" " -f1)"
  fi

  log "=== stage: geometry symlinked, the $KIND cloud is the only cloud in the stage ==="
  mkdir -p "$CELL"
  bash "$STAGER" "$ST" "$POT" "$PIECE" "$AXIS" "$SYN" "$KIND" || { log "FATAL stage"; return 1; }
  cp -f "$ST/inputs.md5" "$CELL/inputs.md5"
  cat "$CELL/inputs.md5"

  log "=== run the pipeline ==="
  mkdir -p "$CELL/logs" "$CELL/surfaces" "$CELL/measure"
  LOG=$CELL/logs/mesh.log
  STATUS_RAW=$CELL/status_raw.tsv
  local ENVS="SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0 SFS_DOWNSAMPLE_TARGET=$SYNN"
  log "env: $ENVS"
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" \
      SFS_AXIS_FILE="$ST/Dataset/Axes/${PIECE}_Axis.xyz" \
      SFS_STATUS_FILE="$STATUS_RAW" SFS_DUMP_STAGE="$CELL/dump" $ENVS "$BIN" ) > "$LOG" 2>&1
  RC=$?
  log "pipeline rc=$RC log=$(stat -c %s "$LOG" 2>/dev/null || echo 0) bytes"
  [ -f "$LOG" ] || { log "FATAL no pipeline log (rc=$RC)"; return 1; }
  grep -E "\[(SPACING|COUNT|SPLITTER|SWITCH)-2[234]\]|\[(FLOOR|RETRY|SINGLE|STATUS)-23\]|\[NORMAL-3[34]\]|\[PAPER-234\]|\[DUMP-25\]|\[DOWNSAMPLING|Number of clusters" \
    "$LOG" > "$CELL/logs/lines38.log" || true
  log "kept $(wc -l < "$CELL/logs/lines38.log") log lines"
  grep -m2 "Number of clusters" "$LOG" | while read -r ln; do log "pipeline: $ln"; done

  local NCLUST
  NCLUST=$(grep -m1 "Number of clusters" "$LOG" | sed -n "s/.*equal to \([0-9]*\).*/\1/p")
  {
    echo "piece	$PIECE"
    echo "pot	$POT"
    echo "level	$LEVEL"
    echo "cloud_kind	$KIND"
    echo "cloud	$SYN"
    echo "cloud_md5	$(md5sum "$SYN" | cut -d" " -f1)"
    echo "cloud_points	$SYNN"
    echo "cloud_achieved_spacing_mm	$SYNACH"
    echo "requested_spacing_mm	$S"
    echo "pipeline_rc	$RC"
    echo "pipeline_clusters	$NCLUST"
    echo "spacing_policy	$(grep -m1 "\[SPACING-22\]" "$LOG" | sed -n "s/.*policy=\([^ ]*\).*/\1/p")"
    echo "spacing_s0MM	$(grep -m1 "\[SPACING-22\]" "$LOG" | sed -n "s/.*s0MM=\([^ ]*\).*/\1/p")"
    echo "spacing_S	$(grep -m1 "\[SPACING-22\]" "$LOG" | sed -n "s/.* S=\([^ ]*\).*/\1/p")"
    echo "count_minCluster	$(grep -m1 "\[COUNT-22\]" "$LOG" | sed -n "s/.*minCluster=\([^ ]*\).*/\1/p")"
    echo "status_npts	$(grep -m1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*npts=\([^ ]*\).*/\1/p")"
    echo "status_floor	$(grep -m1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*floor=\([^ ]*\).*/\1/p")"
    echo "status_outcome	$(grep -m1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*outcome=\([^ ]*\).*/\1/p")"
    echo "status_surf0_points	$(grep -m1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*surf0_points=\([^ ]*\).*/\1/p")"
    echo "status_surf1_points	$(grep -m1 "\[STATUS-23\]" "$LOG" | sed -n "s/.*surf1_points=\([^ ]*\).*/\1/p")"
    echo "retry_sizes	$(grep -m1 "\[RETRY-23\]" "$LOG" | sed -n "s/.*sizes=\([^ ]*\).*/\1/p")"
    echo "downsampling	$(grep -m1 "\[DOWNSAMPLING RESULT\]" "$LOG" | sed -n "s/.*Result=\([0-9]*\).*/\1/p")"
    echo "downsampling_radius	$(grep -m1 "\[DOWNSAMPLING RESULT\]" "$LOG" | sed -n "s/.*Radius(leaf)=\([0-9.eE+-]*\).*/\1/p")"
  } > "$CELL/cell.tsv"
  cat "$CELL/cell.tsv"

  log "=== the surfaces the pipeline wrote, measured against the ORIGINAL cloud and mesh ==="
  for K in 0 1; do
    F=""
    for ext in ply xyz; do
      [ -f "$ST/Temp/Data/$POT/${PIECE}_Surface_${K}.${ext}" ] && F=$ST/Temp/Data/$POT/${PIECE}_Surface_${K}.${ext}
    done
    if [ -n "$F" ]; then
      cp -f "$F" "$CELL/surfaces/" 2>/dev/null || true
      if [ "${F##*.}" = "ply" ]; then
        "$PY" "$GROW38" surface --ply "$F" --mesh "$MESH" --orig-cloud "$CLOUD" \
          --tag "${PIECE}_${TAG}_Surface_${K}" --outdir "$CELL/measure" || log "WARN surface $K not measured"
      else
        log "surface $K is ${F##*.}, not a ply: cannot measure normals, kept as written"
      fi
    else
      log "surface $K: the pipeline wrote none"
    fi
  done
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
print("[PIPELINE] SampledWithNormals: points=%d median_nn=%.5f mm" % (len(xyz), sp["median"]))
PYEOF
  fi

  local DUMP
  DUMP=$(ls -1 "$CELL"/dump/*/r2_clusters_premerge.ply 2>/dev/null | head -1)
  if [ -n "$DUMP" ]; then
    cp -f "$DUMP" "$CELL/measure/" 2>/dev/null || true
    "$PY" - "$DUMP" "$CELL/measure/rung2_sizes.json" "$INSTR" <<'PYEOF' || true
import json, sys
import numpy as np
sys.path.insert(0, sys.argv[3])
import replica37 as R
xyz, nrm, cid, reason, props = R.read_rung2_ply(sys.argv[1])
u, c = np.unique(cid, return_counts=True)
order = np.argsort(-c)
sizes = [int(c[i]) for i in order[:20]]
row = {"ply": sys.argv[1], "points": int(len(xyz)), "clusters": int(len(u)),
       "largest": int(c.max()), "sizes_top20": sizes,
       "ge10": int((c >= 10).sum()), "ge20": int((c >= 20).sum()),
       "ge30": int((c >= 30).sum()), "ge50": int((c >= 50).sum()),
       "ge_pct1": int((c >= 0.01 * len(xyz)).sum()),
       "ge_pct5": int((c >= 0.05 * len(xyz)).sum()),
       "ge_pct10": int((c >= 0.10 * len(xyz)).sum())}
json.dump(row, open(sys.argv[2], "w"), indent=1, sort_keys=True)
print("[PIPELINE] rung2 dump: points=%d clusters=%d largest=%d ge50=%d ge_pct5=%d"
      % (row["points"], row["clusters"], row["largest"], row["ge50"], row["ge_pct5"]))
print("[PIPELINE] rung2 top20 sizes: %s" % (sizes,))
PYEOF
  else
    log "WARN no rung-2 dump under $CELL/dump"
  fi

  log "=== count the geometry this cell produced, then delete it ==="
  {
    find "$ST" "$CELL/dump" "$GEOM" -type f -printf "%p\t%s\n" 2>/dev/null | awk -F"\t" '
      { n=split($1,a,"."); ext=(n>1?a[n]:"none");
        if (ext !~ /^(pcd|ply|xyz|obj|png|json|pcd.gz)$/) ext="other";
        files[ext]++; bytes[ext]+=$2; tf++; tb+=$2 }
      END { printf "ext\tfiles\tbytes\n";
            for (e in files) printf "%s\t%d\t%d\n", e, files[e], bytes[e];
            printf "TOTAL\t%d\t%d\n", tf, tb }' | sort
  } > "$CELL/geometry_counts.tsv"
  cat "$CELL/geometry_counts.tsv"
  rm -rf "$ST" "$CELL/dump"
  log "deleted stage $ST and dump $CELL/dump after the counted record above"

  local NOTE=ok
  [ "$RC" -ne 0 ] && NOTE="pipeline rc=$RC"
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$PIECE" "$POT" "$LEVEL" "$KIND" "$SYNN" "$S" "$SYNACH" "$RC" "${NCLUST:-na}" \
    "$(sed -n "s/^status_outcome	//p" "$CELL/cell.tsv")" \
    "$(sed -n "s/^status_surf0_points	//p" "$CELL/cell.tsv")" \
    "$(sed -n "s/^status_surf1_points	//p" "$CELL/cell.tsv")" "$NOTE" >> "$SUM"
  [ "$RC" -eq 0 ] || FAILED="$FAILED $PIECE/$TAG"
  return 0
}

for SPEC in $CELL_LIST; do
  POT=${SPEC%%:*}; REST=${SPEC#*:}; PIECE=${REST%%:*}; LEVEL=${REST##*:}
  LEFT=$(time_left_s)
  if [ "$LEFT" -lt "$MIN_LEFT_S" ]; then
    log "SKIP $PIECE $LEVEL: only ${LEFT}s of wall clock left, and a cell needs more than that"
    printf "%s\t%s\t%s\tSKIPPED\t-\t-\t-\t-\t-\t-\t-\t-\tonly %ss left\n" "$PIECE" "$POT" "$LEVEL" "$LEFT" >> "$SUM"
    continue
  fi
  log "wall clock left: ${LEFT}s"
  run_cell "$POT" "$PIECE" "$LEVEL" || log "WARN cell $PIECE $LEVEL did not complete"
done

log "=== every cell, as recorded ==="
cat "$SUM"
if [ -n "$FAILED" ]; then
  log "FAILED cells:$FAILED"
  exit 8
fi
log "all cells ran"
log "done"
