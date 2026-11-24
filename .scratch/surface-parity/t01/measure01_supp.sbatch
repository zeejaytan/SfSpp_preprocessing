#!/bin/bash
#SBATCH --job-name=t01-surf2
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:40:00
#SBATCH --output=supplements/t01-turn2/logs/slurm-surf2-%j.out
#SBATCH --error=supplements/t01-turn2/logs/slurm-surf2-%j.err
# Ticket 01 turn 2: re-render the surface figures with the frozen mesh and the
# unmatched points legible. Writes only into $RUN/supplements/t01-turn2; the
# frozen run's evidence/ and its surface hashes are left untouched.
set -uo pipefail
P=/data/gpfs/projects/punim2657
SHIP=$P/SfSpp/runs/20261121-1319_2e951d9_t03-ship
T03E=$P/SfSpp/runs/20261121-1319_2e951d9_t03-potE
FIXED="$T03E/trees/E_K3R1/E/MM"
ORIG=$P/sfs_main/original_samples/SfS_pp
PY=$P/TORA/envs/tora/bin/python3
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261124-1431_1233d62_t01-surface-parity
OUT="$RUN/supplements/t01-turn2"
export PYTHONPATH="$SHIP/work/impl_t03:$SHIP/work"
export OMP_NUM_THREADS=4
mkdir -p "$OUT/tables" "$OUT/renders" "$OUT/logs"
"$PY" "$OUT/work/surface01.py" --run "$RUN" --fixed "$FIXED" --orig "$ORIG" \
  --out "$OUT/tables" --renders "$OUT/renders"
