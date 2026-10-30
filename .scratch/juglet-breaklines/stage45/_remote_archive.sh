#!/bin/bash
set -uo pipefail
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
BR=45-adopt-the-curvature-formula-as-the-default-growth-angle
git -C "$CANON" fetch --no-tags origin '+refs/heads/*:refs/remotes/origin/*' >/dev/null 2>&1
NEW=$(git -C "$CANON" rev-parse "refs/remotes/origin/$BR")
echo "NEW=$NEW"
D=$(mktemp -d /tmp/t45submit.XXXXXX)
git -C "$CANON" archive "$NEW" .scratch/juglet-breaklines/stage45 | tar -x -C "$D"
echo "D=$D"
echo "--- instruments ---"
ls "$D/.scratch/juglet-breaklines/stage45/instruments"
echo "--- CR check ---"
if grep -rlU $'\r' "$D/.scratch/juglet-breaklines/stage45/instruments"; then echo "CR FOUND"; else echo "no CR anywhere"; fi
echo "--- md5 ---"
cd "$D/.scratch/juglet-breaklines/stage45/instruments" && md5sum *.py *.sh *.tsv 2>/dev/null | sort -k2
echo "D=$D" > /tmp/t45_last_dir.txt
