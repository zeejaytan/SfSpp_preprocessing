#!/bin/bash
# ticket 57 -- ONE arm of the SFS_WORNESS sweep: step 3 (mesh->surfaces) then step 4
# (surfaces->breaklines) for all nine Juglet pieces, using the t55 cell runner unchanged
# except that the dial is optional (empty WORNESS = the DEFAULT arm, SFS_WORNESS never
# passed).  Identical code for every arm; nothing is retuned per arm.
set -uo pipefail

ARM=${ARM:?arm label (w050, default, ...)}
WORNESS=${WORNESS-}
OUT=${OUT:?arm output dir}
export WORNESS

log() { echo "[ARM57 $ARM] $*"; }
log "start worness=${WORNESS:-<unset>} out=$OUT"
mkdir -p "$OUT" || exit 7

bash "$INSTR/run_cell57.sh" > "$OUT/cells57.log" 2>&1
RC=$?
log "cell runner rc=$RC"

if [ -f "$OUT/pieces57.tsv" ]; then
  log "pieces57.tsv:"
  cat "$OUT/pieces57.tsv"
fi
log "end rc=$RC"
exit $RC