#!/bin/bash
#SBATCH --job-name=t308d-render
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 308 Stage D -- renders.  One figure per pot, panels = the arms being compared,
# each panel top (x,y) and side (x,z) in ONE shared view box, so a panel that is wrong is
# wrong in the same frame as the panel that is right.  Drawn by render305.py from the
# assembler's own Result dirs: every piece cloud placed by its T_<i>to_<i>.txt, and every
# Edgeline_*.xyz drawn over it.
#
# The render is a data plot, not a photograph: it shows which pieces the assembler placed
# and where their edgelines landed relative to each other.  It cannot show surface quality.
set -uo pipefail
RUN=$SLURM_SUBMIT_DIR
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
WORK=$RUN/work
SPEC=$RUN/spec.tsv
OUT=$RUN/out/renders
mkdir -p "$OUT" logs
JOBID=${SLURM_JOB_ID:-na}
echo "[JOB] render job=$JOBID run=$(basename "$RUN")"
cat "$SPEC"

$PY -c "import matplotlib, numpy; print('matplotlib', matplotlib.__version__, 'numpy', numpy.__version__)" || exit 5

while IFS=$'\t' read -r POT TITLE PANELS; do
  [ -n "${POT:-}" ] || continue
  case "$POT" in \#*) continue;; esac
  ARGS=()
  for p in $PANELS; do ARGS+=("$p"); done
  echo "[JOB] $POT -> $OUT/pot_$POT.png  panels: $PANELS"
  $PY "$WORK/render305.py" "$OUT/pot_$POT.png" "$TITLE" "${ARGS[@]}" > "logs/render_$POT.log" 2>&1
  echo "[JOB] $POT rc=$? $(tail -1 "logs/render_$POT.log")"
done < "$SPEC"

ls -l "$OUT"
{ echo "jobid=$JOBID"; date -u +%FT%TZ; } > "$RUN/run-meta.txt"
echo "[JOB] complete"
