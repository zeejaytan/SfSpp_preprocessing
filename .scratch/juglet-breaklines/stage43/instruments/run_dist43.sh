#!/bin/bash
# ticket 43 Part A/B -- the two neighbour-turn distributions per sherd, the two derived theta
# rules, and the figure.  Nothing here is part of the pipeline: dist43.py reads the released
# meshes and writes tables and a png.
#
#   dist43.py pieces  --spec instruments/spec.tsv  (one row per sherd: pot, piece, mesh.obj,
#                        spacing_mm = the S that piece's own pipeline run resolved, ladder_theta)
#   dist43.py rules   -- the R1 (k x within p90, k calibrated so Pot A's median lands at 3.4)
#                        and R2 (geometric mean of within p90 and across p10) thetas
#   dist43.py figure  -- one panel per sherd, 3.4 and the ladder theta marked
#
# Paid-for traps written around here: CRLF in a script (grep gate in submit43.sh); scipy is only
# in the TORA env (the shipped python3 has numpy alone); grep -a is used on nothing binary here,
# but every table is written tab-separated with explicit printf formats so no field is lost.
set -uo pipefail

: "${PY:?}" "${INSTR:?}" "${OUT:?}" "${RUN:?}" "${JOBID:?}"
mkdir -p "$OUT/partA" "$OUT/partB" logs || exit 7

log() { echo "[DIST43] $*"; }
SPEC=$INSTR/spec.tsv
[ -f "$SPEC" ] || { log "FATAL no spec $SPEC"; exit 4; }

log "spec: $(grep -cv '^#' "$SPEC" || true) data lines"
grep -v '^#' "$SPEC" | grep -c '' || true

# the meshes this run reads, with their md5, recorded before the sampling starts
{
  printf "pot\tpiece\tmd5\tbytes\tpath\n"
  grep -v '^#' "$SPEC" | while IFS='	' read -r POT PIECE MESH SP LAD; do
    [ -n "${MESH:-}" ] || continue
    if [ -f "$MESH" ]; then
      printf "%s\t%s\t%s\t%s\t%s\n" "$POT" "$PIECE" "$(md5sum "$MESH" | cut -d' ' -f1)" "$(stat -c %s "$MESH")" "$MESH"
    else
      printf "%s\t%s\tMISSING\t-\t%s\n" "$POT" "$PIECE" "$MESH"
    fi
  done
} > "$OUT/meshes_read.tsv"
cat "$OUT/meshes_read.tsv"
NMISS=$(grep -c 'MISSING' "$OUT/meshes_read.tsv" || true)
[ "${NMISS:-0}" = "0" ] || { log "FATAL ${NMISS} mesh(es) missing; nothing was sampled"; exit 5; }

log "=== Part A: the distributions, one row per sherd ==="
"$PY" "$INSTR/dist43.py" pieces --spec "$SPEC" --outdir "$OUT/partA" --seed 4301
RCA=$?
log "dist43.py pieces rc=$RCA"
[ "$RCA" -eq 0 ] || { log "FATAL Part A failed rc=$RCA"; exit "$RCA"; }

log "=== Part B: the two derived rules ==="
"$PY" "$INSTR/dist43.py" rules --partA-dir "$OUT/partA" --outdir "$OUT/partB"
RCB=$?
log "dist43.py rules rc=$RCB"
[ "$RCB" -eq 0 ] || { log "FATAL Part B failed rc=$RCB"; exit "$RCB"; }

log "=== the figure ==="
"$PY" "$INSTR/dist43.py" figure --partA-dir "$OUT/partA" --out "$OUT/partA/figure_partA.png"
RCF=$?
log "dist43.py figure rc=$RCF (a missing matplotlib is a missing figure, not a missing table)"

{
  echo "runid=$(basename "$RUN")"
  echo "jobid=$JOBID"
  echo "host=$(hostname)"
  echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "pieces=$(grep -vc '^#' "$SPEC")"
  echo "partA_rc=$RCA"
  echo "partB_rc=$RCB"
  echo "figure_rc=$RCF"
  echo "seed=4301"
} > "$OUT/partA/run-meta.txt"
cat "$OUT/partA/run-meta.txt"

log "=== partA.tsv ==="
cat "$OUT/partA/partA.tsv"
log "=== partB.tsv ==="
cat "$OUT/partB/partB.tsv"
log "=== thetas.tsv (the values Part C arms B and C will carry) ==="
cat "$OUT/partB/thetas.tsv"

# Part A writes no geometry (json, tsv, png only).  Recorded anyway, before any delete, so the
# closing bookkeeping of this ticket has the same shape in every run directory.
{
  echo "# Part A writes no geometry; nothing is deleted by this phase"
  echo "utc $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "geometry_files_before $(find "$OUT" -type f \( -name '*.pcd' -o -name '*.ply' -o -name '*.obj' -o -name '*.xyz' \) | wc -l)"
  echo "geometry_files_after $(find "$OUT" -type f \( -name '*.pcd' -o -name '*.ply' -o -name '*.obj' -o -name '*.xyz' \) | wc -l)"
} > "$OUT/GEOMETRY_DELETED.txt"
cat "$OUT/GEOMETRY_DELETED.txt"

log "done"
