#!/bin/bash
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
SCP="/c/Windows/System32/OpenSSH/scp.exe"
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261106-0450_3695976_t311a-attr
DEST=C:/PR/SfSpp_preprocessing/artifacts/pota311/stageA
mkdir -p "$DEST"

"$SSH" -T -o BatchMode=yes spartan "
sacct -j 34427662 --format=JobID,State,ExitCode,Elapsed
squeue -j 34427662 2>/dev/null || true
ls -la $RUN/out $RUN/logs
cat $RUN/logs/slurm-34427662.out 2>/dev/null || true
cat $RUN/logs/slurm-34427662.err 2>/dev/null || true
"
"$SCP" "spartan:$RUN/out/a1_provenance.tsv" "$DEST/a1_provenance.tsv" 2>/dev/null || true
"$SCP" "spartan:$RUN/out/a2_pieces.tsv" "$DEST/a2_pieces.tsv" 2>/dev/null || true
"$SCP" "spartan:$RUN/out/a2_joins.tsv" "$DEST/a2_joins.tsv" 2>/dev/null || true
"$SCP" "spartan:$RUN/out/a2_arms.json" "$DEST/a2_arms.json" 2>/dev/null || true
