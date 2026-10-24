#!/bin/bash
#SBATCH --job-name=p287fix
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:30:00

# Ticket 287 fix-up: lane H02/before only. In job 33746239 that lane's stage-tree copy failed
# because \$SCR/run did not exist yet (cp -a into a missing parent); the edge stage then ran in
# the wrong cwd and produced a 2.6 ms no-op log with no pcds. No code, sheet or parameter changes.
# This job recreates the same stage tree from the same build tree, runs the one lane, then re-runs
# score287.py so \$RUN/out/score287.txt covers all eight lanes.
set -u
RUN=${RUN_DIR:?}
CANON=${CANONICAL:?}
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SRC=/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1604_d1b61cb_p280-extent/stage/H02_norm
SCR=/data/gpfs/projects/punim2657/sfs-vote-248/p287-fix-${SLURM_JOB_ID}
mkdir -p "$SCR" "$SCR/run" "$RUN/logs" "$RUN/out"
say() { echo "[$(date -u +%H:%M:%S)] $*"; }
say "fix-up job $SLURM_JOB_ID on $(hostname) for lane H02 before"
md5sum "$RUN/bin/EdgeLineExtractionHeadless_before"
lab=H02; stem=Pot_H_Piece_02; pot=Pot_H; arm=before
T="$SCR/run/H02_before"; O="$RUN/out/H02_before"
rm -rf "$T" "$O"; mkdir -p "$O"
cp -a "$SRC" "$T" || { echo "STAGE COPY FAILED"; exit 1; }
[ -d "$T/Temp/Data/$pot" ] || { echo "SOURCE MISSING $T/Temp/Data/$pot"; exit 1; }
mkdir -p "$T/Dataset/Breaklines/$pot"
rm -f "$T/Dataset/Breaklines/$pot"/*.pcd "$T/Dataset/Breaklines/$pot"/*.ply "$T/Dataset/Breaklines/$pot"/*.xyz 2>/dev/null
rm -rf "$T/Temp/Temp_edge"
md5sum "$T"/Temp/Data/"$pot"/*_Surface_*.xyz "$T"/Dataset/Axes/*.xyz > "$O/sheets_pre.md5"
( cd "$T" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$pot" "$RUN/bin/EdgeLineExtractionHeadless_$arm" > "$O/edge.log" 2>&1 )
echo "EDGE_EXIT[$lab $arm]=$?" | tee "$O/exit.txt"
md5sum "$T"/Temp/Data/"$pot"/*_Surface_*.xyz "$T"/Dataset/Axes/*.xyz > "$O/sheets_post.md5"
diff -q "$O/sheets_pre.md5" "$O/sheets_post.md5" >/dev/null && echo "sheets unchanged [$lab $arm]" || echo "SHEETS CHANGED [$lab $arm]"
cp "$T/Dataset/Breaklines/$pot"/* "$O"/ 2>/dev/null
ls -l "$O"/*.pcd
grep -E 'FULL-263|SEED-287|STOP-267 BEGIN' "$O/edge.log" | head -6
say "=== re-score all eight lanes ==="
OUT="$RUN/out" python3 "$RUN/score287.py" 2>&1 | tee "$RUN/out/score287.txt"
say "=== fix-up done ==="