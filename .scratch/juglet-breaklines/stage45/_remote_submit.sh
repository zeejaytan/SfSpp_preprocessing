#!/bin/bash
set -uo pipefail
D=$(sed -n 's/^D=//p' /tmp/t45_last_dir.txt)
cd "$D/.scratch/juglet-breaklines/stage45/instruments" || exit 9
echo "PWD=$(pwd)"
echo "--- HEAD of the submitter ---"
git rev-parse HEAD 2>/dev/null || echo "(not a git dir, expected: archive)"
echo "--- submitting ---"
bash submit45.sh default 08:00:00
