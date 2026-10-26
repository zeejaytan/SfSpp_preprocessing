#!/usr/bin/env bash
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --job-name=__JOBNAME__
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --output=logs/slurm-%j.out
#
# ticket 23: analysis over a finished grid run. Reads that run's kept cells (surfaces,
# cells23.tsv, status23.tsv, measure23.tsv) and writes only into this run's out/.
# Nothing is re-run: no cell is staged and no geometry is deleted here.
set -uo pipefail
RUN=__RUNDIR__
GRID=__GRIDRUN__
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
INSTR=$RUN/instruments
CELLROOT=$GRID/out/cells
cd "$RUN" || exit 1
mkdir -p logs out/renders
say() { echo "[$(date +%H:%M:%S)] $*"; }
say "job ${SLURM_JOB_ID:-local} analysis over $GRID"

say "coverage of every written surface over its own piece"
"$PY" "$INSTR/coverage23.py" "$CELLROOT" "$RUN/out/coverage23.tsv" > out/coverage.log 2>&1
say "coverage exit=$? -> $(tail -1 out/coverage.log)"

say "renders"
"$PY" "$INSTR/render23.py" "$CELLROOT" "$RUN/out/renders/ticket23_surfaces_over_cloud.png" > out/render23.log 2>&1
say "render exit=$?"
sed -n '1,40p' out/render23.log

say "surfaces written per arm (from the grid's own rows)"
awk -F'\t' 'NR>1 {n[$1]++; if ($15=="yes") s0[$1]++; if ($16=="yes") s1[$1]++
                   out[$1"/"$11]++}
             END {for (a in n) printf "  %-6s cells=%d surface_0=%d surface_1=%d\n", a, n[a], s0[a]+0, s1[a]+0;
                  print "  outcomes:"; for (k in out) printf "    %-12s %d\n", k, out[k]}' \
  "$CELLROOT/cells23.tsv" | sort > out/surfaces_by_arm.txt
cat out/surfaces_by_arm.txt

say "one-surface pieces, coverage and extent (the pieces that were silent at the defaults)"
awk -F'\t' 'NR==1 || ($5==1 && ($4=="one"))' "$RUN/out/coverage23.tsv" > out/one_surface_coverage.tsv
column -t -s$'\t' out/one_surface_coverage.tsv | head -30

say "run dir bytes: $(du -sb "$RUN" | awk '{print $1}')"
printf "%s\t%s\t%s\t%s\t\t\n" "$(basename "$RUN")" "${SLURM_JOB_ID:-local}" "__NEWCOMMIT__" "p23-analysis" >> /data/gpfs/projects/punim2657/SfSpp/runs/index.tsv
say "done"
