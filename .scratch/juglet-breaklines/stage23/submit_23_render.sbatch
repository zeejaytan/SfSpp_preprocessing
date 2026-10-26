#!/usr/bin/env bash
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --job-name=p23-render
#SBATCH --time=00:30:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --output=logs/slurm-%j.out
#
# ticket 23: renders of written surfaces over their own piece, at a stated mm/px.
# Reads the grid run's kept cells (surfaces + cells23.tsv); writes only into this run's out/.
set -uo pipefail
RUN=__RUNDIR__
CELLDIR=__CELLDIR__
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
INSTR=$RUN/instruments
cd "$RUN" || exit 1
mkdir -p logs out/renders
say() { echo "[$(date +%H:%M:%S)] $*"; }
say "job ${SLURM_JOB_ID:-local} render: cells=$CELLDIR"
"$PY" "$INSTR/render23.py" "$CELLDIR" "$RUN/out/renders/ticket23_surfaces_over_cloud.png" > out/render23.log 2>&1
say "render exit=$?"
sed -n '1,40p' out/render23.log
ls -l out/renders
say "run dir bytes: $(du -sb "$RUN" | awk '{print $1}')"
printf "%s\t%s\t%s\t%s\t\t\n" "$(basename "$RUN")" "${SLURM_JOB_ID:-local}" "__NEWCOMMIT__" "p23-renders" >> /data/gpfs/projects/punim2657/SfSpp/runs/index.tsv
say "done"
