#!/bin/bash
# submit307e.sh -- run on spartan: create the 12 NP=8 Stage B run dirs, submit, index.
set -uo pipefail
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
TS=$(date -u +%Y%m%d-%H%M)
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
cd /tmp/t307e || exit 1
for d in bake_e/PLACEHOLDER_*; do
  b=$(basename "$d")
  runid=${b/PLACEHOLDER_TS/$TS}
  R=$RUNS/$runid
  if [ -e "$R/submit.sbatch" ]; then echo "SKIP exists $runid"; continue; fi
  mkdir -p "$R/logs" "$R/out" "$R/work"
  cp "$d/submit.sbatch" "$R/submit.sbatch"
  cp helpers/* "$R/work/" 2>/dev/null
  cp "$d/run.json" "$R/run.json"
  jobid=$(cd "$R" && sbatch --parsable submit.sbatch 2>&1 | tail -1)
  echo "$runid job=$jobid"
  if [ -z "$jobid" ]; then continue; fi
  $PY /tmp/t307e/writer.py "$R/run.json" "$jobid" "$runid" > /dev/null 2>&1 || echo "  WARN run.json not updated"
  tag=$($PY -c "import json,sys;print(json.load(open(sys.argv[1]))['tag'])" "$R/run.json")
  printf '%s\t%s\te6adf69\t%s\t\t\n' "$runid" "$jobid" "$tag" > "$R/index_row.tsv"
  cat "$R/index_row.tsv" >> "$RUNS/index.tsv"
done
echo "== last 12 index rows"
tail -12 "$RUNS/index.tsv"
