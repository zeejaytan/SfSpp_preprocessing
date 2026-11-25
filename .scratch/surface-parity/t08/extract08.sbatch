#!/bin/bash
# Ticket 08 Stage 1 -- exact XYZ dedup of all 157 own-surface pieces (314 walls)
# and frozen Ticket 03 axis extraction in native def_3x Juglet units.
#SBATCH --job-name=t08-ship
#SBATCH --time=12:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --output=logs/t08-ship_%j.out
#SBATCH --error=logs/t08-ship_%j.err
set -euo pipefail

RUN=${SLURM_SUBMIT_DIR:?}
SHIP=/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship
IMPL=$SHIP/work/impl_t03
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
T08=$RUN/work/t08

export SFS_IMPL=$IMPL
export PYTHONPATH=$SHIP/work:$IMPL:$IMPL/scripts
export MPLBACKEND=Agg
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

cd "$RUN"
mkdir -p logs out tables

echo "[t08-ship] host=$(hostname) run=$RUN job=${SLURM_JOB_ID:-none} start=$(date -Is)"
echo "[t08-ship] SHIP=$SHIP"
echo "[t08-ship] python=$PY"
"$PY" -c "import numpy; print('[t08-ship] numpy', numpy.__version__)"

set +e
"$PY" "$T08/extract08.py" --run "$RUN"
RC=$?
set -e
echo "[t08-ship] extract08 exit=$RC end=$(date -Is)"
if [ "$RC" -ne 0 ]; then
  echo "[t08-ship] FAILED rc=$RC"
  exit "$RC"
fi
echo "[t08-ship] T08-SHIP-OK"
