#!/bin/bash
# ticket 39, second (and last) job -- the picture of what arm B wrote.
#
# The tables from the first job say the two surfaces separate in own mode and nest in radius mode.
# A change that moves geometry has to be LOOKED at, not only measured, so this driver takes the
# surfaces the two cells of one piece just wrote -- the same bytes the tables were computed from --
# and draws them: three orthographic views plus one edge-on view whose plane contains the mean
# normal of Surface_0, and the signed through-distance histogram of Surface_1 against Surface_0 for
# both arms on one common axis.
#
# It renders BEFORE the job's closing geometry delete, because the surfaces are the input.  The
# figure files are PNG and are kept; every .pcd/.ply/.obj/.xyz under out/ is counted and deleted by
# the job's finish(), which writes the count before the delete.
set -uo pipefail

: "${INSTR:?}" "${PY:?}" "${OUT:?}" "${FIG:?}" "${RUN:?}" "${JOBID:?}"
PIECE=${PIECE:-Juglet_Piece_9}
LEVEL=${LEVEL:-1}

PIPECELL=$OUT/cells-pipeline
FIG39=$INSTR/fig39.py
mkdir -p "$FIG" || exit 7
# matplotlib builds a font cache on first use; a node with a read-only HOME would abort the render,
# so the cache goes inside the run directory where the job already has write access.
export MPLCONFIGDIR=$OUT/.mplcache
mkdir -p "$MPLCONFIGDIR" || exit 7

log() { echo "[FIG39] $*"; }

A0=$PIPECELL/${PIECE}_x${LEVEL}_armA/surfaces/${PIECE}_Surface_0.ply
A1=$PIPECELL/${PIECE}_x${LEVEL}_armA/surfaces/${PIECE}_Surface_1.ply
B0=$PIPECELL/${PIECE}_x${LEVEL}_armB/surfaces/${PIECE}_Surface_0.ply
B1=$PIPECELL/${PIECE}_x${LEVEL}_armB/surfaces/${PIECE}_Surface_1.ply
SYN=$(ls -1 "$OUT"/geometry/${PIECE}_synthetic_x${LEVEL}_spacing_*.pcd 2>/dev/null | head -1)

log "piece $PIECE x$LEVEL -- the surfaces the two cells wrote"
for f in "$A0" "$A1" "$B0" "$B1" "$SYN"; do
  if [ -f "$f" ]; then
    log "  present $(stat -c %s "$f") bytes md5=$(md5sum "$f" | cut -d' ' -f1) $f"
  else
    log "  MISSING $f"
  fi
done
for f in "$A0" "$A1" "$B0" "$B1"; do
  [ -f "$f" ] || { log "FATAL cannot draw: $f was not written"; exit 6; }
done
[ -n "$SYN" ] && [ -f "$SYN" ] || { log "FATAL cannot draw: the synthetic cloud is not under $OUT/geometry"; exit 6; }

TAG=${PIECE}_x${LEVEL}
log "rendering from the same arrays that are measured"
"$PY" "$FIG39" render --piece "$PIECE" --level "$LEVEL" --cloud "$SYN" \
  --a-s0 "$A0" --a-s1 "$A1" --b-s0 "$B0" --b-s1 "$B1" \
  --a-label "A radius (control)" --b-label "B own" \
  --outdir "$FIG" --tag "$TAG" || { log "FATAL fig39 render failed"; exit 7; }

J=$FIG/fig39_${TAG}_figures.json
[ -f "$J" ] || { log "FATAL no figure record $J"; exit 7; }

# One row per figure, and one row per arm carrying the three quantities recomputed here, so the
# figure and the table are provably the same bytes: the md5 of each input surface is in this row.
FT=$PIPECELL/figures.tsv
printf "piece\tlevel\tfigure\tarm\tpath\tbytes\tmd5\tmm_per_px\tmm_per_px_spread\tshared\tshared_over_smaller\tmean_normal_dot\tmed_along\tmed_across\tmed_t_signed\tn0\tn1\ts0_md5\ts1_md5\n" > "$FT"
for ARM in A B; do
  VIEWS=$("$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); v=d["views_figure"]["views"][sys.argv[2]]; print("%s\t%d\t%s\t%.6f\t%.3e" % (v["png"], v["bytes"], v["md5"], v["mm_per_px"], v["mm_per_px_spread"]))' "$J" "$ARM")
  NUM=$("$PY" -c 'import json,sys; d=json.load(open(sys.argv[1]))["arms"][sys.argv[2]]; n=d["nest"]; p=d["pair"]; print("%d\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%d\t%d\t%s\t%s" % (n["shared"], n["shared_over_smaller"], n["mean_normal_dot"], p["med_along"], p["med_across"], p["med_t_signed"], n["n0"], n["n1"], d["surface_0"]["md5"], d["surface_1"]["md5"]))' "$J" "$ARM")
  # 4 lead fields + VIEWS' 5 + NUM's 10 = the 19 the header declares
  printf "%s\t%s\tviews\t%s\t%s\t%s\n" "$PIECE" "$LEVEL" "$ARM" "$VIEWS" "$NUM" >> "$FT"
done
HIST=$("$PY" -c 'import json,sys; d=json.load(open(sys.argv[1]))["hist_figure"]; print("%s\t%d\t%s" % (d["png"], d["bytes"], d["md5"]))' "$J")
{ printf "%s\t%s\thist\t%s\t%s" "$PIECE" "$LEVEL" "A,B" "$HIST"
  printf "\t\t\t\t\t\t\t\t\t\t\t\t\n"; } >> "$FT"
cat "$FT"

log "=== the PNGs, as written ==="
for f in "$FIG"/*.png; do
  [ -f "$f" ] || continue
  log "  $(stat -c %s "$f") bytes md5=$(md5sum "$f" | cut -d' ' -f1) $f"
done

log "=== what this driver consumed, counted before the job's delete ==="
{
  printf "ext\tfiles\tbytes\n"
  find "$FIG" -type f -name '*.png' -printf "%p\t%s\n" | awk -F"\t" '{n++; b+=$2} END {printf "png\t%d\t%d\n", n, b}'
  find "$PIPECELL" -type f -name '*_Surface_*.ply' -printf "%p\t%s\n" | awk -F"\t" '{n++; b+=$2} END {printf "ply-surface\t%d\t%d\n", n, b}'
} > "$PIPECELL/figures_geometry.tsv"
cat "$PIPECELL/figures_geometry.tsv"

log "done"
