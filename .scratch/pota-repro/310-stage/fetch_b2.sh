#!/bin/bash
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SCP=/c/Windows/System32/OpenSSH/scp.exe
SSH=/c/Windows/System32/OpenSSH/ssh.exe
D=C:/PR/SfSpp_preprocessing/artifacts/pota310
LT=$(cygpath -w /tmp)
R1=/data/gpfs/projects/punim2657/SfSpp/runs/20261105-1221_1a6f16e_t310b2-arms
R2=/data/gpfs/projects/punim2657/SfSpp/runs/20261105-1225_1a6f16e_t310b2-cap
mkdir -p "$D/310b2"
"$SSH" spartan "mkdir -p /tmp/t310b2 && cp $R1/out/b2.tsv /tmp/t310b2/arms_cap6.tsv && cp $R2/out/b2.tsv /tmp/t310b2/arms_cap2.tsv && cp $R1/logs/stageb2.log /tmp/t310b2/arms_cap6.log && cp $R2/logs/stageb2.log /tmp/t310b2/arms_cap2.log && tar czf /tmp/t310b2.tgz -C /tmp/t310b2 ."
"$SCP" spartan:/tmp/t310b2.tgz "$LT\\t310b2.tgz"
cd "$D/310b2" && tar xzf /tmp/t310b2.tgz && ls -l && echo '--- cap6 summary' && grep '^\[B2\]' arms_cap6.log && echo '--- cap2 summary' && grep '^\[B2\]' arms_cap2.log