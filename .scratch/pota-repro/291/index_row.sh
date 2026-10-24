#!/bin/bash
# Append one run row to the project index. Usage: index_row.sh <runid> <jobid> <commit> <tag>
set -uo pipefail
IDX=/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv
HEADER=$(printf "runid\tjobid\tcommit\ttag\tverdict\thuman_note")
[ -f "$IDX" ] || { printf "%s\n" "$HEADER" > "$IDX"; }
[ "$(head -1 "$IDX")" = "$HEADER" ] || { echo "HEADER_MISMATCH: $(head -1 "$IDX")" >&2; exit 9; }
printf "%s\t%s\t%s\t%s\t\t\n" "$1" "$2" "$3" "$4" >> "$IDX"
echo "APPENDED: $(tail -1 "$IDX")"
echo "ROWS: $(wc -l < "$IDX")"
