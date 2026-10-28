#!/bin/bash
# ticket 40 -- render every piece that wrote both surfaces in both arms, then the cross-piece F2.
#
# Same contract as ticket 39's figure driver, lifted from one piece to a whole group: F1 (the
# four-view picture, arm A over arm B, same camera and scale) and F3 (the signed through-distance
# histogram, one axis, both arms) come from fig39.py render per piece, drawn from the SAME surface
# bytes the tables were measured from.  F2 -- shared fraction and mean dot, arm A against arm B,
# every piece on one axis, Pot A flagged -- comes from fig40.py reading the nest table the cells
# wrote.  A piece whose cells did not write both surfaces in both arms is recorded as missing, not
# silently skipped.
set -uo pipefail

: "${INSTR:?}" "${PY:?}" "${OUT:?}" "${FIG:?}" "${RUN:?}" "${JOBID:?}" "${DS:?}" "${CORP:?}"
GROUP=${GROUP:?}
LEVEL=${LEVEL:-1}
PIECES=${PIECES:?}

PIPECELL=$OUT/cells-pipeline
FIG39=$INSTR/fig39.py
FIG40=$INSTR/fig40.py
mkdir -p "$FIG" || exit 7
export MPLCONFIGDIR=$OUT/.mplcache
mkdir -p "$MPLCONFIGDIR" || exit 7

log() { echo "[FIG40] $*"; }

released_cloud() {
  case "$1" in
    Pot_A_*) echo "$CORP/Point/Pot_A/${1}_Point.pcd" ;;
    *) echo "$DS/Point/Juglet/${1}_Point.pcd" ;;
  esac
}
group_cloud() {
  if [ "$GROUP" = g1 ]; then
    ls -1 "$OUT"/geometry/${1}_synthetic_x${LEVEL}_spacing_*.pcd 2>/dev/null | head -1
  else
    released_cloud "$1"
  fi
}

FT=$PIPECELL/figures.tsv
[ -f "$FT" ] || printf "group\tpiece\tlevel\tfigure\tarm\tpath\tbytes\tmd5\tmm_per_px\tmm_per_px_spread\tshared\tshared_over_smaller\tmean_normal_dot\tmed_along\tmed_across\tmed_t_signed\tn0\tn1\ts0_md5\ts1_md5\n" > "$FT"

RENDERED=0
for PIECE in $PIECES; do
  TAG=${PIECE}_x${LEVEL}
  A0=$PIPECELL/${TAG}_armA/surfaces/${PIECE}_Surface_0.ply
  A1=$PIPECELL/${TAG}_armA/surfaces/${PIECE}_Surface_1.ply
  B0=$PIPECELL/${TAG}_armB/surfaces/${PIECE}_Surface_0.ply
  B1=$PIPECELL/${TAG}_armB/surfaces/${PIECE}_Surface_1.ply
  CLOUD=$(group_cloud "$PIECE")
  MISS=""
  for f in "$A0" "$A1" "$B0" "$B1"; do [ -f "$f" ] || MISS="$MISS ${f##*/}"; done
  if [ -n "$MISS" ] || [ -z "$CLOUD" ] || [ ! -f "$CLOUD" ]; then
    log "MISSING $GROUP/$PIECE:$MISS cloud=${CLOUD:-none} -- recorded, not rendered"
    printf "%s\t%s\t%s\tmissing\tA,B\t-\t0\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\n" \
      "$GROUP" "$PIECE" "$LEVEL" >> "$FT"
    continue
  fi
  log "=== $GROUP/$PIECE: drawing from the surfaces the two cells wrote ==="
  for f in "$A0" "$A1" "$B0" "$B1"; do
    log "  $(stat -c %s "$f") bytes md5=$(md5sum "$f" | cut -d' ' -f1) $f"
  done
  if "$PY" "$FIG39" render --piece "$PIECE" --level "$LEVEL" --cloud "$CLOUD" \
      --a-s0 "$A0" --a-s1 "$A1" --b-s0 "$B0" --b-s1 "$B1" \
      --a-label "A radius (control)" --b-label "B own" \
      --outdir "$FIG" --tag "$TAG"; then
    J=$FIG/fig39_${TAG}_figures.json
    if [ -f "$J" ]; then
      for ARM in A B; do
        VIEWS=$("$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); v=d["views_figure"]["views"][sys.argv[2]]; print("%s\t%d\t%s\t%.6f\t%.3e" % (v["png"], v["bytes"], v["md5"], v["mm_per_px"], v["mm_per_px_spread"]))' "$J" "$ARM")
        NUM=$("$PY" -c 'import json,sys; d=json.load(open(sys.argv[1]))["arms"][sys.argv[2]]; n=d["nest"]; p=d["pair"]; print("%d\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%d\t%d\t%s\t%s" % (n["shared"], n["shared_over_smaller"], n["mean_normal_dot"], p["med_along"], p["med_across"], p["med_t_signed"], n["n0"], n["n1"], d["surface_0"]["md5"], d["surface_1"]["md5"]))' "$J" "$ARM")
        printf "%s\t%s\t%s\t%s\tviews\t%s\t%s\t%s\n" "$GROUP" "$PIECE" "$LEVEL" "$ARM" "$VIEWS" "$NUM" >> "$FT"
      done
      HIST=$("$PY" -c 'import json,sys; d=json.load(open(sys.argv[1]))["hist_figure"]; print("%s\t%d\t%s" % (d["png"], d["bytes"], d["md5"]))' "$J")
      { printf "%s\t%s\t%s\thist\tA,B\t%s" "$GROUP" "$PIECE" "$LEVEL" "$HIST"
        printf "\t\t\t\t\t\t\t\t\t\t\t\n"; } >> "$FT"
      RENDERED=$((RENDERED+1))
    else
      log "WARN render ran but no record $J"
      printf "%s\t%s\t%s\tnorecord\tA,B\t-\t0\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\n" \
        "$GROUP" "$PIECE" "$LEVEL" >> "$FT"
    fi
  else
    log "WARN fig39 render FAILED on $GROUP/$PIECE (recorded)"
    printf "%s\t%s\t%s\tfailed\tA,B\t-\t0\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\n" \
      "$GROUP" "$PIECE" "$LEVEL" >> "$FT"
  fi
done
log "rendered $RENDERED of $(echo $PIECES | wc -w) pieces"

# ---- F2: every piece on one axis, arm A against arm B, Pot A flagged
log "=== F2 from the nest table the cells wrote ==="
"$PY" "$FIG40" f2 --nest "$PIPECELL/nest.tsv" --cells "$PIPECELL/pipeline_cells.tsv" \
  --outdir "$FIG" --tag "f2_${GROUP}" \
  && log "F2 written to $FIG" || log "WARN fig40 f2 FAILED (recorded in figures.log only)"

log "=== the PNGs, as written ==="
for f in "$FIG"/*.png; do
  [ -f "$f" ] || continue
  log "  $(stat -c %s "$f") bytes md5=$(md5sum "$f" | cut -d' ' -f1) $f"
done

{
  printf "ext\tfiles\tbytes\n"
  find "$FIG" -type f -name '*.png' -printf "%p\t%s\n" | awk -F"\t" '{n++; b+=$2} END {printf "png\t%d\t%d\n", n, b}'
  find "$PIPECELL" -type f -name '*_Surface_*.ply' -printf "%p\t%s\n" | awk -F"\t" '{n++; b+=$2} END {printf "ply-surface\t%d\t%d\n", n, b}'
} > "$PIPECELL/figures_geometry_${GROUP}.tsv"
cat "$PIPECELL/figures_geometry_${GROUP}.tsv"

log "done"
