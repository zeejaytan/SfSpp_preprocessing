#!/bin/bash
# ticket 42 measurement rerun -- fill surfaces.tsv, surface_pairs.tsv and nest.tsv from the KEPT
# cell PLYs of the run of record plus the ORIGINAL released clouds/meshes.  No pipeline rerun and
# no binary build: the run of record's cells are READ-ONLY here (only their surfaces/*.ply are
# read), and every JSON this writes lands under the NEW run's out/measure.
# Paid-for traps: replica37/measure34/mesh38 must sit beside grow38.py (ticket 41's first grid
# died on ModuleNotFoundError replica37 -- exactly why this rerun exists); the run of record is
# never written to; grep -a is used on binary-ish PLY headers.
set -uo pipefail

: "${PY:?}" "${INSTR:?}" "${SRC_RUN:?}" "${OUT:?}" "${DS:?}" "${CORP:?}"

GROW38=$INSTR/grow38.py
NEST39=$INSTR/nest39.py
MREG=$OUT/measure
mkdir -p "$MREG" || exit 7

log() { echo "[MEAS42] $*"; }
jget() { "$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])' "$1" "$2" 2>/dev/null || echo ""; }
jgetna() {
  local v
  v=$(jget "$1" "$2") || { echo na; return 0; }
  [ -z "$v" ] && { echo na; return 0; }
  [ "$v" = "None" ] && v=na
  printf "%s\n" "$v"
}
piece_mesh()  { if [ "$1" = "Pot_A" ]; then echo "$CORP/Mesh/$2_Mesh.obj"; else echo "$DS/Mesh/$1/$2_Mesh.obj"; fi; }
piece_cloud() { if [ "$1" = "Pot_A" ]; then echo "$CORP/Point/$1/$2_Point.pcd"; else echo "$DS/Point/$1/$2_Point.pcd"; fi; }

SURFSUM=$OUT/surfaces.tsv
PAIRSUM=$OUT/surface_pairs.tsv
NESTSUM=$OUT/nest.tsv
ANCH=$OUT/anchors.tsv
printf "pot\tpiece\tarm\tsurface\tpoints\tdistinct\text_x\text_y\text_z\tdiag\tcov_2mm\tfold_deg\n" > "$SURFSUM"
printf "pot\tpiece\tarm\tn0\tn1\tmed_nn\tmed_along\tmed_across\tmed_angle_deg\tcoin\tmed_t_signed\tp05_t_signed\tp95_t_signed\tnormal_src_a\tnormal_src_b\twall_med_mm\n" > "$PAIRSUM"
printf "pot\tpiece\tarm\tn0\tn0_distinct\tn1\tn1_distinct\tshared\tshared_over_a\tshared_over_b\tshared_over_smaller\tmean_normal_dot\tmatched\tmedian_point_normal_angle_deg\n" > "$NESTSUM"

# wall medians of the run of record, joined into the pair rows on pot/piece/arm
WALLMED=$MREG/wall_med.tsv
awk -F'\t' 'NR>1 {print $1"\t"$2"\t"$3"\t"$6}' "$SRC_RUN/out/cells-pipeline/walls.tsv" > "$WALLMED" 2>/dev/null || true
wall_med() { awk -F'\t' -v p="$1" -v c="$2" -v a="$3" '$1==p && $2==c && $3==a {print $4; exit}' "$WALLMED"; }
log "wall join table: $(wc -l < "$WALLMED") rows from the run of record's walls.tsv"

FAILED=""
NC_CELL=0
for CELLDIR in "$SRC_RUN"/out/cells-pipeline/*_arm*; do
  [ -d "$CELLDIR" ] || continue
  [ -d "$CELLDIR/surfaces" ] || continue
  TAGNAME=$(basename "$CELLDIR")
  PIECE=${TAGNAME%_arm*}
  ARM=${TAGNAME##*_arm}
  CELLTSV=$CELLDIR/cell.tsv
  [ -f "$CELLTSV" ] || { log "WARN no cell.tsv in $CELLDIR, skipped"; continue; }
  POT=$(sed -n "s/^pot$(printf '\t')//p" "$CELLTSV")
  [ -n "$POT" ] || { log "WARN no pot line in $CELLTSV, skipped"; continue; }
  MESH=$(piece_mesh "$POT" "$PIECE"); CLOUD=$(piece_cloud "$POT" "$PIECE")
  [ -f "$MESH" ] && [ -f "$CLOUD" ] || { log "WARN $TAGNAME: missing mesh or cloud, skipped"; continue; }
  NC_CELL=$((NC_CELL+1))
  log "=== cell $POT/$PIECE arm $ARM ==="
  for K in 0 1; do
    F=$CELLDIR/surfaces/${PIECE}_Surface_${K}.ply
    if [ ! -f "$F" ]; then
      log "surface $K: not kept for this arm, no row"
      continue
    fi
    SJ=$MREG/surface_${TAGNAME}_Surface_${K}.json
    DJ=$MREG/distinct_${TAGNAME}_Surface_${K}.json
    if "$PY" "$GROW38" surface --ply "$F" --mesh "$MESH" --orig-cloud "$CLOUD" \
         --tag "${TAGNAME}_Surface_$K" --outdir "$MREG" \
       && "$PY" "$NEST39" count --ply "$F" --tag "${TAGNAME}_Surface_$K" --outdir "$MREG"; then
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "$POT" "$PIECE" "$ARM" "$K" "$(jget "$SJ" points)" "$(jget "$DJ" distinct)" \
        "$(jget "$SJ" ext_x)" "$(jget "$SJ" ext_y)" "$(jget "$SJ" ext_z)" \
        "$(jget "$SJ" diag)" "$(jget "$SJ" cov_2mm)" "$(jget "$SJ" fold_deg)" >> "$SURFSUM"
      log "surface $K measured: points=$(jget "$SJ" points) cov=$(jget "$SJ" cov_2mm) fold=$(jget "$SJ" fold_deg)"
    else
      log "WARN surface $K not measured on $TAGNAME"
      FAILED="$FAILED $TAGNAME/surf$K"
    fi
  done
  F0=$CELLDIR/surfaces/${PIECE}_Surface_0.ply
  F1=$CELLDIR/surfaces/${PIECE}_Surface_1.ply
  if [ -f "$F0" ] && [ -f "$F1" ]; then
    PJ=$MREG/surfacepair_${TAGNAME}.json
    NJ=$MREG/nest_${TAGNAME}.json
    if "$PY" "$GROW38" surfacepair --a "$F0" --b "$F1" --tag "$TAGNAME" --outdir "$MREG" \
       && "$PY" "$NEST39" pair --a "$F0" --b "$F1" --tag "$TAGNAME" --outdir "$MREG"; then
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "$POT" "$PIECE" "$ARM" "$(jget "$PJ" n0)" "$(jget "$PJ" n1)" "$(jget "$PJ" med_nn)" \
        "$(jget "$PJ" med_along)" "$(jget "$PJ" med_across)" "$(jget "$PJ" med_angle_deg)" \
        "$(jget "$PJ" coin)" "$(jget "$PJ" med_t_signed)" "$(jget "$PJ" p05_t_signed)" \
        "$(jget "$PJ" p95_t_signed)" "$(jget "$PJ" normal_src_a)" "$(jget "$PJ" normal_src_b)" \
        "$(wall_med "$POT" "$PIECE" "$ARM")" >> "$PAIRSUM"
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "$POT" "$PIECE" "$ARM" "$(jget "$NJ" n0)" "$(jget "$NJ" n0_distinct)" "$(jget "$NJ" n1)" \
        "$(jget "$NJ" n1_distinct)" "$(jget "$NJ" shared)" "$(jget "$NJ" shared_over_a)" \
        "$(jget "$NJ" shared_over_b)" "$(jget "$NJ" shared_over_smaller)" \
        "$(jget "$NJ" mean_normal_dot)" "$(jget "$NJ" matched)" \
        "$(jgetna "$NJ" median_point_normal_angle_deg)" >> "$NESTSUM"
      log "pair measured: n0=$(jget "$PJ" n0) n1=$(jget "$PJ" n1) med_nn=$(jget "$PJ" med_nn) med_along=$(jget "$PJ" med_along) med_across=$(jget "$PJ" med_across) coin=$(jget "$PJ" coin) mean_normal_dot=$(jget "$NJ" mean_normal_dot)"
    else
      log "WARN the two surfaces of $TAGNAME were not paired"
      FAILED="$FAILED $TAGNAME/pair"
    fi
  else
    log "pair: $TAGNAME did not keep both surfaces, no pair row"
  fi
done

log "=== $NC_CELL cells visited ==="
log "=== surfaces ($(wc -l < "$SURFSUM") lines incl header) ==="
cat "$SURFSUM"
log "=== surface_pairs ($(wc -l < "$PAIRSUM") lines incl header) ==="
cat "$PAIRSUM"
log "=== nest ($(wc -l < "$NESTSUM") lines incl header) ==="
cat "$NESTSUM"

# ---- hard anchors: ticket-41 run-of-record pair numbers, +/-0.01, reported not tuned
"$PY" - "$PAIRSUM" "$ANCH" <<'PYEOF' || true
import sys
pairsum, out = sys.argv[1], sys.argv[2]
ANCHORS = [("Juglet", "Juglet_Piece_1", "A", (2.0146, 1.8152, 0.5282)),
           ("Pot_A", "Pot_A_Piece_01", "A", (7.0952, 7.0888, 0.2709))]
rows = {}
for ln in open(pairsum):
    f = ln.rstrip("\n").split("\t")
    if len(f) >= 9 and f[0] != "pot":
        rows[(f[0], f[1], f[2])] = f
bad = 0
with open(out, "w") as fh:
    fh.write("pot\tpiece\tarm\tstat\tgot\tanchor\tabs_diff\thit\n")
    for pot, piece, arm, (a_nn, a_al, a_ac) in ANCHORS:
        r = rows.get((pot, piece, arm))
        if r is None:
            fh.write("%s\t%s\t%s\tall\tMISSING ROW\t-\t-\tno\n" % (pot, piece, arm))
            bad += 1
            continue
        for name, got, anc in (("med_nn", float(r[5]), a_nn),
                               ("med_along", float(r[6]), a_al),
                               ("med_across", float(r[7]), a_ac)):
            d = abs(got - anc)
            hit = "yes" if d <= 0.01 else "no"
            if hit == "no":
                bad += 1
            fh.write("%s\t%s\t%s\t%s\t%.4f\t%.4f\t%.4f\t%s\n" % (pot, piece, arm, name, got, anc, d, hit))
print("[ANCHORS] %d miss(es); see %s" % (bad, out))
open(out + ".flag", "w").write("%d\n" % bad)
PYEOF
cat "$ANCH"
ANCH_BAD=0
[ -f "$ANCH.flag" ] && ANCH_BAD=$(cat "$ANCH.flag")

if [ -n "$FAILED" ]; then
  log "FAILED measurements:$FAILED"
fi
if [ "$ANCH_BAD" != "0" ]; then
  log "ANCHOR MISS ($ANCH_BAD statistic(s) outside +/-0.01): reported, not tuned"
  log "done-with-anchor-miss"
  exit 10
fi
log "anchors hit; done"
exit 0
