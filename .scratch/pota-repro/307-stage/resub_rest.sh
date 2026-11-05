#!/bin/bash
# resub_rest.sh -- resubmit the Stage B run dirs whose arm67.sh arrived with CRLF,
# in ONE ssh connection (per-run scp trips Spartan's login rate limit). Arguments: run dirs.
set -uo pipefail
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
for d in "$@"; do
  cp /tmp/arm67_LF.sh "$d/work/arm67.sh"
  J=$(cd "$d" && sbatch --parsable submit.sbatch)
  T=$(basename "$d")
  printf '%s\t%s\te6adf69\t%s-r2\t\t\n' "$T" "$J" "$T" >> "$RUNS/index.tsv"
  sed -i "s/\"jobid\": \"[0-9]*\"/\"jobid\": \"$J\"/" "$d/run.json"
  echo "$T job=$J"
done
