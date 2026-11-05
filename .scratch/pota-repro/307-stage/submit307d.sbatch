#!/bin/bash
#SBATCH --job-name=t307d-jug
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=03:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 307 Stage C4 -- Juglet, one arm, F20 floor.
#   Part 1: our Juglet axes at the SHIPPED 307 default (paper chain, walls WHOLE -> truncate=0,
#           cost prune ON), seed 0, from the same t66 S0/S1 walls the authors' lanes use.
#   Part 2: the ticket 305 F20 harness verbatim (jug305.sbatch body): F20O_r1..3 = authors'
#           Dataset axes, F20N_r1..3 = ours, everything else identical.
set -uo pipefail

RUN=$SLURM_SUBMIT_DIR
JUGG=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
WORK=$RUN/work
JOBID=${SLURM_JOB_ID:-na}

for v in $(compgen -e | grep -E '^(SFS_|POT_NAME$)'); do unset "$v"; done
cd "$RUN" || exit 1
mkdir -p logs work out score

echo "[JOB] runid=$(basename "$RUN") job=$JOBID host=$(hostname) at $(date -u +%FT%TZ)"
echo "[JOB] SFS_* env present: $(compgen -e | grep -c '^SFS_') (expect 0)"
{ echo "commit $(cat work/code_commit.txt 2>/dev/null || echo na)"; md5sum "$WORK"/code/sfs_axes/*.py; } > logs/code.md5
cat logs/code.md5

# ---- corpus + juglet input guard
md5_jug() { local out=$1
  { md5sum "$CORP"/Surfaces/*.xyz "$CORP"/Axes/*.xyz "$JUGG"/Juglet_Piece_?.S0 "$JUGG"/Juglet_Piece_?.S1 2>/dev/null; } | sort -k2 > "$out"; }
md5_jug "$RUN/logs/inputs_before.md5"

# ---- Part 1: our Juglet axes at the shipped 307 default
AD=$WORK/jugsurf
rm -rf "$AD"; mkdir -p "$AD"
for n in 1 2 3 4 5 6 7 8 9; do
  nn=$(printf "%02d" "$n")
  ln -sf "$JUGG/Juglet_Piece_${n}.S0" "$AD/Pot_JUGLET_Piece_${nn}_Surface_0.xyz"
  ln -sf "$JUGG/Juglet_Piece_${n}.S1" "$AD/Pot_JUGLET_Piece_${nn}_Surface_1.xyz"
done
md5sum "$JUGG"/Juglet_Piece_?.S0 "$JUGG"/Juglet_Piece_?.S1 > "$RUN/logs/jug_walls.md5"
export PYTHONPATH="$WORK/code"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
$PY "$WORK/axes305.py" --surfaces "$AD" --out "$RUN/out/jug" --pot JUGLET --seeds 1 \
    --truncate 0 --jobs 9 --write-seeds 1 > "$RUN/logs/axes_jug.log" 2>&1
echo "[JOB] juglet axes rc=$?"
tail -6 "$RUN/logs/axes_jug.log"
mkdir -p "$RUN/out/jug/axes307"
for n in 1 2 3 4 5 6 7 8 9; do
  nn=$(printf "%02d" "$n")
  src=$RUN/out/jug/axes305/Pot_JUGLET_Piece_${nn}_Axis.xyz
  dst=$RUN/out/jug/axes307/Juglet_Piece_${n}_Axis.xyz
  if [ -s "$src" ]; then cp -f "$src" "$dst"; else : > "$dst"; fi
  printf "Juglet_Piece_%s\t%s lines\n" "$n" "$(wc -l < "$dst")"
done
md5sum "$RUN/out/jug/axes307"/*.xyz

# ---- Part 2: the 305 F20 harness, JAXDIR substituted
sed "s|__JAXDIR__|$RUN/out/jug/axes307|" "$WORK/jug305.tmpl" > "$WORK/jug305_run.sh"
grep -n 'JAXDIR=' "$WORK/jug305_run.sh" | head -3
bash "$WORK/jug305_run.sh"
echo "[JOB] jug305 rc=$?"

md5_jug "$RUN/logs/inputs_after.md5"
diff "$RUN/logs/inputs_before.md5" "$RUN/logs/inputs_after.md5" > logs/inputs.diff || true
if [ -s logs/inputs.diff ]; then echo "[JOB] WARN inputs changed"; cat logs/inputs.diff; else echo "[JOB] corpus and juglet walls unchanged"; fi
echo "[JOB] complete at $(date -u +%FT%TZ)"
