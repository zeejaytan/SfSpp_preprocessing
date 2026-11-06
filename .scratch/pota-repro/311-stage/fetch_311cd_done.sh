#!/usr/bin/env bash
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe -T -o BatchMode=yes"
SCP="/c/Windows/System32/OpenSSH/scp.exe -q -o BatchMode=yes"
RDIR="/data/gpfs/projects/punim2657/SfSpp/runs/20261106-0502_3695976_t311cd-basins"
ART="/c/PR/SfSpp_preprocessing/artifacts/pota311/stageCD"
mkdir -p "$ART/basins"

$SSH spartan "sacct -j 34428026 --format=JobID,State,ExitCode,Elapsed && wc -l $RDIR/logs/corpus_before.md5 $RDIR/logs/corpus_after.md5 $RDIR/logs/corpus.diff"
$SCP "spartan:$RDIR/out/stagec_summary.tsv" "$ART/"
$SCP "spartan:$RDIR/out/basins/*.tsv" "$ART/basins/"
ls -la "$ART" "$ART/basins"
