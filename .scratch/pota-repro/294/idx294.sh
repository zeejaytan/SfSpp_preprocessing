#!/usr/bin/env bash
set -euo pipefail
IDX=/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv
head -1 "$IDX" | cat -A | head -1
printf "%s\t%s\t%s\t%s\t\t\n" "20261025-0340_0f8a4a4_p294-pictures" "33752717" "0f8a4a417221647e7d6e7f7d031a90109930d44d" "p294-pictures" >> "$IDX"
tail -2 "$IDX"
echo "rows=$(wc -l < "$IDX")"
