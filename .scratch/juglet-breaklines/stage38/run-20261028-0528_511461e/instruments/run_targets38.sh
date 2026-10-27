#!/bin/bash
# ticket 38 phase 1 -- the two target sherds (Juglet 2 and 9): does more resolution give them a face?
#
# Per piece, all on one compute node, no pipeline binary:
#   validate   the sampler must reproduce the shipped cloud's count and median NN spacing within 5%
#   subdiv     the displacement midpoint subdivision introduces, MEASURED against the original mesh
#   sample     a synthetic cloud at each level's own spacing s0/L, drawn from the ORIGINAL triangles
#   lattice    what sampling the SUBDIVIDED mesh at s0/L would give instead (the m>=1 lattice floor)
#   cell       grow at 3.4 deg on every cloud: arm scan (shipped cloud, the ticket-37 anchor),
#              arms A and F at every level, arm B (PCA re-estimation) at x4 and x10
#   figure     one figure per piece: a panel per level against the original mesh, plus largest
#              region against achieved spacing with the 50-point floor marked
# Every synthetic cloud carries 'synthetic' in its filename; every table row carries its arm.
set -uo pipefail

PIECES=${PIECES:-"2 9"}
LEVELS=${LEVELS:-"1 2 4 10"}
BDEEP=${BDEEP:-"4 10"}

: "${INSTR:?}" "${PY:?}" "${OUT:?}" "${GEOM:?}" "${CELLS:?}" "${MREG:?}" "${FIG:?}"
: "${DS:?}" "${FIGS37:?}" "${T37DIR:?}"

MESH38=$INSTR/mesh38.py
GROW38=$INSTR/grow38.py
FIG38=$INSTR/fig38.py

log() { echo "[TARGETS] $*"; }
die() { echo "[TARGETS] FATAL $*" >&2; exit 5; }
jget() { "$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])' "$1" "$2"; }

mkdir -p "$GEOM" "$CELLS" "$MREG" "$FIG" || die "mkdir"

log "instruments=$INSTR python=$PY"
"$PY" "$MESH38" selftest || die "mesh38 selftest failed (rc=$?)"
"$PY" "$GROW38" selftest || die "grow38 selftest failed (rc=$?)"

for P in $PIECES; do
  PIECE=Juglet_Piece_$P
  MESH=$DS/Mesh/Juglet/${PIECE}_Mesh.obj
  CLOUD=$DS/Point/Juglet/${PIECE}_Point.pcd
  [ -f "$MESH" ] || die "missing mesh $MESH"
  [ -f "$CLOUD" ] || die "missing cloud $CLOUD"

  log "=== $PIECE: sampler validation against the shipped cloud ==="
  "$PY" "$MESH38" validate --mesh "$MESH" --cloud "$CLOUD" --piece "$PIECE" --outdir "$MREG"
  rc=$?
  if [ "$rc" -ne 0 ]; then
    echo "SAMPLER-DOES-NOT-REPRODUCE $PIECE rc=$rc" > "$OUT/STOP-sampler-not-validated.txt"
    die "sampler did not reproduce the shipped cloud for $PIECE (rc=$rc); stopping before any result is used"
  fi
  VJ=$MREG/sampler_validate_${PIECE}.json
  ROUTE=$(jget "$VJ" gate_route) || die "no gate_route in $VJ"
  if [ "$ROUTE" != "literal" ]; then
    {
      echo "SAMPLER GATE DISCLOSURE  piece=$PIECE  gate_route=$ROUTE"
      echo "The literal comparison the ticket names did not reproduce the shipped cloud on this piece."
      echo "  route 1 sample at the shipped median NN: count_ratio=$(jget "$VJ" count_ratio) spacing_ratio=$(jget "$VJ" spacing_ratio)"
      echo "  a uniform covering of the mesh's own area at that spacing would carry $(jget "$VJ" uniform_points_at_shipped_median) points = $(jget "$VJ" uniform_over_shipped)x the shipped count"
      echo "  mesh: verts=$(jget "$VJ" mesh_verts) faces=$(jget "$VJ" mesh_faces) area=$(jget "$VJ" surface_area_mm2) mm2"
      echo "  mesh shape: edge_median=$(jget "$VJ" edge_median_mm) mm edge_cv=$(jget "$VJ" edge_cv) angle_median=$(jget "$VJ" angle_median_deg) deg angle_min=$(jget "$VJ" angle_min_deg) deg frac(tri min angle<20deg)=$(jget "$VJ" frac_tri_min_angle_lt20)"
      echo "  route 2 spacing: achieved $(jget "$VJ" sampled_median_mm) mm at request $(jget "$VJ" shipped_median_mm) mm, and $(jget "$VJ" half_median_mm) mm at request $(jget "$VJ" half_request_mm) mm"
      echo "  route 2 cover: random surface points to the nearest cloud point median=$(jget "$VJ" cover_median_mm) mm = $(jget "$VJ" cover_median_over_spacing)s, p99=$(jget "$VJ" cover_p99_over_spacing)s"
      echo "  route 2 surface: cloud to the original triangles median=$(jget "$VJ" offset_median_over_spacing)s p99=$(jget "$VJ" offset_p99_over_spacing)s max=$(jget "$VJ" offset_max_over_spacing)s ($(jget "$VJ" offset_max_mm) mm; $(jget "$VJ" offset_far_points) points past 0.5 s re-measured over every triangle)"
      echo "  sampler density: $(jget "$VJ" density_index) points*s^2/area at the request, $(jget "$VJ" half_density_index) at half of it, $(jget "$VJ" shipped_density_index) for the shipped cloud"
      echo "  route 2 sample at the density-implied spacing $(jget "$VJ" density_spacing_mm) mm: count_ratio=$(jget "$VJ" dens_count_ratio) spacing_ratio=$(jget "$VJ" dens_spacing_ratio)"
      echo "  Readings: every synthetic cloud in this run reports ACHIEVED spacing beside requested;"
      echo "  no result below depends on the sampler's absolute density, only on the achieved spacing it prints."
    } | tee "$OUT/SAMPLER-GATE-DISCLOSURE_${PIECE}.txt"
  fi
  S0=$(jget "$VJ" shipped_median_mm) || die "no s0 in $VJ"
  log "$PIECE shipped median NN spacing s0=$S0 mm (this is the level-1 spacing)"

  T37PLY=$T37DIR/${PIECE}_prefloor_regions.ply
  if [ -f "$T37PLY" ]; then
    log "=== $PIECE: ticket-37 anchor -- re-grow ticket 37's own pre-floor cloud ==="
    T37PCD=$GEOM/${PIECE}_t37prefloor_cloud.pcd
    "$PY" "$GROW38" fromply --ply "$T37PLY" --out "$T37PCD" || die "fromply $PIECE"
    T37S=$(jget "$T37PCD.json" median_mm) || die "no spacing from $T37PCD.json"
    log "$PIECE ticket-37 cloud: $(jget "$T37PCD.json" points) points, median NN $T37S mm"
    "$PY" "$GROW38" cell --cloud "$T37PCD" --mesh "$MESH" --orig-cloud "$CLOUD" \
      --piece "$PIECE" --level 1 --arm scan37 --requested "$T37S" --achieved "$T37S" \
      --outdir "$CELLS" || die "cell scan37 $PIECE"
  else
    log "WARN no ticket-37 pre-floor PLY at $T37PLY; the anchor cell is skipped"
  fi

  log "=== $PIECE: subdivision displacement (measured, not estimated) ==="
  for L in 2 4 10; do
    OBJ=""
    [ "$L" -eq 2 ] && OBJ="$GEOM/${PIECE}_synthetic_x2_subdiv.obj"
    "$PY" "$MESH38" subdiv --mesh "$MESH" --level "$L" --piece "$PIECE" --outdir "$MREG" ${OBJ:+--out "$OBJ"} || die "subdiv L=$L $PIECE"
  done

  log "=== $PIECE: clouds, one per level, drawn from the original triangles ==="
  for L in $LEVELS; do
    S=$("$PY" -c "print('%.8f' % (float('$S0')/float('$L')))") || die "spacing arith"
    SYN=$GEOM/${PIECE}_synthetic_x${L}_spacing_${S}.pcd
    "$PY" "$MESH38" sample --mesh "$MESH" --spacing "$S" --level "$L" --sample-from 1 \
      --piece "$PIECE" --outdir "$MREG" --out "$SYN" || die "sample L=$L $PIECE"
    # what the lattice floor would do instead: same spacing, drawn from the SUBDIVIDED mesh
    if [ "$L" -gt 1 ]; then
      "$PY" "$MESH38" sample --mesh "$MESH" --spacing "$S" --level "$L" --sample-from "$L" \
        --piece "${PIECE}_fromx${L}" --outdir "$MREG/lattice_floor" \
        || log "WARN lattice-floor demo failed for $PIECE x$L"
    fi
  done

  log "=== $PIECE: the ticket-37 anchor, arm scan on the shipped cloud at its own spacing ==="
  "$PY" "$GROW38" cell --cloud "$CLOUD" --mesh "$MESH" --orig-cloud "$CLOUD" \
    --piece "$PIECE" --level 1 --arm scan --requested "$S0" --achieved "$S0" \
    --outdir "$CELLS" || die "cell scan $PIECE"

  log "=== $PIECE: arms A and F at every level, arm B at x4 and x10 ==="
  for L in $LEVELS; do
    S=$("$PY" -c "print('%.8f' % (float('$S0')/float('$L')))") || die "spacing arith"
    SYN=$GEOM/${PIECE}_synthetic_x${L}_spacing_${S}.pcd
    SJ=$MREG/sample_${PIECE}_x${L}.json
    ACH=$(jget "$SJ" achieved_median_mm) || die "no achieved spacing in $SJ"
    for A in A F; do
      "$PY" "$GROW38" cell --cloud "$SYN" --mesh "$MESH" --orig-cloud "$CLOUD" \
        --piece "$PIECE" --level "$L" --arm "$A" --requested "$S" --achieved "$ACH" \
        --outdir "$CELLS" || die "cell $A $PIECE x$L"
    done
    case " $BDEEP " in
      *" $L "*)
        "$PY" "$GROW38" cell --cloud "$SYN" --mesh "$MESH" --orig-cloud "$CLOUD" \
          --piece "$PIECE" --level "$L" --arm B --requested "$S" --achieved "$ACH" \
          --outdir "$CELLS" || die "cell B $PIECE x$L"
        ;;
    esac
  done

  log "=== $PIECE: figure (arm A, one panel per level, same camera and scale) ==="
  TGT=$("$PY" -c "print('0.05' if '$P'=='2' else '0.035')")
  "$PY" "$FIG38" --cells "$CELLS" --mesh "$MESH" --piece "$PIECE" --outdir "$FIG" \
    --arm A --target-mm-px "$TGT" --levels "$(echo "$LEVELS" | tr ' ' ',')" \
    || log "WARN figure failed for $PIECE"
done

log "=== aggregate ==="
"$PY" "$GROW38" aggregate --cells "$CELLS" --outdir "$OUT" --figures37 "$FIGS37" \
  || die "aggregate"

cp -f "$MREG"/sampler_validate_*.json "$MREG"/subdiv_*.json "$MREG"/sample_*.json "$OUT"/ 2>/dev/null || true
log "done"
