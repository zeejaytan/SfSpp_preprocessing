#!/bin/bash
OUTF=/data/gpfs/projects/punim2657/SfSpp/runs/20261031-0346_a51819f_t47-jugletcc/submit.sbatch
echo "--- pattern as in submit47.sh (single-quoted):"
grep -o -E '\$[A-Za-z_][A-Za-z0-9_]*' "$OUTF" | wc -l
echo "--- fgrep dollar sign count:"
grep -c -F '$' "$OUTF"
echo "--- dollar-VAR plain ERE without backslash:"
grep -o -E '[$][A-Za-z_][A-Za-z0-9_]*' "$OUTF" | wc -l
