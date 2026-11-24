#!/bin/bash
#SBATCH --job-name=t01-cell
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=8G
#SBATCH --time=02:30:00
#SBATCH --output=logs/slurm-cell-%j.out
#SBATCH --error=logs/slurm-cell-%j.err
# Ticket 01 submission entry: sbatch --parsable "$RUN/submit.sbatch" ARM REP.
# The resource block above must stay identical to work/t01/cell01.sbatch, because a
# shell-invoked cell01.sbatch cannot apply its own #SBATCH lines; it execs that body
# in this job so the archive's wave command shape keeps working and the returned id
# is the id of the cell that actually ran.
set -uo pipefail
RUN="${SLURM_SUBMIT_DIR:?}"
exec bash "$RUN/work/t01/cell01.sbatch" "$@"
