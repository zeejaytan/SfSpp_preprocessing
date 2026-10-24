#!/usr/bin/env bash
#SBATCH --job-name=p294render
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --output=logs/slurm-%j.out
# Ticket 294 job B: draw the eleven pictures from the geometry job A left behind, then delete that
# geometry (rule: geometry dies with its ticket) and record what was deleted.
set -uo pipefail

: ${RUN_DIR:?RUN_DIR must be exported}
RUN=$RUN_DIR
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
mkdir -p $RUN/logs $RUN/out/png $RUN/work/mpl
export MPLCONFIGDIR=$RUN/work/mpl
echo "[RENDER] node=$(hostname) job=$SLURM_JOB_ID start=$(date -Is)"
echo "[RENDER] manifest lanes=$(grep -c . $RUN/out/lanes_wanted.tsv) wanted"

"$PY" "$RUN/scripts/p294_render.py" "$RUN" > $RUN/out/render.log 2>&1
REXIT=$?
echo "[RENDER] renderer exit=$REXIT"
tail -40 $RUN/out/render.log

NP=$(ls -1 $RUN/out/png/*.png 2>/dev/null | wc -l)
echo "[RENDER] png files=$NP (11 expected)"
md5sum $RUN/out/png/*.png > $RUN/out/png.md5 2>/dev/null
cat $RUN/out/png.md5

# ---- geometry out: stage trees, surfaces, exported lines ----
D=$RUN/out/GEOMETRY_DELETED.txt
{
  echo "ticket 294 -- geometry deleted after the pictures existed, $(date -Is) on $(hostname)"
  echo "deleted (run output): stage trees under $RUN/stage, the extracted surfaces in out/geom/*.xyz,"
  echo "and the exported breaklines in out/geom/*.pcd. The pictures and the tables stay."
  echo "not deleted: the frozen corpus under /data/gpfs/projects/punim2657/sfs_main/original_samples (INPUT),"
  echo "the binaries in bin/ (record), scripts/, logs/, out/*.tsv, out/*.json, out/*.log, out/png/."
  echo ""
  echo "stage trees:"
  du -sh $RUN/stage/* 2>/dev/null
  echo ""
  echo "files deleted (path bytes):"
  find $RUN/stage $RUN/out/geom -type f -printf "%p %s\n" 2>/dev/null
  echo ""
  echo "counts: stage files=$(find $RUN/stage -type f 2>/dev/null | wc -l) geom files=$(ls -1 $RUN/out/geom 2>/dev/null | wc -l)"
} > $D
rm -rf $RUN/stage
rm -f $RUN/out/geom/*.xyz $RUN/out/geom/*.pcd
rm -rf $RUN/work
echo "STAGE_DIRS_REMAINING=$(ls -1d $RUN/stage/* 2>/dev/null | wc -l) GEOM_FILES_REMAINING=$(ls -1 $RUN/out/geom 2>/dev/null | wc -l)" >> $D
echo "[RENDER] deleted stage trees and out/geom geometry; record in $D"

BIG=$(find $RUN -type f -size +1M ! -path "*/bin/*" | wc -l)
echo "[RENDER] files over 1 MiB outside bin/: $BIG (0 expected)"
find $RUN -type f -size +1M ! -path "*/bin/*" | head -5
echo "[RENDER] done $(date -Is)"
