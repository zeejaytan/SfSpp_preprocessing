#!/usr/bin/env bash
#SBATCH --job-name=p293draw
#SBATCH --time=00:40:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --output=logs/slurm-%j.out
# Ticket 293 job B: run the cluster/face census over the geometry job A left behind, draw the eleven
# pictures, then delete that geometry (rule: geometry dies with its ticket) and record what went.
set -uo pipefail

RUN=$RUN_DIR
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
mkdir -p $RUN/logs $RUN/out/png $RUN/out/census $RUN/work/mpl
export MPLCONFIGDIR=$RUN/work/mpl
echo "[CENSUS] node=$(hostname) job=$SLURM_JOB_ID start=$(date -Is)"
echo "[CENSUS] diag dumps=$(ls -1 $RUN/out/diag 2>/dev/null | wc -l) surfaces=$(ls -1 $RUN/out/geom/*.xyz 2>/dev/null | wc -l) lines=$(ls -1 $RUN/out/geom/*.pcd 2>/dev/null | wc -l)"

"$PY" "$RUN/scripts/p293_census.py" "$RUN" > $RUN/out/census.log 2>&1
CENSUS_EXIT=$?
echo "[CENSUS] census exit=$CENSUS_EXIT"
tail -40 $RUN/out/census.log
for f in clusters.tsv assign_summary.tsv phaseB.tsv selfcheck286.txt census.json; do
  [ -f "$RUN/out/$f" ] && echo "[CENSUS] $f $(stat -c%s $RUN/out/$f) B md5=$(md5sum $RUN/out/$f | awk '{print $1}')"
done

"$PY" "$RUN/scripts/p293_render.py" "$RUN" > $RUN/out/render.log 2>&1
REXIT=$?
echo "[RENDER] renderer exit=$REXIT"
tail -30 $RUN/out/render.log

NP=$(ls -1 $RUN/out/png/*.png 2>/dev/null | wc -l)
echo "[RENDER] png files=$NP (11 expected)"
md5sum $RUN/out/png/*.png > $RUN/out/png.md5 2>/dev/null
cat $RUN/out/png.md5

# ---- geometry out: stage trees, surfaces, exported lines, the staged axis copies ----
D=$RUN/out/GEOMETRY_DELETED.txt
{
  echo "ticket 293 -- geometry deleted after the census and the pictures existed, $(date -Is) on $(hostname)"
  echo "deleted (run output): the nine stage trees under $RUN/stage, the extracted surfaces in"
  echo "out/geom/*.xyz, the exported breaklines in out/geom/*.pcd, and the 7 KB axis copies in"
  echo "out/axis/*.axis.xyz (copies of corpus inputs, not corpus). The ticket-276 cluster dumps in"
  echo "out/diag/ are text tables of labels and coordinates, kept as the census record; the pictures,"
  echo "the tables and the scripts stay."
  echo "not deleted: the frozen corpus under /data/gpfs/projects/punim2657/sfs_main/original_samples (INPUT),"
  echo "the binaries in bin/ (record), scripts/, logs/, out/*.tsv, out/*.json, out/*.log, out/png/, out/diag/"
  echo ""
  echo "stage trees:"
  du -sh $RUN/stage/* 2>/dev/null
  echo ""
  echo "files deleted (path bytes):"
  find $RUN/stage $RUN/out/geom $RUN/out/axis -type f -printf "%p %s\n" 2>/dev/null
  echo ""
  echo "counts: stage files=$(find $RUN/stage -type f 2>/dev/null | wc -l) geom files=$(ls -1 $RUN/out/geom 2>/dev/null | wc -l) axis files=$(ls -1 $RUN/out/axis 2>/dev/null | wc -l)"
} > $D
rm -rf $RUN/stage
rm -f $RUN/out/geom/*.xyz $RUN/out/geom/*.pcd $RUN/out/axis/*.axis.xyz
rm -rf $RUN/work
echo "STAGE_DIRS_REMAINING=$(ls -1d $RUN/stage/* 2>/dev/null | wc -l) GEOM_FILES_REMAINING=$(ls -1 $RUN/out/geom 2>/dev/null | wc -l) AXIS_FILES_REMAINING=$(ls -1 $RUN/out/axis 2>/dev/null | wc -l)" >> $D
echo "[CENSUS] deleted stage trees, out/geom geometry and the axis copies; record in $D"

echo "[CENSUS] diag dumps kept: $(ls -1 $RUN/out/diag 2>/dev/null | wc -l), total $(du -sh $RUN/out/diag 2>/dev/null | awk '{print $1}')"
BIG=$(find $RUN -type f -size +1M ! -path "*/bin/*" | wc -l)
echo "[CENSUS] files over 1 MiB outside bin/: $BIG"
find $RUN -type f -size +1M ! -path "*/bin/*" | head -5
echo "[CENSUS] done $(date -Is)"
