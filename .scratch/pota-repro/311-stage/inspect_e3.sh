#!/bin/bash
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
"$SSH" -T -o BatchMode=yes -o ConnectTimeout=25 spartan '
R310E=/data/gpfs/projects/punim2657/SfSpp/runs/20261105-1407_1a6f16e_t310c2-E
echo "=== isSimilarTrans in data_structure.cpp ==="
grep -n -B 5 -A 35 "isSimilarTrans(" /data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker/class/data_structure.cpp
echo "=== T_ files in MMR1 and MMR2 ==="
ls $R310E/out/MMR1/T_*.txt
echo "---"
ls $R310E/out/MMR2/T_*.txt
echo "=== Full MMR1.tsv and MMR2.tsv ==="
cat $R310E/score/MMR1.tsv
echo "==="
cat $R310E/score/MMR2.tsv
'
