#!/bin/bash
# ticket 38 phase 3 -- ONE real pipeline cell on a synthetic cloud.
#
# The pipeline is not modified: it is built from the pushed commit and handed a synthetic cloud
# staged inside this run directory, exactly as production hands it a scan.  The cell runs at the
# finest level phase 1 found, which is the level the ticket asks about.  Its own log lines are
# kept, and the cloud the pipeline actually ended up growing on is measured, not assumed.
set -uo pipefail

PIECE=${PIECE:-Juglet_Piece_9}
POT=${POT:-Juglet}
LEVEL=${LEVEL:-}

: "${INSTR:?}" "${PY:?}" "${OUT:?}" "${GEOM:?}" "${MREG:?}" "${DS:?}" "${BIN:?}"
: "${APT:?}" "${SIF:?}" "${STAGER:?}" "${FIG:?}" "${RUN:?}"

MESH38=$INSTR/mesh38.py
GROW38=$INSTR/grow38.py
PIPECELL=$OUT/cells-pipeline
CELL=$PIPECELL/${PIECE}_synth_x${LEVEL:-auto}
ST=$PIPECELL/stage_${PIECE}

log() { echo "[PIPELINE] $*"; }
die() { echo "[PIPELINE] FATAL $*" >&2; exit 7; }
jget() { "$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])' "$1" "$2"; }

mkdir -p "$PIPECELL" "$MREG" "$GEOM" || die "mkdir"

if [ -z "$LEVEL" ]; then
  FJ=$FIG/figure_${PIECE}.json
  if [ -f "$FJ" ]; then
    LEVEL=$(jget "$FJ" floor_reached_at)
    case "$LEVEL" in None|null|"") LEVEL=""; log "phase 1 recorded no level whose largest region reaches 50 points" ;; esac
  fi
fi
if [ -z "$LEVEL" ]; then
  LEVEL=10
  log "no level reached the 50-point floor; running the FINEST level this ticket has, x$LEVEL, and the report will say so"
fi
CELL=$PIPECELL/${PIECE}_synth_x${LEVEL}
log "piece=$PIECE pot=$POT level=x$LEVEL cell=$CELL"

log "=== regenerate the synthetic cloud this cell grows on (self-contained, same seed) ==="
MESH=$DS/Mesh/${POT}/${PIECE}_Mesh.obj
CLOUD=$DS/Point/${POT}/${PIECE}_Point.pcd
AXIS=$DS/Axes/${POT}/${PIECE}_Axis.xyz
[ -f "$MESH" ] || die "missing mesh $MESH"
[ -f "$CLOUD" ] || die "missing cloud $CLOUD"
[ -f "$AXIS" ] || die "missing axis $AXIS"
"$PY" "$MESH38" validate --mesh "$MESH" --cloud "$CLOUD" --piece "$PIECE" --outdir "$MREG" \
  || log "WARN sampler check outside 5% on $PIECE (recorded, not hidden)"
S0=$(jget "$MREG/sampler_validate_${PIECE}.json" shipped_median_mm) || die "no s0"
S=$("$PY" -c "print('%.8f' % (float('$S0')/float('$LEVEL')))") || die "spacing arith"
SYN=$GEOM/${PIECE}_synthetic_x${LEVEL}_spacing_${S}.pcd
"$PY" "$MESH38" sample --mesh "$MESH" --spacing "$S" --level "$LEVEL" --sample-from 1 \
  --piece "$PIECE" --outdir "$MREG" --out "$SYN" || die "sample"
jget "$MREG/sample_${PIECE}_x${LEVEL}.json" points > /dev/null || die "missing sample json"
SYNN=$(jget "$MREG/sample_${PIECE}_x${LEVEL}.json" points)
SYNACH=$(jget "$MREG/sample_${PIECE}_x${LEVEL}.json" achieved_median_mm)
log "synthetic cloud $SYN: $SYNN points, achieved median NN $SYNACH mm (requested $S mm)"
log "synthetic md5=$(md5sum "$SYN" | cut -d' ' -f1)"

log "=== stage (geometry symlinked; the synthetic cloud is the only cloud in the stage) ==="
mkdir -p "$CELL"
bash "$STAGER" "$ST" "$POT" "$PIECE" "$AXIS" "$SYN" || die "stage"
cp -f "$ST/inputs.md5" "$CELL/inputs.md5"
cat "$CELL/inputs.md5"

log "=== run the pipeline ==="
mkdir -p "$CELL/logs" "$CELL/surfaces" "$CELL/measure"
LOG=$CELL/logs/mesh.log
STATUS_RAW=$CELL/status_raw.tsv
ENVS="SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0 SFS_DOWNSAMPLE_TARGET=$SYNN"
log "env: $ENVS"
( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" \
    SFS_AXIS_FILE="$ST/Dataset/Axes/${PIECE}_Axis.xyz" \
    SFS_STATUS_FILE="$STATUS_RAW" SFS_DUMP_STAGE="$CELL/dump" $ENVS "$BIN" ) > "$LOG" 2>&1
rc=$?
log "pipeline rc=$rc log=$(stat -c %s "$LOG" 2>/dev/null || echo 0) bytes"
[ -f "$LOG" ] || die "no pipeline log (rc=$rc)"
grep -E '\[(SPACING|COUNT|SPLITTER|SWITCH)-2[234]\]|\[(FLOOR|RETRY|SINGLE|STATUS)-23\]|\[NORMAL-3[34]\]|\[PAPER-234\]|\[DUMP-25\]|\[DOWNSAMPLING' \
  "$LOG" > "$CELL/logs/lines38.log" || true
log "kept $(wc -l < "$CELL/logs/lines38.log") log lines"

fld() { grep -m1 "$1" "$LOG" | tr ' ' '\n' | grep -m1 "^$2=" | cut -d= -f2-; }
{
  echo "piece	$PIECE"
  echo "pot	$POT"
  echo "level	x$LEVEL"
  echo "synthetic_cloud	$SYN"
  echo "synthetic_md5	$(md5sum "$SYN" | cut -d' ' -f1)"
  echo "synthetic_points	$SYNN"
  echo "synthetic_achieved_spacing_mm	$SYNACH"
  echo "requested_spacing_mm	$S"
  echo "pipeline_rc	$rc"
  echo "spacing_policy	$(fld '\[SPACING-22\]' policy)"
  echo "spacing_diagMM	$(fld '\[SPACING-22\]' diagMM)"
  echo "spacing_s0MM	$(fld '\[SPACING-22\]' s0MM)"
  echo "spacing_S	$(fld '\[SPACING-22\]' S)"
  echo "count_minCluster	$(fld '\[COUNT-22\]' minCluster)"
  echo "status_npts	$(fld '\[STATUS-23\]' npts)"
  echo "status_floor	$(fld '\[STATUS-23\]' floor)"
  echo "status_floor_from	$(fld '\[STATUS-23\]' floor_from)"
  echo "status_capped	$(fld '\[STATUS-23\]' capped)"
  echo "status_outcome	$(fld '\[STATUS-23\]' outcome)"
  echo "status_surf0_points	$(fld '\[STATUS-23\]' surf0_points)"
  echo "status_surf1_points	$(fld '\[STATUS-23\]' surf1_points)"
  echo "retry_sizes	$(grep -m1 '\[RETRY-23\]' "$LOG" | sed -n 's/.*sizes=\([^ ]*\).*/\1/p')"
  echo "retry_clusters	$(grep -m1 '\[RETRY-23\]' "$LOG" | sed -n 's/.*clusters=\([^ ]*\).*/\1/p')"
  echo "retry_clusters_pre	$(grep -m1 '\[RETRY-23\]' "$LOG" | sed -n 's/.*clusters_pre=\([^ ]*\).*/\1/p')"
  echo "downsampling	$(grep -m1 '\[DOWNSAMPLING RESULT\]' "$LOG" | sed -n 's/.*Result=\([0-9]*\).*/\1/p')"
  echo "downsampling_radius	$(grep -m1 '\[DOWNSAMPLING RESULT\]' "$LOG" | sed -n 's/.*Radius(leaf)=\([0-9.eE+-]*\).*/\1/p')"
} > "$CELL/cell.tsv"
cat "$CELL/cell.tsv"

log "=== what the pipeline actually grew on, and on what ==="
for f in "$ST/Temp/Data/$POT/${PIECE}_SampledWithNormals.ply"; do
  if [ -f "$f" ]; then
    cp -f "$f" "$CELL/surfaces/" 2>/dev/null || true
    "$PY" - "$f" "$CELL/measure/sampled_spacing.json" "$INSTR" <<'PYEOF' || true
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
done
for k in 0 1; do
  for ext in ply xyz; do
    f="$ST/Temp/Data/$POT/${PIECE}_Surface_${k}.${ext}"
    [ -f "$f" ] && cp -f "$f" "$CELL/surfaces/" 2>/dev/null
  done
done

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
  find "$ST" "$CELL/dump" "$GEOM" -type f -printf '%p\t%s\n' 2>/dev/null | awk -F'\t' '
    { n=split($1,a,"."); ext=(n>1?a[n]:"none");
      if (ext !~ /^(pcd|ply|xyz|obj|png|json|pcd.gz)$/) ext="other";
      files[ext]++; bytes[ext]+=$2; tf++; tb+=$2 }
    END { printf "ext\tfiles\tbytes\n";
          for (e in files) printf "%s\t%d\t%d\n", e, files[e], bytes[e];
          printf "TOTAL\t%d\t%d\n", tf, tb }' | sort
} > "$CELL/geometry_counts.tsv"
cat "$CELL/geometry_counts.tsv"
if [ -n "$DUMP" ]; then cp -f "$DUMP" "$OUT/${PIECE}_synth_x${LEVEL}_rung2_clusters_premerge.ply" 2>/dev/null || true; fi
rm -rf "$ST" "$CELL/dump"
log "deleted stage $ST and dump $CELL/dump after the counted record above"
log "done"
