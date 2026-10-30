#!/bin/bash
# submit from the archive the previous script made; one job, PHASE=all (1,4,7,8,9)
set -uo pipefail
D=$(sed -n 's/^D=//p' /tmp/t46_last_dir.txt)
cd "$D/.scratch/juglet-breaklines/stage46/instruments" || exit 9
echo "PWD=$(pwd)"
echo "--- HEAD of the submitter ---"
git rev-parse HEAD 2>/dev/null || echo "(not a git dir, expected: archive)"
echo "--- submitting ---"
bash submit46.sh covering3 01:30:00
