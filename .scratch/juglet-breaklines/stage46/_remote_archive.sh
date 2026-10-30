#!/bin/bash
# archive the pushed branch head into a temp dir on Spartan, so the submitter comes out of the
# commit (the job md5-compares its instruments against that commit and fails rc=4 on a mismatch)
set -uo pipefail
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
BR=46-feed-the-growth-an-even-covering
git -C "$CANON" fetch --no-tags origin '+refs/heads/*:refs/remotes/origin/*' >/dev/null 2>&1
NEW=$(git -C "$CANON" rev-parse "refs/remotes/origin/$BR")
echo "NEW=$NEW"
D=$(mktemp -d /tmp/t46submit.XXXXXX)
git -C "$CANON" archive "$NEW" .scratch/juglet-breaklines/stage46 | tar -x -C "$D"
echo "D=$D"
echo "--- instruments ---"
ls "$D/.scratch/juglet-breaklines/stage46/instruments"
echo "--- CR check ---"
if grep -rlU $'\r' "$D/.scratch/juglet-breaklines/stage46/instruments"; then echo "CR FOUND"; else echo "no CR anywhere"; fi
echo "--- md5 ---"
cd "$D/.scratch/juglet-breaklines/stage46/instruments" && md5sum *.py *.sh *.tsv 2>/dev/null | sort -k2
echo "D=$D" > /tmp/t46_last_dir.txt
