#!/bin/bash
# _remote_submit47.sh -- run ON SPARTAN (uploaded from the laptop).
#
# Single entry point for the ticket 47 submit: fetch the canonical checkout,
# extract the stage47 instruments from the PUSHED commit (never a local copy),
# and hand off to submit47.sh which renders, gates and sbatch's.  Deleting the
# temp tree on exit keeps nothing lying around on the login node.
set -euo pipefail

CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
BRANCH=47-rebuild-the-juglet-input-clouds-with-the-corpus-converter

cd "$CANON"
git fetch --no-tags origin "+refs/heads/*:refs/remotes/origin/*" > /dev/null
NEW=$(git rev-parse "origin/$BRANCH")
echo "[remote] resolved $BRANCH -> $NEW"

TMP=$(mktemp -d /tmp/t47sub.XXXXXX)
trap 'rm -rf "$TMP"' EXIT
git archive "$NEW" .scratch/juglet-breaklines/stage47 | tar -x -C "$TMP"
echo "[remote] instruments extracted from commit $NEW"

bash "$TMP/.scratch/juglet-breaklines/stage47/instruments/submit47.sh" jugletcc 00:30:00
