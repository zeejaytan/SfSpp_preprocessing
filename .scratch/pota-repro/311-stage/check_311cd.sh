#!/bin/bash
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
SCP="/c/Windows/System32/OpenSSH/scp.exe"
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261106-0502_3695976_t311cd-basins
DEST=C:/PR/SfSpp_preprocessing/artifacts/pota311/stageCD
mkdir -p "$DEST"

"$SSH" -T -o BatchMode=yes spartan "
squeue -u zhuojiat
ls -la $RUN/out $RUN/logs
cat $RUN/logs/stage311cd.log 2>/dev/null || true
"
"$SCP" "spartan:$RUN/out/pot_e_ref_stationarity.tsv" "$DEST/pot_e_ref_stationarity.tsv" 2>/dev/null || true
"$SCP" "spartan:$RUN/out/d_corpus_sweep.tsv" "$DEST/d_corpus_sweep.tsv" 2>/dev/null || true
