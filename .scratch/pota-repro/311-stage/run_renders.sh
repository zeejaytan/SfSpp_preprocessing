#!/bin/bash
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
SCP="/c/Windows/System32/OpenSSH/scp.exe"
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261106-0454_3695976_t311b-kladder-E
RUN2=/data/gpfs/projects/punim2657/SfSpp/runs/20261106-0624_3695976_t311b2-kladder-K23
"$SCP" -q -o BatchMode=yes C:/PR/SfSpp_preprocessing/.scratch/pota-repro/311-stage/render311.py "spartan:$RUN/work/render311.py"
"$SSH" -T -o BatchMode=yes spartan "
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
mkdir -p $RUN/out/renders
\$PY $RUN/work/render311.py $RUN/out/renders $RUN $RUN2
ls -lh $RUN/out/renders
"
