#!/usr/bin/env bash
set -euo pipefail
SCP="/c/Windows/System32/OpenSSH/scp.exe -q -o BatchMode=yes"
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261106-0454_3695976_t311b-kladder-E
ART="/c/PR/SfSpp_preprocessing/artifacts/pota311/stageB"
mkdir -p "$ART"
$SCP "spartan:$RUN/score/E_K1R2_cpp.json" "$ART/"
$SCP "spartan:$RUN/score/E_K1R2.Acc.txt" "$ART/"
cat "$ART/E_K1R2.Acc.txt"
