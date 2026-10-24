#!/usr/bin/env bash
#SBATCH --job-name=p292collect
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --output=logs/slurm-%j.out
# Ticket 292 job C: corpus re-check, geometry assertion, summary.md, per-pot pictures.
set -uo pipefail

: ${RUN_DIR:?RUN_DIR must be exported}
RUN=$RUN_DIR
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
out=$RUN/out

echo "[COLLECT] $(date -Is) tasks=$(ls $out/status | wc -l) lane_files=$(ls $out/lanes | wc -l) tiles=$(ls $out/tiles | wc -l) pngs=$(ls $out/png | wc -l)"

# ---- corpus re-check: the same 148 clouds, byte-identical ----
xargs -a $out/cloud_paths.txt -P 8 -n 1 md5sum | sort -k2 > $out/corpus_after.md5
{ echo "before_rows=$(wc -l < $out/corpus_before.md5) after_rows=$(wc -l < $out/corpus_after.md5)";
  if cmp -s $out/corpus_before.md5 $out/corpus_after.md5; then
    echo "corpus_unchanged=YES (all 148 cloud md5s identical before and after the array)";
  else
    echo "corpus_unchanged=NO"; diff $out/corpus_before.md5 $out/corpus_after.md5 | head -20;
  fi
  echo "the staged cloud md5s were also checked against MANIFEST_released/derived by stage_piece.sh at staging time";
} > $out/corpus_check.txt
cat $out/corpus_check.txt

# ---- geometry assertion ----
find $RUN -type f -size +1M -not -path "$RUN/bin/*" -not -path "$RUN/logs/*" -not -path "$out/logs/*" > $out/big_files.txt
{ echo "files over 1 MiB under $RUN outside bin/: $(wc -l < $out/big_files.txt) (0 expected)";
  sed -n "1,20p" $out/big_files.txt;
  echo "run dir total: $(du -sh $RUN | cut -f1)";
  echo "logs over 1 MiB (record, not geometry): $(find $RUN/logs $out/logs -type f -size +1M 2>/dev/null | wc -l)";
  echo "out total: $(du -sh $out | cut -f1) tiles=$(ls $out/tiles | wc -l) miss_png=$(ls $out/png/*_Bl*.png 2>/dev/null | wc -l) pot_png=$(ls $out/png/pot_*.png 2>/dev/null | wc -l)";
  echo "deleted_stage_records=$(ls $out/deleted | wc -l) of 148 array tasks";
} > $out/geometry_check.txt
cat $out/geometry_check.txt

# ---- what each task deleted ----
{ echo "# GEOMETRY_DELETED -- ticket 292 array: one block per array task, written before its rm -rf";
  echo "# node-local stage tree removed: the staged symlinks into the frozen corpus, the mesh stage";
  echo "# output (Temp/Data: surfaces and ply companions), the edge stage work (Temp/Temp_edge: bags,";
  echo "# stepring) and the two exported lanes. Kept: run.json, the sbatch scripts, logs, the scorer,";
  echo "# lanes.tsv, summary.md, out/png (pictures), out/tiles, out/recheck, out/status, and bin/.";
  for f in $(ls $out/deleted/*.tsv | sort); do echo "== $(basename $f .tsv)"; cat $f; done;
} > $out/GEOMETRY_DELETED.txt
echo "[COLLECT] GEOMETRY_DELETED.txt lines=$(wc -l < $out/GEOMETRY_DELETED.txt)"

# ---- summary and per-pot pictures ----
"$PY" "$RUN/scripts/summary292.py" "$RUN" || echo "[COLLECT] summary292.py failed"
"$PY" "$RUN/scripts/potpng292.py" "$RUN" || echo "[COLLECT] potpng292.py failed"

echo "[COLLECT] headline:"
sed -n "/## Headline/,/^Pieces that/p" $out/summary.md | head -20
echo "[COLLECT] done $(date -Is)"