#!/bin/bash
# ticket 38 phase 2 -- the controls and the always-works reference.
#
# Juglet 3, 5 (one-cluster cases) and Juglet 7 (already surfaces) at x1, x2 and x4: does the
# level at which a sherd starts to grow a face move with resolution?  Pot A 07 is the reference
# that works at its own resolution; it is grown from ticket 37's own pre-floor cloud so the
# 34608-point / 2494-region / 13131-largest row is reproduced from ticket 37's bytes, not re-derived.
# Then part E: the two redraws the conservator asked for, and the ink/grey/colour fractions
# measured off the new PNGs (and off a replay of ticket 37's own style, to calibrate the measure).
set -uo pipefail

PIECES=${PIECES:-"3 5 7"}
LEVELS=${LEVELS:-"1 2 4"}
POTA=${POTA:-Pot_A_Piece_07}

: "${INSTR:?}" "${PY:?}" "${OUT:?}" "${GEOM:?}" "${CELLS:?}" "${MREG:?}" "${FIG:?}"
: "${DS:?}" "${CORP:?}" "${FIGS37:?}" "${T37DIR:?}"

MESH38=$INSTR/mesh38.py
GROW38=$INSTR/grow38.py
PARTE38=$INSTR/parte38.py

log() { echo "[CONTROLS] $*"; }
die() { echo "[CONTROLS] FATAL $*" >&2; exit 6; }
jget() { "$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])' "$1" "$2"; }

mkdir -p "$GEOM" "$CELLS" "$MREG" "$FIG" || die "mkdir"

for P in $PIECES; do
  PIECE=Juglet_Piece_$P
  MESH=$DS/Mesh/Juglet/${PIECE}_Mesh.obj
  CLOUD=$DS/Point/Juglet/${PIECE}_Point.pcd
  [ -f "$MESH" ] || die "missing mesh $MESH"
  [ -f "$CLOUD" ] || die "missing cloud $CLOUD"

  log "=== $PIECE (control): sampler check against its shipped cloud ==="
  if ! "$PY" "$MESH38" validate --mesh "$MESH" --cloud "$CLOUD" --piece "$PIECE" --outdir "$MREG"; then
    log "WARN sampler check did not reproduce $PIECE's shipped cloud; its levels are still reported with achieved spacing"
  fi
  VJ=$MREG/sampler_validate_${PIECE}.json
  S0=$(jget "$VJ" shipped_median_mm) || die "no s0 in $VJ"

  log "=== $PIECE: anchor at x1 on the shipped cloud, then arms A and F at x1/x2/x4 ==="
  "$PY" "$GROW38" cell --cloud "$CLOUD" --mesh "$MESH" --orig-cloud "$CLOUD" \
    --piece "$PIECE" --level 1 --arm scan --requested "$S0" --achieved "$S0" \
    --outdir "$CELLS" || die "cell scan $PIECE"

  for L in $LEVELS; do
    S=$("$PY" -c "print('%.8f' % (float('$S0')/float('$L')))") || die "spacing arith"
    SYN=$GEOM/${PIECE}_synthetic_x${L}_spacing_${S}.pcd
    "$PY" "$MESH38" sample --mesh "$MESH" --spacing "$S" --level "$L" --sample-from 1 \
      --piece "$PIECE" --outdir "$MREG" --out "$SYN" || die "sample L=$L $PIECE"
    SJ=$MREG/sample_${PIECE}_x${L}.json
    ACH=$(jget "$SJ" achieved_median_mm) || die "no achieved spacing in $SJ"
    for A in A F; do
      "$PY" "$GROW38" cell --cloud "$SYN" --mesh "$MESH" --orig-cloud "$CLOUD" \
        --piece "$PIECE" --level "$L" --arm "$A" --requested "$S" --achieved "$ACH" \
        --outdir "$CELLS" || die "cell $A $PIECE x$L"
    done
  done
done

log "=== $POTA (always-works reference): ticket 37's own pre-floor cloud, re-grown ==="
PMESH=$CORP/Mesh/${POTA}_Mesh.obj
PCLOUD=$CORP/Point/Pot_A/${POTA}_Point.pcd
PPLY=$T37DIR/${POTA}_prefloor_regions.ply
if [ -f "$PMESH" ] && [ -f "$PCLOUD" ] && [ -f "$PPLY" ]; then
  PPCD=$GEOM/${POTA}_t37prefloor_cloud.pcd
  "$PY" "$GROW38" fromply --ply "$PPLY" --out "$PPCD" || die "fromply $POTA"
  PS=$(jget "$PPCD.json" median_mm) || die "no spacing for $POTA"
  log "$POTA ticket-37 cloud: $(jget "$PPCD.json" points) points, median NN $PS mm"
  "$PY" "$GROW38" cell --cloud "$PPCD" --mesh "$PMESH" --orig-cloud "$PCLOUD" \
    --piece "$POTA" --level 1 --arm scan37 --requested "$PS" --achieved "$PS" \
    --outdir "$CELLS" || die "cell scan37 $POTA"
else
  log "WARN missing Pot_A input(s): mesh=$PMESH cloud=$PCLOUD ply=$PPLY"
fi

log "=== part E: piece 9 and Pot A 07, tail at full opacity and a continuous rank palette ==="
"$PY" "$PARTE38" --t37 "$T37DIR" --outdir "$FIG" || die "parte38"

log "=== aggregate ==="
"$PY" "$GROW38" aggregate --cells "$CELLS" --outdir "$OUT" --figures37 "$FIGS37" \
  || die "aggregate"
cp -f "$MREG"/sampler_validate_*.json "$MREG"/sample_*.json "$OUT"/ 2>/dev/null || true
log "done"
