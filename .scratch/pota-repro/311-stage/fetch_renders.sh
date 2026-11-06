#!/bin/bash
set -euo pipefail
SCP="/c/Windows/System32/OpenSSH/scp.exe"
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261106-0454_3695976_t311b-kladder-E
OUT=C:/PR/SfSpp_preprocessing/artifacts/pota311/renders
mkdir -p "$OUT"
"$SCP" -q -o BatchMode=yes "spartan:$RUN/out/renders/*.png" "$OUT/"
ls -lh "$OUT"
