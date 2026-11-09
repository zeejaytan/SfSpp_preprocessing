#!/bin/bash
#SBATCH --job-name=t323-render
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:15:00
#SBATCH --output=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0740_d628fc0_t323-potA/logs/render_%j.out
# Ticket 323: GT vs authors'-axes control (MOR1) vs axes323 (K3R1), Pots A, H, J.
set -uo pipefail
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
R=/data/gpfs/projects/punim2657/SfSpp/runs
S=$R/20261110-0740_d628fc0_t323-potA/work/render323.py
for P in A H J; do
  RUN=$R/20261110-0740_d628fc0_t323-pot$P
  mkdir -p $RUN/out/renders
  $PY $S $P $RUN ${P}_MOR1 "Authors' axes (MOR1)" ${P}_K3R1 "axes323 (K3R1)" $RUN/out/renders/pot$P.png "Pot $P - ticket 323"
done
